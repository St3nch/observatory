# DB-4 Owner Readiness Review

Status: owner-ready planning review; not package acceptance or implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 — Database Hammer Harness and Migration Specification
Review result: ready_for_validation_and_owner_review

## Review question

Does the DB-4 planning package define one exact, bounded, reviewable future
implementation across `ob_dev` and Observatory, derived from accepted DB-3, while
creating no executable SQL, migrations, tools, database, credentials, or runtime
authority?

## Candidate result

Yes, subject to final repository validation recorded before commit.

The package separates:

- current dormant-code evidence;
- exact future `ob_dev` code and test scope;
- exact future Observatory migration/harness scope;
- owner-controlled security, credential, restart, and recovery actions;
- the later implementation decision.

## Exact review targets

### Dormant-code gap and disposition

Path:

`planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md`

Version: 0.1

SHA-256:

`a65919ace9da12c16b7dcc3aa7b8262c1150f2acbc2dc521c91ca7c2ee055a2a`

Role:

Binds the live dormant `ob_dev` modules/tests by hash, identifies reusable
mechanisms and conflicts, and disposes all 17 dormant wrappers against the accepted
28-tool contract.

### Exact ob-dev implementation package

Path:

`planning-inbox/db4-exact-ob-dev-implementation-package-specification.md`

Version: 0.1

SHA-256:

`b44711fe80a1967ddf3d5413ce150fcc5d56ca7f61ddb5d8f42747c63d9ce14a`

Role:

Defines the future 17-path `ob_dev` edit manifest, version 0.5.0, exact 28 tools,
expected 60-tool total, module ownership, capability/database classes, common
envelope, tests, validation, rollback, and implementation stop conditions.

### Migration harness and proof package

Path:

`planning-inbox/db4-migration-harness-and-proof-package-specification.md`

Version: 0.1

SHA-256:

`9aff671e31fe94dabe5acca6a6631b14f8197a7c85ad55115caced354c7dad2e`

Role:

Defines the future exact 46-path Observatory implementation manifest: migration and
rollback candidates, broken fixtures, fixed profiles, validators, tests, disposable
proof, cleanup, and DB-5 boundary.

### Security and owner-action runbook

Path:

`planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md`

Version: 0.1

SHA-256:

`8c08648051a2b88c58d5999f861596c79e8a479f68f02e6061586111edb86b7f`

Role:

Defines credential custody, fixed configuration, redaction, authority binding,
owner-only restart/refresh, capability transition, failure recovery, proof logging,
and stop conditions.

## Accepted foundation

The package preserves the exact accepted DB-3 inputs:

| Artifact | SHA-256 |
|---|---|
| `planning-inbox/db3-accepted-input-traceability-matrix.md` | `db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98` |
| `planning-inbox/db3-fresh-postgres-design-specification-v0-1.md` | `9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e` |
| `planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md` | `d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec` |

Acceptance/closure authority:

`decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md`

DB-3 remains immutable. DB-4 planning does not edit accepted DB-3 bytes.

## Live dormant baseline

Read-only inspection bound the current `ob_dev` baseline:

- commit `46df253c40b9de03826aa562c744a1943fe52ccf`;
- version 0.4.0;
- 32 registered tools;
- generic execution false;
- clean worktree;
- no remote/upstream;
- 57 tests passing;
- Ruff passing;
- dormant PostgreSQL modules import successfully;
- no dormant wrapper is registered.

This baseline proves code availability and fixture tests only. It proves no real
PostgreSQL behavior.

## Package completeness review

| Requirement | Result |
|---|---|
| Exact accepted 28-tool registry | pass |
| Expected 60-tool total | pass |
| Exact future `ob_dev` manifest | pass — 17 paths |
| Exact future Observatory manifest | pass — 46 paths |
| Dormant wrapper disposition | pass |
| Protected/governed name posture | pass |
| Disposable prefix and marker | pass |
| Capability classes | pass |
| Database classes | pass |
| Common result envelope | pass |
| Authority/identity/confirmation gates | pass |
| Fixed binary and endpoint posture | pass |
| Credential non-disclosure | pass |
| Owner-only restart and service control | pass |
| Migration/rollback pair inventory | pass |
| Broken-candidate inventory | pass |
| Fixed hammer profiles | pass |
| Proof classes and result register | pass |
| Timeout reconciliation | pass |
| Cleanup and recovery | pass |
| DB-5 separation | pass |
| Production absence | pass |

## Exact future implementation manifests

### ob-dev

Future code implementation is limited to 17 paths:

- 13 existing files modified;
- 4 files created;
- no new dependency;
- no `start.ps1` change;
- no root-policy change;
- no non-PostgreSQL module change.

The implementation commit occurs in `ob_dev` only.

### Observatory

Future migration/harness implementation is limited to 46 paths:

- 6 folder/control indexes;
- 9 forward candidates;
- 9 paired rollback candidates;
- 8 intentionally broken fixtures;
- 5 profile manifests;
- 8 validator/test files;
- 1 `.gitignore` update.

The Observatory implementation commit remains separate from the `ob_dev` commit.

## Tool registry review

The 28 accepted tools are partitioned exactly:

- 9 inspection;
- 4 disposable lifecycle;
- 7 migration/physical inventory;
- 5 hammer profile;
- 3 backup/restore.

No service-control, catalog-selection, raw SQL, generic command, arbitrary path,
self-edit, self-update, self-restart, capability-escalation, production, provider,
capture, or ingestion tool is included.

## Risk review

### Risk: dormant code mistaken for accepted implementation

Disposition: fail closed. The gap matrix requires substantial replacement and exact
contract tests. Dormant code remains unregistered.

### Risk: tool registration treated as database permission

Disposition: capability defaults to `inspection_only`; health reports mutation
disabled; exact authority and identity are checked at execution.

### Risk: prefix-only deletion

Disposition: lifecycle mutation requires both `observatory_test_` and an accepted
marker plus confirmation digest. Protected/governed names are unconditional rejects.

### Risk: secret exposure

Disposition: owner custody, no secret arguments/results, centralized suppression,
synthetic sentinel tests, and operation failure on exposure review.

### Risk: service-control escalation

Disposition: service mutation is absent from the 28 tools. Restart and PostgreSQL
service control remain owner actions.

### Risk: mock proof inflation

Disposition: fixture tests retain fixture/contract proof. Only separately authorized
real disposable execution may earn `real_postgres_disposable_pass`.

### Risk: implementation package too broad

Disposition: exact 17-path and 46-path manifests, no dependency changes, phased
execution, stop on extra path.

### Risk: DB-4 becomes DB-5

Disposition: `observatory` remains protected, governed capability blocked, no
governed database/roles/migrations/evidence, new owner decision required.

## Validation record

### Current baseline

- `ob_dev` pytest: 57 passed;
- `ob_dev` Ruff: passed;
- PostgreSQL package imports: passed;
- `observatory` authority sync before package: passed;
- protected audit file: excluded and untouched.

### Required final package checks

Before this planning package is committed:

- authority sync must pass with an exact five-artifact DB-4 planning allowlist;
- complete Observatory unittest must pass;
- Ruff must show no new finding in changed files;
- text integrity must pass;
- executable SQL statement-shape scan must return zero in planning artifacts;
- all retired paths must remain absent;
- no `sql/`, `migrations/`, `database/`, or `.sql` artifact may appear;
- diff check must pass;
- exact eight-path staged manifest must match owner approval.

The final commit report is the durable execution evidence for these checks.

## Remaining owner decision

This planning package may be accepted, rejected, or revised.

Acceptance alone does not authorize implementation. A later decision must
independently authorize or refuse:

1. the exact 17-path `ob_dev` implementation;
2. version 0.5.0 and the exact 28/60 registry;
3. the exact 46-path Observatory implementation;
4. owner credential setup;
5. owner restart and connector refresh;
6. exact disposable PostgreSQL lifecycle;
7. exact migration/profile files and SHA binding;
8. real disposable hammer and restore proof;
9. cleanup;
10. continued prohibition of governed/real/production work.

One decision may authorize the complete phased DB-4 implementation only when it binds
the final planning artifacts by exact SHA-256 and includes stop-after-failure
sequencing.

## Non-authorizations

This review does not authorize:

- any `ob_dev` source/test edit;
- version change or tool registration;
- install or dependency change;
- restart or connector refresh;
- PostgreSQL startup/control;
- credentials or secrets;
- database or role creation;
- SQL, DDL, migrations, or rollbacks;
- disposable lifecycle;
- hammers, backup, or restore;
- persistence, providers, capture, raw storage, customer/private data;
- recurring or production work;
- DB-5.

## Final assessment

The DB-4 package is coherent, exact, implementation-oriented, and bounded. It is
ready for final repository validation and then owner review. The project now has a
credible path from dormant scaffolding to a real disposable PostgreSQL proof without
silently creating a governed database.
