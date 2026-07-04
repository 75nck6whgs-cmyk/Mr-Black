#!/usr/bin/env python3
"""
Connection tester — validates all API keys before the first real run.
Run: python test_connections.py

Exit code 0 = all required services reachable.
Exit code 1 = at least one required service failed.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent))
console = Console()


def _check(label: str, required: bool, fn) -> tuple[str, str, str]:
    try:
        result = fn()
        return label, "✓", result
    except Exception as e:
        status = "✗ FAIL" if required else "— skip"
        return label, status, str(e)[:80]


# ── Individual checks ──────────────────────────────────────────────────────

def check_anthropic():
    import anthropic
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}],
    )
    return f"OK — model: claude-haiku-4-5-20251001"


def check_google_maps():
    import googlemaps
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY not set")
    gmaps = googlemaps.Client(key=key)
    result = gmaps.places(query="coffee shop in Miami, FL", page_token=None)
    count = len(result.get("results", []))
    return f"OK — {count} results for test query"


def check_did():
    import requests
    key = os.getenv("DID_API_KEY")
    if not key:
        raise ValueError("DID_API_KEY not set")
    resp = requests.get(
        "https://api.d-id.com/talks",
        headers={"Authorization": f"Basic {key}"},
        timeout=10,
    )
    resp.raise_for_status()
    return f"OK — status {resp.status_code}"


def check_twilio():
    import os
    from twilio.rest import Client
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise ValueError("TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not set")
    client = Client(sid, token)
    account = client.api.accounts(sid).fetch()
    return f"OK — account: {account.friendly_name}"


def check_smtp():
    import smtplib
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER")
    pwd = os.getenv("SMTP_PASS")
    if not all([host, user, pwd]):
        raise ValueError("SMTP_HOST/USER/PASS not set")
    with smtplib.SMTP(host, port, timeout=8) as s:
        s.starttls()
        s.login(user, pwd)
    return f"OK — {user} @ {host}:{port}"


def check_website_checker():
    from core.website_checker import check_website
    r = check_website("http://www.spacejam.com", timeout=8)
    return f"OK — spacejam score={r['oldness_score']} outdated={r['is_outdated']}"


def check_state():
    from core.state import StateManager
    s = StateManager()
    stats = s.stats()
    total = sum(stats.values())
    return f"OK — {total} items across {len(stats)} stages"


# ── Runner ─────────────────────────────────────────────────────────────────

CHECKS = [
    ("Anthropic Claude",   True,  check_anthropic),
    ("Google Maps",        True,  check_google_maps),
    ("D-ID Video API",     False, check_did),
    ("Twilio SMS/WA",      False, check_twilio),
    ("SMTP Email",         False, check_smtp),
    ("Website Checker",    True,  check_website_checker),
    ("File System State",  True,  check_state),
]


def main():
    console.print("\n[bold]Mr. Noble Agency — Connection Test[/bold]\n")

    table = Table(show_header=True, border_style="blue")
    table.add_column("Service",  style="cyan", width=22)
    table.add_column("Required", justify="center", width=10)
    table.add_column("Status",   width=8)
    table.add_column("Detail",   style="dim")

    failures = []
    for label, required, fn in CHECKS:
        _, status, detail = _check(label, required, fn)
        req_label = "[red]YES[/red]" if required else "[dim]no[/dim]"
        style = "green" if status == "✓" else ("red" if required else "yellow")
        table.add_row(label, req_label, f"[{style}]{status}[/{style}]", detail)
        if status != "✓" and required:
            failures.append(label)

    console.print(table)

    if failures:
        console.print(f"\n[red]✗ {len(failures)} required service(s) failed: {', '.join(failures)}[/red]")
        console.print("Add missing keys to your .env file and re-run.\n")
        sys.exit(1)
    else:
        console.print("\n[green]✓ All required services are connected.[/green]")
        console.print("Optional services (D-ID, Twilio, SMTP) enhance the pipeline but are not required.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
