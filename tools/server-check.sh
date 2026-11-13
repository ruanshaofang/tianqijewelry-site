#!/bin/bash
# Server housekeeping for tianqijewelry.com. Safe to run again.
#  1. Nginx: serve the site's own 404 page (backup + test + automatic rollback)
#  2. SSL: show expiry and test that automatic renewal works
#  3. Disk: show what takes space in the home folder (deletes nothing)

echo "== 1. Custom 404 page"
CONF=$(sudo grep -rl "server_name tianqijewelry.com" /etc/nginx/ | head -1)
if sudo grep -q "error_page 404 /404.html" "$CONF"; then
  echo "   already set in $CONF"
else
  sudo cp "$CONF" "$CONF.bak-404"
  sudo python3 - "$CONF" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
s = re.sub(r'(server_name tianqijewelry\.com[^;]*;)', r'\1\n    error_page 404 /404.html;', s)
open(p, 'w').write(s)
PY
  if sudo nginx -t 2>/dev/null; then sudo systemctl reload nginx; echo "   set in $CONF"
  else sudo cp "$CONF.bak-404" "$CONF"; echo "   nginx test failed - restored original, nothing changed"; fi
fi
curl -s -o /dev/null -w "   test: /this-page-does-not-exist -> %{http_code}\n" https://tianqijewelry.com/this-page-does-not-exist

echo "== 2. SSL certificate"
echo | openssl s_client -connect tianqijewelry.com:443 -servername tianqijewelry.com 2>/dev/null | openssl x509 -noout -issuer -enddate | sed 's/^/   /'
if command -v certbot >/dev/null; then
  echo "   tool: certbot"
  systemctl list-timers 2>/dev/null | grep -i certbot | sed 's/^/   timer: /' || true
  sudo crontab -l 2>/dev/null | grep -i certbot | sed 's/^/   cron: /' || true
  echo "   renewal test (takes ~30 s)..."
  sudo certbot renew --dry-run 2>&1 | grep -E "Congratulations|succeeded|failed|error" | head -3 | sed 's/^/   /'
elif sudo test -d /root/.acme.sh || [ -d "$HOME/.acme.sh" ]; then
  echo "   tool: acme.sh"
  sudo crontab -l 2>/dev/null | grep -i acme | sed 's/^/   cron: /'
  crontab -l 2>/dev/null | grep -i acme | sed 's/^/   cron: /'
else
  echo "   no certbot / acme.sh found - certificate may have been uploaded manually; renewal must be done by hand"
fi

echo "== 3. Disk use"
df -h / | tail -1 | awk '{print "   disk: " $3 " used of " $2 " (" $5 ")"}'
du -sh "$HOME"/* 2>/dev/null | sort -rh | head -8 | sed 's/^/   /'
