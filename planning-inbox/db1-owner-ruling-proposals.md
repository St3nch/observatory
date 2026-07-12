# DB-1 Owner-Ruling Proposals

Status: planning proposal; not accepted until owner rules
Date: 2026-07-12
Milestone: DB-1 — Post-v1 Audit Reconciliation and Ruling Closure

## OR-B1 — What counts as a hammer pass

Proposed ruling:

```text
A fixture, mock, stub, or in-memory pass may prove contract behavior only.
It does not satisfy a persistence, transaction, role, concurrency, migration,
backup, restore, or database-invariant hammer.

A database hammer is accepted only when executed against the real authorized
Postgres substrate or a disposable Postgres instance using the same migration,
constraint, role, and transaction behavior as the governed local database.
```

Proof classes must remain explicit:

```text
defined_only
fixture_contract_pass
in_memory_behavior_pass
owner_local_process_pass
real_postgres_disposable_pass
real_local_database_pass
production_surface_pass
```

No weaker class may be relabeled as a stronger class.

## OR-B2 — Which hammers gate which database permissions

Proposed ruling:

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

## OR-C2 — Raw retention posture by source family

Proposed ruling:

Use a fail-closed per-family posture. No global “retain everything” default.

Initial default map:

| Source family | Default posture | Notes |
|---|---|---|
| controlled provider API payload | `capture_and_purge_raw` until provider-specific rights and operational need justify stronger retention | Retain manifest, hash, shape fingerprint, purge proof where allowed |
| public manual observation | `retain_manifest_only` by default | Retain direct observation facts and public artifact references only as rights permit |
| public page snapshot | `no_raw_storage` until capture method, copyright, and retention rules are separately accepted | Hash/pointer planning does not authorize capture |
| AI/GEO answer surface | `no_raw_storage` until surface-specific terms and citation methodology are accepted | Do not infer broad permission from public visibility |
| marketplace surface | `no_raw_storage` until marketplace-specific admission | Customer/private dashboards remain forbidden |
| video/YouTube surface | `no_raw_storage` until source-specific admission | Private creator analytics remain forbidden |
| customer first-party / owned telemetry overlay | `forbidden_no_capture` for durable Observatory storage | Ephemeral read-time overlay only under current law |

A future family-specific decision may choose:

```text
retain_raw_payload
retain_manifest_only
capture_and_purge_raw
no_raw_storage
forbidden_no_capture
```

Unknown family or missing ruling fails closed to `forbidden_no_capture`.

## OR-C4 — Raw archive layout

Proposed ruling:

```text
Use a hybrid pointer architecture.

Postgres stores governed manifests, hashes, byte counts, media type, rights,
retention, support status, purge status, shape fingerprint, parser status,
and an internal opaque artifact pointer.

Raw payload bytes do not live in ordinary relational evidence tables.
When a future family is authorized for raw retention, payload bytes live in a
separately governed local/object artifact store behind an opaque pointer.
```

Requirements:

- raw pointer is internal and non-customer-facing;
- pointer and hash verification are mandatory;
- database row IDs, evidence IDs, citation handles, provider job IDs, and raw IDs remain distinct;
- no arbitrary filesystem path is exposed through typed reads;
- object/cloud storage is not authorized by this ruling alone;
- no raw-retention family is admitted merely because the layout exists;
- capture-and-purge must preserve only the metadata permitted by rights/retention.

## Recommended decision bundle

```text
ACCEPT OR-B1 REAL-SUBSTRATE HAMMER PROOF CLASSES
ACCEPT OR-B2 DATABASE-PHASE HAMMER GATE MAPPING
ACCEPT OR-C2 FAIL-CLOSED PER-SOURCE-FAMILY RAW RETENTION POSTURE
ACCEPT OR-C4 HYBRID RAW-MANIFEST / OPAQUE-ARTIFACT-POINTER LAYOUT
```

## Effect if accepted

Acceptance would authorize hammer-policy and data-contract planning only.

It would not authorize:

```text
Postgres creation
DDL
migration files or execution
raw capture
raw artifact storage
provider execution
cloud/object-store creation
real ingestion
```
