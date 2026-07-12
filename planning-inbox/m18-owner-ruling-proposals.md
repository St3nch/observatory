# M18 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Milestone: M18
Date: 2026-07-12

## Purpose

Present the minimum rulings needed to close M18 responsibly without accidentally authorizing recurring execution.

## M18-R1 — v1 execution posture

Proposed ruling:

```text
Recurring capture execution is rejected for Observatory v1.
```

M18 may preserve a future-ready policy and approval checklist. It may not implement or enable recurrence.

## M18-R2 — Maximum cadence classes

Proposed ruling:

Only these planning classes are admitted:

```text
manual_only
monthly_review_candidate
biweekly_review_candidate
weekly_review_candidate
```

Daily, hourly, continuous, event-driven, and adaptive recurrence remain blocked.

## M18-R3 — Budget posture

Proposed ruling:

Every future recurring proposal requires explicit per-run and rolling 30-day ceilings. There are no automatic budget increases, retries, fallback providers, or request-shape changes.

## M18-R4 — Duplicate posture

Proposed ruling:

A deterministic duplicate key must bind scope, immutable panel version, recipe, provider/instrument, scheduled window, and request-shape hash. Any unresolved collision blocks execution.

## M18-R5 — Stop posture

Proposed ruling:

Rights, retention, provider, pricing, endpoint, request-shape, credential, account-limit, panel-version, failure-budget, or owner-disable changes stop the panel before capture.

## M18-R6 — Manual review posture

Proposed ruling:

Manual review is mandatory before first execution, after first success, after every failure or material drift, and before cadence, budget, membership, or source-family changes.

## M18-R7 — No scheduler artifact

Proposed ruling:

M18 creates no scheduler code, cron definition, Windows task, automation file, queue worker, recurring job record, credential path, or provider execution task.

## Recommended decision bundle

```text
ACCEPT the M18 watch-panel policy as future planning guidance
REJECT recurring capture execution for Observatory v1
ACCEPT weekly as the highest planning cadence class
ACCEPT explicit fixed budget ceilings and no automatic increases
ACCEPT deterministic duplicate prevention and fail-closed collisions
ACCEPT stop conditions and mandatory manual review gates
ACCEPT no scheduler or execution artifacts in M18
```

## Deferred

- any real recurring panel;
- exact provider/run budget;
- production scheduling technology;
- credential and secret delivery;
- recurring persistence and audit records;
- alerting and operational response;
- marketplace or AI/GEO recurrence;
- production API/MCP integration.
