"""
Filmer Agent
Generates a 10-second vertical promo video for each built lead via D-ID API.
Falls back to script-only mode when DID_API_KEY is not set.
"""
import logging
import os
import sys
import time
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager
from core.claude_client import ClaudeClient

load_dotenv()
logger = logging.getLogger("filmer")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
_FILMED_DIR = Path(__file__).resolve().parent.parent / "state" / "filmed"
_DID_API = "https://api.d-id.com"
_PRESENTER_IMAGE = "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/image.jpeg"

_SCRIPT_SYSTEM = (
    "Write a punchy 10-second sales script for a web design agency pitch. "
    "Max 35 words. Spoken words only — no stage directions, no quotes."
)


class Filmer:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.claude = ClaudeClient()
        self.film_cfg = self.cfg["filmer"]
        self.did_key = os.getenv("DID_API_KEY")
        _FILMED_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------

    def _generate_script(self, lead: dict) -> str:
        biz = lead["business"]
        diag = lead.get("diagnosis", {})
        prompt = (
            f"Business: {biz['name']} ({biz['type']})\n"
            f"Rating: {biz['rating']} stars, {biz['reviews']} reviews\n"
            f"Gap: {diag.get('opportunity_summary', 'no website')}\n"
            f"Offer: $400 website, ready in 48 hours\n\nScript:"
        )
        return self.claude.complete(_SCRIPT_SYSTEM, prompt, max_tokens=80).strip()

    def _create_did_video(self, script: str, lead_id: str) -> dict | None:
        headers = {
            "Authorization": f"Basic {self.did_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "script": {
                "type": "text",
                "input": script,
                "provider": {"type": "microsoft", "voice_id": self.film_cfg["voice_id"]},
            },
            "source_url": _PRESENTER_IMAGE,
            "config": {"fluent": True, "pad_audio": 0.0},
        }

        try:
            resp = requests.post(f"{_DID_API}/talks", json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            talk_id = resp.json()["id"]

            for _ in range(30):
                time.sleep(3)
                status = requests.get(f"{_DID_API}/talks/{talk_id}", headers=headers, timeout=10).json()
                if status.get("status") == "done":
                    video_url = status.get("result_url")
                    if video_url:
                        video_bytes = requests.get(video_url, timeout=60).content
                        out = _FILMED_DIR / f"{lead_id}.mp4"
                        out.write_bytes(video_bytes)
                        return {"provider": "did", "talk_id": talk_id, "file": str(out)}
                    break
                elif status.get("status") == "error":
                    logger.error(f"D-ID error: {status.get('error')}")
                    break
        except Exception as e:
            logger.error(f"D-ID API error: {e}")

        return None

    def film_lead(self, lead: dict) -> bool:
        biz = lead["business"]
        logger.info(f"Filming: {biz['name']}")

        script = self._generate_script(lead)
        logger.info(f"  Script: {script[:90]}…")

        video: dict
        if self.did_key:
            video = self._create_did_video(script, lead["id"]) or {
                "provider": "did", "status": "failed", "script": script
            }
        else:
            logger.warning("  DID_API_KEY not set — script-only mode")
            video = {"provider": "none", "status": "script_only"}

        video["script"] = script
        lead["video"] = video

        self.state.save("filmed", lead)
        self.state.delete("built", lead["id"])
        return True

    def run(self) -> int:
        leads = self.state.list_all("built")
        logger.info(f"Filming {len(leads)} leads…")
        filmed = 0
        for lead in leads:
            if self.film_lead(lead):
                filmed += 1
        logger.info(f"Filmer done — {filmed} leads filmed")
        return filmed


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [FILMER] %(message)s")
    return Filmer().run()


if __name__ == "__main__":
    run()
