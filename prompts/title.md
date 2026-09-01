# Prompt — titles and thumbnails

## Title
Pattern: `<headline in plain words> — AI Daily Diff <Mon DD>`

Rules:
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
