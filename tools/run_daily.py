"""Unattended daily driver — meant to be launched by Windows Task Scheduler, not by hand or from
inside a Claude/Codex session. Replaces the old "someone opens Claude, does ingestion/authoring,
renders, drags files into the browser" loop end to end, up to the point a human has to look at it.

Ingestion no longer happens here: this machine sits behind a corporate TLS-intercepting proxy that
breaks Python's certificate verification for every one of src/ingest.py's sources (confirmed
2026-09-10 — 24/24 sources failed with CERTIFICATE_VERIFY_FAILED). .github/workflows/ingest.yml
runs ingest.py + selection.py on a schedule on a clean GitHub runner and commits
data/inbox/<date>*.json straight to main instead. This script just needs that data to already be
on main by the time it runs (Task Scheduler should fire a couple of hours after ingest.yml's cron).

What it does, in order:
  1. pulls main; merges today's API inbox and imported radar reports into selection.
  2. author (src/author.py) — scaffolds data/episodes/<date>.json with TODO fields.
  3. hands the judgment work (headline/why-it-matters/diff/example) to a headless `codex exec` run,
     which must fill every TODO, build real examples/<date>-<slug>/ folders, and ACTUALLY RUN them
     to capture real output (never hand-type it — that's the entire premise of Gate 2).
  4. re-verifies Gate 1 + Gate 2 itself (never trusts Codex's own "done" claim).
  5. commits data/episodes/<date>.json + examples/<date>-*/ to a new draft/<date> branch and
     pushes it.
  6. prints the compare URL so a human opens it and clicks "Create pull request."

It never pushes to main and never opens/merges a PR — .github/workflows/render.yml renders a
preview on the PR for a human to review (PROJECT_INSTRUCTIONS.md §15, 28/08: "gate umano su ogni
video", never automated), and only rendering + publishing happen after a human merges.

Usage:
  python tools/run_daily.py                  # today, real run
  python tools/run_daily.py 2026-09-15        # a specific date (backfill/testing)
  python tools/run_daily.py --dry-run         # everything except the final commit/push
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
LOGS = ROOT / "logs"

# Codex's output can contain characters the Windows console's default (cp1252) encoding can't
# represent — without this, printing that output crashes the driver and swallows the real error.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

CODEX_PROMPT_TEMPLATE = """\
You are finishing the authoring stage of a daily AI-news brief. Work ONLY inside this repository.

Read, in order:
  0. prompts/research.md — primary-source checks and the two ChatGPT radar lanes.
  1. prompts/daily.md — the rules for every field in an episode item.
  2. prompts/example.md — how to build a valid, runnable example per vertical.
  3. prompts/title.md — title and thumbnail-text rules.
  4. data/inbox/{date}.selected.json — the candidates already chosen for today, with their scores.

Then, editing ONLY data/episodes/{date}.json and creating/editing ONLY files under
examples/{date}-*/, for every item currently containing "TODO" fields:

- Fetch and actually read each item's source_url before writing anything about it. Never
  paraphrase from the title/summary alone.
- Fill every TODO field per prompts/daily.md: headline and what_changed are each capped at 22
  words (mechanically enforced, do not exceed), why_it_matters must pass the "what can the viewer
  decide?" test (switch model / budget a cost / upgrade or wait / patch before a date — if you
  can't state the decision in one line, the item doesn't belong in this brief), the_number is
  exactly one quantity quoted from the source or computed by your own example code, diff is a
  one-line before/after.
- Build examples/{date}-<slug>/ for each item: run.sh + expected_output.txt, correct
  example.kind (real / stub / analysis, per prompts/example.md's per-vertical rules), CPU-only,
  under 60 seconds, no paid API keys.
- CRITICAL, non-negotiable: actually execute every run.sh and capture its real stdout into
  expected_output.txt and into the item's example.output field. Never hand-type or invent output.
  This is the entire premise of Gate 2 — a fabricated output here is worse than a missing one.
- Fill title, thumbnail_text, and closing_line per prompts/title.md.
- Complete source_review after reading the primary source: status=verified, checked_at
  (YYYY-MM-DD), excerpt (at most 25 words), decision and availability. Radar reports are
  discovery leads, not evidence. Drop an unsupported candidate instead of inventing facts.
- Write portable run.sh scripts using "${{PYTHON:-python3}}" run.py.
- This machine is behind a corporate TLS-intercepting proxy: if fetching a source_url with Python
  (requests/urllib) fails with an SSL/certificate error, retry with `curl -sL <url>` instead.

When you believe every TODO is resolved, self-check by running:
  python src/schema.py data/episodes/{date}.json --verify-examples
Keep fixing and re-running until it's green. Do not stop while it's red.

Hard rules:
- Do NOT run `git commit`, `git add`, or `git push` — an external script owns git for this run.
- Do NOT edit any file other than data/episodes/{date}.json and examples/{date}-*/.
- Do NOT touch data/inbox/, data/dedup_index/, src/, templates/, prompts/, or any other episode.
- Leave examples/{date}-*/ containing only run.sh, expected_output.txt, and any file run.sh
  explicitly needs (e.g. a per-example requirements.txt) — no scratch files, caches, or
  dependency-install byproducts (e.g. a .pytest-deps/ or similar directory).
"""


def log(msg: str, logfile: pathlib.Path | None = None) -> None:
    line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line)
    if logfile is not None:
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(ROOT), text=True, **kw)


def branch_exists_on_origin(branch: str) -> bool:
    result = run(["git", "ls-remote", "--heads", "origin", branch], capture_output=True)
    return bool(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("date", nargs="?", help="YYYY-MM-DD, defaults to today")
    parser.add_argument("--dry-run", action="store_true", help="skip the final commit/push")
    args = parser.parse_args()

    date = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    date_str = date.isoformat()

    LOGS.mkdir(exist_ok=True)
    logfile = LOGS / f"daily_run_{date_str}.log"
    branch = f"draft/{date_str}"

    dirty = run(["git", "status", "--porcelain"], capture_output=True, check=True)
    if dirty.stdout.strip():
        log("Working tree has changes; refusing to switch branches or commit someone else's work.", logfile)
        return 1

    log(f"=== daily run for {date_str} (dry_run={args.dry_run}) ===", logfile)

    episode_path = ROOT / "data" / "episodes" / f"{date_str}.json"
    if episode_path.exists():
        log(f"{episode_path} already exists on disk — aborting (idempotency guard).", logfile)
        return 0
    if branch_exists_on_origin(branch):
        log(f"origin/{branch} already exists — aborting (idempotency guard).", logfile)
        return 0

    log("git fetch/checkout main/pull --ff-only", logfile)
    run(["git", "fetch", "origin"], check=True)
    run(["git", "checkout", "main"], check=True)
    run(["git", "pull", "--ff-only", "origin", "main"], check=True)

    # Check again after pulling: an episode may have arrived from another run.
    if episode_path.exists():
        log("Episode already exists on updated main; nothing to do.", logfile)
        return 0

    # Include curated radar reports imported since CI ingestion. This also works on a
    # radar-only day; selection never marks an unpublished story as already covered.
    selection = run([sys.executable, "src/selection.py", date_str], capture_output=True)
    if selection.returncode != 0:
        log(selection.stderr, logfile)
        return 1

    log("stage 1: check today's ingestion landed (produced by .github/workflows/ingest.yml)", logfile)
    selected_path = ROOT / "data" / "inbox" / f"{date_str}.selected.json"
    if not selected_path.exists():
        log(f"{selected_path} not on main yet — ingest.yml hasn't run (or is late) for "
            f"{date_str}. Aborting cleanly, try again later today.", logfile)
        return 0
    if not json.loads(selected_path.read_text(encoding="utf-8"))["selected"]:
        log(f"thin day: no candidate cleared the floor for {date_str}. Nothing to publish today.", logfile)
        return 0

    existing = run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"])
    if existing.returncode == 0:
        log(f"Local {branch} exists; preserve it for review/resume instead of deleting it.", logfile)
        return 1
    run(["git", "checkout", "-b", branch], check=True)

    def abort(reason: str) -> int:
        log(f"ABORT: {reason}", logfile)
        log(f"Draft and working files preserved on {branch} for diagnosis.", logfile)
        return 1

    try:
        log("stage 2: author (scaffold)", logfile)
        author = run([sys.executable, "src/author.py", date_str], capture_output=True)
        log(author.stdout, logfile)
        if author.returncode != 0:
            log(author.stderr, logfile)
            return abort("src/author.py failed")

        log("stage 3: headless Codex authors the brief + examples", logfile)
        prompt = CODEX_PROMPT_TEMPLATE.format(date=date_str)
        # `codex` is an npm-installed .cmd shim on Windows — subprocess can't exec it directly
        # without shell=True. The prompt goes on stdin ("-") rather than as an argv entry: it's
        # long and multi-line, and Windows command-line quoting (via shell=True) can't be trusted
        # with that. --approve-for-me already runs under the workspace-write sandbox — passing
        # -s/--sandbox too is rejected by codex exec as a conflicting argument.
        codex = run(
            ["codex", "exec", "-C", str(ROOT), "--approve-for-me", "-"],
            input=prompt, capture_output=True, shell=True, encoding="utf-8",
        )
        log(codex.stdout, logfile)
        if codex.returncode != 0:
            log(codex.stderr, logfile)
            return abort("codex exec failed")

        log("stage 4: independently re-verify Gate 1 + Gate 2 for today's episode "
            "(never trust Codex's own report)", logfile)
        # Check today's episode here; CI independently verifies the whole archive.
        # schema.py supplies the active Python executable to portable run.sh scripts.
        verify = run(
            [sys.executable, "src/schema.py", str(episode_path), "--verify-examples"],
            capture_output=True,
        )
        log(verify.stdout, logfile)
        if verify.returncode != 0:
            log(verify.stderr, logfile)
            return abort("Gate 1/2 verification failed after Codex run")

        if args.dry_run:
            log(f"--dry-run: stopping before commit/push. Branch {branch} left checked out locally.", logfile)
            return 0

        log("stage 5: commit + push draft branch", logfile)
        # data/inbox/** and data/dedup_index/** already live on main, committed by ingest.yml —
        # only the judgment-requiring files belong in this draft branch.
        paths_to_add = [
            str(episode_path.relative_to(ROOT)),
            f"examples/{date_str}-*",
            str(selected_path.relative_to(ROOT)),
        ]
        run(["git", "add", *paths_to_add], check=True)
        commit = run(["git", "commit", "-m", f"Draft episode {date_str}"])
        if commit.returncode != 0:
            return abort("nothing to commit (unexpected — Codex may not have written anything)")
        run(["git", "push", "-u", "origin", branch], check=True)
        run(["git", "checkout", "main"], check=True)

        compare_url = f"https://github.com/marcocm28/ai-daily-diff/compare/main...{branch}?expand=1"
        log(f"Pushed. Open a PR: {compare_url}", logfile)
        print(compare_url)
        return 0
    except Exception as e:  # noqa: BLE001 — this runs unattended overnight; never crash unlogged
        return abort(f"unexpected exception: {e!r}")


if __name__ == "__main__":
    sys.exit(main())
