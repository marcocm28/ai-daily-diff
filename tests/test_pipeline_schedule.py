import datetime as dt
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from production_schedule import plan, slots, timestamp, validate_target
from pipeline_watch import recovery_actions


def test_rome_slots_follow_dst_and_skip_sunday():
    assert slots(dt.date(2026, 9, 30))[0].utcoffset() == dt.timedelta(hours=2)
    assert slots(dt.date(2026, 11, 2))[0].utcoffset() == dt.timedelta(hours=1)
    assert slots(dt.date(2026, 10, 4)) == []


def test_prepare_two_hours_early_and_warn_before_target():
    early = plan(timestamp("2026-09-30T07:30:00+02:00"), [], {}, [])
    assert early["next_target"] == "2026-09-30T09:30:00+02:00"
    assert not early["slots"][0]["at_risk"]
    blocked = plan(timestamp("2026-09-30T08:50:00+02:00"), [], {}, ["github-inbox"])
    assert blocked["next_target"] is None
    assert blocked["slots"][0]["at_risk"]
    assert blocked["slots"][0]["state"] == "inputs_pending"


def test_assigned_slot_and_missed_slot_never_create_another_episode():
    episode = {"date": "2026-09-30", "episode_id": "2026-09-30-model",
               "publication": {"ready": True, "publish_at": "2026-09-30T07:30:00Z"}}
    result = plan(timestamp("2026-09-30T08:00:00+02:00"), [episode], {}, [])
    assert result["next_target"] is None
    assert result["slots"][0]["state"] == "queued"
    result = plan(timestamp("2026-09-30T11:30:00+02:00"), [], {}, [])
    assert result["slots"][0]["state"] == "missed"
    assert result["next_target"] == "2026-09-30T13:30:00+02:00"


@pytest.mark.parametrize("value", ["2026-09-30T09:30:00", "2026-10-01T09:30:00+02:00",
                                    "2026-09-30T10:30:00+02:00"])
def test_rejects_ambiguous_dates_and_unapproved_slots(value):
    with pytest.raises(ValueError):
        validate_target({"date": "2026-09-30"}, value)


def run(**extra):
    return {"id": 123, "status": "completed", "conclusion": "success", "run_attempt": 1,
            "created_at": "2026-09-29T05:00:00Z", "updated_at": "2026-09-29T05:10:00Z", **extra}


def test_missing_ingest_recovers_but_never_duplicates_an_active_job():
    now = timestamp("2026-09-30T07:00:00Z")
    assert recovery_actions(now, True, {"ingest.yml": [run()]}) == [
        {"workflow": "ingest.yml", "action": "dispatch"}]
    assert recovery_actions(now, True, {"ingest.yml": [run(status="queued")]}) == []
    assert recovery_actions(now, False, {}) == []


def test_retry_is_bounded_and_cooldown_prevents_dispatch_loop():
    now = timestamp("2026-09-30T07:00:00Z")
    failed = run(conclusion="failure", created_at="2026-09-30T05:00:00Z", updated_at="2026-09-30T05:10:00Z")
    assert recovery_actions(now, False, {"upload.yml": [failed]})[0]["action"] == "rerun"
    assert recovery_actions(now, False, {"upload.yml": [{**failed, "run_attempt": 2}]}) == []
    assert recovery_actions(now, False, {"upload.yml": [{**failed, "updated_at": "2026-09-30T06:55:00Z"}]}) == []


def test_scheduled_receipts_are_polled_without_dispatching_an_upload():
    actions = recovery_actions(timestamp("2026-09-30T07:00:00Z"), False, {}, True)
    assert actions == [{"workflow": "reconcile.yml", "action": "dispatch"}]


def test_slot_duplicate_is_visible_and_cannot_be_authored_again():
    episode = {"date": "2026-09-30", "publication": {"publish_at": "2026-09-30T09:30:00+02:00"}}
    result = plan(timestamp("2026-09-30T08:30:00+02:00"), [episode, episode], {}, [])
    assert result["slots"][0]["state"] == "conflict"
    assert result["next_target"] is None


def test_missing_downstream_triggers_recover_only_from_successful_recent_render():
    now = timestamp("2026-09-30T08:00:00Z")
    rendered = run(created_at="2026-09-30T06:00:00Z", updated_at="2026-09-30T07:00:00Z")
    actions = recovery_actions(now, False, {"render.yml": [rendered]})
    assert [a["workflow"] for a in actions] == ["upload.yml", "pages.yml"]
    assert actions[0]["inputs"] == {"render_run_id": "123", "dry_run": "false"}
    assert recovery_actions(now, False, {"render.yml": [{**rendered, "conclusion": "failure", "run_attempt": 2}]}) == []


def test_missing_render_trigger_is_recovered_once_run_appears():
    now = timestamp("2026-09-30T08:00:00Z")
    assert recovery_actions(now, False, {}, queued_at="2026-09-30T07:00:00Z") == [
        {"workflow": "render.yml", "action": "dispatch"}]
    assert recovery_actions(now, False, {"render.yml": [run(status="in_progress")]},
                            queued_at="2026-09-30T07:00:00Z") == []


def test_old_exhausted_failure_does_not_block_new_work():
    now = timestamp("2026-09-30T08:00:00Z")
    failed = run(conclusion="failure", run_attempt=2)
    rendered = run(created_at="2026-09-30T06:00:00Z", updated_at="2026-09-30T07:00:00Z")
    actions = recovery_actions(now, True, {"ingest.yml": [failed],
        "render.yml": [rendered], "upload.yml": [failed], "pages.yml": [failed]})
    assert [a["workflow"] for a in actions] == ["ingest.yml", "upload.yml", "pages.yml"]
    assert all(a["action"] == "dispatch" for a in actions)


def test_independent_research_is_ready_without_inbox_or_personal_tasks():
    from pipeline_watch import inspect
    class API:
        def file(self, path):
            assert path == "data/inbox/2026-09-30.json"
            return None
        def documents(self, path):
            assert path in {"data/episodes", "data/publications"}
            return {}
        def runs(self, workflow):
            return []
    result = inspect(API(), timestamp("2026-09-30T07:30:00+02:00"))
    assert result["missing_inputs"] == ["github-inbox"]
    assert result["next_target"] == "2026-09-30T09:30:00+02:00"
