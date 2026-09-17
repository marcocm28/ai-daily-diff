"""Stage 3 — AUTHOR (scaffold half).

Writing WHAT CHANGED / WHY IT MATTERS / the diff / the example is a judgment call — it needs a
person or Claude reading the actual source, per prompts/daily.md. This script does the
*mechanical* half only: it turns data/inbox/YYYY-MM-DD.selected.json into a draft
data/episodes/YYYY-MM-DD.json with every field that can be filled without judgment already
filled, and every field that needs writing marked "TODO — see prompts/daily.md".

Usage:
  python src/author.py 2026-08-28                 # daily, from today's/that date's selection
  python src/author.py 2026-08-28 --kind method     # weekly method video scaffold
  python src/author.py 2026-08-28 --kind deep       # occasional long variant

After running, open the file, replace every "TODO" following prompts/daily.md (or deep.md), then
write the matching examples/YYYY-MM-DD-<slug>/ folder (run.sh + expected_output.txt) per
prompts/example.md before rendering.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
INBOX = ROOT / "data" / "inbox"
EPISODES = ROOT / "data" / "episodes"

RAIL_COLORS = ["var(--accent)", "var(--accent2)", "var(--ok)"]

VERTICAL_LABELS = {
    "models-releases": "MODELS & RELEASES",
    "cost-limits": "COST & LIMITS",
    "tools-agents": "TOOLS & AGENTS",
    "media-generation": "MEDIA GENERATION",
    "claims-risks": "CLAIMS & RISKS",
}


def slugify(title: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:40].rstrip("-")


def draft_item(candidate: dict, date: dt.date) -> dict:
    vertical = candidate.get("_vertical_hint", "models-releases")
    slug = slugify(candidate["title"])
    ex_dir = f"examples/{date.isoformat()}-{slug}"
    return {
        "id": f"{date.isoformat()}-{slug}",
        "vertical": vertical,
        "vertical_label": VERTICAL_LABELS.get(vertical, vertical.upper()),
        "headline": "TODO — one sentence, <=22 words, no unexplained jargon (prompts/daily.md)",
        "what_changed": "TODO — WHAT CHANGED, one sentence",
        "why_it_matters": "TODO — WHY IT MATTERS, the consequence for builders",
        "who_should_care": "TODO — one sentence, who this is for",
        "the_number": {
            "value": "TODO",
            "label": "TODO — what the number measures",
            "notes": ["TODO — supporting bullet 1", "TODO — supporting bullet 2"],
        },
        "diff": {
            "minus": "TODO — the 'before', in one line",
            "plus": "TODO — the 'after', in one line",
        },
        "watch_out": "",
        "example": {
            "kind": "TODO",  # real | stub | analysis — see prompts/example.md
            "dir": ex_dir,
            "run_cmd": "bash run.sh",
            "run_summary": "TODO — e.g. '12 lines, CPU, <10s'",
            "caption": "TODO — one line describing what the example demonstrates",
            "code": "TODO — paste the exact code that will live in " + ex_dir + "/run.sh",
            "output": "TODO — the real captured output, once run",
            "tested_in_ci": False,
        },
        "source_url": candidate["url"],
        "source_review": {"status": "pending", "checked_at": "", "excerpt": "",
                          "decision": candidate.get("decision", ""),
                          "availability": candidate.get("availability", "unknown")},
        "_origin": {"source": candidate["source"], "raw_title": candidate["title"],
                     "score": candidate.get("_score"),
                     "discovery_task": candidate.get("discovery_task"),
                     "discovered_at": candidate.get("discovered_at")},
    }


def run(date: dt.date, kind: str = "daily") -> pathlib.Path:
    suffix = "" if kind == "daily" else f".{kind}"
    selected_path = INBOX / f"{date.isoformat()}{suffix}.selected.json"
    if not selected_path.exists():
        print(f"no selection file for {date} — run src/selection.py {date} --kind {kind} first", file=sys.stderr)
        sys.exit(1)

    selected = json.loads(selected_path.read_text(encoding="utf-8"))["selected"]
    if not selected:
        print(f"selection for {date} is empty — nothing to author", file=sys.stderr)
        sys.exit(1)

    items = [draft_item(c, date) for c in (selected if kind == "daily" else selected[:1])]
    for i, item in enumerate(items):
        item["rail_color"] = RAIL_COLORS[i % len(RAIL_COLORS)]

    episode = {
        "date": date.isoformat(),
        "kind": kind,
        "title": f"TODO — {kind} title (prompts/title.md)",
        "thumbnail_text": "TODO",
        "closing_line": "TODO — one sentence takeaway tying the items together",
        "items": items,
    }

    EPISODES.mkdir(parents=True, exist_ok=True)
    out_path = EPISODES / f"{date.isoformat()}.json"
    if out_path.exists():
        print(f"refusing to overwrite existing {out_path}", file=sys.stderr)
        sys.exit(1)

    out_path.write_text(json.dumps(episode, indent=2), encoding="utf-8")
    print(f"Wrote draft episode -> {out_path}")
    print(f"{len(items)} item(s), all qualitative fields marked TODO — fill per prompts/daily.md")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="YYYY-MM-DD")
    parser.add_argument("--kind", default="daily", choices=["daily", "method", "deep"])
    args = parser.parse_args()
    run(dt.date.fromisoformat(args.date), kind=args.kind)
