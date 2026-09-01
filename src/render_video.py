"""Stage 5a — RENDER video. episode JSON -> MP4. No generative AI: Chromium screenshots an
HTML/CSS deck, ffmpeg assembles the screenshots into a silent video, matplotlib draws any chart.

Usage:
  python src/render_video.py data/episodes/2026-08-28.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import schema  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"

W, H, FPS = 1920, 1080, 30
CHANNEL_TAG = "AI DAILY DIFF"

# Reading-speed formula — RECIPE.md is the human-readable copy of this constant. If the loop
# changes reading_speed_coeff, change it in both places in the same commit.
WORDS_PER_SECOND_COEFF = 0.35
BASE_HOLD = 0.5
MIN_HOLD, MAX_HOLD = 0.9, 4.5
CHART_BONUS = 1.8
CODE_FINAL_BONUS = 2.5
SOURCE_BONUS = 2.2


def word_count(*texts: str) -> int:
    return sum(len(t.split()) for t in texts if t)


def hold_for(new_words: int, *, chart: bool = False, code_final: bool = False,
             source: bool = False) -> float:
    base = max(MIN_HOLD, min(MAX_HOLD, WORDS_PER_SECOND_COEFF * new_words + BASE_HOLD))
    bonus = (CHART_BONUS if chart else 0) + (CODE_FINAL_BONUS if code_final else 0) + (SOURCE_BONUS if source else 0)
    return round(base + bonus, 2)


def build_chart(item: dict, out_dir: pathlib.Path) -> str | None:
    """Optional: only draws a chart if the item supplies chart_data as [[x, y], ...] pairs.
    No generative AI — this is matplotlib plotting numbers the item already carries."""
    data = item.get("chart_data")
    if not data:
        return None
    xs = [p[0] for p in data]
    ys = [p[1] for p in data]
    fig, ax = plt.subplots(figsize=(14, 5.2), dpi=100)
    fig.patch.set_facecolor("#121821"); ax.set_facecolor("#121821")
    ax.plot(xs, ys, color="#4CC2FF", lw=4)
    ax.fill_between(xs, ys, color="#4CC2FF", alpha=0.13)
    ax.set_xlabel(item.get("chart_xlabel", ""), color="#8494A8", fontsize=17, labelpad=14)
    ax.set_ylabel(item.get("chart_ylabel", ""), color="#8494A8", fontsize=17, labelpad=14)
    ax.tick_params(colors="#8494A8", labelsize=15)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color("#1E2733")
    ax.grid(True, color="#1E2733", lw=1)
    fig.tight_layout()
    out_path = out_dir / f"chart_{item['id']}.png"
    fig.savefig(out_path, facecolor="#121821")
    plt.close(fig)
    return out_path.name


def build_states_and_holds(episode: dict) -> tuple[list, list]:
    """Returns (STATES, HOLDS) — STATES is [[slide_id, [ids_shown]], ...], HOLDS is seconds."""
    items = episode["items"]
    n = len(items)
    states = []
    holds = []

    # cover: bare, then reveal each headline
    states.append(["cover", []])
    holds.append(hold_for(0))
    shown = []
    for i, item in enumerate(items):
        shown = shown + [f"hd{i}"]
        states.append(["cover", list(shown)])
        holds.append(hold_for(word_count(item["headline"])))

    for i, item in enumerate(items):
        rail = f"story{i}"
        states.append([rail, []])
        holds.append(hold_for(0))
        states.append([rail, [f"d{i}minus"]])
        holds.append(hold_for(word_count(item["diff"]["minus"])))
        states.append([rail, [f"d{i}minus", f"d{i}plus"]])
        holds.append(hold_for(word_count(item["diff"]["plus"])))
        states.append([rail, [f"d{i}minus", f"d{i}plus", f"card{i}why", f"card{i}who", f"src{i}"]])
        holds.append(hold_for(word_count(item["why_it_matters"], item["who_should_care"]), source=True))

        code = f"code{i}"
        states.append([code, []])
        holds.append(hold_for(word_count(item["example"]["caption"])))
        states.append([code, [f"codeblock{i}"]])
        holds.append(hold_for(word_count(item["example"]["code"])))
        states.append([code, [f"codeblock{i}", f"out{i}"]])
        holds.append(hold_for(word_count(item["example"]["output"]), code_final=True))

        num = f"num{i}"
        has_chart = bool(item.get("chart_data"))
        states.append([num, [f"numwrap{i}"]])
        holds.append(hold_for(word_count(item["the_number"]["value"], item["the_number"]["label"]),
                               chart=has_chart))

    states.append(["takeaway", []])
    holds.append(hold_for(word_count(episode.get("closing_line", ""))))

    return states, holds


def render_deck_html(episode: dict, out_dir: pathlib.Path) -> pathlib.Path:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)
    template = env.get_template("deck.html")

    items = []
    for item in episode["items"]:
        chart_name = build_chart(item, out_dir)
        items.append({**item, "chart_path": chart_name})

    cover_lines = episode.get("cover_title", "Three things that shipped today.").split("|", 1)
    cover1 = cover_lines[0]
    cover2 = cover_lines[1] if len(cover_lines) > 1 else ""

    html = template.render(
        channel_tag=CHANNEL_TAG,
        date_label=episode["date"],
        cover_title_line1=cover1,
        cover_title_line2=cover2,
        items=items,
        closing_line=episode.get("closing_line", ""),
        tagline="A NEW DIFF EVERY WEEKDAY",
    )
    out_path = out_dir / "deck_rendered.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def capture_frames(deck_path: pathlib.Path, states: list, frames_dir: pathlib.Path) -> None:
    frames_dir.mkdir(parents=True, exist_ok=True)
    states_json = json.dumps(states)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(deck_path.as_uri())
        page.wait_for_timeout(200)
        page.evaluate(f"window.STATES = {states_json};")
        page.wait_for_timeout(100)
        for i in range(len(states)):
            page.evaluate(f"applyState({i})")
            page.wait_for_timeout(60)
            page.screenshot(path=str(frames_dir / f"s{i:03d}.png"))
        browser.close()


def assemble_video(frames_dir: pathlib.Path, holds: list, out_path: pathlib.Path,
                    music_path: pathlib.Path | None = None) -> None:
    n = len(holds)
    list_path = frames_dir / "list.txt"
    with list_path.open("w") as f:
        for i in range(n):
            f.write(f"file 's{i:03d}.png'\nduration {holds[i]}\n")
        f.write(f"file 's{n - 1:03d}.png'\n")  # ffmpeg concat quirk: last frame needs repeating

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
    ]
    if music_path and music_path.exists():
        total_duration = sum(holds)
        cmd += ["-stream_loop", "-1", "-i", str(music_path),
                "-shortest", "-c:a", "aac", "-b:a", "128k",
                "-af", "volume=0.18"]
    cmd += ["-vf", f"fps={FPS},format=yuv420p,scale={W}:{H}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-movflags", "+faststart", str(out_path)]
    subprocess.run(cmd, check=True, cwd=str(frames_dir))


def run(episode_path: pathlib.Path) -> pathlib.Path:
    episode = schema.load_episode(episode_path)
    problems = schema.validate_episode(episode)
    if problems:
        print(f"Refusing to render — schema/Gate 1 problems in {episode_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    ep_out_dir = OUTPUT / episode["date"]
    ep_out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = pathlib.Path(tmp)
        deck_path = render_deck_html(episode, tmp_dir)
        states, holds = build_states_and_holds(episode)
        capture_frames(deck_path, states, tmp_dir)

        music_files = sorted((ROOT / "assets" / "music").glob("*.mp3"))
        music_path = music_files[0] if music_files else None

        video_path = ep_out_dir / "video.mp4"
        assemble_video(tmp_dir, holds, video_path, music_path=music_path)

    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(video_path)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(result.stdout)["format"]
    print(f"{len(states)} states -> {video_path}  "
          f"{float(info['duration']):.1f}s  {int(info['size']) / 1e6:.2f} MB")
    return video_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    args = parser.parse_args()
    run(pathlib.Path(args.episode_json))
