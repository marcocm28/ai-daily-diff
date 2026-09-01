"""Stage 2 — SELECT. Scores candidates from data/inbox/YYYY-MM-DD.json, dedupes against the
30-day index, and writes the top N (balanced across verticals) to
data/inbox/YYYY-MM-DD.selected.json.

WEIGHTS below is the exact table mirrored in RECIPE.md — Loop B (PROJECT_INSTRUCTIONS.md §10.2)
edits this constant, and RECIPE.md is updated to match in the same commit.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
INBOX = ROOT / "data" / "inbox"
DEDUP_INDEX = ROOT / "data" / "dedup_index" / "index.json"

DEDUP_WINDOW_DAYS = 30
MAX_SELECTED = 3

# PROJECT_INSTRUCTIONS.md §9.2 — keep in sync with RECIPE.md's copy of this table.
WEIGHTS = {
    "is_primary_source_multiplier": 1.5,   # gate: 0 without it, item is dropped outright
    "has_runnable_artifact": 0.30,
    "corroboration_count": 0.20,
    "interest_signal": 0.20,
    "source_authority": 0.15,
    "freshness": 0.15,
}

SOURCE_AUTHORITY = {
    "arxiv": 0.9, "huggingface": 0.8, "github": 0.85,
}

# Very rough vertical routing by source prefix — select.py doesn't try to be clever here; a
# human (or Claude, authoring) makes the real call on vertical fit before writing the episode.
VERTICAL_HINTS = {
    "arxiv:cs.LG": "architectures-models",
    "arxiv:cs.CV": "video-image-generation",
    "arxiv:cs.CL": "agents-prompting",
    "arxiv:cs.AI": "agents-prompting",
    "huggingface:models": "architectures-models",
    "huggingface:datasets": "data-evaluation",
}


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _hash(candidate: dict) -> str:
    key = candidate["url"] + "|" + _normalize_title(candidate["title"])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_dedup_index() -> dict:
    if DEDUP_INDEX.exists():
        return json.loads(DEDUP_INDEX.read_text(encoding="utf-8"))
    return {"entries": {}}  # hash -> date published


def save_dedup_index(index: dict) -> None:
    DEDUP_INDEX.parent.mkdir(parents=True, exist_ok=True)
    DEDUP_INDEX.write_text(json.dumps(index, indent=2), encoding="utf-8")


def prune_dedup_index(index: dict, today: dt.date) -> dict:
    cutoff = today - dt.timedelta(days=DEDUP_WINDOW_DAYS)
    index["entries"] = {
        h: d for h, d in index["entries"].items()
        if dt.date.fromisoformat(d) >= cutoff
    }
    return index


def score(candidate: dict) -> float:
    if not candidate.get("is_primary_source"):
        return 0.0  # gate — no primary source, no score, no ship

    source_prefix = candidate["source"].split(":")[0]
    authority = SOURCE_AUTHORITY.get(source_prefix, 0.5)

    signals = candidate.get("signals", {})
    interest_raw = (signals.get("downloads", 0) or 0) + (signals.get("likes", 0) or 0) * 20
    interest = min(1.0, interest_raw / 10000)  # crude normalization, tune once real data exists

    corroboration = 0.0  # single-source ingestion for now; multi-source corroboration is future work

    has_artifact = 1.0 if source_prefix in ("github", "huggingface") else 0.5

    freshness = 1.0  # ingest.py only pulls recent items already; refine once published_at parsed consistently

    total = (
        WEIGHTS["has_runnable_artifact"] * has_artifact
        + WEIGHTS["corroboration_count"] * corroboration
        + WEIGHTS["interest_signal"] * interest
        + WEIGHTS["source_authority"] * authority
        + WEIGHTS["freshness"] * freshness
    ) * WEIGHTS["is_primary_source_multiplier"]

    return round(total, 4)


def run(date: dt.date | None = None, max_selected: int = MAX_SELECTED) -> pathlib.Path:
    date = date or dt.date.today()
    inbox_path = INBOX / f"{date.isoformat()}.json"
    if not inbox_path.exists():
        print(f"no inbox file for {date} — run src/ingest.py first", file=sys.stderr)
        sys.exit(1)

    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    index = prune_dedup_index(load_dedup_index(), date)

    scored = []
    for c in inbox["candidates"]:
        h = _hash(c)
        if h in index["entries"]:
            continue  # already covered within the dedup window
        s = score(c)
        if s <= 0:
            continue
        scored.append({**c, "_hash": h, "_score": s,
                        "_vertical_hint": VERTICAL_HINTS.get(c["source"], "architectures-models")})

    scored.sort(key=lambda c: c["_score"], reverse=True)

    selected = []
    seen_verticals = set()
    # First pass: best item per vertical, to avoid an all-one-vertical brief.
    for c in scored:
        if len(selected) >= max_selected:
            break
        if c["_vertical_hint"] not in seen_verticals:
            selected.append(c)
            seen_verticals.add(c["_vertical_hint"])
    # Second pass: fill any remaining slots with the next best regardless of vertical.
    for c in scored:
        if len(selected) >= max_selected:
            break
        if c not in selected:
            selected.append(c)

    for c in selected:
        index["entries"][c["_hash"]] = date.isoformat()
    save_dedup_index(index)

    out_path = INBOX / f"{date.isoformat()}.selected.json"
    out_path.write_text(json.dumps({"date": date.isoformat(), "selected": selected}, indent=2),
                         encoding="utf-8")

    print(f"Selected {len(selected)}/{len(scored)} scored candidate(s) -> {out_path}")
    for c in selected:
        print(f"  [{c['_score']:.3f}] {c['_vertical_hint']:<24} {c['title'][:70]}")
    return out_path


if __name__ == "__main__":
    run()
