# Prompt — titles and thumbnails

## Title — two patterns, because the two formats get traffic from different places

**Daily Diff:** `<headline in plain words> — AI Daily Diff <Mon DD>`
Those views come from subscribers and browse, where the brand prefix helps recall.

**Method Diff (weekly):** `<the query, phrased the way a person types it>` — and nothing else.
Those views come from search. The title is finite, and every word spent on branding is a word not
spent on the query. The brand lives in the thumbnail logo and the end card. See `prompts/method.md`.

- ✅ `The measured way to keep an agent on track across long sessions`
- ❌ `AI Daily Diff Sep 9 — agent memory`

Rules for both:
- The headline half must be understandable with zero prior context — no acronym left unexpanded,
  no "you won't believe" framing, no exaggeration the video doesn't back up (§4: policy +
  accuracy constraints are not optimizable, even if the loop finds exaggeration raises CTR).
- Lead with the concrete change or number if it fits; the number is often the strongest hook a
  technical audience responds to.
- Never claim a result the example does not reproduce.

## Thumbnail (`src/thumbnail.py`)
- One number or one short technical term, large, high contrast.
- No faces, no red arrows, no company logos as the subject.
- Same HTML/CSS engine as the deck — parametric, so thumbnails are testable like everything else.
- In the dev niche, restraint is the quality signal: looking different from slop content is
  positioning, not a compromise.

## Standing corrections
*(none yet — this is where Loop A's title/thumbnail experiments get written up once closed)*
