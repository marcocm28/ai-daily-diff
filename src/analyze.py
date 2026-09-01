"""Loop A/B analysis. Pulls per-video stats from the YouTube Analytics API, joins them against
data/metrics/manifest.csv (which records which experiment variant each video belongs to), and
prints median-based comparisons plus a draft LEDGER.md entry — per the decision rules in
PROJECT_INSTRUCTIONS.md §10.3: median not mean, n>=5 or "insufficient data", ~2-week cohorts,
max 2 variables at a time.

This script never writes LEDGER.md, RECIPE.md, or prompts/*.md for you — §10.7 is explicit that
the loop cannot replace editorial judgment. It prints a draft; a person (or Claude, reviewing)
decides whether the conclusion is real and pastes it in.

data/metrics/manifest.csv columns (create by hand as episodes publish):
  video_id,date,experiment,variant,vertical

Usage:
  python src/analyze.py --experiment reading_speed_coeff --since 2026-09-01
  python src/analyze.py --experiment reading_speed_coeff --since 2026-09-01 --dry-run
    (dry-run: skips the API call, uses data/metrics/manifest.csv's own 'views' /
     'avg_view_pct' columns if present — useful for testing this script itself)
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from upload import get_credentials  # noqa: E402 — reuses the same OAuth credentials

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "metrics" / "manifest.csv"

MIN_N = 5


def load_manifest() -> list[dict]:
    if not MANIFEST.exists():
        print(f"no manifest at {MANIFEST} — nothing to analyze yet", file=sys.stderr)
        return []
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fetch_video_stats(video_ids: list[str]) -> dict[str, dict]:
    from googleapiclient.discovery import build

    creds = get_credentials()
    yta = build("youtubeAnalytics", "v2", credentials=creds)
    out = {}
    for vid in video_ids:
        try:
            resp = yta.reports().query(
                ids="channel==MINE",
                startDate="2020-01-01", endDate=dt.date.today().isoformat(),
                metrics="views,averageViewPercentage,averageViewDuration",
                filters=f"video=={vid}",
            ).execute()
            row = resp.get("rows", [[0, 0, 0]])[0]
            out[vid] = {"views": row[0], "avg_view_pct": row[1], "avg_view_duration": row[2]}
        except Exception as e:  # noqa: BLE001
            print(f"  warning: could not fetch stats for {vid}: {e}", file=sys.stderr)
            out[vid] = {}
    return out


def run(experiment: str, since: dt.date, dry_run: bool) -> None:
    rows = [r for r in load_manifest()
            if r.get("experiment") == experiment
            and dt.date.fromisoformat(r["date"]) >= since]

    if not rows:
        print(f"no manifest rows for experiment '{experiment}' since {since}")
        return

    if not dry_run:
        stats = fetch_video_stats([r["video_id"] for r in rows])
        for r in rows:
            r.update(stats.get(r["video_id"], {}))

    by_variant: dict[str, list[dict]] = {}
    for r in rows:
        by_variant.setdefault(r["variant"], []).append(r)

    print(f"Experiment: {experiment}  (cohort since {since})\n")
    summaries = {}
    for variant, group in by_variant.items():
        n = len(group)
        pct_values = [float(r["avg_view_pct"]) for r in group if r.get("avg_view_pct")]
        if n < MIN_N or not pct_values:
            print(f"  variant={variant:<20} n={n:<3} -> INSUFFICIENT DATA (need n>={MIN_N})")
            continue
        median_pct = statistics.median(pct_values)
        summaries[variant] = (median_pct, n)
        print(f"  variant={variant:<20} n={n:<3} median avg_view_pct={median_pct:.1f}%")

    if len(summaries) < 2:
        print("\nFewer than 2 variants with sufficient data — no comparison to draw yet.")
        return

    print("\n--- draft LEDGER.md entry (review before pasting) ---\n")
    variants_str = " vs ".join(f"{v} (n={n})" for v, (_, n) in summaries.items())
    medians_str = " vs ".join(f"{med:.1f}%" for _, (med, _) in summaries.items())
    print(f"## Experiment #NNN — {since.isoformat()} -> {dt.date.today().isoformat()}")
    print("**Loop:** A or B — fill in")
    print(f"**Hypothesis:** fill in — what did changing `{experiment}` predict?")
    print(f"**Variable(s):** {experiment} — {variants_str}. Everything else held constant.")
    print(f"**Result:** median avg_view_pct {medians_str}.")
    print("**Conclusion:** fill in — is the difference large enough, and consistent with the "
          "hypothesis, to act on?")
    print("**Correction applied:** which file changed (RECIPE.md weight / prompts/*.md rule) "
          "and how.")
    print(f"**Note:** smallest n above is {min(n for _, n in summaries.values())} — "
          "re-confirm at a later experiment if close to the n>=5 floor.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="value in manifest.csv's 'experiment' column")
    parser.add_argument("--since", required=True, help="YYYY-MM-DD, start of the cohort window")
    parser.add_argument("--dry-run", action="store_true",
                         help="use avg_view_pct/views already in manifest.csv instead of calling the API")
    args = parser.parse_args()
    run(args.experiment, dt.date.fromisoformat(args.since), args.dry_run)
