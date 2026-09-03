"""Stage 2 — SELECT. Scores candidates from data/inbox/YYYY-MM-DD.json, dedupes against the
30-day index, and writes the top N (balanced across verticals) to
data/inbox/YYYY-MM-DD.selected.json.

WEIGHTS is the table mirrored in RECIPE.md — Loop B (PROJECT_INSTRUCTIONS.md §10.2) edits this
constant, and RECIPE.md is updated to match in the same commit.

Revision of 2026-09-02, after the first real episode: the original weights optimised for novelty
and primary-sourcing, which is how a day's brief ended up as two arXiv preprints and a preview
config — all defensible, all narrow. Two signals were missing, and they are now the two heaviest:

  blast_radius        how many people building with AI this actually touches
  decision_relevance  whether it changes a choice someone makes this week

A paper with no shipped artifact now carries an explicit penalty. It can still win — but it has
to beat a price change or a release on reach, which is the right bar for a daily.
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

# A daily brief is about today, so freshness decays over four days. But a thin day is a real
# thing, and padding a brief with a weak item is worse than reaching back a week for a strong
# one — so when too few candidates clear the floor, the window widens instead.
SCORE_FLOOR = 0.55
FRESHNESS_DAYS = 4
FRESHNESS_DAYS_WIDENED = 7

# PROJECT_INSTRUCTIONS.md §9.2 — keep in sync with RECIPE.md's copy of this table.
WEIGHTS = {
    "is_primary_source_multiplier": 1.5,   # gate: 0 without it, the item is dropped outright
    "blast_radius": 0.35,
    "decision_relevance": 0.30,
    "has_runnable_artifact": 0.25,
    "freshness": 0.20,
    "interest_signal": 0.15,
    "source_authority": 0.10,
    "corroboration_count": 0.10,
    "research_only_penalty": -0.25,        # preprint with nothing shipped to use or verify
}

# How far each kind of source reaches, and how likely it is to change a decision this week.
# These are the priors the loop will correct; the point is that they exist at all now.
SOURCE_PROFILE = {
    # kind:            (blast_radius, decision_relevance, authority, runnable_artifact)
    "pricing":         (1.00, 1.00, 0.95, 0.9),   # price, quota or limit changed
    "deprecation":     (0.95, 1.00, 0.95, 0.8),   # something you depend on breaks on a date
    "vendor_release":  (0.90, 0.80, 0.95, 0.7),   # a major vendor shipped a model or feature
    "method":          (0.75, 0.90, 0.85, 1.0),   # a documented better way to do a real task
    "model_weights":   (0.70, 0.70, 0.80, 0.9),   # open weights you can actually download
    "tool_release":    (0.65, 0.65, 0.85, 1.0),   # library, agent framework, runtime
    "dataset":         (0.35, 0.35, 0.80, 0.9),
    "research":        (0.15, 0.20, 0.90, 0.5),   # preprint: narrow until something ships
}
DEFAULT_PROFILE = (0.30, 0.30, 0.50, 0.5)


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
    index["entries"] = {h: d for h, d in index["entries"].items()
                        if dt.date.fromisoformat(d) >= cutoff}
    return index


def freshness(candidate: dict, today: dt.date, window: int = FRESHNESS_DAYS) -> float:
    """1.0 today, decaying to 0 across the window. A daily brief is about today."""
    published = candidate.get("published_at")
    if not published:
        return 0.6  # unknown: neither rewarded nor punished
    try:
        day = dt.date.fromisoformat(str(published)[:10])
    except ValueError:
        return 0.6
    age = (today - day).days
    return max(0.0, 1.0 - age / window)


def score(candidate: dict, today: dt.date, freshness_window: int = FRESHNESS_DAYS) -> tuple[float, dict]:
    """Returns (score, breakdown). The breakdown is written to the selection file so a later
    session — or Loop B — can see why an item won, not just that it did."""
    if not candidate.get("is_primary_source"):
        return 0.0, {"rejected": "no primary source"}

    kind = candidate.get("kind", "")
    blast, decision, authority, runnable = SOURCE_PROFILE.get(kind, DEFAULT_PROFILE)

    # a candidate may carry explicit overrides when the author knows better than the prior
    blast = float(candidate.get("blast_radius", blast))
    decision = float(candidate.get("decision_relevance", decision))

    signals = candidate.get("signals", {})
    interest_raw = (signals.get("downloads", 0) or 0) + (signals.get("likes", 0) or 0) * 20 \
        + (signals.get("stars", 0) or 0) * 10
    interest = min(1.0, interest_raw / 500_000)

    parts = {
        "blast_radius": WEIGHTS["blast_radius"] * blast,
        "decision_relevance": WEIGHTS["decision_relevance"] * decision,
        "has_runnable_artifact": WEIGHTS["has_runnable_artifact"] * runnable,
        "freshness": WEIGHTS["freshness"] * freshness(candidate, today, freshness_window),
        "interest_signal": WEIGHTS["interest_signal"] * interest,
        "source_authority": WEIGHTS["source_authority"] * authority,
        "corroboration_count": WEIGHTS["corroboration_count"]
                                * min(1.0, candidate.get("corroboration_count", 0) / 3),
    }
    if kind == "research" and not candidate.get("shipped_artifact"):
        parts["research_only_penalty"] = WEIGHTS["research_only_penalty"]

    total = sum(parts.values()) * WEIGHTS["is_primary_source_multiplier"]
    return round(total, 4), {k: round(v, 4) for k, v in parts.items()}


def run(date: dt.date | None = None, max_selected: int = MAX_SELECTED) -> pathlib.Path:
    date = date or dt.date.today()
    inbox_path = INBOX / f"{date.isoformat()}.json"
    if not inbox_path.exists():
        print(f"no inbox file for {date} — run src/ingest.py first", file=sys.stderr)
        sys.exit(1)

    inbox = json.loads(inbox_path.read_text(encoding="utf-8"))
    index = prune_dedup_index(load_dedup_index(), date)

    def score_all(window: int) -> list[dict]:
        out = []
        for c in inbox["candidates"]:
            h = _hash(c)
            if h in index["entries"]:
                continue  # already covered inside the dedup window
            s, breakdown = score(c, date, window)
            if s <= 0:
                continue
            out.append({**c, "_hash": h, "_score": s, "_breakdown": breakdown,
                         "_freshness_window": window,
                         "_vertical_hint": c.get("vertical", "models-releases")})
        out.sort(key=lambda c: c["_score"], reverse=True)
        return out

    scored = score_all(FRESHNESS_DAYS)
    strong = [c for c in scored if c["_score"] >= SCORE_FLOOR]
    if len(strong) < max_selected:
        widened = score_all(FRESHNESS_DAYS_WIDENED)
        if len([c for c in widened if c["_score"] >= SCORE_FLOOR]) > len(strong):
            print(f"thin day: only {len(strong)} candidate(s) above {SCORE_FLOOR} in "
                  f"{FRESHNESS_DAYS} days — widening to {FRESHNESS_DAYS_WIDENED}")
            scored = widened

    selected, seen = [], set()
    for c in scored:                      # best per vertical first: no all-one-vertical brief
        if len(selected) >= max_selected:
            break
        if c["_vertical_hint"] not in seen:
            selected.append(c)
            seen.add(c["_vertical_hint"])
    for c in scored:                      # then fill remaining slots with the next best
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
        print(f"  [{c['_score']:.3f}] {c.get('kind', '?'):<14} {c['_vertical_hint']:<18} "
              f"{c['title'][:60]}")
    return out_path


if __name__ == "__main__":
    run()
