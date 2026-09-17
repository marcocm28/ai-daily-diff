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

**Current workflow (2026-09-17):** ChatGPT research tasks → scheduled Codex
synchronization and authoring on the PC → verified episode pushed to main → GitHub
Render → automatic Pages + YouTube upload from that exact verified release.

The destination is **@aidailydiff**, channel ID `UCDEWpe6dU5_-3Im8KxQk5WA`.
The existing OAuth token uploaded to the personal channel instead; it must be
reconnected once. Upload refuses any other channel before sending video bytes.
See [setup and recovery](docs/AUTOMATION.md).

Codex checks at 13:30 and 17:30 Europe/Rome, Monday-Saturday, using the isolated
`.local/pipeline` clone and [scheduled instructions](prompts/scheduled-pipeline.md).
The PC, Codex and authenticated browser must be available. Daily episodes run on
weekdays; Saturday is the Method/Deep slot. GitHub still performs all video rendering.
`tools/queue_episode.py DATE` verifies a finished episode and marks it ready for CI.
The old `tools/run_daily.py` remains a manual draft tool, not the scheduled entrypoint.

CI output is retained as artifacts rather than committed binaries. The publisher
checks run provenance, SHA-256 digests, source reviews and the target channel. Durable
receipts in `data/publications/` and a channel-side episode marker prevent blind
re-uploads after failures. Only new, explicitly queued episodes can be published.

## ChatGPT radars

**AI Productivity Radar** and **Novità tecniche AI** provide editorial JSON exports.
The scheduled Codex task reads and imports them through the authenticated browser;
GitHub never receives browser credentials or private chat transcripts. Manual import
remains available via `python src/radar.py .local/radar/report.json`.
See [radar integration](docs/RADAR_INTEGRATION.md) and [research rules](prompts/research.md).

## Setup

Use Python **3.12**, matching CI. Direct Python dependencies are pinned; system
tools are separate: install **Git Bash** on Windows and **FFmpeg** for local video
rendering. Schema/example tests do not need Chromium or FFmpeg.

```
pip install -r requirements.txt
playwright install chromium   # first time only, if not already present
```

See `PROJECT_INSTRUCTIONS.md` §14 for the one-time manual setup (Google Cloud OAuth, YouTube,
GitHub secrets).

Run checks with `python -m pytest tests/ -q`. On Windows the example verifier locates
Git's Bash and passes the current Python interpreter to `run.sh`; no `python3` alias
is required. `python tools/doctor.py` reports missing local prerequisites.

## License

Code: MIT (see individual files). Cheat sheets and slides: CC BY 4.0 — see `assets/LICENSES.md`.
