"""Stamps the "TESTED IN CI" badge on an episode — the last step of Gate 2, and the only place
that flag is ever set to true. Called from .github/workflows/render.yml, on a clean GitHub-hosted
runner, after Gate 2 has already passed there. Never call this from a Claude/Codex session or a
developer machine and expect the badge to mean anything: it certifies "this ran green on the CI
runner just now", not "this ran green somewhere once" (see PROJECT_INSTRUCTIONS.md §9.1, §15).

Usage:
  python tools/mark_ci_verified.py data/episodes/2026-09-02.json

Refuses to write anything if Gate 1 or Gate 2 fails — a badge that wasn't earned must not exist
as a file (PROJECT_INSTRUCTIONS.md §15, 01/09).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from schema import load_episode, validate_episode, verify_example  # noqa: E402


def main() -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        sys.exit("CI badge can only be stamped inside GitHub Actions")
    if len(sys.argv) != 2:
        print("usage: python tools/mark_ci_verified.py <episode.json>", file=sys.stderr)
        sys.exit(2)

    path = pathlib.Path(sys.argv[1])
    episode = load_episode(path)

    problems = validate_episode(episode)
    if problems:
        print(f"GATE 1 FAILED — {len(problems)} problem(s), refusing to stamp the badge:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    all_ok = True
    for item in episode["items"]:
        ok, msg = verify_example(item)
        print(f"  [{'PASS' if ok else 'FAIL'}] {item['id']}: {msg if not ok else 'example output matches'}")
        all_ok = all_ok and ok

    if not all_ok:
        print("GATE 2 FAILED — refusing to stamp the badge.", file=sys.stderr)
        sys.exit(1)

    for item in episode["items"]:
        item["example"]["tested_in_ci"] = True

    path.write_text(json.dumps(episode, indent=2), encoding="utf-8")
    print(f"Gate 2 OK on this runner — stamped tested_in_ci=true for {len(episode['items'])} item(s) -> {path}")


if __name__ == "__main__":
    main()
