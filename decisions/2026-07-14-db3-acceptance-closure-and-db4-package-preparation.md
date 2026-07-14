# Decision — DB-3 Acceptance, Closure, and DB-4 Package Preparation

Status: accepted decision
Date: 2026-07-14
Owner authority: three explicit independent owner decisions recorded in project conversation
Related milestone: DB-3 closure / DB-4 implementation-package preparation activation

## Decision

The owner made three independent affirmative decisions.

### OR-I1 — accept the exact DB-3 planning package

The owner accepts these exact planning artifacts:

```text
path: planning-inbox/db3-accepted-input-traceability-matrix.md
version: 0.1
sha256: db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98

path: planning-inbox/db3-fresh-postgres-design-specification-v0-1.md
version: 0.1
sha256: 9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e

path: planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md
version: 0.1
sha256: d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec
```

The owner also accepts the bounded authority-checker correction and regression test
committed with the package:

```text
tools/check_authority_sync.py
tests/test_authority_sync.py
commit: 588fd754d954817f92530c6408a20b312f81af65
```

The accepted DB-3 artifacts remain immutable planning specifications. Their
acceptance does not turn them into executable SQL, migrations, tools, or database
objects.

### OR-I2 — close DB-3 successfully

DB-3 — Postgres Operational Boundary and Physical Schema Specification is closed
successfully. DB-3 is trusted, accepted, complete, and becomes the last trusted
completed database milestone.

DB-1 remains trusted and complete. DB-2 remains trusted, accepted, and complete.

### OR-I3 — authorize preparation of an exact DB-4 implementation package

The owner activates:

```text
DB-4 — Database Hammer Harness and Migration Specification
```

DB-4 authority is limited to preparing an exact, reviewable implementation package.

Preparation may define:

- the exact future `ob_dev` source and test edit manifest;
- the exact 28-tool PostgreSQL control-plane registry derived from the accepted DB-3
  contract;
- fixed input/output schemas, capability classes, protected names, credential
  boundaries, redaction rules, and connector recovery steps;
- exact migration-specification and rollback-pair file inventories without creating
  executable migration files;
- disposable-database and hammer-profile plans without starting PostgreSQL or
  creating a database;
- required validation, restart, owner action, and staged acceptance sequences;
- explicit stop conditions and non-authorizations.

Preparation must first produce an exact artifact inventory for owner review. No
implementation artifact may be created merely because this milestone is active.

## Explicit non-authorizations

This decision does not authorize:

```text
PostgreSQL startup, shutdown, restart, or control
database creation, reset, drop, or connection
role creation or privilege mutation
credentials, passwords, secrets, or credential setup
SQL execution
executable SQL or DDL files
executable migration or rollback files
migration validation or execution
ob_dev source implementation
PostgreSQL tool registration
ob_dev restart or connector refresh
disposable database lifecycle
real PostgreSQL hammers
backup or restore execution
governed database creation
synthetic or real persistence
provider integration or provider calls
paid pulls
ingestion or capture
raw-payload storage
customer or private data
recurring work
production work
DB-5 planning or activation
```

The accepted DB-3 specification describes future behavior; it does not supply
execution authority.

## Required DB-4 package gate

Before any DB-4 implementation, the owner must separately approve an exact package
that names at minimum:

1. every `ob_dev` file to create or modify;
2. every Observatory planning, fixture, migration-specification, and test path;
3. the exact tool registry and expected total tool count;
4. credential custody and owner-only setup actions;
5. protected database names and disposable-name/marker enforcement;
6. fixed PostgreSQL binary, host, port, and version inspection behavior;
7. migration path and SHA-256 controls;
8. hammer profiles and proof-result contracts;
9. restart and connector-refresh procedure;
10. validation, staged manifest, commit, and manual push sequence;
11. explicit implementation permissions and prohibitions.

Approval of package preparation is not approval of that future package.

## Permanently retired artifacts

The five retired DB-3/DB-4 artifacts remain permanently absent and forbidden:

```text
decisions/2026-07-13-db2-closure-and-db3-activation.md
decisions/2026-07-13-db3-closure-and-db4-activation.md
planning-inbox/db3-postgres-operational-boundary-specification.md
planning-inbox/db3-physical-schema-specification.md
planning-inbox/db3-specification-readiness-review.md
```

They must not be restored, salvaged, reused, copied, paraphrased, or reconstructed.

## Authority impact

```text
scope change: yes — explicit owner decision
doctrine change: no
DB-3 acceptance: yes
DB-3 closure: yes
DB-4 package preparation authority: yes
DB-4 implementation authority: no
database authority: no
execution authority: no
```

## Final rule

```text
DB-3 specifies the future physical boundary and closes.
DB-4 may prepare one exact implementation package for separate owner review.
Nothing in this decision authorizes the database or its tooling to execute.
```
