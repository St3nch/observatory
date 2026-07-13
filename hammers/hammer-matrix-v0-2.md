# Hammer Matrix v0.2

Status: DB-1 owner-ready policy candidate
Authority: planning output subordinate to accepted decisions until separately accepted
Milestone: DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
Supersedes for post-v1 database planning: `hammer-matrix-v0-1.md`

## Purpose

Carry the H1-H22 hostile-path model into the post-v1 database sequence using the accepted OR-B1 real-substrate proof classes and OR-B2 database-phase gate mapping.

This document defines what must be proven. It does not execute hammers, create Postgres objects, authorize migrations, or upgrade prior fixture/in-memory results into database proof.

## Accepted proof classes

```text
defined_only
fixture_contract_pass
in_memory_behavior_pass
owner_local_process_pass
real_postgres_disposable_pass
real_local_database_pass
production_surface_pass
```

Rules:

1. Proof class is determined by the actual execution substrate.
2. Fixture, mock, stub, and in-memory results may prove contract behavior only.
3. Persistence, transaction, role, concurrency, migration, backup, restore, and database-invariant claims require real PostgreSQL execution.
4. No result may be relabeled upward because the code resembles the future implementation.
5. `pass` without a proof class and execution surface is invalid proof metadata.

## Result vocabulary

```text
pass
fail
blocked_not_implemented
blocked_contract_missing
blocked_owner_ruling_required
blocked_authority_missing
blocked_required_surface_missing
blocked_manual_review_required
not_applicable_with_reason
```

A result of `pass` counts only when the required proof class for the applicable gate is met.

## H1-H22 continuity

The hammer IDs and hostile intents defined in `hammer-matrix-v0-1.md` remain stable:

| ID | Area |
|---|---|
| H1 | Scope isolation |
| H2 | Rights fail-closed |
| H3 | Retention enforcement |
| H4 | Customer-private rejection |
| H5 | No strategy/recommendation storage |
| H6 | CapturePackage validation |
| H7 | Provider spend and duplicate tasks |
| H8 | Provider attribution and disagreement |
| H9 | Freshness, volatility, and claim use |
| H10 | AI/GEO overclaim rejection |
| H11 | Marketplace evidence ceiling |
| H12 | Raw archive/manifest integrity |
| H13 | Provider drift and parser safety |
| H14 | Query panel immutability |
| H15 | Evidence ID and citation integrity |
| H16 | Consumer request and overlay boundary |
| H17 | LLM/agent access boundary |
| H18 | Hostile weird input |
| H19 | Append-only observations |
| H20 | Concurrency safety |
| H21 | Audit-first enforcement |
| H22 | Migration rollback and recovery |

v0.2 changes the accepted proof and database-gate mapping. It does not silently redefine the hostile intent of H1-H22.

## Database-phase gate mapping

### DB-1 — Reconciliation and policy closure

Required posture:

- H1-H22 remain defined and mapped.
- OR-B1 and OR-B2 are recorded as ruled.
- per-hammer result-register contract exists.
- no real database execution is required or authorized.

Maximum relevant proof class under DB-1:

```text
owner_local_process_pass
```

That class may apply only to bounded fixture/in-memory contract behavior already executed. Database claims remain `defined_only` or blocked.

### DB-2 — Physical data-contract freeze

DB-2 must classify each durable, append-only, versioned, derived, ephemeral, external, forbidden, and unresolved concept against applicable hammers.

Required mappings:

- scope and identity: H1, H4, H15
- rights and retention: H2, H3, H12
- no interpretation persistence: H5, H8, H10, H16
- capture/admission envelope: H6, H7, H13, H20, H21
- append-only and lifecycle: H19, H21
- migration/recovery implications: H22

No executed database hammer is required. No DDL or migration file is authorized.

### DB-3 — Operational boundary and physical schema specification

The specification must name enforceable mechanisms and expected failing hammers for:

```text
H1 H2 H3 H4 H5 H6 H12 H15 H19 H20 H21 H22
```

Role/read boundaries must map:

```text
H1 H15 H17
```

Provider and ingestion-adjacent structures must preserve future mappings for:

```text
H7 H8 H11 H13 H20
```

DB-3 remains specification-only. Required result class remains `defined_only` for database enforcement.

### DB-4 — Disposable PostgreSQL harness and migration specification

DB-4 must prove the real-Postgres harness can fail against intentionally broken candidates and can record structured results.

Minimum real-disposable proof families:

```text
H1 scope constraints/isolation
H2 rights fail-closed
H3 retention fail-closed
H4 customer-private rejection where mechanically enforceable
H5 forbidden persistence rejection
H6 admission-envelope constraints
H12 raw-manifest/hash/pointer invariants
H15 identity-layer separation
H19 append-only enforcement
H20 concurrency behavior
H21 audit-first same-transaction behavior
H22 migration forward/rollback/failure recovery
```

Required proof class where executed:

```text
real_postgres_disposable_pass
```

A fixture or owner-local process pass cannot close these DB-4 database gates.

### DB-5 — Governed local database bootstrap

Before DB-5 may close, the exact accepted migration set must pass on the governed local database for:

```text
H1 H2 H3 H5 H6 H12 H15 H19 H21 H22
```

Role and privilege behavior must pass applicable H17 checks.

Required proof class:

```text
real_local_database_pass
```

DB-5 does not authorize evidence ingestion.

### DB-6 — First persisted synthetic evidence slice

Required real-local proof:

```text
H1 H2 H3 H4 H5 H6 H12 H15 H18 H19 H20 H21
```

H14 applies if query panels are persisted in the accepted slice.

No real provider observation is allowed.

### DB-7 — Database-backed typed read proof

Required proof against the real local database and read-only role:

```text
H1 H5 H8 H9 H10 H15 H16 H17 H18
```

The read proof must additionally demonstrate:

- deterministic bounded pagination;
- cursor binding and expiration;
- honest truncation and omitted-result disclosure;
- uniform not-found behavior;
- non-detachable attribution and caveats;
- raw pointer and credential non-exposure.

Required proof class:

```text
real_local_database_pass
```

Network or production claims remain unauthorized.

### DB-8 — Backup and restore proof

Required real-disposable restore proof:

```text
H1 H3 H12 H15 H19 H21 H22
```

The restored database must preserve evidence-ID resolution, raw-manifest hash continuity, audit continuity, scope isolation, schema version, and migration history.

Minimum proof class:

```text
real_postgres_disposable_pass
```

Encrypted off-machine proof remains a separate required operational result before real evidence.

### DB-9 — First persisted real observation

Before any request-specific real observation is accepted, the applicable set must include:

```text
H1 H2 H3 H4 H5 H6 H7 H8 H9 H11 H12 H13 H15 H18 H19 H20 H21
```

H10 applies to AI/GEO surfaces. H14 applies where a query panel is used. H16 applies to consumer-triggered requests.

Required database proof class:

```text
real_local_database_pass
```

Provider authority, rights, budget, idempotency, and request-specific owner approval remain separate gates.

### DB-10 — Database-phase acceptance

DB-10 reviews every mandatory hammer result, every blocked result, every exception, and every known limit.

DB-10 cannot infer production authority. `production_surface_pass` is unavailable until a future production roadmap explicitly defines and executes that surface.

## Fail-closed application rules

- Unknown applicability means applicable until dispositioned.
- `not_applicable_with_reason` requires a named contract/surface reason and reviewer.
- Missing evidence means not passed.
- Missing authority means `blocked_authority_missing`, not pass.
- A successful tool call is not automatically a hammer pass.
- A tool catalog is not execution evidence.
- Test count alone is not proof classification.
- Database hammers must identify database class and database identity without exposing credentials.

## Non-authorizations

```text
No PostgreSQL creation.
No roles or credentials.
No DDL or migration files.
No migration execution.
No disposable database lifecycle.
No real PostgreSQL hammer execution.
No ingestion.
No provider calls.
No customer/private data.
No production API/MCP.
No strategy or recommendation persistence.
```

## Final rule

```text
Name the hostile claim.
Name the required substrate.
Run it only when the gate opens.
Never promote weak proof into strong proof.
```
