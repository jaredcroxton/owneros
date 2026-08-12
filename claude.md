# OwnerOS — Constitution

Local Business OS cockpit. One stdlib Python server, five screens plus roadmap, PerformOS brand,
ivory default theme with ink stage mode.

## Design law (locked 2026-08-11 evening, supersedes PerformOS brand for this app)
Dark only. Tokens: bg #0b0e13, panel #12151c, card #171b23, line #232936, text #eceef2,
muted #8b93a3, accent coral #ff6b4a (single hot accent), ok teal #2dd4a7, warn amber
#e8b931, bad red #ef5350, info blue #4a9eff (sparingly). Inter UI, JetBrains Mono for
data/ids/dates. Icon sidebar + topbar search + avatar J. Glassy cards radius 14px.
Ambient drifting glow field on body::before. Motion: rise entrances, count-ups, growing
bars, hover lifts, SSE birth toasts; every animation has a non-rAF fallback and a
prefers-reduced-motion path. today.html is the canonical reference implementation.
No Instrument Serif, no ivory, no theme toggle, no external resources at runtime.

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
Playbook: `playbook.md` in this folder (app-owned copy of the CREW plays library) is
the single source for the Plays screen; parsed fresh per request by `parse_playbook()`
(## = category, ### = play, `**Field:**` bullets, `# Chain plays` section). To update
plays: edit playbook.md here (or re-copy from wherever the master lives) and reload
the page. Intents power the plain-words search.
Skill card: frontmatter `name` + `description` from `~/.claude/skills/crew-*/SKILL.md`;
pack membership from `pack-map.json` (generated from `~/Desktop/cluade/crew-skill-packs/packs/`,
regenerate by rerunning the build snippet in progress.md when packs change).

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
- Fonts are local (`fonts/`). No CDN at runtime.
- Debug: `tail -20 ~/.owneros/os.log`; `curl localhost:4890/api/health`.
