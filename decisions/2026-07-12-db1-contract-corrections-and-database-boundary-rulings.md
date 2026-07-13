# Decision — DB-1 Contract Corrections and Database-Boundary Rulings

Status: accepted decision
Date: 2026-07-12
Milestone: DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
Owner authority: explicit owner ruling in project chat

## Decision

The owner accepted the following ruling exactly:

```text
ACCEPT TYPED-READ API / MCP CONTRACT v0.1.1 CORRECTIONS
ACCEPT SEARCHCLARITY PROOF WORKFLOW CONTRACT v0.1.1 CORRECTION

ACCEPT OR-B1 REAL-SUBSTRATE HAMMER PROOF CLASSES
ACCEPT OR-B2 DATABASE-PHASE HAMMER GATE MAPPING
ACCEPT OR-C2 FAIL-CLOSED PER-SOURCE-FAMILY RAW RETENTION POSTURE
ACCEPT OR-C4 HYBRID RAW-MANIFEST / OPAQUE-ARTIFACT-POINTER LAYOUT
```

## Accepted contract corrections

The following corrective amendments are accepted as binding within their declared scopes:

```text
contracts/typed-read-api-mcp-v0-1.md — version 0.1.1
contracts/searchclarity-proof-workflow-v0-1.md — version 0.1.1
```

The accepted typed-read corrections cover:

- honest disclosure when page-size, total-result, or other extraction ceilings withhold otherwise-visible evidence;
- accurate omitted-evidence counts;
- expiring, bound cursors that fail closed after expiry;
- authorization against the declared outer request type without accidental nested public-handler grants;
- computed `consumer_promotion_required` behavior;
- corrected Hermes lineage status.

The accepted SearchClarity correction records conservative M15-to-M14 claim-intent translation as evidence selection only and forbids silent semantic strengthening.

The owner-local corrective proof remains classified as:

```text
proof_class: owner_local_process_pass
execution_surface: local Python fixture/in-memory suite
proof_strength: contract and prototype behavior only
result: Ran 188 tests in 0.331s — OK
```

This is not database, transaction, role, migration, persistence, network, concurrency, or production proof.

## OR-B1 — Real-substrate hammer proof classes

Accepted ruling:

```text
A fixture, mock, stub, or in-memory pass may prove contract behavior only.
It does not satisfy a persistence, transaction, role, concurrency, migration,
backup, restore, or database-invariant hammer.

A database hammer is accepted only when executed against the real authorized
Postgres substrate or a disposable Postgres instance using the same migration,
constraint, role, and transaction behavior as the governed local database.
```

Accepted proof classes:

```text
defined_only
fixture_contract_pass
in_memory_behavior_pass
owner_local_process_pass
real_postgres_disposable_pass
real_local_database_pass
production_surface_pass
```

No weaker proof class may be relabeled as a stronger class.

## OR-B2 — Database-phase hammer gate mapping

Accepted ruling:

```text
Physical planning and logical data-contract work do not require executed database hammers.
Physical schema specification requires mapped hammer expectations.
Migration execution requires the migration, constraint, identity, append-only,
audit-first, and role hammers to exist and be capable of failing.
Synthetic persistence requires those hammers to pass against real Postgres.
Real ingestion additionally requires provider authority, idempotency, rights,
retention, raw-integrity, recovery, and concurrency hammers to pass.
Database-backed typed reads require scope, authorization, pagination, truncation,
handle, attribution, stale-warning, raw-leakage, and read-role hammers to pass.
Production requires a separate future ruling and is not admitted by this sequence.
```

## OR-C2 — Fail-closed source-family raw retention

Accepted posture:

| Source family | Default posture |
|---|---|
| controlled provider API payload | `capture_and_purge_raw` |
| public manual observation | `retain_manifest_only` |
| public page snapshot | `no_raw_storage` |
| AI/GEO answer surface | `no_raw_storage` |
| marketplace surface | `no_raw_storage` |
| video/YouTube surface | `no_raw_storage` |
| customer first-party / owned telemetry overlay | `forbidden_no_capture` |

Allowed future family-specific postures are:

```text
retain_raw_payload
retain_manifest_only
capture_and_purge_raw
no_raw_storage
forbidden_no_capture
```

An unknown source family or missing family ruling fails closed to:

```text
forbidden_no_capture
```

This ruling does not authorize capture.

## OR-C4 — Hybrid raw-manifest and opaque-pointer layout

Accepted posture:

```text
Postgres stores governed manifests, hashes, byte counts, media type, rights,
retention, support status, purge status, shape fingerprint, parser status,
and an internal opaque artifact pointer.

Raw payload bytes do not live in ordinary relational evidence tables.
When a future source family is separately authorized for raw retention, payload
bytes live in a separately governed artifact store behind an opaque pointer.
```

Requirements:

- raw pointers remain internal and non-customer-facing;
- pointer and hash verification are mandatory;
- row IDs, evidence IDs, citation handles, provider IDs, and raw IDs remain distinct;
- typed reads never expose arbitrary filesystem paths, bucket keys, or storage locators;
- cloud/object storage is not authorized by this ruling;
- layout existence does not authorize capture or retention;
- capture-and-purge preserves only metadata permitted by rights and retention.

## Effect

This decision authorizes DB-1 hammer-policy v0.2 planning, per-hammer result-register planning, and DB-2 data-contract-freeze preparation under the existing DB-1 boundary.

It does not activate DB-2 and does not authorize:

```text
Postgres creation
database roles or credentials
DDL
migration files
migration execution
synthetic persistence
real persistence
raw capture
raw artifact storage
provider calls or paid pulls
real ingestion
production API/MCP
customer or private data
strategy or recommendation persistence
cloud/object-store creation
production deployment
```

## Milestone state

DB-1 remains active.

DB-1 may continue with hammer matrix / acceptance-gate policy v0.2, per-hammer result-register requirements, and complete DB-2 specification. DB-2 activation still requires a separate owner decision.

## Final rule

```text
Contract corrections are accepted.
Database hammers require real substrate.
Rights and retention fail closed by source family.
Raw bytes remain outside ordinary evidence tables.
No database permission is inferred beyond DB-1 planning.
```
