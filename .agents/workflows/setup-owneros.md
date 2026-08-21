---
description: Set up OwnerOS on this Mac. Checks prerequisites, asks the five onboarding questions in chat, runs the installer, confirms the cockpit is live, and points the owner at their first job.
---

# /setup-owneros

You are setting up OwnerOS for the person in the chat. They have usually just come
from a workshop and installed the CREW skills. Keep it to plain words, one question
at a time, and do not redesign anything. Read `AGENTS.md` first and keep its rules.

## 1. Check what is on the Mac

Run these, then report the results as a short checklist (ok / missing), not a lecture:

```
uname
command -v python3
command -v claude
ls -d ~/.claude/skills/crew-*/ 2>/dev/null | wc -l
test -f ~/.claude/crew-state/brand-context.md && echo brand-ok || echo brand-missing
test -d ~/.hermes && echo hermes-found || echo hermes-absent
test -e ~/.hermes/crew-state && echo SPLIT-BRAIN || echo one-brain
```

- Not Darwin: stop. OwnerOS uses launchd; say it is Mac-only for now.
- python3 missing: tell them to run `xcode-select --install`, then come back.
- claude missing: continue, but say Brock's briefing and the Files assistant will be
  quiet until Claude Code is installed and logged in.
- CREW count is 0: continue, but say Workforce, Plays and Personas will be empty
  until CREW is installed:
  `git clone https://github.com/jaredcroxton/Crew-Agents.git && cd Crew-Agents && bash install.sh --all --global`
- SPLIT-BRAIN: do not delete it. Tell them `~/.hermes/crew-state` exists, that it
  splits the crew's one cabinet in two, and that the Hermes sync will refuse to run
  until they move it aside themselves. Offer the exact `mv` the sync script prints.

## 2. Ask the five questions, one at a time

1. What is your first name?
2. What is your business called?
3. One line: what does the business do?
4. Do you run Hermes Agent on this Mac? (If step 1 found `~/.hermes`, say so and
   suggest yes. If it did not, suggest no and explain that Hermes is optional, the
   cockpit runs without it, and it can be switched on later.)
5. Do you have a Fish Audio API key for Brock's voice? (Optional. If not, the browser
   voice is used. Never ask them to paste a key into the chat if they would rather
   not; they can put it in `~/.owneros/fish.key` themselves later.)

## 3. Run the installer with flags

From the OwnerOS folder:

```
./install.sh --name "<name>" --business "<business>" --about "<one line>" \
             --hermes <yes|no> --fish-key "<key or empty>" --no-open
```

Show them the installer output. If they said yes to Hermes, the sync output tells
them how many crew skills Hermes can see; relay it. If it says STOP, relay that too,
word for word, and do not try to fix it for them.

## 4. Confirm it is live

```
cat ~/.owneros/os-url.txt
curl -s "$(cat ~/.owneros/os-url.txt)/api/health"
```

`ok: true` and the URL is the result. Open it for them: `open "$(cat ~/.owneros/os-url.txt)"`.
If health fails: `tail -20 ~/.owneros/os.log`, then `./start-os.sh`, and read the
log before guessing.

## 5. Point them at the first job

- If step 1 said brand-missing: their first job is the brand conversation. In Claude
  Code, anywhere: **"use the crew, build my brand context"**. Ten minutes, plain
  questions, and it writes the one file every role reads first. Today and Projects
  fill up from there.
- Then: open `/plays`, pick a play, press Copy, paste it into Claude Code.
- If Hermes is on: run crew skills in the default profile (plain `hermes`). Named
  profiles do not see the CREW skills. The record lands in the same cabinet and shows
  up in Projects without anyone being told.
- Update later: `git pull` then `./start-os.sh`.

Stop there. Setup is done when the cockpit is open and they know their first job.
