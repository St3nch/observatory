# DB-1 ob-dev Database Control-Plane Requirements

Status: planning specification; no MCP implementation or database authority
Date: 2026-07-12
Milestone: DB-1 — Post-v1 Audit Reconciliation and Ruling Closure

## Purpose

Make the ob-dev MCP capability expansion an explicit dependency of the database phase instead of an implied future task.

The owner requires ob-dev to remain the Observatory development MCP. Database creation, migration execution, and real-Postgres hammer proof must not depend on Go8 or on repeated emergency MCP edits during the database build.

This document plans one coherent ob-dev database-control expansion before governed database creation. It does not authorize editing ob-dev, restarting the server, creating Postgres objects, executing SQL, or running migrations.

## Current truth

The ob-dev repository currently provides bounded repository, text, Git, environment, and process-inspection tools.

Its README and settings already preserve a future PostgreSQL posture:

- fixed `psql.exe` and `pg_isready.exe` binaries from configured paths;
- fixed host, port, superuser, and default-database settings;
- password read only from the `POSTGRES_PASSWORD` environment variable at call time;
- no password tool argument or result exposure;
- no arbitrary SQL strings from callers;
- identifier grammar `[a-z_][a-z0-9_]*`, maximum 63 characters;
- migration execution only from exact registered-root `.sql` files bound to expected SHA-256.

No PostgreSQL MCP tool is implemented yet.

## Timing ruling for the roadmap

```text
DB-1 plans and records the required control-plane surface.
DB-2 freezes the logical data contract without requiring database tools.
DB-3 accepts the operational boundary and the exact ob-dev database-tool contract.
DB-4 implements and proves the expanded ob-dev tool surface against disposable Postgres before any governed local database is created.
DB-5 may use the accepted tools for governed local database bootstrap and migration execution only after a separate owner gate.
```

The intent is one coherent MCP expansion and one planned restart/refresh cycle, not repeated piecemeal edits while database work is active.

## Required capability groups

### 1. Read-only Postgres inspection

Required before mutation tools:

```text
postgres_tooling_status
postgres_readiness
postgres_server_identity
postgres_database_inventory
postgres_role_inventory
postgres_extension_inventory
postgres_setting_read
postgres_schema_inventory
postgres_migration_history_read
```

Rules:

- fixed binaries and fixed configured host/port only;
- no caller-supplied executable paths;
- no arbitrary SQL;
- redacted outputs;
- no passwords, connection strings, or secret environment values returned;
- deterministic structured results suitable for proof records.

### 2. Disposable-database lifecycle

Required for DB-4 hammer work:

```text
postgres_create_disposable_database
postgres_drop_disposable_database
postgres_create_bounded_test_roles
postgres_reset_disposable_database
```

Rules:

- disposable names must use a fixed Observatory test prefix plus strict identifier validation;
- tools must refuse the governed database name and protected system databases;
- drop/reset requires exact expected database identity and disposable marker proof;
- no generic database deletion tool;
- operations must be auditable and return exact before/after state.

### 3. Migration execution and verification

Required for DB-4/DB-5:

```text
postgres_validate_migration_file
postgres_apply_migration_file
postgres_apply_rollback_file
postgres_migration_status
postgres_constraint_inventory
postgres_index_inventory
postgres_privilege_inventory
```

Rules:

- migrations come only from exact repository-relative `.sql` paths;
- expected SHA-256 is mandatory;
- no raw SQL tool argument;
- forward and rollback files remain paired;
- execution target must be an explicitly named allowed database class;
- governed-database execution remains disabled until DB-5 owner authorization;
- transaction outcome and server error evidence must be returned without leaking secrets.

### 4. Hammer execution profiles

Required for real-substrate proof:

```text
postgres_run_hammer_profile
postgres_run_migration_hammer_profile
postgres_run_role_hammer_profile
postgres_run_concurrency_hammer_profile
postgres_run_restore_verification_profile
```

Rules:

- profiles are allowlisted by repository file/config identifier;
- no generic command, script, Python, PowerShell, or SQL execution;
- each result records hammer ID, proof class, execution surface, database identity class, commit, migration hash, result, and evidence path;
- concurrency profiles must launch only fixed repository-owned test entry points;
- fixture passes cannot be reported as real-Postgres passes.

### 5. Backup and restore controls

Required no later than DB-8, preferably designed in the same expansion:

```text
postgres_create_bounded_backup
postgres_restore_to_disposable_database
postgres_verify_semantic_restore
```

Rules:

- fixed `pg_dump` / `pg_restore` binaries when selected by later ruling;
- exact destination roots under registered bounded paths;
- no cloud upload tool;
- no arbitrary restore target;
- semantic verification includes evidence-ID resolution, manifest/hash checks, scope isolation, and audit continuity;
- encryption and off-machine transfer remain separate owner-controlled gates.

## Capability activation model

Tool existence must not imply permission to use every mode.

Recommended control classes:

```text
inspection_only
postgres_disposable_only
migration_spec_proof_only
governed_bootstrap_authorized
real_ingestion_authorized
restore_proof_authorized
```

The server must fail closed when the active capability class does not admit the requested operation.

A tool must not infer authority from the presence of credentials, a database, migration files, or a prior successful hammer run.

## ob-dev self-proof requirements

Before the expanded MCP surface may be trusted:

- unit tests cover identifier rejection, protected-database rejection, path traversal, SHA mismatch, password redaction, wrong binary paths, wrong database class, and attempted raw SQL injection;
- fixture tests prove deterministic result shapes;
- disposable real-Postgres tests prove create/apply/rollback/drop behavior;
- intentionally broken migrations and hammers demonstrably fail;
- server health reports the enabled capability class and PostgreSQL tool count;
- no generic shell, arbitrary PowerShell, arbitrary Python, arbitrary SQL, or arbitrary executable path is introduced;
- the owner performs the required server restart and connector refresh after the coherent expansion is committed.

## Roadmap gates

### DB-3 exit dependency

DB-3 must produce an accepted ob-dev database-tool contract that binds:

- tool names and schemas;
- allowed database classes;
- credential custody;
- fixed binary paths;
- protected database names;
- migration path and SHA requirements;
- capability activation classes;
- audit/result shapes;
- restart and recovery procedure for the MCP server.

### DB-4 exit dependency

DB-4 cannot close unless:

- the accepted ob-dev database tools are implemented;
- the owner has restarted/refreshed ob-dev;
- disposable Postgres lifecycle works through ob-dev;
- migration and rollback files execute only through exact-path SHA-bound tools;
- mandatory hammers can fail and pass through allowlisted profiles;
- per-hammer proof records classify the execution as `real_postgres_disposable_pass` where earned.

### DB-5 entry dependency

The governed local database must not be created by manual ad-hoc commands merely because the MCP tooling was forgotten.

DB-5 entry requires either:

1. the accepted ob-dev governed-bootstrap tools are present and proven; or
2. an explicit owner decision documents a bounded manual bootstrap exception and why the MCP route is unavailable.

The default is option 1.

## Non-authorizations

```text
No ob-dev source edits under DB-1.
No MCP restart under DB-1.
No Postgres creation.
No database or role mutation.
No SQL or migration execution.
No disposable database creation.
No hammer execution against Postgres.
No governed database bootstrap.
No provider calls or ingestion.
```

## Final rule

```text
The database phase must not arrive at DB-4 and discover that the steward cannot operate the test substrate.
Plan the control plane now.
Build it once.
Gate every dangerous mode.
```
