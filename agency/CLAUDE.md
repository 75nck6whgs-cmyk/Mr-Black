# Mr. Noble Agency — Claude Code Context

## What this is
A 7-agent automated website sales pipeline. Claude Code powers the AI steps.
Run everything from the `agency/` directory.

## Agent pipeline (in order)
| Agent | File | Input | Output |
|---|---|---|---|
| Scout | `agents/scout.py` | Google Maps API | `state/leads/` |
| Diagnoser | `agents/diagnoser.py` | `state/leads/` | `state/diagnosed/` |
| Builder | `agents/builder.py` | `state/diagnosed/` | `state/built/` + HTML files |
| Filmer | `agents/filmer.py` | `state/built/` | `state/filmed/` + MP4 files |
| Checker | `agents/checker.py` | `state/filmed/` | `state/checked/` |
| (Owner approval) | `approve.py` or mobile app | `state/checked/` | `state/approved/` |
| Pitcher | `agents/pitcher.py` | `state/approved/` | `state/sent/` |

## Key files
- `config.yaml` — cities, business types, limits, API settings
- `.env` — all secrets (never commit this)
- `core/state.py` — shared state manager (JSON files per lead)
- `core/claude_client.py` — Anthropic API wrapper
- `core/website_checker.py` — detects outdated/missing websites

## Running
```bash
source .venv/bin/activate
python orchestrate.py           # full pipeline
python orchestrate.py scout     # single agent
python approve.py               # CLI approval
python -m agents.mobile.app    # mobile approval UI (port 5001)
python orchestrate.py pitcher   # send approved leads
```

## Lead JSON structure
Each lead file in `state/<stage>/<id>.json` has:
- `business` — name, type, city, phone, rating, etc.
- `website_check` — has_website, is_outdated, oldness_score, issues
- `diagnosis` — priority_score, message, pain_points, recommended_features
- `pages` — list of {style, file} for built HTML pages
- `video` — script, file, provider
- `check` — QA scores and issues
- `pitch` — sent_at, sent_via, channel_results

## Environment variables required
- `ANTHROPIC_API_KEY` — for Diagnoser, Builder, Filmer (script), Checker
- `GOOGLE_MAPS_API_KEY` — for Scout
- `DID_API_KEY` — for Filmer (video); optional, falls back to script-only
- `TWILIO_*` — for Pitcher SMS/WhatsApp; optional
- `SMTP_*` — for Pitcher email; optional
