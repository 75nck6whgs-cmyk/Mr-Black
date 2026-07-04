"""
Deduplicator — prevents the same business from being pitched twice.
Persists a seen-set of place_ids and phone numbers in state/seen.json.
"""
import json
from pathlib import Path

_SEEN_FILE = Path(__file__).resolve().parent.parent / "state" / "seen.json"


class Deduplicator:
    def __init__(self):
        self._data: dict = self._load()

    def _load(self) -> dict:
        if _SEEN_FILE.exists():
            try:
                return json.loads(_SEEN_FILE.read_text())
            except Exception:
                pass
        return {"place_ids": [], "phones": []}

    def _save(self):
        _SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SEEN_FILE.write_text(json.dumps(self._data, indent=2))

    def is_seen(self, place_id: str | None, phone: str | None) -> bool:
        if place_id and place_id in self._data["place_ids"]:
            return True
        if phone and phone in self._data["phones"]:
            return True
        return False

    def mark_seen(self, place_id: str | None, phone: str | None):
        changed = False
        if place_id and place_id not in self._data["place_ids"]:
            self._data["place_ids"].append(place_id)
            changed = True
        if phone and phone not in self._data["phones"]:
            self._data["phones"].append(phone)
            changed = True
        if changed:
            self._save()

    def total(self) -> int:
        return len(self._data["place_ids"])

    def reset(self):
        self._data = {"place_ids": [], "phones": []}
        self._save()
