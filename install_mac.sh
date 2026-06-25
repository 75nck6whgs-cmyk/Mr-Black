#!/usr/bin/env bash
# install_mac.sh — One-command Mac setup for the aviation pipeline.
# Run this once after cloning the repo:
#   bash install_mac.sh

set -euo pipefail

echo ""
echo "=== Aviation Pipeline — Mac Setup ==="
echo ""

# ── Homebrew ──────────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
    echo "[1/4] Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    # Apple Silicon installs to /opt/homebrew — add to PATH for this session
    if [[ -f /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        echo "  Added Homebrew to PATH (~/.zprofile)"
    fi
else
    echo "[1/4] Homebrew already installed ✓"
fi

# ── System tools ──────────────────────────────────────────────────────────────
echo ""
echo "[2/4] Installing ffmpeg, python3, git..."
brew install ffmpeg python3 git 2>/dev/null || brew upgrade ffmpeg python3 git 2>/dev/null || true
echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1 | cut -d' ' -f3)"
echo "  python: $(python3 --version)"

# ── Python virtualenv ─────────────────────────────────────────────────────────
echo ""
echo "[3/4] Creating virtual environment..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  Packages installed ✓"

# ── Folder structure ──────────────────────────────────────────────────────────
echo ""
echo "[4/4] Creating working directories..."
mkdir -p raw processed output metadata assets

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "================================================"
echo "  Setup complete!"
echo ""
echo "  Every new Terminal session, run first:"
echo "    source .venv/bin/activate"
echo ""
echo "  Then build your first episode:"
echo "    make build EP=episode_002.json"
echo ""
echo "  Create a new episode interactively:"
echo "    python3 new_episode.py"
echo "================================================"
echo ""
