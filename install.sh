#!/bin/zsh
# OwnerOS installer. Run from the cloned folder: ./install.sh
# Prerequisites: macOS, python3, Claude Code installed and logged in,
# the CREW skills installed (your workshop covers both).
set -e
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PY3="$(command -v python3)"
if [[ -z "$PY3" ]]; then
  echo "python3 not found. Install Xcode command line tools first:"
  echo "  xcode-select --install"
  exit 1
fi

echo ""
echo "  OwnerOS_  ·  your business, one screen"
echo ""
printf "Your first name: "
read OWNER_NAME
printf "Your business name: "
read OWNER_BIZ
printf "One line on what the business does: "
read OWNER_ABOUT

mkdir -p "$HOME/.owneros"
"$PY3" - "$OWNER_NAME" "$OWNER_BIZ" "$OWNER_ABOUT" <<'EOF'
import json, sys, pathlib
name, biz, about = (sys.argv[1] or "Owner"), (sys.argv[2] or "My Business"), sys.argv[3]
pathlib.Path.home().joinpath(".owneros/owner.json").write_text(json.dumps({
    "name": name.strip() or "Owner",
    "initial": (name.strip()[:1] or "O").upper(),
    "business": biz.strip() or "My Business",
    "about": about.strip() or "a small business"}, indent=1))
print("identity written: ~/.owneros/owner.json")
EOF

PLIST="$HOME/Library/LaunchAgents/com.owneros.plist"
sed -e "s|__PYTHON3__|$PY3|g" \
    -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$APP_DIR/com.owneros.plist.template" > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
sleep 2
URL="$(cat "$HOME/.owneros/os-url.txt" 2>/dev/null || echo http://localhost:4890)"
echo ""
echo "OwnerOS is live: $URL"
echo "Optional voice upgrade: paste a Fish Audio API key into ~/.owneros/fish.key"
open "$URL"
