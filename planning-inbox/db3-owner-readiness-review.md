# DB-3 Owner Readiness Review

Status: owner-ready planning review; not acceptance, closure, DB-4, or implementation authority
Date: 2026-07-14
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Review result: ready_for_owner_review

## Review question

Has fresh DB-3 produced a coherent planning-only PostgreSQL operational boundary,
physical schema specification, and future ob-dev control-plane contract derived from
the exact accepted DB-2 freeze without restoring retired work or performing database
implementation?

## Result

The DB-3 candidate package is ready for owner review.

This review does not:

- accept any candidate;
- close DB-3;
- activate DB-4;
- authorize ob_dev edits or restart;
- authorize PostgreSQL, databases, roles, credentials, SQL, migrations, hammers,
  backup, restore, persistence, providers, capture, customer data, or production.

## Exact review targets

### Candidate 1 — accepted-input traceability

Path:

planning-inbox/db3-accepted-input-traceability-matrix.md

Version/status:

- version 0.1
- planning specification; not authority

SHA-256:

db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98

Role:

Maps the exact accepted DB-2 classifications, identities, lifecycles, boundaries,
raw postures, forbidden persistence, and H1-H22 expectations to future physical
responsibilities.

### Candidate 2 — combined PostgreSQL design

Path:

planning-inbox/db3-fresh-postgres-design-specification-v0-1.md

Version/status:

- version 0.1
- planning candidate; not authority

SHA-256:

9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e

Role:

Specifies the proposed PostgreSQL 18 development target, database classes, role and
credential boundaries, namespaces, future relation responsibilities, constraints,
indexes, append-only and audit-first mechanisms, scope isolation, raw boundary,
typed-read boundary, and non-executable migration/rollback/backup policies.

### Candidate 3 — future ob-dev control plane

Path:

planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md

Version/status:

- version 0.1
- planning candidate; not authority

SHA-256:

d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec

Role:

Specifies 28 future bounded PostgreSQL tools, expected 60 total tools if the current
32 remain, capability/database classes, input and result contracts, protected names,
credential custody, migration/profile SHA rules, proof metadata, and the planned
owner-controlled restart/connector recovery procedure.

## Accepted foundation verification

The package binds the exact accepted DB-2 freeze:

- path: planning-inbox/db2-physical-data-contract-freeze-specification.md
- version: 0.2.1
- SHA-256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891

It also preserves:

- decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md;
- decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md;
- hammers/hammer-matrix-v0-2.md;
- hammers/acceptance-gate-policy-v0-2.md;
- hammers/per-hammer-result-register-v0-1.md;
- 02-boundaries.md;
- POST_V1_DATABASE_ROADMAP.md.

No planning-inbox artifact is promoted by self-description.

## Retired-artifact exclusion

Verified absent:

- decisions/2026-07-13-db2-closure-and-db3-activation.md
- decisions/2026-07-13-db3-closure-and-db4-activation.md
- planning-inbox/db3-postgres-operational-boundary-specification.md
- planning-inbox/db3-physical-schema-specification.md
- planning-inbox/db3-specification-readiness-review.md

No retired filename is reused. No retired artifact was read or reconstructed.

## Traceability review

| Area | Result |
|---|---|
| Singular DB-2 classifications | pass |
| Distinct identity namespaces | pass |
| Immutable facts vs append-only transitions vs derived state | pass |
| Scope and customer boundary | pass |
| Rights and retention fail-closed | pass |
| Provider attribution/disagreement | pass |
| Candidate/admission/evidence lifecycle | pass |
| Raw manifest/payload/token separation | pass |
| Freshness, volatility, and claim fitness derived only | pass |
| Overlays and consumer requests ephemeral | pass |
| Strategy/recommendation/conclusion/reasoning forbidden | pass |
| H1-H22 mapped to future failing mechanisms | pass |
| Open rulings preserved fail-closed | pass |

## Operational-boundary review

| Area | Candidate disposition |
|---|---|
| PostgreSQL major | 18; exact minor/build inspected and bound before DB-4 proof |
| Instance | Owner-controlled local development only |
| Production | Absent and unauthorized |
| Governed database name | observatory, protected until an exact DB-5 gate |
| Disposable prefix | observatory_test_ plus generated bounded suffix and marker |
| Protected names | postgres, template0, template1, observatory |
| Minimum roles | migrator, ingest, reader, auditor/security/backup specializations |
| Role posture | Non-superuser least privilege; functional and login roles separated |
| Credential custody | External owner-controlled environment/secret boundary; never arguments/results/repo |
| Time/encoding | UTC/timezone-aware semantics and UTF-8 |
| Extensions | None assumed |
| Backup-before-migration | Mandatory for future governed migrations |
| Production/network authority | None |

## Physical-schema review

The combined design:

- uses seven application responsibility namespaces plus a safe read boundary;
- gives every relation one narrow responsibility;
- keeps domain identities separate;
- uses an internal governed-target anchor only for assignment integrity and never as
  an evidence identity;
- defines no persistent disagreement, claim support, freshness result, overlay,
  report state, recommendation, strategy, or LLM reasoning structure;
- prohibits relational raw bytes and underlying storage locators;
- specifies direct scope relationships and database-enforced isolation;
- specifies insert-only history with transition relations;
- specifies same-transaction audit verification;
- specifies deterministic migration identity and future rollback proof;
- creates no executable DDL.

## Control-plane review

The future contract contains exactly 28 PostgreSQL tool headings:

- 9 inspection tools;
- 4 disposable lifecycle tools;
- 7 migration/inventory tools;
- 5 hammer-profile tools;
- 3 backup/restore tools.

The contract preserves:

- fixed configured binaries/host/port;
- no caller-supplied executable;
- no arbitrary SQL;
- no generic shell, PowerShell, Python, or command;
- strict identifiers;
- exact paths and SHA-256;
- protected governed/system names;
- disposable prefix plus marker;
- explicit capability class;
- structured redacted results;
- per-hammer proof metadata;
- owner-controlled restart/connector recovery;
- no self-edit, self-update, self-restart, or privilege escalation.

## Authority-checker correction

During validation, tools/check_authority_sync.py failed because its stale DB-2 closure
guard rejected every fresh filename containing db3 or db4.

The bounded correction:

- adds only the four approved DB-3 planning paths to an exact allowlist;
- retains all five retired paths as forbidden;
- rejects every unlisted DB-3 and DB-4 artifact;
- adds a temporary-directory regression test.

Changed support files:

- tools/check_authority_sync.py
- tests/test_authority_sync.py
- planning-inbox/README.md

The correction changes no project milestone, doctrine, database authority, or
implementation permission.

## Validation evidence

### Authority sync

Tool/profile:

ob_dev_run_test_profile — authority_sync

Result:

- exit code 0
- passed true
- DB-2 trusted, accepted, complete, and last trusted
- DB-3 active for fresh planning and specification only
- DB-4 and implementation unauthorized

The first run failed on the stale allowlist. The checker correction and rerun are
preserved in this review rather than pretending the failure never happened.

### Unit tests

Tool/profile:

ob_dev_run_test_profile — unittest

Result:

- exit code 0
- 207 tests passed
- network execution remained unauthorized
- provider fixture paths remained fail-closed

### Ruff

Tool/profile:

ob_dev_run_test_profile — ruff

Result:

- exit code 1
- two findings outside this package:
  - unused local variable first in src/observatory_provider_cross_check/compare.py
  - unused json import in tests/test_dataforseo_probe.py
- neither file was changed in DB-3
- no Ruff finding identified the changed checker or authority test

The unrelated baseline is recorded and not silently fixed under DB-3.

### Document and repository checks

Passed:

- text integrity on all DB-3 planning files and planning index;
- zero executable SQL statement shapes;
- zero obsolete tool references in the new package;
- exactly 28 future PostgreSQL tool headings;
- no .sql file;
- no migrations directory;
- all five retired paths absent;
- git diff check exit code 0;
- protected audits/kaizen_to_slash_goal_prompt.md untouched and untracked.

## Remaining owner decisions

The owner must decide independently:

1. Accept, reject, or revise the exact traceability candidate and SHA.
2. Accept, reject, or revise the exact combined PostgreSQL design and SHA.
3. Accept, reject, or revise the exact future ob-dev control-plane contract and SHA.
4. Accept or reject the bounded authority-checker correction.
5. Close or continue DB-3.
6. Separately authorize or refuse a future DB-4 implementation package.

No answer implies another.

## Candidate-specific review points

Owner attention is especially requested for:

- PostgreSQL 18 as the planned major family;
- observatory as the future governed database name;
- observatory_test_ as the disposable prefix;
- the proposed role names and separation;
- seven application namespaces plus obs_read;
- the internal governed_target assignment anchor;
- forced RLS/equivalent plus explicit scope joins;
- trigger/privilege-based append-only defense;
- deferred same-transaction audit verification;
- 28 new ob-dev PostgreSQL tools and expected total count of 60;
- one coherent ob-dev expansion/restart rather than piecemeal edits;
- backup/restore tools included in the future coherent contract but capability-gated.

## Recommended owner gate

If the package is accepted without revision, the owner should make three separate
decisions.

Decision 1 — accept exact DB-3 planning package:

- planning-inbox/db3-accepted-input-traceability-matrix.md
  SHA-256 db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98
- planning-inbox/db3-fresh-postgres-design-specification-v0-1.md
  SHA-256 9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e
- planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md
  SHA-256 d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec
- bounded authority-checker correction and regression test.

Decision 2 — close or continue DB-3.

Decision 3 — separately authorize or refuse preparation of an exact DB-4
implementation package.

Even if all three are affirmative, DB-4 execution authority must name the exact
ob_dev edit scope, disposable PostgreSQL actions, credential setup, migration/profile
fixtures, required hammers, and restart/refresh procedure. It must not authorize a
governed database or evidence persistence.

## Non-authorizations

No PostgreSQL startup, database, schema, role, credential, secret, SQL, DDL,
migration file, migration execution, ob_dev implementation, tool registration,
restart, connector refresh, disposable database, real PostgreSQL hammer, backup,
restore, governed database, synthetic or real persistence, provider, capture, raw
storage, customer/private data, recurring work, DB-4, production, strategy,
recommendation, conclusion, report-state, or LLM-reasoning persistence is authorized.

## Final assessment

The fresh DB-3 planning package is coherent, traceable, bounded, and ready for owner
review. It has not been accepted, and the database still does not exist.
