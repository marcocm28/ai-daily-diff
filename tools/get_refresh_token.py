"""Reconnect the existing Google OAuth client to the configured dedicated channel.
Run locally with the downloaded Desktop client JSON. Marco completes the consent
screen and selects the AI Daily Diff brand channel. The script verifies the channel
and saves secrets only to ignored .local/youtube-secrets.env, never to stdout.
Usage: python tools/get_refresh_token.py path/to/client_secret.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import ssl
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
    root = pathlib.Path(__file__).resolve().parent.parent
    ca_file = None
    if sys.platform == "win32":
        # Honor the Windows trust store (including the installed corporate proxy CA).
        # Certificate verification stays enabled for OAuth exchange and channel lookup.
        ca_file = root / ".local" / "windows-trust.pem"
        ca_file.parent.mkdir(exist_ok=True)
        certs = ssl.create_default_context().get_ca_certs(binary_form=True)
        ca_file.write_text("".join(ssl.DER_cert_to_PEM_cert(cert) for cert in certs), encoding="ascii")
        flow.oauth2session.verify = str(ca_file)
    # prompt="consent" forces Google to issue a refresh_token even if this account already
    # granted these scopes before (otherwise a repeat consent can come back with none).
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    if not creds.refresh_token:
        print("\nNo refresh_token came back — Google only issues one on the first consent for a "
              "given account+scopes+client. Revoke this app's access at "
              "https://myaccount.google.com/permissions and re-run to force a fresh one.",
              file=sys.stderr)
        sys.exit(1)

    from googleapiclient.discovery import build
    policy = json.loads((root / "config/publishing.json").read_text(encoding="utf-8"))
    if ca_file:
        import httplib2
        from google_auth_httplib2 import AuthorizedHttp
        youtube = build("youtube", "v3", http=AuthorizedHttp(creds, http=httplib2.Http(ca_certs=str(ca_file))))
    else:
        youtube = build("youtube", "v3", credentials=creds)
    channels = youtube.channels().list(part="snippet", mine=True).execute()["items"]
    if len(channels) != 1 or channels[0]["id"] != policy["channel_id"]:
        print("Wrong channel selected. No secrets saved. Select the AI Daily Diff brand channel.",
              file=sys.stderr)
        sys.exit(1)
    target = root / ".local" / "youtube-secrets.env"
    target.parent.mkdir(exist_ok=True)
    target.write_text(f"YT_CLIENT_ID={creds.client_id}\nYT_CLIENT_SECRET={creds.client_secret}\n"
                      f"YT_REFRESH_TOKEN={creds.refresh_token}\n", encoding="utf-8")
    print(f"Verified channel: {channels[0]['snippet']['title']} ({channels[0]['id']})")
    print(f"Secrets saved locally to {target}. Never paste them into chat or commit this file.")
    print("Copy the three values into the existing GitHub Actions secrets, then run Verify YouTube channel.")


if __name__ == "__main__":
    main()
