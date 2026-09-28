import copy
import json
import pathlib
import sys
from unittest.mock import MagicMock

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import content_routing
import channel_sync
import schema
import upload
import author
import datetime as dt


def route(primary="builder"):
    return {"primary_playlist": primary, "prompt_profile": primary, "primary_audience": "builder",
            "playlist_review": {"status": "approved", "reviewer": "creator", "reason": "The whole script serves this path."}}


def test_author_scaffold_records_exact_prompt_profile_and_blocks_wrong_level(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"; inbox.mkdir()
    monkeypatch.setattr(author, "INBOX", inbox)
    monkeypatch.setattr(author, "EPISODES", tmp_path / "episodes")
    day = dt.date(2026, 9, 29)
    (inbox / f"{day}.selected.json").write_text(json.dumps({"selected": [
        {"title": "Agent feature", "url": "https://example.org/feature", "source": "primary"}]}))
    with pytest.raises(ValueError):
        author.run(day, playlist="everyday", audience="builder")
    assert not (tmp_path / "episodes").exists()
    path = author.run(day, playlist="agents", audience="builder")
    draft = json.loads(path.read_text())
    assert draft["primary_playlist"] == draft["prompt_profile"] == "agents"
    assert draft["production_prompts"] == content_routing.profile_files("agents", "builder", "daily")
    assert draft["playlist_review"]["status"] == "pending"
    assert schema.validate_episode(draft)


def test_future_video_requires_correct_specialization_and_prompt_before_queue():
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-28.json")
    ep.update(date="2026-09-29", **route(), audiences=["builder"],
              production_prompts=content_routing.profile_files("builder", "builder", "daily"))
    assert schema.validate_episode(ep) == []
    ep["prompt_profile"] = "agents"
    assert any("prompt_profile" in p for p in schema.validate_episode(ep))
    ep.update(**route("models"), topics=["models", "agents"])
    assert any("one topic" in p for p in schema.validate_episode(ep))
    with pytest.raises(ValueError):
        content_routing.profile_files("everyday", "builder", "daily")
    with pytest.raises(ValueError):
        content_routing.approved_primary({"date": "2026-09-28", "kind": "daily", "topics": ["models"]}, {})
    for primary, audience, kind in [("models", "everyday", "daily"), ("architectures", "builder", "deep"),
                                    ("agents", "professional", "method"), ("builder", "builder", "daily")]:
        assert all((ROOT / name).is_file() for name in content_routing.profile_files(primary, audience, kind))


@pytest.mark.parametrize("selected_route", [route("models"), route("agents")])
def test_new_script_never_inherits_selection_approval(tmp_path, monkeypatch, selected_route):
    inbox = tmp_path / "inbox"; inbox.mkdir()
    monkeypatch.setattr(author, "INBOX", inbox)
    monkeypatch.setattr(author, "EPISODES", tmp_path / "episodes")
    day = dt.date(2026, 9, 29)
    selected = {"selected": [{"title": "Agent feature", "url": "https://example.org/feature", "source": "primary"}],
                **selected_route}
    (inbox / f"{day}.selected.json").write_text(json.dumps(selected))
    draft = json.loads(author.run(day, playlist="agents", audience="builder").read_text())
    assert draft["playlist_review"]["status"] == "pending"
    assert any("approved" in error for error in content_routing.episode_problems(draft))


def test_brief_adapts_same_topic_to_two_audiences_and_uses_channel_promise():
    selection = {"editorial_review": {"viewer_question": "Which new capability changes this task?"}}
    everyday = content_routing.production_brief("2026-09-29", "models", "everyday", "daily", selection)
    builder = content_routing.production_brief("2026-09-29", "models", "builder", "daily", selection)
    config = json.loads((ROOT / "config/channel.json").read_text(encoding="utf-8"))
    promise = next(p["description"] for p in config["playlists"] if p["key"] == "models")
    for brief in (everyday, builder):
        assert promise in brief and selection["editorial_review"]["viewer_question"] in brief
        for name in ("prompts/research.md", "prompts/example.md", "prompts/playlists/models.md"):
            assert (ROOT / name).read_text(encoding="utf-8") in brief
    assert (ROOT / "prompts/playlists/everyday.md").read_text(encoding="utf-8") in everyday
    assert (ROOT / "prompts/playlists/builder.md").read_text(encoding="utf-8") in builder
    assert "## prompts/playlists/builder.md" not in everyday
    assert "## prompts/playlists/everyday.md" not in builder


def publisher_fixture():
    yt = MagicMock()
    cfg = {"channel_id": "channel", "description": "Description", "keywords": "AI", "playlists": [
        {"key": "models", "title": "Models", "description": "Models"},
        {"key": "builder", "title": "Builders", "description": "Builders"}]}
    channel = {"id": "channel", "brandingSettings": {"channel": {
        "description": "Description", "keywords": "AI", "defaultLanguage": "en"}}}
    playlists = [{"id": p["key"], "snippet": {"title": p["title"], "description": p["description"],
                   "channelId": "channel"}, "status": {"privacyStatus": "public"}} for p in cfg["playlists"]]
    members = {"models": [{"id": "wrong-association", "contentDetails": {"videoId": "video"}},
                          {"id": "manual-association", "contentDetails": {"videoId": "manual"}}], "builder": []}
    yt.channels().list().execute.side_effect = lambda: {"items": [copy.deepcopy(channel)]}
    def list_playlists(**kw):
        req = MagicMock(); req.execute.return_value = {"items": copy.deepcopy([
            p for p in playlists if "id" not in kw or p["id"] == kw["id"]])}; return req
    yt.playlists().list.side_effect = list_playlists
    def list_members(**kw):
        req = MagicMock(); req.execute.return_value = {"items": copy.deepcopy(members[kw["playlistId"]])}; return req
    yt.playlistItems().list.side_effect = list_members
    def delete(**kw):
        for key in members:
            members[key][:] = [m for m in members[key] if m["id"] != kw["id"]]
        return MagicMock()
    yt.playlistItems().delete.side_effect = delete
    def insert(**kw):
        snippet = kw["body"]["snippet"]
        members[snippet["playlistId"]].append({"id": "correct-association", "contentDetails": {"videoId": snippet["resourceId"]["videoId"]}})
        return MagicMock()
    yt.playlistItems().insert.side_effect = insert
    yt.videos().list().execute.return_value = {"items": [{"snippet": {"channelId": "channel"}, "status": {"privacyStatus": "public"}}]}
    episodes = {"2026-09-28": {"date": "2026-09-28", "kind": "daily", "topics": ["models", "agents"], **route()}}
    receipts = {"2026-09-28": {"channel_id": "channel", "actual_privacy": "public", "video_id": "video"}}
    return yt, cfg, episodes, receipts, members


def test_remove_wrong_associations_preserve_manual_members_and_second_run_is_idle():
    yt, cfg, episodes, receipts, members = publisher_fixture()
    channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    assert members["models"] == [{"id": "manual-association", "contentDetails": {"videoId": "manual"}}]
    assert [m["contentDetails"]["videoId"] for m in members["builder"]] == ["video"]
    assert yt.playlistItems().delete.call_count == 1
    assert yt.playlistItems().insert.call_count == 1
    yt.videos().delete.assert_not_called()


def test_incomplete_review_blocks_all_mutations_and_failed_removal_is_detected():
    yt, cfg, episodes, receipts, members = publisher_fixture()
    episodes["2026-09-28"]["playlist_review"]["status"] = "pending"
    with pytest.raises(ValueError, match="approved"):
        channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    yt.playlistItems().delete.assert_not_called()
    yt.playlistItems().insert.assert_not_called()
    yt.channels().update.assert_not_called()
    episodes["2026-09-28"]["playlist_review"]["status"] = "approved"
    yt.playlistItems().delete.side_effect = None
    with pytest.raises(ValueError, match="membership verification"):
        channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)


def test_mixed_archive_can_be_excluded_but_new_unassigned_video_is_blocked():
    yt, cfg, episodes, receipts, members = publisher_fixture()
    exclusion = {"primary_playlist": None, "prompt_profile": None,
                 "playlist_review": {"status": "approved", "disposition": "unassigned",
                     "reviewer": "publisher", "reason": "Mixed prerequisites do not fit a specialist playlist."}}
    cfg["archive_routes"] = {"2026-09-28": exclusion}
    channel_sync.synchronize(yt, cfg, episodes, receipts, apply=True)
    assert members["models"] == [{"id": "manual-association", "contentDetails": {"videoId": "manual"}}]
    assert not members["builder"]
    yt.playlistItems().insert.assert_not_called()
    yt.videos().delete.assert_not_called()
    future = {"date": "2026-09-29", "kind": "daily", **exclusion}
    assert any("primary_playlist" in error for error in content_routing.episode_problems(future))


def test_description_links_only_to_the_reviewed_whole_video_route(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir(); (tmp_path / "config").mkdir()
    (tmp_path / "config/channel.json").write_text(json.dumps({"archive_routes": {"2026-09-28": route()}}))
    (tmp_path / "data/channel_state.json").write_text(json.dumps({"playlists": {
        "builder": {"title": "Builders", "url": "https://youtube.com/playlist?list=builders"},
        "models": {"title": "Models", "url": "https://youtube.com/playlist?list=models"}}}))
    monkeypatch.setattr(upload, "ROOT", tmp_path)
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-28.json")
    result = upload.build_description(ep, tmp_path)
    assert "list=builders" in result and "list=models" not in result


def test_live_description_cleanup_preserves_metadata_and_retries_reads_only(monkeypatch):
    yt = MagicMock()
    snippet = {"channelId": "channel", "title": "Existing title", "categoryId": "28", "tags": ["Original tag"],
               "description": "Sources and credits\n\nExplore this topic:\nModels: https://youtube.com/playlist?list=models"}
    video = {"snippet": copy.deepcopy(snippet), "status": {"privacyStatus": "public"}}
    expected = "Sources and credits\n\nExplore this topic:\nBuilders: https://youtube.com/playlist?list=builders"
    new_video = copy.deepcopy(video); new_video["snippet"]["description"] = expected
    yt.videos().list().execute.side_effect = [{"items": [video]}, {"items": [video]}, {"items": [new_video]}]
    monkeypatch.setattr(channel_sync.time, "sleep", lambda _: None)
    episodes = {"2026-09-28": {"date": "2026-09-28", "kind": "daily", **route()}}
    receipts = {"2026-09-28": {"channel_id": "channel", "actual_privacy": "public", "video_id": "video"}}
    channel_sync.synchronize_description_links(yt, {"channel_id": "channel"}, episodes, receipts,
        {"playlists": {"builder": {"title": "Builders", "url": "https://youtube.com/playlist?list=builders"}}}, apply=True)
    body = yt.videos().update.call_args.kwargs["body"]["snippet"]
    assert body["description"] == expected and body["title"] == snippet["title"] and body["tags"] == snippet["tags"]
    assert yt.videos().update.call_count == 1
