# OwnerOS_

Your business, one screen. A local operating system for owners who run their
company with an AI crew: a living cockpit over the crew's filing cabinet, a
daily-briefing chief of staff who speaks, a second-brain map, live thought
capture, the full skill deck, a plain-words playbook, and safe file management.
Everything runs on your Mac. Nothing leaves it (one optional exception: the
Fish voice, key-gated).

## Install (3 lines)

```
git clone <this repo> ~/OwnerOS
cd ~/OwnerOS
./install.sh
```

The installer asks your name and business, wires the always-on service, and
opens your cockpit. Prerequisites: macOS, Claude Code installed and logged in,
the CREW skills installed.

## The rooms

| Room | What it is |
|---|---|
| Today | The morning glance: Brock's briefing (spoken), what needs you, radar, live capture pulse |
| Projects | The cabinet: every project, records read-only, pin/star/hide, New project form |
| Brain | Your second-brain map, embedded live (needs the brain server; degrades gracefully) |
| Capture | Type or speak a thought; it becomes a node in the brain while you watch |
| Launch | The crew skill deck: 89 skills, click copies the invoke phrase |
| Plays | The playbook: 46 plays + 12 chains in plain words, intent search, copyable prompts |
| Files | Safe-zone file manager: browse, rename, move, ask AI about a folder |
| Roadmap | Parked ideas, on purpose |

## Hard rules baked in

- The crew's filing cabinet (`~/.claude/crew-state`) is read-only to the OS.
- The OS writes only to its own home (`~/.owneros`).
- No cloud at runtime; Fish voice activates only if `~/.owneros/fish.key` exists.

## Update

```
git pull
launchctl unload ~/Library/LaunchAgents/com.owneros.plist
launchctl load ~/Library/LaunchAgents/com.owneros.plist
```

## Customise

- `~/.owneros/owner.json` — your name, initial, business (the installer writes it)
- `~/.owneros/fish-voice.txt` — a Fish voice model id for Brock's voice
- `playbook.md` — the plays library; edit and reload
- `assets/` — the cinematic plates; swap for your own world
