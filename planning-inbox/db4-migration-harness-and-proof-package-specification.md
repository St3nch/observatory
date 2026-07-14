# DB-4 Migration Harness and Proof Package Specification

Status: planning specification; owner-approved artifact inventory; not implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 — Database Hammer Harness and Migration Specification

## Purpose

Define the exact future Observatory-side migration, rollback, disposable-harness,
hammer-profile, and proof package that a separately authorized DB-4 implementation
would create.

This document contains no executable SQL or migration bytes. It creates no
`database/` directory, starts no PostgreSQL service, creates no database or role,
runs no hammer, and authorizes no implementation.

## Boundary

DB-4 future execution targets only databases classified `disposable_postgres` with:

- exact prefix `observatory_test_`;
- accepted marker;
- expected server fingerprint;
- exact database identity expectation;
- active `migration_spec_proof_only` or narrower accepted capability;
- exact DB-4 implementation authority reference.

The protected names `postgres`, `template0`, `template1`, and `observatory`
can never be lifecycle or migration targets during DB-4.

DB-4 creates no governed database and persists no real or synthetic Observatory
evidence as an accepted corpus.

## Future Observatory implementation manifest

The following paths are proposed for a separately authorized implementation. They do
not exist under this planning package.

### Folder control

1. `database/README.md`
2. `database/migrations/README.md`
3. `database/rollbacks/README.md`
4. `database/hammer-fixtures/README.md`
5. `database/hammer-profiles/README.md`
6. `tests/postgres/README.md`

### Forward migration candidates

7. `database/migrations/001_identity_namespaces.sql`
8. `database/migrations/002_governance_scope.sql`
9. `database/migrations/003_capture_provider.sql`
10. `database/migrations/004_evidence_identity.sql`
11. `database/migrations/005_raw_support.sql`
12. `database/migrations/006_audit_append_only.sql`
13. `database/migrations/007_scope_rls_roles.sql`
14. `database/migrations/008_typed_read.sql`
15. `database/migrations/010_recovery_verification.sql`

### Paired rollback candidates

16. `database/rollbacks/001_identity_namespaces.sql`
17. `database/rollbacks/002_governance_scope.sql`
18. `database/rollbacks/003_capture_provider.sql`
19. `database/rollbacks/004_evidence_identity.sql`
20. `database/rollbacks/005_raw_support.sql`
21. `database/rollbacks/006_audit_append_only.sql`
22. `database/rollbacks/007_scope_rls_roles.sql`
23. `database/rollbacks/008_typed_read.sql`
24. `database/rollbacks/010_recovery_verification.sql`

Order 009 is intentionally reserved for hammer fixtures outside governed migration
history, matching the accepted DB-3 sequence.

### Intentionally broken disposable candidates

25. `database/hammer-fixtures/009_missing_scope_boundary.sql`
26. `database/hammer-fixtures/009_mutable_evidence.sql`
27. `database/hammer-fixtures/009_missing_audit_pair.sql`
28. `database/hammer-fixtures/009_excess_role_privilege.sql`
29. `database/hammer-fixtures/009_unbounded_raw_locator.sql`
30. `database/hammer-fixtures/009_dirty_constraint_seed.sql`
31. `database/hammer-fixtures/009_partial_migration_failure.sql`
32. `database/hammer-fixtures/009_schema_version_divergence.sql`

Broken candidates are never accepted migrations and never appear as successful
migration-history entries.

### Fixed hammer profile manifests

33. `database/hammer-profiles/db4_invariants_v1.json`
34. `database/hammer-profiles/db4_migration_v1.json`
35. `database/hammer-profiles/db4_roles_v1.json`
36. `database/hammer-profiles/db4_concurrency_v1.json`
37. `database/hammer-profiles/db4_restore_verification_v1.json`

Profiles contain only closed IDs, exact repository paths, SHA-256 values, expected
hammer IDs, bounded concurrency counts, timeout profile IDs, and proof-output
identifiers. They contain no SQL, command, module, credential, host, port, or
executable supplied by a caller.

### Repository validators and tests

38. `tools/check_database_package.py`
39. `tests/test_database_package.py`
40. `tests/postgres/conftest.py`
41. `tests/postgres/test_db4_invariants.py`
42. `tests/postgres/test_db4_migrations.py`
43. `tests/postgres/test_db4_roles.py`
44. `tests/postgres/test_db4_concurrency.py`
45. `tests/postgres/test_db4_restore.py`
46. `.gitignore`

The future Observatory implementation manifest is exactly 46 paths. Any additional
path requires a revised owner gate.

## Migration mapping

| Candidate | Accepted DB-3 responsibility |
|---|---|
| 001 | database marker, migration history, namespaces, privilege baseline |
| 002 | governance vocabularies, scopes, target anchors, assignments |
| 003 | query panels, capture packages/events, validation, providers, fingerprints, drift |
| 004 | candidates, admission, observations, evidence identity, citation identity |
| 005 | raw manifest/payload/token/support structures without relational raw bytes |
| 006 | audit-first same-transaction and append-only enforcement |
| 007 | direct scope relationships, RLS/equivalent enforcement, functional role privileges |
| 008 | safe typed-read views/functions, deterministic pagination support |
| 009 fixtures | intentionally broken candidates and dirty seeds, outside migration history |
| 010 | schema fingerprint and semantic-restore verification support |

## Migration metadata contract

Every forward and rollback candidate must declare bounded metadata that the validation
tool can read without executing the file:

- immutable version;
- direction;
- responsibility ID;
- paired path;
- expected paired SHA-256;
- required prior version;
- resulting version;
- database class;
- transaction posture;
- required proof class;
- authority reference placeholder;
- expected namespaces affected;
- destructive-posture classification.

The metadata format must be exact and machine-checked. Unknown keys, missing fields,
duplicate versions, or pair disagreement block validation.

## Transaction rules

- one candidate executes as one transaction when PostgreSQL permits;
- stop-on-error is mandatory;
- non-transactional operations are absent from the first DB-4 package;
- a failed candidate must not become an accepted migration-history row;
- before/after schema fingerprints are recorded;
- migration history is append-only;
- dirty or divergent history blocks the next candidate;
- forward and rollback bytes are reviewed and SHA-bound together;
- DB-4 rollback targets disposable databases only.

## Physical design preservation

The candidate set must preserve all accepted DB-2 and DB-3 boundaries:

- separate evidence, observation, capture-package, and capture-event identities;
- immutable facts and append-only transitions;
- provider testimony and disagreement computed on read;
- rights and retention fail closed;
- raw manifests separated from raw bytes and access tokens;
- no raw storage locator exposure;
- direct scope ownership and isolation;
- customer/private data absent;
- overlays, reports, strategy, recommendations, conclusions, and LLM reasoning absent;
- typed reads expose shaped evidence, not direct table access.

## Role profile plan

The future bounded test-role tool may create only these disposable profiles:

1. `db4_minimal_migration_roles_v1`;
2. `db4_scope_isolation_roles_v1`;
3. `db4_typed_read_roles_v1`.

Profile intent:

| Profile | Future roles under test | Required denial |
|---|---|---|
| minimal migration | migration owner/migrator split | provider calls, ingestion, arbitrary database creation |
| scope isolation | ingest plus scope-bound variants | cross-scope reads/writes and bypass |
| typed read | reader/auditor/security-reader variants | direct mutation, raw locator, credential/auth data |

Names, grants, and setup statements are fixed in repository-owned implementation.
The caller supplies only a profile ID and database identity.

## Hammer-family coverage

The future profile set must cover:

- scope and contamination;
- rights and retention;
- evidence and raw integrity;
- append-only and audit-first;
- concurrency and idempotency;
- migration forward/rollback/failure recovery;
- role and privilege boundaries;
- typed-read authorization, pagination, and truncation;
- backup/restore semantic continuity.

Every accepted H1-H22 implication from the DB-2 freeze is mapped to at least one
profile result. A mapping is not a pass.

## Required expected failures

DB-4 must prove the harness can fail by applying or evaluating each broken candidate
against a disposable database and receiving the expected rejection or hammer failure.

An expected failure result records:

- candidate/profile identity and SHA-256;
- exact hammer IDs;
- failure phase;
- expected result code;
- observed sanitized result;
- before/after schema fingerprint;
- transaction outcome;
- cleanup disposition.

A broken candidate that unexpectedly passes blocks DB-4.

## Concurrency ceilings

Fixed first-package ceilings:

- maximum concurrent workers: 2;
- maximum attempts per concurrency case: 2;
- maximum target databases: 1;
- maximum profile invocation per owner-confirmed operation: 1;
- no retry after a mutation-shaped timeout without identity reconciliation;
- no caller-defined process, thread, delay, query, or loop.

Concurrency profiles test duplicate identity, capture admission, evidence mint,
policy assignment, append-only transitions, and audit pairing.

## Proof output

Future runtime proof belongs outside Observatory evidence under a bounded ignored
working root, proposed as:

`C:\dev\observatory\.database-proof\db4\`

The future `.gitignore` edit ignores the working root. Only a later reviewed,
redacted, machine-readable result register may be committed. Dumps, credentials,
raw subprocess transcripts, database files, and private content are never committed.

This planning document creates no proof directory.

## Validator obligations

`tools/check_database_package.py` must fail on:

- missing or extra manifest path;
- executable candidate outside registered roots;
- non-UTF-8 or integrity findings;
- duplicate/missing versions;
- forward/rollback pair mismatch;
- SHA mismatch;
- forbidden path traversal or symlink escape;
- profile unknown keys or commands;
- broken fixture admitted as a governed migration;
- missing H1-H22 mapping;
- missing role/restore/concurrency profile;
- protected/governed DB target;
- unignored proof working root.

The validator does not execute SQL or connect to PostgreSQL.

## Test proof classes

- `tests/test_database_package.py`: repository contract proof only;
- `tests/postgres/*` without a real authorized target: fixture/contract proof only;
- real disposable execution through accepted tools: may earn
  `real_postgres_disposable_pass`;
- no DB-4 result may claim `real_local_database_pass`;
- production proof is impossible under DB-4.

## Future implementation phases

### Phase A — ob-dev code

Implement and commit the exact 17-path `ob_dev` package. Run fixture tests. Owner
reviews the commit.

### Phase B — owner restart

Owner restarts `ob-dev`, verifies 60 tools and default `inspection_only`, and
refreshes the connector. No mutation class is enabled.

### Phase C — Observatory candidates

Create and commit the exact 46-path Observatory package. Validation remains
non-executing until the implementation decision permits the exact files.

### Phase D — disposable proof

Owner supplies the separately authorized local setup and capability transition.
Tools create one marked disposable target, apply candidates, run profiles and broken
candidates, roll back where specified, and remove the disposable target.

### Phase E — DB-4 review

Record exact results, verify no governed database or evidence exists, and return to
the owner for DB-4 acceptance/closure and any DB-5 decision.

One future owner decision may authorize all five phases only if it binds both exact
manifests and every capability/action. Failure at one phase stops later phases.

## Cleanup and recovery

- only a database with prefix plus marker may be dropped;
- identity is re-read after timeout before any retry;
- proof artifacts remain bounded and secret-reviewed;
- failed cleanup is reported; it is not hidden by deleting evidence;
- the governed name is never a cleanup target;
- no Git clean/reset command is authorized;
- no database directory or backup is manually deleted through generic tooling.

## DB-5 boundary

DB-5 remains blocked. It requires a new decision naming:

- governed database creation;
- exact role profiles;
- exact accepted migration paths and SHA-256 values;
- capability transition to `governed_bootstrap_authorized`;
- governed backup-before-migration proof;
- exact validation and hammer profiles.

Disposable DB-4 success does not authorize governed bootstrap.

## Final rule

The package must prove both that the intended schema works and that broken schema
candidates fail. Until a later owner gate, all 46 future paths are names on paper.
