# AI Daily Diff

> A daily AI-news brief, in English, where every claim links to a primary source and every
> code example actually runs. No generative AI is used to make the videos: slides are HTML/CSS,
> screenshots are Chromium, video is ffmpeg, charts are matplotlib.

- Channel: youtube.com/@aidailydiff
- Format: silent (no voice), on-screen text + code that builds itself + background music
- Cadence: **Daily Diff** (weekdays, 3 news items) + one weekly video, by default a
  **Method Diff** (4-6 min, one task and one measured method, title shaped like the search query).
  The 10-15 min **Deep Diff** is the occasional variant of that weekly slot.
- Five verticals: Models & Releases · Cost & Limits · Tools & Agents · Media Generation ·
  Claims & Risks

Full project spec, decisions, and rationale: [`PROJECT_INSTRUCTIONS.md`](PROJECT_INSTRUCTIONS.md).
Read it before changing anything — it is the single source of truth for *why* this repo looks
the way it does.

## One episode, one file, five outputs

Everything about one episode lives in `data/episodes/YYYY-MM-DD.json`. Video, `slides.pdf`,
`cheatsheet.pdf`, `brief.md` and the episode web page are all pure functions of that one file.

## Daily flow

```
1. INGEST    src/ingest.py        → data/inbox/YYYY-MM-DD.json          (free public APIs)
2. SELECT    src/selection.py     → data/inbox/YYYY-MM-DD.selected.json (score + dedup)
3. AUTHOR    src/author.py        → data/episodes/YYYY-MM-DD.json       (draft, then filled by hand / by Claude)
             prompts/daily.md for a brief · prompts/method.md for the weekly · prompts/deep.md for the long variant
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
