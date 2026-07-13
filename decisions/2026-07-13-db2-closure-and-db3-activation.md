# Decision — DB-2 Closure and DB-3 Activation

Status: suspended by `decisions/2026-07-13-database-phase-recovery-to-db1.md`; retained as historical claimed acceptance
Date: 2026-07-13
Owner ruling: accepted verbatim in chat
Related milestone: DB-2 closure; DB-3 activation
Related files:

- `planning-inbox/db2-physical-data-contract-freeze-specification.md`
- `planning-inbox/db2-freeze-v0-1-1-classification-corrections.md`
- `planning-inbox/db2-closure-readiness-review.md`
- `POST_V1_DATABASE_ROADMAP.md`

---

## Decision

```text
ACCEPT DB-2 PHYSICAL DATA-CONTRACT FREEZE v0.1.1 CLASSIFICATION CORRECTIONS

CLOSE DB-2 — PHYSICAL DATA-CONTRACT FREEZE

ACTIVATE DB-3 — POSTGRES OPERATIONAL BOUNDARY AND PHYSICAL SCHEMA SPECIFICATION

AUTHORIZE SPECIFICATION WORK ONLY.
DO NOT AUTHORIZE DATABASE CREATION, ROLES, CREDENTIALS, DDL,
MIGRATION FILES, MIGRATION EXECUTION, DISPOSABLE DATABASES,
POSTGRES HAMMERS, SYNTHETIC OR REAL PERSISTENCE, PROVIDER CALLS,
CUSTOMER DATA, RAW CAPTURE, OR PRODUCTION.
```

## Effect

- DB-2 is closed.
- The v0.1.1 classification corrections are accepted and bind DB-3.
- DB-3 is active for specification work only.
- One concept must have one primary classification; qualifiers may refine behavior but may not widen authority.
- DB-3 may specify operational boundaries and physical schema design, but may not create or execute any database artifact.

## Scope

This decision applies to:

- PostgreSQL operational-boundary specification;
- physical schema specification;
- role and privilege specification;
- credential and secret-boundary specification;
- naming, identity, lifecycle, index, constraint, append-only, audit-first, raw-pointer, backup-before-migration, and migration-policy specification;
- mapping every physical mechanism to accepted hammers.

This decision does not authorize:

- PostgreSQL database creation;
- role or credential creation;
- SQL or DDL files;
- migration files or migration execution;
- disposable database lifecycle;
- real PostgreSQL hammer execution;
- synthetic or real persistence;
- provider calls, paid pulls, or ingestion;
- customer/private data;
- raw capture or artifact-store creation;
- production.

## Authority impact

```text
scope change: DB-2 closed; DB-3 specification-only work activated
doctrine change: no
implementation authority: no
database execution authority: no
```

## Follow-up work

| Follow-up | Target milestone | Status |
|---|---|---|
| Reconcile accepted v0.1.1 classifications into the canonical freeze | DB-3 entry | required |
| Specify PostgreSQL operational boundary | DB-3 | active |
| Specify physical schema without DDL | DB-3 | active |
| Prepare DB-3 closure review and DB-4 gate | DB-3 | pending |

## Anti-drift notes

- Specification is not implementation.
- A table design is not DDL authority.
- A role design is not role-creation authority.
- An available PostgreSQL tool is not permission to use it.
- DB-4 remains inactive until a separate owner decision.
