"""Same-day publications keep independent artifacts, journals and channel markers."""
import copy
import json
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import publication
import upload
import channel_sync
import strategy
import content_routing
import schema


def manifest_episode(root, identity, date="2026-09-28"):
    episode = {"date": date, "episode_id": identity}
    paths = [f"data/episodes/{identity}.json"] + [f"output/{identity}/{name}" for name in
        ("video.mp4", "thumbnail.png", "brief.md")]
    for name in paths:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(episode) if name.endswith(".json") else identity, encoding="utf-8")
    return {"id": identity, "date": date,
            "files": {name: publication.digest(root / name) for name in paths}}


def test_same_day_release_has_distinct_materials_and_journals(tmp_path):
    ids = ["2026-09-28-models-builder", "2026-09-28-guides-everyday"]
    manifest = {"run_id": "123", "commit": "abc", "episodes": [manifest_episode(tmp_path, key) for key in ids]}
    publication.verify_release(tmp_path, manifest, "123", "abc")
    assert set(manifest["episodes"][0]["files"]).isdisjoint(manifest["episodes"][1]["files"])
    journals = [publication.GitHubJournal("owner/repo", "test-token", key) for key in ids]
    assert journals[0].url != journals[1].url
    assert all(journal.url.endswith(f"/{key}.json") for journal, key in zip(journals, ids))
    swapped = copy.deepcopy(manifest)
    swapped["episodes"][1]["files"] = manifest["episodes"][0]["files"]
    with pytest.raises(ValueError, match="Unexpected"):
        publication.verify_release(tmp_path, swapped, "123", "abc")
    manifest["episodes"][1]["date"] = "2026-09-29"
    with pytest.raises(ValueError, match="episode_id"):
        publication.verify_release(tmp_path, manifest, "123", "abc")


def test_existing_video_lookup_and_description_do_not_collide_same_day(tmp_path):
    ids = ["2026-09-28-models-builder", "2026-09-28-guides-everyday"]
    yt = MagicMock()
    yt.playlistItems().list().execute.return_value = {"items": [
        {"snippet": {"description": f"AI Daily Diff episode: {key}", "resourceId": {"videoId": str(i)}}}
        for i, key in enumerate(["2026-09-28", *ids])]}
    assert upload.find_existing(yt, {"uploads": "uploads"}, "2026-09-28") == "0"
    assert upload.find_existing(yt, {"uploads": "uploads"}, ids[0]) == "1"
    assert upload.find_existing(yt, {"uploads": "uploads"}, ids[1]) == "2"
    for key, primary, audience, kind in zip(ids, ["models", "guides"], ["builder", "everyday"], ["daily", "method"]):
        episode = {"date": "2026-09-28", "episode_id": key, "title": "Title",
                   "kind": kind, "primary_playlist": primary, "prompt_profile": primary, "primary_audience": audience,
                   "playlist_review": {"status": "approved", "reviewer": "editor", "reason": "Whole video fits the topic."},
                   "items": [{"source_url": "https://example.org/source", "evidence_mode": "documented"}]}
        # No channel state is necessary for testing artifact URLs and identity markers.
        description = upload.build_description(episode, tmp_path)
        assert f"AI Daily Diff episode: {key}\n" in description
        assert f"/{key}/slides.pdf" in description
        assert "AI Daily Diff episode: 2026-09-28\n" not in description


def test_queue_receipt_reconciliation_uses_exact_episode_identity(tmp_path):
    ids = ["2026-09-28-models-builder", "2026-09-28-guides-everyday"]
    entries = [{"id": str(i), "episode_date": "2026-09-28", "episode_id": key,
                "item_id": "shared-item", "url": "https://example.org/source", "state": "editorial_ready"}
               for i, key in enumerate(ids)]
    path = tmp_path / "models.json"
    path.write_text(json.dumps({"entries": entries}))
    episodes = {key: {"date": "2026-09-28", "episode_id": key, "publication": {"ready": True},
                     "items": [{"id": "shared-item", "source_url": entries[0]["url"]}]} for key in ids}
    receipts = {ids[0]: {"date": "2026-09-28", "episode_id": ids[0], "channel_id": "channel",
                       "actual_privacy": "public", "video_id": "first", "url": "https://youtu.be/first"}}
    strategy.reconcile_queues(tmp_path, episodes, receipts, "channel")
    result = json.loads(path.read_text())["entries"]
    assert [entry["state"] for entry in result] == ["published", "queued"]
    assert "publication_url" not in result[1]
    with pytest.raises(ValueError):
        channel_sync.receipt_episode(ids[1], receipts[ids[0]], episodes)


def test_two_verified_same_day_uploads_reserve_distinct_receipts_then_retry_without_insert(tmp_path):
    day = "2026-09-02"
    base = json.loads((ROOT / f"data/episodes/{day}.json").read_text(encoding="utf-8"))
    base.update(primary_playlist="models", prompt_profile="models", primary_audience="builder",
                topics=["models"], audiences=["builder"],
                production_prompts=content_routing.profile_files("models", "builder", base["kind"]),
                playlist_review={"status": "approved", "reviewer": "editor", "reason": "Whole-video release decision."})
    policy = {"privacy": "public", "channel_id": "channel"}
    yt = MagicMock()
    yt.channels().list().execute.return_value = {"items": [{"id": "channel", "snippet": {"title": "AI Daily Diff"},
        "contentDetails": {"relatedPlaylists": {"uploads": "uploads"}}}]}
    yt.playlistItems().list().execute.return_value = {"items": []}
    yt.videos().insert().next_chunk.side_effect = [(None, {"id": "first"}), (None, {"id": "second"})]
    yt.videos().list().execute.return_value = {"items": [{"snippet": {"channelId": "channel"},
        "status": {"privacyStatus": "public", "uploadStatus": "processed"}}]}
    yt.reset_mock()

    class MemoryJournal:
        def __init__(self):
            self.receipt = None
            self.writes = []
        def read(self):
            return copy.deepcopy(self.receipt)
        def write(self, value):
            self.receipt = copy.deepcopy(value)
            self.writes.append(copy.deepcopy(value))

    records = []
    for suffix in ("models-builder", "models-professional"):
        episode = copy.deepcopy(base)
        episode["episode_id"] = f"{day}-{suffix}"
        if suffix.endswith("professional"):
            episode.update(primary_audience="professional", audiences=["professional"],
                           production_prompts=content_routing.profile_files("models", "professional", episode["kind"]))
        assert schema.validate_episode(episode) == []
        folder = tmp_path / episode["episode_id"]
        folder.mkdir()
        for name in ("video.mp4", "thumbnail.png", "brief.md"):
            (folder / name).write_bytes(episode["episode_id"].encode())
        journal = MemoryJournal()
        upload.publish_verified(episode, folder, policy, journal, youtube=yt)
        records.append((episode, folder, journal))
    assert yt.videos().insert.call_count == 2
    assert [record[2].receipt["video_id"] for record in records] == ["first", "second"]
    assert records[0][2].receipt["episode_id"] != records[1][2].receipt["episode_id"]
    assert all(record[2].writes[0]["state"] == "reserved" for record in records)
    yt.reset_mock()
    for episode, folder, journal in records:
        upload.publish_verified(episode, folder, policy, journal, youtube=yt)
    yt.videos().insert.assert_not_called()
