# AI Daily Diff

> A daily AI-news brief, in English, where every claim links to a primary source and every
> code example actually runs. No generative AI is used to make the videos: slides are HTML/CSS,
> screenshots are Chromium, video is ffmpeg, charts are matplotlib.

- Channel: youtube.com/@aidailydiff
- Format: silent (no voice), on-screen text + code that builds itself + background music
- Cadence: **Daily Diff** (weekdays, 3:30-5:00) + **Deep Diff** (weekly, 10-15 min)
- Five verticals: Architectures & Models · Agents & Prompting · Video & Image Generation ·
  Data & Evaluation · Serving, Inference & Cost

Full project spec, decisions, and rationale: [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md).
Read it before changing anything — it is the single source of truth for *why* this repo looks
the way it does.

## One episode, one file, five outputs

Everything about one episode lives in `data/episodes/YYYY-MM-DD.json`. Video, `slides.pdf`,
`cheatsheet.pdf`, `brief.md` and the episode web page are all pure functions of that one file.

## Daily flow

```
1. INGEST    src/ingest.py        → data/inbox/YYYY-MM-DD.json          (free public APIs)
2. SELECT    src/select.py        → data/inbox/YYYY-MM-DD.selected.json (score + dedup)
3. AUTHOR    src/author.py        → data/episodes/YYYY-MM-DD.json       (draft, then filled by hand / by Claude)
4. EXAMPLES  examples/YYYY-MM-DD-slug/run.sh  — written, run, output captured for real
5. RENDER    src/render_video.py, src/render_artifacts.py, src/thumbnail.py, src/render_page.py
6. GATE      Marco watches the video and approves or drops it — never automatic
7. PUBLISH   git push → CI re-runs every example on a clean machine → GitHub Pages + YouTube upload
```

Steps 1-5 are normally run inside a Claude session (ingestion needs judgment, authoring needs
writing). Step 7's CI re-run is what actually earns the "TESTED IN CI ✓" badge — nothing is
self-certified.

## Setup

```
pip install -r requirements.txt
playwright install chromium   # first time only, if not already present
```

See `PROJECT_INSTRUCTIONS.md` §14 for the one-time manual setup (Google Cloud OAuth, YouTube,
GitHub secrets).

## License

Code: MIT (see individual files). Cheat sheets and slides: CC BY 4.0 — see `assets/LICENSES.md`.
