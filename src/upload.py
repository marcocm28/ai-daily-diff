"""YouTube client for verified GitHub releases.
publication.py owns artifact validation and the persistent publication journal.
This module verifies OAuth identity, reconciles existing uploads and records the
actual YouTube status. Direct CLI use supports dry-run only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import brand  # noqa: E402
import schema  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output"

PAGES_BASE_URL = "https://marcocm28.github.io/ai-daily-diff"
REPO_URL = "https://github.com/marcocm28/ai-daily-diff"

# Category 28 = "Science & Technology". https://developers.google.com/youtube/v3/docs/videoCategories
CATEGORY_ID = "28"


def build_description(episode: dict, output_dir: pathlib.Path | None = None) -> str:
    date = episode["date"]
    brief_path = (output_dir or OUTPUT / date) / "brief.md"
    body = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""

    intro = episode.get("youtube_description")
    if intro is not None:
        if not isinstance(intro, str) or not intro.strip() or len(intro) > 2500:
            raise ValueError("youtube_description must be non-empty text, at most 2500 characters")
        body = intro.strip()
    else:
        # Backward compatibility for the existing archive.
        body = body or episode["title"]

    footer = [
        f"AI Daily Diff episode: {date}",
        f"Episode page (all downloads): {PAGES_BASE_URL}/{date}/",
        f"Slides (PDF): {PAGES_BASE_URL}/{date}/slides.pdf",
        f"Cheat sheet (PDF, CC BY 4.0): {PAGES_BASE_URL}/{date}/cheatsheet.pdf",
        f"All code: {REPO_URL}/tree/main/examples",
        "",
        brand.MUSIC_CREDIT,
        "",
        "AI Daily Diff — verified developments in leading AI models. Every claim sourced, every example tested "
        "in CI before this video is published.",
    ]
    sources = list(dict.fromkeys(item["source_url"] for item in episode["items"]))
    footer = ["Primary sources:", *sources, "", *footer]
    # YouTube's API rejects title/description containing a literal < or > (reason:
    # invalidDescription, confirmed via googleapis/google-api-go-client#59) — both can show up
    # legitimately in brief text (e.g. "< 1 s", code output, comparisons). Spell them out instead
    # of stripping, so the sentence still reads correctly.
    def safe(text: str) -> str:
        return text.replace("<", "less than ").replace(">", "more than ")

    # Reserve space for identity, sources and credits; never truncate them behind a long brief.
    tail = safe("\n".join(footer))
    budget = 4900 - len(tail) - 2
    if budget < 1:
        raise ValueError("Description sources and credits exceed the available space")
    return safe(body)[:budget].rstrip() + "\n\n" + tail


def get_credentials():
    from google.oauth2.credentials import Credentials

    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")
    missing = [n for n, v in (("YT_CLIENT_ID", client_id), ("YT_CLIENT_SECRET", client_secret),
                               ("YT_REFRESH_TOKEN", refresh_token)) if not v]
    if missing:
        print(f"Missing environment variable(s): {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly"],
    )


def youtube_client():
    from googleapiclient.discovery import build
    return build("youtube", "v3", credentials=get_credentials())


def channel_info(youtube) -> dict:
    channels = youtube.channels().list(part="snippet,contentDetails", mine=True).execute()["items"]
    if len(channels) != 1:
        raise ValueError("OAuth must resolve to exactly one YouTube channel")
    channel = channels[0]
    return {"id": channel["id"], "title": channel["snippet"]["title"],
            "url": f"https://www.youtube.com/channel/{channel['id']}",
            "uploads": channel["contentDetails"]["relatedPlaylists"]["uploads"]}


def find_existing(youtube, channel: dict, date: str) -> str | None:
    token = None
    matches = set()
    while True:
        page = youtube.playlistItems().list(part="snippet", playlistId=channel["uploads"],
                                             maxResults=50, pageToken=token).execute()
        for item in page.get("items", []):
            text = item["snippet"].get("description", "")
            if (f"AI Daily Diff episode: {date}" in text.splitlines()
                    or f"Episode page (all downloads): {PAGES_BASE_URL}/{date}/" in text.splitlines()):
                matches.add(item["snippet"]["resourceId"]["videoId"])
        token = page.get("nextPageToken")
        if not token:
            break
    if len(matches) > 1:
        raise ValueError("Multiple videos already exist for this episode; reconcile manually")
    return next(iter(matches), None)


def publish_verified(episode: dict, output_dir: pathlib.Path, policy: dict, journal,
                     *, dry_run: bool = False, youtube=None) -> str | None:
    """Called only after publication.verify_release; never blindly retry an insert."""
    problems = schema.validate_episode(episode)
    if problems:
        raise ValueError("Invalid episode: " + "; ".join(problems))
    privacy = policy["privacy"]
    if privacy not in {"public", "unlisted", "private"}:
        raise ValueError("Invalid privacy")
    video_path = output_dir / "video.mp4"
    thumb_path = output_dir / "thumbnail.png"
    if not video_path.is_file() or not thumb_path.is_file():
        raise ValueError("Missing verified video or thumbnail")
    description = build_description(episode, output_dir)
    title = episode["title"]

    if dry_run:
        print("DRY RUN — would upload:")
        print(f"  title: {title}")
        print(f"  video: {video_path}")
        print(f"  thumbnail: {thumb_path if thumb_path.exists() else '(none)'}")
        print(f"  privacy: {privacy}")
        print("  description:")
        print(description)
        return None
    from googleapiclient.http import MediaFileUpload
    youtube = youtube or youtube_client()
    channel = channel_info(youtube)
    if not policy.get("channel_id") or channel["id"] != policy["channel_id"]:
        raise ValueError(f"Wrong OAuth channel: {channel['title']} ({channel['id']}); upload blocked")
    print(f"Verified destination: {channel['title']} — {channel['url']}")
    fingerprint = hashlib.sha256(json.dumps(episode, sort_keys=True).encode()).hexdigest()
    receipt = journal.read()
    if receipt and (receipt["channel_id"] != channel["id"]
                    or receipt["episode_sha256"] != fingerprint):
        raise ValueError("A different channel or episode already owns this publication date")
    video_id = receipt.get("video_id") if receipt else None
    if not video_id:
        video_id = find_existing(youtube, channel, episode["date"])
    if receipt and not video_id:
        raise ValueError("Previous upload outcome is uncertain. No new upload; reconcile YouTube first")
    if not receipt:
        receipt = {"date": episode["date"], "channel_id": channel["id"],
                   "episode_sha256": fingerprint, "state": "reserved", "video_id": video_id,
                   "requested_privacy": privacy,
                   "created_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        journal.write(receipt)  # Must succeed BEFORE calling videos.insert.
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": CATEGORY_ID,
            "tags": ["AI", "machine learning", episode["items"][0]["vertical_label"].title()],
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    if not video_id:
        media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            progress, response = request.next_chunk()
            if progress:
                print(f"  upload progress: {int(progress.progress() * 100)}%")
        video_id = response["id"]
    receipt.update(video_id=video_id, url=f"https://youtu.be/{video_id}", state="uploaded")
    journal.write(receipt)  # Record ID before thumbnail or subsequent calls can fail.
    info = youtube.videos().list(part="snippet,status", id=video_id).execute()["items"]
    if len(info) != 1 or info[0]["snippet"]["channelId"] != channel["id"]:
        raise ValueError("Uploaded video/channel could not be verified")
    status = info[0]["status"]
    receipt.update(actual_privacy=status["privacyStatus"], upload_status=status.get("uploadStatus"))
    journal.write(receipt)
    if status["privacyStatus"] != privacy or status.get("uploadStatus") in {"failed", "rejected", "deleted"}:
        raise ValueError("YouTube status differs from requested publication; inspect the receipt")
    if not receipt.get("thumbnail_set"):
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
        receipt["thumbnail_set"] = True
    receipt["state"] = "published" if status.get("uploadStatus") == "processed" else "processing"
    journal.write(receipt)
    print(f"{receipt['state']}: {receipt['url']} ({receipt['actual_privacy']})")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(f"\n- {episode['date']}: [{video_id}]({receipt['url']}) — "
                         f"{channel['title']} ({channel['id']}), {receipt['actual_privacy']}, {receipt['state']}\n")
    return video_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    parser.add_argument("--dry-run", action="store_true",
                         help="Print what would be uploaded without calling the YouTube API.")
    args = parser.parse_args()
    if not args.dry_run:
        parser.error("Use the GitHub Upload workflow with a verified Render run; direct uploads are disabled")
    episode = schema.load_episode(pathlib.Path(args.episode_json))
    publish_verified(episode, OUTPUT / episode["date"], {"privacy": "public"}, None, dry_run=True)
