import datetime as dt
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import radar
import selection
import author
import schema

TODAY = dt.date(2026, 9, 16)


def report():
    return {"task": "AI Productivity Radar", "date": TODAY.isoformat(), "items": [{
        "title": "Documented workflow", "url": "https://example.org/release?utm_source=chatgpt",
        "published_at": TODAY.isoformat(), "kind": "method", "vertical": "tools-agents",
        "summary": "A documented change", "decision": "Try on a fixed task",
        "example_idea": "Measure retry budget offline", "suggested_format": "daily",
        "is_primary_source": True, "confidence": 10, "private_chat": "not public",
    }]}


def test_import_is_idempotent_and_does_not_trust_radar_confidence(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(report()), encoding="utf-8")
    directory = tmp_path / "reports"
    first = radar.import_report(source, directory)
    assert radar.import_report(source, directory) == first
    content = json.loads(first.read_text(encoding="utf-8"))
    assert "confidence" not in content["items"][0]
    assert "private_chat" not in content["items"][0]
    candidates = radar.load_candidates(TODAY, directory)
    assert candidates[0]["is_primary_source"] is False
    assert candidates[0]["requires_source_review"] is True
    assert candidates[0]["url"] == "https://example.org/release"
    revised = report()
    revised["items"][0]["summary"] = "Changed"
    source.write_text(json.dumps(revised), encoding="utf-8")
    with pytest.raises(ValueError, match="different report"):
        radar.import_report(source, directory)


@pytest.mark.parametrize("url", ["https://chatgpt.com/c/private", "file:///secret",
                                 "https://user:password@example.org/", "https://localhost/test"])
def test_private_and_non_web_sources_are_rejected(url):
    with pytest.raises(ValueError):
        radar.canonical_url(url)


def test_old_and_future_reports_do_not_leak_into_today(tmp_path):
    source = tmp_path / "report.json"
    data = report()
    data["date"] = "2026-08-01"
    data["items"][0]["published_at"] = "2026-08-01"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert radar.load_candidates(TODAY, tmp_path) == []
    data["date"] = "2026-09-17"
    source.write_text(json.dumps(data), encoding="utf-8")
    assert radar.load_candidates(TODAY, tmp_path) == []


def configure(monkeypatch, tmp_path, candidates, radar_candidates=None):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    (inbox / f"{TODAY}.json").write_text(json.dumps({"candidates": candidates}), encoding="utf-8")
    monkeypatch.setattr(selection, "INBOX", inbox)
    monkeypatch.setattr(selection, "EPISODES", episodes)
    monkeypatch.setattr(selection, "DEDUP_INDEX", tmp_path / "index.json")
    monkeypatch.setattr(selection, "load_candidates", lambda _: radar_candidates or [])
    return inbox, episodes


def candidate(**overrides):
    return {"title": "A release", "url": "https://example.org/release", "source": "official",
            "published_at": TODAY.isoformat(), "kind": "tool_release",
            "vertical": "tools-agents", "is_primary_source": True, **overrides}


def selected():
    return json.loads(selection.run(TODAY).read_text(encoding="utf-8"))["selected"]


def test_below_floor_and_stale_candidates_do_not_fill_slots(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path, [candidate(),
        candidate(title="Old", url="https://example.org/old", published_at="2026-08-01"),
        candidate(title="Weak", url="https://example.org/weak", kind="research", vertical="claims-risks")])
    result = selected()
    assert len(result) == 1 and result[0]["title"] == "A release"


def test_selections_are_repeatable_and_only_authored_episodes_dedup(monkeypatch, tmp_path):
    _, episodes = configure(monkeypatch, tmp_path, [candidate()])
    first = selected()
    assert selected() == first
    assert not selection.DEDUP_INDEX.exists()
    (episodes / "2026-09-15.json").write_text(json.dumps({"date": "2026-09-15", "items": [
        {"source_url": "https://example.org/release?utm_source=other"}]}), encoding="utf-8")
    assert selected() == []


def test_merge_radars_deduplicates_tracking_urls_and_keeps_weekly_backlog(monkeypatch, tmp_path):
    extra = candidate(title="Same story from a radar", url="https://example.org/release/?utm_source=x",
                      source="chatgpt-task:technical", is_primary_source=False, requires_source_review=True)
    weekly = candidate(url="https://example.org/weekly", suggested_format="method")
    configure(monkeypatch, tmp_path, [candidate()], [extra, weekly])
    assert len(selected()) == 1


def test_thin_day_widens_to_seven_days(monkeypatch, tmp_path):
    configure(monkeypatch, tmp_path, [candidate(published_at="2026-09-10")])
    result = selected()
    assert len(result) == 1 and result[0]["_freshness_window"] == 7


def test_weekly_selection_authors_one_topic_and_requires_review(monkeypatch, tmp_path):
    weekly = candidate(source="chatgpt-task:productivity", is_primary_source=False,
                       requires_source_review=True, suggested_format="method", kind="method")
    inbox, episodes = configure(monkeypatch, tmp_path, [candidate()], [weekly])
    result_path = selection.run(TODAY, kind="method")
    assert result_path.name.endswith(".method.selected.json")
    monkeypatch.setattr(author, "INBOX", inbox)
    monkeypatch.setattr(author, "EPISODES", episodes)
    path = author.run(TODAY, kind="method")
    episode = json.loads(path.read_text(encoding="utf-8"))
    assert len(episode["items"]) == 1
    assert episode["items"][0]["source_review"]["status"] == "pending"
    assert any("source_review" in p for p in schema.validate_episode(episode))


def test_radar_only_day_works_without_api_inbox(monkeypatch, tmp_path):
    extra = candidate(source="chatgpt-task:technical", is_primary_source=False,
                      requires_source_review=True)
    inbox, _ = configure(monkeypatch, tmp_path, [], [extra])
    (inbox / f"{TODAY}.json").unlink()
    assert len(selected()) == 1


def test_empty_report_does_not_invent_news():
    data = report()
    data["items"] = []
    assert radar.normalize_report(data)["items"] == []


def test_curated_deep_research_is_not_discarded_by_daily_news_floor(monkeypatch, tmp_path):
    research = candidate(kind="research", vertical="claims-risks", suggested_format="deep",
                         source="chatgpt-task:technical", is_primary_source=False,
                         requires_source_review=True)
    configure(monkeypatch, tmp_path, [], [research])
    path = selection.run(TODAY, kind="deep")
    items = json.loads(path.read_text(encoding="utf-8"))["selected"]
    assert len(items) == 1 and items[0]["requires_source_review"]
