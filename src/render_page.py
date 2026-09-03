"""Stage 5d — RENDER site page. episode JSON -> site/YYYY-MM-DD/index.html, plus a refreshed
site/index.html archive across every episode in data/episodes/. Copies the PDFs/brief already
built by render_artifacts.py into site/YYYY-MM-DD/ so GitHub Pages can serve them directly.

Usage:
  python src/render_page.py data/episodes/2026-08-28.json --video-url https://youtu.be/XXXXXXXXX
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand  # noqa: E402
import schema  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"
SITE = ROOT / "site"
EPISODES = ROOT / "data" / "episodes"

REPO_URL = "https://github.com/marcocm28/ai-daily-diff"

KIND_LABELS = {"daily": "Daily Diff", "method": "Method Diff", "deep": "Deep Diff"}


def render_episode_page(episode: dict, video_url: str) -> pathlib.Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    template = env.get_template("page.html")

    html = template.render(
        logo_uri=brand.channel_logo(),
        episode_title=episode["title"],
        meta_description=episode.get("closing_line", episode["title"]),
        date_label=episode["date"],
        kind_label=KIND_LABELS.get(episode["kind"], episode["kind"]),
        items=episode["items"],
        video_url=video_url or "#",
        repo_url=REPO_URL,
    )

    ep_dir = SITE / episode["date"]
    ep_dir.mkdir(parents=True, exist_ok=True)
    out_path = ep_dir / "index.html"
    out_path.write_text(html, encoding="utf-8")

    src_dir = OUTPUT / episode["date"]
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
        except Exception:  # noqa: BLE001 — a malformed episode file shouldn't break the archive
            continue
        episodes.append({
            "date": ep["date"],
            "date_label": ep["date"],
            "kind_label": KIND_LABELS.get(ep.get("kind"), ep.get("kind", "")),
            "title": ep.get("title", ep["date"]),
        })

    html = template.render(episodes=episodes, repo_url=REPO_URL, logo_uri=brand.channel_logo())
    SITE.mkdir(parents=True, exist_ok=True)
    out_path = SITE / "index.html"
    out_path.write_text(html, encoding="utf-8")
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
