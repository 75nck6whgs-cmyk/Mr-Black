#!/usr/bin/env python3
"""
Batch-build a week (or more) of episodes from a content schedule.
Usage: python batch_build.py schedule.json

Runs build_episode.py for each manifest in order, then optionally
runs caption_episode.py and make_thumbnail.py on each finished episode.
"""

import json
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).parent


def run_step(cmd: list, label: str) -> bool:
    print(f"  → {label}")
    result = subprocess.run([str(c) for c in cmd])
    if result.returncode != 0:
        print(f"  ✗ Failed: {label}")
        return False
    return True


def batch(schedule_path: Path):
    schedule = json.loads(schedule_path.read_text())
    episodes = schedule.get("episodes", [])
    captions = schedule.get("captions", False)
    thumbnails = schedule.get("thumbnails", False)
    whisper_model = schedule.get("whisper_model", "base")

    if not episodes:
        sys.exit("No episodes listed in schedule.json")

    print(f"=== Batch build: {len(episodes)} episode(s) ===")
    if captions:
        print(f"    Captions: on  (Whisper {whisper_model})")
    if thumbnails:
        print(f"    Thumbnails: on")
    print()

    built, failed = [], []

    for i, entry in enumerate(episodes, 1):
        # Entry can be a plain string (manifest filename) or a dict with options.
        if isinstance(entry, str):
            manifest_file = entry
            thumb_title = None
            thumb_ts = 3.0
        else:
            manifest_file = entry["manifest"]
            thumb_title = entry.get("thumbnail_title")
            thumb_ts = entry.get("thumbnail_timestamp", 3.0)

        manifest_path = BASE / manifest_file
        if not manifest_path.exists():
            print(f"[{i}/{len(episodes)}] SKIP — not found: {manifest_file}\n")
            failed.append(manifest_file)
            continue

        print(f"[{i}/{len(episodes)}] {manifest_file}")

        ok = run_step(
            ["python3", BASE / "build_episode.py", manifest_path],
            "build episode",
        )
        if not ok:
            failed.append(manifest_file)
            continue

        stem = manifest_path.stem
        episode_mp4 = BASE / "output" / f"{stem}.mp4"

        if captions and episode_mp4.exists():
            run_step(
                ["python3", BASE / "caption_episode.py", episode_mp4, "--model", whisper_model],
                "generate captions",
            )

        if thumbnails and episode_mp4.exists():
            title = thumb_title or stem.replace("_", " ").title()
            run_step(
                ["python3", BASE / "make_thumbnail.py", episode_mp4, title,
                 "--timestamp", str(thumb_ts)],
                f"make thumbnail ({title})",
            )

        built.append(manifest_file)
        print()

    print(f"=== Done: {len(built)}/{len(episodes)} built ===")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python batch_build.py schedule.json")
    batch(Path(sys.argv[1]))
