#!/usr/bin/env python3
"""
CLI Approval Tool — review checked leads from the terminal.
Use this when you're not on your phone.

Usage:
  python approve.py           # interactive review
  python approve.py --all     # show all, not just first 10
  python approve.py --stats   # pipeline snapshot only
"""
import sys
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


def _display_lead(lead: dict):
    biz = lead["business"]
    diag = lead.get("diagnosis", {})
    check = lead.get("check", {})
    video = lead.get("video", {})
    pages = lead.get("pages", [])

    body = (
        f"[bold]{biz['name']}[/bold]  [dim]{biz['type']} · {biz['city']}[/dim]\n"
        f"⭐ {biz['rating']} ({biz['reviews']} reviews) · "
        f"Phone: {biz.get('phone', 'N/A')}\n"
        f"Website: {biz.get('website') or '[red]NONE[/red]'}\n\n"
        f"[yellow]Priority:[/yellow] {diag.get('priority_score', '?')}/10   "
        f"[yellow]QA:[/yellow] {check.get('total_score', '?')}/100   "
        f"[yellow]Pages:[/yellow] {len(pages)}   "
        f"[yellow]Video:[/yellow] {'✓' if video.get('file') else '✗'}\n\n"
        f"[bold green]Message:[/bold green]\n{diag.get('message', 'N/A')}\n"
    )

    if check.get("issues"):
        body += "\n[yellow]QA issues:[/yellow] " + ", ".join(check["issues"])

    if video.get("script"):
        body += f"\n\n[blue]Video script:[/blue] {video['script']}"

    if pages:
        body += f"\n\n[blue]Previews:[/blue] state/built/{lead['id']}_*.html"

    console.print(Panel(body, title=f"Lead [{lead['id']}]", border_style="blue"))


def _show_stats():
    stats = state.stats()
    table = Table(title="Pipeline State", border_style="cyan")
    table.add_column("Stage", style="cyan")
    table.add_column("Items", justify="right", style="green")
    for stage, count in stats.items():
        table.add_row(stage, str(count))
    console.print(table)


@click.command()
@click.option("--all", "show_all", is_flag=True, help="Show all leads (no limit)")
@click.option("--stats", "stats_only", is_flag=True, help="Just show pipeline stats")
@click.option("--limit", default=10, help="Max leads to review (default 10)")
def main(show_all, stats_only, limit):
    """Interactive CLI to approve or reject leads before sending."""
    _show_stats()

    if stats_only:
        return

    leads = state.list_all("checked")
    if not leads:
        console.print("\n[yellow]No leads in 'checked' — run the pipeline first:[/yellow]")
        console.print("  python orchestrate.py\n")
        return

    if not show_all:
        leads = leads[:limit]

    console.print(f"\n[bold]Reviewing {len(leads)} lead(s). Actions: a=approve  r=reject  s=skip  q=quit[/bold]\n")

    for lead in leads:
        _display_lead(lead)

        action = click.prompt(
            "Action",
            type=click.Choice(["a", "r", "s", "q"], case_sensitive=False),
            default="s",
        )

        if action == "q":
            break

        elif action == "a":
            state.save("approved", lead)
            state.delete("checked", lead["id"])
            console.print(f"[green]✓ Approved → {lead['business']['name']}[/green]\n")

        elif action == "r":
            reason = click.prompt("Reason", default="Not a good fit")
            lead["rejection_reason"] = reason
            state.save("rejected", lead)
            state.delete("checked", lead["id"])
            console.print(f"[red]✗ Rejected → {lead['business']['name']}[/red]\n")

        elif action == "s":
            console.print("[dim]Skipped[/dim]\n")

    approved = state.count("approved")
    if approved:
        console.print(f"\n[bold green]{approved} lead(s) approved and ready.[/bold green]")
        console.print("  Send them now:  python orchestrate.py pitcher\n")


if __name__ == "__main__":
    main()
