"""Idempotent description/playlist management on the verified dedicated channel."""
import argparse
import copy
import json
import pathlib
import time

from googleapiclient.errors import HttpError

import upload
import strategy
import content_routing

ROOT = pathlib.Path(__file__).resolve().parent.parent


def all_items(request, **params):
    items, page = [], None
    while True:
        for attempt in range(5):
            try:
                response = request(**params, **({"pageToken": page} if page else {})).execute()
                break
            except HttpError as exc:
                # A just-created playlist can take a few seconds to become readable.
                # Retry reads only; never repeat an insert after an ambiguous response.
                if exc.resp.status != 404 or "playlistId" not in params or attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        items.extend(response.get("items", []))
        page = response.get("nextPageToken")
        if not page:
            return items


def synchronize(youtube, config, episodes, receipts, *, apply=False):
    channels = youtube.channels().list(part="snippet,brandingSettings", mine=True).execute()["items"]
    if len(channels) != 1 or channels[0]["id"] != config["channel_id"]:
        raise ValueError("Wrong channel; no channel or playlist changes allowed")
    channel = channels[0]
    branding = copy.deepcopy(channel.get("brandingSettings", {}))
    branding.setdefault("channel", {}).update(description=config["description"], keywords=config["keywords"], defaultLanguage="en")
    playlists = all_items(youtube.playlists().list, part="snippet,status", mine=True, maxResults=50)
    by_title = {}
    for playlist in playlists:
        title = playlist["snippet"]["title"]
        if title in by_title and title in {p["title"] for p in config["playlists"]}:
            raise ValueError("Duplicate managed playlist titles; reconcile before changing anything")
        by_title[title] = playlist
    placements = []
    managed_videos = set()
    for date, receipt in receipts.items():
        if receipt.get("channel_id") != config["channel_id"] or receipt.get("actual_privacy") != "public" or not receipt.get("video_id"):
            continue
        episode = episodes.get(date, {})
        managed_videos.add(receipt["video_id"])
        primary = content_routing.approved_primary(episode, config)
        for key in ([primary] if primary else []):
            if key not in {p["key"] for p in config["playlists"]}:
                raise ValueError("Unknown playlist placement")
            placements.append((key, receipt["video_id"]))
    # Verify every video before the first mutation, including manually edited receipts.
    for video in sorted(managed_videos):
        items = youtube.videos().list(part="snippet,status", id=video).execute()["items"]
        if len(items) != 1 or items[0]["snippet"]["channelId"] != config["channel_id"] or items[0]["status"]["privacyStatus"] != "public":
            raise ValueError("Playlist video is not public on the configured channel")
    # Read all existing managed playlists before any mutation. Unknown/manual members
    # are preserved; only videos owned by verified publication receipts are reconciled.
    inventory = {}
    for plan in config["playlists"]:
        playlist = by_title.get(plan["title"])
        if playlist:
            if playlist["snippet"].get("channelId", channel["id"]) != channel["id"]:
                raise ValueError("Playlist ownership mismatch")
            members = all_items(youtube.playlistItems().list, part="contentDetails", playlistId=playlist["id"], maxResults=50)
            if any(not member.get("id") for member in members if member["contentDetails"]["videoId"] in managed_videos):
                raise ValueError("Managed membership has no association ID")
            inventory[playlist["id"]] = members
    if apply and branding != channel.get("brandingSettings"):
        youtube.channels().update(part="brandingSettings", body={"id": channel["id"], "brandingSettings": branding}).execute()
    state = {"channel_id": channel["id"], "applied": apply, "playlists": {}}
    for plan in config["playlists"]:
        playlist = by_title.get(plan["title"])
        if not playlist:
            if not apply:
                state["playlists"][plan["key"]] = {"title": plan["title"], "action": "create"}
                continue
            playlist = youtube.playlists().insert(part="snippet,status", body={
                "snippet": {"title": plan["title"], "description": plan["description"], "defaultLanguage": "en"},
                "status": {"privacyStatus": "public"}}).execute()
        if playlist.get("snippet", {}).get("channelId", channel["id"]) != channel["id"]:
            raise ValueError("Playlist ownership mismatch")
        snippet = playlist["snippet"]
        if apply and (snippet.get("description") != plan["description"] or playlist["status"]["privacyStatus"] != "public"):
            youtube.playlists().update(part="snippet,status", body={"id": playlist["id"],
                "snippet": {"title": plan["title"], "description": plan["description"], "defaultLanguage": "en"},
                "status": {"privacyStatus": "public"}}).execute()
        ident = playlist["id"]
        state["playlists"][plan["key"]] = {"id": ident, "title": plan["title"], "url": f"https://www.youtube.com/playlist?list={ident}"}
        members = inventory.get(ident, [])
        wanted = {video for key, video in placements if key == plan["key"]}
        existing = set()
        for member in members:
            video = member["contentDetails"]["videoId"]
            if video in managed_videos and (video not in wanted or video in existing):
                if apply:
                    youtube.playlistItems().delete(id=member["id"]).execute()
                continue
            existing.add(video)
        state["playlists"][plan["key"]]["managed_video_ids"] = sorted(wanted)
        if not apply:
            state["playlists"][plan["key"]]["remove_associations"] = [m["id"] for m in members
                if m["contentDetails"]["videoId"] in managed_videos and m["contentDetails"]["videoId"] not in wanted]
        for key, video in placements:
            if key == plan["key"] and video not in existing:
                if apply:
                    youtube.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": ident, "position": 0,
                        "resourceId": {"kind": "youtube#video", "videoId": video}}}).execute()
                existing.add(video)
    if apply:
        actual = youtube.channels().list(part="brandingSettings", mine=True).execute()["items"]
        if actual[0]["brandingSettings"]["channel"].get("description") != config["description"]:
            raise ValueError("Description update could not be verified")
        for plan in config["playlists"]:
            ident = state["playlists"][plan["key"]]["id"]
            actual = youtube.playlists().list(part="snippet,status", id=ident).execute()["items"]
            if len(actual) != 1 or actual[0]["snippet"]["title"] != plan["title"] or actual[0]["snippet"].get("description") != plan["description"] or actual[0]["status"]["privacyStatus"] != "public":
                raise ValueError("Playlist metadata verification failed")
            members = all_items(youtube.playlistItems().list, part="contentDetails", playlistId=ident, maxResults=50)
            actual_ids = {x["contentDetails"]["videoId"] for x in members}
            wanted = {video for key, video in placements if key == plan["key"]}
            managed_members = [m["contentDetails"]["videoId"] for m in members if m["contentDetails"]["videoId"] in managed_videos]
            if actual_ids & managed_videos != wanted or len(managed_members) != len(wanted):
                raise ValueError("Playlist membership verification failed")
    return state


def synchronize_description_links(youtube, config, episodes, receipts, state, *, apply=False):
    """Correct only the navigation footer; preserve the published script and metadata."""
    planned = []
    for date, receipt in receipts.items():
        if receipt.get("channel_id") != config["channel_id"] or receipt.get("actual_privacy") != "public" or not receipt.get("video_id"):
            continue
        key = content_routing.approved_primary(episodes.get(date, {}), config)
        video_id = receipt["video_id"]
        videos = youtube.videos().list(part="snippet,status", id=video_id).execute().get("items", [])
        if len(videos) != 1 or videos[0]["snippet"]["channelId"] != config["channel_id"] or videos[0]["status"]["privacyStatus"] != "public":
            raise ValueError("Wrong video destination for description routing")
        snippet = videos[0]["snippet"]
        base = snippet.get("description", "").rsplit("\nExplore this topic:\n", 1)[0].rstrip()
        if key:
            playlist = state["playlists"][key]
            description = base + f"\n\nExplore this topic:\n{playlist['title']}: {playlist['url']}"
        else:
            description = base
        if len(description) > 5000:
            raise ValueError("Approved navigation exceeds description limit; do not truncate sources")
        if not snippet.get("title") or not snippet.get("categoryId"):
            raise ValueError("Required video metadata missing; cannot safely update description")
        writable = {key: copy.deepcopy(value) for key, value in snippet.items() if key in {
            "title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage"}}
        writable["description"] = description
        planned.append((video_id, writable, description != snippet.get("description", "")))
    if apply:
        for video_id, snippet, changed in planned:
            if changed:
                youtube.videos().update(part="snippet", body={"id": video_id, "snippet": snippet}).execute()
                for attempt in range(5):
                    actual = youtube.videos().list(part="snippet", id=video_id).execute()["items"]
                    if len(actual) == 1 and actual[0]["snippet"].get("description") == snippet["description"]:
                        break
                    if attempt == 4:
                        raise ValueError("Description playlist link verification failed")
                    time.sleep(2 ** attempt)
    return [{"video_id": video, "description_changed": changed} for video, _, changed in planned]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    config = json.loads((ROOT / "config/channel.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "config/publishing.json").read_text(encoding="utf-8"))
    if config["channel_id"] != policy["channel_id"]:
        raise ValueError("Channel configuration does not match publication destination")
    episodes = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "data/episodes").glob("*.json")}
    receipts = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "data/publications").glob("*.json")}
    youtube = upload.youtube_client(management=args.apply)
    state = synchronize(youtube, config, episodes, receipts, apply=args.apply)
    if args.apply:
        synchronize_description_links(youtube, config, episodes, receipts, state, apply=True)
        strategy.reconcile_queues(ROOT / "data/production", episodes, receipts, config["channel_id"])
    target = ROOT / ("data/channel_state.json" if args.apply else ".local/channel-plan.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
