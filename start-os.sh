#!/bin/zsh
# OwnerOS: start everything (the OS server + the Second Brain server).
set -e
AGENTS="$HOME/Library/LaunchAgents"

if ! launchctl list | grep -q com.jared.secondbrain; then
  launchctl load "$AGENTS/com.jared.secondbrain.plist"
  echo "Second Brain agent loaded."
fi
if ! launchctl list | grep -q com.jared.owneros; then
  launchctl load "$AGENTS/com.jared.owneros.plist"
  echo "OwnerOS agent loaded."
fi

sleep 1
URL=$(cat "$HOME/.owneros/os-url.txt" 2>/dev/null || echo "http://localhost:4890")
echo ""
echo "OwnerOS  -> $URL"
echo "Brain    -> http://localhost:4880"
open "$URL"
