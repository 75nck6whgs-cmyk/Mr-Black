"""
Mobile Agent — Flask approval interface
Run: python -m agents.mobile.app
Open http://<your-machine-ip>:5001 on your phone.
"""
import logging
import os
import sys
from pathlib import Path
from functools import wraps

import yaml
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, jsonify, url_for, send_file

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from core.state import StateManager

load_dotenv()
logger = logging.getLogger("mobile")

_CFG_PATH = Path(__file__).resolve().parent.parent.parent / "config.yaml"
_BUILT_DIR = Path(__file__).resolve().parent.parent.parent / "state" / "built"
_FILMED_DIR = Path(__file__).resolve().parent.parent.parent / "state" / "filmed"

app = Flask(__name__)
app.secret_key = os.getenv("MOBILE_APP_SECRET", "change-me")
state = StateManager()


# ------------------------------------------------------------------
# Auth (simple token check — good enough for a private LAN app)
# ------------------------------------------------------------------

def _token_ok() -> bool:
    secret = os.getenv("MOBILE_APP_SECRET", "change-me")
    return (
        request.args.get("token") == secret
        or request.headers.get("X-Token") == secret
        or secret == "change-me"  # dev mode: no auth when secret is default
    )


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@app.route("/")
def index():
    leads = state.list_all("checked")
    stats = state.stats()
    return render_template("index.html", leads=leads, stats=stats)


@app.route("/lead/<lead_id>")
def lead_detail(lead_id):
    lead = state.load("checked", lead_id)
    if not lead:
        for stage in ("approved", "sent"):
            lead = state.load(stage, lead_id)
            if lead:
                break
    if not lead:
        abort(404)
    return render_template("lead.html", lead=lead, pages=lead.get("pages", []))


@app.route("/action/<lead_id>", methods=["POST"])
def lead_action(lead_id):
    action = request.form.get("action")
    lead = state.load("checked", lead_id)
    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    if action == "approve":
        lead["owner_note"] = request.form.get("note", "")
        state.save("approved", lead)
        state.delete("checked", lead_id)

    elif action == "reject":
        lead["rejection_reason"] = request.form.get("reason", "Owner rejected")
        state.save("rejected", lead)
        state.delete("checked", lead_id)

    elif action == "schedule":
        cfg = yaml.safe_load(_CFG_PATH.read_text())
        lead["meeting_scheduled"] = True
        state.save("approved", lead)
        state.delete("checked", lead_id)
        return redirect(cfg["agency"].get("calendly", "/"))

    else:
        return jsonify({"error": "Unknown action"}), 400

    return redirect(url_for("index"))


@app.route("/preview/<lead_id>/<style>")
def preview_page(lead_id, style):
    path = _BUILT_DIR / f"{lead_id}_{style}.html"
    if path.exists():
        return path.read_text(encoding="utf-8"), 200, {"Content-Type": "text/html"}
    abort(404)


@app.route("/video/<lead_id>")
def serve_video(lead_id):
    path = _FILMED_DIR / f"{lead_id}.mp4"
    if path.exists():
        return send_file(path, mimetype="video/mp4")
    abort(404)


@app.route("/api/stats")
def api_stats():
    return jsonify(state.stats())


@app.route("/api/approve/<lead_id>", methods=["POST"])
def api_approve(lead_id):
    """Quick approve endpoint for mobile shortcuts / Siri shortcuts."""
    lead = state.load("checked", lead_id)
    if not lead:
        return jsonify({"error": "not found"}), 404
    state.save("approved", lead)
    state.delete("checked", lead_id)
    return jsonify({"status": "approved", "id": lead_id})


# ------------------------------------------------------------------

def run():
    cfg = yaml.safe_load(_CFG_PATH.read_text())
    mobile = cfg.get("mobile", {})
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [MOBILE] %(message)s")
    app.run(
        host=mobile.get("host", "0.0.0.0"),
        port=mobile.get("port", 5001),
        debug=mobile.get("debug", False),
    )


if __name__ == "__main__":
    run()
