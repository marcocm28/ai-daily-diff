# Prompt — titles and thumbnails

> Editorial update 25 September 2026: read `prompts/editorial.md` first. Its novelty,
> practical-value and honest-evidence gates supersede conflicting editorial preferences
> below. Existing schema and CI requirements still apply.

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
- Lead with the newly possible action and recognisable task. Use a number only when
  it materially explains the capability, never merely as an attention device.
- Attribute vendor demonstrations as vendor claims. Never present them as our results;
  claims about our tests must match what our example reproduces.

## Thumbnail (`src/thumbnail.py`)
- One short, plain-language capability or useful quantity, large, high contrast.
- No faces, no red arrows, no company logos as the subject.
- Same HTML/CSS engine as the deck — parametric, so thumbnails are testable like everything else.
- In the dev niche, restraint is the quality signal: looking different from slop content is
  positioning, not a compromise.

## Standing corrections
*(none yet — this is where Loop A's title/thumbnail experiments get written up once closed)*

## Search discovery and YouTube descriptions

For every episode choose one primary search intent: exact model/product name plus
the new feature or task. Add a second phrase only when it describes real coverage.
Use the official current name/version and natural English throughout title, opening
description and video. Do not list other popular models absent from the episode.
Prefer `<model/product>: <new capability or practical task> — AI Daily Diff <date>`
for Daily; weekly titles name the model and the actual how-to question. Keep the
title within YouTube's 100-character limit, with the useful topic before branding.
Search relevance cannot justify choosing a weaker or repeated story.

Write a unique top-level `youtube_description` string in the episode JSON (plain
text, 500–1800 characters as an editorial target, maximum 2500). It is the opening
description consumed by upload.py; do not rely on an automatic dump of the brief.

1. First two sentences: exact model/product, concrete verified novelty, and what
   the viewer learns or can do. Include the primary search phrase naturally.
2. Short topic bullets: the specific features/use cases actually covered, with
   availability or important limits where needed. No code dumps or repeated keywords.
3. A concise invitation to subscribe to AI Daily Diff for verified developments in
   leading AI models. Promise useful future coverage, not a guaranteed release tomorrow.

The uploader appends primary-source links, episode/download links, publication marker
and music credits. Do not duplicate these boilerplate sections in the authored text.
Use timestamps only when verified against the final rendered video; never estimate
chapters. Hashtags are optional, relevant and sparse, never a substitute for prose.
Do not invent keyword volumes, popularity or guaranteed ranking/subscriber growth.
Use available YouTube Analytics search terms to refine later episodes; if unavailable,
write clear query-shaped language without pretending demand was measured.

Before queueing, inspect `upload.build_description(episode)` and the title together:
the visible opening must identify the model and payoff; metadata must match the video;
links, credits and the episode marker must survive length handling. Record the chosen
query and the metadata review in editorial_review.

Official guidance consulted: https://support.google.com/youtube/answer/12948449
and https://support.google.com/youtube/answer/141805 . SEO supports discovery;
viewer satisfaction and returning viewers still require the editorial promise.
