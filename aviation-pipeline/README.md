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

## Usage

```bash
# 1. Drop your legally-sourced clips into raw/
# 2. Describe the episode in a manifest (copy episode_001.json)
# 3. Build:
python3 build_episode.py episode_001.json
# -> output/episode_001.mp4  + metadata/episode_001_description.txt
```

## Running in Claude Code

This works in either place. Claude Code is the better home for it because you'll
be iterating on files and running ffmpeg repeatedly:

```bash
cd aviation-pipeline
claude
# then ask it to: add a clip, tweak the card style, batch-build a week of episodes
```

## ATC-audio overlay

Add real radio comms to any clip by dropping the audio into `assets/` and
declaring it in the manifest. The builder ducks ambient sound and mixes ATC
on top — the tension of the real transmission is what keeps viewers watching.

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
| `atc_audio` | — | Filename in `assets/`. Omit to skip overlay. |
| `atc_delay` | `0` | Seconds into the clip before ATC starts. Align to the peak moment. |
| `atc_volume` | `0.85` | ATC level (0–1). |
| `ambient_duck` | `0.15` | How much to reduce the clip's original audio under ATC. |

**Where to get ATC audio (legally):**
- **NTSB accident dockets** — CVR transcripts and sometimes audio. Public domain.
- **LiveATC.net** — Real-time and archived ATC. Check their terms; non-commercial
  archival use is generally permitted with credit.
- **FAA FOIA requests** — Request specific recordings. Free, takes a few weeks.

## Next build-outs (ask and I'll add them)

- ~~**ATC-audio overlay**~~ — ✅ done
- **Auto-caption generation** (Whisper) — for accessibility + SEO
- **Thumbnail generator** — 1280×720 with title text
- **YouTube Data API uploader** — for your OWN finished episodes
- **Batch mode** — build a whole content calendar in one run
