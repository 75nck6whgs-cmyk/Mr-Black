"""
Checker Agent
QA-reviews the outreach message for each filmed lead before it reaches the
owner. Low-scoring messages get an AI-improved version. All leads advance to
state/checked/ regardless — the owner makes the final call.
"""
import logging
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager
from core.claude_client import ClaudeClient

load_dotenv()
logger = logging.getLogger("checker")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

_SYSTEM = """You are a QA specialist reviewing cold outreach messages for a web design agency.

Score the message on four dimensions (0–25 each):
1. Personalization — does it reference the specific business by name and data?
2. Value proposition — is the $400 / 48-hour offer clearly stated?
3. Tone — is it warm, human, conversational (not salesy or spammy)?
4. CTA — is there a clear, low-friction next step?

Also flag: spam trigger words, grammatical errors, excessive exclamation marks.

Return JSON only:
{
  "total_score": 82,
  "breakdown": { "personalization": 20, "value_proposition": 22, "tone": 20, "cta": 20 },
  "issues": [],
  "improved_message": "Only include if total_score < 75, otherwise omit this key.",
  "approved": true
}"""


class Checker:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.claude = ClaudeClient()

    def check_lead(self, lead: dict) -> bool:
        biz = lead["business"]
        message = lead.get("diagnosis", {}).get("message", "")

        prompt = (
            f'Message to review:\n"{message}"\n\n'
            f"Business context:\n"
            f"- Name: {biz['name']}\n"
            f"- Type: {biz['type']}\n"
            f"- Rating: {biz['rating']} stars, {biz['reviews']} reviews\n"
            f"- Has website: {biz.get('website') is not None}"
        )

        try:
            result = self.claude.json_complete(_SYSTEM, prompt)
            lead["check"] = result

            # Auto-apply improved message if score is low
            improved = result.get("improved_message")
            if improved and result.get("total_score", 100) < 75:
                lead["diagnosis"]["message"] = improved
                lead["check"]["message_auto_improved"] = True
                logger.info(f"  ↑ Message auto-improved for {biz['name']}")

            self.state.save("checked", lead)
            self.state.delete("filmed", lead["id"])
            score = result.get("total_score", "?")
            logger.info(f"  ✓ {biz['name']} QA score={score}/100")
            return True

        except Exception as e:
            logger.error(f"Check failed ({biz['name']}): {e}")
            # Save anyway so it doesn't get stuck
            lead["check"] = {"total_score": 0, "issues": [str(e)], "approved": False}
            self.state.save("checked", lead)
            self.state.delete("filmed", lead["id"])
            return False

    def run(self) -> int:
        leads = self.state.list_all("filmed")
        logger.info(f"Checking {len(leads)} leads…")
        checked = 0
        for lead in leads:
            if self.check_lead(lead):
                checked += 1
        logger.info(f"Checker done — {checked} leads reviewed")
        return checked


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [CHECKER] %(message)s")
    return Checker().run()


if __name__ == "__main__":
    run()
