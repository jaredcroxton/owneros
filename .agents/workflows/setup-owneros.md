---
description: Set up OwnerOS on this Mac from chat alone, for Antigravity's own agent. The canonical procedure lives in the Claude Code skill at .claude/skills/setup-owneros/SKILL.md; this workflow follows it.
---

# /setup-owneros

Read `.claude/skills/setup-owneros/SKILL.md` in this folder (or in `~/OwnerOS` if this
folder is not OwnerOS; clone it first with
`git clone https://github.com/jaredcroxton/owneros.git ~/OwnerOS`) and follow it step
by step, exactly as written. Read `AGENTS.md` first and keep its rules.

One difference for an agent that is not Claude Code: CREW skills do not load for you
automatically. When a step says "invoke the skill", open
`~/.claude/skills/<skill-name>/SKILL.md`, read it, and follow it exactly, including its
Step 0 and its Final Step. The file is the procedure.
