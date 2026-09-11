"""Stage 7 — PUBLISH (YouTube half). Uploads output/YYYY-MM-DD/video.mp4 with a description
built from the episode + brief.md, and sets the thumbnail.

Reads three secrets from the environment — never from a file committed to the repo:
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
These come from get_refresh_token.py (run once, locally, by Marco) and are stored as GitHub
Actions repository secrets (Settings -> Secrets and variables -> Actions).

This step only runs after .github/workflows/test.yml has passed on the commit — see that
workflow file. It is never run on an episode whose examples haven't been re-verified on a clean
CI runner (Gate 2).

Usage:
  python src/upload.py data/episodes/2026-08-28.json
"""
from __future__ import annotations

import argparse
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


def build_description(episode: dict) -> str:
    date = episode["date"]
    brief_path = OUTPUT / date / "brief.md"
    body = brief_path.read_text(encoding="utf-8") if brief_path.exists() else ""

    chapters = ["00:00 Front page"]
    # Rough even split — replace with real per-item timestamps once render_video.py reports
    # cumulative hold times per slide (a good first Loop A refinement).
    lines = [
        body,
        "",
        f"Episode page (all downloads): {PAGES_BASE_URL}/{date}/",
        f"Slides (PDF): {PAGES_BASE_URL}/{date}/slides.pdf",
        f"Cheat sheet (PDF, CC BY 4.0): {PAGES_BASE_URL}/{date}/cheatsheet.pdf",
        f"All code: {REPO_URL}/tree/main/examples",
        "",
        "\n".join(chapters),
        "",
        brand.MUSIC_CREDIT,
        "",
        "AI Daily Diff — a new diff every weekday. Every claim sourced, every example tested "
        "in CI before this video is published.",
    ]
    description = "\n".join(lines)[:4900]  # YouTube description limit is 5000 chars
    # YouTube's API rejects title/description containing < or > (reason: invalidDescription) —
    # both can show up legitimately in brief text (e.g. "< 1 s", code output, comparisons).
    return description.replace("<", "‹").replace(">", "›")


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


def upload(episode_path: pathlib.Path, *, privacy: str = "public", dry_run: bool = False) -> str | None:
    episode = schema.load_episode(episode_path)
    problems = schema.validate_episode(episode)
    if problems:
        print(f"Refusing to upload — schema/Gate 1 problems in {episode_path}:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    video_path = OUTPUT / episode["date"] / "video.mp4"
    thumb_path = OUTPUT / episode["date"] / "thumbnail.png"
    if not video_path.exists():
        print(f"missing {video_path} — run src/render_video.py first", file=sys.stderr)
        sys.exit(1)

    description = build_description(episode)
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

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

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
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded: https://youtu.be/{video_id}")

    if thumb_path.exists():
        youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()
        print("Thumbnail set.")

    return video_id


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("episode_json")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--dry-run", action="store_true",
                         help="Print what would be uploaded without calling the YouTube API.")
    args = parser.parse_args()
    upload(pathlib.Path(args.episode_json), privacy=args.privacy, dry_run=args.dry_run)
