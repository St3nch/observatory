# Decision — DB-4 Remediation Implementation Authorization

Date: 2026-07-14
Status: accepted
Authority: owner ruling
Milestone: DB-4 remediation implementation

## Decision

The owner approves the exact DB-4 remediation implementation package committed at:

```text
4d37a4f1fec51843a568dab00763f2e05da11ca2
```

The following package artifacts are accepted as the bounded implementation authority:

```text
planning-inbox/db4-remediation-exact-implementation-manifest-v0-1.md
planning-inbox/db4-proof-security-and-operations-package-v0-1.md
planning-inbox/db4-one-restart-implementation-and-validation-plan-v0-1.md
planning-inbox/db4-remediation-implementation-package-readiness-review.md
```

This decision authorizes the bounded Observatory and ob-dev implementation work defined by those exact artifacts.

## Authorized work

Authorized implementation includes:

- replacement of the diagnostic DB-4 migration and rollback files with DB-3-faithful candidates;
- implementation of atomic, append-only, SHA-bound migration/history handling;
- implementation of deterministic schema fingerprinting;
- implementation of data-driven, exact-path, SHA-bound hammer profiles;
- implementation and redesign of broken candidates through the real migration admission path;
- implementation of behavioral role, RLS, append-only, audit-first, identity, concurrency, migration, rollback, and cleanup checks;
- implementation of immutable result-register, campaign, and supersession records;
- implementation of authority, marker, redaction, credential, role-lifecycle, and network-posture hardening;
- implementation of the exact Observatory and ob-dev source, profile, fixture, proof, validator, and test paths named by the package;
- static validation, unit tests, integration-test code, exact staging, commits, and manual owner pushes;
- one planned owner restart and connector refresh after the complete ob-dev implementation batch passes validation.

## Explicitly prohibited

This decision does not authorize:

- any PostgreSQL connection, migration execution, rollback execution, hammer execution, role mutation, database create/reset/drop, backup, restore, or cleanup operation;
- creation of the governed database named `observatory`;
- DB-5 planning, activation, implementation, or execution;
- provider integration, provider calls, paid pulls, capture, ingestion, or raw provider payload persistence;
- customer records, customer first-party analytics, or private data;
- recurring work, scheduling, autonomous spend, production, deployment, dashboards, or product API/MCP work;
- strategy, recommendation, conclusion, score-as-truth, report-state, prompt, or LLM-reasoning persistence;
- arbitrary shell, arbitrary SQL, caller-selected executable paths, weakened fixed roots, or weakened authority controls.

## Implementation sequence

The authorized sequence is:

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
```

I10 disposable PostgreSQL execution remains separately prohibited and requires a later exact owner decision.

## Stop conditions

Stop on any:

- path outside the exact accepted package;
- missing DB-3 traceability;
- migration/history split transaction;
- mutable migration history;
- caller-selected SQL or executable path;
- profile or SHA drift;
- superuser-only role/RLS proof design;
- result overwrite or incomplete failure record;
- marker or authority mismatch;
- secret exposure;
- unverified remote mutation exposure;
- avoidable restart churn beyond the one planned restart;
- PostgreSQL execution or any separately prohibited work.

## Milestone state

```text
DB-1 complete
DB-2 complete
DB-3 complete
DB-4 active for exact bounded remediation implementation
DB-5 inactive
PostgreSQL execution separately prohibited
```

No milestone implies the next milestone.
