"""Shared file-system state manager. All agents read/write through this."""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

STAGES = ["leads", "diagnosed", "built", "filmed", "checked", "approved", "rejected", "sent"]

_BASE = Path(__file__).resolve().parent.parent / "state"


class StateManager:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base = Path(base_dir) if base_dir else _BASE
        for stage in STAGES:
            (self.base / stage).mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def save(self, stage: str, lead: dict) -> str:
        if "id" not in lead:
            lead["id"] = str(uuid.uuid4())[:8]
        lead.setdefault("created_at", datetime.utcnow().isoformat())
        lead["updated_at"] = datetime.utcnow().isoformat()
        lead["stage"] = stage
        path = self.base / stage / f"{lead['id']}.json"
        path.write_text(json.dumps(lead, indent=2, ensure_ascii=False))
        return lead["id"]

    def load(self, stage: str, lead_id: str) -> Optional[dict]:
        path = self.base / stage / f"{lead_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list_all(self, stage: str) -> list[dict]:
        results = []
        for f in sorted((self.base / stage).glob("*.json"), key=lambda x: x.stat().st_mtime):
            try:
                results.append(json.loads(f.read_text()))
            except Exception:
                pass
        return results

    def move(self, from_stage: str, to_stage: str, lead_id: str) -> dict:
        lead = self.load(from_stage, lead_id)
        if not lead:
            raise FileNotFoundError(f"Lead {lead_id} not in {from_stage}")
        self.save(to_stage, lead)
        (self.base / from_stage / f"{lead_id}.json").unlink(missing_ok=True)
        return lead

    def delete(self, stage: str, lead_id: str) -> None:
        (self.base / stage / f"{lead_id}.json").unlink(missing_ok=True)

    def count(self, stage: str) -> int:
        return len(list((self.base / stage).glob("*.json")))

    def stats(self) -> dict:
        return {stage: self.count(stage) for stage in STAGES}

    def exists(self, stage: str, lead_id: str) -> bool:
        return (self.base / stage / f"{lead_id}.json").exists()
