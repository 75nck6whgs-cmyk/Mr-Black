#!/usr/bin/env python3
"""
Interactive episode manifest creator.
Asks you questions, writes the JSON — no manual editing needed.

Usage: python3 new_episode.py
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).parent


def ask(prompt: str, default: str = "") -> str:
    if default:
        val = input(f"  {prompt} [{default}]: ").strip()
        return val if val else default
    while True:
        val = input(f"  {prompt}: ").strip()
        if val:
            return val
        print("  (required — please enter a value)")


def ask_optional(prompt: str) -> str:
    return input(f"  {prompt} (leave blank to skip): ").strip()


def next_episode_path() -> Path:
    existing = sorted(BASE.glob("episode_[0-9][0-9][0-9].json"))
    n = len(existing) + 1
    return BASE / f"episode_{n:03d}.json"


def main():
    print()
    print("=== New Episode ===")
    print("Press Ctrl+C at any time to cancel.")
    print()

    title       = ask("Episode title")
    description = ask("YouTube description (one line — you can expand later in Studio)")
    outro       = ask("Outro text", "Subscribe for more aviation breakdowns")

    clips = []
    print()
    print("Now add your clips. Enter a blank filename when you're done.")
    print()

    i = 1
    while True:
        print(f"  — Clip {i} —")
        fname = ask_optional("Filename in raw/ (e.g. clip_01.mp4)")
        if not fname:
            if i == 1:
                print("  No clips added. Exiting.")
                sys.exit(0)
            break

        caption = ask("Caption (what happens in this clip)")
        source  = ask("Source (e.g. NTSB, NASA, ViralHog)")
        license_ = ask("License (e.g. Public Domain (US Gov) / Licensed via ViralHog #VH-XXXX)")
        url     = ask_optional("Source URL")

        clip: dict = {
            "file":    fname,
            "caption": caption,
            "source":  source,
            "license": license_,
        }
        if url:
            clip["url"] = url

        print()
        atc = ask_optional("ATC audio file in assets/ (e.g. clip_01_atc.mp3)")
        if atc:
            delay  = ask("ATC start — seconds into the clip where radio comms begin", "0")
            volume = ask("ATC volume 0–1", "0.85")
            duck   = ask("Ambient duck 0–1 (how quiet to make the original audio)", "0.15")
            clip["atc_audio"]    = atc
            clip["atc_delay"]    = float(delay)
            clip["atc_volume"]   = float(volume)
            clip["ambient_duck"] = float(duck)

        clips.append(clip)
        i += 1
        print()

    manifest = {
        "title":       title,
        "description": description,
        "outro":       outro,
        "clips":       clips,
    }

    out = next_episode_path()
    out.write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"✅ Created: {out.name}")
    print()
    print("  Next steps:")
    print(f"    1. Drop your clips into raw/")
    if any(c.get("atc_audio") for c in clips):
        print(f"    2. Drop ATC audio into assets/")
    print(f"    3. make build EP={out.name}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
