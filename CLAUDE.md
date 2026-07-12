# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mr-Noble is a Python media-generation project with two components:

1. **Coco Tree UGC Video Generator** (`generate_video.py`) — Creates short vertical promo videos from a single avatar image using the D-ID talking-avatar API, adding burned-in product captions and TTS voiceover.

2. **Aviation Incident Pipeline** (`aviation-pipeline/`) — A template system for building YouTube-style aviation incident breakdown videos from legally-sourced footage (public domain, licensed marketplaces, or direct permission). Handles normalization, ATC audio overlay, attribution burning, and episode stitching.

Both are single-file Python tools with file-based pipelines and CLI interfaces.

## Getting Started

### Environment Setup

```bash
# Create virtual env
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# System dependency: ffmpeg
# macOS: brew install ffmpeg
# Linux: apt install ffmpeg (or equivalent)
```

### Configuration

```bash
# Copy template to .env
cp .env.example .env

# Fill in your D-ID API key (required for avatar videos)
# DID_API_KEY=your_actual_key_here

# Optional: set custom voiceover path, output path, aspect ratio, duration
```

## Common Commands

### Coco Tree Video Generator

Generate a single talking-avatar video from an image:

```bash
python generate_video.py \
  --image /path/to/avatar.png \
  --output output/video.mp4 \
  --aspect-ratio 9:16
```

**Key CLI flags:**
- `--image` (required) — Avatar image path
- `--script` (default: built-in Coco Tree script) — Promo text to be TTS-voiced and lip-synced
- `--audio` — Optional existing voiceover .mp3; if omitted, gTTS generates one from `--script`
- `--output` (default: `output/coco_tree_talking_ugc.mp4`) — Output video path
- `--aspect-ratio` — `9:16` (default, Reels/TikTok) or `4:5` (Instagram)

**Captions:** Burned-in text is hardcoded in the script (`CAPTIONS` list at the top). Edit there to change timing/text.

**Fallback mode:** If D-ID API key is missing and SadTalker is installed locally, the script falls back to SadTalker.

### Aviation Pipeline

Build a single episode from a manifest:

```bash
cd aviation-pipeline
python build_episode.py episode_001.json
```

This outputs:
- `output/episode_001.mp4` — Final stitched video
- `metadata/episode_001_description.txt` — YouTube description with full attribution

**Manifest structure** (see `episode_001.json`):
```json
{
  "title": "Episode Title",
  "description": "Long-form description",
  "clips": [
    {
      "file": "clip_name.mp4",
      "source": "NTSB / FAA / Licensed Marketplace",
      "license": "Public Domain / CC-BY / Commercial License",
      "url": "https://link_to_source",
      "caption": "Display caption for attribution",
      "atc_audio": "audio_file.mp3",
      "atc_delay": 2.5,
      "atc_volume": 0.85,
      "ambient_duck": 0.15
    }
  ],
  "outro": "Thanks for watching"
}
```

**Key design constraint:** Every clip must declare `source` and `license`. The build aborts if missing—this is intentional, to keep a rights paper trail.

**ATC audio overlay:** Drop .mp3 files into `assets/`, declare them in the manifest. The pipeline automatically ducks the ambient sound and mixes ATC on top.

**Sourcing legally:**
- Public domain: NTSB, NASA, FAA, military archives
- Licensed marketplaces: ViralHog, Newsflare, AP Archive, Reuters (they buy rights and sublicense)
- Direct permission: DM the creator, keep the email on file

## Architecture

### Coco Tree Video Generator

**Flow:**
1. Load `.env` for D-ID API key
2. Generate TTS voiceover from script (gTTS → MP3)
3. Upload avatar image to D-ID API → get image URL
4. Create "talk" on D-ID (lip-sync animation request) → get talk ID
5. Poll D-ID status until video is ready → download raw MP4
6. Burn captions into the video using moviepy (crop to aspect ratio, overlay text clips)
7. Output final video

**Key functions:**
- `did_upload_image()` — D-ID image upload
- `did_create_talk()` — D-ID lip-sync generation request
- `did_wait_and_download()` — Poll until D-ID result is ready
- `add_burned_captions()` — MoviePy caption overlay with resizing
- `generate_tts()` — gTTS voiceover generation
- `run_sadtalker_fallback()` — Local SadTalker CLI fallback (if installed)

**Dependencies:**
- `requests` — D-ID API calls
- `python-dotenv` — `.env` loading
- `gTTS` — Text-to-speech
- `moviepy` — Video editing (captions, cropping, resizing)
- `Pillow` — Image handling (imported but used by moviepy)

### Aviation Pipeline

**Flow:**
1. Load manifest (JSON)
2. Generate title card (lavfi + ffmpeg)
3. For each clip:
   - Normalize to 1080p/30fps (scale, pad to preserve aspect)
   - Burn source attribution text at bottom
   - Optionally mix ATC audio with ambient ducking
4. Generate outro card
5. Concatenate all parts (ffmpeg concat demuxer)
6. Write attribution description file with full source URLs

**Key functions:**
- `normalize()` — Scale/pad, unify FPS/audio, burn credit, optionally mix ATC audio
- `make_card()` — Generate a title/outro card from text (ffmpeg lavfi)
- `concat()` — Stitch parts together (ffmpeg concat demuxer)
- `build()` — Orchestrate the full pipeline

**ffmpeg filters used:**
- `scale`, `pad`, `fps` — Video normalization
- `drawtext` — Attribution text overlay
- `adelay`, `amix`, `volume` — ATC audio mixing with ambient ducking

**Assumptions:**
- All clips must be valid video files (MP4 preferred)
- Audio must exist on all clips (or ffmpeg will fail)
- ffmpeg must be on PATH
- ATC audio files go in `assets/` directory

## File & Directory Structure

```
Mr-Noble/
├── generate_video.py              # Coco Tree UGC generator (main script)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── README.md                      # User-facing setup guide
├── styles.css, *.html, *.svg      # Legacy files (vCard/QR code generation?)
├── aviation-pipeline/             # Aviation episode builder
│   ├── build_episode.py           # Episode builder (main script)
│   ├── README.md                  # Sourcing + usage guide
│   ├── episode_001.json           # Manifest template
│   ├── episode_002.json           # Another example
│   ├── raw/                       # Input clips (user supplies)
│   ├── processed/                 # Intermediate normalized clips (generated)
│   ├── output/                    # Final episode MP4 + description
│   ├── metadata/                  # Description files with attribution
│   ├── assets/                    # ATC audio files
│   └── .gitignore                 # Ignores raw/, processed/, output/
└── CLAUDE.md                      # This file
```

## Development Notes

### Adding New Captions (Coco Tree)

Edit the `CAPTIONS` list in `generate_video.py`:
```python
CAPTIONS = [
    ("Text", start_seconds, end_seconds),
    ...
]
```

Text will appear white with a black stroke. Font is Arial-Bold, size 68, centered at 82% down the frame.

### Changing Video Specs (Aviation Pipeline)

Edit `W, H, FPS, ABR` constants at the top of `build_episode.py`:
```python
W, H, FPS = 1920, 1080, 30  # width, height, frames per second
ABR = "192k"                 # audio bitrate
```

### Testing D-ID Integration

If you don't have a D-ID API key, the script will try SadTalker fallback. To test the full D-ID flow:
1. Sign up at https://www.d-id.com/
2. Get an API key
3. Set `DID_API_KEY` in `.env`
4. Run `generate_video.py` with a test image

### Debugging Video Issues

- **moviepy font errors** — Make sure Arial or Arial-Bold is installed on your system
- **ffmpeg not found** — Verify ffmpeg is on PATH (`which ffmpeg`)
- **D-ID auth/upload errors** — Check API key, verify image format (PNG recommended)
- **ATC audio sync issues** — Adjust `atc_delay` in the manifest; use Audacity to find the exact time

## Rights & Attribution

Both tools are designed around a core principle: **source legally, transform meaningfully, credit fully.**

- Coco Tree generator: Single-image transformation with TTS + lip-sync (D-ID adds significant value)
- Aviation pipeline: Enforces source + license declaration per clip and burns attribution on-screen + in description

Do not use these tools to download-and-repost content without transformation and proper attribution.
