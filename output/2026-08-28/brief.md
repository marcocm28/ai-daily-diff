# [PIPELINE TEST — not for publish] Prefix cache reuse cuts serving cost

2026-08-28

Every claim below links to a primary source. Every example is executed in CI before this video is published; if an example fails, the video does not ship.

## 01 · A cache-reuse trick cuts long-context serving cost, and it is a config flag.
**Vertical:** SERVING, INFERENCE & COST

WHAT CHANGED — Shared request prefixes get cached once across requests instead of being recomputed for every single one.
WHY IT MATTERS — Serving cost stops scaling with total tokens and starts scaling with unique tokens.
THE NUMBER — 65.7% (fewer tokens billed in the example below)

Run it yourself (9 lines, CPU, offline, <1s):
  examples/2026-08-28-prefix-cache/

Caveat: The prefix must be byte-identical -- one changed timestamp invalidates the cache. Cache residency is bounded by memory. A cache shared across tenants is a data-isolation decision, not just a performance one.

Primary source: https://github.com/vllm-project/vllm
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-08-28-prefix-cache

---
Slides (PDF): https://marcocm28.github.io/ai-daily-diff/2026-08-28/slides.pdf      Cheat sheet (PDF): https://marcocm28.github.io/ai-daily-diff/2026-08-28/cheatsheet.pdf
Episode page: https://marcocm28.github.io/ai-daily-diff/2026-08-28/