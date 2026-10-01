"""Bind publication to a verified CI release and persist upload reservations on GitHub."""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import pathlib
import re

import requests
import schema
from production_schedule import timestamp
from episode_identity import episode_key

ROOT = pathlib.Path(__file__).resolve().parent.parent


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def eligible(episode: dict, policy: dict, today: dt.date) -> bool:
    day = dt.date.fromisoformat(episode["date"])
    return (episode.get("publication", {}).get("ready") is True
            and dt.date.fromisoformat(policy["start_date"]) <= day <= today
            and (today - day).days <= 7)


def build_manifest(root: pathlib.Path = ROOT) -> dict:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise ValueError("Release manifests are created only by GitHub Actions")
    policy = json.loads((root / "config/publishing.json").read_text(encoding="utf-8"))
    today = dt.datetime.now(dt.timezone.utc).date()
    entries = []
    seen = set()
    targets = set()
    for path in sorted((root / "data/episodes").glob("*.json")):
        episode = json.loads(path.read_text(encoding="utf-8"))
        if not eligible(episode, policy, today):
            continue
        identity = episode_key(episode)
        if path.stem != identity or identity in seen:
            raise ValueError("Episode filename must match its unique identity")
        seen.add(identity)
        target = episode.get("publication", {}).get("publish_at")
        if target:
            target = timestamp(target)
            if target in targets:
                raise ValueError("Two episodes own the same publication slot")
            targets.add(target)
        problems = schema.validate_episode(episode)
        if problems:
            raise ValueError("Invalid release episode: " + "; ".join(problems))
        for item in episode["items"]:
            if item.get("source_review", {}).get("status") != "verified":
                raise ValueError(f"Unverified source in {path.name}")
            if not schema.checks_stamped(item):
                raise ValueError(f"Evidence checks not completed in CI in {path.name}")
        paths = [path.relative_to(root).as_posix()]
        paths += [f"output/{identity}/{name}" for name in
                  ("video.mp4", "thumbnail.png", "brief.md")]
        entries.append({"id": identity, "date": episode["date"],
                        "files": {name: digest(root / name) for name in paths}})
    manifest = {"commit": os.environ["GITHUB_SHA"], "run_id": os.environ["GITHUB_RUN_ID"],
                "episodes": entries}
    (root / "release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def verify_release(root: pathlib.Path, manifest: dict, expected_run: str,
                   expected_commit: str) -> None:
    if manifest.get("run_id") != expected_run or manifest.get("commit") != expected_commit:
        raise ValueError("Release does not belong to the successful Render run")
    seen = set()
    for entry in manifest["episodes"]:
        day = dt.date.fromisoformat(entry["date"]).isoformat()
        identity = episode_key({"date": day, "episode_id": entry.get("id", day)})
        if identity in seen:
            raise ValueError("Duplicate episode in release")
        seen.add(identity)
        allowed = {f"data/episodes/{identity}.json"} | {
            f"output/{identity}/{name}" for name in ("video.mp4", "thumbnail.png", "brief.md")}
        if set(entry["files"]) != allowed:
            raise ValueError("Unexpected or missing release file")
        for name, sha in entry["files"].items():
            if digest(root / name) != sha:
                raise ValueError(f"Release file changed: {name}")
        episode = json.loads((root / f"data/episodes/{identity}.json").read_text(encoding="utf-8"))
        if episode.get("date") != day or episode_key(episode) != identity:
            raise ValueError("Release identity/date does not match its episode")


class GitHubJournal:
    """A durable reservation BEFORE insert prevents blind retries after network failures.

    GitHub contents PUT requires the previous blob SHA, so concurrent reservations conflict.
    No credentials, resumable session URLs or full API responses are stored in the journal.
    """
    def __init__(self, repository: str, token: str, date: str):
        if not re.fullmatch(r"[\w.-]+/[\w.-]+", repository):
            raise ValueError("Invalid repository")
        date = episode_key({"date": date[:10], "episode_id": date})
        self.url = f"https://api.github.com/repos/{repository}/contents/data/publications/{date}.json"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {token}",
                                     "Accept": "application/vnd.github+json"})
        self.sha = None

    def read(self):
        response = self.session.get(self.url, params={"ref": "main"}, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        self.sha = data["sha"]
        return json.loads(base64.b64decode(data["content"]))

    def write(self, receipt: dict):
        content = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
        body = {"message": f"YouTube {episode_key(receipt)}: {receipt['state']} [skip ci]",
                "branch": "main", "content": base64.b64encode(content.encode()).decode()}
        if self.sha:
            body["sha"] = self.sha
        response = self.session.put(self.url, json=body, timeout=30)
        response.raise_for_status()
        self.sha = response.json()["content"]["sha"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["manifest", "publish", "channel", "reconcile"])
    parser.add_argument("--release", type=pathlib.Path, default=ROOT)
    parser.add_argument("--run-id", default=os.environ.get("RENDER_RUN_ID", ""))
    parser.add_argument("--commit", default=os.environ.get("RENDER_COMMIT", ""))
    parser.add_argument("--date", type=dt.date.fromisoformat)
    parser.add_argument("--episode", type=lambda key: episode_key({"date": key[:10], "episode_id": key}),
                        help="Publish only this stable episode identity")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.action == "manifest":
        print(json.dumps(build_manifest(), indent=2))
        return
    import upload
    policy = json.loads((ROOT / "config/publishing.json").read_text(encoding="utf-8"))
    if args.action == "reconcile":
        # Reconcile pending receipts independently of expired render artifacts.
        errors = []
        newly_public = False
        for path in sorted((ROOT / "data/publications").glob("*.json")):
            receipt = json.loads(path.read_text(encoding="utf-8"))
            if receipt.get("state") == "published":
                continue
            journal = GitHubJournal(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"], path.stem)
            try:
                current = upload.reconcile_receipt(journal, policy)
                newly_public = newly_public or current.get("state") == "published"
                print(json.dumps({k: current.get(k) for k in
                                  ("episode_id", "date", "state", "url", "actual_privacy")}))
            except Exception as exc:
                errors.append(f"{path.stem}: {type(exc).__name__}: {exc}")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as stream:
                stream.write(f"new_publications={str(newly_public).lower()}\n")
        if errors:
            raise ValueError("; ".join(errors))
        return
    if args.action == "channel":
        channel = upload.channel_info(upload.youtube_client())
        print(json.dumps(channel, indent=2, ensure_ascii=False))
        expected = policy.get("channel_id")
        if not expected or channel["id"] != expected:
            raise ValueError("OAuth channel is not the configured AI Daily Diff destination")
        return
    manifest = json.loads((args.release / "release.json").read_text(encoding="utf-8"))
    verify_release(args.release, manifest, args.run_id, args.commit)
    if not policy.get("enabled") and not args.dry_run:
        print("Automatic publication disabled: configure and verify the dedicated channel first.")
        return
    if not re.fullmatch(r"UC[\w-]{22}", policy.get("channel_id") or ""):
        raise ValueError("A verified channel ID is required")
    for entry in manifest["episodes"]:
        identity = episode_key({"date": entry["date"], "episode_id": entry.get("id", entry["date"])})
        if args.episode and identity != args.episode:
            continue
        if args.date and entry["date"] != args.date.isoformat():
            continue
        path = args.release / f"data/episodes/{identity}.json"
        episode = json.loads(path.read_text(encoding="utf-8"))
        current = json.loads((ROOT / f"data/episodes/{identity}.json").read_text(encoding="utf-8"))
        # CI stamps the badge only in the artifact; every editorial field must still match main.
        for item in current["items"]:
            schema.stamp_checks(item, True)
        if current != episode:
            raise ValueError("Episode changed after render; wait for the new verified release")
        if not eligible(episode, policy, dt.datetime.now(dt.timezone.utc).date()):
            raise ValueError("Episode is no longer eligible for automatic publication")
        journal = None if args.dry_run else GitHubJournal(
            os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"], identity)
        upload.publish_verified(episode, args.release / "output" / identity,
                                policy, journal, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
