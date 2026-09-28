"""The deployed archive sitemap must follow new and removed articles automatically."""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import render_page


def test_archive_rebuild_updates_sitemap_for_distinct_same_day_articles(tmp_path, monkeypatch):
    episodes = tmp_path / "episodes"
    episodes.mkdir()
    site = tmp_path / "site"
    monkeypatch.setattr(render_page, "EPISODES", episodes)
    monkeypatch.setattr(render_page, "SITE", site)
    monkeypatch.setattr(render_page.brand, "channel_logo", lambda: "")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    def locations():
        render_page.render_index()
        tree = ET.parse(site / "sitemap.xml")
        assert not tree.findall(".//s:lastmod", namespace)
        return [el.text for el in tree.findall("s:url/s:loc", namespace)]

    base = render_page.SITE_URL
    assert locations() == [base]
    keys = ["2026-09-28-agents", "2026-09-28-repositories"]
    for key in keys:
        (episodes / f"{key}.json").write_text(json.dumps({
            "date": "2026-09-28", "episode_id": key, "title": "An article", "kind": "daily", "items": []
        }), encoding="utf-8")
    (episodes / "broken.json").write_text("invalid", encoding="utf-8")
    expected = {base, *(f"{base}{key}/index.html" for key in keys)}
    assert set(locations()) == expected
    assert len(locations()) == 3
    (episodes / f"{keys[0]}.json").unlink()
    assert set(locations()) == {base, f"{base}{keys[1]}/index.html"}
