"""Stage 5b — RENDER companions. episode JSON -> slides.pdf, cheatsheet.pdf, brief.md.
All three are pure functions of data/episodes/YYYY-MM-DD.json — same source as the video.

Usage:
  python src/render_artifacts.py data/episodes/2026-08-28.json
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import schema  # noqa: E402
from render_video import build_chart, CHANNEL_TAG  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"

REPO_URL = "https://github.com/marcocm28/ai-daily-diff"
PAGES_BASE_URL = "https://marcocm28.github.io/ai-daily-diff"

# Forces every slide fully revealed and stacked one-per-page, regardless of how many
# reveal-states the video would normally step through. This is the only place slides.pdf
# differs from the video's own rendering path.
PRINT_CSS = """
  @page { size: 1920px 1080px; margin: 0; }
  body { width:1920px !important; height:auto !important; overflow:visible !important; }
  .slide { position:relative !important; display:flex !important;
           width:1920px; height:1080px; page-break-after:always; break-after:page; }
  .slide:last-child { page-break-after:auto; break-after:auto; }
  ul.head li, .card, pre, .out, .diff > div, .src, .numwrap { opacity:1 !important; }
"""


def render_slides_pdf(episode: dict, tmp_dir: pathlib.Path, out_path: pathlib.Path) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    template = env.get_template("deck.html")

    items = []
    for item in episode["items"]:
        chart_name = build_chart(item, tmp_dir)
        items.append({**item, "chart_path": chart_name})

    cover_lines = episode.get("cover_title", "Three things that shipped today.").split("|", 1)

    html = template.render(
        channel_tag=CHANNEL_TAG,
        date_label=episode["date"],
        cover_title_line1=cover_lines[0],
        cover_title_line2=(cover_lines[1] if len(cover_lines) > 1 else ""),
        items=items,
        closing_line=episode.get("closing_line", ""),
        tagline="A NEW DIFF EVERY WEEKDAY",
    )
    deck_path = tmp_dir / "deck_for_pdf.html"
    deck_path.write_text(html, encoding="utf-8")

    n_pages = 2 + len(episode["items"]) * 3

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(deck_path.as_uri())
        page.wait_for_timeout(200)
        page.add_style_tag(content=PRINT_CSS)
        page.wait_for_timeout(150)
        page.pdf(path=str(out_path), width="1920px", height="1080px", print_background=True,
                 page_ranges=f"1-{n_pages}",
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()


def render_cheatsheet_pdf(episode: dict, out_path: pathlib.Path) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    template = env.get_template("cheatsheet.html")
    html = template.render(
        items=episode["items"],
        date_label=episode["date"],
        date_label_iso=episode["date"],
        episode_title=episode["title"],
        repo_url=REPO_URL,
        pages_base_url=PAGES_BASE_URL,
    )
    with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
        f.write(html)
        tmp_path = pathlib.Path(f.name)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(tmp_path.as_uri())
        page.wait_for_timeout(200)
        page.pdf(path=str(out_path), format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        browser.close()
    tmp_path.unlink(missing_ok=True)


def render_brief_md(episode: dict, out_path: pathlib.Path) -> None:
    lines = [f"# {episode['title']}", "", episode["date"], "",
             "Every claim below links to a primary source. Every example is executed in CI "
             "before this video is published; if an example fails, the video does not ship.", ""]
    for i, item in enumerate(episode["items"], start=1):
        lines += [
            f"## {i:02d} · {item['headline']}",
            f"**Vertical:** {item['vertical_label']}",
            "",
            f"WHAT CHANGED — {item['what_changed']}",
            f"WHY IT MATTERS — {item['why_it_matters']}",
            f"THE NUMBER — {item['the_number']['value']} ({item['the_number']['label']})",
            "",
            f"Run it yourself ({item['example']['run_summary']}):",
            f"  {item['example']['dir']}/",
            "",
        ]
        if item.get("watch_out"):
            lines += [f"Caveat: {item['watch_out']}", ""]
        lines += [
            f"Primary source: {item['source_url']}",
            f"Tested example: {REPO_URL}/tree/main/{item['example']['dir']}",
            "",
        ]

    date = episode["date"]
    lines += [
        "---",
        f"Slides (PDF): {PAGES_BASE_URL}/{date}/slides.pdf      "
        f"Cheat sheet (PDF): {PAGES_BASE_URL}/{date}/cheatsheet.pdf",
        f"Episode page: {PAGES_BASE_URL}/{date}/",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def run(episode_path: pathlib.Path) -> pathlib.Path:
    episode = schema.load_episode(episode_path)
    problems = schema.validate_episode(episode)
    if problems:
        print(f"Refusing to render — schema/Gate 1 problems in {episode_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    out_dir = OUTPUT / episode["date"]
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        slides_path = out_dir / "slides.pdf"
        render_slides_pdf(episode, tmp_dir, slides_path)

    cheatsheet_path = out_dir / "cheatsheet.pdf"
    render_cheatsheet_pdf(episode, cheatsheet_path)

    brief_path = out_dir / "brief.md"
    render_brief_md(episode, brief_path)

    for f in (slides_path, cheatsheet_path, brief_path):
        print(f"{f.name:16} {f.stat().st_size / 1024:8.1f} KB")

    return out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    args = parser.parse_args()
    run(pathlib.Path(args.episode_json))
