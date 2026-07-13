# Acceptance Gate Policy v0.2

Status: DB-1 owner-ready policy candidate
Authority: planning output subordinate to accepted decisions until separately accepted
Milestone: DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
Supersedes for post-v1 database planning: `acceptance-gate-policy-v0-1.md`

## Purpose

Define when hammer planning is sufficient, when executed proof is mandatory, which proof class is required, and what must block milestone closure across DB-1 through DB-10.

This policy incorporates the accepted OR-B1 real-substrate proof classes and OR-B2 database-phase gate mapping.

## Core acceptance rule

```text
A milestone closes only when every mandatory hammer has one of:
1. a passing result at or above the required proof class; or
2. an explicit blocked result that the milestone's own exit criteria permit; or
3. a reviewed not-applicable disposition with an exact reason.
```

Silence is not a disposition. A planned hammer is not an executed hammer. A fixture pass is not database proof.

## Proof classes

Ordered only by execution surface strength, not by automatic substitutability:

```text
defined_only
fixture_contract_pass
in_memory_behavior_pass
owner_local_process_pass
real_postgres_disposable_pass
real_local_database_pass
production_surface_pass
```

A stronger surface does not excuse missing hammer intent, missing authority, or missing evidence metadata.

## Mandatory result fields

Every claimed hammer result must conform to `per-hammer-result-register-v0-1.md` and include at minimum:

```text
hammer_id
result
proof_class
execution_surface
required_proof_class
database_class when applicable
code_commit
contract_or_policy_version
started_at
finished_at
evidence_paths
review_status
```

A pass missing required metadata is invalid and counts as not proven.

## Result interpretation

| Result | Acceptance meaning |
|---|---|
| `pass` | Counts only when the required proof class and evidence fields are satisfied |
| `fail` | Blocks closure |
| `blocked_not_implemented` | Allowed only in planning milestones that do not require execution |
| `blocked_contract_missing` | Blocks any milestone that requires the missing contract |
| `blocked_owner_ruling_required` | Blocks unless the milestone explicitly allows carrying the ruling forward fail-closed |
| `blocked_authority_missing` | Blocks execution; cannot be bypassed by available tools or credentials |
| `blocked_required_surface_missing` | Blocks milestones requiring that substrate |
| `blocked_manual_review_required` | Blocks until the named human review occurs |
| `not_applicable_with_reason` | Counts only after documented review and exact scope reason |

## DB milestone gates

### DB-1 — Policy and reconciliation gate

DB-1 may close when:

- all audit findings N-01 through N-14 have committed dispositions;
- accepted corrections and owner rulings are reflected in current documents;
- hammer matrix v0.2 exists and is owner-ready;
- this policy exists and is owner-ready;
- the per-hammer result-register contract exists and is owner-ready;
- ob-dev control-plane requirements are committed and mapped to DB-3/DB-4;
- DB-2 deliverables and non-authorizations are fully specified;
- no PostgreSQL, DDL, migration, or real-ingestion action occurred.

Executed database proof is forbidden, not required.

### DB-2 — Data-contract freeze gate

DB-2 may close only when one owner-accepted logical data contract:

- classifies every concept as durable, append-only, versioned, derived, ephemeral, external, forbidden, or unresolved;
- maps identity, lifecycle, provenance, scope, rights, retention, write authority, read exposure, and hammer implications;
- contains an explicit forbidden-persistence register;
- preserves provider disagreement as derived unless separately ruled;
- preserves overlays as ephemeral and forbidden persistence;
- incorporates OR-C2 and OR-C4 without inferring capture authority.

Required proof posture: `defined_only` mappings. No database execution.

### DB-3 — Operational boundary and physical specification gate

DB-3 may close only when:

- instance, database-class, role, credential, backup-before-migration, naming, migration, append-only, audit-first, identity, index, constraint, and raw-pointer boundaries are specified;
- the exact ob-dev PostgreSQL contract is accepted;
- every physical mechanism maps to hammers that can fail;
- governed mutation modes remain disabled;
- no database, role, DDL, or migration execution occurred.

Required proof posture: `defined_only` for database enforcement.

### DB-4 — Disposable real-Postgres proof gate

DB-4 may close only when:

- accepted ob-dev database tools are implemented and owner-refreshed;
- the disposable database class is protected and operational;
- exact-path, expected-SHA forward and rollback execution works;
- mandatory hammers can be shown failing against intentionally broken candidates;
- required passing hammers earn `real_postgres_disposable_pass`;
- result-register entries are complete and reviewable;
- no governed durable Observatory database exists.

Fixture, mock, in-memory, and owner-local process results cannot satisfy DB-4 database gates.

### DB-5 — Governed bootstrap gate

DB-5 requires a separate explicit owner authorization for database creation, role creation, and exact migration execution.

Closure requires:

- accepted migrations and rollback pairs;
- role and privilege proof;
- append-only and audit-first proof;
- identity and constraint proof;
- migration-history proof;
- required results at `real_local_database_pass`.

No evidence ingestion is implied.

### DB-6 — Synthetic persistence gate

Closure requires passing real-local results for all applicable persistence hammers, including scope, rights, retention, forbidden persistence, admission, identity, hostile input, append-only, concurrency, and audit-first behavior.

Only synthetic evidence is allowed.

### DB-7 — Database-backed typed-read gate

Closure requires real-local proof under the read-only role for:

- scope-aware authorization;
- uniform not-found behavior;
- deterministic bounded pagination;
- bound and expiring cursors;
- honest truncation and omitted-result disclosure;
- attribution and caveat integrity;
- stale/freshness warnings;
- raw locator and credential non-exposure;
- no SQL/CRUD path for LLMs.

The required proof class is `real_local_database_pass`. Production/network authority remains absent.

### DB-8 — Recovery gate

Closure requires:

- verified database backup;
- restore into disposable PostgreSQL;
- schema and migration-history continuity;
- evidence-ID, raw-manifest hash, audit, and scope continuity;
- encrypted owner-controlled artifact;
- verified off-machine generation before real evidence.

Database restore hammers require at least `real_postgres_disposable_pass`.

### DB-9 — Real-observation gate

Entry requires all of:

- structural provider authority and attempt ledger;
- request-specific owner authorization;
- source-family rights and retention ruling;
- budget and remaining-authorization enforcement;
- duplicate and concurrency safety;
- drift and quarantine handling;
- recovery proof already passed.

Closure requires applicable hammers at `real_local_database_pass`. One authorized observation does not authorize another.

### DB-10 — Database-phase acceptance gate

DB-10 must review:

- every mandatory hammer result;
- every blocked or failed result;
- every not-applicable disposition;
- migration and recovery evidence;
- synthetic and real observation proof;
- typed-read proof;
- known limits and deferred capabilities.

DB-10 may accept, reject, or return the local database for hardening. It cannot authorize production by implication.

## Authority controls

- Tool existence is not roadmap authorization.
- Credentials are not authorization.
- A running PostgreSQL service is not authorization.
- Dormant code is not accepted architecture.
- A successful command is not automatically a hammer pass.
- Owner approval must be linked to the exact gated action.
- No prior approval may be stretched to a new database, migration, provider call, or capture.

## Exception policy

There is no silent exception path.

Any proposed exception must record:

```text
exception_id
blocked gate
exact reason
scope and duration
risk accepted
compensating controls
owner decision
expiry or closure condition
```

An exception cannot redefine proof class or convert a failure into a pass.

## Non-authorizations

```text
No PostgreSQL creation.
No roles or credentials.
No DDL or migration files.
No migration execution.
No disposable database lifecycle.
No real PostgreSQL hammer execution.
No ingestion or provider calls.
No customer/private data.
No production surface.
No strategy or recommendation persistence.
```

## Final rule

```text
The gate asks what was actually proven, on what substrate, under whose authority.
Anything less is paperwork cosplay.
```
