#!/bin/zsh
# OwnerOS installer. Run from the cloned folder: ./install.sh
#
# Asks five things (name, business, one line, Hermes yes/no, optional Fish key),
# wires the always-on service, opens your cockpit. Every question is also a
# flag, so an agent (Antigravity, Claude Code) can ask you in chat and run this
# without prompts:
#
#   ./install.sh --name Jo --business "Jo's Plumbing" --about "domestic plumbing, Brisbane" \
#                --hermes no --fish-key "" --no-open
#
#   --hermes yes|no     Do you run Hermes Agent on this Mac? yes also copies the
#                       CREW skills into ~/.hermes/skills/crew (see hermes-sync.sh)
#   --fish-key KEY      Fish Audio key for Brock's voice (optional, "" to skip)
#   --yes               Accept the default for anything not given, ask nothing
#   --no-open           Do not open the browser at the end
#
# Writes only ~/.owneros/* and ~/Library/LaunchAgents/com.owneros.plist.
# Never writes into ~/.claude/crew-state, ~/.claude/skills, or ~/.hermes/profiles.

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
OWN="$HOME/.owneros"
CREW_STATE="$HOME/.claude/crew-state"
SKILLS="$HOME/.claude/skills"

OWNER_NAME=""; OWNER_BIZ=""; OWNER_ABOUT=""; HERMES_ANS=""; FISH_KEY=""
FISH_GIVEN=0; ASSUME_YES=0; OPEN_AFTER=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --name)      OWNER_NAME="$2"; shift 2 ;;
    --business)  OWNER_BIZ="$2"; shift 2 ;;
    --about)     OWNER_ABOUT="$2"; shift 2 ;;
    --hermes)    HERMES_ANS="$2"; shift 2 ;;
    --fish-key)  FISH_KEY="$2"; FISH_GIVEN=1; shift 2 ;;
    --yes|-y)    ASSUME_YES=1; shift ;;
    --no-open)   OPEN_AFTER=0; shift ;;
    -h|--help)   sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "install.sh: unknown flag $1 (try --help)"; exit 1 ;;
  esac
done

ask() {
  # ask VAR "prompt" "default"  (prompts only when the flag was not given)
  local var="$1" prompt="$2" def="$3" cur="${(P)1}"
  if [[ -n "$cur" ]]; then return; fi
  if [[ $ASSUME_YES -eq 1 ]]; then eval "$var=\"\$def\""; return; fi
  if [[ -n "$def" ]]; then printf "%s [%s]: " "$prompt" "$def"; else printf "%s: " "$prompt"; fi
  local reply; read reply
  [[ -z "$reply" ]] && reply="$def"
  eval "$var=\"\$reply\""
}

echo ""
echo "  OwnerOS_  ·  your business, one screen"
echo ""

# ---- pre-flight: say what is here and what is missing, then carry on --------
PY3="$(command -v python3)"
if [[ -z "$PY3" ]]; then
  echo "python3 not found. Install the Xcode command line tools first:"
  echo "  xcode-select --install"
  exit 1
fi
echo "  python3          ok ($PY3)"

if command -v claude >/dev/null 2>&1; then
  echo "  Claude Code      ok (run 'claude' once and /login if Brock stays quiet)"
else
  echo "  Claude Code      MISSING. Brock's briefing, chat and the Files assistant need it."
  echo "                   Install Claude Code, run 'claude' once to log in, then carry on."
fi

# find, not a glob: zsh aborts an unmatched glob with "no matches found" before ls runs
CREW_COUNT=$(find "$SKILLS" -maxdepth 1 -type d -name 'crew-*' 2>/dev/null | wc -l | tr -d ' ')
if [[ "$CREW_COUNT" -gt 0 ]]; then
  echo "  CREW skills      ok ($CREW_COUNT installed)"
else
  echo "  CREW skills      NONE under $SKILLS."
  echo "                   Workforce, Plays and Personas stay empty until CREW is installed."
fi

if [[ -f "$CREW_STATE/brand-context.md" ]]; then
  echo "  Brand context    ok (the cabinet is live)"
  HAVE_BRAND=1
else
  echo "  Brand context    not yet. Your first job after install is the brand conversation."
  HAVE_BRAND=0
fi

HERMES_DEFAULT="n"
if [[ -d "$HOME/.hermes" ]]; then
  echo "  Hermes Agent     found (~/.hermes)"
  HERMES_DEFAULT="y"
else
  echo "  Hermes Agent     not found (optional)"
fi
echo ""

# ---- the five questions ----------------------------------------------------
ask OWNER_NAME  "Your first name" "Owner"
ask OWNER_BIZ   "Your business name" "My Business"
ask OWNER_ABOUT "One line on what the business does" "a small business"
ask HERMES_ANS  "Do you run Hermes Agent on this Mac? (y/n)" "$HERMES_DEFAULT"
if [[ $FISH_GIVEN -eq 0 && $ASSUME_YES -eq 0 ]]; then
  if [[ -s "$OWN/fish.key" ]]; then
    printf "Fish Audio key for Brock's voice (one is already on file, Enter keeps it): "
  else
    printf "Fish Audio key for Brock's voice (optional, Enter to skip): "
  fi
  read FISH_KEY
fi

case "${HERMES_ANS:l}" in
  y|yes|true|1) HERMES_ON=1 ;;
  *)            HERMES_ON=0 ;;
esac

# ---- Hermes: copy CREW in, one brain, default profile ----------------------
echo ""
if [[ $HERMES_ON -eq 1 ]]; then
  if [[ ! -d "$HOME/.hermes" ]]; then
    echo "You said yes to Hermes, but ~/.hermes is not on this Mac. Recording Hermes as off"
    echo "so the cockpit stays clean. When Hermes is installed, run ./hermes-sync.sh and"
    echo "set \"hermes\": true in ~/.owneros/owner.json (or re-run ./install.sh)."
    HERMES_ON=0
  else
    "$APP_DIR/hermes-sync.sh"
    SYNC=$?
    if [[ $SYNC -eq 2 ]]; then
      echo "Hermes stays ON in the cockpit, and its Connections panel will refuse the"
      echo "one-brain claim until ~/.hermes/crew-state is moved aside. Then ./hermes-sync.sh."
    elif [[ $SYNC -ne 0 ]]; then
      echo "Hermes sync did not finish (exit $SYNC). Hermes stays ON in the cockpit; the"
      echo "Hermes room will show honestly what is and is not connected. Re-run ./hermes-sync.sh later."
    fi
  fi
else
  echo "Hermes off. The cockpit loads without the Hermes room or the Sessions toggle."
  echo "Change your mind later: ./hermes-sync.sh, then set \"hermes\": true in ~/.owneros/owner.json."
fi

# ---- identity + switches, the only state this installer owns ---------------
mkdir -p "$OWN"
"$PY3" - "$OWNER_NAME" "$OWNER_BIZ" "$OWNER_ABOUT" "$HERMES_ON" <<'EOF'
import json, sys, pathlib
name, biz, about, hermes = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"
name = name.strip() or "Owner"
pathlib.Path.home().joinpath(".owneros/owner.json").write_text(json.dumps({
    "name": name,
    "initial": name[:1].upper(),
    "business": biz.strip() or "My Business",
    "about": about.strip() or "a small business",
    "hermes": hermes}, indent=1) + "\n")
print("identity written: ~/.owneros/owner.json (hermes: %s)" % ("on" if hermes else "off"))
EOF

if [[ -n "$FISH_KEY" ]]; then
  printf "%s" "$FISH_KEY" > "$OWN/fish.key"
  chmod 600 "$OWN/fish.key"
  echo "voice key written: ~/.owneros/fish.key"
fi

# ---- the always-on service -------------------------------------------------
PLIST="$HOME/Library/LaunchAgents/com.owneros.plist"
mkdir -p "$HOME/Library/LaunchAgents"
sed -e "s|__PYTHON3__|$PY3|g" \
    -e "s|__APP_DIR__|$APP_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$APP_DIR/com.owneros.plist.template" > "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
sleep 2
URL="$(cat "$OWN/os-url.txt" 2>/dev/null || echo http://localhost:4890)"

echo ""
echo "OwnerOS is live: $URL"
echo ""
echo "Next:"
if [[ $HAVE_BRAND -eq 0 ]]; then
  echo "  1. Tell your agent (Antigravity or Claude Code):  use the crew, build my brand context"
  echo "     Ten minutes of plain questions. It writes ~/.claude/crew-state/brand-context.md,"
  echo "     the file every role reads first. Today and Projects fill up from there."
  echo "  2. Then your first play: open $URL/plays, pick one, Copy, paste it to your agent."
else
  echo "  1. Open $URL/plays, pick a play, Copy, paste it to your agent."
fi
if [[ $HERMES_ON -eq 1 ]]; then
  echo "  Hermes: run crew skills in the default profile (plain 'hermes'). The record lands"
  echo "  in the same cabinet and shows up in Projects without being told."
fi
[[ -z "$FISH_KEY" && ! -s "$OWN/fish.key" ]] && \
  echo "  Voice: Brock speaks with the browser voice. For the real one, paste a Fish Audio key into ~/.owneros/fish.key"
echo "  Update later: git pull, then ./start-os.sh"
echo ""
[[ $OPEN_AFTER -eq 1 ]] && open "$URL"
exit 0
