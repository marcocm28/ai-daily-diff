"""Stage 1 — INGEST. Pulls raw candidates from free, public, keyless sources and writes them to
data/inbox/YYYY-MM-DD.json for src/select.py to score.

Sources mirror SOURCES.md — keep the two in sync.

Design note: this uses plain `requests`. It is meant to run in GitHub Actions (on a scheduled
workflow) or on a normal machine with normal internet — both have unrestricted outbound access.
It is NOT meant to run inside a Claude session's own sandboxed tools (WebFetch there can reach
these same endpoints, but curl/requests are blocked in that sandbox specifically) — if you are
doing ingestion by hand inside a Claude session, use WebFetch on the same URLs instead of trying
to exec this file there.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

import requests

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
INBOX = ROOT / "data" / "inbox"
UA = {"User-Agent": "ai-daily-diff-ingest/1.0 (+https://github.com/marcocm28/ai-daily-diff)"}

ARXIV_CATEGORIES = ["cs.LG", "cs.CL", "cs.CV", "cs.AI"]

# Mirrors SOURCES.md — edit both together.
GITHUB_REPOS = [
    "vllm-project/vllm",
    "ggml-org/llama.cpp",
    "sgl-project/sglang",
    "huggingface/text-generation-inference",
]


def fetch_arxiv(category: str, limit: int = 25) -> list[dict]:
    url = f"https://rss.arxiv.org/rss/{category}"
    resp = requests.get(url, headers=UA, timeout=20)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        if not title or not link:
            continue
        out.append({
            "source": f"arxiv:{category}",
            "title": title,
            "url": link,
            "summary": desc,
            "is_primary_source": True,
            "signals": {},
        })
        if len(out) >= limit:
            break
    return out


def fetch_hf_models(limit: int = 25) -> list[dict]:
    url = "https://huggingface.co/api/models"
    params = {"sort": "trendingScore", "direction": -1, "limit": limit}
    resp = requests.get(url, headers=UA, params=params, timeout=20)
    resp.raise_for_status()
    out = []
    for m in resp.json():
        model_id = m.get("id") or m.get("modelId")
        if not model_id:
            continue
        out.append({
            "source": "huggingface:models",
            "title": model_id,
            "url": f"https://huggingface.co/{model_id}",
            "summary": ", ".join(m.get("tags", [])[:8]),
            "is_primary_source": True,
            "signals": {"downloads": m.get("downloads", 0), "likes": m.get("likes", 0)},
        })
    return out


def fetch_hf_datasets(limit: int = 25) -> list[dict]:
    url = "https://huggingface.co/api/datasets"
    params = {"sort": "trendingScore", "direction": -1, "limit": limit}
    resp = requests.get(url, headers=UA, params=params, timeout=20)
    resp.raise_for_status()
    out = []
    for d in resp.json():
        ds_id = d.get("id")
        if not ds_id:
            continue
        out.append({
            "source": "huggingface:datasets",
            "title": ds_id,
            "url": f"https://huggingface.co/datasets/{ds_id}",
            "summary": ", ".join(d.get("tags", [])[:8]),
            "is_primary_source": True,
            "signals": {"downloads": d.get("downloads", 0), "likes": d.get("likes", 0)},
        })
    return out


def fetch_github_releases(repo: str, limit: int = 5) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/releases"
    resp = requests.get(url, headers=UA, params={"per_page": limit}, timeout=20)
    resp.raise_for_status()
    out = []
    for rel in resp.json():
        if rel.get("draft"):
            continue
        out.append({
            "source": f"github:{repo}",
            "title": f"{repo} {rel.get('tag_name', '')} — {rel.get('name') or ''}".strip(),
            "url": rel.get("html_url", f"https://github.com/{repo}/releases"),
            "summary": (rel.get("body") or "")[:600],
            "is_primary_source": True,
            "signals": {"published_at": rel.get("published_at")},
        })
    return out


def run(date: dt.date | None = None) -> pathlib.Path:
    date = date or dt.date.today()
    candidates: list[dict] = []
    errors: list[str] = []

    for cat in ARXIV_CATEGORIES:
        try:
            candidates += fetch_arxiv(cat)
        except Exception as e:  # noqa: BLE001 — ingestion must not die on one bad source
            errors.append(f"arxiv:{cat}: {e}")

    for fn, name in ((fetch_hf_models, "hf:models"), (fetch_hf_datasets, "hf:datasets")):
        try:
            candidates += fn()
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: {e}")

    for repo in GITHUB_REPOS:
        try:
            candidates += fetch_github_releases(repo)
        except Exception as e:  # noqa: BLE001
            errors.append(f"github:{repo}: {e}")

    INBOX.mkdir(parents=True, exist_ok=True)
    out_path = INBOX / f"{date.isoformat()}.json"
    out_path.write_text(json.dumps({
        "date": date.isoformat(),
        "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        "candidate_count": len(candidates),
        "errors": errors,
        "candidates": candidates,
    }, indent=2), encoding="utf-8")

    print(f"Wrote {len(candidates)} candidates to {out_path}")
    if errors:
        print(f"{len(errors)} source(s) failed (non-fatal):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    return out_path


if __name__ == "__main__":
    run()
