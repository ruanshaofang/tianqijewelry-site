#!/bin/bash
# Set up email sending for website inquiries (Zoho Mail).
# Asks for the SMTP host and the Zoho app password on screen; the password is
# typed hidden, stored only in /etc/tianqi-inquiry.env (root-only), never in git.
set -e
echo "SMTP host for info@tianqijewelry.com"
echo "  free Zoho account      -> smtp.zoho.com"
echo "  paid Zoho Mail account -> smtppro.zoho.com"
read -r -p "Host [smtp.zoho.com]: " HOST
HOST=${HOST:-smtp.zoho.com}
read -r -s -p "Zoho app password (typing is hidden): " PASS; echo
[ -n "$PASS" ] || { echo "No password entered, nothing changed."; exit 1; }

printf 'INQ_MAIL_TO=info@tianqijewelry.com\nINQ_SMTP_HOST=%s\nINQ_SMTP_PORT=465\nINQ_SMTP_USER=info@tianqijewelry.com\nINQ_SMTP_PASS=%s\n' "$HOST" "$PASS" \
  | sudo tee /etc/tianqi-inquiry.env >/dev/null
sudo chmod 600 /etc/tianqi-inquiry.env
unset PASS
sudo systemctl restart tianqi-inquiry
sleep 2

echo "Sending a test inquiry..."
curl -s -X POST http://127.0.0.1:8788/api/inquiry -H 'Content-Type: application/json' \
  -d '{"type":"Setup test","name":"Website setup test","email":"info@tianqijewelry.com","country":"-","message":"Test inquiry from the server. If you see this email, website inquiries now reach your inbox."}'
echo; sleep 3
echo "== result =="; sudo journalctl -u tianqi-inquiry -n 3 --no-pager | grep -E "inquiry|failed|sent" || true
