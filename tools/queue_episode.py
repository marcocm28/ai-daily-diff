"""Mark a completed episode for the automatic GitHub pipeline after local checks."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import schema
from episode_identity import episode_key


def queue(path: pathlib.Path) -> None:
    episode = schema.load_episode(path)
    if path.stem != episode_key(episode):
        raise ValueError("Episode filename does not match its publication identity")
    problems = schema.validate_episode(episode)
    for item in episode.get("items", []):
        if item.get("source_review", {}).get("status") != "verified":
            problems.append(f"{item['id']}: primary source review missing")
    if problems:
        raise ValueError("; ".join(problems))
    for item in episode["items"]:
        ok, message = schema.verify_example(item)
        if not ok:
            raise ValueError(f"{item['id']}: {message}")
        schema.stamp_checks(item, False)
    episode["publication"] = {"ready": True, "queued_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Queued {episode_key(episode)}. GitHub must reverify and render before publication.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("episode", help="YYYY-MM-DD or YYYY-MM-DD-topic episode identity")
    args = parser.parse_args()
    key = episode_key({"date": args.episode[:10], "episode_id": args.episode})
    queue(ROOT / "data/episodes" / f"{key}.json")
