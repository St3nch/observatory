# DB-3 PostgreSQL Operational Boundary Specification

Status: DB-3 specification draft; no execution authority
Date: 2026-07-13
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Normative inputs:

- `planning-inbox/db2-physical-data-contract-freeze-specification.md`
- `planning-inbox/db2-freeze-v0-1-1-classification-corrections.md`
- `hammers/hammer-matrix-v0-2.md`
- `hammers/acceptance-gate-policy-v0-2.md`
- `planning-inbox/db1-ob-dev-database-control-plane-requirements.md`
- `02-boundaries.md`

## Purpose

Specify the PostgreSQL operational boundary that a later DB-4 disposable proof harness and DB-5 governed bootstrap must obey.

This document defines operational classes, role boundaries, credential custody, naming, migration governance, backup-before-migration rules, protected targets, ob-dev capability behavior, and proof expectations.

It does not create a database, role, credential, SQL file, migration, disposable database, or PostgreSQL hammer run.

## Non-authorization boundary

```text
No PostgreSQL database creation.
No role or credential creation.
No SQL or DDL files.
No migration files or execution.
No disposable database lifecycle.
No PostgreSQL hammer execution.
No synthetic or real persistence.
No provider calls or ingestion.
No customer/private data.
No raw capture or artifact-store creation.
No production.
```

Specification is not implementation. Available PostgreSQL tools or credentials do not widen this authority.

## Instance and version posture

### Instance ownership

The initial PostgreSQL server is owner-controlled and local to the development environment.

The Observatory owns no server-wide administration authority. Server installation, service management, superuser custody, system-database maintenance, and global configuration remain owner operations outside ordinary Observatory runtime roles.

### Version posture

The governed database must bind to one explicit PostgreSQL major version at bootstrap time.

Required recorded identity:

```text
server_major_version
server_full_version
server_encoding
server_timezone
password_encryption_setting
host
port
database_class
```

A later major-version change requires a separately reviewed migration and restore plan. A version discovered at runtime is evidence, not automatic acceptance.

### Connection posture

Initial database access is local-only.

The DB-3 design assumes:

```text
network exposure: none
public listener: forbidden
LLM direct connection: forbidden
agent direct connection: forbidden
application access: typed service boundary only when later authorized
```

## Database classes

Every database target must have exactly one class.

| Database class | Purpose | Creation authority | Data allowed | Destructive lifecycle |
|---|---|---|---|---|
| `system_protected` | PostgreSQL system databases | Never by Observatory | None | Never through ob-dev |
| `observatory_governed` | Future canonical local Observatory database | DB-5 owner gate only | Governed synthetic/real evidence only under later gates | No generic drop/reset |
| `observatory_disposable` | DB-4 migration and hammer substrate | DB-4 owner gate and protected ob-dev mode | Fixtures and synthetic proof data only | Create/reset/drop through marker-checked tools |
| `observatory_restore_target` | DB-8 disposable restore verification | DB-8 owner gate | Restored proof copy only | Drop after reviewed restore proof |
| `unknown_or_unclassified` | Any target lacking accepted class | None | None | All mutation blocked |

Class is determined by accepted configuration and verified target identity, never by caller assertion alone.

## Database naming policy

Candidate governed name:

```text
observatory
```

Candidate disposable prefix:

```text
obs_tmp_
```

Candidate restore prefix:

```text
obs_restore_
```

Rules:

- PostgreSQL identifier grammar is `[a-z_][a-z0-9_]*`, maximum 63 characters;
- system databases `postgres`, `template0`, and `template1` are permanently protected;
- the governed database name is protected from disposable reset/drop tools;
- disposable and restore targets require both the expected prefix and an internal disposable marker;
- a matching prefix alone is insufficient proof of disposability;
- caller-selected arbitrary database names are not accepted by dangerous tools.

Final names become binding only in the DB-3 acceptance decision.

## Role model

Roles are separated by function. No routine role receives superuser, role-creation, database-creation, replication, or bypass-RLS privileges.

### `observatory_migrator`

Purpose:

- execute exact accepted forward/rollback migrations under later gates;
- own schema objects where ownership is required;
- update migration history in the same migration transaction.

May later receive:

- connect to the exact target class authorized by the current capability mode;
- schema create/alter/drop privileges only through SHA-bound migration execution;
- no ordinary application login path.

Must not:

- ingest observations;
- serve reads;
- call providers;
- create/drop databases;
- create roles;
- bypass accepted migration paths.

### `observatory_ingest`

Purpose:

- write CapturePackage, attempt, candidate, admission, raw-manifest metadata, drift, and audit records under governed transactions when later authorized.

May later receive:

- execute only bounded stored operations or application transactions mapped to accepted write-authority classes;
- no DDL;
- no migration-history mutation;
- no cross-scope unrestricted reads.

Must not:

- overwrite append-only observations;
- mint evidence identity outside admission transaction;
- persist forbidden concepts;
- expose credentials or raw locators;
- create roles/databases.

### `observatory_reader`

Purpose:

- support database-backed typed evidence reads under DB-7.

May later receive:

- select from approved views/functions only;
- bounded scope-aware evidence resolution;
- no direct access to secret, raw-locator, security-log, or unrestricted operational fields.

Must not:

- write any canonical or audit record;
- execute DDL;
- read arbitrary tables merely because they exist;
- receive direct SQL from LLMs or agents.

### `observatory_auditor`

Purpose:

- bounded human/internal review of migration history, audit events, rights/retention state, and proof metadata.

May later receive read-only access to approved internal audit surfaces.

Must not receive credentials, raw secret values, or customer/private data.

### `observatory_backup`

Purpose:

- run bounded backup/restore operations under DB-8 authority.

This role is inactive and uncreated until the DB-8 design and owner gate.

## Privilege principles

1. Default deny.
2. No routine role owns the database.
3. Schema ownership and object privileges are explicit.
4. No `PUBLIC` create privilege on governed schemas.
5. No application role receives role/database administration.
6. Migration, ingestion, read, audit, and backup duties remain separate.
7. Role membership is explicit and non-inherited unless specifically justified.
8. Privilege grants and revocations require migration/audit evidence.
9. Search path is fixed; caller-controlled schema resolution is forbidden.
10. No direct LLM/agent credential custody.

## Credential and secret custody

### Custody

- PostgreSQL superuser password remains owner-controlled environment configuration.
- ob-dev reads required credentials only at call time from fixed environment names.
- passwords, DSNs, connection strings, secret environment values, and authentication tokens never appear in tool arguments, repository files, logs, proof records, or responses.
- application-role credentials, when later created, require separate managed-secret storage and rotation posture before DB-backed reads or ingestion.

### Fail-closed behavior

Mutation or inspection fails when:

```text
credential missing
credential source unexpected
target class unresolved
binary path mismatch
host or port mismatch
server identity mismatch
capability class insufficient
```

Credential existence never implies authority.

## Fixed binary boundary

PostgreSQL operations through ob-dev use only configured fixed binaries.

Candidate required binaries by phase:

```text
psql.exe
pg_isready.exe
pg_dump.exe
pg_restore.exe
```

Rules:

- no caller-supplied executable path;
- no PATH-based ambiguous resolution for dangerous operations;
- binary version and file identity are reported in redacted structured status;
- DB-4 must prove wrong/missing binary paths fail safely;
- backup binaries remain dormant until DB-8 authority.

## ob-dev capability classes

Accepted design classes:

| Capability class | Permitted behavior |
|---|---|
| `inspection_only` | Readiness, server identity, settings, inventories; no mutation |
| `postgres_disposable_only` | Protected disposable create/reset/drop and disposable migration proof |
| `migration_spec_proof_only` | Validate repository migration files and hashes without governed execution |
| `governed_bootstrap_authorized` | Exact DB-5 owner-approved governed bootstrap/migration actions |
| `real_ingestion_authorized` | Exact later request-specific ingestion actions after DB-9 entry gates |
| `restore_proof_authorized` | Exact DB-8 backup/restore proof actions |

Rules:

- server health reports the active class;
- each tool checks the class independently;
- class is configured outside caller control;
- no capability class grants generic shell, arbitrary SQL, arbitrary scripts, or arbitrary executables;
- dangerous modes remain disabled by default.

## Exact ob-dev tool contract

### Inspection group

```text
postgres_tooling_status()
postgres_readiness()
postgres_server_identity()
postgres_database_inventory()
postgres_role_inventory()
postgres_extension_inventory()
postgres_setting_read(setting_name: allowlisted enum)
postgres_schema_inventory(database_class: allowed enum)
postgres_migration_history_read(database_class: allowed enum)
postgres_constraint_inventory(database_class: allowed enum)
postgres_index_inventory(database_class: allowed enum)
postgres_privilege_inventory(database_class: allowed enum)
```

### Disposable lifecycle group

```text
postgres_create_disposable_database(database: strict disposable name)
postgres_reset_disposable_database(database: strict disposable name, expected_marker: fixed proof token)
postgres_drop_disposable_database(database: strict disposable name, expected_marker: fixed proof token)
postgres_create_bounded_test_roles(database: strict disposable name, profile: allowlisted enum)
```

### Migration group

```text
postgres_validate_migration_file(kind, relative_path, expected_sha256)
postgres_apply_migration_file(database_class, database, relative_path, expected_sha256)
postgres_apply_rollback_file(database_class, database, relative_path, expected_sha256)
postgres_migration_status(database_class, database)
```

### Hammer group

```text
postgres_run_hammer_profile(profile_id: allowlisted identifier)
postgres_run_migration_hammer_profile(profile_id: allowlisted identifier)
postgres_run_role_hammer_profile(profile_id: allowlisted identifier)
postgres_run_concurrency_hammer_profile(profile_id: allowlisted identifier)
postgres_run_restore_verification_profile(profile_id: allowlisted identifier)
```

### Backup/restore group

```text
postgres_create_bounded_backup(database_class, destination_profile)
postgres_restore_to_disposable_database(backup_id, target_database)
postgres_verify_semantic_restore(profile_id, target_database)
```

The precise JSON schemas are DB-4 implementation work, but DB-4 must not broaden these argument classes.

## Migration path and SHA policy

Candidate repository roots:

```text
migrations/forward/
migrations/rollback/
```

Rules:

- migration files are repository-owned UTF-8 `.sql` files;
- each forward migration has one exact rollback partner or an explicit reviewed irreversible disposition;
- file paths are repository-relative and traversal-safe;
- expected SHA-256 is mandatory for validation and execution;
- no raw SQL argument exists;
- migration execution is transactional where PostgreSQL permits;
- migration history records version, direction, hash, repository commit, actor class, target class, start/end time, and outcome;
- a changed file after acceptance has a new version and hash; accepted history is never rewritten;
- out-of-order, duplicate, hash-mismatched, or target-mismatched execution fails closed.

## Migration version policy

Candidate format:

```text
0001_<bounded_description>.sql
0001_<bounded_description>_rollback.sql
```

Rules:

- monotonically increasing four-digit versions for the initial local phase;
- version identity is immutable once accepted/executed;
- one migration represents one reviewable bounded change set;
- no timestamp-only identity as the sole ordering mechanism;
- schema compatibility and rollback expectations are documented before DB-4 proof.

## Backup-before-migration rule

### Governed database

Before every DB-5+ governed migration:

1. verify current database identity and migration history;
2. create a bounded backup using the accepted backup path available for that milestone;
3. hash and record the backup artifact;
4. confirm backup completion before migration begins;
5. record backup ID in migration evidence;
6. stop on any backup failure.

Until DB-8 backup tooling is accepted, DB-5 must define and owner-approve the exact interim backup method before governed migration execution.

### Disposable database

Disposable DB-4 targets do not require durable pre-migration backup, but reset/recreate and rollback proof must be deterministic.

## Restart and recovery procedure for ob-dev

DB-4 implementation must be one coherent capability batch.

Required sequence:

1. commit and push ob-dev implementation with tests passing;
2. record commit and expected tool inventory;
3. owner stops and restarts the ob-dev MCP server using the documented fixed command;
4. owner refreshes the ChatGPT connector/tool inventory;
5. steward verifies health, version, capability class, and expected PostgreSQL tools;
6. if verification fails, do not edit the Observatory repo to pretend the tools exist;
7. recover ob-dev from its clean committed state, restart, and reverify;
8. only after successful verification may DB-4 disposable proof begin.

No repeated piecemeal MCP edits are planned during active database execution.

## Required structured result shape

Every PostgreSQL operation returns a redacted deterministic envelope containing, as applicable:

```text
operation
result
capability_class
database_class
database_identity
server_identity
started_at
finished_at
repository_commit
migration_path
migration_sha256
hammer_id
proof_class
affected_object_counts
evidence_paths
warnings
error_class
```

Never returned:

```text
password
DSN
connection string
secret environment value
raw credential-bearing command
arbitrary raw SQL containing secrets
```

## Hammer mapping

| Boundary | Required hammers |
|---|---|
| Database classes and protected names | H1, H18, H21, H22 |
| Role separation and least privilege | H1, H4, H5, H17, H21 |
| Credential redaction and custody | H17, H18, H21 |
| Fixed binaries and target identity | H18, H21, H22 |
| Migration path/SHA/version rules | H18, H21, H22 |
| Append-only and audit-first mechanisms | H19, H20, H21, H22 |
| Raw pointer boundary | H2, H3, H12, H15, H17, H22 |
| Backup-before-migration | H3, H12, H19, H21, H22 |
| Capability activation | H7, H17, H18, H21 |
| Disposable lifecycle safety | H18, H20, H21, H22 |

Mapping is not execution proof.

## DB-3 acceptance criteria for this boundary

The operational boundary is owner-ready when it:

- fixes instance ownership and version posture;
- defines database classes and protected targets;
- defines role and privilege separation;
- defines credential custody and redaction;
- defines fixed binary behavior;
- defines migration path, SHA, version, and history rules;
- defines backup-before-migration behavior;
- defines ob-dev capability classes, tool groups, result shapes, and restart/recovery procedure;
- maps mechanisms to hammers;
- contains no SQL, DDL, database creation, role creation, or execution authority.

## Final rule

```text
Design the control plane so later database proof can fail safely.
Do not confuse a complete specification with permission to execute it.
```
