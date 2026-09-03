"""Stage 1 — INGEST. Pulls raw candidates from free, public, keyless sources and writes them to
data/inbox/YYYY-MM-DD.json for src/selection.py to score.

Sources mirror SOURCES.md — keep the two in sync.

Every candidate carries a `kind` (pricing / deprecation / vendor_release / model_weights /
tool_release / dataset / research) and a `vertical`, because that pair is what the scoring in
src/selection.py reads. A source that cannot say which kind it is does not belong here.

The watch-page mechanism deserves a note: vendor pricing and deprecation pages have no feed, so
we hash their text and emit a candidate only when the hash moves. That is literally a diff, which
is the whole premise of the channel — and it catches the highest-decision-relevance news there
is (a price changed, an endpoint is going away) that no RSS feed would have told us about.

Design note: this uses plain `requests`. It is meant to run in GitHub Actions (on a scheduled
workflow) or on a normal machine with normal internet. It is NOT meant to run inside a Claude
session's sandbox, where curl/requests are blocked — there, use WebFetch on the same URLs.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
INBOX = ROOT / "data" / "inbox"
WATCH_STATE = ROOT / "data" / "dedup_index" / "watch_hashes.json"
UA = {"User-Agent": "ai-daily-diff-ingest/1.0 (+https://github.com/marcocm28/ai-daily-diff)"}
TIMEOUT = 25

ARXIV_CATEGORIES = ["cs.LG", "cs.CL", "cs.CV", "cs.AI"]

# Tools people actually run. Mirrors SOURCES.md — edit both together.
GITHUB_REPOS = {
    "vllm-project/vllm": "cost-limits",
    "ggml-org/llama.cpp": "cost-limits",
    "sgl-project/sglang": "cost-limits",
    "ollama/ollama": "tools-agents",
    "langchain-ai/langgraph": "tools-agents",
    "modelcontextprotocol/servers": "tools-agents",
    "comfyanonymous/ComfyUI": "media-generation",
    "huggingface/transformers": "tools-agents",
}

# Official docs and cookbooks: a new commit here is a newly *documented* method, which is the
# highest-value kind of item in the tools-agents vertical (see PROJECT_INSTRUCTIONS.md §5,
# filone 3). Commits are a feed the HTML pages don't give us.
COOKBOOK_REPOS = {
    "openai/openai-cookbook": "tools-agents",
    "anthropics/anthropic-cookbook": "tools-agents",
    "anthropics/claude-code": "tools-agents",
    "modelcontextprotocol/servers": "tools-agents",
    "modelcontextprotocol/modelcontextprotocol": "tools-agents",
}

# GitHub code search, for methods and tooling that never get a release or a blog post. Kept to a
# handful of queries: unauthenticated search allows ~10 requests a minute.
GITHUB_SEARCHES = [
    ("mcp server in:name,description", "tools-agents"),
    ("claude code skill OR skills in:name,description", "tools-agents"),
    ("multi-agent OR agent orchestration in:name,description", "tools-agents"),
    ("prompt engineering OR context engineering in:name,description", "tools-agents"),
]

# Pages with no feed, watched for changes. A moved hash is the candidate.
WATCH_PAGES = [
    ("https://platform.openai.com/docs/deprecations", "deprecation", "claims-risks"),
    ("https://docs.claude.com/en/docs/about-claude/model-deprecations", "deprecation", "claims-risks"),
    ("https://ai.google.dev/gemini-api/docs/changelog", "vendor_release", "models-releases"),
]

VERTICAL_BY_ARXIV = {
    "cs.LG": "claims-risks", "cs.CL": "tools-agents",
    "cs.CV": "media-generation", "cs.AI": "tools-agents",
}


def _get(url: str, **kw):
    resp = requests.get(url, headers=UA, timeout=TIMEOUT, **kw)
    resp.raise_for_status()
    return resp


def fetch_openrouter_pricing(top: int = 40) -> list[dict]:
    """Machine-readable prices for hundreds of models, no key required. The highest-value source
    we have for the cost-limits vertical: a price is a fact, and a price change is a decision."""
    data = _get("https://openrouter.ai/api/v1/models").json().get("data", [])
    out = []
    for m in data[:top]:
        pricing = m.get("pricing", {}) or {}
        out.append({
            "source": "openrouter:models",
            "kind": "pricing",
            "vertical": "cost-limits",
            "title": f"{m.get('name') or m.get('id')} — "
                      f"${float(pricing.get('prompt') or 0) * 1e6:.2f}/M in, "
                      f"${float(pricing.get('completion') or 0) * 1e6:.2f}/M out",
            "url": f"https://openrouter.ai/{m.get('id', '')}",
            "summary": f"context {m.get('context_length')}",
            "is_primary_source": True,
            # OpenRouter's `created` is when the model was LISTED THERE, not when it was
            # released. Verified 2026-09-02: granite-4.2-8b shows created 2026-08-31 on
            # OpenRouter and 2026-08-07 on the Hugging Face repo. Feeding it to published_at
            # made month-old models look like today's news, so it is kept under its own name
            # and never used as a release date. A price story's freshness comes from a *change*
            # in the price (the watch mechanism), not from this field.
            "listed_at": (dt.datetime.utcfromtimestamp(m["created"]).date().isoformat()
                           if m.get("created") else None),
            "published_at": None,
            "signals": {},
            "raw": {"id": m.get("id"), "pricing": pricing, "context_length": m.get("context_length")},
        })
    return out


def fetch_hf(endpoint: str, kind: str, vertical: str, limit: int = 25) -> list[dict]:
    data = _get(f"https://huggingface.co/api/{endpoint}",
                params={"sort": "trendingScore", "direction": -1, "limit": limit}).json()
    prefix = "datasets/" if endpoint == "datasets" else ""
    out = []
    for m in data:
        rid = m.get("id") or m.get("modelId")
        if not rid:
            continue
        out.append({
            "source": f"huggingface:{endpoint}",
            "kind": kind,
            "vertical": vertical,
            "title": rid,
            "url": f"https://huggingface.co/{prefix}{rid}",
            "summary": ", ".join(m.get("tags", [])[:8]),
            "is_primary_source": True,
            "shipped_artifact": True,
            "published_at": (m.get("createdAt") or "")[:10] or None,
            "signals": {"downloads": m.get("downloads", 0), "likes": m.get("likes", 0)},
        })
    return out


def fetch_github_releases(repo: str, vertical: str, limit: int = 3) -> list[dict]:
    data = _get(f"https://api.github.com/repos/{repo}/releases", params={"per_page": limit}).json()
    out = []
    for rel in data:
        if rel.get("draft"):
            continue
        out.append({
            "source": f"github:{repo}",
            "kind": "tool_release",
            "vertical": vertical,
            "title": f"{repo} {rel.get('tag_name', '')} — {rel.get('name') or ''}".strip(" —"),
            "url": rel.get("html_url", f"https://github.com/{repo}/releases"),
            "summary": (rel.get("body") or "")[:800],
            "is_primary_source": True,
            "shipped_artifact": True,
            "published_at": (rel.get("published_at") or "")[:10] or None,
            "signals": {},
        })
    return out


def fetch_arxiv(category: str, limit: int = 20) -> list[dict]:
    root = ET.fromstring(_get(f"https://rss.arxiv.org/rss/{category}").content)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        out.append({
            "source": f"arxiv:{category}",
            "kind": "research",
            "vertical": VERTICAL_BY_ARXIV.get(category, "claims-risks"),
            "title": title,
            "url": link,
            "summary": (item.findtext("description") or "").strip()[:800],
            "is_primary_source": True,
            "shipped_artifact": False,   # set true by hand if the paper ships weights or code
            "published_at": dt.date.today().isoformat(),
            "signals": {},
        })
        if len(out) >= limit:
            break
    return out


def fetch_cookbook_commits(repo: str, vertical: str, days: int = 3, limit: int = 6) -> list[dict]:
    """Recent commits to an official cookbook or docs repo: a documented method, from the source
    that defines it. `kind: method` scores near the top — see src/selection.py::SOURCE_PROFILE."""
    since = (dt.datetime.utcnow() - dt.timedelta(days=days)).isoformat() + "Z"
    data = _get(f"https://api.github.com/repos/{repo}/commits",
                params={"since": since, "per_page": limit}).json()
    out = []
    for c in data:
        message = ((c.get("commit") or {}).get("message") or "").split("\n")[0]
        # merge and version-bump noise is not a documented method
        if not message or message.lower().startswith(("merge ", "bump ", "chore", "ci:", "docs: fix typo")):
            continue
        out.append({
            "source": f"cookbook:{repo}",
            "kind": "method",
            "vertical": vertical,
            "title": f"{repo}: {message[:140]}",
            "url": c.get("html_url", f"https://github.com/{repo}"),
            "summary": "New or updated content in an official cookbook / docs repo.",
            "is_primary_source": True,
            "shipped_artifact": True,
            "published_at": ((c.get("commit") or {}).get("author") or {}).get("date", "")[:10] or None,
            "signals": {},
        })
    return out


def search_github(query: str, vertical: str, days: int = 3, limit: int = 10) -> list[dict]:
    """Repos matching a method/tooling query, pushed recently. Deliberately not filtered by star
    count: a small repo with an interesting architecture is exactly what the big feeds miss."""
    pushed = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    data = _get("https://api.github.com/search/repositories",
                params={"q": f"{query} pushed:>={pushed}", "sort": "updated",
                         "order": "desc", "per_page": limit}).json()
    out = []
    for r in data.get("items", []):
        out.append({
            "source": "github:search",
            "kind": "method",
            "vertical": vertical,
            "title": f"{r.get('full_name')} — {(r.get('description') or '')[:120]}",
            "url": r.get("html_url", ""),
            "summary": (r.get("description") or "")[:400],
            "is_primary_source": True,
            "shipped_artifact": True,
            "published_at": (r.get("pushed_at") or "")[:10] or None,
            "signals": {"stars": r.get("stargazers_count", 0)},
        })
    return out


def _text_fingerprint(html: str) -> str:
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(text.encode("utf-8", "ignore")).hexdigest()


def fetch_watch_pages() -> list[dict]:
    """Emits a candidate only for pages whose text changed since the last run."""
    state = json.loads(WATCH_STATE.read_text(encoding="utf-8")) if WATCH_STATE.exists() else {}
    out = []
    for url, kind, vertical in WATCH_PAGES:
        try:
            fingerprint = _text_fingerprint(_get(url).text)
        except Exception as e:  # noqa: BLE001 — a watched page going down is not fatal
            print(f"  watch page failed: {url}: {e}", file=sys.stderr)
            continue
        previous = state.get(url)
        state[url] = fingerprint
        if previous and previous != fingerprint:
            out.append({
                "source": f"watch:{url}",
                "kind": kind,
                "vertical": vertical,
                "title": f"CHANGED: {url}",
                "url": url,
                "summary": "The text of this page changed since the last check. Diff it by hand "
                            "and find what moved — this is a lead, not a story.",
                "is_primary_source": True,
                "published_at": dt.date.today().isoformat(),
                "signals": {},
            })
    WATCH_STATE.parent.mkdir(parents=True, exist_ok=True)
    WATCH_STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return out


def run(date: dt.date | None = None) -> pathlib.Path:
    date = date or dt.date.today()
    candidates: list[dict] = []
    errors: list[str] = []

    jobs = [
        ("openrouter:pricing", lambda: fetch_openrouter_pricing()),
        ("hf:models", lambda: fetch_hf("models", "model_weights", "models-releases")),
        ("hf:datasets", lambda: fetch_hf("datasets", "dataset", "claims-risks")),
        ("watch:pages", fetch_watch_pages),
    ]
    jobs += [(f"github:{r}", (lambda r=r, v=v: fetch_github_releases(r, v)))
             for r, v in GITHUB_REPOS.items()]
    jobs += [(f"cookbook:{r}", (lambda r=r, v=v: fetch_cookbook_commits(r, v)))
             for r, v in COOKBOOK_REPOS.items()]
    jobs += [(f"search:{q[:24]}", (lambda q=q, v=v: search_github(q, v)))
             for q, v in GITHUB_SEARCHES]
    jobs += [(f"arxiv:{c}", (lambda c=c: fetch_arxiv(c))) for c in ARXIV_CATEGORIES]

    for name, fn in jobs:
        try:
            candidates += fn()
        except Exception as e:  # noqa: BLE001 — ingestion must not die on one bad source
            errors.append(f"{name}: {e}")

    INBOX.mkdir(parents=True, exist_ok=True)
    out_path = INBOX / f"{date.isoformat()}.json"
    out_path.write_text(json.dumps({
        "date": date.isoformat(),
        "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        "candidate_count": len(candidates),
        "errors": errors,
        "candidates": candidates,
    }, indent=2), encoding="utf-8")

    by_kind: dict[str, int] = {}
    for c in candidates:
        by_kind[c.get("kind", "?")] = by_kind.get(c.get("kind", "?"), 0) + 1
    print(f"Wrote {len(candidates)} candidates to {out_path}")
    for kind, n in sorted(by_kind.items(), key=lambda kv: -kv[1]):
        print(f"  {kind:16} {n}")
    if errors:
        print(f"{len(errors)} source(s) failed (non-fatal):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    return out_path


if __name__ == "__main__":
    run()
