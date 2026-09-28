"""One editorially approved playlist and its matching production prompt."""
import pathlib
import json
from episode_identity import episode_key

ROOT = pathlib.Path(__file__).resolve().parent.parent
AUDIENCES = {"everyday", "professional", "builder"}
PROFILES = {
    "everyday": ({"everyday"}, {"daily", "method"}),
    "professional": ({"professional"}, {"daily", "method"}),
    "builder": ({"builder"}, {"daily", "method", "deep"}),
    "models": (AUDIENCES, {"daily", "method", "deep"}),
    "repositories": ({"builder"}, {"daily", "method", "deep"}),
    "architectures": ({"builder"}, {"daily", "deep"}),
    "agents": ({"professional", "builder"}, {"daily", "method", "deep"}),
    "guides": (AUDIENCES, {"method"}),
}


def profile_files(playlist, audience, kind):
    if playlist not in PROFILES or audience not in PROFILES[playlist][0] or kind not in PROFILES[playlist][1]:
        raise ValueError("Playlist, audience and format do not match an editorial profile")
    files = ["prompts/editorial.md", "prompts/research.md", "prompts/playlist.md", f"prompts/{kind}.md"]
    if audience != playlist:
        files.append(f"prompts/playlists/{audience}.md")
    return files + [f"prompts/playlists/{playlist}.md", "prompts/example.md", "prompts/title.md"]


def production_brief(date, playlist, audience, kind, selection=None):
    """Compose existing prompts with the channel's actual playlist promise and context."""
    files = profile_files(playlist, audience, kind)
    config = json.loads((ROOT / "config/channel.json").read_text(encoding="utf-8"))
    entry = next(p for p in config["playlists"] if p["key"] == playlist)
    parts = [f"Production: {date}; playlist={playlist}; audience={audience}; format={kind}",
             f"Playlist: {entry['title']}\nPromise: {entry['description']}",
             "Use the audience profile for prerequisites, vocabulary, examples and search intent; "
             "use the topic profile for subject scope. Every story must meet both. "
             "This brief is an authoring input, not approval of the finished script."]
    context = (selection or {}).get("editorial_review")
    if context:
        parts.append("Selection editorial context (research input; verify before use):\n" +
                     json.dumps(context, indent=2, ensure_ascii=False))
    else:
        parts.append("Before writing, complete the viewer question, assumed knowledge, task, "
                     "supported payoff and evidence mode in selection editorial_review.")
    for name in files:
        parts.append(f"## {name}\n\n" + (ROOT / name).read_text(encoding="utf-8"))
    return "\n\n".join(parts) + "\n"


def contract_problems(route, kind):
    if not isinstance(route, dict):
        return ["playlist route must be an object"]
    errors = []
    primary = route.get("primary_playlist")
    if not isinstance(primary, str) or primary not in PROFILES:
        return ["primary_playlist requires one supported playlist"]
    if route.get("prompt_profile") != primary:
        errors.append("prompt_profile must match primary_playlist")
    try:
        profile_files(primary, route.get("primary_audience"), kind)
    except (ValueError, TypeError):
        errors.append("playlist profile does not support the primary audience or format")
    review = route.get("playlist_review")
    if not isinstance(review, dict) or review.get("status") != "approved":
        errors.append("playlist_review must be approved before production")
    elif any(not isinstance(review.get(key), str) or not review[key].strip() for key in ("reviewer", "reason")):
        errors.append("playlist_review requires reviewer and whole-video fit reason")
    return errors


def episode_problems(episode):
    date = episode.get("date", "")
    if not isinstance(date, str) or (date < "2026-09-29" and "episode_id" not in episode):
        return []
    errors = contract_problems(episode, episode.get("kind"))
    primary = episode.get("primary_playlist")
    if isinstance(primary, str) and primary in {"models", "repositories", "architectures", "agents", "guides"} and episode.get("topics") != [primary]:
        errors.append("a topic playlist requires the whole episode to focus on that one topic")
    if episode.get("audiences") != [episode.get("primary_audience")]:
        errors.append("audiences must identify the single specialization used to produce this episode")
    if not errors and episode.get("production_prompts") != profile_files(primary, episode["primary_audience"], episode["kind"]):
        errors.append("production_prompts must record the exact prompts for the approved profile")
    return errors


def approved_primary(episode, config):
    # Published episode hashes are immutable; retrospective decisions live separately.
    key = episode_key(episode)
    route = config.get("archive_routes", {}).get(key, episode)
    # A published mixed video can be explicitly excluded from specialized paths.
    # This exception is retrospective only; new episode validation never accepts it.
    if key in config.get("archive_routes", {}) and isinstance(route, dict) and route.get("primary_playlist") is None:
        review = route.get("playlist_review", {})
        if isinstance(review, dict) and review.get("status") == "approved" and review.get("disposition") == "unassigned" and all(
            isinstance(review.get(key), str) and review[key].strip() for key in ("reviewer", "reason")) and route.get("prompt_profile") is None:
            return None
    errors = contract_problems(route, episode.get("kind"))
    if errors:
        raise ValueError("Missing or invalid approved playlist route: " + "; ".join(errors))
    return route["primary_playlist"]
