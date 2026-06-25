#!/usr/bin/env python3
"""
Generate captions from a finished episode using Whisper, then burn them in.
Produces: metadata/<stem>.srt  +  output/<stem>_captioned.mp4

Requires: pip install openai-whisper  +  ffmpeg with libass on PATH
"""

import sys
import subprocess
import shutil
import tempfile
from pathlib import Path

import whisper

BASE = Path(__file__).parent
META = BASE / "metadata"
OUT  = BASE / "output"


def format_time(seconds: float) -> str:
    h  = int(seconds // 3600)
    m  = int((seconds % 3600) // 60)
    s  = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def caption(episode_path: Path, model_size: str = "base"):
    META.mkdir(exist_ok=True)
    stem          = episode_path.stem
    srt_path      = META / f"{stem}.srt"
    captioned_path = OUT / f"{stem}_captioned.mp4"

    print(f"Transcribing with Whisper ({model_size})...")
    model  = whisper.load_model(model_size)
    result = model.transcribe(str(episode_path), task="transcribe")

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            f.write(
                f"{i}\n"
                f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n"
                f"{seg['text'].strip()}\n\n"
            )
    print(f"✅ SRT:       {srt_path}")

    # Copy SRT to a safe temp path — ffmpeg's subtitles filter is picky
    # about colons, spaces, and backslashes in the file path.
    with tempfile.TemporaryDirectory() as tmp:
        safe_srt = Path(tmp) / "captions.srt"
        shutil.copy(srt_path, safe_srt)

        style = (
            "FontSize=24,PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,Outline=2,Bold=1,"
            "Alignment=2,MarginV=30"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(episode_path),
                "-vf", f"subtitles={safe_srt}:force_style='{style}'",
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "copy",
                str(captioned_path),
            ],
            check=True,
        )

    print(f"✅ Captioned: {captioned_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("episode", help="Path to finished episode MP4")
    p.add_argument(
        "--model", default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model (default: base). Use 'small' for better accuracy.",
    )
    args = p.parse_args()
    caption(Path(args.episode), args.model)
