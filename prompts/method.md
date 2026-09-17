# Prompt — the weekly Method Diff (the flagship)

> Decided 2026-09-02. One video a week, 4-6 minutes, one task, one measured method.
> This is the channel's **acquisition engine**: the Daily builds the habit and the archive, this
> earns the search traffic that lasts months. `PROJECT_INSTRUCTIONS.md` §2.5, §8.2.

## The one rule that makes or breaks it: the title is the query

A method video only earns evergreen traffic if its title is **the sentence someone types**. Write
the query first, before the video exists:

- ✅ `The measured way to keep an agent on track across long sessions`
- ✅ `How much a code review with Claude actually costs, per pull request`
- ❌ `AI Daily Diff Sep 9 — agent memory`  ← the query is nowhere in it

**No series name at the front of the title, and normally not in it at all.** On the Daily the brand
prefix is fine, because those views come from subscribers and browse. Here the views come from
search, the title is finite, and every word spent on branding is a word not spent on the query.
The brand lives in the thumbnail logo and the end card.

Corollary: pick the task from what people actually search for, phrased their way — "reading a
200-page PDF", "code review", "keeping context across sessions" — not our way ("context window
management strategies").

## Structure (five beats, same canonical schema as an item)

The renderer treats a method episode as a single-item episode, so the beats map onto the existing
slides:

1. **Cover** — the query, stated as the question the viewer asked.
2. **The diff** — `−` how this is usually done, `+` what the method changes. One line each.
3. **Reproduce it** — the deterministic stub standing in for the model, and the measurement code.
   The slide must say it is a stub (`PROJECT_INSTRUCTIONS.md` §5, filone 3).
4. **The number** — measured by our code: tokens per task, steps to completion, retry rate, or
   success rate on a fixed task. **Never a self-assigned score out of ten.**
5. **Takeaway** — when to use it, and when not to. The "when not to" is what makes it trustworthy.

## What qualifies as a method

Apply `prompts/research.md`. Review `data/radar/*productivity.json`, including the
items marked `suggested_format: method`, for practical tasks and proposed experiments.
The task report proposes an experiment; it does not establish the result. Measure the
baseline and the intervention yourself and complete `source_review` before rendering.

A documented, reproducible way to do a real task better with ChatGPT, Claude, Codex or an agent.
The source must be an artifact: official docs or cookbook, a repo, a gist, a spec. A community post
claiming a better way is a **lead** — follow it to the artifact and cite that. If nothing is
documented, it does not ship.

## Honesty requirements specific to this format

Because a method video makes a *recommendation*, not just a report:

- Say what was measured and what was not. A stub demonstrates structure, not model quality.
- Say where the method fails or is not worth it (below what scale, above what cost).
- If the improvement is small, say it is small. A method that saves 8% is still worth publishing —
  claiming it saves 80% is not.

## Length

4-6 minutes. Long enough to satisfy the query, short enough to produce weekly inside the time
budget (§11). The 10-15 minute Deep Diff shape (`prompts/deep.md`) is the occasional variant of
this same weekly slot, for emerging patterns and multi-stage verifications that need the room.

## Standing corrections
*(none yet)*
