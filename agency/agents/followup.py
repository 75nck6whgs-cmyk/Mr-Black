"""
Follow-up Agent
Re-engages leads that were sent N days ago but never responded.
Reads state/sent/, generates a warmer second-touch message via Claude,
and moves qualifying leads back to state/approved/ for Pitcher to re-send.

Run: python orchestrate.py followup
"""
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager
from core.claude_client import ClaudeClient

load_dotenv()
logger = logging.getLogger("followup")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

_SYSTEM = """You are writing a warm, brief follow-up message for a web agency.
The business was contacted a few days ago but hasn't responded.

Rules:
- 1-2 sentences max
- Acknowledge you reached out before
- Add ONE new hook (a question, a different angle, or a quick win offer)
- Never be pushy or guilt-trip them
- End with a soft question

Return only the message text — no quotes, no JSON."""


class FollowUp:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.claude = ClaudeClient()
        self.follow_up_days = self.cfg["pitcher"].get("follow_up_days", 3)
        self.max_followups = 2

    def _is_eligible(self, lead: dict) -> bool:
        sent_at_str = lead.get("pitch", {}).get("sent_at", "")
        if not sent_at_str:
            return False

        sent_at = datetime.fromisoformat(sent_at_str)
        days_since = (datetime.utcnow() - sent_at).days

        follow_up_count = lead.get("follow_up_count", 0)
        if follow_up_count >= self.max_followups:
            return False

        return days_since >= self.follow_up_days

    def _generate_followup_message(self, lead: dict) -> str:
        biz = lead["business"]
        original = lead.get("diagnosis", {}).get("message", "")
        follow_up_count = lead.get("follow_up_count", 0)

        angles = [
            "mention they could be losing X customers/month without a website",
            "offer to send the mockup right now with no strings attached",
        ]
        angle = angles[min(follow_up_count, len(angles) - 1)]

        prompt = (
            f"Business: {biz['name']} ({biz['type']}, {biz['city']})\n"
            f"Rating: {biz['rating']} stars, {biz['reviews']} reviews\n"
            f"Original message sent:\n\"{original}\"\n\n"
            f"Days since first contact: {self.follow_up_days}\n"
            f"Follow-up angle to use: {angle}\n\n"
            f"Write the follow-up:"
        )

        try:
            return self.claude.complete(_SYSTEM, prompt, max_tokens=120).strip()
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return (
                f"Hi again! Just wanted to follow up on my message about {biz['name']}. "
                f"I'd love to send you a free mockup — no commitment needed. "
                f"Would that be helpful?"
            )

    def run(self) -> int:
        sent_leads = self.state.list_all("sent")
        eligible = [l for l in sent_leads if self._is_eligible(l)]
        logger.info(f"Follow-up: {len(sent_leads)} sent, {len(eligible)} eligible for re-contact")

        queued = 0
        for lead in eligible:
            biz = lead["business"]
            new_message = self._generate_followup_message(lead)

            lead["diagnosis"]["message"] = new_message
            lead["follow_up_count"] = lead.get("follow_up_count", 0) + 1
            lead["follow_up_at"] = datetime.utcnow().isoformat()

            self.state.save("approved", lead)
            self.state.delete("sent", lead["id"])
            queued += 1
            logger.info(
                f"  → {biz['name']} queued for follow-up #{lead['follow_up_count']}"
            )

        logger.info(f"Follow-up done — {queued} leads re-queued")
        return queued


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [FOLLOWUP] %(message)s")
    return FollowUp().run()


if __name__ == "__main__":
    run()
