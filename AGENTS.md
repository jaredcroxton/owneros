# OwnerOS, for agents working in this folder

You are inside OwnerOS: a local business cockpit for an owner who runs their company
with an AI crew. One stdlib Python server (`server.py`), eleven HTML rooms, no build
step, no dependencies, nothing leaves the Mac. The owner has usually just come from a
workshop where they installed the CREW skills, and they are here to set this up and
make it theirs. Help them do that. Do not redesign it.

If the owner asks you to set it up, run the `/setup-owneros` workflow
(`.agents/workflows/setup-owneros.md`). If that workflow is not available, follow
the same steps by hand: check prerequisites, ask the five questions in chat, run
`./install.sh` with flags, confirm the cockpit is live, point them at the first job.

## What you must never do here

These are the invariants the whole product rests on. `claude.md` is the full
constitution; these are the ones an agent is most likely to break by being helpful.

1. **Never write into `~/.claude/crew-state`.** That is the crew's filing cabinet.
   OwnerOS reads it and never writes it. Do not create, rename, move, fix, or tidy
   anything in there, not even a record that looks broken. Broken records render as
   "unparsed record" on purpose.
2. **Never create `~/.hermes/crew-state`.** Every CREW skill hardcodes
   `~/.claude/crew-state` in its Step 0 and Final Step. That single path is why one
   brain can serve two runtimes. A second cabinet splits it. If you find an old
   instruction or a `sed` that rewrites that path, do not run it.
3. **Never write into `~/.claude/skills` or `~/.hermes/profiles`.** The installer
   copies skills into `~/.hermes/skills/crew` (via `hermes-sync.sh`) and nowhere else.
4. **Never delete.** Not `tasks.db` (it is not ours), not a skill, not a record, not a
   Hermes profile. If something must go, park it with a rename and tell the owner.
5. **No cloud at runtime.** Do not add a CDN font, an analytics tag, a remote API, or
   a fetch to anything off the machine. The one sanctioned exception is Fish Audio,
   and only when `~/.owneros/fish.key` exists.
6. **Do not add rooms, endpoints, or capabilities** unless the owner asks for exactly
   that. Setup is configuration, not a build.

## What the installer owns

`install.sh` writes only `~/.owneros/*` (owner.json, fish.key, os-url.txt, logs) and
`~/Library/LaunchAgents/com.owneros.plist`. Those are the only files setup touches.
Every question is a flag, so you can ask in chat and run it without prompts:

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
| python3 | `command -v python3` | `xcode-select --install` |
| Claude Code, logged in | `command -v claude` | Install Claude Code, run `claude` once, `/login`. Brock's briefing and the Files assistant need it; the rooms still load without it |
| CREW skills | `ls -d ~/.claude/skills/crew-*` count > 0 | `git clone https://github.com/jaredcroxton/Crew-Agents.git && cd Crew-Agents && bash install.sh --all --global` |
| Brand context | `~/.claude/crew-state/brand-context.md` exists | Not a blocker. After install, the owner says "use the crew, build my brand context" in Claude Code |
| Hermes Agent | `~/.hermes` is a directory | Optional. Only matters if they want the second runtime |

## After install

- Live URL is in `~/.owneros/os-url.txt` (normally `http://localhost:4890`).
- Health: `curl localhost:4890/api/health` returns `ok`, `brain`, `fish`, `hermes`.
- Log: `tail -20 ~/.owneros/os.log`.
- Restart after any edit: `./start-os.sh`. Stop: `./stop-os.sh`.
- First job if there is no brand context yet: in Claude Code, "use the crew, build my
  brand context". Then `/plays`, pick a play, Copy, paste into Claude Code.
- Hermes users run crew skills in the default profile (plain `hermes`), never
  `hermes -p <name>`; named profiles do not see the CREW skills.

## If you are asked to change the product

Read `claude.md` first. It holds the design law (the Midnight Cockpit), the data
schemas, the architectural invariants, and the maintenance log. Update it before you
change code when a schema or rule moves. Frontend rooms are single monolithic HTML
files; keep them that way. Shared tokens live in `midnight.css`. No em dashes in
anything you write here.
