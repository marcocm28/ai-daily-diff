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

*(empty — no experiment has closed yet; the first is #001, silent vs. voice, per
`PROJECT_INSTRUCTIONS.md` §10.4, scheduled to start once ~2 weeks of baseline Daily Diffs exist)*
