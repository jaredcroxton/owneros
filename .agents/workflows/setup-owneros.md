---
description: Set up OwnerOS on this Mac from chat alone. Clones or updates the repo, checks prerequisites, asks the five onboarding questions one at a time, runs the installer, confirms the cockpit is live in the browser, and starts the owner's first job. The owner never touches a terminal; you run every command.
---

# /setup-owneros

You are setting up OwnerOS for the person in this chat. They have come from a
workshop that put Claude Code and the CREW skills on this Mac, maybe Hermes Agent.
They will not open a terminal at any point. You run every command yourself, show
them what matters, and ask one question at a time in plain words. Read
`AGENTS.md` in the OwnerOS folder first and keep its rules. Do not redesign anything.

## 0. Find or fetch OwnerOS

If this workflow file lives inside the folder you are working in, that folder is
OwnerOS. Otherwise OwnerOS lives at `~/OwnerOS`:

```
test -d ~/OwnerOS/.git && git -C ~/OwnerOS pull --ff-only || git clone https://github.com/jaredcroxton/owneros.git ~/OwnerOS
```

If `git` is missing, macOS will offer to install the command line tools in a
dialog. Tell the owner to click Install, wait for it, then say "done", and run
the clone again. That dialog also installs python3.

Call the folder `$OS` from here on.

## 1. Check what is on the Mac

Run these, then report a short checklist (ok / missing), not a lecture:

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
- claude missing: continue, but say Brock's briefing and the Files assistant stay
  quiet until Claude Code is installed and signed in. The rooms still load.
- CREW count is 0: continue, but say Workforce, Plays and Personas stay empty until
  the CREW skills are installed. Offer to install them now:
  `git clone https://github.com/jaredcroxton/Crew-Agents.git ~/Crew-Agents && bash ~/Crew-Agents/install.sh --all --global`
- SPLIT-BRAIN: do not delete anything. Explain that `~/.hermes/crew-state` is a
  second cabinet that splits the crew's one brain, that the Hermes sync will refuse
  to run while it exists, and offer to park it with a rename (never a delete):
  `mv ~/.hermes/crew-state ~/.hermes/crew-state.parked-$(date +%Y%m%d)`
  Only run that if they say yes.

## 2. Ask the five questions, one at a time

1. What is your first name?
2. What is your business called?
3. One line: what does the business do?
4. Do you run Hermes Agent on this Mac? If step 1 found `~/.hermes`, say so and
   suggest yes. If not, suggest no and say Hermes is optional: the cockpit runs
   without it and it can be switched on later.
5. Do you have a Fish Audio API key for Brock's voice? Optional. If not, the
   browser voice is used. If they have one and would rather not paste it in chat,
   skip it here; they can drop it into `~/.owneros/fish.key` later and you can do
   that for them if they hand it over.

## 3. Run the installer with flags

```
"$OS/install.sh" --name "<name>" --business "<business>" --about "<one line>" \
                 --hermes <yes|no> --fish-key "<key or empty>" --no-open
```

Show the output. If they said yes to Hermes, the sync line says how many crew
skills Hermes can see; relay it. If it says STOP, relay it word for word; do not
work around it.

## 4. Confirm it is live, in the browser

```
cat ~/.owneros/os-url.txt
curl -s "$(cat ~/.owneros/os-url.txt)/api/health"
open "$(cat ~/.owneros/os-url.txt)"
```

`"ok": true` is the result. If you have a browser tool, open the Today room and
look: the owner's initial top right, their name in the greeting. If health fails,
read `tail -20 ~/.owneros/os.log` before guessing, then `"$OS/start-os.sh"`.

## 5. Start the first job, here in the chat

- If step 1 said brand-missing, the first job is the brand conversation, and it
  can happen right here. Read `~/.claude/skills/crew-core-brand-context/SKILL.md`
  and follow it exactly, including its Step 0 and Final Step. It is a short
  plain-language conversation; it writes `~/.claude/crew-state/brand-context.md`,
  the file every role reads first. Writing that file is the skill's job, not
  OwnerOS's; write exactly what the skill says and nowhere else. (If the owner
  prefers Claude Code, they say "use the crew, build my brand context" there.)
- Then the first play: open `<url>/plays` for them, let them pick one, and when
  they paste the play into this chat, read
  `~/.claude/skills/crew-core-using-crew/SKILL.md` and follow it. The record it
  files lands in the cabinet and shows up in Projects on the next reload.
- If Hermes is on: crew skills run in the default profile (plain `hermes`),
  never `hermes -p <name>`. Same cabinet, same Projects room.
- For next time: suggest they open `~/OwnerOS` as their workspace in Antigravity,
  so `/setup-owneros` and the OwnerOS rules are on hand. Updating later is one
  sentence to you: "update OwnerOS" means `git -C "$OS" pull --ff-only && "$OS/start-os.sh"`.

Stop when the cockpit is open and the first job has started. Setup is not a build.
