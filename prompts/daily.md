# Prompt — authoring a Daily Diff

> Used by whoever (Claude, in a session) does step 3 (AUTHOR) of the daily flow. This file is
> corrected by the weekly loop (`PROJECT_INSTRUCTIONS.md` §10.5) — if a rule below caused a bad
> outcome in the ledger, the fix is a new line here, not a one-off judgment call next time.

## Inputs
- `data/inbox/YYYY-MM-DD.selected.json` — up to 3 scored candidates, already deduped.
- `PROJECT_INSTRUCTIONS.md` §5 (per-vertical spec), §6 (canonical schema), §6.2 (form limits).

## Task
For each selected candidate, write the five canonical fields (§6):

1. **WHAT CHANGED** — one sentence. No unexplained jargon, no press-release language. If a term
   must appear, expand it once, on the slide, the first time it shows up.
2. **WHY IT MATTERS** — the consequence for someone who builds things, not abstract importance.
3. **THE NUMBER** — exactly one quantity. Either quoted from the primary source or computed by
   our own example code (prefer the latter — it is the thing competitors cannot fake).
4. **RUN IT** — design the minimal executable example (see `prompts/example.md`) before writing
   this field; the field is a one-line description of what the example does.
5. **SOURCE** — the primary URL, printed in full, never shortened.

Then write:
- `diff.minus` / `diff.plus` — the "before" and "after" in one line each, in the diff visual
  identity (a real `−`/`+` pair, not a metaphor).
- `title` (see `prompts/title.md`) and `thumbnail_text`.

## Hard limits (§6.2 — never relaxed)
- Max 22 words per slide.
- Exactly one number per item.
- Exactly one example per item.
- Max 3 items per Daily Diff.
- No slide without a `source_url`. If a candidate has no primary source, it does not ship —
  go back to `select.py` output, do not invent one.

## Standing corrections
*(none yet — this section grows as the weekly loop finds retention problems; e.g. a past
correction might read: "lead with the concrete number by second 8, not the setup.")*
