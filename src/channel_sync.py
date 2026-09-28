"""Idempotent description/playlist management on the verified dedicated channel."""
import argparse
import copy
import json
import pathlib
import time

from googleapiclient.errors import HttpError

import upload
import strategy

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
    for date, receipt in receipts.items():
        if receipt.get("channel_id") != config["channel_id"] or receipt.get("actual_privacy") != "public" or not receipt.get("video_id"):
            continue
        episode = episodes.get(date, {})
        keys = config.get("archive_placements", {}).get(date, episode.get("topics", []) + episode.get("audiences", []))
        if not keys:
            continue
        for key in dict.fromkeys(keys):
            if key not in {p["key"] for p in config["playlists"]}:
                raise ValueError("Unknown playlist placement")
            placements.append((key, receipt["video_id"]))
    # Verify every video before the first mutation, including manually edited receipts.
    for video in dict.fromkeys(video for _, video in placements):
        items = youtube.videos().list(part="snippet,status", id=video).execute()["items"]
        if len(items) != 1 or items[0]["snippet"]["channelId"] != config["channel_id"] or items[0]["status"]["privacyStatus"] != "public":
            raise ValueError("Playlist video is not public on the configured channel")
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
        members = all_items(youtube.playlistItems().list, part="contentDetails", playlistId=ident, maxResults=50)
        existing = {x["contentDetails"]["videoId"] for x in members}
        for key, video in placements:
            if key == plan["key"] and video not in existing:
                if apply:
                    youtube.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": ident,
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
            if any(video not in actual_ids for key, video in placements if key == plan["key"]):
                raise ValueError("Playlist membership verification failed")
    return state


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
    state = synchronize(upload.youtube_client(management=args.apply), config, episodes, receipts, apply=args.apply)
    if args.apply:
        strategy.reconcile_queues(ROOT / "data/production", episodes, receipts, config["channel_id"])
    target = ROOT / ("data/channel_state.json" if args.apply else ".local/channel-plan.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
