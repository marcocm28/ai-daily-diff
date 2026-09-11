"""One-shot local helper — run by hand, once, whenever the YouTube OAuth refresh token needs to
be (re)issued. Never run this from a Claude/Codex session: it opens a real browser and a local
redirect server, which only makes sense on Marco's machine.

Why this is needed again now: the OAuth consent screen was in "Testing" publishing status, and
Google expires refresh tokens issued to a Testing app after 7 days regardless of activity — that's
why YT_REFRESH_TOKEN went stale. Moving the consent screen to "In production" (done 2026-09-11)
removes the 7-day expiry, but the *existing* refresh token isn't retroactively extended — a new
one has to be minted under the app's new publishing status. This script does that exchange and
prints the values to put in the three GitHub Actions repo secrets (Settings -> Secrets and
variables -> Actions): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.

Prerequisites (Google Cloud Console, same project as before):
  1. APIs & Services -> OAuth consent screen: publishing status "In production".
     youtube.upload is a restricted scope, so if this project has never been through Google's
     verification, you'll see an "unverified app" warning during consent below. That's expected
     for a single-user app you own — click "Advanced" -> "Go to <project name> (unsafe)" to
     proceed. If Google has actually suspended/blocked the scope pending verification, the consent
     screen will refuse outright instead of just warning; if that happens, stop and check the
     consent screen's verification status before continuing.
  2. APIs & Services -> Credentials: an OAuth client of type "Desktop app" (create one if the old
     client no longer works). Download its JSON via the download icon.

Usage:
  python tools/get_refresh_token.py path/to/client_secret.json

This opens your default browser for the Google consent screen, then prints the new client ID,
client secret, and refresh token. Nothing is written to disk in this repo.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("client_secret_json", type=pathlib.Path,
                         help="Downloaded from Google Cloud Console -> Credentials -> your Desktop OAuth client.")
    args = parser.parse_args()

    if not args.client_secret_json.exists():
        print(f"not found: {args.client_secret_json}", file=sys.stderr)
        sys.exit(1)

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(args.client_secret_json), SCOPES)
    # prompt="consent" forces Google to issue a refresh_token even if this account already
    # granted these scopes before (otherwise a repeat consent can come back with none).
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    print("\nSet these as GitHub repo secrets (Settings -> Secrets and variables -> Actions):\n")
    print(f"YT_CLIENT_ID={creds.client_id}")
    print(f"YT_CLIENT_SECRET={creds.client_secret}")
    print(f"YT_REFRESH_TOKEN={creds.refresh_token}")

    if not creds.refresh_token:
        print("\nNo refresh_token came back — Google only issues one on the first consent for a "
              "given account+scopes+client. Revoke this app's access at "
              "https://myaccount.google.com/permissions and re-run to force a fresh one.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
