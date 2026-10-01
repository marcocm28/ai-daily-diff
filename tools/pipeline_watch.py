"""Inspect/recover GitHub work; never author, render locally or upload to YouTube.

Run on GitHub and from the existing Codex heartbeat. Local authentication uses the
existing Git Credential Manager; no new credentials are stored or printed.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys
from zoneinfo import ZoneInfo

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from production_schedule import plan, settings, timestamp

REPOSITORY = "marcocm28/ai-daily-diff"
WORKFLOWS = ("ingest.yml", "render.yml", "upload.yml", "pages.yml", "reconcile.yml", "channel-sync.yml")


class GitHub:
    def __init__(self):
        token = os.environ.get("GH_TOKEN")
        if not token:
            result = subprocess.run(["git", "credential", "fill"],
                input=f"protocol=https\nhost=github.com\npath={REPOSITORY}.git\n\n",
                text=True, capture_output=True, check=True,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never"})
            token = dict(line.split("=", 1) for line in result.stdout.splitlines()
                         if "=" in line).get("password")
        if not token:
            raise ValueError("GitHub credential unavailable; authenticate Git Credential Manager")
        self.session = requests.Session()
        self.session.headers.update(Authorization=f"Bearer {token}", Accept="application/vnd.github+json")
        trust = ROOT.parent / "windows-trust.pem"
        if trust.is_file() and not os.environ.get("GITHUB_ACTIONS"):
            self.session.verify = str(trust)

    def get(self, path):
        response = self.session.get(f"https://api.github.com/repos/{REPOSITORY}/{path}", timeout=30)
        if response.status_code == 404 and path.startswith("contents/"):
            return None
        response.raise_for_status()
        return response.json()

    def file(self, path):
        data = self.get(f"contents/{path}?ref=main")
        return json.loads(base64.b64decode(data["content"])) if data else None

    def documents(self, directory):
        entries = self.get(f"contents/{directory}?ref=main") or []
        return {p["name"][:-5]: self.file(p["path"]) for p in entries if p["name"].endswith(".json")}

    def runs(self, workflow):
        data = self.get(f"actions/workflows/{workflow}/runs?branch=main&per_page=20")
        return [r for r in data["workflow_runs"] if r["event"] in {"push", "schedule", "workflow_dispatch", "workflow_run"}
                and r.get("head_repository", {}).get("full_name") == REPOSITORY]

    def post(self, path, body=None):
        response = self.session.post(f"https://api.github.com/repos/{REPOSITORY}/{path}", json=body, timeout=30)
        response.raise_for_status()


def recovery_actions(now, missing_inbox, runs, pending_receipts=False, config=None, queued_at=None):
    config = config or settings()
    actions = []
    today = now.astimezone(ZoneInfo(config["timezone"])).date()
    for workflow in WORKFLOWS:
        history = runs.get(workflow, [])
        # Never start a second job while an earlier dispatch is queued or active.
        if any(r["status"] != "completed" for r in history):
            continue
        latest = history[0] if history else None
        recent = latest and now - timestamp(latest["updated_at"]) < dt.timedelta(minutes=config["retry_minutes"])
        if recent:
            continue
        render = next(iter(runs.get("render.yml", [])), None)
        newer_work = bool(latest and (
            (workflow == "ingest.yml" and missing_inbox and
             timestamp(latest["created_at"]).astimezone(ZoneInfo(config["timezone"])).date() < today)
            or (workflow == "render.yml" and queued_at and timestamp(latest["created_at"]) < timestamp(queued_at))
            or (workflow in {"upload.yml", "pages.yml"} and render and
                render["status"] == "completed" and render["conclusion"] == "success" and
                timestamp(latest["created_at"]) < timestamp(render["created_at"]))
        ))
        if latest and latest["conclusion"] in {"failure", "timed_out", "cancelled"} and not newer_work:
            # One automatic retry, never infinite retries of a gate/auth failure.
            if (now - timestamp(latest["created_at"]) < dt.timedelta(days=1)
                    and latest.get("run_attempt", 1) < config["max_run_attempts"]):
                actions.append({"workflow": workflow, "action": "rerun", "run_id": latest["id"]})
            continue
        if workflow == "ingest.yml" and missing_inbox and today.weekday() in config["weekdays"]:
            if latest and timestamp(latest["created_at"]).astimezone(ZoneInfo(config["timezone"])).date() == today:
                # A successful run without its inbox is a fault, not a reason to loop.
                continue
            actions.append({"workflow": workflow, "action": "dispatch"})
        if workflow == "reconcile.yml" and pending_receipts:
            actions.append({"workflow": workflow, "action": "dispatch"})
        if workflow == "render.yml" and queued_at:
            if not latest or timestamp(latest["created_at"]) < timestamp(queued_at):
                actions.append({"workflow": workflow, "action": "dispatch"})
        if workflow in {"upload.yml", "pages.yml"}:
            if (render and render["status"] == "completed" and render["conclusion"] == "success"
                    and dt.timedelta(minutes=config["retry_minutes"]) <= now - timestamp(render["updated_at"]) < dt.timedelta(days=1)
                    and (not latest or timestamp(latest["created_at"]) < timestamp(render["created_at"]))):
                inputs = {"render_run_id": str(render["id"])}
                if workflow == "upload.yml":
                    inputs["dry_run"] = "false"
                actions.append({"workflow": workflow, "action": "dispatch", "inputs": inputs})
    return actions


def inspect(api, now):
    config = settings()
    day = now.astimezone(ZoneInfo(config["timezone"])).date()
    inbox = api.file(f"data/inbox/{day}.json")
    missing = [] if inbox is not None and inbox.get("date") == str(day) else ["github-inbox"]
    episodes = api.documents("data/episodes")
    receipts = api.documents("data/publications")
    runs = {workflow: api.runs(workflow) for workflow in WORKFLOWS}
    # An absent feed triggers recovery, not a research blockade: Codex performs
    # the project's own primary-source search and records its real provenance.
    result = plan(now, list(episodes.values()), receipts, [], config)
    result["missing_inputs"] = missing
    result["research_mode"] = "project-primary-research"
    result["checked_at"] = now.isoformat()
    result["runs"] = {key: [{k: r.get(k) for k in ("id", "status", "conclusion", "run_attempt", "html_url")}
                            for r in values[:2]] for key, values in runs.items()}
    result["receipts"] = [{k: r.get(k) for k in ("episode_id", "date", "state", "url", "actual_privacy", "publish_at")}
                          for r in receipts.values()]
    queued = [e["publication"]["queued_at"] for key, e in episodes.items()
              if e.get("publication", {}).get("ready") and e["publication"].get("queued_at")
              and key not in receipts and e["date"] == str(day)]
    result["recovery_actions"] = recovery_actions(now, "github-inbox" in missing, runs,
        any(r.get("state") != "published" for r in receipts.values()), config, max(queued) if queued else None)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Dispatch missing collection or one bounded retry")
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()
    api = GitHub()
    result = inspect(api, dt.datetime.now(dt.timezone.utc))
    result["actions_applied"] = []
    if args.apply:
        for action in result["recovery_actions"]:
            if action["action"] == "rerun":
                api.post(f"actions/runs/{action['run_id']}/rerun-failed-jobs")
            else:
                api.post(f"actions/workflows/{action['workflow']}/dispatches",
                         {"ref": "main", "inputs": action.get("inputs", {})})
            result["actions_applied"].append(action)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
