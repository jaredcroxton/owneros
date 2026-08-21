#!/bin/zsh
# OwnerOS: stop the OS server. The Second Brain keeps running unless --all.
AGENTS="$HOME/Library/LaunchAgents"

OS_PLIST=""
for label in com.owneros com.jared.owneros; do
  [[ -f "$AGENTS/$label.plist" ]] && { OS_PLIST="$AGENTS/$label.plist"; break; }
done
if [[ -z "$OS_PLIST" ]]; then
  echo "No OwnerOS LaunchAgent found. Nothing to stop."
  exit 0
fi

launchctl unload "$OS_PLIST" 2>/dev/null && \
  echo "OwnerOS stopped." || echo "OwnerOS was not running."

if [[ "$1" == "--all" && -f "$AGENTS/com.jared.secondbrain.plist" ]]; then
  launchctl unload "$AGENTS/com.jared.secondbrain.plist" 2>/dev/null && \
    echo "Second Brain stopped." || echo "Second Brain was not running."
fi
