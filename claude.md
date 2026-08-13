# OwnerOS — Constitution

Local Business OS cockpit. One stdlib Python server, five screens plus roadmap, PerformOS brand,
ivory default theme with ink stage mode.

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
- Workforce (route /launch, all in launch.html): "The Company Register" design,
  built 2026-08-13 from scratch after Jared reverted a GSAP-look reskin. Its own law
  (this screen only; coral law governs the rest): warm paper #F6F3EC, ink #161310,
  single rubric red #B42318 (index numerals, links, worked-this-month dot, stamp —
  nothing else), Fraunces (variable, local) + IBM Plex Mono 400/500 data voice,
  14px floor, radius 2px, no shadows/gradients/glass, light only. Structure:
  masthead nameplate + double rule + compiled line, Brock editor's-note card,
  underline search with red match counter, status legend, 17 numbered department
  entries (01-17) on a 1px spine, single-open wells with dotted-leader role lines
  numbered 001-089 (stable by API order), personnel-file drawer (salary AUD
  units-only, $ stripped; COPIED stamp on copy), 72px two-letter rail (bottom bar
  ≤390px), bottom-sheet drawer ≤560px. Deep link `/launch?open=<dept>` preserved.
  Entrance rule learned hard: base state = final state, animations fill backwards;
  never base-hidden + forwards. The old map build lives unused in `workforce-map/`;
  do not re-embed without Jared's ask (map rejected 2026-08-13, GSAP skin reverted
  same day — its tokens live in git history at 30fe05e if ever wanted).
- Fonts are local (`fonts/`). No CDN at runtime.
- Debug: `tail -20 ~/.owneros/os.log`; `curl localhost:4890/api/health`.
