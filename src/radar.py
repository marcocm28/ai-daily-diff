"""Import curated ChatGPT task results, never account credentials or chat history.

Reports are discovery leads. A reported primary URL is not proof of a checked claim.
The author must retrieve it and complete source_review before an episode can render.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
RADAR_DIR = ROOT / "data" / "radar"
TASKS = {"AI Productivity Radar": "productivity", "Novità tecniche AI": "technical"}
KINDS = {"pricing", "deprecation", "vendor_release", "method", "model_weights",
         "tool_release", "dataset", "research"}
VERTICALS = {"models-releases", "cost-limits", "tools-agents", "media-generation", "claims-risks"}


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise ValueError("expected a public HTTP(S) source URL without credentials")
    if parts.hostname.lower() in {"chatgpt.com", "chat.openai.com", "localhost", "127.0.0.1"}:
        raise ValueError("use the public source, not the private ChatGPT conversation")
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"),
                       urlencode(sorted(query)), ""))


def normalize_report(report: dict) -> dict:
    if not isinstance(report, dict) or report.get("task") not in TASKS:
        raise ValueError("task must be AI Productivity Radar or Novità tecniche AI")
    report_date = dt.date.fromisoformat(report["date"])
    if not isinstance(report.get("items"), list):
        raise ValueError("items must be a list (empty is valid on a quiet day)")
    if len(report["items"]) > 5:
        raise ValueError("a radar report contains at most five curated leads")
    items = []
    for item in report["items"]:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")
        for field in ("title", "url", "summary", "decision", "example_idea"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"missing or empty {field}")
        if item.get("kind") not in KINDS or item.get("vertical") not in VERTICALS:
            raise ValueError("unknown kind or vertical")
        published = item.get("published_at")
        if published is not None:
            published = dt.date.fromisoformat(published).isoformat()
            if published > report_date.isoformat():
                raise ValueError("publication cannot be after report date")
        if item.get("suggested_format", "daily") not in {"daily", "method", "deep"}:
            raise ValueError("unknown suggested_format")
        # Allowlist fields: raw chat text, scores and personal metadata are not carried forward.
        cleaned = {k: item[k].strip() for k in ("title", "summary", "decision", "example_idea")}
        cleaned.update(url=canonical_url(item["url"]), published_at=published,
                       kind=item["kind"], vertical=item["vertical"],
                       suggested_format=item.get("suggested_format", "daily"),
                       availability=str(item.get("availability", "unknown")),
                       verification_status="pending")
        items.append(cleaned)
    return {"task": report["task"], "date": report_date.isoformat(), "items": items}


def load_candidates(today: dt.date, directory: pathlib.Path = RADAR_DIR) -> list[dict]:
    candidates = []
    for path in sorted(directory.glob("*.json")):
        report = normalize_report(json.loads(path.read_text(encoding="utf-8")))
        age = (today - dt.date.fromisoformat(report["date"])).days
        if not 0 <= age <= 7:
            continue
        for item in report["items"]:
            candidates.append({**item, "source": f"chatgpt-task:{TASKS[report['task']]}",
                               "discovery_task": report["task"], "discovered_at": report["date"],
                               "is_primary_source": False, "requires_source_review": True,
                               "signals": {}})
    return candidates


def import_report(path: pathlib.Path, directory: pathlib.Path = RADAR_DIR) -> pathlib.Path:
    report = normalize_report(json.loads(path.read_text(encoding="utf-8-sig")))
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{report['date']}-{TASKS[report['task']]}.json"
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != content:
        raise ValueError(f"{target} already contains a different report; review it before replacing")
    target.write_text(content, encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=pathlib.Path)
    args = parser.parse_args()
    print(import_report(args.report))
