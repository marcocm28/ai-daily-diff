"""Stage 5a — RENDER video. episode JSON -> MP4. No generative AI: Chromium screenshots an
HTML/CSS deck, ffmpeg assembles the screenshots into a silent video, matplotlib draws any chart.

Usage:
  python src/render_video.py data/episodes/2026-08-28.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from jinja2 import Environment, FileSystemLoader  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand  # noqa: E402
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

# Music level. The bed is the ONLY audio in a silent-format video, which changes the maths:
# a fixed "-15 dB under the voice" is wrong when there is no voice. YouTube normalises loud
# content down to about -14 LUFS but does not raise quiet content, so a bed mixed to -26 LUFS
# just plays quiet and the viewer turns their volume up — then the next video shouts at them.
# So we measure the track's integrated loudness and compute the gain that lands it here:
# clearly quieter than a music video, loud enough to need no volume change.
MUSIC_TARGET_LUFS = -18.0
CODE_FINAL_BONUS = 2.5
SOURCE_BONUS = 2.2


def word_count(*texts: str) -> int:
    return sum(len(t.split()) for t in texts if t)


def hold_for(new_words: int, *, chart: bool = False, code_final: bool = False,
             source: bool = False) -> float:
    base = max(MIN_HOLD, min(MAX_HOLD, WORDS_PER_SECOND_COEFF * new_words + BASE_HOLD))
    bonus = (CHART_BONUS if chart else 0) + (CODE_FINAL_BONUS if code_final else 0) + (SOURCE_BONUS if source else 0)
    return round(base + bonus, 2)


def measure_loudness(path: pathlib.Path) -> float | None:
    """Integrated loudness in LUFS, via ffmpeg's EBU R128 meter. None if it cannot be read."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True, check=False,
    )
    # ebur128 prints a running "I:" line throughout the file and then the final one in its
    # Summary. Taking the FIRST match gives -70.0, the meter's starting placeholder — which is
    # how this first computed a +52 dB gain and produced a video at +10 LUFS. Take the last.
    matches = re.findall(r"I:\s*(-?\d+\.\d+)\s*LUFS", result.stderr)
    return float(matches[-1]) if matches else None


def build_chart(item: dict, out_dir: pathlib.Path) -> str | None:
    """Optional. Draws a chart only if the item supplies one, in either form:

        "chart_data": [[x, y], ...]                       — single series
        "chart": {"xlabel": .., "ylabel": .., "series": [{"label": .., "data": [[x, y], ..]}, ..]}

    No generative AI: matplotlib plotting numbers the item already carries, which are themselves
    computed by the item's own example. A chart here is never decorative — if there is nothing to
    plot, the slide is the number alone.
    """
    chart = item.get("chart")
    if not chart and item.get("chart_data"):
        chart = {"xlabel": item.get("chart_xlabel", ""), "ylabel": item.get("chart_ylabel", ""),
                 "series": [{"label": "", "data": item["chart_data"]}]}
    if not chart:
        return None

    colors = ["#4CC2FF", "#FFB74C", "#5BD6A0"]
    fig, ax = plt.subplots(figsize=(14, 4.2), dpi=100)
    fig.patch.set_facecolor("#121821"); ax.set_facecolor("#121821")
    for idx, s in enumerate(chart["series"]):
        xs = [p[0] for p in s["data"]]
        ys = [p[1] for p in s["data"]]
        color = colors[idx % len(colors)]
        ax.plot(xs, ys, color=color, lw=4, label=s.get("label") or None)
        ax.fill_between(xs, ys, color=color, alpha=0.10)
    ax.set_xlabel(chart.get("xlabel", ""), color="#8494A8", fontsize=19, labelpad=12)
    ax.set_ylabel(chart.get("ylabel", ""), color="#8494A8", fontsize=19, labelpad=12)
    ax.tick_params(colors="#8494A8", labelsize=17)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    for s_ in ("bottom", "left"):
        ax.spines[s_].set_color("#1E2733")
    ax.grid(True, color="#1E2733", lw=1)
    ax.set_ylim(bottom=0)
    if any(s.get("label") for s in chart["series"]):
        leg = ax.legend(loc="upper left", fontsize=18, frameon=False)
        for txt, s in zip(leg.get_texts(), chart["series"]):
            txt.set_color("#E8EDF4")
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
        has_chart = bool(item.get("chart") or item.get("chart_data"))
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
        items.append({**item, "chart_path": chart_name,
                       "org_logo_uri": brand.vendor_logo(item.get("org"))})

    cover_lines = episode.get("cover_title", "Three things that shipped today.").split("|", 1)
    cover1 = cover_lines[0]
    cover2 = cover_lines[1] if len(cover_lines) > 1 else ""

    html = template.render(
        logo_uri=brand.channel_logo(),
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
        scales = page.evaluate("fitSlides()")
        for i, k in enumerate(scales):
            if k < 1:
                print(f"  code slide {i}: content scaled to {k:.3f} to fit 1080p")
        page.wait_for_timeout(80)
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
        total = sum(holds)
        fade = 1.5
        measured = measure_loudness(music_path)
        gain_db = (MUSIC_TARGET_LUFS - measured) if measured is not None else -15.0
        gain = 10 ** (gain_db / 20)
        print(f"  music: {music_path.name} measured {measured} LUFS -> "
              f"{gain_db:+.1f} dB to reach {MUSIC_TARGET_LUFS} LUFS")
        # Looped to length and faded at both ends, so a loop point never lands as a hard cut.
        # RECIPE.md carries `music_bed` as a Loop A variable: the target, not this arithmetic,
        # is what the loop may change.
        cmd += ["-stream_loop", "-1", "-i", str(music_path),
                "-shortest", "-c:a", "aac", "-b:a", "128k",
                "-af", f"volume={gain:.4f},afade=t=in:st=0:d={fade},"
                        f"afade=t=out:st={max(0.0, total - fade):.2f}:d={fade}"]
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
