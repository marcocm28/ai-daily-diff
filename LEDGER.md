# LEDGER.md — experiment log

> Every entry needs: hypothesis, variable(s) changed (max 2), sample size (n≥5 or "insufficient
> data"), median result, conclusion, and the prompt/weight correction that follows from it.
> Rules: median not mean · n≥5 · ~2-week cohort · max 2 variables at a time · epsilon-greedy
> 80/20, exploration never fully stops · §3/§4 constraints are never optimized away.
> Full rules: `PROJECT_INSTRUCTIONS.md` §10.3.

---

## Template — copy this block for each new entry

```markdown
## Experiment #NNN — YYYY-MM-DD → YYYY-MM-DD
**Loop:** A (packaging) or B (selection)
**Hypothesis:** ...
**Variable(s):** name — value A (n=?) vs value B (n=?). Everything else held constant.
**Result:** median metric A vs median metric B.
**Conclusion:** ...
**Correction applied:** which file changed (RECIPE.md weight, prompts/*.md rule) and how.
**Note:** sample size caveat, re-confirm at experiment #___.
```

---

## Log

### Baseline notes (not experiments — no n yet)

**2026-09-01 — first real episode.** 3 items, 29 states, 2:05, 2.03 MB. Render time end to end
(video + slides.pdf + cheatsheet.pdf + brief.md + thumbnail + page): under 2 minutes of CPU.
Cheat sheet needed shrink-to-fit on 2 of 3 pages (scales 0.972 and 0.914) to keep one item per
page — watch whether that becomes routine, because if every episode scales below ~0.90 the fix is
less content per item, not smaller type.

**2026-09-02 — selection function, dry run on the new weights.** Scored six candidates of the
shapes we actually see (synthetic where noted, real for the three used on 09-01), cohort date
2026-09-02:

| score | kind | item |
|---|---|---|
| 1.755 | pricing | a price per million tokens moved |
| 1.691 | deprecation | a vendor deprecation page changed |
| 1.361 | tool_release | a runtime shipped a release |
| 1.234 | model_weights | Qwen/Qwen3.8-Flash-Next (real, used 09-01) |
| 0.116 | research | DAMP preprint (real, used 09-01) — penalty applied |
| 0.116 | research | quantization-backdoor preprint (real, used 09-01) — penalty applied |

The two preprints that made up two thirds of the first episode now sit an order of magnitude below
a price change. **This is not evidence that the new weights are right** — it is evidence that they
do what they were changed to do. Whether decision-shaped items actually retain better is
experiment territory, and needs published episodes and n≥5 before anyone claims anything.

**2026-09-03 — music bed added, level calibrated by measurement.** Two bugs found by measuring
the output instead of trusting the code: the fixed −15 dB default was structurally wrong for a
format where music is the only audio (it would have shipped videos at ~−26 LUFS, which YouTube
does not raise), and the first measured-gain implementation read the ebur128 meter's *first*
printed value (−70.0, its startup placeholder) instead of the summary, computing a +52 dB gain
and producing a video at +10 LUFS. Final: −18.3 LUFS integrated, LRA 4.0 LU, true peak −7.7 dBFS.

**2026-09-02 — first episode selected under the revised weights.** Two items, not three: the day
offered two strong candidates (a 267× price spread, an Ollama release changing local sampling
defaults) and one eight-day-old model release. Ran short rather than padding, per RECIPE.md.
Video 1:26, 20 states. Two rendering bugs found and fixed by looking at the output: the code
slide's captured output overflowed 1080p and bled onto the next PDF page, and the first fit
attempt measured hidden slides (clientHeight 0) and returned -Infinity. Both now scale the block
instead — 0.719 and 0.935 on this episode.

The 2026-09-01 episode stays in the repo as the reference build; it was selected under the old
weights and is **not** the publication candidate.

**2026-09-02 — experiment #002 declared, not started.** Format allocation: Daily news vs. weekly
Method Diff. Metric: median views at 30 days per format, plus median APV, one cohort, n≥5 per arm.
Decision rule and the understatement caveat are written in `RECIPE.md` under Open experiments —
declared *before* any data exists, which is the point. Earliest possible read: week 8.

*(no experiment has closed yet; the first is #001, silent vs. voice, per
`PROJECT_INSTRUCTIONS.md` §10.4, scheduled to start once ~2 weeks of baseline Daily Diffs exist)*
