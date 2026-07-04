#!/usr/bin/env python3
"""
Revenue Tracker — mark leads as paying clients and view income stats.

Commands:
  python revenue.py list              # show all sent/approved leads
  python revenue.py paid <id>         # mark a lead as paid ($400)
  python revenue.py paid <id> --amount 600   # custom amount
  python revenue.py stats             # revenue summary
  python revenue.py dashboard         # full pipeline + revenue view
"""
import json
import sys
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent))
from core.state import StateManager

console = Console()
state = StateManager()

_REVENUE_FILE = Path(__file__).resolve().parent / "state" / "revenue.json"


def _load_revenue() -> dict:
    if _REVENUE_FILE.exists():
        return json.loads(_REVENUE_FILE.read_text())
    return {"clients": [], "total": 0}


def _save_revenue(data: dict):
    _REVENUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _REVENUE_FILE.write_text(json.dumps(data, indent=2))


def _find_lead(lead_id: str) -> tuple[str, dict] | tuple[None, None]:
    for stage in ["sent", "approved", "checked"]:
        lead = state.load(stage, lead_id)
        if lead:
            return stage, lead
    return None, None


# ── Commands ───────────────────────────────────────────────────────────────

@click.group()
def cli():
    """Mr. Noble Agency — Revenue Tracker"""


@cli.command("list")
@click.option("--stage", default="sent", help="Stage to list (sent/approved/checked)")
def list_leads(stage):
    """List leads eligible to be marked as paid."""
    leads = state.list_all(stage)
    revenue = _load_revenue()
    paid_ids = {c["lead_id"] for c in revenue["clients"]}

    table = Table(title=f"Leads in '{stage}' stage", border_style="blue")
    table.add_column("ID", style="dim", width=10)
    table.add_column("Business", style="cyan")
    table.add_column("City")
    table.add_column("Rating", justify="right")
    table.add_column("Sent via")
    table.add_column("Status", justify="center")

    for lead in leads:
        biz = lead["business"]
        sent_via = ", ".join(lead.get("pitch", {}).get("sent_via", ["—"]))
        paid = "💰 PAID" if lead["id"] in paid_ids else ""
        table.add_row(
            lead["id"], biz["name"], biz["city"],
            f"⭐ {biz['rating']}", sent_via, paid,
        )

    console.print(table)
    console.print(f"\n[dim]To mark as paid:  python revenue.py paid <ID>[/dim]")


@cli.command("paid")
@click.argument("lead_id")
@click.option("--amount", default=400, help="Payment amount (default: $400)")
@click.option("--note", default="", help="Optional note")
def mark_paid(lead_id, amount, note):
    """Mark a lead as a paying client."""
    stage, lead = _find_lead(lead_id)
    if not lead:
        console.print(f"[red]Lead {lead_id} not found in sent/approved/checked stages.[/red]")
        sys.exit(1)

    revenue = _load_revenue()
    if any(c["lead_id"] == lead_id for c in revenue["clients"]):
        console.print(f"[yellow]{lead_id} is already marked as paid.[/yellow]")
        return

    biz = lead["business"]
    entry = {
        "lead_id": lead_id,
        "business_name": biz["name"],
        "business_type": biz["type"],
        "city": biz["city"],
        "amount": amount,
        "paid_at": datetime.utcnow().isoformat(),
        "note": note,
    }
    revenue["clients"].append(entry)
    revenue["total"] = sum(c["amount"] for c in revenue["clients"])
    _save_revenue(revenue)

    # Also tag the lead in state
    lead["client"] = {"paid": True, "amount": amount, "paid_at": entry["paid_at"]}
    state.save(stage, lead)

    console.print(
        Panel(
            f"[bold green]💰 Payment recorded[/bold green]\n\n"
            f"Client:  {biz['name']}\n"
            f"Amount:  [bold]${amount}[/bold]\n"
            f"Total revenue to date:  [bold green]${revenue['total']:,}[/bold green]",
            border_style="green",
        )
    )


@cli.command("stats")
def stats():
    """Show revenue summary."""
    revenue = _load_revenue()
    clients = revenue["clients"]
    total = revenue["total"]
    count = len(clients)

    pipeline = state.stats()
    sent_count = pipeline["sent"] + pipeline["approved"]

    conversion = (count / sent_count * 100) if sent_count else 0
    monthly_target = 47 * 400
    api_cost = 480
    net = total - api_cost

    console.print(
        Panel(
            f"[bold]Revenue Summary[/bold]\n\n"
            f"Paying clients:    [bold cyan]{count}[/bold cyan]\n"
            f"Total revenue:     [bold green]${total:,}[/bold green]\n"
            f"API cost (est.):   [dim]$480/mo[/dim]\n"
            f"Net profit:        [bold green]${net:,}[/bold green]\n\n"
            f"Pitches sent:      {sent_count}\n"
            f"Conversion rate:   {conversion:.1f}%\n\n"
            f"Monthly target:    47 clients × $400 = ${monthly_target:,}\n"
            f"Progress:          {count}/47 clients this cycle",
            border_style="blue",
            title="💰 Mr. Noble Agency",
        )
    )

    if clients:
        table = Table(title="Paid Clients", border_style="green")
        table.add_column("Business", style="cyan")
        table.add_column("City")
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Date")
        for c in clients:
            table.add_row(
                c["business_name"], c["city"],
                f"${c['amount']}", c["paid_at"][:10],
            )
        console.print(table)


@cli.command("dashboard")
def dashboard():
    """Full pipeline + revenue view."""
    pipeline = state.stats()
    revenue = _load_revenue()

    table = Table(title="Full Pipeline + Revenue", border_style="cyan")
    table.add_column("Stage", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for stage, count in pipeline.items():
        style = "bold green" if count > 0 else "dim"
        table.add_row(stage, str(count), style=style)

    table.add_section()
    table.add_row("paying clients", str(len(revenue["clients"])), style="bold green")
    table.add_row("total revenue", f"${revenue['total']:,}", style="bold green")

    console.print(table)


if __name__ == "__main__":
    cli()
