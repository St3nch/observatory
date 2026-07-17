# Post-v1 Database Roadmap — The Observatory

Status: authority for post-v1 sequencing after owner acceptance
Authority: original sequence from `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`; recovery state from `decisions/2026-07-13-database-phase-recovery-to-db1.md`; current DB-4 implementation gate from `decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md`
Purpose: govern the path from accepted bounded v1 proof system to a real local Postgres-backed evidence system without widening authority accidentally
Last updated: 2026-07-14

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
Last trusted database milestone: DB-3 — trusted, accepted, and complete
Active milestone: DB-4 — Database Hammer Harness and Migration Specification
DB-4 state: Route C drift correction and completion; R0 reconciliation active; PostgreSQL execution separately prohibited
DB-4 closure status: not ready; prior proof is diagnostic only
DB-5: inactive
Governed database or governed role creation: not authorized
New PostgreSQL execution under the prior campaign: not authorized
Audit reconciliation, traceability, redesign, and exact package preparation: authorized
Governed, production, provider, customer/private-data, recurring, and DB-5 work: not authorized
```

Current authority:
`decisions/2026-07-16-db4-remediation-reconciliation-and-r0-authorization.md`.

Accepted implementation authority remains bounded by:
`decisions/2026-07-14-db4-remediation-implementation-authorization.md`.

Current conformance baseline:
`database/db4-remediation-conformance-manifest.json`.

---

## Milestone summary

| ID | Name | Status | Main gate |
|---|---|---|---|
| DB-1 | Post-v1 Audit Reconciliation and Ruling Closure | closed | Audit findings routed; corrections and rulings accepted; DB-2 package prepared |
| DB-2 | Physical Data-Contract Freeze | closed / accepted | Exact v0.2.1 freeze accepted by path, version, and SHA-256; sole normative input to DB-3 |
| DB-3 | Postgres Operational Boundary and Physical Schema Specification | closed / accepted | Exact planning package accepted by path/SHA; bounded checker correction accepted; sole normative input to DB-4 preparation |
| DB-4 | Database Hammer Harness and Migration Specification | active / remediation | Audit findings reconciled; DB-3-faithful migration, behavioral hammer, durable proof, security, and restart-reduction package must be prepared and separately approved before re-execution |
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

DB-2 activation was completed by `decisions/2026-07-13-db1-closure-and-db2-activation.md`; the later recovery and reconciliation were completed by the 2026-07-14 DB-2 closure decision.

---

# Closed milestone

DB-2 reconciliation is complete. The prior later-milestone claims and their five
untrusted artifacts remain permanently retired and deleted from the active repository.

Accepted DB-2 artifact:

```text
planning-inbox/db2-physical-data-contract-freeze-specification.md
version 0.2.1
sha256 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
decision: decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
```

The exact accepted artifact is immutable and is the sole normative DB-2 input to
fresh DB-3 planning. Acceptance does not authorize DB-4 or implementation.

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

Completed by the exact accepted artifact and decision above.

---

# Closed milestone

## DB-3 — Postgres Operational Boundary and Physical Schema Specification

DB-3 was accepted and closed by
`decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md`.

Accepted DB-3 artifacts:

```text
planning-inbox/db3-accepted-input-traceability-matrix.md
version 0.1
sha256 db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98

planning-inbox/db3-fresh-postgres-design-specification-v0-1.md
version 0.1
sha256 9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e

planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md
version 0.1
sha256 d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec
```

The bounded authority-checker correction and regression test in commit
`588fd754d954817f92530c6408a20b312f81af65` were also accepted.

### Purpose

Specify the local Postgres operational boundary and derive the physical schema only
from the accepted DB-2 freeze.

### Exit

Completed. The accepted package defines the future operational boundary, physical
responsibilities, exact 28-tool control-plane contract, migration/rollback/backup
policies, hammer mappings, and non-authorizations without creating executable SQL,
migrations, database objects, tools, or a database.

Acceptance does not authorize implementation. The five retired DB-3/DB-4 artifacts
remain permanently absent and prohibited from restoration, salvage, reuse, copying,
paraphrased reconstruction, or memory-based reconstruction.

---

# Active milestone

## DB-4 — Database Hammer Harness and Migration Specification

Status: active in remediation and exact implementation-package preparation under
`decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`.

The prior DB-4 implementation and disposable campaign are diagnostic only. They do
not satisfy closure and may not become the DB-5 bootstrap set.

### Purpose

Produce a DB-3-faithful migration specification and a real disposable PostgreSQL
hammer system whose behavior, failure evidence, security controls, and result records
satisfy the accepted DB-1 gate policy.

### Governing remediation plan

```text
planning-inbox/db4-audit-remediation-program-v0-1.md
```

### Required remediation workstreams

- R0 authority reconciliation and proof-campaign freeze;
- R1 exact DB-2/DB-3 responsibility traceability;
- R2 atomic immutable migration/history redesign;
- R3 DB-3-faithful physical candidate rebuild;
- R4 behavioral hammer and hostile-candidate rebuild;
- R5 durable result-register emission and validation;
- R6 role/RLS, marker, authority, redaction, and remote-access hardening;
- R7 data-driven profiles and restart reduction;
- R8 fresh clean-substrate re-execution after a separate owner gate.

### Required DB-4 exit properties

- every accepted DB-3 responsibility is implemented or explicitly deferred by owner ruling;
- migration and history are one-session, one-transaction, append-only, SHA-bound, and serialized;
- before/after fingerprints detect columns, constraints, indexes, triggers, policies, functions, and relevant ownership state;
- mandatory hammer IDs map exactly to their accepted hostile claims;
- structural checks are labeled as preconditions rather than passes;
- role/RLS behavior is tested under bounded role switching, not superuser-only observation;
- broken candidates traverse the real migration admission path;
- concurrency tests exercise project identity/admission behavior with forced overlap;
- failures and cleanup are fully recorded;
- immutable reviewable per-hammer result records exist;
- the disposable database and cluster test roles are cleaned and recorded;
- no governed database exists.

### Allowed now

- audit reconciliation and finding disposition;
- traceability matrices and architecture options;
- migration/history, schema, hammer, proof, security, and restart-reduction design;
- exact bounded implementation-package preparation;
- current-state and roadmap corrections;
- repository validation, exact staging, commits, and manual owner pushes.

### Forbidden now

```text
new PostgreSQL execution under the prior campaign
governed database creation
DB-5 planning, activation, or implementation
providers, capture, ingestion, paid pulls, or raw provider payloads
customer/private data
recurring or production work
strategy, recommendation, conclusion, score-as-truth, or report persistence
arbitrary SQL or shell
weakened fixed-root, authority, credential, or protected-name controls
```

### Exit

DB-4 remediation planning exits only when:

- the R1 traceability matrix is complete and independently reviewed;
- migration/history architecture is selected and exact;
- the physical candidate set faithfully maps to DB-3;
- behavioral hammer and result-record designs are complete;
- security and restart-reduction designs are complete;
- exact file/tool/test manifests and stop conditions are owner-ready;
- the owner separately accepts an implementation/execution package.

DB-4 itself closes only after a later clean disposable campaign produces accepted,
reviewable `real_postgres_disposable_pass` records for every required family.

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
