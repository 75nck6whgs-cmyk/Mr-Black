#!/usr/bin/env python3
"""
Upload a finished episode to YOUR YouTube channel via Data API v3.
Defaults to 'private' so you can review before publishing.

Setup (one-time):
  1. Go to console.cloud.google.com → APIs & Services → Enable YouTube Data API v3
  2. Create OAuth 2.0 credentials (Desktop app) → download as client_secrets.json
  3. Place client_secrets.json in this directory
  4. pip install google-api-python-client google-auth-oauthlib

Docs: https://developers.google.com/youtube/v3/guides/uploading_a_video
"""

import sys
import argparse
from pathlib import Path

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
BASE = Path(__file__).parent
SECRETS = BASE / "client_secrets.json"
META = BASE / "metadata"

# YouTube category IDs relevant to aviation content.
# 28 = Science & Technology, 25 = News & Politics, 19 = Travel & Events
CATEGORY_ID = "28"


def upload(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    privacy: str,
) -> str:
    if not SECRETS.exists():
        sys.exit(
            "client_secrets.json not found.\n"
            "See the docstring at the top of this file for setup steps."
        )

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        str(SECRETS), SCOPES
    )
    credentials = flow.run_local_server(port=0)
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": CATEGORY_ID,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
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

    print(f"Uploading {video_path.name} ({privacy})...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%", end="\r")

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"\n✅ Uploaded: {url}")
    return video_id


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("video", help="Path to finished episode MP4")
    p.add_argument("--title", required=True, help="Video title")
    p.add_argument(
        "--description",
        default="",
        help="Video description. If omitted, auto-loads from metadata/<stem>_description.txt",
    )
    p.add_argument(
        "--tags",
        default="aviation,incident,breakdown,atc,cockpit",
        help="Comma-separated tags (default: aviation,incident,breakdown,atc,cockpit)",
    )
    p.add_argument(
        "--privacy",
        default="private",
        choices=["private", "unlisted", "public"],
        help="Privacy status (default: private — review before publishing)",
    )
    args = p.parse_args()

    desc = args.description
    if not desc:
        desc_file = META / (Path(args.video).stem + "_description.txt")
        if desc_file.exists():
            desc = desc_file.read_text(encoding="utf-8")
            print(f"Auto-loaded description from {desc_file.name}")

    upload(Path(args.video), args.title, desc, args.tags.split(","), args.privacy)
