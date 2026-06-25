#!/usr/bin/env bash
# build.sh — Build one episode end-to-end: encode, caption, thumbnail.
# Run this on the VPS from inside aviation-pipeline/.
#
# Usage:
#   bash build.sh episode_002.json
#   bash build.sh episode_002.json --no-captions
#   bash build.sh episode_002.json --no-thumbnail
#
# Outputs:
#   output/<stem>.mp4                  finished episode
#   output/<stem>_captioned.mp4        with burned-in captions
#   metadata/<stem>.srt                caption file
#   metadata/<stem>_description.txt    YouTube description (paste-ready)
#   metadata/<stem>_thumbnail.jpg      1280x720 thumbnail

set -euo pipefail

MANIFEST="${1:-}"
if [[ -z "$MANIFEST" ]]; then
    echo "Usage: bash build.sh <manifest.json> [--no-captions] [--no-thumbnail]"
    exit 1
fi

DO_CAPTIONS=true
DO_THUMBNAIL=true
WHISPER_MODEL="base"

for arg in "${@:2}"; do
    case "$arg" in
        --no-captions)   DO_CAPTIONS=false ;;
        --no-thumbnail)  DO_THUMBNAIL=false ;;
        --model=*)       WHISPER_MODEL="${arg#--model=}" ;;
    esac
done

# Activate virtualenv
# shellcheck disable=SC1091
source "$(dirname "$0")/.venv/bin/activate"

STEM="${MANIFEST%.json}"
EPISODE="output/${STEM}.mp4"

echo
echo "=== Build: $MANIFEST ==="
echo

# ── Step 1: Encode episode ────────────────────────────────────────────────────
echo "[1] Encoding episode..."
python3 build_episode.py "$MANIFEST"

if [[ ! -f "$EPISODE" ]]; then
    echo "✗ Episode not found at $EPISODE — build failed."
    exit 1
fi

# ── Step 2: Captions (Whisper) ────────────────────────────────────────────────
if $DO_CAPTIONS; then
    echo
    echo "[2] Generating captions (Whisper $WHISPER_MODEL)..."
    python3 caption_episode.py "$EPISODE" --model "$WHISPER_MODEL"
else
    echo
    echo "[2] Captions skipped (--no-captions)"
fi

# ── Step 3: Thumbnail ─────────────────────────────────────────────────────────
if $DO_THUMBNAIL; then
    echo
    echo "[3] Generating thumbnail..."
    # Pull title from manifest
    TITLE=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['title'])" "$MANIFEST")
    python3 make_thumbnail.py "$EPISODE" "$TITLE" --timestamp 5
else
    echo
    echo "[3] Thumbnail skipped (--no-thumbnail)"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo
echo "============================================"
echo "  Done: $STEM"
echo
ls -lh output/${STEM}*.mp4 2>/dev/null || true
ls -lh metadata/${STEM}* 2>/dev/null || true
echo "============================================"
