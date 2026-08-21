# OwnerOS_

Your business, one screen. A local operating system for owners who run their
company with an AI crew: a living cockpit over the crew's filing cabinet, a
daily-briefing chief of staff who speaks, a second-brain map, live thought
capture, the full skill deck, a plain-words playbook, and safe file management.
Everything runs on your Mac. Nothing leaves it (one optional exception: the
Fish voice, key-gated).

## Set up, in Antigravity, no terminal

The workshop put Claude Code and the CREW skills on your Mac (and Hermes Agent, if
you chose it). From there you never open a terminal. Your agent does the typing.

Open Antigravity and paste this into the agent chat:

```
Set up OwnerOS for me. Clone https://github.com/jaredcroxton/owneros.git into ~/OwnerOS
(pull if it is already there), then read ~/OwnerOS/AGENTS.md and follow
~/OwnerOS/.agents/workflows/setup-owneros.md step by step. Ask me the questions one at a
time. Run every command yourself; I will not use a terminal.
```

What happens next, all in the chat:

1. **It checks the Mac.** python3, Claude Code, how many CREW skills are installed,
   whether your brand context exists yet, whether Hermes is there. Anything missing is
   named, with what it means, and setup carries on.
2. **It asks you five things, one at a time.**

   | Question | Why |
   |---|---|
   | Your first name | The avatar initial and how Brock addresses you |
   | Your business name | Shown across the rooms |
   | One line on what the business does | Brock's briefing context |
   | **Do you run Hermes Agent on this Mac?** | **Yes**: copies the CREW skills into `~/.hermes/skills/crew` so Hermes can run them, and keeps the Hermes room and the Sessions toggle. **No**: the cockpit loads without the Hermes room, the Sessions toggle, or any Hermes read. Either answer can be changed later |
   | A Fish Audio key, if you have one | Brock's real voice. Skip it and the browser voice takes over |

3. **It runs the installer** with your answers, wires the always-on service, and opens
   your cockpit at `http://localhost:4890`.
4. **It starts your first job.** If you have no brand context yet, that is a
   ten-minute plain-language conversation, right there in the chat. It writes
   `~/.claude/crew-state/brand-context.md`, the one file every role reads first. Today
   and Projects fill up from there. Then you open `/plays`, pick a play, press Copy,
   and paste it back to the agent.

Afterwards, open `~/OwnerOS` as your workspace in Antigravity. `/setup-owneros` and
the OwnerOS rules are then on hand, and "update OwnerOS" is a sentence, not a command.

### If you said yes to Hermes

- Run crew skills in the **default** Hermes profile (plain `hermes`). Named profiles
  (`hermes -p name`) keep their own skill folders and do not see the CREW skills.
- After a CREW update, ask your agent to run `hermes-sync.sh` to refresh the copy
  Hermes reads.
- One brain: every runtime reads and writes `~/.claude/crew-state`. Never create
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

## Under the hood

What the agent runs, for anyone who would rather do it by hand:

```
git clone https://github.com/jaredcroxton/owneros.git ~/OwnerOS
cd ~/OwnerOS
./install.sh
```

`install.sh` asks the same five questions, or takes them as flags so an agent can
answer without prompts (`./install.sh --help`):

```
./install.sh --name Jo --business "Jo's Plumbing" --about "domestic plumbing, Brisbane" \
             --hermes no --fish-key "" --no-open
```

It writes only `~/.owneros/*` and `~/Library/LaunchAgents/com.owneros.plist`.
`hermes-sync.sh` is the Hermes copy. `start-os.sh` starts or restarts the service
(so `git pull` then `./start-os.sh` is the update); `stop-os.sh` stops it.
`AGENTS.md` is the contract any agent keeps while working in here; `.agents/rules`
and `.agents/workflows` are the Antigravity-native copies of it.

## Customise

- `~/.owneros/owner.json`: your name, initial, business, and `hermes` true/false (the installer writes it)
- `~/.owneros/fish-voice.txt`: a Fish voice model id for Brock's voice
- `playbook.md`: the validated fallback plays library, used only if the live CREW library is missing
- `assets/`: the cinematic plates; swap for your own world
