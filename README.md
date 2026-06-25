# Faceless Aviation-Incident Channel — Pipeline

A repeatable system for producing aviation-incident breakdown videos at scale,
without filming anything yourself and without scraping other people's videos.
The automation handles the legal-to-automate parts: normalizing footage,
stamping attribution, building intro/outro, stitching episodes, and generating
a description with full source credits.

## The rule that keeps the channel alive

You source footage you have the RIGHT to use, then transform it. You never
download-and-repost. Three legal sourcing routes:

1. **Public domain** — NTSB, NASA, FAA, military. Free, on-theme, no license needed.
2. **Licensed marketplaces** — ViralHog, Newsflare, Storyful/Jukin, AP Archive,
   Reuters. They buy rights from the original filmer and sublicense to you.
   This is how the big "crazy footage" channels actually operate.
3. **Direct permission** — DM the filmer. Keep the email/agreement on file.

Each clip's manifest entry must declare `source` + `license` or the build aborts.
That guardrail is intentional: it keeps a rights paper trail per clip.

## The transformation requirement

YouTube's reused-content policy demerits straight reposts even with a credit.
Add real value: ATC audio walkthrough, a diagram of the aircraft's path,
"here's the moment the crew recovered and why it worked." That's what makes the
upload defensible AND a better product.

---

## Zero to published — complete walkthrough

### 1. Server setup (one-time)

```bash
ssh user@your-vps
git clone <repo-url> && cd Mr-Noble
bash vps_setup.sh
```

Or with make:
```bash
make setup
```

### 2. Push your clips (from phone or laptop)

Edit `sync.sh` — set `SERVER=user@your-vps-ip` — then:

```bash
bash sync.sh raw/incident_01.mp4          # footage
bash sync.sh assets/incident_01_atc.mp3  # ATC audio
```

### 3. Create your episode manifest

Copy `episode_001.json`, fill in your clips, sources, and licenses.
Every clip needs `source` + `license` or the build refuses to run.

### 4. Build

```bash
# Single episode — encode + captions + thumbnail in one command
make build EP=episode_002.json

# Full content calendar
make batch
```

### 5. Pull finished files back to your phone

```bash
bash sync.sh --pull
# -> output/*.mp4, metadata/*_thumbnail.jpg, metadata/*_description.txt
```

### 6. Upload to YouTube

```bash
make upload EP=output/episode_002.mp4 TITLE="When Pilots Save the Day"

# Schedule a publish time
python3 upload_episode.py output/episode_002.mp4 \
  --title "When Pilots Save the Day" \
  --publish-at 2026-07-01T18:00:00Z
```

Token is cached after first login — no browser re-auth on repeat uploads.
Thumbnail is attached automatically if `metadata/<stem>_thumbnail.jpg` exists.

---

## ATC-audio overlay

Add real radio comms to any clip. Drop the audio into `assets/`, declare it in
the manifest. The builder ducks ambient sound and mixes ATC on top.

```json
{
  "file": "incident_01.mp4",
  "atc_audio": "incident_01_atc.mp3",
  "atc_delay": 2.5,
  "atc_volume": 0.85,
  "ambient_duck": 0.15
}
```

| Field | Default | Effect |
|---|---|---|
| `atc_audio` | — | Filename in `assets/`. Omit to skip. |
| `atc_delay` | `0` | Seconds into the clip before ATC starts. |
| `atc_volume` | `0.85` | ATC level (0–1). |
| `ambient_duck` | `0.15` | How much to reduce ambient under ATC. |

**Where to get ATC audio (legally):**
- **NTSB accident dockets** — CVR transcripts + sometimes audio. Public domain.
- **LiveATC.net** — Archived ATC recordings. Non-commercial use with credit.
- **FAA FOIA requests** — Request specific recordings. Free, takes a few weeks.

---

## YouTube uploader setup (one-time)

1. [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Enable **YouTube Data API v3**
2. Create OAuth 2.0 credentials (Desktop app) → download as `client_secrets.json`
3. Place `client_secrets.json` in this directory (gitignored — never committed)
4. First upload opens a browser for OAuth — token saved to `~/.aviation_pipeline_token.json` after that

---

## Running in Claude Code

```bash
claude
# ask it to: add a clip, tweak the card style, batch-build a week of episodes
```

---

## Install dependencies

```bash
pip install -r requirements.txt

# Mac
brew install ffmpeg

# Linux / VPS
sudo apt install ffmpeg
```

## Make targets

```
make setup      Install everything on the server
make build      Build + caption + thumbnail (EP=episode_002.json)
make batch      Build all episodes in schedule.json
make upload     Upload to YouTube (EP=output/ep.mp4 TITLE="...")
make clean      Remove processed/ and output/ files
```
