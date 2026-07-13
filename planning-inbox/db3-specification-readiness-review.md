# DB-3 Specification Readiness Review

Status: invalidated historical review; not current closure evidence
Date: 2026-07-13
Reviewed documents:

- `planning-inbox/db3-postgres-operational-boundary-specification.md`
- `planning-inbox/db3-physical-schema-specification.md`

## Review question

Do the DB-3 specifications satisfy the roadmap requirement to define the PostgreSQL operational boundary and physical schema without crossing into database creation, role creation, SQL/DDL, migration files, execution, or persistence?

## Result

```text
result: invalidated_by_unreconciled_db2_freeze
DB-3: suspended / inactive
DB-4: suspended / inactive
PostgreSQL execution: unauthorized
```

## Coverage review

| Required DB-3 decision | Result | Evidence |
|---|---|---|
| Instance ownership/version posture | pass | Owner-controlled local instance, explicit server identity, major-version binding, local-only connection posture |
| Database-class separation | pass | Governed, disposable, restore, protected-system, and unknown classes are distinct and fail closed |
| Role model | pass | Migrator, ingest, reader, auditor, and backup responsibilities are separated |
| Credential custody | pass | Owner/environment custody, no secrets in arguments/repo/results, fail-closed identity behavior |
| Fixed binary boundary | pass | Fixed PostgreSQL binaries, no caller-selected executables, version/file identity expectations |
| Naming policy | pass | Governed/disposable/restore names and protected system names are specified |
| Migration path/SHA/version policy | pass | Exact repository paths, expected SHA-256, immutable version/history, paired rollback expectations |
| Backup-before-migration | pass | Governed migration stops on backup failure; disposable reset/rollback remains deterministic |
| ob-dev capability model | pass | Inspection, disposable, proof, governed bootstrap, ingestion, and restore classes are separated |
| ob-dev tool contract | pass | Tool groups, bounded arguments, redacted result envelope, and restart/recovery sequence are specified |
| Schema families | pass | Core, governance, audit, operations, and read responsibilities are separated |
| Identity strategy | pass | Stable logical IDs remain distinct from row/provider/customer/report identities |
| Table responsibilities | pass | Every accepted DB-2 durable/versioned/append-only/external context is mapped without adding forbidden meaning |
| Relationship/cardinality strategy | pass | Scope, capture, candidate, observation, evidence, raw, and drift relationships are defined |
| Append-only enforcement | pass | Mechanism intentions and hostile-role proof requirements are specified |
| Audit-first same transaction | pass | Consequential writes and mandatory audit context are defined |
| Constraints/indexes | pass | Enforcement-oriented constraints and bounded query indexes are defined; speculative analytics rejected |
| Raw boundary | pass | Manifest, opaque pointer, and external bytes remain separate |
| Forbidden-persistence absence | pass | Customer, strategy, recommendation, conclusion, reasoning, credential, and consumer-state tables are explicitly absent |
| Read exposure | pass | Approved read surfaces only; no generic CRUD or direct LLM SQL |
| Hammer mapping | pass | Operational and physical mechanisms map to H1-H22 families |
| No execution drift | pass | No SQL, DDL, migrations, database/role creation, credentials, or PostgreSQL commands were produced or executed |

## Conflict review

No conflict found with:

- `02-boundaries.md`;
- accepted DB-2 freeze v0.1.1;
- hammer matrix and acceptance-gate policy v0.2;
- typed-read and evidence-ID contracts;
- accepted OR-C2 and OR-C4 raw boundaries;
- ob-dev database-control-plane requirements;
- DB-3 specification-only owner authorization.

## Deferred decisions preserved

The specifications correctly leave these to later gates:

```text
exact SQL syntax
actual PostgreSQL object names if owner revises candidates
role/database/credential creation
migration file contents
trigger/function implementation choice
real privilege proof
real append-only and audit-first proof
actual artifact-store technology
backup encryption and off-machine transfer
production/network posture
provider execution and ingestion
customer/private data
```

## DB-3 closure recommendation

The owner may accept both DB-3 specifications, close DB-3, and activate DB-4 planning/implementation only through a separate exact gate.

DB-4 should authorize:

- coherent ob-dev database-control-plane implementation;
- migration and rollback specification files;
- disposable real-PostgreSQL harness implementation and proof;
- intentionally broken candidates proving hammers can fail;
- one owner-controlled ob-dev restart and connector refresh.

DB-4 should not authorize:

- governed Observatory database creation;
- governed roles or credentials;
- governed migration execution;
- synthetic or real evidence persistence in a governed database;
- provider calls, ingestion, customer/private data, raw capture, or production.

## Exact owner gate candidate

```text
ACCEPT DB-3 POSTGRES OPERATIONAL BOUNDARY SPECIFICATION v0.1
ACCEPT DB-3 PHYSICAL SCHEMA SPECIFICATION v0.1

CLOSE DB-3 — POSTGRES OPERATIONAL BOUNDARY AND PHYSICAL SCHEMA SPECIFICATION

ACTIVATE DB-4 — DATABASE HAMMER HARNESS AND MIGRATION SPECIFICATION

AUTHORIZE THE COHERENT ob-dev DATABASE-CONTROL-PLANE IMPLEMENTATION,
MIGRATION/ROLLBACK SPECIFICATION FILES, AND DISPOSABLE REAL-POSTGRES
HARNESS/PROOF ONLY.

DO NOT AUTHORIZE THE GOVERNED OBSERVATORY DATABASE, GOVERNED ROLES OR
CREDENTIALS, GOVERNED MIGRATION EXECUTION, SYNTHETIC OR REAL GOVERNED
PERSISTENCE, PROVIDER CALLS, CUSTOMER DATA, RAW CAPTURE, OR PRODUCTION.
```

This is a proposal only until explicitly accepted by the owner.

## Final rule

```text
DB-3 has specified the machine.
DB-4 may build and break the disposable proving ground.
The governed database still waits behind DB-5.
```
