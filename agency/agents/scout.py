"""
Scout Agent
Scans Google Maps city-by-city for businesses without websites (or with
outdated ones) and saves them as leads to state/leads/.
Daily target: ~220 businesses.
"""
import logging
import os
import sys
import time
from pathlib import Path

import googlemaps
import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager
from core.website_checker import check_website

load_dotenv()
logger = logging.getLogger("scout")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"

QUERY_TEMPLATES = {
    "restaurant": "restaurants",
    "salon": "hair salons",
    "barbershop": "barbershops",
    "plumber": "plumbers",
    "electrician": "electricians",
    "dentist": "dentists",
    "gym": "gyms",
    "bakery": "bakeries",
    "auto_repair": "auto repair shops",
    "cleaning_service": "cleaning services",
    "florist": "florists",
    "photographer": "photographers",
    "accountant": "accountants",
    "real_estate": "real estate agents",
}


class Scout:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.scout_cfg = self.cfg["scout"]
        self.checker_cfg = self.cfg["website_checker"]
        self.found_today = 0

        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise EnvironmentError("GOOGLE_MAPS_API_KEY is not set.")
        self.gmaps = googlemaps.Client(key=api_key)

    # ------------------------------------------------------------------

    def _get_details(self, place_id: str) -> dict:
        return self.gmaps.place(
            place_id,
            fields=[
                "name", "formatted_address", "formatted_phone_number",
                "website", "opening_hours", "types", "url",
            ],
        )["result"]

    def _qualify(self, place: dict) -> bool:
        return (
            place.get("rating", 0) >= self.scout_cfg["min_rating"]
            and place.get("user_ratings_total", 0) >= self.scout_cfg["min_reviews"]
        )

    def _process(self, place: dict, city: str, btype: str) -> bool:
        if not self._qualify(place):
            return False

        try:
            details = self._get_details(place["place_id"])
        except Exception as e:
            logger.debug(f"Details fetch failed: {e}")
            return False

        website = details.get("website")
        if website:
            check = check_website(
                website,
                timeout=self.checker_cfg["timeout"],
                user_agent=self.checker_cfg["user_agent"],
            )
            if not check["is_outdated"]:
                return False  # modern website — skip
        else:
            check = {
                "has_website": False, "is_outdated": True,
                "oldness_score": 100, "issues": ["No website"],
            }

        hours_data = details.get("opening_hours", {})
        hours_text = "; ".join(hours_data.get("weekday_text", [])[:3])

        lead = {
            "business": {
                "name": details.get("name", place.get("name", "Unknown")),
                "type": btype,
                "city": city,
                "address": details.get("formatted_address", place.get("vicinity", "")),
                "phone": details.get("formatted_phone_number"),
                "website": website,
                "rating": place.get("rating", 0),
                "reviews": place.get("user_ratings_total", 0),
                "place_id": place["place_id"],
                "google_url": details.get("url"),
                "hours": hours_text or "N/A",
                "categories": place.get("types", []),
            },
            "website_check": check,
        }

        lead_id = self.state.save("leads", lead)
        logger.info(f"  + {lead['business']['name']} [{lead_id}]")
        return True

    def scan(self, city: str, btype: str) -> int:
        query = f"{QUERY_TEMPLATES.get(btype, btype)} in {city}"
        logger.info(f"Scanning: {query}")
        found = 0

        try:
            resp = self.gmaps.places(query=query)
            places = resp.get("results", [])
            token = resp.get("next_page_token")
            limit = self.scout_cfg["max_per_city_per_type"]

            while token and len(places) < limit:
                time.sleep(2)
                next_resp = self.gmaps.places(query=query, page_token=token)
                places.extend(next_resp.get("results", []))
                token = next_resp.get("next_page_token")

            for place in places[:limit]:
                if self.found_today >= self.scout_cfg["daily_limit"]:
                    break
                if self._process(place, city, btype):
                    self.found_today += 1
                    found += 1
                time.sleep(0.3)

        except Exception as e:
            logger.error(f"Scan error ({city}/{btype}): {e}")

        return found

    def run(self) -> int:
        logger.info(f"Scout starting — target {self.scout_cfg['daily_limit']} leads/day")
        total = 0

        for city in self.scout_cfg["cities"]:
            if self.found_today >= self.scout_cfg["daily_limit"]:
                break
            for btype in self.scout_cfg["business_types"]:
                if self.found_today >= self.scout_cfg["daily_limit"]:
                    break
                total += self.scan(city, btype)
                time.sleep(0.5)

        logger.info(f"Scout done — {total} leads saved")
        return total


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [SCOUT] %(message)s")
    return Scout().run()


if __name__ == "__main__":
    run()
