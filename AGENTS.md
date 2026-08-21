# OwnerOS, for agents working in this folder

You are inside OwnerOS: a local business cockpit for an owner who runs their company
with an AI crew. One stdlib Python server (`server.py`), eleven HTML rooms, no build
step, no dependencies, nothing leaves the Mac. The owner has usually just come from a
workshop where they installed the CREW skills, and they are here to set this up and
make it theirs. Help them do that. Do not redesign it.

**The owner does not use a terminal.** You run every command yourself and show them
what matters. Never answer a setup question with "run this"; run it.

To set it up, follow `.agents/workflows/setup-owneros.md` (`/setup-owneros` when
this folder is the workspace). If you were pointed here by a pasted prompt and the
repo is not cloned yet, the workflow's step 0 clones it to `~/OwnerOS`.

## What you must never do here

These are the invariants the whole product rests on. `claude.md` is the full
constitution; these are the ones an agent is most likely to break by being helpful.

1. **OwnerOS never writes into `~/.claude/crew-state`.** That is the crew's filing
   cabinet. The OS reads it; CREW skills write it, and only what their own SKILL.md
   says (Step 0 reads, Final Step writes the record). Do not create, rename, move,
   fix, or tidy anything in there yourself. Broken records render as "unparsed
   record" on purpose.
2. **Never create `~/.hermes/crew-state`.** Every CREW skill hardcodes
   `~/.claude/crew-state`. That single path is why one brain can serve more than one
   runtime. A second cabinet splits it. If you find an old instruction or a `sed`
   that rewrites that path, do not run it.
3. **Never write into `~/.claude/skills` or `~/.hermes/profiles`.** The installer
   copies skills into `~/.hermes/skills/crew` (via `hermes-sync.sh`) and nowhere else.
4. **Never delete.** Not `tasks.db` (it is not ours), not a skill, not a record, not a
   Hermes profile. If something must go, park it with a rename, and only after the
   owner says yes.
5. **No cloud at runtime.** Do not add a CDN font, an analytics tag, a remote API, or
   a fetch to anything off the machine. The one sanctioned exception is Fish Audio,
   and only when `~/.owneros/fish.key` exists.
6. **Do not add rooms, endpoints, or capabilities** unless the owner asks for exactly
   that. Setup is configuration, not a build.

## Running a CREW skill from this chat

A CREW skill is a markdown procedure at `~/.claude/skills/<crew-name>/SKILL.md`. Any
capable agent can run one: read the file, follow it exactly, including its Step 0
(read `~/.claude/crew-state/brand-context.md` and the active project) and its Final
Step (write the handoff record where it says). When the owner pastes a play from the
Plays room, start from `~/.claude/skills/crew-core-using-crew/SKILL.md`, the
dispatcher, and let it route. The record a skill files is what OwnerOS shows in
Projects; the OS is never told, it just reads the cabinet.

## What the installer owns

`install.sh` writes only `~/.owneros/*` (owner.json, fish.key, os-url.txt, logs) and
`~/Library/LaunchAgents/com.owneros.plist`. Those are the only files setup touches.
Every question is a flag, so you ask in chat and run it without prompts:

```
./install.sh --name "<first name>" --business "<business>" --about "<one line>" \
             --hermes yes|no --fish-key "<key or empty>" --no-open
```

`--hermes yes` also runs `./hermes-sync.sh`, which copies the CREW skills into
`~/.hermes/skills/crew` and verifies with `hermes skills list`. It exits 2 and does
nothing if `~/.hermes/crew-state` exists. Relay that message to the owner as is.

The runtime switch lives in `~/.owneros/owner.json` as `"hermes": true|false`.
Off means the Hermes room, the Sessions toggle, and every Hermes read are gone.
Absent means auto (on when `~/.hermes` is a directory). Flip it by editing the file
and running `./start-os.sh`.

## Prerequisites to check before setup

| Check | How | If missing |
|---|---|---|
| macOS | `uname` is Darwin | The service uses launchd; other platforms are not supported yet |
| git and python3 | `command -v git python3` | Run `xcode-select --install`; macOS shows a dialog, the owner clicks Install |
| Claude Code, signed in | `command -v claude` | Not a blocker for the rooms. Brock's briefing and the Files assistant need it |
| CREW skills | `ls -d ~/.claude/skills/crew-*` count > 0 | `git clone https://github.com/jaredcroxton/Crew-Agents.git ~/Crew-Agents && bash ~/Crew-Agents/install.sh --all --global` |
| Brand context | `~/.claude/crew-state/brand-context.md` exists | Not a blocker. The first job after install; you can run it in this chat |
| Hermes Agent | `~/.hermes` is a directory | Optional. Only matters if they want the second runtime |

## After install

- Live URL is in `~/.owneros/os-url.txt` (normally `http://localhost:4890`).
- Health: `curl localhost:4890/api/health` returns `ok`, `brain`, `fish`, `hermes`.
- Log: `tail -20 ~/.owneros/os.log`.
- Restart after any edit: `./start-os.sh`. Stop: `./stop-os.sh`.
- "Update OwnerOS" means `git pull --ff-only && ./start-os.sh` in this folder.
- Hermes users run crew skills in the default profile (plain `hermes`), never
  `hermes -p <name>`; named profiles do not see the CREW skills.

## If you are asked to change the product

Read `claude.md` first. It holds the design law (the Midnight Cockpit), the data
schemas, the architectural invariants, and the maintenance log. Update it before you
change code when a schema or rule moves. Frontend rooms are single monolithic HTML
files; keep them that way. Shared tokens live in `midnight.css`. No em dashes in
anything you write here.
