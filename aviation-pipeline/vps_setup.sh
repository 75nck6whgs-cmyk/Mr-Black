#!/usr/bin/env bash
# vps_setup.sh — Run once on a fresh Ubuntu/Debian VPS.
# Sets up Python, ffmpeg, and the pipeline virtualenv.
#
# Usage:
#   ssh user@your-server
#   git clone <repo-url>
#   cd Mr-Noble/aviation-pipeline
#   bash vps_setup.sh

set -euo pipefail

echo "=== Aviation pipeline — VPS setup ==="
echo

# ── System dependencies ──────────────────────────────────────────────────────
echo "[1/4] Installing system packages..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    ffmpeg \
    git \
    libass-dev \
    2>/dev/null

echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
echo "  python: $(python3 --version)"

# ── Python virtualenv ─────────────────────────────────────────────────────────
echo
echo "[2/4] Creating virtual environment..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet

# ── Python dependencies ───────────────────────────────────────────────────────
echo
echo "[3/4] Installing Python packages..."
pip install -r requirements.txt --quiet
echo "  Packages installed: $(pip list 2>/dev/null | wc -l)"

# ── Folder structure ──────────────────────────────────────────────────────────
echo
echo "[4/4] Creating working directories..."
mkdir -p raw processed output metadata assets
echo "  raw/       ← drop clips here (via sync.sh or SFTP)"
echo "  assets/    ← drop ATC audio here"
echo "  output/    ← finished episodes appear here"
echo "  metadata/  ← description txt, SRT, thumbnail appear here"

# ── Done ──────────────────────────────────────────────────────────────────────
echo
echo "============================================"
echo "  Setup complete."
echo
echo "  Next steps:"
echo "  1. Push clips:     bash sync.sh incident_01.mp4 user@$(hostname -I | awk '{print $1}')"
echo "  2. Build episode:  bash build.sh episode_002.json"
echo "============================================"
