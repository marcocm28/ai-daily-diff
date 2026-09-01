# RECIPE.md — the current, living production recipe

> This file is the output of the loop (`PROJECT_INSTRUCTIONS.md` §10). It changes when the
> ledger produces a numeric conclusion. It never changes on a hunch.
> Format: one dated entry per change, newest on top. Never delete history — strike it through.

---

## Current recipe (v1 — baseline, no experiments closed yet)

**Reading speed:** 0.35 s/word of new on-screen text (≈170 wpm silent reading).
**Hold formula:**
```
hold(state) = clamp(0.9, 4.5, 0.35 × new_words + 0.5)
  + 1.8s minimum if the state introduces a chart
  + 2.5s minimum for the final state of a code block
  + 2.2s minimum if the state reveals a source URL
```
**Item count per Daily Diff:** 3.
**Item count per Deep Diff:** 1 topic, 6 sections (promise → what the source says → we ran it →
real output → where it breaks → what it means).
**Thumbnail:** one number or technical term, large, no faces, no arrows, no logos.
**Title pattern:** `<headline in plain words> — AI Daily Diff <Mon DD>`.
**Music bed:** none yet selected — see `assets/music/` and `PROJECT_INSTRUCTIONS.md` §14.

---

## Scoring weights (Loop B — `PROJECT_INSTRUCTIONS.md` §9.2)

| Signal | Weight |
|---|---|
| `is_primary_source` | ×1.5 (gate: no primary source → discarded) |
| `has_runnable_artifact` | 0.30 |
| `corroboration_count` | 0.20 |
| `interest_signal` | 0.20 |
| `source_authority` | 0.15 |
| `freshness` (48h decay) | 0.15 |
| `vertical_balance_bonus` | variable, see `src/select.py` |

These are mirrored in `src/select.py::WEIGHTS` — that constant is the one Loop B actually edits.
Keep this table and that constant in sync; CI does not check this for you.

---

## Open experiment

**#001 — silent vs. voice.** Not yet started (needs ~2 weeks of baseline Daily Diffs first, per
`PROJECT_INSTRUCTIONS.md` §10.4). Declare the start date here when it begins.
