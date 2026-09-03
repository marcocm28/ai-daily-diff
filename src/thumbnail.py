"""Stage 5c — RENDER thumbnail. episode JSON -> 1280x720 PNG.
Same engine as everything else: an HTML/CSS page, screenshotted by Chromium. No generative AI,
no faces, no red arrows, no company logos as the subject (PROJECT_INSTRUCTIONS.md §8.4).

Usage:
  python src/thumbnail.py data/episodes/2026-08-28.json
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand  # noqa: E402
import schema  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"

TEMPLATE = """
<meta charset="utf-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1280px; height:720px; overflow:hidden; background:#0B0F14;
          font-family:"DejaVu Sans",sans-serif; color:#E8EDF4; position:relative; }}
  .rail {{ position:absolute; left:0; top:0; width:16px; height:100%; background:{rail}; }}
  .kicker {{ position:absolute; top:52px; left:64px; font-size:26px; letter-spacing:.24em;
             color:{rail}; font-weight:700; }}
  .big {{ position:absolute; left:64px; top:196px; font-size:220px; font-weight:700;
          letter-spacing:-.03em; line-height:1; color:{rail}; }}
  .label {{ position:absolute; left:68px; bottom:64px; font-size:44px; font-weight:700;
            max-width:1020px; line-height:1.2; }}
  .tag {{ position:absolute; left:70px; top:52px; font-size:24px; font-weight:700;
          letter-spacing:.12em; color:#8494A8; }}
  .logo {{ position:absolute; right:56px; top:44px; height:132px; width:auto; }}
</style>
<div class="rail"></div>
{logo_tag}
<div class="tag">{date_label}</div>
<div class="big">{value}</div>
<div class="label">{label}</div>
"""


def run(episode_path: pathlib.Path) -> pathlib.Path:
    episode = schema.load_episode(episode_path)
    problems = schema.validate_episode(episode)
    if problems:
        print(f"Refusing to render — schema/Gate 1 problems in {episode_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    lead = episode["items"][0]
    logo_uri = brand.channel_logo()
    logo_tag = (f'<img class="logo" src="{logo_uri}" alt="AI Daily Diff">'
                if logo_uri else '<div class="kicker">AI DAILY DIFF</div>')
    html = TEMPLATE.format(
        logo_tag=logo_tag,
        rail=(episode.get("thumbnail_color")
              or lead.get("rail_color", "#4CC2FF")).replace("var(--accent)", "#4CC2FF")
                 .replace("var(--accent2)", "#FFB74C").replace("var(--ok)", "#3FD97F"),
        date_label=episode["date"],
        value=episode.get("thumbnail_text") or lead["the_number"]["value"],
        label=episode.get("thumbnail_label") or lead["headline"],
    )

    out_dir = OUTPUT / episode["date"]
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "_thumbnail.html"
    html_path.write_text(html, encoding="utf-8")
    out_path = out_dir / "thumbnail.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(html_path.as_uri())
        page.wait_for_timeout(150)
        page.screenshot(path=str(out_path))
        browser.close()

    html_path.unlink(missing_ok=True)
    print(f"thumbnail -> {out_path}")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    args = parser.parse_args()
    run(pathlib.Path(args.episode_json))
