# Post-v1 Database Roadmap — The Observatory

Status: authority for post-v1 sequencing after owner acceptance
Authority: original sequence from `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`; current recovery state from `decisions/2026-07-13-database-phase-recovery-to-db1.md`
Purpose: govern the path from accepted bounded v1 proof system to a real local Postgres-backed evidence system without widening authority accidentally
Last updated: 2026-07-13

---

## Core rule

```text
The database must physically enforce the telescope doctrine.
Planning is not DDL.
DDL is not migration execution.
Migration execution is not ingestion.
Synthetic persistence is not real evidence admission.
A local database is not production.
```

No milestone implies the next milestone.

---

## Current state

```text
Observatory v1: accepted at bounded proof-system ceiling
Last trusted database milestone: DB-1 — closed
Active milestone: DB-2 — Physical Data-Contract Freeze Reconciliation
DB-3 and DB-4 closure/activation claims: suspended
Postgres creation: not authorized
DDL: not authorized
Migration files or execution: not authorized
Database-control-plane expansion: not authorized
```

Recovery authority: `decisions/2026-07-13-database-phase-recovery-to-db1.md`.

---

## Milestone summary

| ID | Name | Status | Main gate |
|---|---|---|---|
| DB-1 | Post-v1 Audit Reconciliation and Ruling Closure | closed | Audit findings routed; corrections and rulings accepted; DB-2 package prepared |
| DB-2 | Physical Data-Contract Freeze | active recovery | Reconcile the canonical freeze from trusted DB-1 and return it for owner review |
| DB-3 | Postgres Operational Boundary and Physical Schema Specification | suspended / inactive | Existing specifications are untrusted candidates until DB-2 is revalidated |
| DB-4 | Database Hammer Harness and Migration Specification | suspended / inactive | No implementation or PostgreSQL authority during recovery |
| DB-5 | Governed Local Database Bootstrap and Migration Execution | planned | Separate owner execution gate; migration hammers pass |
| DB-6 | First Persisted Synthetic Evidence Slice | planned | Append-only, audit-first, identity, scope, rights, retention, and concurrency hammers pass |
| DB-7 | Database-Backed Typed Read Proof | planned | Read-only role and typed-read hammers pass, including honest truncation |
| DB-8 | Database Backup and Restore Proof | planned | Semantic restore and encrypted off-machine generation proven before real evidence |
| DB-9 | Provider Enforcement Substrate and First Persisted Real Observation | planned | Structural authority/spend/idempotency cage plus request-specific owner approval |
| DB-10 | Database-Phase Acceptance | planned | Accept, reject, or return the local database for hardening; no automatic production authority |

---

# Closed milestone

## DB-1 — Post-v1 Audit Reconciliation and Ruling Closure

### Purpose

Consume the accepted post-v1 audit completely, correct proven v1 truth/code defects, close the rulings needed for database planning, and prepare DB-2 without touching Postgres or DDL.

### Required reading

- `decisions/2026-07-12-observatory-v1-acceptance.md`
- `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`
- `audits/observatory-post-v1-pre-database-deep-audit-2026-07-12.md`
- `planning-inbox/post-v1-pre-database-audit-response-2026-07-12.md`
- `planning-inbox/db1-owner-ruling-proposals.md`
- accepted M14 typed-read contract and proof outputs
- hammer matrix and acceptance-gate policy drafts
- owner-ruling tracker

### Allowed work

- audit indexing and response tracking;
- README / LLM authority-pointer corrections;
- narrow typed-read contract and prototype corrections for accepted audit findings;
- hostile tests for those corrections;
- OR-B1/B2/C2/C4 proposal and decision work;
- hammer matrix/policy v0.2 planning;
- per-hammer result-register contract planning;
- ob-dev database control-plane requirements planning so DB-3/DB-4 do not depend on improvised MCP edits;
- DB-2 physical data-contract-freeze specification.

### Forbidden work

```text
Postgres creation
physical schema or DDL
migration files
migration execution
database roles or credentials
provider calls or paid pulls
real evidence ingestion
customer or private data
recurring capture
production API/MCP
cloud deployment
strategy or recommendation persistence
```

### Exit criteria

- all N-01 through N-14 findings have committed dispositions;
- N-05 and N-09 documentation-truth corrections complete;
- N-01, N-08, N-11, N-13, and N-14 corrections proven under bounded tests or separately gated with exact reasons;
- OR-B1/B2/C2/C4 ruled;
- hammer matrix and acceptance policy v0.2 accepted or owner-ready under an exact decision gate;
- per-hammer register shape accepted or owner-ready;
- ob-dev database control-plane requirements committed and mapped to DB-3/DB-4 gates;
- DB-2 deliverables and non-authorizations fully specified;
- no database, DDL, or migration execution has occurred.

### Next gate

DB-2 activation requires a separate owner decision.

---

# Active milestone

Recovery posture: DB-2 is reopened for reconciliation. Prior DB-2 closure and all later activation claims are suspended. The existing freeze and corrections are candidate inputs, not accepted authority.

## DB-2 — Physical Data-Contract Freeze

### Purpose

Create one owner-accepted logical contract that is the sole normative input to physical schema specification.

### Required content

For every concept, define:

```text
classification: durable / append-only / versioned / derived / ephemeral / external / forbidden / unresolved
identity owner
lifecycle and status vocabulary
required provenance
scope and rights relationship
retention behavior
relationships
write authority
read exposure
hammer implications
```

Must reconcile at least:

- scope and scope class;
- provider/capture instrument;
- query panel definitions as deferred-owned concepts;
- CapturePackage and capture attempt;
- candidate and admitted observation;
- evidence identity and internal citation handle;
- raw manifest/support status and opaque artifact pointer;
- shape fingerprint, parser version, and provider drift event;
- rights, retention, freshness, and volatility vocabularies;
- audit events and security logs as separate concerns;
- provider disagreement as derived only;
- report-safe references as consumer-owned;
- overlays as ephemeral and forbidden persistence;
- forbidden persistence list.

### Forbidden work

No table DDL, migrations, database creation, or implementation.

### Exit

Owner accepts the freeze and authorizes DB-3 planning.

---

## DB-3 — Postgres Operational Boundary and Physical Schema Specification

### Purpose

Specify the local Postgres operational boundary and derive the physical schema only from the accepted DB-2 freeze.

### Required decisions

- instance ownership and version posture;
- database and role model, at minimum migration / ingest / read-only roles;
- credential custody and secret handling;
- local/test/disposable database separation;
- backup-before-migration rule;
- naming and migration version policy;
- append-only enforcement mechanism;
- audit-first same-transaction mechanism;
- identity/index/constraint strategy;
- raw manifest pointer boundary;
- no customer/strategy/recommendation schema rule;
- exact ob-dev database control-plane contract, including fixed binaries, credential custody, protected database names, database classes, migration path/SHA rules, capability activation classes, result shapes, and MCP restart/recovery procedure.

### Allowed

Specifications, diagrams, constraint matrices, migration plans, rollback plans.

### Forbidden

Creating the database, roles, DDL, migration execution, ingestion.

---

## DB-4 — Database Hammer Harness and Migration Specification

### Purpose

Build the disposable real-Postgres test harness before authorizing the governed local database, implement the accepted ob-dev database control-plane expansion, and prove that hammers can actually fail.

The ob-dev expansion should be one coherent, tested capability batch followed by an owner-controlled restart/connector refresh. Tool existence does not authorize governed database mutation; dangerous modes remain capability-gated.

### Minimum control-plane capabilities

- read-only Postgres readiness, identity, settings, database, role, schema, privilege, and migration-history inspection;
- disposable-database create/reset/drop tools with protected-name and disposable-marker enforcement;
- exact-path, expected-SHA migration validation, forward execution, and rollback execution;
- allowlisted migration, role, concurrency, and restore hammer profiles;
- structured per-hammer proof results with no secret leakage;
- no generic shell, arbitrary PowerShell/Python, arbitrary SQL, or caller-selected executable paths.

Detailed planning input:

```text
planning-inbox/db1-ob-dev-database-control-plane-requirements.md
```

### Minimum hammer families

- scope and contamination;
- rights and retention;
- identity and raw integrity;
- append-only and audit-first;
- concurrency and idempotency;
- migration forward/rollback/failure recovery;
- role and privilege boundaries;
- typed-read pagination/truncation/authorization.

### Exit

- accepted ob-dev database tools are implemented, owner-restarted/refreshed, and capability-gated;
- disposable Postgres lifecycle works through ob-dev without exposing generic SQL or execution;
- disposable Postgres harness exists;
- per-hammer register exists;
- candidate migration specifications include rollback pairs and execute only through exact-path, expected-SHA tools;
- mandatory hammers can be shown failing against intentionally broken candidates;
- no governed durable database or real evidence exists.

---

## DB-5 — Governed Local Database Bootstrap and Migration Execution

Requires a separate explicit owner phrase authorizing:

```text
local Postgres database creation
role creation
exact migration execution
```

Exit requires migration, rollback, constraint, role, append-only, audit-first, and identity hammers to pass.

No evidence ingestion is authorized by DB-5 alone.

---

## DB-6 — First Persisted Synthetic Evidence Slice

Persist only synthetic C2-family evidence through the real write path.

Must prove:

- scope isolation;
- rights/retention fail-closed;
- evidence-ID independence;
- candidate/admission lifecycle;
- append-only correction/supersession;
- audit event in the same transaction;
- duplicate and concurrency behavior;
- no customer, overlay, strategy, recommendation, or report data.

No real provider or manual observation is authorized.

---

## DB-7 — Database-Backed Typed Read Proof

Minimum read slice:

```text
evidence_lookup
observation_package_read
```

Must run under a read-only role and prove:

- scope-aware authorization;
- uniform not-found;
- keyset or otherwise deterministic bounded pagination;
- cursor binding and expiration;
- honest truncation and omitted-result disclosure;
- non-detachable attribution/caveats;
- stale/freshness warnings;
- raw pointer and credential non-exposure;
- no direct SQL path for LLMs.

No production MCP/network deployment is implied.

---

## DB-8 — Database Backup and Restore Proof

Must prove:

- database backup and hash/integrity evidence;
- disposable restore;
- schema version and migration history;
- evidence-ID resolution after restore;
- raw-manifest hash continuity;
- audit-event continuity;
- scope isolation after restore;
- encrypted owner-controlled backup artifact;
- at least one verified off-machine generation before real evidence.

---

## DB-9 — Provider Enforcement Substrate and First Persisted Real Observation

Before any real capture:

- decision-linked authority record exists;
- remaining authorization count normally defaults to zero;
- duplicate/attempt ledger is clone-stable and consulted by code;
- cumulative and post-receipt budgets are enforced;
- idempotent ingestion passes concurrent hammers;
- preflight is durably tied to the evidence package;
- canonical shape fingerprint and unknown-shape quarantine exist;
- source-family rights/retention posture is ruled;
- database recovery proof has passed;
- a new request-specific owner decision exists.

One authorized observation does not authorize another.

---

## DB-10 — Database-Phase Acceptance

Accept, reject, or return the local database for hardening against:

- doctrine;
- accepted physical data contract;
- hammer results;
- migration and recovery evidence;
- synthetic and real observation proof;
- typed-read behavior;
- known limits.

DB-10 does not authorize production unless a separate future roadmap explicitly does so.

---

## Permanent deferred / forbidden posture

Until separately ruled:

```text
production deployment
recurring capture
additional provider families
customer data or first-party storage
customer report state
strategy/recommendation/conclusion storage
disagreement materialization
cross-scope aggregate persistence
public API/MCP exposure
dashboards
```

## Final rule

```text
Build the telescope's durable spine.
Do not put the astronomer's conclusions in the database.
Every new permission must be earned by a named gate and a hammer that can fail.
```
