#!/bin/zsh
# OwnerOS: put the CREW skills where Hermes Agent can see them.
#
# Copies every ~/.claude/skills/crew-* folder into ~/.hermes/skills/crew/.
# Copies, not symlinks: this is the layout verified with `hermes skills list`.
# Re-run after a CREW update. Safe to run twice. Never deletes anything.
#
# The cabinet stays at ~/.claude/crew-state. That path is hardcoded in every
# skill's Step 0 and Final Step, which is the only reason one brain can serve
# two runtimes. This script refuses to run if ~/.hermes/crew-state exists.
#
# Exit codes: 0 synced, 2 split brain, 3 Hermes not installed, 4 no CREW skills.

HERMES_HOME="$HOME/.hermes"
SRC_ROOT="$HOME/.claude/skills"
DEST="$HERMES_HOME/skills/crew"
SPLIT="$HERMES_HOME/crew-state"

if [[ ! -d "$HERMES_HOME" ]]; then
  echo "hermes-sync: Hermes Agent is not installed on this Mac (no ~/.hermes)."
  echo "Install Hermes first, then run ./hermes-sync.sh again."
  exit 3
fi

if [[ -e "$SPLIT" ]]; then
  echo ""
  echo "hermes-sync: STOP. $SPLIT exists."
  echo "That is a second cabinet, and it splits the one brain in two: records"
  echo "written there never reach OwnerOS. This script will not touch it and"
  echo "will not sync while it is there. Move it aside yourself, for example:"
  echo "  mv \"$SPLIT\" \"$SPLIT.parked-\$(date +%Y%m%d)\""
  echo "then run ./hermes-sync.sh again."
  exit 2
fi

SRC_COUNT=$(find "$SRC_ROOT" -maxdepth 1 -type d -name 'crew-*' 2>/dev/null | wc -l | tr -d ' ')
if [[ "$SRC_COUNT" == "0" ]]; then
  echo "hermes-sync: no CREW skills found under $SRC_ROOT."
  echo "Install the CREW skills (the workshop covers this), then run ./hermes-sync.sh again."
  exit 4
fi

PY3="$(command -v python3)"
if [[ -z "$PY3" ]]; then
  echo "hermes-sync: python3 not found. Run: xcode-select --install"
  exit 1
fi

mkdir -p "$DEST"
"$PY3" - "$SRC_ROOT" "$DEST" <<'EOF'
import shutil, sys
from pathlib import Path
src_root, dest = Path(sys.argv[1]), Path(sys.argv[2])
copied = 0
for skill in sorted(src_root.glob("crew-*")):
    if not skill.is_dir() or not (skill / "SKILL.md").is_file():
        continue
    shutil.copytree(skill, dest / skill.name, dirs_exist_ok=True)
    copied += 1
print(f"hermes-sync: {copied} crew skills copied into {dest}")
EOF
[[ $? -ne 0 ]] && exit 1

# Verify with Hermes itself when the CLI is reachable. A non-login shell may
# not have ~/.local/bin on PATH, so look there too.
HERMES_BIN="$(command -v hermes 2>/dev/null)"
[[ -z "$HERMES_BIN" && -x "$HOME/.local/bin/hermes" ]] && HERMES_BIN="$HOME/.local/bin/hermes"
if [[ -n "$HERMES_BIN" ]]; then
  SEEN=$("$HERMES_BIN" skills list 2>/dev/null | grep -c "crew-")
  if [[ "$SEEN" -gt 0 ]]; then
    echo "hermes-sync: Hermes can see $SEEN crew skills (hermes skills list)."
  else
    echo "hermes-sync: copied, but 'hermes skills list' shows no crew skills yet."
    echo "Open a new terminal and run: hermes skills list"
  fi
else
  echo "hermes-sync: copied. Could not find the hermes CLI to verify; run: hermes skills list"
fi

echo ""
echo "Run crew skills in the DEFAULT Hermes profile (plain 'hermes', not 'hermes -p name')."
echo "Named profiles keep their own skill folders and do not see these."
echo "One brain: every skill reads and writes ~/.claude/crew-state, in both runtimes."
exit 0
