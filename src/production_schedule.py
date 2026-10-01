"""Publication targets in Rome time, separate from research/authoring start times."""
from __future__ import annotations

import datetime as dt
import json
import pathlib
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent


def settings():
    return json.loads((ROOT / "config/production-schedule.json").read_text(encoding="utf-8"))


def timestamp(value: str) -> dt.datetime:
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Publication time must include a timezone")
    return result.astimezone(dt.timezone.utc)


def slots(day: dt.date, config=None):
    config = config or settings()
    if day.weekday() not in config["weekdays"]:
        return []
    zone = ZoneInfo(config["timezone"])
    return [dt.datetime.combine(day, dt.time.fromisoformat(t), zone)
            for t in config["publication_times"]]


def validate_target(episode, value):
    target = timestamp(value)
    if target not in slots(dt.date.fromisoformat(episode["date"])):
        raise ValueError("publish_at must be an approved slot on the actual episode date")
    return target


def plan(now, episodes, receipts, missing, config=None):
    """No quota: return at most one unoccupied slot in its preparation window."""
    config = config or settings()
    today = now.astimezone(ZoneInfo(config["timezone"])).date()
    result = {"date": str(today), "missing_inputs": missing, "slots": [], "next_target": None}
    for target in slots(today, config):
        assigned = [e for e in episodes if e.get("publication", {}).get("publish_at")
                    and timestamp(e["publication"]["publish_at"]) == target]
        state = "waiting"
        identity = None
        if len(assigned) > 1:
            state = "conflict"
        elif assigned:
            e = assigned[0]
            identity = e.get("episode_id", e["date"])
            r = receipts.get(identity, {})
            state = r.get("state", "queued" if e.get("publication", {}).get("ready") else "draft")
            if state == "published" and (r.get("actual_privacy") != "public"
                                          or r.get("upload_status") != "processed"):
                state = "unconfirmed"
        elif now >= target:
            state = "missed"
        elif now >= target - dt.timedelta(minutes=config["prepare_minutes"]):
            state = "inputs_pending" if missing else "ready_to_author"
            if not missing and result["next_target"] is None:
                result["next_target"] = target.isoformat()
        risk = (now >= target - dt.timedelta(minutes=config["warning_minutes"])
                and state not in {"published", "scheduled"})
        result["slots"].append({"target": target.isoformat(), "state": state,
                                "episode_id": identity, "at_risk": risk})
    return result
