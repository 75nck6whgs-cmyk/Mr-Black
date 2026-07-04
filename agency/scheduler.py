#!/usr/bin/env python3
"""
Daily scheduler — keeps the pipeline running automatically without cron.
Run once and leave it in the background (tmux / screen / nohup).

  nohup python scheduler.py &

Default schedule:
  06:00  Full pipeline (scout → checker)
  07:00  Send approved leads (pitcher)
  18:00  Re-engage old leads (followup → pitcher)

Edit SCHEDULE below to change times.
"""
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parent))

console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER] %(message)s",
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("scheduler")


def _run(agent: str):
    from orchestrate import run_agent
    logger.info(f"Firing: {agent}")
    try:
        count = run_agent(agent)
        logger.info(f"{agent} done — {count} items")
    except Exception as e:
        logger.error(f"{agent} failed: {e}")


def morning_pipeline():
    """06:00 — scout → diagnoser → builder → filmer → checker"""
    logger.info("=== MORNING PIPELINE START ===")
    for agent in ["scout", "diagnoser", "builder", "filmer", "checker"]:
        _run(agent)
    from core.state import StateManager
    pending = StateManager().count("checked")
    logger.info(f"Morning pipeline done — {pending} leads awaiting approval")
    if pending:
        console.print(
            f"\n[bold yellow]⚡ {pending} lead(s) need your approval.[/bold yellow]\n"
            f"   Open: http://localhost:5001\n"
            f"   Or run: python approve.py\n"
        )


def morning_pitcher():
    """07:00 — send whatever was approved overnight"""
    logger.info("=== MORNING PITCHER ===")
    _run("pitcher")


def evening_followup():
    """18:00 — re-engage leads that went cold + send them"""
    logger.info("=== EVENING FOLLOW-UP ===")
    _run("followup")
    _run("pitcher")


# ── Schedule ───────────────────────────────────────────────────────────────

SCHEDULE = {
    "06:00": morning_pipeline,
    "07:00": morning_pitcher,
    "18:00": evening_followup,
}


def main():
    console.print(
        "\n[bold cyan]Mr. Noble Agency Scheduler[/bold cyan]\n"
        "[dim]Running in background. Press Ctrl+C to stop.[/dim]\n"
    )

    for time_str, fn in SCHEDULE.items():
        schedule.every().day.at(time_str).do(fn)
        console.print(f"  {time_str} → {fn.__doc__.strip()}")

    console.print(f"\n[dim]Scheduler started at {datetime.now().strftime('%H:%M')}[/dim]\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
