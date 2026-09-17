# Prompt — the Deep Diff (occasional variant of the weekly slot)

> Since 2026-09-02 the weekly slot's default is the **Method Diff** (`prompts/method.md`), 4-6
> minutes with a query-shaped title. Use this longer shape when the subject genuinely needs the
> room: an emerging pattern that requires showing evidence from several sources, or a verification
> with several stages. One weekly video, two possible shapes — never both in the same week.

One topic, six sections (`PROJECT_INSTRUCTIONS.md` §8.2):

1. **The promise** — what the source claims, in its own framing.
2. **What the source says** — the mechanism, plainly, one level deeper than a Daily Diff item.
3. **We ran it** — state that the example was actually executed; show the command.
4. **The real output** — the captured output, not a paraphrase.
5. **Where it breaks** — the failure mode, the edge case, the caveat the announcement omits.
   This section is the point of the format: no slop channel produces it, because it requires
   having actually run the thing.
6. **What it means** — for someone building today, not a hype conclusion.

Same hard limits as `prompts/daily.md` apply per slide (22 words, one source per claim). A Deep
Diff may use more than one example if each maps to a distinct section above, but still exactly
one "the number" for the whole episode — pick the number that best carries section 6.

## Preferred format: the workflow of the week (added 2026-09-02)

One real agentic or prompting workflow, built, run, and broken:

```
GOAL → PLANNER → TOOL / MCP / SKILL → SUBAGENT → VERIFY → OUTPUT
```

For each stage, our own measurement: tokens spent, steps taken, retries. Then the section that
matters most — **where it breaks**: the stage that fails first, and what it costs when it does.

**Emerging patterns belong here, not in a Daily item.** A pattern is only declared with evidence
from several independent sources, and a weekly episode has room to show it. §10.3 applies: if
there are two sources, say "two" — not "a trend is emerging".

## Standing corrections
*(none yet)*
# Research inputs

Read `prompts/research.md` and the curated reports in `data/radar/`. Architectural
patterns are hypotheses unless supported by independent primary sources. Complete
`source_review` and distinguish measurements from inference before rendering.
