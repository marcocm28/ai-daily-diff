import copy
import datetime as dt
import json
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import publication
import upload


@pytest.fixture
def sample(tmp_path):
    episode = json.loads((ROOT / "data/episodes/2026-09-02.json").read_text(encoding="utf-8"))
    for name in ("video.mp4", "thumbnail.png", "brief.md"):
        (tmp_path / name).write_bytes(b"test fixture")
    policy = {"enabled": True, "channel_id": "UCDEWpe6dU5_-3Im8KxQk5WA", "privacy": "public"}
    yt = MagicMock()
    yt.channels().list().execute.return_value = {"items": [{
        "id": policy["channel_id"], "snippet": {"title": "AI Daily Diff"},
        "contentDetails": {"relatedPlaylists": {"uploads": "UUuploads"}}}]}
    yt.playlistItems().list().execute.return_value = {"items": []}
    yt.videos().insert().next_chunk.return_value = (None, {"id": "video123"})
    yt.videos().list().execute.return_value = {"items": [{
        "snippet": {"channelId": policy["channel_id"]},
        "status": {"privacyStatus": "public", "uploadStatus": "processed"}}]}
    yt.reset_mock()
    class Journal:
        def __init__(self):
            self.receipt = None
            self.writes = []
        def read(self):
            return copy.deepcopy(self.receipt)
        def write(self, value):
            self.receipt = copy.deepcopy(value)
            self.writes.append(copy.deepcopy(value))
    return episode, tmp_path, policy, Journal(), yt


def publish(sample):
    episode, folder, policy, journal, yt = sample
    return upload.publish_verified(episode, folder, policy, journal, youtube=yt)


def test_channel_mismatch_blocks_before_reservation_and_insert(sample):
    sample[2]["channel_id"] = "wrong"
    with pytest.raises(ValueError, match="Wrong OAuth channel"):
        publish(sample)
    assert sample[3].writes == []
    sample[4].videos().insert.assert_not_called()


def test_upload_reserves_first_and_second_run_never_inserts_again(sample):
    assert publish(sample) == "video123"
    assert sample[3].writes[0]["state"] == "reserved"
    assert sample[3].receipt["state"] == "published"
    assert sample[3].receipt["actual_privacy"] == "public"
    sample[4].reset_mock()
    assert publish(sample) == "video123"
    sample[4].videos().insert.assert_not_called()
    sample[4].thumbnails().set.assert_not_called()


def test_reservation_write_failure_never_uploads(sample):
    sample[3].write = MagicMock(side_effect=RuntimeError("GitHub unavailable"))
    with pytest.raises(RuntimeError):
        publish(sample)
    sample[4].videos().insert.assert_not_called()


def test_uncertain_insert_is_not_retried(sample):
    sample[4].videos().insert().next_chunk.side_effect = TimeoutError()
    with pytest.raises(TimeoutError):
        publish(sample)
    assert sample[3].receipt["state"] == "reserved"
    sample[4].reset_mock()
    with pytest.raises(ValueError, match="uncertain"):
        publish(sample)
    sample[4].videos().insert.assert_not_called()


def test_crash_after_upload_recovers_from_channel_marker(sample):
    sample[4].videos().insert().next_chunk.side_effect = TimeoutError()
    with pytest.raises(TimeoutError):
        publish(sample)
    sample[4].reset_mock()
    sample[4].playlistItems().list().execute.return_value = {"items": [{"snippet": {
        "description": "AI Daily Diff episode: 2026-09-02\nbody",
        "resourceId": {"videoId": "recovered"}}}]}
    assert publish(sample) == "recovered"
    sample[4].videos().insert.assert_not_called()


def test_actual_private_restriction_is_not_reported_as_public(sample):
    sample[4].videos().list().execute.return_value["items"][0]["status"]["privacyStatus"] = "private"
    with pytest.raises(ValueError, match="status differs"):
        publish(sample)
    assert sample[3].receipt["actual_privacy"] == "private"
    assert sample[3].receipt["state"] != "published"
    assert sample[3].receipt["video_id"] == "video123"


def test_thumbnail_failure_keeps_video_id_for_retry(sample):
    sample[4].thumbnails().set().execute.side_effect = RuntimeError("thumbnail quota")
    with pytest.raises(RuntimeError):
        publish(sample)
    assert sample[3].receipt["video_id"] == "video123"
    sample[4].thumbnails().set().execute.side_effect = None
    sample[4].reset_mock()
    publish(sample)
    sample[4].videos().insert.assert_not_called()
    assert sample[3].receipt["thumbnail_set"]


def test_episode_edit_after_upload_requires_review(sample):
    publish(sample)
    sample[0]["title"] = "A changed title"
    sample[4].reset_mock()
    with pytest.raises(ValueError, match="already owns"):
        publish(sample)
    sample[4].videos().insert.assert_not_called()


def test_remote_dedup_paginates_and_recognizes_legacy_episode_link(sample):
    sample[4].playlistItems().list().execute.side_effect = [
        {"items": [], "nextPageToken": "page2"},
        {"items": [{"snippet": {"description":
          f"Episode page (all downloads): {upload.PAGES_BASE_URL}/2026-09-02/",
          "resourceId": {"videoId": "legacy"}}}]}]
    assert publish(sample) == "legacy"
    sample[4].videos().insert.assert_not_called()


def test_dry_run_never_contacts_youtube_or_journal(sample):
    upload.publish_verified(*sample[:4], dry_run=True, youtube=sample[4])
    assert sample[4].mock_calls == []
    assert sample[3].writes == []


@pytest.mark.parametrize("ready,date,expected", [
    (False, "2026-09-17", False), (True, "2026-09-16", False),
    (True, "2026-09-17", True), (True, "2026-09-19", False),
    (True, "2026-09-01", False)])
def test_automatic_scope_excludes_archive_and_future(ready, date, expected):
    episode = {"date": date, "publication": {"ready": ready}}
    assert publication.eligible(episode, {"start_date": "2026-09-17"}, dt.date(2026, 9, 18)) == expected


def test_manifest_binds_run_and_all_files(tmp_path):
    day = "2026-09-17"
    names = [f"data/episodes/{day}.json"] + [f"output/{day}/{n}" for n in
                                                ("video.mp4", "thumbnail.png", "brief.md")]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"verified")
    manifest = {"run_id": "123", "commit": "abc", "episodes": [
        {"date": day, "files": {name: publication.digest(tmp_path / name) for name in names}}]}
    publication.verify_release(tmp_path, manifest, "123", "abc")
    with pytest.raises(ValueError, match="successful Render"):
        publication.verify_release(tmp_path, manifest, "999", "abc")
    (tmp_path / names[1]).write_bytes(b"tampered")
    with pytest.raises(ValueError, match="file changed"):
        publication.verify_release(tmp_path, manifest, "123", "abc")
    manifest["episodes"][0]["files"]["../outside"] = "abc"
    with pytest.raises(ValueError, match="Unexpected"):
        publication.verify_release(tmp_path, manifest, "123", "abc")
