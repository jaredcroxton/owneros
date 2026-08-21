# OwnerOS workspace rules

Read `AGENTS.md` at the root of this folder before doing anything here. It is short
and it is the contract. The six rules that matter most, so they are never out of view:

1. OwnerOS never writes into `~/.claude/crew-state`. Only a CREW skill writes there,
   and only what its own SKILL.md says. Never create, move, rename, fix, or tidy a
   record yourself.
2. Never create `~/.hermes/crew-state`. One cabinet, one brain.
3. Never write into `~/.claude/skills` or `~/.hermes/profiles`.
4. Never delete. Park with a rename, only after the owner says yes.
5. No cloud at runtime. No CDN, no analytics, no remote calls. Fish Audio only, and
   only when `~/.owneros/fish.key` exists.
6. Setup is configuration, not a build. No new rooms, endpoints, or capabilities
   unless the owner asks for exactly that.

The owner does not use a terminal. You run every command and show them what matters.
Setup is `/setup-owneros` (`.agents/workflows/setup-owneros.md`). Product changes
start with `claude.md`. No em dashes in anything you write here.
