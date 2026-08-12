#!/bin/zsh
# OwnerOS: stop the OS server. The Second Brain keeps running unless --all.
AGENTS="$HOME/Library/LaunchAgents"

launchctl unload "$AGENTS/com.jared.owneros.plist" 2>/dev/null && \
  echo "OwnerOS stopped." || echo "OwnerOS was not running."

if [[ "$1" == "--all" ]]; then
  launchctl unload "$AGENTS/com.jared.secondbrain.plist" 2>/dev/null && \
    echo "Second Brain stopped." || echo "Second Brain was not running."
fi
