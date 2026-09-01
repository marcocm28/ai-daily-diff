# SOURCES.md — source registry

> One row per source. `src/ingest.py` reads the endpoint list from here indirectly (see
> `src/ingest.py::SOURCES`); this file is the human-readable ledger of how each source performs,
> which Loop B uses to demote or disable noisy sources (`PROJECT_INSTRUCTIONS.md` §5.1, §10.2).

| Source | Endpoint | Verticals served | Rate limit | Last checked | Items published | Median performance | Status |
|---|---|---|---|---|---|---|---|
| arXiv cs.LG | `rss.arxiv.org/rss/cs.LG` | Architectures & Models, Data & Eval | none published, be polite | 2026-08-28 | 0 | — | active |
| arXiv cs.CL | `rss.arxiv.org/rss/cs.CL` | Architectures & Models, Agents & Prompting, Data & Eval | none published, be polite | 2026-08-28 | 0 | — | active |
| arXiv cs.CV | `rss.arxiv.org/rss/cs.CV` | Architectures & Models, Video & Image Gen | none published, be polite | 2026-08-28 | 0 | — | active |
| arXiv cs.AI | `rss.arxiv.org/rss/cs.AI` | Agents & Prompting | none published, be polite | 2026-08-28 | 0 | — | active |
| HuggingFace Models API | `huggingface.co/api/models?sort=trendingScore` | Architectures & Models, Video & Image Gen | ~unauthenticated, be polite | 2026-08-28 | 0 | — | active |
| HuggingFace Datasets API | `huggingface.co/api/datasets` | Data & Evaluation | ~unauthenticated, be polite | 2026-08-28 | 0 | — | active |
| GitHub Releases API | `api.github.com/repos/<org>/<repo>/releases` | Serving/Inference & Cost, Agents & Prompting | 60/hr unauthenticated, 5000/hr with token | 2026-08-28 | 0 | — | active |
| Official pricing pages | (per-provider, fetched manually) | Serving, Inference & Cost | n/a | 2026-08-28 | 0 | — | active |

**Cross-cutting rule:** Hacker News / Reddit signal ("what people care about") never counts as a
primary source. An item ships only with a primary source URL (`is_primary_source`, §9.2).

**Repos tracked via GitHub Releases API (Serving/Inference & Cost + Agents & Prompting):**
`vllm-project/vllm`, `ggml-org/llama.cpp`, `sgl-project/sglang`, `huggingface/text-generation-inference`.
Edit this list, and the mirrored list in `src/ingest.py::GITHUB_REPOS`, together.
