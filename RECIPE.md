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
**Cadence (revised 2026-09-02).** Daily Diff every weekday, 3 news items. One weekly video, whose
default shape is the **Method Diff**: 4-6 minutes, one task, one measured method, **title shaped
like the search query, no series name in it**. The 10-15 minute Deep Diff is the occasional variant
of that same weekly slot. A method item appears in a Daily only when it is too good to wait.

**Item count per Daily Diff:** 3. **Method / Deep:** exactly 1 topic (enforced in `src/schema.py`).
**Measured length, first real episode (2026-09-01):** 2:05 for 3 items, 29 reveal states, from the
formula above — not from a target. `PROJECT_INSTRUCTIONS.md` §8.1 estimated 3:30-5:00 before any
real episode existed. **We do not pad a video to hit a spec.** Length is a Loop A variable
(`length_s`): if retention data later says longer is better, the lever is more content per item,
not slower holds.
**Item count per Deep Diff:** 1 topic, 6 sections (promise → what the source says → we ran it →
real output → where it breaks → what it means).
**Thumbnail:** one number or technical term, large, no faces, no arrows, no logos.
**Title pattern:** `<headline in plain words> — AI Daily Diff <Mon DD>`.
**Music bed:** none yet selected — see `assets/music/` and `PROJECT_INSTRUCTIONS.md` §14.

---

## Scoring weights (Loop B — `PROJECT_INSTRUCTIONS.md` §9.2)

**Revised 2026-09-02.** The first weights optimised for novelty and never asked how many people a
story touches, or whether it changes a decision. Those two are now the heaviest.

| Signal | Weight |
|---|---|
| `is_primary_source` | ×1.5 multiplier (gate: no primary source → discarded) |
| `blast_radius` | 0.35 |
| `decision_relevance` | 0.30 |
| `has_runnable_artifact` | 0.25 |
| `freshness` (4-day decay) | 0.20 |
| `interest_signal` | 0.15 |
| `source_authority` | 0.10 |
| `corroboration_count` | 0.10 |
| `research_only_penalty` | −0.25 |

Mirrored in `src/selection.py::WEIGHTS` — that constant is the one Loop B actually edits. Keep this
table and that constant in sync; CI does not check this for you. The per-source-kind priors for
`blast_radius` and `decision_relevance` live in `src/selection.py::SOURCE_PROFILE`.

**Music bed (set 2026-09-03):** `assets/music/daily-bed.mp3` — "Nebula", The Grey Room / Density
& Time, YouTube Audio Library. 3:09, so a Daily never reaches a loop point.

The level is **measured, not fixed**. The renderer reads the track's integrated loudness and
computes the gain to land the finished video at **−18 LUFS**, with 1.5 s fades at both ends. Why
that target and not the "−15 dB under the voice" it used to be: in a silent format the bed is the
*only* audio, and YouTube normalises loud content down to about −14 LUFS but never raises quiet
content. A bed mixed to −26 LUFS just plays quiet, the viewer turns the volume up, and the next
video shouts at them. Verified on the 2026-09-02 render: −18.3 LUFS integrated, LRA 4.0 LU, true
peak −7.7 dBFS.

`music_bed` and the −18 target are both Loop A variables. Selection criteria and the measurements
taken on arrival are in `assets/music/CREDITS.md`.

**Vendor logos:** identifier only, never the subject, never beside a judgement
(`PROJECT_INSTRUCTIONS.md` §8.5). Text chip when the official asset is missing.

---

## Open experiments

**#001 — silent vs. voice.** Not yet started (needs ~2 weeks of baseline Daily Diffs first, per
`PROJECT_INSTRUCTIONS.md` §10.4). Declare the start date here when it begins.

**#002 — format allocation: Daily news against weekly Method.** Declared 2026-09-02, decided at
week 8. Compare **median views at 30 days** per format, plus median average-view-percentage, over a
single cohort, per the §10.3 rules (median not mean, n≥5 per arm, max 2 variables).
Decision rule, written before the data exists so it cannot be rationalised afterwards:

- Method median ≥ 2× Daily median → move to two weekly Method videos and three Dailies.
- Within 2× either way → keep 5 + 1 and re-check at week 16.
- Daily median ≥ 2× Method median → the audience wants the newspaper; keep 5 + 1 and stop treating
  Method as the acquisition engine (update §2.5 and this file).

Note the asymmetry to watch for when reading it: Method videos accumulate views for months, so a
30-day window **understates** them. If the call is close, extend the window rather than deciding
on a number that structurally favours the Daily.
