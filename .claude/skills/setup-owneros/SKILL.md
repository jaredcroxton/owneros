---
name: setup-owneros
description: Set up OwnerOS on this Mac from the chat alone. Clones or updates the repo, checks prerequisites, asks three short questions one at a time, runs the installer, confirms the cockpit is live in the browser, then starts the owner's first job with the crew. Invoke when someone says "set up OwnerOS", "install OwnerOS", pastes the OwnerOS setup prompt, or types /setup-owneros. The owner never touches a terminal; you run every command.
---

# Set up OwnerOS

You are setting up OwnerOS for the person in this chat. They have come from a
workshop that put Claude Code and the CREW skills on this Mac. They will not open a
terminal at any point. You run every command yourself (they click Allow when asked),
show them what matters, and ask one question at a time in plain words. Read
`AGENTS.md` in the OwnerOS folder first and keep its rules. Do not redesign anything.

One rule of tone: **do not mention Hermes Agent unless step 1 finds `~/.hermes`.**
Almost nobody has it. If it is not there, the word never comes up.

## 0. Find or fetch OwnerOS

If this skill lives inside the folder you are working in, that folder is OwnerOS.
Otherwise OwnerOS lives at `~/OwnerOS`. Safe to run more than once:

```
test -d ~/OwnerOS/.git && git -C ~/OwnerOS pull --ff-only || git clone https://github.com/jaredcroxton/owneros.git ~/OwnerOS
```

If `git` is missing, macOS offers to install the command line tools in a dialog.
Tell the owner to click Install, wait, say "done", and run the line again. That
dialog also installs python3. If the pull fails because the folder was edited, say
so and stop; do not force it.

Call the folder `$OS` from here on.

## 1. Check what is on the Mac

Run these, then report a short checklist (ok / missing), not a lecture:

```
uname
command -v python3
python3 "$OS/server.py" --find-claude
find ~/.claude/skills -maxdepth 1 -type d -name 'crew-*' 2>/dev/null | wc -l
test -f ~/.claude/crew-state/brand-context.md && echo brand-ok || echo brand-missing
test -d ~/.hermes && echo hermes-found || echo hermes-absent
```

- Not Darwin: stop. OwnerOS uses launchd; say it is Mac-only for now.
- `--find-claude` prints a path: good, Brock can speak. It prints "Claude CLI not
  found": run `which claude` yourself; if that finds one, write its full path into
  `~/.owneros/claude-bin.txt` and check again. If there is truly no CLI, every room
  still loads, Brock's briefing and the Files assistant stay quiet, and you can offer
  the official installer (`curl -fsSL https://claude.ai/install.sh | bash`). The CLI
  shares the sign-in this extension already has.
- CREW count is 0: continue, but say Workforce, Plays and Personas stay empty until
  the CREW skills are installed, and offer to install them now:
  `git clone https://github.com/jaredcroxton/Crew-Agents.git ~/Crew-Agents && bash ~/Crew-Agents/install.sh --all --showcase --global`
  Skills load on the next session; say so.
- hermes-absent: say nothing about it. Do not list it in the checklist.
- hermes-found: also run `test -e ~/.hermes/crew-state && echo SPLIT-BRAIN || echo one-brain`.
  On SPLIT-BRAIN, delete nothing. Explain that `~/.hermes/crew-state` is a second
  cabinet that splits the crew's one brain, that the Hermes sync will refuse to run
  while it exists, and offer to park it with a rename, only if they say yes:
  `mv ~/.hermes/crew-state ~/.hermes/crew-state.parked-$(date +%Y%m%d)`

## 2. Ask three questions, one at a time

1. What is your first name?
2. What is your business called?
3. One line: what does the business do?

Only if step 1 found `~/.hermes`, a fourth: "Hermes Agent is on this Mac. Connect
the crew to it too?" Suggest yes. Otherwise there is no fourth question.

Do not ask about voice keys or anything else. Setup is three answers.

## 3. Run the installer with flags

```
"$OS/install.sh" --name "<name>" --business "<business>" --about "<one line>" --no-open
```

Add `--hermes yes` or `--hermes no` only when the fourth question was asked. Show
the output. If a Hermes sync line appears, relay it; if it says STOP, relay it word
for word and do not work around it.

## 4. Confirm it is live, in the browser

```
cat ~/.owneros/os-url.txt
curl -s "$(cat ~/.owneros/os-url.txt)/api/health"
open "$(cat ~/.owneros/os-url.txt)"
```

`"ok": true` is the result. If health fails, read `tail -20 ~/.owneros/os.log`
before guessing, then `"$OS/start-os.sh"`.

## 5. Start the first job, here in the chat

- If step 1 said brand-missing, the first job is the brand conversation, and it
  happens right here. Ask one thing first: "Does the business have a website? Paste
  the address." Then invoke the `crew-core-brand-context` skill (installed at
  `~/.claude/skills/crew-core-brand-context`; if it is not loaded in this session,
  read its SKILL.md and follow it exactly, Step 0 and Final Step included). If they
  gave a website, read it before asking anything and treat it as the main source:
  name, what they do, products and prices, who buys, how they sound, and the visual
  identity (brand colours as hex, fonts, the logo). Fill the skill's Visual identity
  line and Found online from the site, then ask only what the site does not answer.
  It writes `~/.claude/crew-state/brand-context.md`, the file every role reads first,
  and every design and web skill builds to those colours from then on. Writing that
  file is the skill's job, not OwnerOS's.
- Then the first play: open `<url>/plays` for them, let them pick one, and when
  they paste it back, the `crew-core-using-crew` dispatcher routes it. The record
  it files lands in the cabinet and shows up in Projects on the next reload.
- Only if Hermes was connected: crew skills run in the default profile (plain
  `hermes`), never `hermes -p <name>`. Same cabinet, same Projects room.
- For next time: suggest they open `~/OwnerOS` as their workspace, so
  `/setup-owneros` and the OwnerOS rules are on hand. Updating later is one
  sentence: "update OwnerOS" means `git -C "$OS" pull --ff-only && "$OS/start-os.sh"`.

Stop when the cockpit is open and the first job has started. Setup is not a build.
