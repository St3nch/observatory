# Decision — DB-1 Closure and DB-2 Activation

Status: accepted
Date: 2026-07-13
Owner ruling: explicit owner acceptance in project conversation
Related milestone: DB-1 closure / DB-2 activation
Related files:

- `hammers/hammer-matrix-v0-2.md`
- `hammers/acceptance-gate-policy-v0-2.md`
- `hammers/per-hammer-result-register-v0-1.md`
- `planning-inbox/db2-physical-data-contract-freeze-specification.md`
- `planning-inbox/db1-closure-readiness-review.md`
- `POST_V1_DATABASE_ROADMAP.md`

---

## Decision

The owner accepted the following exact gate:

```text
ACCEPT HAMMER MATRIX v0.2
ACCEPT ACCEPTANCE GATE POLICY v0.2
ACCEPT PER-HAMMER RESULT REGISTER CONTRACT v0.1
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE SPECIFICATION

CLOSE DB-1 — POST-v1 AUDIT RECONCILIATION AND RULING CLOSURE

ACTIVATE DB-2 — PHYSICAL DATA-CONTRACT FREEZE
```

DB-1 is closed. DB-2 is active.

## Accepted artifacts

| Artifact | Accepted role |
|---|---|
| `hammers/hammer-matrix-v0-2.md` | Current database-phase hammer mapping |
| `hammers/acceptance-gate-policy-v0-2.md` | Current database-phase acceptance policy |
| `hammers/per-hammer-result-register-v0-1.md` | Current per-execution hammer proof-record contract |
| `planning-inbox/db2-physical-data-contract-freeze-specification.md` | Normative logical data-contract freeze input for DB-2 |

## Scope

This decision authorizes DB-2 logical-contract work only:

- reconcile and finalize the accepted logical data contract;
- preserve concept classifications, identity ownership, lifecycle, provenance, scope, rights, retention, write authority, read exposure, and hammer implications;
- maintain the forbidden-persistence register;
- prepare DB-2 closure review and the separate DB-3 planning gate.

## Non-authorizations

This decision does not authorize:

```text
PostgreSQL database creation
roles or credentials
physical schema or DDL
migration files or execution
disposable database lifecycle
real PostgreSQL hammer execution
ob-dev database capability activation
synthetic or real persistence
provider calls or ingestion
customer/private data
production API/MCP
strategy, recommendation, or conclusion persistence
```

DB-3 remains inactive. Physical schema specification does not begin until DB-2 closes through a separate owner decision.

## Authority impact

```text
scope change
```

The owner explicitly closed DB-1 and activated DB-2.

## Follow-up work

| Follow-up | Target milestone | Status |
|---|---|---|
| Reconcile active context, roadmap, handoff, and indexes | DB-2 entry | required now |
| Review the accepted freeze for unresolved classifications or contradictions | DB-2 | active |
| Prepare DB-2 closure-readiness review and exact DB-3 planning gate | DB-2 | pending |

## Anti-drift notes

- Acceptance of a logical freeze is not physical schema approval.
- DB-2 activation is not DB-3 activation.
- Tool availability, credentials, or a running PostgreSQL service do not grant authority.
- No database hammer has run or passed.
- No provider or evidence ingestion authority exists.
