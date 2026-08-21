#!/bin/zsh
# OwnerOS: start (or restart) the OS server, and the Second Brain if you have one.
# Safe after `git pull`: the OS agent is always reloaded so new code is live.
AGENTS="$HOME/Library/LaunchAgents"

# The plist carries the label the installer wrote (com.owneros). The original
# machine predates the installer and uses com.jared.owneros; both are honoured.
OS_PLIST=""
for label in com.owneros com.jared.owneros; do
  [[ -f "$AGENTS/$label.plist" ]] && { OS_PLIST="$AGENTS/$label.plist"; break; }
done
if [[ -z "$OS_PLIST" ]]; then
  echo "No OwnerOS LaunchAgent found. Run ./install.sh first."
  exit 1
fi

BRAIN_PLIST="$AGENTS/com.jared.secondbrain.plist"
if [[ -f "$BRAIN_PLIST" ]] && ! launchctl list | grep -q com.jared.secondbrain; then
  launchctl load "$BRAIN_PLIST"
  echo "Second Brain agent loaded."
fi

launchctl unload "$OS_PLIST" 2>/dev/null
launchctl load "$OS_PLIST"
echo "OwnerOS agent loaded ($(basename "$OS_PLIST" .plist))."

sleep 1
URL=$(cat "$HOME/.owneros/os-url.txt" 2>/dev/null || echo "http://localhost:4890")
echo ""
echo "OwnerOS  -> $URL"
[[ -f "$BRAIN_PLIST" ]] && echo "Brain    -> http://localhost:4880"
open "$URL"
