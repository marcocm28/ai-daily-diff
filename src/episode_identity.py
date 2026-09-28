"""Stable publication identity independent of the actual calendar date."""
import datetime as dt
import re


def episode_key(episode):
    date = episode.get("date")
    if not isinstance(date, str) or dt.date.fromisoformat(date).isoformat() != date:
        raise ValueError("episode date must be YYYY-MM-DD")
    key = episode.get("episode_id", date)
    if not isinstance(key, str) or not re.fullmatch(re.escape(date) + r"(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?", key):
        raise ValueError("episode_id must match date followed by an optional lowercase slug")
    if len(key) > 100:
        raise ValueError("episode_id must be at most 100 characters")
    return key
