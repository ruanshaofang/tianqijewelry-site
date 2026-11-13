#!/bin/bash
# Make https://tianqijewelry.cn (and www) work: check DNS, then add the .cn names
# to the site's SSL certificate. Also reports whether the certificate auto-renews.
# Safe to run again. Changes nothing if a check fails.

COM=tianqijewelry.com
CN=tianqijewelry.cn

MYIP=$(curl -s --max-time 8 https://api.ipify.org || curl -s --max-time 8 ifconfig.me)
echo "== Server public IP: ${MYIP:-unknown}"
for h in $CN www.$CN; do
  ip=$(getent ahostsv4 "$h" | awk 'NR==1{print $1}')
  echo "   $h -> ${ip:-NOT RESOLVING}"
  if [ "$ip" != "$MYIP" ]; then BADDNS=1; fi
done
if [ -n "$BADDNS" ]; then
  echo
  echo "RESULT: DNS for $CN does not point to this server yet."
  echo "Fix at your .cn domain registrar: A record  @  -> $MYIP   and   A record  www  -> $MYIP"
  echo "Then run this script again (DNS can take up to an hour)."
  exit 0
fi

echo "== Certificate tool"
if command -v certbot >/dev/null; then
  CERTNAME=$(sudo certbot certificates 2>/dev/null | awk '/Certificate Name:/{n=$3} /Domains:.*'"$COM"'/{print n; exit}')
  echo "   certbot found, certificate: ${CERTNAME:-none}"
  sudo certbot --nginx --non-interactive --agree-tos --expand ${CERTNAME:+--cert-name $CERTNAME} \
    -d $COM -d www.$COM -d $CN -d www.$CN --redirect 2>&1 | tail -4
  sudo nginx -t && sudo systemctl reload nginx
  echo "== Auto-renew"; systemctl list-timers 2>/dev/null | grep -i certbot || sudo crontab -l 2>/dev/null | grep -i certbot || echo "   no certbot timer found"
elif [ -d "$HOME/.acme.sh" ] || sudo test -d /root/.acme.sh; then
  echo "   acme.sh is used on this server - send this output to Claude for the exact command."
  sudo ls /root/.acme.sh 2>/dev/null | head; ls ~/.acme.sh 2>/dev/null | head
else
  echo "   No certbot / acme.sh found. Current certificate:"
  echo | openssl s_client -connect $COM:443 -servername $COM 2>/dev/null | openssl x509 -noout -issuer -ext subjectAltName
  echo "   Send this output to Claude."
fi

echo "== Test"
for u in https://$CN https://www.$CN; do curl -s -o /dev/null -w "$u -> %{http_code}\n" --max-time 10 "$u"; done
