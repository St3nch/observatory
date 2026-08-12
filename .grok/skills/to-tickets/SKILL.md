---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, published to the configured tracker — edges as text in one file per ticket locally, or native blocking links on a real tracker.
disable-model-invocation: true
---

# To Tickets

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/to-tickets/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Prefer an accepted parent at `docs/specs/<slug>.md`. If only conversation is available,
   require Steward confirmation that it is enough to ticket.
3. Read `VOCABULARY.md` and relevant decisions/ADRs.
4. Do not use an issue tracker, triage labels, `.scratch/`, or `docs/agents/`.
5. Create no ticket index or README under `tickets/`.

## Process

### 1. Gather context

Work from the accepted spec and conversation. If the user passes a path, read it fully.

### 2. Explore the codebase (optional)

Understand current code enough to size slices. Prefer prefactor opportunities when they make
the change easy. Use domain vocabulary.

### 3. Draft vertical slices

Break work into **tracer bullet** tickets:

- Each slice is a narrow complete path through required layers — vertical, not one layer
- A completed slice is demoable or verifiable alone
- Each slice fits one fresh context window
- Prefactors first when needed

Give each ticket **blocking edges** — other tickets that must complete first.

**Wide refactors** are the exception: use expand → migrate batches → contract, each as its
own ticket with honest blockers, rather than forcing a false vertical slice.

### 4. Quiz the Steward / Chaz

Present a numbered list. For each ticket show:

- **ID** (feature-prefix form, e.g. `CE-01`, `API-03`)
- **Title**
- **Blocked by**
- **What it delivers**

Ask: granularity, blocking edges, merge/split. Iterate until the breakdown is approved.

### 5. Publish tickets under `tickets/`

After approval, write one file per ticket:

`tickets/<feature-prefix>-<ordinal>-<slug>.md`

Examples: `tickets/CE-01-attempt-record.md`, `tickets/API-03-cursor-page.md`.

Create `tickets/` lazily. Number in dependency order when helpful; blockers must still be
listed in each file. Do not modify the parent spec. Do not close or mark tickets `done`.

## Ticket template

```markdown
# <ID> — <Title>

**Status:** ready-for-agent
**Parent spec:** docs/specs/<slug>.md | none
**Blocked by:** None — can start immediately | <ID> — <title>, …
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work — not a layer-by-layer chore list.

## Acceptance criteria

- [ ] Observable criterion 1
- [ ] Observable criterion 2

## Verification

- Commands: `uv run pytest -q`, `uv run ruff check .`, `uv run mypy` as applicable
- Substrate: ordinary tests | real PostgreSQL | other named substrate
- Forbidden claims: no live provider in ordinary tests; mocks ≠ durability proof

## Out of scope

…

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
```

Status vocabulary: `draft` · `ready-for-agent` · `in-progress` · `review` · `done` ·
`blocked` · `superseded`. Only the Project Steward sets `done`.

Avoid specific file paths or code snippets except prototype-derived decision fragments.

## Completion

Approved ticket files exist under `tickets/` with `ready-for-agent` (or Steward-chosen
status). Next: `implement` on a frontier ticket (all blockers `done` or none).
