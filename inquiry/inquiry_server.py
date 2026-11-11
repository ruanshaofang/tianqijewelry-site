#!/usr/bin/env python3
"""Tianqi Jewelry inquiry receiver.

Listens on 127.0.0.1:8788 behind Nginx at POST /api/inquiry.
Every inquiry is appended to a JSON-lines file first (so nothing is lost),
then emailed to the sales inbox if SMTP settings are present.

Settings come from environment variables (set in /etc/tianqi-inquiry.env,
never committed to git):
  INQ_SMTP_HOST, INQ_SMTP_PORT (465 = SSL, 587 = STARTTLS),
  INQ_SMTP_USER, INQ_SMTP_PASS, INQ_MAIL_TO (default info@tianqijewelry.com),
  INQ_DATA (default /var/lib/tianqi-inquiry/inquiries.jsonl)
Python standard library only.
"""
import json
import os
import re
import smtplib
import ssl
import threading
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST, PORT = "127.0.0.1", int(os.environ.get("INQ_PORT", "8788"))
DATA = os.environ.get("INQ_DATA", "/var/lib/tianqi-inquiry/inquiries.jsonl")
MAIL_TO = os.environ.get("INQ_MAIL_TO", "info@tianqijewelry.com")
SMTP_HOST = os.environ.get("INQ_SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("INQ_SMTP_PORT", "465"))
SMTP_USER = os.environ.get("INQ_SMTP_USER", "")
SMTP_PASS = os.environ.get("INQ_SMTP_PASS", "")

FIELDS = {  # name: max length
    "type": 40, "name": 120, "company": 160, "email": 200, "country": 80,
    "pearl": 120, "qty": 200, "lang": 10, "message": 5000, "page": 300,
}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_lock = threading.Lock()
_hits = {}  # ip -> [timestamps], simple rate limit


def rate_limited(ip, limit=5, window=600):
    now = time.time()
    with _lock:
        recent = [t for t in _hits.get(ip, []) if now - t < window]
        recent.append(now)
        _hits[ip] = recent
        return len(recent) > limit


def save(rec):
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    with _lock, open(DATA, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def send_mail(rec):
    if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
        return "skipped (no SMTP settings)"
    msg = EmailMessage()
    msg["Subject"] = f"[Website inquiry] {rec.get('type','')} — {rec['name']} ({rec.get('country','')})"
    msg["From"] = formataddr(("Tianqi Website", SMTP_USER))
    msg["To"] = MAIL_TO
    msg["Reply-To"] = rec["email"]
    labels = [("Partnership", "type"), ("Name", "name"), ("Company", "company"),
              ("Email", "email"), ("Country", "country"), ("Pearl type", "pearl"),
              ("Quantity / budget", "qty"), ("Site language", "lang"), ("Page", "page"),
              ("Received (UTC)", "received"), ("IP", "ip")]
    body = "\n".join(f"{k}: {rec.get(v) or '-'}" for k, v in labels)
    body += "\n\nDetails:\n" + (rec.get("message") or "-")
    body += "\n\n— Reply to this email to answer the buyer directly."
    msg.set_content(body)
    ctx = ssl.create_default_context()
    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=20) as s:
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
    return "sent"


class Handler(BaseHTTPRequestHandler):
    server_version = "TianqiInquiry/1.0"

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):  # quieter journal
        print("%s %s" % (self.address_string(), fmt % args), flush=True)

    def do_GET(self):
        if self.path.rstrip("/") == "/api/inquiry/health":
            return self._json(200, {"ok": True, "mail": bool(SMTP_HOST)})
        self._json(404, {"ok": False})

    def do_POST(self):
        if self.path.rstrip("/") != "/api/inquiry":
            return self._json(404, {"ok": False})
        ip = self.headers.get("X-Real-IP") or self.headers.get("X-Forwarded-For", "").split(",")[0].strip() or self.client_address[0]
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > 20000:
                return self._json(400, {"ok": False, "error": "size"})
            raw = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            return self._json(400, {"ok": False, "error": "json"})
        if raw.get("website"):  # honeypot field filled = bot; pretend success
            return self._json(200, {"ok": True})
        rec = {k: str(raw.get(k, "")).strip()[:n] for k, n in FIELDS.items()}
        if not rec["name"] or not EMAIL_RE.match(rec["email"]):
            return self._json(400, {"ok": False, "error": "fields"})
        if rate_limited(ip):
            return self._json(429, {"ok": False, "error": "rate"})
        rec["received"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        rec["ip"] = ip
        try:
            save(rec)
        except Exception as e:
            print("SAVE FAILED", e, flush=True)
            return self._json(500, {"ok": False, "error": "save"})
        try:
            rec_status = send_mail(rec)
        except Exception as e:
            rec_status = f"mail failed: {e}"
        print("inquiry", rec["email"], rec_status, flush=True)
        self._json(200, {"ok": True})


if __name__ == "__main__":
    print(f"Tianqi inquiry server on {HOST}:{PORT}, data={DATA}, mail={'on' if SMTP_HOST else 'off'}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
