# OwnerOS — Constitution

Local Business OS cockpit. One stdlib Python server, eleven rooms (Today, Projects, Brain,
Capture, Workforce, Plays, Personas, Hermes, Sessions, Files, Roadmap), PerformOS brand,
Apple language throughout.

## Design law v5, the Midnight Cockpit (locked 2026-08-18, rolling out room by room)
Chosen by Jared over two researched alternatives (Cinema/parchment, Drafted/blueprint)
after a live A/B font test (Fraunces beat Instrument Serif for the display seat).
v4's structure survives; the canvas inverts and the type cast is new. Five laws:
one ink on near-black; one rationed accent (ember) that only ever marks what needs
the owner; depth from a four-step surface ladder, never glows or shadow stacks;
four type voices with strict role ownership; color lives in content and live
states, never chrome.

Tokens: canvas g0 #08090a, card g1 #0f1011, raised g2 #161718, border line #23252a
(inner separator line2 #1b1d21), ink #f7f8f8 (primary text), mid #a3a19c, faint
#6f6d68 (secondary text is WARM neutral, never blue-cast; Jared 2026-08-18),
long-form reading tone --read #cbc8c3, ember #ff6b35 (needs-you, headline cursor,
the ONE filled pill per screen), proof green #49de80 (connected/live states only),
nav rgba(8,9,10,.8) blur 20px.
Contrast law: ink on any ladder step 15:1+; mid on g1 7:1+; faint reserved for
mono labels 9.5px+ (4.5:1 floor); prose on dark always --read, never mid.
No slug-speak on screen: crew-* skill ids and hyphenated cabinet names render
humanized (strip crew- and the department word, hyphens to spaces, sentence case).
Display-only: raw ids stay in data attributes, copy commands, deep links, APIs.
Status language unchanged: ink dot = done, ember = needs attention, outline = quiet,
proof green = connected. Blue #0071e3 and link #0066cc retired everywhere; old ember
#b64400 kept only as a deep-ember reference value.

Type (all local woff2 in fonts/, no CDN): Fraunces VF is display, room headlines
clamp(44-84px) wght 420 opsz 144 tracking -0.015em, wordmark 17px wght 480 opsz 60.
Inter Tight 600 is statement: section heads 19-28px, card titles, buttons, stat
numerals (tabular). Inter 400/500 is body, 15-16px lh 1.55. JetBrains Mono 400/500
is data: eyebrows, ids, dates, states, 9.5-12px caps tracking .12em. Instrument
Serif (400 + italic) is reserved for brand statement lines 38px and up, nothing
else. SF Pro, system stacks, Poppins and IBM Plex Mono are retired. Nothing under
9.5px.

Structure: as v4 (44px sticky nav, band system, 980-1200px inner columns, 980px
pill buttons), with two changes: cards are 12px radius with a 1px line border, and
elevation is climbing the surface ladder (g0 page, g1 card, g2 raised), never
shadows. Bands alternate g0 / g1 instead of white / gray. Hero art plates return
in rollout step 4 as dark re-lights (same objects, black studio ground, one warm
key light), never under a white veil.

Motion: v4 rules stand (200-400ms, backwards-fill, full reduced-motion paths).
Planned in rollout step 5: chart wires draw on entry, count-ups on scroll into
view, one ember flash when the one-brain reveal lands in Projects.

Rollout: shared tokens and @font-face live in midnight.css (served at
/midnight.css); a migrated room links it and keeps only page CSS inline.
today.html migrates first (canonical reference), then the other ten rooms. The
white Apple language (v4) remains in the un-migrated rooms and in git history
until the rollout reaches them.

## Architectural invariants
1. READ-ONLY over `~/.claude/crew-state`. The server's only write path is `~/.owneros/inbox`
   (the Capture endpoint). Never write, rename, or reorganise crew-state.
2. No cloud at runtime. Single sanctioned exception: Fish Audio transcription, active only
   when `~/.owneros/fish.key` exists. No key, no network call.
3. Unparseable handoffs render as "unparsed record". Never crash, never "fix" the file.
4. The Second Brain (`~/Desktop/cluade/second-brain-map`, served from `~/.second-brain-live`,
   LaunchAgent `com.jared.secondbrain`, port 4880) is embedded by iframe, never forked.
5. `tasks.db` files (in the second-brain folder AND in this folder) are not OwnerOS's. Leave them.
6. Filesystem is the database. Reads are fresh per request. No caching layer for v1.

## Data schemas
Handoff record (parsed): `{skill, file, title, date (YYYY-MM-DD), status, parsed, mtime, days, stale}`
Status sanctioned list: NOT STARTED | IN PROGRESS | BLOCKED | READY FOR REVIEW | DONE | DONE_WITH_GAPS | NO OUTPUT
"Needs me" statuses: BLOCKED, READY FOR REVIEW. Stale threshold: 14 days.
Capture file: `~/.owneros/inbox/<YYYYMMDD-HHMMSS>-<slug>.md` with frontmatter
`name`, `description` (<=140 chars), `captured`, `source: owneros-capture`.
Playbook: parsed fresh per request by `parse_playbook()` from the dispatcher's own
`references/plays.md` (## = category, ### = play, `**Field:**` bullets, `^##? Chain
plays` partition). To update plays, edit that file and reload the page. Each chain is
annotated with `roles[]` (each step resolved to an installed skill) and `staffed`.
Intents power the plain-words search.
Role dossier: `parse_skill_doc(name)` slices a SKILL.md on `^## ` headings and returns
steps, step0, final_step, verification, guardrails, handoffs, reads, writes, output and
`gaps[]`. It never raises; a skill with no `## Workflow` reports `gaps:["sop"]` and the
drawer says so. Boilerplate terminates on `^\*\*Final Step` (prefix-anchored: both
"Handoff Save" and "Record Save" variants exist in the corpus). Served by `/api/role`,
deliberately NOT by `/api/workforce` (eager SOP text measured +309KB on a grid where at
most one drawer opens). `handoff_index()` is the app's only cache, memoised on a corpus
signature of (name, mtime_ns, size) so a hand-edited skill is live on next reload.
A `crew-*` folder whose SKILL.md has no parseable `name` is skipped from the roster
entirely. It is never deleted, moved, or "fixed".
Owner file: `~/.owneros/owner.json` = `{name, initial, business, about, hermes}`, written by
`install.sh` (prompts or flags), hand-editable. `hermes` is a bool: the second-runtime switch.
Key absent = auto (on when `~/.hermes` is a directory), so an install that predates the key
behaves exactly as before. `hermes_enabled()` is the only reader; it never infers from the
CLI, the skills tree or the session log, only from the flag or the directory.
Skill card: frontmatter `name` + `description` from `~/.claude/skills/crew-*/SKILL.md`;
pack membership from `pack-map.json` (generated from `~/Desktop/cluade/crew-skill-packs/packs/`,
regenerate by rerunning the build snippet in progress.md when packs change).

## Feature freeze (2026-08-16, before the workshop)
The feature set is frozen. Polish, copy, screenshots and rehearsal only; no new rooms,
endpoints or capabilities until Jared lifts it. `workshop-run-sheet.md` is the operating
document for the day. Two things it depends on that must not be broken:
`~/.claude/crew-state/projects/hermes-handoff-demo/` is the evidence behind the
Connections proof row (delete it and the row honestly reverts to "not yet"), and the live
demo must run in the DEFAULT Hermes profile, because the 13 named profiles carry no crew
skills.

Lifted in one place on 2026-08-21: the GitHub onboarding scope (installer questions,
the Hermes runtime switch, start/stop scripts, AGENTS.md and the Antigravity workflow). No
new rooms, no new capabilities beyond that.

## Maintenance log
- Serve: LaunchAgent `com.jared.owneros` (RunAtLoad + KeepAlive), binds 127.0.0.1, port walk
  starting at 4890, chosen URL written to `~/.owneros/os-url.txt`, log at `~/.owneros/os.log`.
- Start/stop: `./start-os.sh` (loads both agents, opens the URL), `./stop-os.sh` (OS only;
  `--all` also stops the Brain).
- Restart after edits: `launchctl unload ~/Library/LaunchAgents/com.jared.owneros.plist && launchctl load ~/Library/LaunchAgents/com.jared.owneros.plist`
- Fish voice upgrade: put the API key alone in `~/.owneros/fish.key`. Capture then records and
  transcribes through Fish; without it the mic uses browser speech (en-AU).
- Brock daily briefing: POST /api/briefing (claude CLI, Brock persona, cached per day in
  ~/.owneros/briefings/, force:true regenerates), GET returns today's cache. POST /api/speak
  reads text through Fish TTS (needs fish.key; optional voice model id alone in
  ~/.owneros/fish-voice.txt); browser speech is the fallback voice. Requires the claude CLI
  to be logged in (interactive `claude` then /login if it ever expires again).
- Capture inbox is watched by the Brain (listed in both scan_config.json copies). If captures
  stop birthing nodes, reload `com.jared.secondbrain` the sanctioned way (launchctl unload/load).
- Workforce (route /launch, all in launch.html): department tiles, single-open roles
  panel, role drawer with three tabs. The Company Register law that used to sit here
  (warm paper, Fraunces, rubric red) was retired at 852aac0; this screen is pure Apple
  language like every other room. Deep links: `?open=<dept>`, `?role=<crew-skill>`
  with optional `&tab=sop|learned`, `?persona=<id>` to filter to a persona's roster.
  Drawer tabs: The role (what it replaces, trust ladder, invoke phrase, and the
  downloadable skill file), The SOP (steps parsed from the skill's own `## Workflow`),
  Learned (every job the role finished, newest first, read from handoff records).
  The old map build lives unused in `workforce-map/`; do not re-embed without Jared's
  ask (map rejected 2026-08-13, GSAP skin reverted same day — tokens at 30fe05e).
- Personas (route /personas): six market shapes from `personas.json`, app-owned and
  hand-edited. Every role and signature chain named there is validated against the
  live roster per request; anything unresolved renders as a visible warning and is
  never dropped. "Copy the kickoff" names the exact chain and roles and spells out
  the Step 0 read and Final Step write so one paste works in either runtime.
- Hermes (route /hermes): the second runtime, read from `~/.claude-os/agents` (falls
  back to `~/Desktop/Hermes-Agent-Network/agents`, source reported in the payload).
  Both that tree and `~/.hermes` are READ-ONLY to this app. Ownership of packs lives
  in `agent-map.json` (app-owned, hand-edited, server never writes it); an owner id
  that resolves to nothing becomes a vacancy, never an error. Covers are rebuilt with
  `sips -s format jpeg -s formatOptions 72 -Z 800` into `assets/hermes/<id>.jpg`;
  re-run when agents change. The page ends in the Connections panel, which checks
  every claim against disk per request.
- Sessions (route /sessions): both runtimes, METADATA ONLY. This room gets projected in
  workshops, so three rules are load-bearing and must not be relaxed: no message text,
  prompt text or file contents are ever read or returned (`lastPrompt` is deliberately
  not parsed, since it is a raw human turn); folder names are shown instead of full
  paths; cost columns are not selected from the database. Claude Code side reads
  head 16KB + tail 64KB per transcript and never the middle (223 sessions, 2.1GB,
  largest single file 92MB), which is why it reports no message count at all rather
  than a wrong one. Hermes side reads `state.db` (root = Brock) plus each profile's own
  `state.db`; there is no agent column in that schema, so the agent IS the profile
  directory, resolved via `agent-map.json` `profile_aliases`. Sessions with
  `message_count <= 2` are excluded: a bulk agent-mirror-sync cron left an untitled
  two-message probe in ten profiles inside the same four minutes. A project folder name
  is a lossy case-collapsed encoding of the cwd and is NEVER reversed into a path.
- The Hermes proof row in `/api/connections` is computed, never hardcoded. A handoff
  record does not name the runtime that wrote it (that is the point of the shared
  cabinet), so `hermes_ran_a_crew_skill()` correlates the newest 25 records' mtimes
  against Hermes session windows in `state.db`, requires that the session also NAME the
  skill in its own messages (tested with a COUNT; no body is read), and bounds an
  unfinished session by its own last message rather than by "now". Timing alone is
  reported as timing, and does not turn the row on. All state.db reads use a
  `mode=ro` URI plus busy_timeout, because the gateways hold WAL locks.
- NEVER split the cabinet. `~/.claude/crew-state` is the one memory root, hardcoded in
  every skill's Step 0 and Final Step; that is the only reason multi-runtime works. An
  old Hermes deployment doc carries a `sed` that would rewrite it to
  `~/.hermes/crew-state`. Do not run it. `/api/connections` asserts that path does not
  exist, and the Hermes page refuses any one-brain claim if it ever does.
- Play library source of truth is `~/.claude/skills/crew-core-using-crew/references/plays.md`
  (47 plays, 12 chains). `playbook.md` in this folder is now only the validated
  fallback: it is used when the live source is missing, unparseable, has no chains, or
  names a step that resolves to no installed skill, and the Plays room says
  "play library fallback active" when that happens.
- Runtime switch (`hermes` in owner.json). Off: every room drops the Hermes nav link
  (the same per-page `/api/owner` snippet that sets the avatar initial), `/hermes` answers
  302 to `/today`, `/api/sessions` does not open any Hermes store and reports
  `hermes.enabled:false`, and the Sessions room hides the Claude/Hermes toggle. On: nothing
  changes from before; the Hermes room and Connections panel stay honest about what is
  and is not on disk. `/api/owner` and `/api/health` both carry the flag. Never gate a
  read on the flag that the constitution already calls read-only; the flag hides, it does
  not protect (the read-only rule does that).
- Install (`install.sh`, from the cloned folder). Asks three things: first name, business,
  one line on the business. Hermes is NEVER mentioned unless `~/.hermes` exists (Jared,
  2026-08-21: the 29 Aug workshop room will not have it and the word confuses); when it
  does exist, one extra question (default yes). The Fish key is flag-only, never asked.
  Every answer is also a flag (`--name --business --about --hermes yes|no --fish-key
  --no-open`) so an agent driving the install from Antigravity or Claude Code can ask in
  chat and run it non-interactively; `--yes` accepts defaults; a missing answer with no
  terminal exits 2 with the flag syntax instead of hanging on `read`. Before asking it
  checks python3, the claude CLI, the CREW skills count (with `find`, never a zsh glob)
  and the cabinet, and says plainly what is missing. It writes only `~/.owneros/*` and
  the LaunchAgent plist (`com.owneros`).
  Hermes yes runs `hermes-sync.sh`: copies `~/.claude/skills/crew-*` into
  `~/.hermes/skills/crew/` (copies, not links, the layout verified with `hermes skills
  list` on 2026-08-16), refuses to run if `~/.hermes/crew-state` exists (split brain), and
  reports how many crew skills Hermes can see. Re-run it after a CREW update. It never
  touches profiles: crew skills run in the DEFAULT Hermes profile only.
- `start-os.sh` / `stop-os.sh` find the plist by label (`com.owneros` first, the original
  `com.jared.owneros` second) and only touch the Brain agent if its plist exists.
- Antigravity is the front door; the owner never opens a terminal (Jared, 2026-08-21).
  The README opens with one paste-prompt: the agent clones to `~/OwnerOS`, reads
  `AGENTS.md`, follows `.agents/workflows/setup-owneros.md` (`/setup-owneros` once the
  folder is the workspace), asks the five questions in chat, runs `install.sh` with
  flags, opens the cockpit, and starts the brand conversation in the same chat by
  following `crew-core-brand-context/SKILL.md`. `.agents/rules/owneros.md` is the
  auto-loaded rules copy. All three restate the invariants with one clarification, not
  a new rule: the OS never writes the cabinet, but a CREW skill run by any agent writes
  exactly what its own SKILL.md says. That is the same contract Hermes proved on
  2026-08-16; Antigravity is a third reader of the same files, untested as of this note.
- Fonts are local (`fonts/`). No CDN at runtime.
- Debug: `tail -20 ~/.owneros/os.log`; `curl localhost:4890/api/health`.
