# DB-4 Exact ob-dev Implementation Package Specification

Status: planning specification; owner-approved artifact inventory; not implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 — Database Hammer Harness and Migration Specification

## Purpose

Define one exact future `ob_dev` implementation package for the accepted 28-tool
PostgreSQL control plane. This file specifies a future edit manifest and acceptance
contract. It does not edit `C:\dev\ob-dev`, register tools, start PostgreSQL,
create databases, handle credentials, restart a server, or authorize execution.

## Normative inputs

- accepted DB-3 control-plane contract:
  `planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md`
  SHA-256 `d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec`;
- accepted DB-3 physical design:
  `planning-inbox/db3-fresh-postgres-design-specification-v0-1.md`
  SHA-256 `9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e`;
- DB-4 dormant-code disposition matrix;
- accepted hammer matrix, acceptance policy, and per-hammer result register;
- DB-3 closure and DB-4 package-preparation decision.

If this specification differs from an accepted input, the accepted input wins until
an owner decision explicitly accepts a revision.

## Future implementation release identity

Proposed coherent expansion:

| Field | Planned value |
|---|---|
| Repository | `C:\dev\ob-dev` |
| Base commit | `46df253c40b9de03826aa562c744a1943fe52ccf` |
| Current version | 0.4.0 |
| Proposed implementation version | 0.5.0 |
| Existing registered tools preserved | 32 |
| PostgreSQL tools added | 28 |
| Expected total tools | 60 |
| Default PostgreSQL capability | `inspection_only` |
| Generic execution | false |
| Remote/upstream | none |
| Push | not applicable unless owner later configures a remote; no remote creation authorized |

Implementation must stop if the live `ob_dev` base differs materially from the base
commit or if unrelated changes overlap the manifest.

## Exact future ob_dev file manifest

### Modify

1. `README.md`
2. `pyproject.toml`
3. `src/ob_dev/settings.py`
4. `src/ob_dev/server.py`
5. `src/ob_dev/postgres_runtime.py`
6. `src/ob_dev/postgres_control.py`
7. `src/ob_dev/postgres_hammers.py`
8. `src/ob_dev/postgres_backup.py`
9. `tests/test_server.py`
10. `tests/test_postgres_runtime.py`
11. `tests/test_postgres_control.py`
12. `tests/test_postgres_hammers.py`
13. `tests/test_postgres_backup.py`

### Create

14. `src/ob_dev/postgres_contract.py`
15. `src/ob_dev/postgres_inspection.py`
16. `tests/test_postgres_contract.py`
17. `tests/test_postgres_inspection.py`

### Explicitly unchanged

- `start.ps1`;
- root `server.py`;
- `src/ob_dev/root_policy.py`;
- Git, GitHub, file, validation, import, venv, and process-lock modules/tests;
- every file in `chatgpt_mcp`;
- every file in `observatory` during the `ob_dev` implementation commit.

Any required path outside the 17-path future manifest blocks implementation and
requires a revised owner gate.

## Module ownership

| Module | Future responsibility |
|---|---|
| `postgres_contract.py` | closed vocabularies, configuration validation, authority references, database identity, capability checks, result envelope, redaction, digests |
| `postgres_runtime.py` | fixed binary discovery/version checks, readiness, server identity/fingerprint, subprocess runner; no service mutation |
| `postgres_inspection.py` | role, extension, setting, database, schema, migration, constraint, index, and privilege inspection |
| `postgres_control.py` | disposable lifecycle, bounded test roles, migration validation/status/forward/rollback; no governed DB-4 target |
| `postgres_hammers.py` | five allowlisted profile runners and per-hammer result shaping |
| `postgres_backup.py` | bounded backup, disposable restore, semantic restore verification |
| `server.py` | exact 28 registrations, annotations, health fields, public schemas, no business logic |
| `settings.py` | fixed non-secret configuration names and safe defaults; no secret reads at import beyond names/presence |
| tests | hostile validators, exact registry/schema, fixture subprocess behavior, redaction, and regression |

## Exact 28-tool registry

### Inspection: 9

| Tool | Owning module | Minimum class |
|---|---|---|
| `postgres_tooling_status` | runtime/contract | `inspection_only` |
| `postgres_readiness` | runtime | `inspection_only` |
| `postgres_server_identity` | runtime | `inspection_only` |
| `postgres_database_inventory` | inspection | `inspection_only` |
| `postgres_role_inventory` | inspection | `inspection_only` |
| `postgres_extension_inventory` | inspection | `inspection_only` |
| `postgres_setting_read` | inspection | `inspection_only` |
| `postgres_schema_inventory` | inspection | `inspection_only` |
| `postgres_migration_history_read` | inspection | `inspection_only` |

### Disposable lifecycle: 4

| Tool | Owning module | Minimum class |
|---|---|---|
| `postgres_create_disposable_database` | control | `postgres_disposable_only` |
| `postgres_drop_disposable_database` | control | `postgres_disposable_only` |
| `postgres_reset_disposable_database` | control | `postgres_disposable_only` |
| `postgres_create_bounded_test_roles` | control | `postgres_disposable_only` |

### Migration and physical inventory: 7

| Tool | Owning module | Validation/execution class |
|---|---|---|
| `postgres_validate_migration_file` | control | inspection allowed; never executes |
| `postgres_apply_migration_file` | control | `migration_spec_proof_only` for DB-4 disposable |
| `postgres_apply_rollback_file` | control | `migration_spec_proof_only` for DB-4 disposable |
| `postgres_migration_status` | inspection/control | inspection allowed |
| `postgres_constraint_inventory` | inspection | inspection allowed |
| `postgres_index_inventory` | inspection | inspection allowed |
| `postgres_privilege_inventory` | inspection | inspection allowed |

### Hammer profiles: 5

| Tool | Owning module | Minimum class |
|---|---|---|
| `postgres_run_hammer_profile` | hammers | `migration_spec_proof_only` |
| `postgres_run_migration_hammer_profile` | hammers | `migration_spec_proof_only` |
| `postgres_run_role_hammer_profile` | hammers | `migration_spec_proof_only` |
| `postgres_run_concurrency_hammer_profile` | hammers | `migration_spec_proof_only` |
| `postgres_run_restore_verification_profile` | hammers | `restore_proof_authorized` |

### Backup and restore: 3

| Tool | Owning module | Required class |
|---|---|---|
| `postgres_create_bounded_backup` | backup | `restore_proof_authorized` |
| `postgres_restore_to_disposable_database` | backup | `restore_proof_authorized` |
| `postgres_verify_semantic_restore` | backup | `restore_proof_authorized` |

No alias, compatibility wrapper, service-control tool, catalog-selection tool, raw SQL
tool, or generic subprocess tool is registered.

## Health expansion

Version 0.5.0 health must add:

- `postgres_tool_count`, derived as 28;
- `postgres_capability_class`;
- `postgres_configured`;
- `postgres_mutation_enabled`;
- `registry_digest`.

Existing service, framework, roots, tool count, and generic-execution fields remain.
Total tool count and registry digest are derived from the live public registry.

Health must not call PostgreSQL or read a password value.

## Capability implementation

Closed capability vocabulary:

1. `inspection_only`;
2. `postgres_disposable_only`;
3. `migration_spec_proof_only`;
4. `governed_bootstrap_authorized`;
5. `real_ingestion_authorized`;
6. `restore_proof_authorized`.

Rules:

- missing, empty, or unknown configuration becomes `inspection_only` plus a blocked
  configuration warning;
- no class implies the powers of another except the explicitly stated inspection
  floor;
- each tool checks its required class at execution time;
- `governed_bootstrap_authorized` remains unusable until a DB-5 decision is validated;
- `real_ingestion_authorized` remains unusable until DB-9;
- production is absent and always rejected;
- a credential, running server, or existing database supplies no capability.

## Database identity implementation

Closed database classes:

- `protected_system`;
- `disposable_postgres`;
- `governed_local`;
- `production`.

Fixed values:

- governed name: `observatory`;
- disposable prefix: `observatory_test_`;
- protected: `postgres`, `template0`, `template1`, `observatory`;
- maximum target count per mutation: one.

Every disposable database must have both the accepted prefix and an accepted marker.
A prefix alone is insufficient. A marker alone is insufficient.

The exact marker representation is a fixed metadata relation/record created by the
lifecycle implementation and verified before reset, drop, migration, role, hammer,
backup, or restore actions. The marker contains no secret or owner identity.

## Public-schema rules

Every input schema must:

- reject additional properties;
- use strict identifiers and closed literals;
- expose no `sql`, `command`, executable, absolute path, environment value,
  password, or connection string;
- require exact path/SHA for repository-owned executable inputs;
- require database identity expectations before mutation;
- require authority references where the contract names them;
- require confirmation digests for destructive operations.

Every result uses the accepted common envelope. Operation-specific evidence is a
closed Pydantic model. Unknown subprocess/error material is sanitized or suppressed.

## Internal subprocess posture

Allowed binaries are derived only from the fixed configured PostgreSQL binary
directory:

- `psql.exe`;
- `pg_isready.exe`;
- `pg_dump.exe`;
- `pg_restore.exe`.

No shell is used. No caller may select a binary, command, timeout, host, port, user,
or maintenance database. Fixed internal SQL statements may exist only as reviewed
constants for exact operations; callers never supply SQL or fragments.

Service start, stop, and restart are owner actions outside MCP. The existing dormant
service-control public wrapper is removed from the future surface.

## Exact future test obligations

### `tests/test_postgres_contract.py`

Must cover:

- all capability and database classes;
- default/fail-closed class behavior;
- identifier grammar and length;
- protected names and governed-name rejection;
- prefix plus marker;
- authority path/status;
- path containment, symlink escape, suffix, SHA;
- confirmation and registry digests;
- result envelope and secret suppression;
- forbidden public property names.

### `tests/test_postgres_inspection.py`

Must cover all nine inspection tools and three physical inventories with:

- bounded results;
- allowlisted settings;
- no row data;
- no password/auth hashes;
- unknown-shape refusal;
- fingerprint mismatch;
- include-system restrictions;
- definition digests instead of raw definitions.

### Existing PostgreSQL tests

Must be rewritten to cover exact accepted names and contracts. Fixture/mock tests
remain fixture proof and cannot claim real PostgreSQL behavior.

### `tests/test_server.py`

Must assert:

- exactly 60 tools;
- exactly 28 PostgreSQL names;
- exact annotation class per tool;
- deterministic registry digest;
- no forbidden aliases;
- no service-control tool;
- no generic execution;
- closed schemas;
- health fields and default `inspection_only`;
- existing 32-tool behavior unchanged.

## Fixed validation sequence before owner restart

Future implementation must pass, in order:

1. package import check for all PostgreSQL modules;
2. Ruff;
3. full pytest suite;
4. exact registry/schema tests;
5. secret-pattern and text-integrity scans;
6. diff check;
7. complete reviewed `ob_dev` diff;
8. exact 17-path staged manifest;
9. manifest-locked local commit.

No restart occurs within implementation tooling. The owner performs restart and
connector refresh only after reviewing the committed result.

## Rollback of the ob-dev expansion

Because `ob_dev` has no remote, rollback means an owner-reviewed local Git action to
the last known healthy commit. No MCP self-reset or self-checkout tool is added.

Before restart, the previous running server remains the recovery surface. After a
failed restart verification, disposable/governed mutation stays disabled and the
owner returns to the last known healthy committed version through a manual reviewed
action.

No database rollback is implied by an `ob_dev` code rollback.

## Implementation stop conditions

Stop before mutation if:

- the base commit or 17-path manifest is stale;
- a required tool differs from the accepted 28;
- a new dependency is required;
- a public schema needs arbitrary SQL/command/path input;
- a password must cross an MCP argument/result;
- service control appears necessary;
- governed database behavior cannot remain blocked;
- an additional module or test path is required;
- current 32-tool regressions fail;
- default capability is not `inspection_only`.

## Separate implementation gate

This specification is ready to become an implementation input only after an owner
decision binds:

- this artifact by exact SHA-256;
- the 17-path future `ob_dev` manifest;
- version 0.5.0;
- the exact 28-tool registry;
- allowed credential setup;
- allowed disposable PostgreSQL actions;
- allowed migration/profile fixtures;
- real-disposable proof scope;
- the owner restart/refresh procedure.

Until then, no `ob_dev` file named here may be changed under DB-4.

## Final rule

One coherent registry, one closed contract, one reviewed commit, one owner restart.
No tool existence becomes database authority.
