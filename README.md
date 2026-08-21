# OwnerOS_

Your business, one screen. A local operating system for owners who run their
company with an AI crew: a living cockpit over the crew's filing cabinet, a
daily-briefing chief of staff who speaks, a second-brain map, live thought
capture, the full skill deck, a plain-words playbook, and safe file management.
Everything runs on your Mac. Nothing leaves it (one optional exception: the
Fish voice, key-gated).

## Before you install

Three things need to be on the Mac first. The workshop covers all three.

1. **Claude Code**, installed and logged in (run `claude` once, then `/login`).
2. **The CREW skills** in `~/.claude/skills`:
   `git clone https://github.com/jaredcroxton/Crew-Agents.git && cd Crew-Agents && bash install.sh --all --global`
3. **Hermes Agent**, only if you want the second runtime. Optional. OwnerOS runs
   without it and simply does not show the Hermes room.

## Install (3 lines)

```
git clone https://github.com/jaredcroxton/owneros.git ~/OwnerOS
cd ~/OwnerOS
./install.sh
```

The installer checks what is on the Mac, then asks five things:

| Question | Why |
|---|---|
| Your first name | The avatar initial and how Brock addresses you |
| Your business name | Shown across the rooms |
| One line on what the business does | Brock's briefing context |
| **Do you run Hermes Agent on this Mac? (y/n)** | **Yes**: copies the CREW skills into `~/.hermes/skills/crew` so Hermes can run them, and keeps the Hermes room and the Sessions toggle. **No**: the cockpit loads without the Hermes room, the Sessions toggle, or any Hermes read. Change it later in `~/.owneros/owner.json` |
| Fish Audio key (optional) | Brock's real voice. Enter to skip; the browser voice takes over |

Then it wires the always-on service and opens your cockpit.

Every question is also a flag, so an agent can ask you in chat and run the install
without prompts (this is what the Antigravity workflow does):

```
./install.sh --name Jo --business "Jo's Plumbing" --about "domestic plumbing, Brisbane" \
             --hermes no --fish-key "" --no-open
```

`./install.sh --help` lists the rest (`--yes` accepts every default).

### First job after install

If the installer said "Brand context: not yet", open Claude Code anywhere and say
**"use the crew, build my brand context"**. Ten minutes of plain questions writes
`~/.claude/crew-state/brand-context.md`, the one file every role reads first. Today
and Projects fill up from there. Then open `/plays`, pick a play, Copy, paste.

### Setting up from Antigravity

Open the cloned folder in Antigravity and type `/setup-owneros` in the agent chat.
The workflow (`.agents/workflows/setup-owneros.md`) checks the prerequisites, asks
you the five questions in chat, runs the installer with flags, and walks you to your
first play. `AGENTS.md` carries the rules any agent must keep while working in here.

### If you said yes to Hermes

- Run crew skills in the **default** Hermes profile (plain `hermes`). Named profiles
  (`hermes -p name`) keep their own skill folders and do not see the CREW skills.
- After a CREW update, run `./hermes-sync.sh` to refresh the copy Hermes reads.
- One brain: both runtimes read and write `~/.claude/crew-state`. Never create
  `~/.hermes/crew-state`; the sync script refuses to run while it exists.

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
| Personas | Six market shapes, each with a signature chain and a one-paste kickoff |
| Hermes | The second runtime, only if you said yes: the agent network and a Connections panel that checks every claim against disk |
| Sessions | Both runtimes (or just Claude Code), metadata only, safe on a projector |
| Roadmap | Parked ideas, on purpose |

## Hard rules baked in

- The crew's filing cabinet (`~/.claude/crew-state`) is read-only to the OS.
- The OS writes only to its own home (`~/.owneros`).
- No cloud at runtime; Fish voice activates only if `~/.owneros/fish.key` exists.

## Update

```
git pull
./start-os.sh
```

`start-os.sh` reloads the service so the new code is live. `./stop-os.sh` stops it.

## Customise

- `~/.owneros/owner.json`: your name, initial, business, and `hermes` true/false (the installer writes it)
- `~/.owneros/fish-voice.txt` — a Fish voice model id for Brock's voice
- `playbook.md` — the plays library; edit and reload
- `assets/` — the cinematic plates; swap for your own world
