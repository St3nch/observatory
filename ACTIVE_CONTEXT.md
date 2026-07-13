# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-13

---

## Current Phase

The Observatory is in database-phase recovery from the last trusted checkpoint:

```text
DB-1 is closed and trusted.
DB-2 is active for reconciliation and owner review only.
DB-3 and DB-4 closure/activation claims are suspended.
```

Recovery authority:

```text
decisions/2026-07-13-database-phase-recovery-to-db1.md
```

Observatory v1 remains accepted at the bounded proof-system ceiling by `decisions/2026-07-12-observatory-v1-acceptance.md`.

---

## Active Milestone

```text
DB-2 — Physical Data-Contract Freeze Reconciliation
```

This is not ordinary forward milestone execution. The canonical DB-2 freeze must be reconciled and re-reviewed from the trusted DB-1 checkpoint.

No later database milestone is active.

---

## Why Recovery Is Required

The canonical DB-2 freeze claims accepted v0.1.1 status, but its content does not contain all v0.1.1 corrections and still violates its own singular-classification rule.

The later DB-3 readiness review relied on the unsupported claim that the reconciled freeze was complete and conflict-free.

Therefore:

- DB-2 closure is suspended;
- DB-3 specifications are candidate material only;
- DB-3 closure and DB-4 activation are suspended;
- no PostgreSQL or database-control-plane work is authorized.

---

## Current Task

Reconcile DB-2 without widening authority:

1. compare the canonical freeze with the correction package;
2. apply only corrections that survive fresh DB-1-grounded review;
3. verify every concept has exactly one primary classification;
4. verify identity, provenance, scope, rights, retention, write, read, and hammer implications;
5. keep forbidden persistence explicit;
6. prepare a fresh DB-2 readiness review and owner gate.

---

## Immediate Non-Goals

Do not start:

- PostgreSQL database creation
- role or credential creation
- SQL or DDL
- migration files or migration execution
- disposable database lifecycle
- real-PostgreSQL hammers
- database-control-plane expansion
- synthetic or real persistence
- provider calls or paid pulls
- recurring capture
- production API/MCP exposure
- dashboard or operator console work
- customer or private data handling
- raw capture
- customer-facing reports
- marketplace scraping
- browser-extension capture
- strategy, recommendation, conclusion, or report-state storage
- cloud backup upload
- automatic backup jobs
- destructive cleanup
- production deployment

No schema goblin jazz. The paperwork must become true before the database becomes real.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer.

Customer records and customer first-party analytics stay outside Observatory durable storage.

LLMs and agents receive shaped evidence through typed boundaries, not direct SQL access or database credentials.

Provider disagreement is first-class evidence. Proprietary provider scores are provider-attributed testimony, not facts about the web.

Rights and retention fail closed.

Hammer tests are a hard gate for implementation, and database hammers require a real authorized substrate.

Killed ancestor concepts remain killed.

---

## Current Completion State

Trusted and closed:

```text
M0, M0.1, M1 through M20
DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
```

Active for recovery:

```text
DB-2 — Physical Data-Contract Freeze Reconciliation
```

Suspended pending revalidation:

```text
DB-2 closure
DB-3 activation and closure
DB-4 activation
```

Planned and inactive:

```text
DB-3 through DB-10
```

The governing post-v1 sequence remains `POST_V1_DATABASE_ROADMAP.md`, as corrected by the recovery decision. No milestone implies the next milestone.

---

## Tool Posture

- Use Codex native local tools for ordinary PowerShell, filesystem, Git, tests, and code work.
- Use `ob-dev-mcp` only within its current bounded file-oriented surface.
- Do not use old `ob-dev` Git tools.
- Do not add PostgreSQL tools to `ob-dev-mcp` during DB-2 recovery.
- Tool availability never creates roadmap authority.
