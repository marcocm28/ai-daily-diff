"""Documented explanations must never masquerade as executed product tests."""
import copy
import datetime as dt
import json
import pathlib
import sys

import pytest
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import schema
import publication
import render_video
import render_artifacts
import upload


@pytest.fixture
def episode():
    return schema.load_episode(ROOT / "data/episodes/2026-09-27.json")


@pytest.mark.parametrize("field", ["use_case", "steps", "availability", "limitations", "evidence_label", "docs_url"])
def test_missing_documented_evidence_blocks_release(episode, field):
    del episode["items"][0]["walkthrough"][field]
    assert schema.validate_episode(episode)
    assert not schema.verify_example(episode["items"][0])[0]


@pytest.mark.parametrize("field", ["example", "the_number", "chart", "chart_data"])
def test_documented_cannot_carry_execution_or_measurement_fields(episode, field):
    episode["items"][0][field] = {}
    assert schema.validate_episode(episode)


def test_contract_pass_is_separate_from_ci_execution_badge(episode):
    item = episode["items"][0]
    assert schema.validate_episode(episode) == []
    assert schema.verify_example(item)[0]
    schema.stamp_checks(item, False)
    assert not schema.checks_stamped(item)
    schema.stamp_checks(item, True)
    assert schema.checks_stamped(item)
    assert "example" not in item
    item["source_review"]["status"] = "pending"
    assert not schema.checks_stamped(item)


def test_documented_renderers_need_no_number_or_example(episode, tmp_path):
    deck = render_video.render_deck_html(episode, tmp_path).read_text(encoding="utf-8")
    states, holds = render_video.build_states_and_holds(episode)
    assert len(states) == len(holds) and all(h > 0 for h in holds)
    assert "DOCUMENTED CAPABILITY" in deck and "TESTED IN CI" not in deck
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), undefined=StrictUndefined)
    # Supply optional properties just as renderers do. Required evidence remains intact.
    items = [{**item, "watch_out": ""} for item in episode["items"]]
    for name in ("page.html", "cheatsheet.html"):
        html = env.get_template(name).render(items=items, logo_uri="", episode_title=episode["title"],
            meta_description="", date_label=episode["date"], date_label_iso=episode["date"],
            kind_label="Daily Diff", video_url="#", repo_url="", pages_base_url="")
        assert "not a live" in html.lower() or "not tested live" in html.lower()
        assert "TESTED IN CI" not in html
    brief = tmp_path / "brief.md"
    render_artifacts.render_brief_md(episode, brief)
    assert "not a live product test" in brief.read_text(encoding="utf-8")
    description = upload.build_description(episode, tmp_path)
    assert "Project repository:" in description and "All code:" not in description
    assert episode["items"][0]["source_url"] in description


def test_manifest_requires_documented_ci_check(episode, tmp_path, monkeypatch):
    day = dt.datetime.now(dt.timezone.utc).date().isoformat()
    episode["date"] = day
    episode.update(topics=["models"], audiences=["builder"], primary_audience="builder",
        coverage_review={scope: {"status": "checked", "sources": ["https://example.org/source"],
            "decision": "no_qualifying_news", "reason": "Test fixture"} for scope in schema.strategy.SCOPES})
    episode["publication"] = {"ready": True}
    folder = tmp_path / "data/episodes"
    folder.mkdir(parents=True)
    path = folder / f"{day}.json"
    (tmp_path / "config").mkdir()
    (tmp_path / "config/publishing.json").write_text(json.dumps({"start_date": day}), encoding="utf-8")
    output = tmp_path / "output" / day
    output.mkdir(parents=True)
    for name in ("video.mp4", "thumbnail.png", "brief.md"):
        (output / name).write_bytes(b"verified fixture")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SHA", "test-commit")
    monkeypatch.setenv("GITHUB_RUN_ID", "test-run")
    schema.stamp_checks(episode["items"][0], False)
    path.write_text(json.dumps(episode), encoding="utf-8")
    with pytest.raises(ValueError, match="Evidence checks"):
        publication.build_manifest(tmp_path)
    schema.stamp_checks(episode["items"][0], True)
    path.write_text(json.dumps(episode), encoding="utf-8")
    manifest = publication.build_manifest(tmp_path)
    assert manifest["episodes"][0]["date"] == day
