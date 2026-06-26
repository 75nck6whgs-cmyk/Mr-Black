"""
Pitcher Agent
Sends approved leads via WhatsApp → SMS → Email (first channel that works).
Respects a 30-message/day cap. Moves sent leads to state/sent/.
"""
import logging
import os
import smtplib
import sys
from datetime import date, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import yaml
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.state import StateManager

load_dotenv()
logger = logging.getLogger("pitcher")

_CFG_PATH = Path(__file__).resolve().parent.parent / "config.yaml"


class Pitcher:
    def __init__(self):
        self.cfg = yaml.safe_load(_CFG_PATH.read_text())
        self.state = StateManager()
        self.pitch_cfg = self.cfg["pitcher"]
        self.agency = self.cfg["agency"]
        self.sent_today = self._count_sent_today()
        self._twilio = None

    @property
    def twilio(self):
        if self._twilio is None:
            sid = os.getenv("TWILIO_ACCOUNT_SID")
            token = os.getenv("TWILIO_AUTH_TOKEN")
            if sid and token:
                from twilio.rest import Client
                self._twilio = Client(sid, token)
        return self._twilio

    # ------------------------------------------------------------------

    def _count_sent_today(self) -> int:
        today = str(date.today())
        return sum(1 for l in self.state.list_all("sent") if l.get("sent_at", "").startswith(today))

    def _send_whatsapp(self, phone: str, message: str) -> dict:
        if not self.twilio or not phone:
            return {"status": "skipped", "reason": "no twilio or no phone"}
        wa_to = phone if phone.startswith("whatsapp:") else f"whatsapp:{phone}"
        try:
            msg = self.twilio.messages.create(
                body=message,
                from_=os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
                to=wa_to,
            )
            return {"status": "sent", "sid": msg.sid}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _send_sms(self, phone: str, message: str) -> dict:
        if not self.twilio or not phone:
            return {"status": "skipped", "reason": "no twilio or no phone"}
        try:
            msg = self.twilio.messages.create(
                body=message,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=phone,
            )
            return {"status": "sent", "sid": msg.sid}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _send_email(self, email_addr: str, biz_name: str, message: str) -> dict:
        host = os.getenv("SMTP_HOST")
        user = os.getenv("SMTP_USER")
        pwd = os.getenv("SMTP_PASS")
        if not all([host, user, pwd, email_addr]):
            return {"status": "skipped", "reason": "missing smtp config"}
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Free website mockup for {biz_name}"
            msg["From"] = user
            msg["To"] = email_addr
            msg.attach(MIMEText(message, "plain"))
            msg.attach(MIMEText(f"<p>{message.replace(chr(10), '<br>')}</p>", "html"))
            with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", 587))) as s:
                s.starttls()
                s.login(user, pwd)
                s.sendmail(user, email_addr, msg.as_string())
            return {"status": "sent"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # ------------------------------------------------------------------

    def pitch_lead(self, lead: dict) -> bool:
        if self.sent_today >= self.pitch_cfg["daily_limit"]:
            logger.warning(f"Daily limit ({self.pitch_cfg['daily_limit']}) reached — stopping")
            return False

        biz = lead["business"]
        message = lead.get("diagnosis", {}).get("message", "")
        channels = self.pitch_cfg.get("channels", ["sms"])

        sent_via: list[str] = []
        channel_results: dict = {}

        for ch in channels:
            if ch == "whatsapp" and biz.get("phone"):
                r = self._send_whatsapp(biz["phone"], message)
                channel_results["whatsapp"] = r
                if r["status"] == "sent":
                    sent_via.append("whatsapp")
                    break

            elif ch == "sms" and biz.get("phone"):
                r = self._send_sms(biz["phone"], message)
                channel_results["sms"] = r
                if r["status"] == "sent":
                    sent_via.append("sms")
                    break

            elif ch == "email" and biz.get("email"):
                r = self._send_email(biz["email"], biz["name"], message)
                channel_results["email"] = r
                if r["status"] == "sent":
                    sent_via.append("email")
                    break

        lead["pitch"] = {
            "sent_at": datetime.utcnow().isoformat(),
            "sent_via": sent_via,
            "channel_results": channel_results,
            "message_sent": message,
        }

        self.state.save("sent", lead)
        self.state.delete("approved", lead["id"])
        self.sent_today += 1

        status = f"via {sent_via}" if sent_via else "queued (no contact info)"
        logger.info(f"  ✓ {biz['name']} pitched {status}")
        return True

    def run(self) -> int:
        leads = self.state.list_all("approved")
        logger.info(f"Pitching {len(leads)} approved leads (sent today: {self.sent_today})…")
        pitched = 0
        for lead in leads:
            if not self.pitch_lead(lead):
                break
            pitched += 1
        logger.info(f"Pitcher done — {pitched} pitches sent")
        return pitched


def run() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [PITCHER] %(message)s")
    return Pitcher().run()


if __name__ == "__main__":
    run()
