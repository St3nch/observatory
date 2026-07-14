# Decision — DB-4 Package Acceptance and Phased Implementation Authorization

Status: accepted decision
Date: 2026-07-14
Owner authority: explicit owner acceptance and implementation authorization recorded in project conversation
Related milestone: DB-4 implementation

## Decision

The owner made three independent affirmative decisions.

### OR-J1 — accept the exact DB-4 planning package

The owner accepts the exact DB-4 planning package committed at:

```text
commit: 90e6cecec19a8ed3e4bd241b37ff575b55a826b1
subject: Prepare exact DB-4 implementation package
```

Accepted immutable planning artifacts:

```text
path: planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md
version: 0.1
sha256: a65919ace9da12c16b7dcc3aa7b8262c1150f2acbc2dc521c91ca7c2ee055a2a

path: planning-inbox/db4-exact-ob-dev-implementation-package-specification.md
version: 0.1
sha256: b44711fe80a1967ddf3d5413ce150fcc5d56ca7f61ddb5d8f42747c63d9ce14a

path: planning-inbox/db4-migration-harness-and-proof-package-specification.md
version: 0.1
sha256: 9aff671e31fe94dabe5acca6a6631b14f8197a7c85ad55115caced354c7dad2e

path: planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md
version: 0.1
sha256: 8c08648051a2b88c58d5999f861596c79e8a479f68f02e6061586111edb86b7f

path: planning-inbox/db4-owner-readiness-review.md
version: 0.1
sha256: 1a2cfd0ff9f30be9ca793fc386a218deb3710860cd83f36ae294a354fd431c92
```

These planning artifacts remain immutable. Implementation must conform to their exact manifests, controls, sequencing, and stop conditions.

### OR-J2 — authorize the exact phased DB-4 implementation

The owner authorizes the complete package-defined phased DB-4 implementation, limited to:

1. the exact 17-path `ob_dev` source/test implementation manifest;
2. version `0.5.0` and the exact 28 PostgreSQL tools, producing the expected 60-tool registry;
3. the exact 46-path Observatory migration, rollback, fixture, profile, validator, and test manifest;
4. owner-controlled credential setup using the accepted custody and redaction rules;
5. owner-controlled PostgreSQL service actions, `ob_dev` restart, and connector refresh only when required by the runbook;
6. one disposable PostgreSQL proof substrate using the `observatory_test_` prefix, accepted marker, protected-name rejection, authority binding, identity binding, confirmation digest, and fail-closed cleanup controls;
7. exact-path and expected-SHA migration validation, forward execution, failure injection, rollback execution, and cleanup;
8. the package-defined migration, role, concurrency, hammer, backup, restore, and proof profiles;
9. real disposable PostgreSQL proof only, with proof classes reported honestly and no fixture proof inflation;
10. separate commits for `ob_dev` and Observatory implementation, exact staged manifests, complete validation, and manual owner push.

Implementation must proceed in the package-defined phases and stop immediately on any failed gate, extra path, unexpected tool, authority mismatch, identity mismatch, secret exposure, protected-name attempt, marker mismatch, SHA mismatch, cleanup failure, or proof inconsistency.

### OR-J3 — preserve the DB-5 and governed-database boundary

DB-4 remains the active milestone during implementation and proof. DB-4 is not closed by this decision.

DB-5 remains inactive. The governed database name `observatory`, governed roles, governed migrations, governed evidence persistence, and any production-like substrate remain prohibited.

Completion of disposable DB-4 proof may support a later DB-4 closure proposal. It does not activate DB-5 automatically.

## Required owner actions

The following remain owner-executed actions under the accepted runbook and are authorized only as required for this exact DB-4 package:

- create or supply local PostgreSQL credentials without placing secrets in Git, chat, tool arguments, tool results, logs, fixtures, or proof artifacts;
- start, stop, or restart the local PostgreSQL service when the implementation sequence requires it;
- restart `ob_dev` and refresh the ChatGPT connector after the implementation commit and before live tool proof;
- perform manual Git pushes after reviewed local commits.

The steward may prepare exact commands and verify resulting non-secret evidence. The steward must not invent, retain, echo, or expose credentials.

## Explicit continuing prohibitions

This decision does not authorize:

```text
the governed database named observatory
governed or production roles
governed migration execution
production deployment or production-like operation
real evidence persistence
synthetic evidence persistence outside the exact disposable hammer fixtures
provider integration or provider calls
paid pulls
ingestion or capture
raw provider payload storage
customer records or customer first-party data
private data
recurring capture or recurring work
autonomous spend
public API/MCP exposure
dashboards
strategy, recommendation, conclusion, score-as-truth, or report-state persistence
DB-5 planning, activation, implementation, or execution
any path, tool, dependency, database name, profile, or capability not named by the accepted package
```

## Validation and commit rules

Each implementation repository must independently satisfy its exact package gates:

- exact changed-path manifest;
- complete diff review;
- fixed test profiles;
- Ruff where specified;
- package import checks;
- authority sync for Observatory authority changes;
- text-integrity scans;
- secret-sentinel and redaction checks;
- `git diff --check`;
- exact staging manifest;
- manifest-locked commit;
- manual push only.

A failed phase does not authorize improvisation. Correct within the accepted manifest or stop for a new owner ruling.

## Authority impact

```text
scope change: yes — explicit owner decision
DB-4 planning package acceptance: yes
DB-4 implementation authority: yes — exact phased package only
PostgreSQL service owner actions: yes — exact package only
disposable PostgreSQL database authority: yes — exact package only
migration and rollback execution: yes — disposable exact-package proof only
real disposable hammers: yes — exact package only
backup and restore proof: yes — exact package only
DB-4 closure: no
DB-5 authority: no
governed database authority: no
production authority: no
provider or capture authority: no
customer/private-data authority: no
recurring-work authority: no
```

## Final rule

```text
Implement and hammer the exact disposable DB-4 package.
Do not create the governed Observatory database.
A passing disposable proof earns evidence for the next gate, not the next gate itself.
```
