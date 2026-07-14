# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-14

---

## Current Phase

The Observatory has completed DB-2 reconciliation and entered fresh DB-3 planning:

```text
DB-1 is trusted and complete.
DB-2 is trusted, accepted, and complete.
DB-3 is active for fresh planning and specification only.
DB-4 is inactive, with no active or authoritative artifact.
```

Current transition authority:

```text
decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
```

Observatory v1 remains accepted at the bounded proof-system ceiling by `decisions/2026-07-12-observatory-v1-acceptance.md`.

---

## Active Milestone

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

DB-3 is planning and specification only. It derives solely from accepted DB-1
authority, the exact accepted DB-2 freeze, accepted roadmaps/contracts/decisions,
and the 2026-07-14 owner decision. It grants no implementation authority.

---

## Accepted DB-2 checkpoint

The owner accepted the exact immutable DB-2 freeze identified by:

```text
path: planning-inbox/db2-physical-data-contract-freeze-specification.md
version: 0.2.1
sha256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
```

DB-2 is now the last trusted completed database milestone. The candidate file's
historical self-status remains unchanged because the decision binds its exact bytes.

The untrusted later DB-3 and DB-4 artifacts have been permanently retired and deleted from the active repository. Git history is sufficient archival retention.

The five untrusted later DB-3/DB-4 artifacts remain permanently retired and deleted.
They must not be restored, salvaged, reused, copied, paraphrased, or reconstructed.
DB-4 remains inactive. No PostgreSQL or database-control-plane implementation is
authorized.

---

## Current Task

Begin DB-3 fresh by preparing its planning approach from accepted authority:

1. re-read the DB-3 roadmap gate and exact accepted DB-2 freeze;
2. define the specification work sequence without creating implementation artifacts;
3. preserve every accepted identity, lifecycle, rights, retention, exposure,
   forbidden-persistence, and H1-H22 implication;
4. do not use or reconstruct any retired DB-3/DB-4 artifact.

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
DB-2 — Physical Data-Contract Freeze
```

Active for fresh planning and specification only:

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

Inactive with no current artifact or authority:

```text
DB-4
```

Planned and inactive:

```text
DB-4 through DB-10
```

The governing post-v1 sequence remains `POST_V1_DATABASE_ROADMAP.md`, as corrected
by the recovery decision and the 2026-07-14 DB-2 closure decision. No milestone
implies the next milestone.

---

## Tool Posture

- Use Codex native local tools for ordinary PowerShell, filesystem, Git, tests, and code work.
- Use `ob-dev-mcp` only within its current bounded file-oriented surface.
- Do not use old `ob-dev` Git tools.
- Do not implement or activate PostgreSQL tools during DB-3 planning.
- Tool availability never creates roadmap authority.
