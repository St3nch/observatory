# DB-4 Remediation Exact Implementation Manifest v0.1

Status: planning candidate; not implementation authority
Milestone: DB-4 remediation
Depends on:

- `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`
- `planning-inbox/db4-audit-remediation-program-v0-1.md`
- `planning-inbox/db4-db3-implementation-traceability-matrix.md`
- `planning-inbox/db4-migration-history-redesign-options.md`
- `planning-inbox/db4-behavioral-hammer-remapping.md`

## Purpose

Define the exact bounded file and capability package required to replace the thin DB-4 prototype with a DB-3-faithful migration specification, behavioral hammer system, durable proof records, and safer operating model.

This document authorizes nothing by itself.

## Governing implementation rules

1. DB-3 remains the physical-design authority.
2. Every executable object must map to the R1 traceability matrix.
3. No schema object may be added because it is convenient or familiar.
4. No accepted DB-3 responsibility may be omitted without an explicit owner ruling.
5. Migration/history correctness is implemented before the larger schema set.
6. Behavioral hammers are implemented before any closure campaign.
7. Result records are emitted for failures as well as passes.
8. One validated implementation batch should require no more than one planned MCP restart.
9. No governed database is created.
10. No PostgreSQL execution begins until a separate execution gate is accepted.

## Observatory repository exact path package

### Replace current forward migrations

The following existing files are diagnostic prototypes and must be replaced in place after the implementation gate opens:

```text
database/migrations/001_identity_namespaces.sql
database/migrations/002_governance_scope.sql
database/migrations/003_capture_provider.sql
database/migrations/004_evidence_identity.sql
database/migrations/005_raw_support.sql
database/migrations/006_audit_append_only.sql
database/migrations/007_scope_rls_roles.sql
database/migrations/008_typed_read.sql
database/migrations/010_recovery_verification.sql
```

### Replace current rollbacks

```text
database/rollbacks/001_identity_namespaces.down.sql
database/rollbacks/002_governance_scope.down.sql
database/rollbacks/003_capture_provider.down.sql
database/rollbacks/004_evidence_identity.down.sql
database/rollbacks/005_raw_support.down.sql
database/rollbacks/006_audit_append_only.down.sql
database/rollbacks/007_scope_rls_roles.down.sql
database/rollbacks/008_typed_read.down.sql
database/rollbacks/010_recovery_verification.down.sql
```

### Migration responsibility freeze

#### 001 — identity, migration substrate, namespaces, privilege baseline

Must create and enforce:

- application namespaces `obs_meta`, `obs_governance`, `obs_capture`, `obs_evidence`, `obs_raw`, `obs_audit`, `obs_security`, `obs_read`;
- safe schema ownership baseline;
- no PUBLIC CREATE on application schemas;
- append-only `obs_meta.schema_migration` responsibility;
- `obs_meta.database_identity` responsibility;
- `obs_meta.capability_history` responsibility;
- append-only enforcement for accepted metadata facts;
- migration advisory-lock namespace and deterministic fingerprint inputs;
- no application role receives ownership.

The runner, not the migration file, owns atomic history insertion under the selected R2 architecture.

#### 002 — governance identities, vocabularies, targets, and assignments

Must implement every accepted `obs_governance` relation from DB-3:

- scope and scope transitions;
- governed vocabulary families, versions, entries, transitions;
- source families and transitions;
- capture instruments and transitions;
- governed targets and typed target bindings;
- source-family assignments;
- rights assignments and transitions;
- retention assignments and transitions;
- freshness assignments and transitions;
- volatility assignments and transitions.

Must mechanically enforce:

- strict identifiers and bounded lengths;
- exact typed target binding rather than a free-form polymorphic locator;
- missing or unknown rights/retention blocks later admission and read paths;
- one effective compatible assignment where the accepted design requires it;
- no customer identity or strategy fields.

#### 003 — query panels, capture packages, captures, validation, providers, and drift

Must implement every accepted `obs_capture` relation from DB-3:

- query panel, version, item, transition;
- panel run and transitions;
- capture package and transitions;
- capture event and transitions;
- validation-failure vocabulary versions;
- validation results;
- providers and transitions;
- provider testimony and transitions;
- shape fingerprints and recognition transitions;
- parser references and support transitions;
- drift events and review transitions.

Must enforce:

- used panel versions are immutable;
- complete CapturePackage envelope before any capture event;
- exact package-to-capture binding;
- duplicate prevention keys scoped to accepted authority/package context;
- provider attribution inseparable from testimony;
- no provider winner, disagreement ledger, strategy, or conclusion persistence.

#### 004 — candidate, admission, observation, evidence, and citation identity spine

Must implement every accepted `obs_evidence` relation from DB-3:

- observed artifact references and transitions;
- candidate observations and transitions;
- admission transitions;
- observations and transitions;
- evidence identities and transitions;
- citation handles and transitions.

Must enforce:

- candidate is not evidence and is not citable;
- one accepted admission outcome per candidate;
- admitted observation requires successful admission and valid scope/rights/retention/provenance;
- evidence identity cannot exist before accepted admission;
- citation handle is non-enumerable, internal, and distinct from all other IDs;
- lifecycle change is append-only;
- no mutable current-status column becomes canonical.

#### 005 — raw manifest, payload identity, opaque token, and integrity facts

Must implement every accepted `obs_raw` relation from DB-3:

- raw manifests and transitions;
- raw payload identities and transitions;
- opaque artifact tokens and transitions;
- raw integrity observations.

Must enforce:

- no raw bytes in ordinary relational storage;
- no path, drive letter, URI, bucket name, key, signed URL, connection string, or reversible locator;
- exact hash algorithm and digest grammar;
- non-negative byte counts;
- bounded media type;
- distinct raw manifest, payload, observation, evidence, and citation identities;
- rights/retention support requirements.

#### 006 — append-only and audit-first enforcement

Must implement:

- `obs_audit.audit_event`;
- `obs_audit.audit_supersession`;
- append-only trigger functions and attachments for accepted protected relations;
- same-transaction audit-first enforcement for consequential writes;
- deferred verification or equivalent commit-time mechanism proving required audit pairing;
- bounded correction through supersession rather than mutation.

Must not rely on application logs after commit.

#### 007 — roles, grants, ownership, and forced RLS

Must implement the accepted functional role profiles:

- `observatory_migrator`;
- `observatory_ingest`;
- `observatory_reader`;
- `observatory_auditor`;
- `observatory_security_reader`;
- `observatory_backup`.

The exact disposable proof role names may include an approved `observatory_test_` prefix but must map one-to-one to these profiles.

Must enforce:

- NOLOGIN functional roles;
- no role owns application objects;
- no PUBLIC privileges on application schemas or relations;
- reader has no base-table write access and no raw token access;
- ingest has no schema or role management and no direct broad CRUD;
- FORCE ROW LEVEL SECURITY on scope-bound tables;
- explicit USING and WITH CHECK policies;
- bounded transaction-local scope context;
- no role can disable triggers, constraints, or row security.

#### 008 — typed-read security-barrier views/functions

Must implement only bounded DB-3-approved read surfaces:

- evidence lookup;
- observation-package read;
- safe provider attribution;
- current rights/retention/freshness disposition;
- attached warnings and caveats;
- safe raw-support status.

Must enforce:

- security-barrier semantics where applicable;
- deterministic bounded ordering;
- keyset or equivalent bounded pagination;
- cursor binding and expiration inputs where the database interface owns them;
- uniform blocked/not-found behavior;
- no raw token, locator, credential, security event, audit internals, strategy, recommendation, or report state.

#### 009 — intentionally broken candidates

No governed forward migration exists at 009.

All broken candidates remain outside accepted forward migration history and must enter through the same validator and transaction wrapper used by ordinary forward candidates.

#### 010 — recovery and semantic verification support

Must implement only metadata and bounded verification structures needed to prove:

- schema version continuity;
- migration history continuity;
- evidence identity resolution continuity;
- raw manifest hash continuity;
- audit continuity;
- scope isolation after restore.

It must not claim backup or restore has occurred.

## New Observatory profile and proof paths

### Data-driven profile definitions

Create or replace exact JSON profile files under:

```text
database/hammer-profiles/db4-preconditions.json
database/hammer-profiles/db4-behavioral-core.json
database/hammer-profiles/db4-role-rls.json
database/hammer-profiles/db4-concurrency.json
database/hammer-profiles/db4-migration-history.json
database/hammer-profiles/db4-broken-candidates.json
database/hammer-profiles/db4-cleanup.json
database/hammer-profiles/db4-restore-semantic.json
```

Each profile must declare:

- profile version;
- exact check IDs;
- applicable hammer IDs;
- proof class;
- required capability;
- database class;
- exact operation class;
- fixture/candidate paths and expected SHA values where applicable;
- expected SQLSTATE or semantic outcome;
- cleanup action and cleanup verification;
- result-record schema version.

No profile may contain caller-selected arbitrary SQL.

### Broken-candidate set

Retain and redesign the existing eight candidates as real admission-path candidates:

```text
database/hammer-fixtures/009_dirty_constraint_seed.sql
database/hammer-fixtures/009_excess_role_privilege.sql
database/hammer-fixtures/009_missing_audit_pair.sql
database/hammer-fixtures/009_missing_scope_boundary.sql
database/hammer-fixtures/009_mutable_evidence.sql
database/hammer-fixtures/009_partial_migration_failure.sql
database/hammer-fixtures/009_schema_version_divergence.sql
database/hammer-fixtures/009_unbounded_raw_locator.sql
```

Add these missing hostile candidates:

```text
database/hammer-fixtures/009_history_rewrite.sql
database/hammer-fixtures/009_duplicate_version_changed_sha.sql
database/hammer-fixtures/009_history_without_schema.sql
database/hammer-fixtures/009_schema_without_history.sql
database/hammer-fixtures/009_search_path_hijack.sql
database/hammer-fixtures/009_owner_bypass_rls.sql
database/hammer-fixtures/009_rls_without_force.sql
database/hammer-fixtures/009_missing_with_check.sql
database/hammer-fixtures/009_default_privilege_leak.sql
database/hammer-fixtures/009_public_schema_create.sql
database/hammer-fixtures/009_disable_trigger_attempt.sql
database/hammer-fixtures/009_not_valid_constraint.sql
database/hammer-fixtures/009_cross_scope_foreign_key.sql
database/hammer-fixtures/009_duplicate_evidence_mint.sql
database/hammer-fixtures/009_concurrent_migration_without_lock.sql
```

Every fixture must have a manifest row stating:

- violated invariant;
- expected validator or PostgreSQL rejection point;
- expected SQLSTATE or semantic failure;
- expected rollback state;
- expected migration-history state;
- cleanup and cleanup verification.

### Durable proof paths

Create:

```text
database/proof/README.md
database/proof/result-register.schema.json
database/proof/campaign-register.schema.json
database/proof/supersession.schema.json
database/proof/accepted/.gitkeep
```

Runtime local evidence must be written only beneath a configured ignored owner-local evidence root. Redacted accepted records may be promoted into `database/proof/accepted/` only after validation and review.

### Validators and tests

Replace or extend:

```text
tools/check_database_package.py
tests/test_database_package.py
tests/postgres/test_db4_migrations.py
tests/postgres/test_db4_invariants.py
tests/postgres/test_db4_roles.py
tests/postgres/test_db4_concurrency.py
tests/postgres/test_db4_restore.py
```

Add:

```text
tests/postgres/test_db4_history_atomicity.py
tests/postgres/test_db4_profile_manifest.py
tests/postgres/test_db4_broken_candidate_manifest.py
tests/postgres/test_db4_result_register.py
tests/postgres/test_db4_cleanup.py
tests/postgres/test_db4_security_posture.py
```

## ob-dev exact implementation package

The preferred design keeps the public MCP tool surface stable and makes hammer behavior data-driven.

### Existing source paths expected to change

```text
src/ob_dev/postgres_contract.py
src/ob_dev/postgres_runtime.py
src/ob_dev/postgres_control.py
src/ob_dev/postgres_inspection.py
src/ob_dev/postgres_hammers.py
src/ob_dev/postgres_backup.py
src/ob_dev/settings.py
src/ob_dev/server.py
README.md
pyproject.toml
```

### New source paths

```text
src/ob_dev/postgres_profiles.py
src/ob_dev/postgres_fingerprint.py
src/ob_dev/postgres_result_register.py
src/ob_dev/postgres_redaction.py
src/ob_dev/postgres_authority.py
```

### Existing tests expected to change

```text
tests/test_postgres_contract.py
tests/test_postgres_runtime.py
tests/test_postgres_control.py
tests/test_postgres_inspection.py
tests/test_postgres_hammers.py
tests/test_postgres_backup.py
tests/test_server.py
```

### New tests

```text
tests/test_postgres_profiles.py
tests/test_postgres_fingerprint.py
tests/test_postgres_result_register.py
tests/test_postgres_redaction.py
tests/test_postgres_authority.py
tests/test_postgres_migration_atomicity.py
tests/test_postgres_marker_identity.py
tests/test_postgres_restart_minimization.py
```

## Required ob-dev behavior

### Migration runner

The forward and rollback runner must:

1. validate root-relative path and expected SHA;
2. reject symlinks and path escapes;
3. verify authority file existence and operation class;
4. verify server, database class, name, marker, database identity, and capability;
5. acquire a fixed advisory lock;
6. open one psql session;
7. begin one transaction;
8. set local lock timeout, statement timeout, search path, and application name;
9. compute and capture the before fingerprint;
10. execute the exact migration candidate;
11. compute the after fingerprint in the same session;
12. insert an immutable history row in the same transaction;
13. commit;
14. emit a redacted result record;
15. on any failure, roll back and record failure without inserting success history.

### Fingerprinting

Fingerprint inputs must include deterministic ordered representations of:

- namespaces;
- tables and table kinds;
- columns, types, nullability, defaults, identity/generated properties;
- primary, unique, foreign-key, check, and exclusion constraints;
- indexes and predicates;
- triggers and enabled state;
- functions/procedures used by the package, including definition hashes;
- RLS enabled/forced state;
- policies, commands, roles, USING, and WITH CHECK expressions;
- object owners;
- grants and default privileges relevant to application namespaces.

### Profiles

The profile loader must:

- load only allowlisted exact paths beneath the Observatory root;
- validate schema version;
- validate exact check IDs and no duplicates;
- validate referenced file SHA values;
- validate required capability and proof class;
- reject caller-provided SQL, executable paths, or new operation types;
- emit the exact profile hash in every result.

### Result register

The result writer must:

- create immutable files using exclusive creation;
- never overwrite an existing execution ID;
- include dirty-tree state and exact code commits;
- include all checks, including blocked and failed checks;
- include cleanup attempts and verification;
- include secret-review result;
- support supersession through a separate record;
- produce no credential, URI password, raw payload, private content, prompt, or reasoning.

### Marker and authority

The disposable marker must bind:

- database name;
- PostgreSQL database OID or another stable database identity;
- server identity;
- database class;
- creation authority reference;
- created-at timestamp;
- marker version.

Every mutation/proof path must verify it.

Unknown database classification is unauthorized.

### Roles and RLS

Behavioral tools must be able to use fixed allowlisted role switching without exposing arbitrary role selection.

The runner must verify:

- current session user;
- active role after switching;
- role is in the approved test-role set;
- no superuser, bypassrls, create role, create db, replication, or login privilege;
- no unexpected memberships.

### Tool surface

Do not add one MCP tool per hammer.

Retain the bounded PostgreSQL tools unless the exact implementation review proves a tool should be removed or renamed. Prefer generic bounded profile execution behind existing profile tools.

Any registry count change must be documented and tested, but count alone is not a safety property.

## Implementation order

```text
I1 profile/result/authority contracts and tests
I2 atomic migration runner and fingerprinting
I3 DB-3-faithful migration and rollback replacement
I4 behavioral profiles and broken candidates
I5 role/RLS and concurrency behavior
I6 durable result writer, validators, and cleanup
I7 security/reachability and redaction hardening
I8 full static/unit validation
I9 one owner restart and connector refresh
I10 separate disposable execution campaign
```

## Stop conditions

Stop on any:

- path outside this exact package without a revised owner gate;
- missing traceability row;
- migration/history split transaction;
- mutable history;
- caller-selected arbitrary SQL or executable path;
- profile drift or missing SHA binding;
- superuser-only proof of role/RLS behavior;
- result overwrite;
- incomplete failure record;
- marker mismatch;
- unknown database classification;
- secret exposure;
- unverified remote mutation exposure;
- more than one planned restart caused by avoidable unbatched code iteration;
- governed database, DB-5, provider, customer/private data, production, or recurring work.
