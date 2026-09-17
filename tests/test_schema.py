"""Minimal smoke tests. Run with: pytest tests/ (or: python -m pytest tests/)"""
import pathlib
import sys
import copy
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import schema  # noqa: E402


@pytest.mark.parametrize("path", sorted((ROOT / "data" / "episodes").glob("*.json")))
def test_every_episode_passes_schema_and_gate1(path):
    episode = schema.load_episode(path)
    problems = schema.validate_episode(episode)
    assert problems == [], problems


@pytest.mark.parametrize("path", sorted((ROOT / "data" / "episodes").glob("*.json")))
def test_shipped_episode_passes_gate2(path):
    episode = schema.load_episode(path)
    for item in episode["items"]:
        ok, msg = schema.verify_example(item, repo_root=ROOT)
        assert ok, f"{item['id']}: {msg}"


def test_no_src_module_shadows_the_standard_library():
    """Regression guard for a real CI failure (2026-09-01).

    src/ was named select.py for the SELECT stage. Because running `python src/schema.py` puts
    src/ first on sys.path, `import select` inside the stdlib's own selectors/subprocess chain
    resolved to our file instead — breaking subprocess with a cryptic
    "module 'select' has no attribute 'select'". It did not reproduce on machines where select
    is compiled into the interpreter, only where it is a dynamically loaded extension. Any
    src/*.py sharing a name with a stdlib module is the same trap waiting to happen.
    """
    stdlib = getattr(sys, "stdlib_module_names", None)
    if stdlib is None:  # Python < 3.10
        return
    collisions = sorted(
        p.stem for p in (ROOT / "src").glob("*.py") if p.stem in stdlib
    )
    assert collisions == [], (
        f"src/ module name(s) shadow the standard library: {collisions}. Rename them."
    )


def test_validate_episode_catches_missing_source_url():
    bad = {
        "date": "2099-01-01", "kind": "daily", "title": "t",
        "items": [{
            "id": "x", "vertical": "architectures-models", "vertical_label": "X",
            "headline": "h", "what_changed": "w", "why_it_matters": "w",
            "who_should_care": "w", "the_number": {"value": "1", "label": "l"},
            "diff": {"minus": "a", "plus": "b"},
            "example": {"kind": "real", "dir": "d", "run_cmd": "c", "code": "c",
                        "output": "o", "run_summary": "s", "caption": "c"},
            "source_url": "",
        }],
    }
    problems = schema.validate_episode(bad)
    assert any("GATE 1" in p for p in problems)


def test_displayed_output_cannot_drift_from_executed_example():
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-02.json")
    item = copy.deepcopy(ep["items"][0])
    item["example"]["output"] = "a fabricated result"
    ok, message = schema.verify_example(item)
    assert not ok and "displayed" in message


def test_todo_cannot_ship():
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-02.json")
    ep["title"] = "TODO — unfinished headline"
    assert any("TODO" in p for p in schema.validate_episode(ep))


def test_radar_requires_a_primary_source_review():
    ep = schema.load_episode(ROOT / "data/episodes/2026-09-02.json")
    item = ep["items"][0]
    item["_origin"] = {"source": "chatgpt-task:productivity"}
    assert any("source_review" in p for p in schema.validate_episode(ep))
    item["source_review"] = {"status": "verified", "checked_at": "2026-09-16",
                             "excerpt": "Source text", "decision": "Evaluate this approach",
                             "availability": "Preview"}
    assert schema.validate_episode(ep) == []


def test_example_path_must_stay_in_examples():
    ok, message = schema.verify_example({"example": {"dir": "../elsewhere"}})
    assert not ok and "inside examples" in message


@pytest.mark.parametrize("episode", [[], {"items": None}, {"items": [None]},
                                     {"items": [{"example": 4, "the_number": 2, "diff": []}]}])
def test_malformed_json_is_reported_instead_of_crashing(episode):
    assert schema.validate_episode(episode)
