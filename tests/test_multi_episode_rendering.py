"""Same-day episode assets and archive links must never overwrite each other."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import render_artifacts
import render_page


def test_same_day_pages_downloads_and_archive_keep_distinct_episode_identity(tmp_path, monkeypatch):
    output = tmp_path / "output"
    site = tmp_path / "site"
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    monkeypatch.setattr(render_page, "OUTPUT", output)
    monkeypatch.setattr(render_page, "SITE", site)
    monkeypatch.setattr(render_page, "EPISODES", episodes)
    monkeypatch.setattr(render_page.brand, "channel_logo", lambda: "")
    for suffix, title in ((None, "Legacy daily"), ("agents", "Agent workflow"),
                          ("repositories", "Repository walkthrough")):
        key = "2026-09-28" + (f"-{suffix}" if suffix else "")
        episode = {"date": "2026-09-28", "title": title, "kind": "daily", "items": []}
        if suffix:
            episode["episode_id"] = key
        (episodes / f"{key}.json").write_text(json.dumps(episode), encoding="utf-8")
        asset_dir = output / key
        asset_dir.mkdir(parents=True)
        (asset_dir / "slides.pdf").write_bytes(title.encode())
        render_artifacts.render_brief_md(episode, asset_dir / "brief.md")
        page = render_page.render_episode_page(episode, f"https://youtu.be/{suffix or 'legacy'}")
        assert page == site / key / "index.html"
        assert (page.parent / "slides.pdf").read_bytes() == title.encode()
        html = page.read_text(encoding="utf-8")
        assert title in html
        assert "2026-09-28 · Daily Diff" in html
        if suffix:
            assert key + " · Daily Diff" not in html
        brief = (page.parent / "brief.md").read_text(encoding="utf-8")
        assert f"/{key}/slides.pdf" in brief
        assert f"/{key}/cheatsheet.pdf" in brief
        assert f"/{key}/" in brief
    archive = render_page.render_index().read_text(encoding="utf-8")
    for key in ("2026-09-28", "2026-09-28-agents", "2026-09-28-repositories"):
        assert f'href="{key}/index.html"' in archive
    assert archive.count("2026-09-28 · Daily Diff") == 3
