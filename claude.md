# OwnerOS — Constitution

Local Business OS cockpit. One stdlib Python server, eleven rooms (Today, Projects, Brain,
Capture, Workforce, Plays, Personas, Hermes, Sessions, Files, Roadmap), PerformOS brand,
Apple language throughout.

## Design law v4 — the Apple language (locked 2026-08-13 night, OS-wide)
Distilled from Jared's five references (GSAP, Superr, Portrait, dope.security, Apple
MacBook Neo) after he rejected every "AI-feel" build. The five laws: one ink; one
rationed accent; whisper elevation; two type voices with strict size ownership;
color lives in content, never chrome.

Tokens: paper #ffffff, band #f5f5f7, nav #fafafc (blur 20px), hover wash #e8e8ed,
ink #1d1d1f, mid #707070 (secondary text), deep #474747 (nav), hairline #d6d6d6
(rare), blue #0071e3 (filled pill CTAs ONLY, never text/decoration), link #0066cc
(inline text links only), ember #b64400 (tiny status labels, at most once per
screen, e.g. needs-me counts). Status language: ink = done/positive, mid = quiet,
ember = needs attention. NO other colors in chrome; teal/coral/amber retired.

Type: system font stack ("SF Pro Display"/-apple-system/system-ui — real SF on the
Mac this runs on). Display 56-96px weight 600/700 tracking -0.015em, section heads
28-40px weight 600, body 17px 400 lh 1.47 tracking -.022em, captions 12-14px.
Data/ids/dates in ui-monospace (SF Mono) 12-14px. Nothing under 12px.

Structure: NO sidebar — 44px sticky global nav bar (blurred #fafafc, wordmark left,
8 room links center at 12px, avatar right). Full-bleed sections alternating
#ffffff / #f5f5f7 with 80-120px vertical padding; inner column max 980-1200px.
Section separation by band alternation, never dividers. Cards 28px radius,
borderless, no shadow (1px oklab hairline at ≤8% only when floating on same-color
surface). Buttons: pill 980px radius — filled blue for the one primary action,
ghost 1px ink outline for secondary, text+arrow links (#0066cc ›) for tertiary.
Headlines can center; body copy always left-aligned. No gradients, no glass except
the nav blur, no glow, no decorative color, no icons where a word works.

Motion: few, fast, purposeful — 200-400ms ease-out fades/rises on band entry,
count-ups on stats, smooth sheet slides. Base state = final state; animations fill
backwards from keyframes (never base-hidden + forwards). Full
prefers-reduced-motion path. today.html is the canonical reference implementation.
No theme toggle, no dark mode, no external resources at runtime. Old dark builds
live in git history (coral canon ≤ a2e22cf, GSAP 30fe05e, Register 6b42127).

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
- Fonts are local (`fonts/`). No CDN at runtime.
- Debug: `tail -20 ~/.owneros/os.log`; `curl localhost:4890/api/health`.
