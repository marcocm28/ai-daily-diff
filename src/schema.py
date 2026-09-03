"""Canonical episode schema + the two mechanical gates.

Gate 1 (accuracy): every item must carry a source_url. Enforced here — render_* scripts call
validate_episode() and refuse to render a slide/page for an item that fails it.

Gate 2 (reproducibility): every item's example must actually run and match its recorded output.
Enforced by verify_example() here, called both when authoring (to decide whether a slide can
honestly show a CI badge as "pending") and by CI in .github/workflows/test.yml (the run that
actually earns the badge before anything publishes).

Nothing else in this repo should hand-roll episode-JSON validation — import from here.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED_ITEM_FIELDS = [
    "id", "vertical", "vertical_label", "headline", "what_changed", "why_it_matters",
    "who_should_care", "the_number", "diff", "example", "source_url",
]
REQUIRED_NUMBER_FIELDS = ["value", "label"]
REQUIRED_DIFF_FIELDS = ["minus", "plus"]
REQUIRED_EXAMPLE_FIELDS = ["kind", "dir", "run_cmd", "code", "output", "run_summary", "caption"]
VALID_EXAMPLE_KINDS = {"real", "stub", "analysis"}
# Revised 2026-09-02 to be decision-shaped rather than research-shaped: see
# PROJECT_INSTRUCTIONS.md §5 and §15. Media generation stays a vertical (Marco's original
# request) but with a threshold: it appears when something is usable, priced or licensed
# differently, not when a paper describes a method.
VALID_VERTICALS = {
    "models-releases", "cost-limits", "tools-agents", "media-generation", "claims-risks",
}

MAX_WORDS_PER_SLIDE = 22
MAX_ITEMS_DAILY = 3

# daily  — the weekday news brief, up to 3 items
# method — the weekly flagship: one task, one measured method, title shaped like the search query
# deep   — the occasional long variant of the weekly slot: emerging patterns, multi-stage checks
VALID_KINDS = {"daily", "method", "deep"}


class SchemaError(Exception):
    pass


def load_episode(path: pathlib.Path | str) -> dict:
    path = pathlib.Path(path)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_episode(episode: dict, *, is_daily: bool | None = None) -> list[str]:
    """Returns a list of human-readable problems. Empty list = passes Gate 1 + shape checks.

    is_daily is derived from episode["kind"] unless a caller overrides it — passing the default
    down by hand was how a method or deep episode could get checked against the daily item cap.
    """
    problems = []

    for key in ("date", "kind", "title", "items"):
        if key not in episode:
            problems.append(f"episode missing top-level field '{key}'")

    kind = episode.get("kind")
    if kind not in VALID_KINDS:
        problems.append(f"episode kind '{kind}' not one of {sorted(VALID_KINDS)}")
    if is_daily is None:
        is_daily = kind == "daily"

    items = episode.get("items", [])
    if is_daily and len(items) > MAX_ITEMS_DAILY:
        problems.append(f"daily episode has {len(items)} items, max is {MAX_ITEMS_DAILY}")
    if not items:
        problems.append("episode has zero items")
    if kind in ("method", "deep") and len(items) != 1:
        problems.append(f"a {kind} episode covers exactly one topic, found {len(items)} items")

    for idx, item in enumerate(items):
        tag = f"item[{idx}] ({item.get('id', '?')})"
        for field in REQUIRED_ITEM_FIELDS:
            if field not in item:
                problems.append(f"{tag}: missing field '{field}'")

        # Gate 1 — no source_url, no ship.
        src = item.get("source_url", "")
        if not src or not src.startswith(("http://", "https://")):
            problems.append(f"{tag}: GATE 1 FAILED — missing or invalid source_url")

        if item.get("vertical") not in VALID_VERTICALS:
            problems.append(f"{tag}: vertical '{item.get('vertical')}' not one of {sorted(VALID_VERTICALS)}")

        num = item.get("the_number", {})
        for field in REQUIRED_NUMBER_FIELDS:
            if field not in num:
                problems.append(f"{tag}: the_number missing '{field}'")

        diff = item.get("diff", {})
        for field in REQUIRED_DIFF_FIELDS:
            if field not in diff:
                problems.append(f"{tag}: diff missing '{field}'")

        ex = item.get("example", {})
        for field in REQUIRED_EXAMPLE_FIELDS:
            if field not in ex:
                problems.append(f"{tag}: example missing '{field}'")
        if ex.get("kind") not in VALID_EXAMPLE_KINDS:
            problems.append(f"{tag}: example.kind '{ex.get('kind')}' not one of {sorted(VALID_EXAMPLE_KINDS)}")

        if item.get("org") and not str(item["org"]).replace("-", "").isalnum():
            problems.append(f"{tag}: org '{item['org']}' must be a plain slug "
                             "(it names a file in assets/logos/vendors/)")

        for field, label in (("headline", "headline"), ("what_changed", "what_changed")):
            words = len(str(item.get(field, "")).split())
            if words > MAX_WORDS_PER_SLIDE:
                problems.append(f"{tag}: {label} is {words} words, max {MAX_WORDS_PER_SLIDE}")

    return problems


def verify_example(item: dict, *, repo_root: pathlib.Path = REPO_ROOT, timeout: int = 60) -> tuple[bool, str]:
    """Actually runs examples/<item.example.dir>/run.sh and diffs stdout against
    expected_output.txt in the same folder. Returns (passed, message).

    This is Gate 2, mechanically. Called by CI (test.yml) on a clean runner — that run is what
    lets the video legitimately claim "TESTED IN CI ✓". A pass anywhere else (e.g. during
    authoring, in a Claude session) is a useful local check but is NOT what the badge certifies.
    """
    ex_dir = repo_root / item["example"]["dir"]
    run_sh = ex_dir / "run.sh"
    expected_path = ex_dir / "expected_output.txt"

    if not run_sh.exists():
        return False, f"missing {run_sh}"
    if not expected_path.exists():
        return False, f"missing {expected_path}"

    try:
        result = subprocess.run(
            ["bash", str(run_sh)], cwd=str(ex_dir), capture_output=True, text=True,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"

    if result.returncode != 0:
        return False, f"exit code {result.returncode}\nstderr:\n{result.stderr}"

    actual = result.stdout.strip()
    expected = expected_path.read_text(encoding="utf-8").strip()
    if actual != expected:
        return False, f"output mismatch\n--- expected ---\n{expected}\n--- actual ---\n{actual}"

    return True, "ok"


def main():
    """CLI: python src/schema.py data/episodes/2026-08-28.json [--verify-examples]"""
    if len(sys.argv) < 2:
        print("usage: python src/schema.py <episode.json> [--verify-examples]")
        sys.exit(2)

    path = pathlib.Path(sys.argv[1])
    episode = load_episode(path)
    problems = validate_episode(episode)

    if problems:
        print(f"FAILED — {len(problems)} problem(s) in {path}:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    print(f"Schema + Gate 1 OK — {path} ({len(episode['items'])} item(s))")

    if "--verify-examples" in sys.argv:
        all_ok = True
        for item in episode["items"]:
            ok, msg = verify_example(item)
            status = "PASS" if ok else "FAIL"
            print(f"  [{status}] {item['id']}: {msg if not ok else 'example output matches'}")
            all_ok = all_ok and ok
        if not all_ok:
            print("GATE 2 FAILED — at least one example did not reproduce its recorded output.")
            sys.exit(1)
        print("Gate 2 OK — every example reproduced its recorded output.")


if __name__ == "__main__":
    main()
