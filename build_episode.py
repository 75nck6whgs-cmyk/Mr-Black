#!/usr/bin/env python3
"""
Faceless aviation-incident channel — episode builder.

This automates the LEGAL parts of the pipeline: normalizing footage you have
the right to use, stamping on-screen attribution, adding intro/outro cards,
and stitching a finished episode. It does NOT download anything — you feed it
clips you've sourced from licensed marketplaces, public-domain archives
(NTSB/NASA/FAA), or direct creator permission.

Each clip is declared in clips.json along with its source + license, so
attribution is automatic and you keep a paper trail of your rights.

Requires: ffmpeg on PATH.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).parent
RAW = BASE / "raw"
PROC = BASE / "processed"
OUT = BASE / "output"
META = BASE / "metadata"

# Target spec — YouTube-friendly, consistent across clips so concat is clean.
W, H, FPS = 1920, 1080, 30
ABR = "192k"

def run(cmd):
    print("  $", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, capture_output=True)

def normalize(src: Path, dst: Path, credit: str, clip: dict = None):
    """Scale/pad to 1080p, unify fps + audio, burn attribution, optionally mix ATC audio."""
    safe = credit.replace(":", r"\:").replace("’", r"’")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
        f"fps={FPS},"
        f"drawtext=text=’{safe}’:x=20:y=h-40:fontsize=22:"
        f"fontcolor=white@0.85:box=1:boxcolor=black@0.4:boxborderw=8"
    )

    atc_file = (clip or {}).get("atc_audio")
    if atc_file:
        atc_path = BASE / "assets" / atc_file
        if not atc_path.exists():
            sys.exit(f"ATC audio not found: {atc_path}  (place it in assets/)")
        delay_ms = int((clip.get("atc_delay", 0)) * 1000)
        atc_vol = clip.get("atc_volume", 0.85)
        duck = clip.get("ambient_duck", 0.15)
        # Duck ambient under ATC; delay ATC to the moment tension peaks.
        af = (
            f"[0:a]volume={duck}[ambient];"
            f"[1:a]adelay={delay_ms}|{delay_ms},volume={atc_vol}[atc];"
            f"[ambient][atc]amix=inputs=2:duration=first[aout]"
        )
        run([
            "ffmpeg", "-y", "-i", str(src), "-i", str(atc_path),
            "-filter_complex", af,
            "-vf", vf,
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", ABR, "-ar", "48000",
            "-pix_fmt", "yuv420p",
            str(dst),
        ])
    else:
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", ABR, "-ar", "48000",
            "-pix_fmt", "yuv420p",
            str(dst),
        ])

def make_card(text: str, dst: Path, seconds: int = 3):
    """Title/outro card. Uses assets/card_bg.jpg as background if present."""
    safe = text.replace(":", r"\:").replace("’", r"’")
    bg = BASE / "assets" / "card_bg.jpg"
    text_filter = (
        f"drawtext=text=’{safe}’:x=(w-tw)/2:y=(h-th)/2:"
        f"fontsize=64:fontcolor=white:box=1:boxcolor=black@0.45:boxborderw=12"
    )
    if bg.exists():
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(bg),
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
            "-vf", (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H},fps={FPS},{text_filter}"
            ),
            "-t", str(seconds),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", ABR, "-pix_fmt", "yuv420p",
            str(dst),
        ])
    else:
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=0x0a0a14:s={W}x{H}:d={seconds}:r={FPS}",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
            "-vf", text_filter,
            "-t", str(seconds),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", ABR, "-pix_fmt", "yuv420p",
            str(dst),
        ])

def concat(parts, dst: Path):
    listfile = OUT / "_concat.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(listfile), "-c", "copy", str(dst),
    ])
    listfile.unlink()

def build(manifest_path: Path):
    manifest = json.loads(manifest_path.read_text())
    title = manifest["title"]
    clips = manifest["clips"]

    for d in (PROC, OUT, META):
        d.mkdir(exist_ok=True)

    print(f"\n=== Building: {title} ===")
    parts = []

    intro = PROC / "00_intro.mp4"
    make_card(title, intro, seconds=3)
    parts.append(intro)

    attributions = []
    for i, clip in enumerate(clips, 1):
        src = RAW / clip["file"]
        if not src.exists():
            sys.exit(f"Missing clip: {src}")
        # Guard: force you to declare a license before it'll process.
        if not clip.get("license") or not clip.get("source"):
            sys.exit(f"Clip '{clip['file']}' needs 'source' and 'license' fields.")
        credit = f"Source: {clip['source']} ({clip['license']})"
        dst = PROC / f"{i:02d}_{src.stem}.mp4"
        print(f"\n[{i}/{len(clips)}] {clip['file']}" + (" [+ATC]" if clip.get("atc_audio") else ""))
        normalize(src, dst, credit, clip)
        parts.append(dst)
        attributions.append(
            f"- {clip.get('caption', src.stem)} — {clip['source']} ({clip['license']})"
            + (f" {clip['url']}" if clip.get("url") else "")
        )

    outro = PROC / "99_outro.mp4"
    make_card(manifest.get("outro", "Thanks for watching"), outro, seconds=3)
    parts.append(outro)

    final = OUT / f"{manifest_path.stem}.mp4"
    print("\n=== Stitching episode ===")
    concat(parts, final)

    # Write a description with full attribution block ready to paste.
    desc = META / f"{manifest_path.stem}_description.txt"
    desc.write_text(
        manifest.get("description", "") + "\n\n"
        "Footage sources & licenses:\n" + "\n".join(attributions) + "\n"
    )

    print(f"\n✅ Episode:      {final}")
    print(f"✅ Description:  {desc}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python build_episode.py <manifest.json>")
    build(Path(sys.argv[1]))
