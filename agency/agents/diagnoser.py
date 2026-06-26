"""
Diagnoser Agent
Scores each raw lead and generates a personalized sales message.
High-scoring leads move to state/diagnosed/; the rest go to state/rejected/.
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
logger = logging.getLogger("diagnoser")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

_SYSTEM = """You are a sales strategist for a boutique web design agency.
Analyze this local business lead and return JSON only — no prose, no fences.

Score criteria (1-10):
• Rating + review volume → social proof already exists
• Missing/outdated website → pain is real, urgency is high
• Business type → some types convert better (restaurants, salons, dentists)

Return exactly this structure:
{
  "priority_score": 8,
  "opportunity_summary": "One sentence why this is a good prospect.",
  "pain_points": ["pain 1", "pain 2", "pain 3"],
  "recommended_features": ["feature 1", "feature 2", "feature 3"],
  "message": "The outreach message (2-3 sentences, warm, specific, non-pushy)."
}

Message requirements:
- Open with the business name and a specific compliment (rating/reviews)
- State the gap (no website / outdated site)
- Offer a free mockup and mention $400 / 48-hour delivery
- End with a soft question, not a hard sell"""


class Diagnoser:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.claude = ClaudeClient()
        self.diag_cfg = self.cfg["diagnoser"]
        self.agency = self.cfg["agency"]

    def _prompt(self, lead: dict) -> str:
        biz = lead["business"]
        issues = ", ".join(lead["website_check"].get("issues", ["No website"]))
        return f"""Business: {biz['name']}
Type: {biz['type']}
City: {biz['city']}
Address: {biz['address']}
Phone: {biz.get('phone', 'N/A')}
Rating: {biz['rating']} stars ({biz['reviews']} reviews)
Current website: {biz.get('website') or 'NONE'}
Website issues: {issues}
Hours: {biz.get('hours', 'N/A')}

Agency offer: ${self.agency['price']} flat, {self.agency['delivery_hours']}-hour delivery, free mockup first."""

    def diagnose(self, lead: dict) -> dict | None:
        try:
            result = self.claude.json_complete(_SYSTEM, self._prompt(lead))
            lead["diagnosis"] = result
            return lead
        except Exception as e:
            logger.error(f"Diagnosis failed ({lead['business']['name']}): {e}")
            return None

    def run(self) -> int:
        leads = self.state.list_all("leads")
        logger.info(f"Diagnosing {len(leads)} raw leads…")
        diagnosed = 0

        for lead in leads:
            lid = lead["id"]
            result = self.diagnose(lead)

            if not result:
                continue

            score = result["diagnosis"].get("priority_score", 0)
            if score >= self.diag_cfg["min_score"]:
                self.state.save("diagnosed", result)
                self.state.delete("leads", lid)
                diagnosed += 1
                logger.info(f"  ✓ {lead['business']['name']} score={score}")
            else:
                lead["rejection_reason"] = f"Low score: {score}"
                self.state.save("rejected", lead)
                self.state.delete("leads", lid)
                logger.debug(f"  ✗ {lead['business']['name']} score={score}")

        # Keep only the top-k for building
        top_k = self.diag_cfg.get("top_k", 999)
        all_diagnosed = self.state.list_all("diagnosed")
        if len(all_diagnosed) > top_k:
            ranked = sorted(
                all_diagnosed,
                key=lambda x: x.get("diagnosis", {}).get("priority_score", 0),
                reverse=True,
            )
            for overflow in ranked[top_k:]:
                overflow["rejection_reason"] = "Outside top_k"
                self.state.save("rejected", overflow)
                self.state.delete("diagnosed", overflow["id"])

        logger.info(f"Diagnoser done — {diagnosed} leads diagnosed")
        return diagnosed


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [DIAGNOSER] %(message)s")
    return Diagnoser().run()


if __name__ == "__main__":
    run()
