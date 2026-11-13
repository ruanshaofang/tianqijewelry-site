#!/bin/bash
# Auto-deploy for tianqijewelry.com
# Runs every few minutes from cron on the Aliyun server.
# If GitHub has new commits on main, it pulls them and publishes site/ to /var/www/tianqi.
# The live version before each update is kept in /var/www/tianqi.prev (one-step rollback).
set -euo pipefail

REPO="$HOME/tianqi-site"
LIVE="/var/www/tianqi"
PREV="/var/www/tianqi.prev"

cd "$REPO"
git fetch -q origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
[ "$LOCAL" = "$REMOTE" ] && exit 0

git reset -q --hard origin/main

# Safety check: never publish an empty or broken site folder
if [ ! -f site/index.html ]; then
  echo "$(date '+%F %T') ABORT: site/index.html missing in $REMOTE"
  exit 1
fi

sudo rsync -a --delete "$LIVE/" "$PREV/"
sudo rsync -a --delete --exclude '.git' site/ "$LIVE/"
echo "$(date '+%F %T') deployed $(git log --oneline -1)"

# Restart the inquiry receiver when its code changed in this update
if ! git diff --quiet "$LOCAL" "$REMOTE" -- inquiry/ 2>/dev/null; then
  if sudo systemctl restart tianqi-inquiry; then echo "$(date '+%F %T') restarted tianqi-inquiry"
  else echo "$(date '+%F %T') WARN: could not restart tianqi-inquiry"; fi
fi
