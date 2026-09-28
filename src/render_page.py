"""Stage 5d — RENDER site page. episode JSON -> site/YYYY-MM-DD/index.html, plus a refreshed
site/index.html archive across every episode in data/episodes/. Copies the PDFs/brief already
built by render_artifacts.py into site/YYYY-MM-DD/ so GitHub Pages can serve them directly.

Usage:
  python src/render_page.py data/episodes/2026-08-28.json --video-url https://youtu.be/XXXXXXXXX
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand  # noqa: E402
import schema  # noqa: E402
from episode_identity import episode_key  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"
SITE = ROOT / "site"
EPISODES = ROOT / "data" / "episodes"

REPO_URL = "https://github.com/marcocm28/ai-daily-diff"
SITE_URL = "https://marcocm28.github.io/ai-daily-diff/"
ANALYTICS_CONFIG = ROOT / "config" / "analytics.json"

KIND_LABELS = {"daily": "Daily Diff", "method": "Method Diff", "deep": "Deep Diff"}


def analytics_id() -> str:
    """Analytics is optional; reject malformed IDs before putting them in JavaScript."""
    if not ANALYTICS_CONFIG.exists():
        return ""
    value = json.loads(ANALYTICS_CONFIG.read_text(encoding="utf-8")).get("measurement_id", "")
    if value and (not isinstance(value, str) or not re.fullmatch(r"G-[A-Z0-9]+", value)):
        raise ValueError("Invalid GA4 measurement_id in config/analytics.json")
    return value


def render_episode_page(episode: dict, video_url: str) -> pathlib.Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    template = env.get_template("page.html")

    html = template.render(
        analytics_id=analytics_id(),
        logo_uri=brand.channel_logo(),
        episode_title=episode["title"],
        meta_description=episode.get("closing_line", episode["title"]),
        date_label=episode["date"],
        kind_label=KIND_LABELS.get(episode["kind"], episode["kind"]),
        items=episode["items"],
        video_url=video_url or "#",
        repo_url=REPO_URL,
    )

    ep_dir = SITE / episode_key(episode)
    ep_dir.mkdir(parents=True, exist_ok=True)
    out_path = ep_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")

    src_dir = OUTPUT / episode_key(episode)
    for name in ("slides.pdf", "cheatsheet.pdf", "brief.md", "thumbnail.png"):
        src = src_dir / name
        if src.exists():
            shutil.copy2(src, ep_dir / name)

    return out_path


def render_index() -> pathlib.Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    template = env.get_template("index.html")

    episodes = []
    for path in sorted(EPISODES.glob("*.json"), reverse=True):
        try:
            ep = schema.load_episode(path)
            key = episode_key(ep)
        except Exception:  # noqa: BLE001 — a malformed episode file shouldn't break the archive
            continue
        episodes.append({
            "date": key,
            "date_label": ep["date"],
            "kind_label": KIND_LABELS.get(ep.get("kind"), ep.get("kind", "")),
            "title": ep.get("title", ep["date"]),
            "search_text": " ".join([ep.get("title", ""), ep["date"], ep.get("kind", ""),
                *ep.get("topics", []), *ep.get("audiences", []),
                *(item.get("headline", "") for item in ep.get("items", []))]),
        })

    html = template.render(episodes=episodes, repo_url=REPO_URL, logo_uri=brand.channel_logo(),
                           analytics_id=analytics_id())
    SITE.mkdir(parents=True, exist_ok=True)
    out_path = SITE / "index.html"
    out_path.write_text(html, encoding="utf-8")
    # Keep ownership verification available through every site rebuild.
    for verification in (ROOT / "config" / "site-verification").glob("google*.html"):
        shutil.copy2(verification, SITE / verification.name)
    render_sitemap(episodes)
    return out_path


def render_sitemap(episodes: list[dict]) -> pathlib.Path:
    """Publish the same article URLs as the archive, including same-day episodes."""
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("", namespace)
    urlset = ET.Element(f"{{{namespace}}}urlset")
    locations = [SITE_URL, *(f"{SITE_URL}{ep['date']}/index.html" for ep in episodes)]
    for location in dict.fromkeys(locations):
        entry = ET.SubElement(urlset, f"{{{namespace}}}url")
        ET.SubElement(entry, f"{{{namespace}}}loc").text = location
    # Publication dates do not reliably describe later content edits; omit lastmod.
    out_path = SITE / "sitemap.xml"
    ET.ElementTree(urlset).write(out_path, encoding="utf-8", xml_declaration=True)
    return out_path


def run(episode_path: pathlib.Path, video_url: str = "") -> None:
    episode = schema.load_episode(episode_path)
    problems = schema.validate_episode(episode)
    if problems:
        print(f"Refusing to render — schema/Gate 1 problems in {episode_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    ep_page = render_episode_page(episode, video_url)
    index_page = render_index()
    print(f"episode page -> {ep_page}")
    print(f"archive index -> {index_page}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    parser.add_argument("--video-url", default="")
    args = parser.parse_args()
    run(pathlib.Path(args.episode_json), args.video_url)
