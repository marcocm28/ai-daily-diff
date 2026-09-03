# The same work costs $0.30 or $80 — AI Daily Diff Sep 2

2026-09-02

Every claim below links to a primary source. Every example is executed in CI before this video is published; if an example fails, the video does not ship.

## 01 · Same code-review workload, same platform: the price list spans 267× from cheapest to most expensive.
**Vertical:** COST & LIMITS

WHAT CHANGED — Output prices for long-context models on one platform span $0.15 to $50 per million tokens today.
WHY IT MATTERS — Above a certain volume the model you pick decides the bill, not how tightly you write the prompt.
THE NUMBER — $0.30 → $80.00 (the same 200-review month, cheapest against most expensive on today's list — 267×)

Run it yourself (9 lines, CPU, offline, < 1 s):
  examples/2026-09-02-price-spread/

Caveat: This is a cost comparison, not a quality one, and prices move. The example vendors today's price list so the arithmetic stays reproducible — re-fetch before acting on it.

Primary source: https://openrouter.ai/api/v1/models
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-09-02-price-spread

## 02 · Ollama now honours the sampling defaults declared inside the model file. Local outputs may shift.
**Vertical:** TOOLS & AGENTS

WHAT CHANGED — Release v0.33.3 honours GGUF-defined default parameters, so a model runs with the settings its author shipped.
WHY IT MATTERS — If you relied on the runner's own defaults, this upgrade changes your output distribution.
THE NUMBER — 12 → 4 (tokens the model can pick at one step — same weights, only the defaults differ)

Run it yourself (14 lines, numpy, CPU, offline, < 1 s):
  examples/2026-09-02-gguf-defaults/

Caveat: We are not claiming what Ollama's previous defaults were: the release note says defaults are now honoured, and our example quantifies why that class of change matters. Check your own before and after.

Primary source: https://github.com/ollama/ollama/releases
Tested example: https://github.com/marcocm28/ai-daily-diff/tree/main/examples/2026-09-02-gguf-defaults

---
Music: "Nebula" by The Grey Room / Density & Time, from the YouTube Audio Library.

Slides (PDF): https://marcocm28.github.io/ai-daily-diff/2026-09-02/slides.pdf      Cheat sheet (PDF): https://marcocm28.github.io/ai-daily-diff/2026-09-02/cheatsheet.pdf
Episode page: https://marcocm28.github.io/ai-daily-diff/2026-09-02/