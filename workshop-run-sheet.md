# OwnerOS — workshop run sheet

Frozen build. No capability changes before the workshop. This is the sheet for polish,
rehearsal, and the live demo.

---

## 1. Pre-flight, five minutes before you present

```bash
./start-os.sh
```

Then, in order:

1. **Warm the Brain.** Open `/brain` and leave it. The graph takes longer than six seconds
   to paint, and a cold open on stage reads as a broken app. Once warmed it stays warm.
2. **Check the truth panel.** Open `/hermes`, scroll to Connections. It should read
   **8 of 10 connected**, with exactly three honest "not yet" rows and the one-brain
   paragraph at the bottom. If the Hermes proof row says "not yet", stop and read §5.
3. **Confirm the evidence project exists.**
   ```bash
   ls ~/.claude/crew-state/projects/hermes-handoff-demo
   ```
   One file. See §4 — do not delete it.
4. **Silence anything that will interrupt.** The room is a local cockpit; nothing phones
   home, but your machine still will.

Live URL is written to `~/.owneros/os-url.txt` (normally `http://localhost:4890`).

---

## 2. The arc

Eleven rooms is too many to walk through. Use five, in this order, and let the others be
discovered.

| # | Room | The one line to say | What to point at |
|---|---|---|---|
| 1 | **Today** | "This is what needs me, before I open anything else." | The needs-me count, then Brock's card |
| 2 | **Workforce** | "Eighty-eight roles. Not chatbots — each one has a written procedure." | Open Finance → Invoice workflow → **The SOP** tab |
| 3 | *(same drawer)* | "And it learns. This is what it took away from the last three jobs." | The **Learned** tab on `crew-design-documents` |
| 4 | **Plays** | "You don't have to know which role to call. You say it in your words." | A chain, then **Copy chain prompt** |
| 5 | **Hermes** | "Two runtimes, one brain — and here is the receipt." | The chart, then Connections |

**The single strongest beat is the Learned tab.** A downloadable skill file cannot do
that, and it is the thing the rival product in the reel does not have. Spend time there.

Deep links, if you would rather jump than click:

- `/launch?role=crew-finance-invoice-workflow&tab=sop`
- `/launch?role=crew-design-documents&tab=learned`
- `/personas?p=trades`
- `/sessions?side=hermes`

---

## 3. The live handoff demo

The claim: **one brain, two runtimes.** The proof: a skill run in Hermes shows up in
OwnerOS, which was never told about it.

**Run it in the default profile.** The thirteen named profiles keep their own skill
folders and carry no crew skills; only the default install can see them. `hermes -p
bobbuilder` will not work for this.

**Step 1 — show the room before.** On `/projects`, point out the project list.

**Step 2 — run it.** In a terminal:

```bash
hermes -z "Run the crew skill crew-core-idea-pressure-tester. New project, call it hermes-demo-live. The idea to pressure-test: [say a real one from the room]. Follow the skill exactly, including Step 0 and the Final Step: read ~/.claude/crew-state/brand-context.md first, and write your record to ~/.claude/crew-state/projects/hermes-demo-live/ when you finish."
```

It took under two minutes in rehearsal. While it runs, narrate: it is reading the same
brand context file every Claude Code skill reads, because the path is hardcoded in the
skill, not supplied by the runtime.

**Step 3 — the reveal.** Reload `/projects`. The new project is there. Nothing was
imported, synced, or configured. Then open `/hermes` → Connections and show the proof row
naming the skill and the Hermes session id.

**Fallback if it fails on stage:** say "it did this last night, here it is" and show the
existing `hermes-handoff-demo` project plus the Connections row, which is computed from
disk and still true. Do not re-run it twice in front of people.

---

## 4. Protect the evidence project

`~/.claude/crew-state/projects/hermes-handoff-demo/` is now the evidence behind the
Connections proof row.

- **Do not delete it before the workshop.** If it goes, the row honestly flips back to
  "not yet" — the panel working as designed, but a bad surprise on stage.
- OwnerOS will never touch it. The app is read-only over the whole cabinet; its only
  write path is the capture inbox. No marker file was added to that folder for the same
  reason.
- If you do want it gone afterwards, delete it *after* the workshop, and expect the row
  to change. Running the demo again re-creates the evidence.

---

## 5. Failure modes, and what to say

| Symptom | Cause | Fix, or the line |
|---|---|---|
| Proof row says "not yet" | Evidence project deleted, or Hermes `state.db` unreadable | Re-run the demo (§3). On stage: "that row is computed live, and right now it can't prove it — which is the point." |
| Brain panel is blank | Iframe still loading, or the Brain agent is down | Warm it first (§1). To restart: `launchctl unload/load ~/Library/LaunchAgents/com.jared.secondbrain.plist` |
| Plays says "fallback active" | The live crew library moved or broke | Still fully usable — it fell back to the app copy on purpose. Don't debug it live. |
| A room won't load | Server died | `tail -20 ~/.owneros/os.log`, then `./start-os.sh` |
| Brock won't speak | No Fish key | Browser voice takes over automatically. Say nothing. |

---

## 6. What not to put on the projector

- **Sessions** is metadata-only by design: no message text, no prompts, folder names
  instead of full paths, no costs. That is safe to show. Don't go hunting for transcripts
  to prove a point.
- **Files** browses your real Desktop. Either skip it or know what is on screen first.
- **Capture** writes to the Brain. Fine to demo — capture something real and watch the
  node appear — but whatever you type is kept.
- The cabinet holds client names. `/projects` is the room most likely to show one, so
  scan the list before you present.

---

## 7. After the workshop

- Nothing to reset. The app wrote nothing except any captures you made.
- `active-project` currently points at `hermes-handoff-demo`. Switch it when you next
  start real work: *"New project, call it [name]"* or *"Switch to [project]"*.
- If you demoed live, you will have a second evidence project (`hermes-demo-live`). Either
  is enough for the proof row.

---

## The numbers, as at 2026-08-16

88 roles · 108 capabilities · 47 plays · 12 chains · 6 personas · 10 Hermes agents ·
17 sub-agents · 5 packs with no named agent · 8 of 10 connections proven ·
223 Claude Code sessions · 360 Hermes sessions.

Say the ones you can defend. Every one of them is read off disk at request time, so if
someone asks "is that live?", the answer is yes, and you can reload in front of them.
