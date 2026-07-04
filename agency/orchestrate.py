#!/usr/bin/env python3
"""
Mr. Noble Agency — Orchestrator
Runs the full pipeline or individual agents.

Usage:
  python orchestrate.py              # full pipeline (scout→checker)
  python orchestrate.py scout        # single agent
  python orchestrate.py --skip scout # skip one agent
  python orchestrate.py pitcher      # send approved leads
"""
import logging
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

console = Console()

PIPELINE = ["scout", "diagnoser", "builder", "filmer", "checker"]

AGENT_DESCRIPTIONS = {
    "scout":     "Scan Google Maps — find businesses without websites",
    "diagnoser": "Score leads + generate personalized sales messages",
    "builder":   "Build 3 landing page variations per top lead",
    "filmer":    "Create 10-second promo video per lead",
    "checker":   "QA-review messages before owner approval",
    "pitcher":   "Send approved leads via WhatsApp / SMS / Email / Instagram",
    "followup":  "Re-engage sent leads that haven't responded in N days",
}


def _import_agent(name: str):
    if name == "scout":
        from agents.scout import run
    elif name == "diagnoser":
        from agents.diagnoser import run
    elif name == "builder":
        from agents.builder import run
    elif name == "filmer":
        from agents.filmer import run
    elif name == "checker":
        from agents.checker import run
    elif name == "pitcher":
        from agents.pitcher import run
    elif name == "followup":
        from agents.followup import run
    else:
        raise ValueError(f"Unknown agent: {name}")
    return run


def run_agent(name: str) -> int:
    console.print(f"\n[bold cyan]▶  {name.upper()}[/bold cyan]  [dim]{AGENT_DESCRIPTIONS.get(name, '')}[/dim]")
    t0 = datetime.now()
    run = _import_agent(name)
    result = run()
    elapsed = (datetime.now() - t0).seconds
    console.print(f"[green]   ✓ done in {elapsed}s — {result} items processed[/green]")
    return result


def print_stats():
    from core.state import StateManager
    stats = StateManager().stats()
    table = Table(title="Pipeline State", border_style="blue", show_header=True)
    table.add_column("Stage", style="cyan")
    table.add_column("Items", style="green", justify="right")
    for stage, count in stats.items():
        style = "bold green" if count > 0 else "dim"
        table.add_row(stage, str(count), style=style)
    console.print("\n")
    console.print(table)


@click.command()
@click.argument("agent", required=False, default="all")
@click.option("--skip", "-s", multiple=True, help="Agent(s) to skip")
@click.option("--verbose", "-v", is_flag=True, help="Debug logging")
def main(agent, skip, verbose):
    """
    Mr. Noble Agency Automation Orchestrator.

    \b
    AGENT choices: all | scout | diagnoser | builder | filmer | checker | pitcher | followup
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(name)s %(message)s")

    console.print(Panel(
        "[bold white]Mr. Noble Agency Automation[/bold white]\n"
        "[dim]7-agent website sales pipeline[/dim]",
        border_style="cyan",
    ))

    if agent == "all":
        agents_to_run = [a for a in PIPELINE if a not in skip]
    else:
        agents_to_run = [agent]

    console.print(f"[dim]Running: {', '.join(agents_to_run)}[/dim]")

    for a in agents_to_run:
        try:
            run_agent(a)
        except Exception as e:
            console.print(f"[red]✗ {a} failed: {e}[/red]")
            if verbose:
                import traceback
                traceback.print_exc()

    print_stats()

    pending = __import__("core.state", fromlist=["StateManager"]).StateManager().count("checked")
    if pending:
        console.print(
            f"\n[bold yellow]⚡ {pending} lead(s) waiting for your approval.[/bold yellow]\n"
            f"   Mobile app:  python -m agents.mobile.app\n"
            f"   CLI review:  python approve.py"
        )
    else:
        console.print("\n[dim]No leads awaiting approval.[/dim]")


if __name__ == "__main__":
    main()
