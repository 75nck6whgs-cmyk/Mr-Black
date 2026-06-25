#!/usr/bin/env python3
"""
Generate a YouTube thumbnail (1280x720) from a finished episode.
Grabs a frame at --timestamp, applies a dark gradient, overlays title text.
Produces: metadata/<stem>_thumbnail.jpg

Requires: pip install Pillow  +  ffmpeg on PATH
"""

import sys
import subprocess
import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TW, TH = 1280, 720

BASE = Path(__file__).parent
META = BASE / "metadata"

FONT_CANDIDATES = [
    # Mac
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    # Windows
    "C:/Windows/Fonts/arialbd.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_thumbnail(episode: Path, title: str, timestamp: float = 3.0):
    META.mkdir(exist_ok=True)
    frame_path = META / f"{episode.stem}_frame.jpg"
    out_path = META / f"{episode.stem}_thumbnail.jpg"

    # Extract one frame.
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-ss", str(timestamp), "-i", str(episode),
            "-frames:v", "1", "-q:v", "2",
            str(frame_path),
        ],
        check=True,
        capture_output=True,
    )

    img = Image.open(frame_path).convert("RGBA").resize((TW, TH))

    # Dark gradient over the bottom half — makes white text always legible.
    overlay = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    gradient_start = TH // 3
    for y in range(gradient_start, TH):
        alpha = int(200 * (y - gradient_start) / (TH - gradient_start))
        draw.rectangle([(0, y), (TW, y + 1)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)

    # Title text — large, bold, bottom-centre with drop shadow.
    draw = ImageDraw.Draw(img)
    font_large = load_font(80)
    font_small = load_font(52)

    words = title.upper().split()
    # First line bigger if title is short enough.
    if len(words) <= 4:
        lines = [title.upper()]
        font = font_large
        line_h = 95
    else:
        lines = textwrap.wrap(title.upper(), width=20)
        font = font_small
        line_h = 65

    total_h = len(lines) * line_h
    y = TH - total_h - 50

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (TW - w) / 2
        # Drop shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_h

    img.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"✅ Thumbnail: {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("episode", help="Path to finished episode MP4")
    p.add_argument("title", help="Title text to burn onto the thumbnail")
    p.add_argument(
        "--timestamp",
        type=float,
        default=3.0,
        help="Seconds into video to grab the frame (default: 3.0 — skip the intro card)",
    )
    args = p.parse_args()
    make_thumbnail(Path(args.episode), args.title, args.timestamp)
