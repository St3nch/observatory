# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-13

---

## Current Phase

The Observatory is in:

```text
DB-1 post-v1 audit reconciliation and database-phase roadmap planning
```

Observatory v1 remains accepted at the bounded proof-system ceiling by `decisions/2026-07-12-observatory-v1-acceptance.md`. The owner accepted the post-v1 audit as advisory input and activated database-phase planning through `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`. This opens reconciliation, typed-read corrections, hammer/ruling work, and the physical data-contract-freeze plan only. It does not authorize Postgres creation, DDL, migration files or execution, real ingestion, production, customer data, or strategy storage.

---

## Active Milestone

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

M0, M0.1, M1 through M20, DB-1, and DB-2 are complete and committed. DB-3 is active by `decisions/2026-07-13-db2-closure-and-db3-activation.md`.

---

## Current Task

Execute DB-3 specification work only:

- specify PostgreSQL instance and database-class boundaries;
- specify role, privilege, credential, and secret boundaries without creating them;
- specify naming, identity, lifecycle, index, constraint, append-only, audit-first, and raw-pointer mechanisms;
- specify backup-before-migration and migration-governance requirements;
- map every physical mechanism to accepted hammers;
- prepare DB-3 closure readiness and a separate DB-4 gate.

DB-4 remains inactive until a separate owner decision.

Postgres creation, DDL, migration files, migration execution, database credentials, real ingestion, provider calls, and production work remain unauthorized.

---

## Immediate Non-Goals

Do not start:

- provider calls or new paid pulls
- recurring capture
- production API/MCP exposure
- dashboard or operator console work
- live Postgres/schema/migrations
- customer data handling
- customer-facing reports
- marketplace scraping
- browser-extension capture
- strategy or recommendation storage
- cloud backup upload
- automatic backup jobs
- destructive cleanup
- production deployment

No schema goblin jazz. No provider confetti cannon. No dashboard side quest.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer, such as SearchClarity, Neon Ronin, or Kaizen.

Customer records and customer first-party analytics stay outside Observatory durable storage.

LLMs and agents receive shaped evidence through typed boundaries, not direct SQL access or database credentials.

Provider disagreement is first-class evidence. Proprietary provider scores are provider-attributed testimony, not facts about the web.

Hammer tests are a hard gate for implementation.

Bounded repository recovery is proven. Encrypted/off-machine recovery is not yet proven.

---

## Current Completion State

Closed:

- M0 - LLM-first repo navigation and roadmap preservation
- M0.1 - Knowledgebase-to-repo reconciliation and candidate decision pass
- M1 - Roadmap Content Draft and Milestone Sequencing
- M2 - Folder Structure and Folder README Indexes
- M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
- M4 - Boundary Reconciliation and Doctrine Hardening
- M5 - Research Gate Plan
- M6 - Research Gate Execution
- M7 - Core Contract Planning
- M8 - Hammer Matrix and Acceptance Gates
- M9 - First Evidence Slice Definition
- M10 - Schema Planning Only
- M11 - Implementation Foundation
- M12 - First Evidence Slice Build
- M13 - Provider Admission and Controlled Pull Plan
- M14 - Typed Read API / MCP Contract and Prototype
- M15 - SearchClarity Proof Workflow
- M16 - Provider Cross-Check Proof
- M17 - Owned Telemetry Overlay Proof
- M18 - Recurring Watch Panel Planning
- M19 - Hardening, Backup, Recovery, and Operations
- M20 - Observatory v1 Acceptance

Active:

```text
DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
```

Post-v1 roadmap authority:

```text
POST_V1_DATABASE_ROADMAP.md
```

No later database milestone is active. DB-2 requires a separate owner decision.

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
