#!/usr/bin/env python3
"""Deterministic stop-and-go workflow engine.

The engine advances each work packet by no more than one state per run.
That deliberate indexing is the software equivalent of a Geneva mechanism.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TERMINAL_STATES = {"COMPLETE", "HALTED"}


@dataclass
class Packet:
    id: str
    kind: str
    payload: dict[str, Any]
    state: str = "CAPTURE"
    risk: str = "unknown"
    approved: bool = False
    attempts: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Packet":
        return cls(
            id=str(raw.get("id") or uuid.uuid4()),
            kind=str(raw.get("kind") or "generic"),
            payload=dict(raw.get("payload") or {}),
            state=str(raw.get("state") or "CAPTURE"),
            risk=str(raw.get("risk") or "unknown"),
            approved=bool(raw.get("approved", False)),
            attempts=int(raw.get("attempts", 0)),
            history=list(raw.get("history") or []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "payload": self.payload,
            "state": self.state,
            "risk": self.risk,
            "approved": self.approved,
            "attempts": self.attempts,
            "history": self.history,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def read_jsonl(path: Path) -> list[Packet]:
    if not path.exists():
        return []
    packets: list[Packet] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            packets.append(Packet.from_dict(json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
    return packets


def write_jsonl(path: Path, packets: list[Packet]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(json.dumps(packet.to_dict(), sort_keys=True) for packet in packets)
    path.write_text(body + ("\n" if body else ""), encoding="utf-8")


def append_audit(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def classify(packet: Packet, config: dict[str, Any]) -> str:
    risk_map = config.get("risk", {}).get("kind_levels", {})
    return str(risk_map.get(packet.kind, config.get("risk", {}).get("default", "medium")))


def requires_approval(packet: Packet, config: dict[str, Any]) -> bool:
    approval = config.get("approval", {})
    gated_kinds = set(approval.get("gated_kinds", []))
    gated_risks = set(approval.get("gated_risks", []))
    return packet.kind in gated_kinds or packet.risk in gated_risks


def execute_adapter(packet: Packet) -> dict[str, Any]:
    """Safe starter adapter.

    It records intended work rather than contacting an external service. Replace
    this with allow-listed adapters that implement their own idempotency keys.
    """
    return {
        "status": "simulated",
        "idempotency_key": f"{packet.id}:EXECUTE",
        "intent": packet.payload.get("action", "process"),
    }


def advance(packet: Packet, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    state = packet.state

    if state in TERMINAL_STATES:
        return state, {"reason": "terminal"}

    if state == "CAPTURE":
        required = config.get("capture", {}).get("required_payload_fields", [])
        missing = [field for field in required if field not in packet.payload]
        if missing:
            return "HALTED", {"reason": "missing_fields", "fields": missing}
        return "CLASSIFY", {"normalized": True}

    if state == "CLASSIFY":
        packet.risk = classify(packet, config)
        return "PLAN", {"risk": packet.risk}

    if state == "PLAN":
        plan = packet.payload.get("plan") or ["perform one bounded action", "verify result"]
        packet.payload["resolved_plan"] = plan
        return "APPROVE", {"plan": plan}

    if state == "APPROVE":
        if requires_approval(packet, config) and not packet.approved:
            return "APPROVE", {"reason": "approval_required"}
        return "EXECUTE", {"approval": "policy" if not packet.approved else "human"}

    if state == "EXECUTE":
        packet.attempts += 1
        max_attempts = int(config.get("execution", {}).get("max_attempts", 3))
        if packet.attempts > max_attempts:
            return "HALTED", {"reason": "max_attempts_exceeded"}
        result = execute_adapter(packet)
        packet.payload["execution_result"] = result
        return "VERIFY", result

    if state == "VERIFY":
        result = packet.payload.get("execution_result", {})
        if result.get("status") in {"simulated", "success"}:
            return "RECORD", {"verified": True}
        return "REWORK", {"verified": False}

    if state == "REWORK":
        return "PLAN", {"reason": "replanned"}

    if state == "RECORD":
        repeat = bool(packet.payload.get("repeat", False))
        return ("CAPTURE" if repeat else "COMPLETE"), {"repeat": repeat}

    return "HALTED", {"reason": "unknown_state", "state": state}


def run(config_path: Path, queue_path: Path, audit_path: Path) -> int:
    config = load_yaml(config_path)
    packets = read_jsonl(queue_path)

    moved = 0
    for packet in packets:
        before = packet.state
        after, detail = advance(packet, config)
        packet.state = after
        event = {
            "timestamp": utc_now(),
            "packet_id": packet.id,
            "kind": packet.kind,
            "from": before,
            "to": after,
            "payload_hash": stable_hash(packet.payload),
            "detail": detail,
        }
        packet.history.append(event)
        append_audit(audit_path, event)
        if before != after:
            moved += 1

    write_jsonl(queue_path, packets)
    print(json.dumps({"packets": len(packets), "moved": moved, "queue": str(queue_path)}))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Advance each Geneva work packet one state")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--audit", type=Path, default=Path("geneva_loop/audit.jsonl"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        sys.exit(run(args.config, args.queue, args.audit))
    except Exception as exc:  # safe stop with visible failure
        print(f"Geneva loop halted: {exc}", file=sys.stderr)
        sys.exit(1)
