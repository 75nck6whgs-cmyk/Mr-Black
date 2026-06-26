"""
Builder Agent
Generates 3 complete, self-contained HTML landing page variations for each
diagnosed lead using Claude. Pages are saved to state/built/<id>_<style>.html.
"""
import logging
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager
from core.claude_client import ClaudeClient

load_dotenv()
logger = logging.getLogger("builder")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"
_BUILT_DIR = Path(__file__).resolve().parent.parent / "state" / "built"

STYLES = {
    "modern": {
        "palette": "#2563EB (primary blue), #F8FAFC (background), #1E293B (text)",
        "vibe": "Clean, minimal, tech-forward. Lots of whitespace, sharp edges, subtle shadows.",
        "fonts": "Inter (headings), Roboto (body) — load via Google Fonts @import",
    },
    "elegant": {
        "palette": "#1a1a1a (background), #C9A84C (gold accents), #FAF9F6 (text)",
        "vibe": "Sophisticated, dark luxury feel. Gold accents, generous padding, refined typography.",
        "fonts": "Playfair Display (headings), Lato (body) — load via Google Fonts @import",
    },
    "bold": {
        "palette": "#E63946 (primary red), #1D3557 (navy), #F1FAEE (light background)",
        "vibe": "Energetic, high-contrast, strong typography. Bold CTAs, vivid section dividers.",
        "fonts": "Montserrat (headings), Open Sans (body) — load via Google Fonts @import",
    },
}

_SYSTEM = """You are an expert web designer producing stunning local business websites.

Rules:
- Output ONLY the complete HTML document starting with <!DOCTYPE html>
- All CSS must be inline in a <style> tag — no external CSS links
- Google Fonts are allowed via @import inside the <style> tag
- Use picsum.photos for placeholder images (e.g. https://picsum.photos/seed/cafe/800/500)
- Must include: hero, about/features, services/menu preview, contact info, CTA button
- Fully responsive (mobile-first with media queries)
- The page must look professionally designed and visually impressive
- No Lorem Ipsum — write real placeholder content relevant to the business type"""


def _build_prompt(lead: dict, style: str, agency_name: str) -> str:
    biz = lead["business"]
    diag = lead.get("diagnosis", {})
    s = STYLES[style]
    features = "\n".join(f"- {f}" for f in diag.get("recommended_features", []))
    return f"""Create a landing page for this business:

Name: {biz['name']}
Type: {biz['type']}
City: {biz['city']}
Address: {biz['address']}
Phone: {biz.get('phone', 'Call us')}
Rating: {biz['rating']} ⭐  ({biz['reviews']} reviews)
Hours: {biz.get('hours', '')}

Key features to highlight:
{features}

Design style: {style}
Color palette: {s['palette']}
Visual vibe: {s['vibe']}
Typography: {s['fonts']}

Footer note: "Demo site created by {agency_name} — want yours? $400, ready in 48 hours."
CTA button should link to: tel:{biz.get('phone', '')}

Make it beautiful. Make the owner proud."""


class Builder:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.claude = ClaudeClient()
        self.build_cfg = self.cfg["builder"]
        self.agency_name = self.cfg["agency"]["name"]
        _BUILT_DIR.mkdir(parents=True, exist_ok=True)

    def _build_style(self, lead: dict, style: str) -> str | None:
        try:
            html = self.claude.complete(
                _SYSTEM,
                _build_prompt(lead, style, self.agency_name),
                max_tokens=8192,
            )
            # Strip any accidental markdown fences
            html = re.sub(r"^```html?\n?", "", html.strip())
            html = re.sub(r"\n?```$", "", html.strip())
            return html
        except Exception as e:
            logger.error(f"Build failed ({lead['business']['name']}, {style}): {e}")
            return None

    def build_lead(self, lead: dict) -> bool:
        biz = lead["business"]
        logger.info(f"Building pages for: {biz['name']}")
        pages = []

        for style in self.build_cfg["styles"][: self.build_cfg["variations"]]:
            html = self._build_style(lead, style)
            if not html:
                continue
            filename = f"{lead['id']}_{style}.html"
            filepath = _BUILT_DIR / filename
            filepath.write_text(html, encoding="utf-8")
            pages.append({"style": style, "file": str(filepath), "vibe": STYLES[style]["vibe"]})
            logger.info(f"  + {style} page ({len(html):,} chars)")

        if not pages:
            return False

        lead["pages"] = pages
        self.state.save("built", lead)
        self.state.delete("diagnosed", lead["id"])
        return True

    def run(self) -> int:
        leads = self.state.list_all("diagnosed")
        logger.info(f"Building pages for {len(leads)} leads…")
        built = 0
        for lead in leads:
            if self.build_lead(lead):
                built += 1
        logger.info(f"Builder done — {built} leads built")
        return built


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [BUILDER] %(message)s")
    return Builder().run()


if __name__ == "__main__":
    run()
