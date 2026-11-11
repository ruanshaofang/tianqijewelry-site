#!/bin/bash
# One-time setup for the inquiry receiver. Safe to run again.
set -e
cd "$(dirname "$0")"

# 1. data folder + settings file (settings file is never in git)
sudo mkdir -p /var/lib/tianqi-inquiry && sudo chown admin:admin /var/lib/tianqi-inquiry
if [ ! -f /etc/tianqi-inquiry.env ]; then
  printf 'INQ_MAIL_TO=info@tianqijewelry.com\nINQ_SMTP_HOST=\nINQ_SMTP_PORT=465\nINQ_SMTP_USER=\nINQ_SMTP_PASS=\n' | sudo tee /etc/tianqi-inquiry.env >/dev/null
  sudo chmod 600 /etc/tianqi-inquiry.env
fi

# 2. service
sudo cp tianqi-inquiry.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tianqi-inquiry
sudo systemctl restart tianqi-inquiry

# 3. nginx: route /api/inquiry to the receiver (backup + test + rollback)
CONF=$(sudo grep -rl "server_name tianqijewelry.com" /etc/nginx/ | head -1)
if ! sudo grep -q "api/inquiry" "$CONF"; then
  sudo cp "$CONF" "$CONF.bak-inquiry"
  sudo python3 - "$CONF" <<'PY'
import sys,re
p=sys.argv[1]; s=open(p).read()
block='\n    location ^~ /api/inquiry {\n        proxy_pass http://127.0.0.1:8788;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n        client_max_body_size 32k;\n    }\n'
s=re.sub(r'(server_name tianqijewelry\.com[^;]*;)', lambda m: m.group(1)+block, s)
open(p,'w').write(s)
PY
  if sudo nginx -t 2>/dev/null; then sudo systemctl reload nginx; echo "nginx updated: $CONF"
  else sudo cp "$CONF.bak-inquiry" "$CONF"; echo "nginx test FAILED - restored original"; fi
fi

sleep 1
echo "== health =="; curl -s https://tianqijewelry.com/api/inquiry/health; echo
