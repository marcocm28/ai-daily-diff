# SOURCES.md — source registry

> One row per source. `src/ingest.py` holds the machine-readable copy of this list; this file is
> the human-readable ledger of how each source performs, which Loop B uses to demote or disable
> noisy ones (`PROJECT_INSTRUCTIONS.md` §5.1, §10.2).
>
> **Revised 2026-09-02.** The original list was arXiv-heavy, which is how the first real episode
> ended up as two preprints. The `kind` column is what `src/selection.py` scores against: pricing
> and deprecations start at the top of both blast radius and decision relevance, research starts
> near the bottom.

| Source | Endpoint | kind | Verticals | Rate limit | Last checked | Published | Median perf. | Status |
|---|---|---|---|---|---|---|---|---|
| OpenRouter models | `openrouter.ai/api/v1/models` | pricing | Cost & Limits | unauthenticated, be polite | 2026-09-02 ✅ | 0 | — | active |
| OpenAI deprecations | `platform.openai.com/docs/deprecations` | deprecation | Claims & Risks | watch page, hashed | 2026-09-02 | 0 | — | active |
| Anthropic model deprecations | `docs.claude.com/en/docs/about-claude/model-deprecations` | deprecation | Claims & Risks | watch page, hashed | 2026-09-02 | 0 | — | active |
| Gemini API changelog | `ai.google.dev/gemini-api/docs/changelog` | vendor_release | Models & Releases | watch page, hashed | 2026-09-02 | 0 | — | active |
| HuggingFace models | `huggingface.co/api/models?sort=trendingScore` | model_weights | Models & Releases | unauthenticated | 2026-09-02 ✅ | 1 | — | active |
| HuggingFace datasets | `huggingface.co/api/datasets` | dataset | Claims & Risks | unauthenticated | 2026-09-02 | 0 | — | active |
| GitHub releases — vLLM | `api.github.com/repos/vllm-project/vllm/releases` | tool_release | Cost & Limits | 60/hr anon, 5000/hr with token | 2026-09-02 | 0 | — | active |
| GitHub releases — llama.cpp | `.../ggml-org/llama.cpp/releases` | tool_release | Cost & Limits | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — SGLang | `.../sgl-project/sglang/releases` | tool_release | Cost & Limits | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — Ollama | `.../ollama/ollama/releases` | tool_release | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — LangGraph | `.../langchain-ai/langgraph/releases` | tool_release | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — MCP servers | `.../modelcontextprotocol/servers/releases` | tool_release | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — ComfyUI | `.../comfyanonymous/ComfyUI/releases` | tool_release | Media Generation | as above | 2026-09-02 | 0 | — | active |
| GitHub releases — transformers | `.../huggingface/transformers/releases` | tool_release | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| OpenAI Cookbook (commits) | `api.github.com/repos/openai/openai-cookbook/commits` | method | Tools & Agents | 60/hr anon | 2026-09-02 | 0 | — | active |
| Anthropic Cookbook (commits) | `.../anthropics/anthropic-cookbook/commits` | method | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| Claude Code (commits) | `.../anthropics/claude-code/commits` | method | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| MCP spec + servers (commits) | `.../modelcontextprotocol/*/commits` | method | Tools & Agents | as above | 2026-09-02 | 0 | — | active |
| GitHub search — MCP servers | `api.github.com/search/repositories` | method | Tools & Agents | ~10/min anon | 2026-09-02 | 0 | — | active |
| GitHub search — Claude Code skills | as above | method | Tools & Agents | ~10/min anon | 2026-09-02 | 0 | — | active |
| GitHub search — multi-agent / orchestration | as above | method | Tools & Agents | ~10/min anon | 2026-09-02 | 0 | — | active |
| GitHub search — prompt / context engineering | as above | method | Tools & Agents | ~10/min anon | 2026-09-02 | 0 | — | active |
| arXiv cs.LG | `rss.arxiv.org/rss/cs.LG` | research | Claims & Risks | none published, be polite | 2026-09-02 ✅ | 2 | — | active, demoted |
| arXiv cs.CL | `rss.arxiv.org/rss/cs.CL` | research | Tools & Agents | as above | 2026-09-02 | 0 | — | active, demoted |
| arXiv cs.CV | `rss.arxiv.org/rss/cs.CV` | research | Media Generation | as above | 2026-09-02 | 0 | — | active, demoted |
| arXiv cs.AI | `rss.arxiv.org/rss/cs.AI` | research | Tools & Agents | as above | 2026-09-02 | 0 | — | active, demoted |

✅ = reachable, verified by fetching it on that date.

## Caveats found by verification, not by reading docs

**OpenRouter `created` is a listing date, not a release date** (found 2026-09-02). `granite-4.2-8b`
reports `created: 2026-08-31` on OpenRouter and `createdAt: 2026-08-07` on its Hugging Face repo.
Treating it as a publication date made month-old models look like today's news. `src/ingest.py`
now stores it as `listed_at` and leaves `published_at` empty for pricing candidates: a price
story's freshness comes from a *change* in the price, caught by the watch mechanism, never from
this field.

**GitHub's REST API answers 403 to our fetcher, the HTML release pages do not** (2026-09-02).
When ingesting by hand in a Claude session, use `github.com/<org>/<repo>/releases` rather than
`api.github.com`. `src/ingest.py` keeps using the API, which works fine from GitHub Actions and
from a normal machine — this is a constraint of the session sandbox, not of the source.

**Some vendor doc domains require per-URL approval before our fetcher will load them**
(`docs.claude.com`, 2026-09-02). For those, the URL has to be pasted into the session by Marco,
or the item sourced from a domain that loads. Never substitute a reseller's page for a vendor's
announcement just because it loads: that breaks Gate 1's "primary source" requirement.

**"Demoted" means:** still ingested, still scored, but carrying `research_only_penalty` unless the
paper ships weights or code. Set `shipped_artifact: true` on the candidate by hand when it does —
a preprint with a working repo is a different animal from a preprint with a promise.

**Cross-cutting rule:** Hacker News and Reddit tell you *what people care about*; the primary
source tells you *what is true*. An item ships only with the second. When a community post *is*
the story ("I found a better way to do X"), the item is the **documented artifact** it points to —
the repo, the gist, the doc page — never the post itself, and the slide says which is which.

**Why commits and not pages, for official docs:** a new commit to an official cookbook is a method
that just got documented, timestamped, by the people who define the thing. It is the cleanest
signal available for the tools-agents vertical, and the rendered HTML pages don't expose it.

**Why GitHub search has no star floor:** a small repo with an interesting architecture is exactly
what the big feeds miss, and it is where an emerging pattern is visible first. Stars are recorded
as an interest signal, not used as a gate.

## Wanted, not yet wired

Vendor pricing pages are the highest-value watch targets and each needs its URL confirmed before
being added (they move often, and a 404 that silently returns HTML would look like a "change"):
OpenAI pricing, Anthropic pricing, Google AI pricing, AWS Bedrock pricing, Azure OpenAI pricing.
Add them one at a time, and check the first hash change by hand before trusting the mechanism.
