# OwnerOS_

Your business, one screen. A local operating system for owners who run their
company with an AI crew: a living cockpit over the crew's filing cabinet, a
daily-briefing chief of staff who speaks, a second-brain map, live thought
capture, the full skill deck, a plain-words playbook, and safe file management.
Everything runs on your Mac. Nothing leaves it (one optional exception: the
Fish voice, key-gated).

## Set up from the Claude Code panel, no terminal

The workshop put Claude Code and the CREW skills on your Mac. From there you never
open a terminal. Claude does the typing; you click Allow when it asks to run something.

Open your IDE (Antigravity, VS Code or Cursor), open the Claude Code panel, and paste:

```
Set up OwnerOS for me. Clone https://github.com/jaredcroxton/owneros.git into ~/OwnerOS
(pull if it is already there), then read ~/OwnerOS/AGENTS.md and follow
~/OwnerOS/.claude/skills/setup-owneros/SKILL.md step by step. Ask me the questions one
at a time. Run every command yourself; I will not use a terminal.
```

What happens next, all in the chat:

1. **It checks the Mac.** python3, Claude Code, how many CREW skills are installed,
   whether your brand context exists yet. Anything missing is named, with what it
   means, and setup carries on.
2. **It asks you three things, one at a time.**

   | Question | Why |
   |---|---|
   | Your first name | The avatar initial and how Brock addresses you |
   | Your business name | Shown across the rooms |
   | One line on what the business does | Brock's briefing context |

3. **It runs the installer** with your answers, wires the always-on service, and opens
   your cockpit at `http://localhost:4890`.
4. **It starts your first job.** If you have no brand context yet, that is a short
   plain-language conversation with the crew's brand skill, right there in the chat.
   Give it your website and it reads your colours, fonts, logo, products and voice
   from there, then asks only what the site does not answer. It writes
   `~/.claude/crew-state/brand-context.md`, the one file every role reads first, and
   everything the crew builds afterwards looks like your business. Today, Projects and
   Roadmap fill up from there. Then you open `/plays`, pick a play, press Copy, and
   paste it back to Claude.

Afterwards, open `~/OwnerOS` as your workspace. `/setup-owneros` is then a slash
command in the Claude Code panel, and "update OwnerOS" is a sentence, not a command.

### Advanced: Hermes Agent

If Hermes Agent is already on the Mac (`~/.hermes` exists), setup asks one extra
question: connect the crew to it too? Yes copies the CREW skills into
`~/.hermes/skills/crew`, keeps the Hermes room and the Sessions toggle, and the two
runtimes share one cabinet at `~/.claude/crew-state`. Run crew skills in the default
Hermes profile (plain `hermes`); named profiles do not see them. After a CREW update,
ask your agent to run `hermes-sync.sh`. Never create `~/.hermes/crew-state`.
Without Hermes on the Mac, none of this is mentioned and none of it appears.

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
| Hermes | Only if Hermes Agent is on the Mac and connected: the agent network and a Connections panel that checks every claim against disk |
| Sessions | Your Claude Code history (and Hermes, if connected), metadata only, safe on a projector |
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

`install.sh` asks the same three questions, or takes them as flags so an agent can
answer without prompts (`./install.sh --help`):

```
./install.sh --name Jo --business "Jo's Plumbing" --about "domestic plumbing, Brisbane" --no-open
```

It writes only `~/.owneros/*` and `~/Library/LaunchAgents/com.owneros.plist`.
`hermes-sync.sh` is the Hermes copy. `start-os.sh` starts or restarts the service
(so `git pull` then `./start-os.sh` is the update); `stop-os.sh` stops it.
`AGENTS.md` is the contract any agent keeps while working in here. The setup
procedure is the Claude Code project skill at `.claude/skills/setup-owneros/SKILL.md`;
`.agents/workflows` and `.agents/rules` point Antigravity's own agent at the same files.

## Customise

- `~/.owneros/owner.json`: your name, initial, business, and `hermes` true/false (the installer writes it)
- `~/.owneros/fish-voice.txt`: a Fish voice model id for Brock's voice
- `playbook.md`: the validated fallback plays library, used only if the live CREW library is missing
- `assets/`: the cinematic plates; swap for your own world
