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


def queue(path: pathlib.Path) -> None:
    episode = schema.load_episode(path)
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
        item["example"]["tested_in_ci"] = False
    episode["publication"] = {"ready": True, "queued_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    path.write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Queued {episode['date']}. GitHub must reverify and render before publication.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date", type=dt.date.fromisoformat)
    args = parser.parse_args()
    queue(ROOT / "data/episodes" / f"{args.date}.json")
