#!/usr/bin/env bash
# sync.sh — Push clips and ATC audio from your local machine/phone to the VPS.
# Run this on your LOCAL device (laptop, Termux on Android), not the server.
#
# Setup (one-time):
#   1. Edit the SERVER and REMOTE_PATH lines below with your VPS details.
#   2. For passwordless login from phone: ssh-keygen, then ssh-copy-id user@server
#
# Usage:
#   bash sync.sh raw/incident_01.mp4           # push one clip
#   bash sync.sh raw/                           # push everything in raw/
#   bash sync.sh assets/incident_01_atc.mp3    # push ATC audio
#   bash sync.sh --pull                         # pull finished episodes back to local

# ── Configure these ───────────────────────────────────────────────────────────
SERVER="user@your-server-ip"
REMOTE_PATH="~/Mr-Noble/aviation-pipeline"
# ─────────────────────────────────────────────────────────────────────────────

if [[ -z "${SERVER##*your-server-ip*}" ]]; then
    echo "Edit sync.sh first: set SERVER to user@your-vps-ip"
    exit 1
fi

if [[ "${1:-}" == "--pull" ]]; then
    echo "Pulling finished episodes from server..."
    mkdir -p output metadata
    scp "${SERVER}:${REMOTE_PATH}/output/*.mp4" output/ 2>/dev/null && echo "  → output/" || echo "  No MP4s yet."
    scp "${SERVER}:${REMOTE_PATH}/metadata/*_thumbnail.jpg" metadata/ 2>/dev/null && echo "  → metadata/ (thumbnails)" || true
    scp "${SERVER}:${REMOTE_PATH}/metadata/*_description.txt" metadata/ 2>/dev/null && echo "  → metadata/ (descriptions)" || true
    exit 0
fi

if [[ $# -eq 0 ]]; then
    echo "Usage:"
    echo "  bash sync.sh raw/incident_01.mp4       # push a clip"
    echo "  bash sync.sh assets/atc.mp3            # push ATC audio"
    echo "  bash sync.sh --pull                    # pull finished episodes"
    exit 1
fi

for FILE in "$@"; do
    if [[ ! -f "$FILE" && ! -d "$FILE" ]]; then
        echo "Not found: $FILE"
        continue
    fi

    # Route to the right remote folder based on local path.
    if [[ "$FILE" == assets/* ]]; then
        DEST="${SERVER}:${REMOTE_PATH}/assets/"
    else
        DEST="${SERVER}:${REMOTE_PATH}/raw/"
    fi

    echo "Uploading $FILE → $DEST"
    scp -r "$FILE" "$DEST"
done

echo
echo "Done. SSH in and run: bash build.sh <manifest.json>"
