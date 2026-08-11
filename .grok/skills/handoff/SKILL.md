---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

# Handoff

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/handoff/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Require an active VedaOps lease before writing.
3. Overwrite only `docs-temp/GROK-HANDOFF.md`. That path is ignored and is never authority.

## Process

Write a compact handoff so a fresh agent can continue.

Include:

- current ticket path and status
- start commit and end commit (if any)
- working-tree state
- last checks run
- open blockers
- exact next action
- whether Implementation report is complete and Steward closure is still required
- **Suggested skills** limited to the approved project skills in `AGENTS.md`

Do not duplicate content already in specs, tickets, ADRs, or commits — reference by path.
Redact secrets and credentials.

If the user passed arguments, treat them as the next session's focus and tailor the handoff.

## Completion

`docs-temp/GROK-HANDOFF.md` updated. Ticket remains open until the Steward sets `done`.
