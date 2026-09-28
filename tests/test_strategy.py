import copy
import datetime as dt
import json
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import strategy
import schema
import channel_sync
import selection


def test_playlist_read_retries_visibility_delay_without_repeating_mutations(monkeypatch):
    from googleapiclient.errors import HttpError
    import httplib2
    request = MagicMock()
    missing = HttpError(httplib2.Response({"status": "404"}), b'{"error":{"message":"not found"}}')
    request.return_value.execute.side_effect = [missing, {"items": []}]
    monkeypatch.setattr(channel_sync.time, "sleep", lambda _: None)
    assert channel_sync.all_items(request, playlistId="new-playlist") == []
    assert request.call_count == 2
    request.return_value.execute.side_effect = [missing] * 5
    with pytest.raises(HttpError):
        channel_sync.all_items(request, playlistId="missing-playlist")


def reviewed_episode():
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-27.json")
    ep.update(date="2026-09-28", topics=["models"], audiences=["builder"], primary_audience="builder",
        coverage_review={scope: {"status": "checked", "sources": ["https://example.org/source"],
            "decision": "deferred", "reason": "Review fixture"} for scope in strategy.SCOPES})
    return ep


def test_new_production_requires_complete_coverage():
    ep = reviewed_episode()
    assert schema.validate_episode(ep) == []
    ep["coverage_review"]["anthropic"] = {"status": "unavailable", "decision": "no_qualifying_news"}
    assert any("anthropic" in p for p in schema.validate_episode(ep))
    ep = reviewed_episode()
    del ep["coverage_review"]["architectures"]
    assert any("architectures" in p for p in schema.validate_episode(ep))


def test_queue_merge_preserves_human_review_and_unknown_event_date(tmp_path):
    c = {"url": "https://example.org/release", "kind": "research", "title": "Architecture", "published_at": "2026-09-28"}
    strategy.update_queues([c], tmp_path, dt.date(2026, 9, 28))
    path = tmp_path / "architectures.json"
    data = json.loads(path.read_text())
    assert data["entries"][0]["event_date"] is None
    data["entries"][0].update(state="editorial_ready", reason="Verified by editor")
    path.write_text(json.dumps(data))
    strategy.update_queues([c], tmp_path, dt.date(2026, 9, 29))
    data = json.loads(path.read_text())
    assert len(data["entries"]) == 1 and data["entries"][0]["state"] == "editorial_ready"


def test_queue_publication_requires_exact_item_and_public_channel_receipt(tmp_path):
    entry = {"id": "lead", "url": "https://example.org/source", "episode_date": "2026-09-28",
             "item_id": "item", "state": "editorial_ready"}
    path = tmp_path / "models.json"
    path.write_text(json.dumps({"entries": [entry]}))
    episodes = {"2026-09-28": {"publication": {"ready": True}, "items": [
        {"id": "item", "source_url": entry["url"]}]}}
    receipt = {"channel_id": "wrong", "actual_privacy": "public", "video_id": "video", "url": "https://youtu.be/video"}
    strategy.reconcile_queues(tmp_path, episodes, {"2026-09-28": receipt}, "channel")
    assert json.loads(path.read_text())["entries"][0]["state"] == "queued"
    receipt["channel_id"] = "channel"
    strategy.reconcile_queues(tmp_path, episodes, {"2026-09-28": receipt}, "channel")
    assert json.loads(path.read_text())["entries"][0]["state"] == "published"


def test_multiple_strong_releases_beat_weaker_category_diversity(tmp_path, monkeypatch):
    day = dt.date(2026, 9, 28)
    inbox, episodes = tmp_path / "inbox", tmp_path / "episodes"
    inbox.mkdir(); episodes.mkdir()
    candidates = [{"url": f"https://example.org/{i}", "title": str(i), "kind": "vendor_release",
        "vertical": "models-releases" if i < 2 else "claims-risks", "published_at": day.isoformat(),
        "is_primary_source": True, "blast_radius": 1 if i < 2 else .1,
        "decision_relevance": 1 if i < 2 else .1} for i in range(3)]
    (inbox / f"{day}.json").write_text(json.dumps({"candidates": candidates}))
    monkeypatch.setattr(selection, "INBOX", inbox)
    monkeypatch.setattr(selection, "EPISODES", episodes)
    monkeypatch.setattr(selection, "load_candidates", lambda date: [])
    out = json.loads(selection.run(day, max_selected=2).read_text())
    assert [c["title"] for c in out["selected"]] == ["0", "1"]
    assert len(out["review_candidates"]) == 3


def test_wrong_channel_blocks_all_management_mutations():
    yt = MagicMock()
    yt.channels().list().execute.return_value = {"items": [{"id": "wrong"}]}
    with pytest.raises(ValueError, match="Wrong channel"):
        channel_sync.synchronize(yt, {"channel_id": "expected"}, {}, {}, apply=True)
    yt.channels().update.assert_not_called()
    yt.playlists().insert.assert_not_called()


def test_sync_is_idempotent_and_preserves_existing_branding():
    yt = MagicMock()
    cfg = {"channel_id": "channel", "description": "Description", "keywords": "AI",
        "playlists": [{"key": "models", "title": "Models", "description": "Releases"}]}
    channel = {"id": "channel", "brandingSettings": {"channel": {"country": "IT", "title": "Name"}}}
    playlists, members = [], []
    yt.channels().list().execute.side_effect = lambda: {"items": [copy.deepcopy(channel)]}
    def update_channel(**kwargs):
        channel["brandingSettings"] = kwargs["body"]["brandingSettings"]
        req = MagicMock(); req.execute.return_value = copy.deepcopy(channel); return req
    yt.channels().update.side_effect = update_channel
    def list_playlists(**kwargs):
        req = MagicMock(); req.execute.return_value = {"items": copy.deepcopy(playlists)}; return req
    yt.playlists().list.side_effect = list_playlists
    def insert_playlist(**kwargs):
        p = {"id": "playlist", **kwargs["body"]}; p["snippet"]["channelId"] = "channel"
        playlists.append(p)
        req = MagicMock(); req.execute.return_value = copy.deepcopy(p); return req
    yt.playlists().insert.side_effect = insert_playlist
    yt.playlistItems().list().execute.side_effect = lambda: {"items": copy.deepcopy(members)}
    def insert_member(**kwargs):
        members.append({"id": "association", "contentDetails": {"videoId": kwargs["body"]["snippet"]["resourceId"]["videoId"]}})
        return MagicMock()
    yt.playlistItems().insert.side_effect = insert_member
    yt.videos().list().execute.return_value = {"items": [{"snippet": {"channelId": "channel"}, "status": {"privacyStatus": "public"}}]}
    episodes = {"2026-09-28": {"date": "2026-09-28", "kind": "daily", "topics": ["models"],
        "primary_playlist": "models", "prompt_profile": "models", "primary_audience": "builder",
        "playlist_review": {"status": "approved", "reviewer": "editor", "reason": "Whole-video model focus"}}}
    receipts = {"2026-09-28": {"channel_id": "channel", "video_id": "video", "actual_privacy": "public"}}
    channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    assert yt.playlists().insert.call_count == 1 and yt.playlistItems().insert.call_count == 1
    assert yt.playlistItems().insert.call_args.kwargs["body"]["snippet"]["position"] == 0
    assert channel["brandingSettings"]["channel"]["country"] == "IT"
    assert channel["brandingSettings"]["channel"]["title"] == "Name"
