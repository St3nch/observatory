---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Write a compact handoff so a fresh agent can continue the work.

For Observatory, overwrite `docs-temp/GROK-HANDOFF.md`. The directory is ignored and the
handoff is working state, never project authority.

Include the current ticket, starting commit, working-tree state, last checks run, open
blockers, and exact next action. Include a "suggested skills" section limited to the
approved project skills in `AGENTS.md`.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
