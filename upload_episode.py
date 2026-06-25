#!/usr/bin/env python3
"""
Upload a finished episode to YOUR YouTube channel via Data API v3.
Defaults to 'private' so you can review before publishing.
Token is cached after first login — no browser needed on repeat runs.

Setup (one-time):
  1. console.cloud.google.com → APIs & Services → Enable YouTube Data API v3
  2. Create OAuth 2.0 credentials (Desktop app) → download as client_secrets.json
  3. Place client_secrets.json in this directory
  4. pip install google-api-python-client google-auth-oauthlib google-auth

Docs: https://developers.google.com/youtube/v3/guides/uploading_a_video
"""

import sys
import argparse
from pathlib import Path

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
BASE = Path(__file__).parent
SECRETS = BASE / "client_secrets.json"
META = BASE / "metadata"
TOKEN_FILE = Path.home() / ".aviation_pipeline_token.json"
CATEGORY_ID = "28"  # Science & Technology


def get_credentials() -> Credentials:
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not SECRETS.exists():
                sys.exit(
                    "client_secrets.json not found.\n"
                    "See the docstring at the top of this file for setup steps."
                )
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                str(SECRETS), SCOPES
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        print(f"  Token saved to {TOKEN_FILE} (reused on future uploads)")

    return creds


def upload_thumbnail(youtube, video_id: str, thumb_path: Path):
    media = googleapiclient.http.MediaFileUpload(
        str(thumb_path), mimetype="image/jpeg"
    )
    youtube.thumbnails().set(videoId=video_id, media_body=media).execute()
    print(f"✅ Thumbnail attached")


def upload(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str,
    publish_at: str | None,
) -> str:
    creds = get_credentials()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    status = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at  # RFC 3339: 2026-07-01T18:00:00Z

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": CATEGORY_ID,
        },
        "status": status,
    }

    media = googleapiclient.http.MediaFileUpload(
        str(video_path),
        chunksize=256 * 1024,
        resumable=True,
        mimetype="video/mp4",
    )
    request = youtube.videos().insert(
        part=",".join(body.keys()), body=body, media_body=media
    )

    print(f"Uploading {video_path.name} [{privacy}]...")
    response = None
    while response is None:
        status_obj, response = request.next_chunk()
        if status_obj:
            print(f"  {int(status_obj.progress() * 100)}%", end="\r")

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\n✅ Uploaded: {url}")

    if publish_at:
        print(f"   Scheduled: {publish_at}")

    # Auto-attach thumbnail if present.
    stem = video_path.stem.replace("_captioned", "")
    thumb = META / f"{stem}_thumbnail.jpg"
    if thumb.exists():
        print(f"  Attaching thumbnail: {thumb.name}")
        upload_thumbnail(youtube, video_id, thumb)
    else:
        print(f"  No thumbnail at {thumb} — set one manually in YouTube Studio")

    return video_id


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("video", help="Path to finished episode MP4")
    p.add_argument("--title", required=True, help="Video title")
    p.add_argument(
        "--description", default="",
        help="Description. Auto-loads from metadata/<stem>_description.txt if omitted.",
    )
    p.add_argument(
        "--tags", default="aviation,incident,breakdown,atc,cockpit",
        help="Comma-separated tags",
    )
    p.add_argument(
        "--privacy", default="private",
        choices=["private", "unlisted", "public"],
    )
    p.add_argument(
        "--publish-at", default=None, metavar="RFC3339",
        help="Schedule publish time e.g. 2026-07-01T18:00:00Z",
    )
    args = p.parse_args()

    desc = args.description
    if not desc:
        desc_file = META / (Path(args.video).stem.replace("_captioned", "") + "_description.txt")
        if desc_file.exists():
            desc = desc_file.read_text(encoding="utf-8")
            print(f"Auto-loaded description from {desc_file.name}")

    upload(
        Path(args.video), args.title, desc,
        args.tags.split(","), args.privacy, args.publish_at,
    )
