---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

# Implement

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Require one Project Steward-approved ticket path under `tickets/` with status
   `ready-for-agent` or `in-progress`.
3. Read `VISION.md`, `VOCABULARY.md`, both decision registers, `AGENTS.md`, the ticket,
   its parent spec when named, and any relevant ADR.
4. Require an active VedaOps lease before any filesystem write (including `docs-temp/`).
   Renew when fewer than 30 minutes remain. Align `expected_git_head` with reality.
5. Record the starting commit on the ticket. Working tree must have no unexplained changes.
6. Do not edit product authority to make code fit. Propose changes to the Steward.

## Process

1. Restate ticket boundary, acceptance behavior, approved seams, and deferred work. Stop
   only for a contradiction that materially changes the implementation.
2. Set ticket **Status** to `in-progress` when starting (under lease).
3. Use project-local `tdd` in small vertical slices. The ticket pre-authorizes its seams.
4. Run the narrow relevant test after each slice. Run Ruff and mypy regularly.
5. Never make live provider calls from ordinary tests. Use real PostgreSQL when the claim
   depends on PostgreSQL behavior.
6. When slices are done, run full test, lint, and typecheck commands.
7. Invoke project-local `code-review` against the recorded starting commit. Resolve valid
   findings and rerun affected checks.
8. Fill the ticket **Implementation report** (end commit, acceptance evidence, unproven
   limits, remaining review findings). Set **Status** to `review` when ready for Steward
   closure. Never set `done`. Never fill **Closure**.
9. Commit the bounded ticket work only after checks and review pass. Do not push or broaden
   the ticket unless the Steward directs it.
10. Invoke `handoff` when the session ends without Steward closure.

## Completion

Code committed, checks green, review addressed or residual findings listed, ticket at
`review` with a complete Implementation report. Only the Project Steward sets `done`.
