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

## The decision rule (added 2026-09-02 — read this before writing anything)

Every item must let the viewer **decide something**: switch model, budget a cost, upgrade or wait,
patch before a date. Write the decision down for yourself first, in one line. If you cannot, the
item is background reading, not a Daily Diff item — send it back.

This is also the test for `why_it_matters`: "this is an interesting result" fails, "this changes
what one GPU can hold" passes.

## The first fifteen seconds

The cover slide's three headlines are the whole hook, and in a silent format nobody's voice tells
the viewer to hold on. So each headline must:

- state the **consequence**, not the mechanism — "62% less KV cache", not "a new attention variant";
- contain at least one concrete noun or number a reader recognises;
- be readable in one pass, no subordinate clauses.

## The method item (kind: `method`, vertical: tools-agents)

**Where the method lane actually lives: the weekly video** (`prompts/method.md`), because evergreen
traffic needs a video whose *title is the query*, and a Daily title never can be. A method item
buried in a brief costs the most to produce and captures the least of what makes it valuable.

So in the Daily a method item is **occasional, not scheduled**: include one when it is too good to
wait a week, and otherwise leave the lane to the weekly. When you do include one, write it as:

Write it as:

- **the task** it improves, named in the words someone would search for ("code review", "reading a
  200-page PDF", "keeping an agent on track across long sessions");
- **the diff**: `−` how it is usually done, `+` what the method changes;
- **the number**: tokens per task, steps to completion, retry rate, or success rate on a fixed
  task. **Never a self-assigned score out of ten** — see `PROJECT_INSTRUCTIONS.md` §5, filone 3;
- **the example**: a deterministic stub standing in for the model, demonstrating the structure —
  and the slide must say it is a stub.

A community post claiming a better way is a lead, not an item. Follow it to the documented
artifact (repo, gist, doc page) and cite that. If there is nothing documented, it does not ship.

## Who it is about

Set `org` (a slug, e.g. `qwen`, `openai`) and `org_label` (e.g. `QWEN`) when a story is about a
specific vendor. The renderer shows the official logo if `assets/logos/vendors/<slug>.png` exists
and a text chip otherwise. Never set `org` on a comparison slide or next to a judgement about that
vendor (`PROJECT_INSTRUCTIONS.md` §8.5).

## Hard limits (§6.2 — never relaxed)
- Max 22 words per slide.
- Exactly one number per item.
- Exactly one example per item.
- Max 3 items per Daily Diff.
- No slide without a `source_url`. If a candidate has no primary source, it does not ship —
  go back to `selection.py` output, do not invent one.

## Standing corrections
*(none yet — this section grows as the weekly loop finds retention problems; e.g. a past
correction might read: "lead with the concrete number by second 8, not the setup.")*
