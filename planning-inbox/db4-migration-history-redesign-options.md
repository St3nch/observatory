# DB-4 Migration and History Redesign Options

Status: remediation planning candidate; not implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 remediation R2 planning
Authority: `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`

## Purpose

Select an exact migration architecture that cannot produce:

- applied schema without history;
- history without applied schema;
- silent history rewrite;
- duplicate version with changed bytes;
- partial accepted schema after failure;
- concurrent migration forks;
- search-path object substitution;
- false drift confidence from weak fingerprints.

The audit correctly requires atomicity and immutable history. This document compares
implementation mechanisms rather than accepting one mechanism without review.

## Non-negotiable requirements

Every accepted design must provide:

1. one database session and one transaction for transactional DDL plus history;
2. plain insert semantics for migration identity;
3. duplicate version, duplicate path, or changed SHA failure;
4. append-only protection on history itself;
5. exact migration and rollback path/SHA validation before connection;
6. clean-tree or exact-commit execution evidence;
7. transaction-level serialization;
8. safe pinned search path;
9. explicit lock and statement timeouts;
10. before and after schema fingerprints;
11. fingerprint sensitivity to schemas, relations, columns, types, defaults,
    constraints, indexes, triggers, policies, functions, ownership, and privileges
    relevant to project law;
12. exact authority reference and database identity;
13. full failure evidence;
14. defined rollback-history semantics;
15. no caller-selected SQL.

## Option A — Migration-owned transaction and history insert

Shape:

```text
BEGIN;
SET LOCAL ...;
perform DDL;
perform validation preconditions;
INSERT immutable history row;
COMMIT;
```

The runner validates metadata and SHA, binds trusted values, and executes the file in
one session.

### Advantages

- history naturally commits with DDL;
- easy to inspect one transaction boundary;
- no post-commit split-brain window;
- migration author sees the complete atomic unit.

### Risks

- migration files need a secure way to receive exact validated SHA, authority, commit,
  and before-fingerprint values;
- literal substitution is dangerous;
- psql variables require exact escaping and strict identifier/value separation;
- repeated boilerplate can drift;
- migration authors could omit or alter the history statement unless validator proves
  exact structure.

### Required safeguards

- generated immutable execution wrapper rather than free-form string replacement;
- validator proves exactly one history insert as final transactional operation;
- history insert uses bound or safely quoted literals only;
- migration body cannot commit early;
- no `ON CONFLICT` clause;
- test kills execution before final statement and proves full rollback.

## Option B — Runner-owned single-session transaction

Shape:

```text
open one PostgreSQL session
BEGIN
SET LOCAL ...
compute/record before fingerprint
execute exact validated migration body on same session
compute after fingerprint
INSERT immutable history row on same session
COMMIT
```

The migration file contains only the bounded DDL body. The runner owns transaction,
serialization, fingerprinting, and history.

### Advantages

- one uniform implementation for every migration;
- history cannot be omitted by a migration author;
- trusted metadata remains in runner control;
- easier to enforce advisory lock, timeouts, search path, and fingerprinting;
- less migration boilerplate.

### Risks

- current subprocess-per-command design cannot satisfy this;
- requires a real single-session execution method;
- using `psql` correctly may require a generated wrapper file or stdin script;
- error handling and output parsing must prove the transaction truly remained one
  session;
- wrapper generation must not create arbitrary-SQL capability.

### Required safeguards

- fixed implementation only; no caller SQL;
- migration body path and SHA allowlisted;
- generated wrapper exists only in bounded temp/proof root and records its own hash;
- `ON_ERROR_STOP=1` and explicit final rollback on error;
- integration test proves backend PID/session continuity;
- wrapper bytes retained in result evidence or reproducibly derivable.

## Option C — Database function/procedure migration executor

A fixed database-side function receives validated migration identity and performs
history operations while DDL is executed in its transaction context.

### Advantages

- database enforces transaction/history pairing;
- centralizes history rules.

### Risks

- dynamic DDL would require dangerous execution capability;
- SECURITY DEFINER/search-path risks;
- expands permanent control-plane schema;
- difficult to keep migration SQL non-caller-selected;
- creates a privileged runtime surface that may outlive DB-4.

### Disposition

Reject for DB-4. The security and complexity costs outweigh benefits.

## Option D — External migration framework

Adopt Alembic, Flyway, Sqitch, Liquibase, or another migration framework.

### Advantages

- mature migration tracking and operational patterns;
- may reduce custom code.

### Risks

- new dependency and execution surface;
- framework history semantics may not meet exact append-only/SHA/authority/fingerprint
  contract;
- framework commands may widen generic execution;
- Windows/local MCP integration and proof capture require new design;
- current milestone should repair exact bounded substrate, not import an unreviewed
  operational system.

### Disposition

Defer. Reconsider only if Option B proves impractical and after a separate dependency,
security, and governance review.

## Recommended architecture

Select **Option B: runner-owned single-session transaction**, implemented through a
fixed generated execution wrapper or equivalent fixed session API.

Reasoning:

- migration identity and authority stay under the bounded control plane;
- migration files remain declarative DDL bodies rather than self-reporting scripts;
- every execution receives identical advisory lock, timeout, search-path,
  fingerprinting, history, and error behavior;
- validators can focus on metadata and forbidden statements;
- the runner can make missing history impossible by construction.

Option A remains the fallback if a safe single-session wrapper cannot be proven.
Switching from B to A requires an explicit readiness-review amendment, not an
implementation improvisation.

## Exact transaction contract

A forward migration execution must perform, in one backend session:

```text
1. verify current database identity and disposable marker;
2. BEGIN;
3. acquire transaction-scoped advisory lock derived from fixed project/database key;
4. SET LOCAL lock_timeout;
5. SET LOCAL statement_timeout;
6. SET LOCAL idle_in_transaction_session_timeout;
7. SET LOCAL search_path = pg_catalog;
8. verify no existing version/path row conflicts;
9. compute before fingerprint;
10. execute exact SHA-validated migration body;
11. execute migration-specific postconditions;
12. compute after fingerprint;
13. INSERT one immutable history row;
14. COMMIT;
15. emit result record.
```

Any failure before commit must roll back DDL and history.

The wrapper must reject migration bodies containing transaction control unless a
separately approved non-transactional exception exists.

## History model

`obs_meta.schema_migration` must include at minimum:

```text
migration_event_id UUID PK
version bounded ordered identifier
relative_path
file_sha256
paired_rollback_path
paired_rollback_sha256
direction
accepted_authority_reference
code_commit
repository_dirty boolean required false for closure-grade runs
database_identity_id
execution_started_at
execution_finished_at
before_schema_fingerprint
after_schema_fingerprint
fingerprint_algorithm_version
transaction_result
result_record_reference
```

Constraints:

- unique forward version;
- unique forward path;
- same version cannot carry another SHA;
- exact SHA grammar;
- no UPDATE/DELETE privileges;
- reject-mutation trigger;
- rollback events are append-only events, not destructive edits of forward history;
- failed migration attempts belong in result records and optionally a separate
  append-only attempt relation, never as accepted forward rows.

## Rollback history semantics

Choose append-only event semantics:

- a successful forward migration inserts a `forward_applied` event;
- a successful disposable rollback inserts a `rollback_applied` event referencing
  the forward event;
- the original forward row remains immutable;
- effective schema version is derived from ordered forward/rollback events;
- re-application after rollback inserts a new forward event with the same migration
  identity only if policy explicitly permits a new execution occurrence while
  preserving immutable file identity;
- a changed SHA for the same version/path always fails.

A full teardown may drop the history schema only after closure evidence has captured
all events. Dropping history is not itself proof.

## Fingerprint design

The current name-only MD5 is rejected.

The fingerprint must use SHA-256 over a canonical ordered representation of:

- application schemas and owners;
- tables, partitions, views, materialized views, sequences;
- columns, order, types, domains, collation, nullability, defaults, identity/generated
  expressions;
- primary, unique, foreign-key, check, exclusion constraints including validation and
  deferrability state;
- indexes and predicates;
- triggers and enabled state;
- functions/procedures used by enforcement, including language, volatility,
  security-definer flag, configuration, and normalized definition hash;
- RLS enabled/forced state;
- policy commands, roles, USING, and WITH CHECK expressions;
- object owners;
- relevant schema/table/function privileges and default privileges;
- migration-history structural definition, excluding volatile row values where
  necessary to avoid self-reference.

The canonicalization algorithm must be versioned. The result record stores both
algorithm version and digest.

A sabotage test must prove each of these changes affects the fingerprint:

- drop append-only trigger;
- remove FORCE RLS;
- change policy to `USING (true)`;
- remove a FK;
- add PUBLIC privilege;
- change a column type/default;
- mark a constraint NOT VALID;
- change enforcement function body.

## Advisory locking

Use a fixed project key plus database identity, not caller input.

Required proof:

- worker A begins and holds the migration lock;
- worker B attempts a different or same migration;
- worker B times out or receives the defined blocked result;
- no partial DDL/history appears;
- the result record distinguishes serialization blocking from migration failure.

## Timeout posture

Exact values remain owner-ready design inputs, but all three must exist:

- `lock_timeout` short enough to avoid indefinite owner blocking;
- `statement_timeout` sufficient for local disposable migrations but finite;
- `idle_in_transaction_session_timeout` finite.

Timeout values must be fixed per capability/profile, not caller-selected.

## Search-path and ownership posture

- execution session pins `search_path` to `pg_catalog`;
- migration DDL uses fully qualified application names;
- temporary and public schemas are never implicitly trusted;
- application schemas revoke PUBLIC CREATE;
- object ownership is explicitly assigned to migration owner;
- SECURITY DEFINER is forbidden unless separately reviewed and search-path hardened;
- migration body validation rejects unqualified application object references where
  practical.

## Metadata contract redesign

Each forward candidate metadata block must identify:

```text
metadata_version
migration_version
relative_path
file_sha256 or externally bound expected SHA
paired_rollback_path
paired_rollback_sha256
required_prior_effective_version
resulting_effective_version
authority_reference
transactional_required true
fingerprint_algorithm_version
postcondition_profile
```

The package validator must verify:

- unique versions and paths;
- exact chain continuity;
- exact forward/rollback pairing;
- SHA grammar and actual file hash;
- no duplicate or missing number without explicit reserved reason;
- broken fixtures do not masquerade as accepted migrations;
- no symlink/path escape;
- no transaction-control or prohibited operation in migration body;
- all traceability responsibilities map to a migration.

## Required tests

### Unit/contract

- wrapper generation is deterministic;
- exact paths/SHA required;
- metadata chain and pair validation;
- duplicate version/path rejection;
- changed SHA rejection;
- forbidden transaction control rejection;
- search-path and timeout preamble always present;
- history insert contains no ON CONFLICT update;
- result envelope redaction.

### Real PostgreSQL disposable

- forward DDL and history commit together;
- intentional failure after DDL leaves neither DDL nor history;
- intentional failure during history insert leaves no DDL;
- history UPDATE/DELETE rejected;
- duplicate reapply rejected;
- concurrent migration serialized;
- search-path hijack fails;
- fingerprint changes for each sabotage class;
- rollback inserts immutable rollback event;
- reapply semantics follow the selected policy;
- full teardown does not become substitute for rollback evidence.

## Stop conditions

Stop implementation on any:

- second database session for history recording;
- `ON CONFLICT DO UPDATE` in migration history;
- caller-supplied SQL or timeout/lock/search-path values;
- fingerprint blind to a project enforcement mechanism;
- mutable/deletable accepted history;
- rollback deleting or rewriting forward history;
- advisory lock absent;
- migration body owning uncontrolled transaction boundaries;
- dirty-tree closure-grade execution;
- missing exact rollback SHA where rollback is claimed.

## R2 planning exit

R2 design is owner-ready when:

- Option B implementation shape is exact enough for a bounded file/tool manifest;
- Option A fallback conditions are explicit;
- history schema and rollback semantics are fixed;
- fingerprint algorithm inputs are fixed;
- all required unit and real-PostgreSQL tests are named;
- no code or PostgreSQL execution has occurred under this planning artifact.
