# Decision — DB-3 Closure and DB-4 Activation

Status: accepted
Date: 2026-07-13
Owner ruling: accepted verbatim in chat
Related milestone: DB-3 closure; DB-4 activation
Related files:

- `planning-inbox/db3-postgres-operational-boundary-specification.md`
- `planning-inbox/db3-physical-schema-specification.md`
- `planning-inbox/db3-specification-readiness-review.md`
- `POST_V1_DATABASE_ROADMAP.md`

---

## Decision

```text
ACCEPT DB-3 POSTGRES OPERATIONAL BOUNDARY SPECIFICATION v0.1
ACCEPT DB-3 PHYSICAL SCHEMA SPECIFICATION v0.1

CLOSE DB-3 — POSTGRES OPERATIONAL BOUNDARY AND PHYSICAL SCHEMA SPECIFICATION

ACTIVATE DB-4 — DATABASE HAMMER HARNESS AND MIGRATION SPECIFICATION

AUTHORIZE THE COHERENT ob-dev DATABASE-CONTROL-PLANE IMPLEMENTATION,
MIGRATION/ROLLBACK SPECIFICATION FILES, AND DISPOSABLE REAL-POSTGRES
HARNESS/PROOF ONLY.

DO NOT AUTHORIZE THE GOVERNED OBSERVATORY DATABASE, GOVERNED ROLES OR
CREDENTIALS, GOVERNED MIGRATION EXECUTION, SYNTHETIC OR REAL GOVERNED
PERSISTENCE, PROVIDER CALLS, CUSTOMER DATA, RAW CAPTURE, OR PRODUCTION.
```

## Effect

- DB-3 is closed.
- The PostgreSQL operational-boundary specification v0.1 is accepted.
- The physical schema specification v0.1 is accepted.
- DB-4 is active.
- DB-4 may implement the coherent ob-dev database-control-plane expansion.
- DB-4 may create migration and rollback specification files and operate only against protected disposable PostgreSQL databases for harness proof.
- Governed Observatory database creation and governed persistence remain unauthorized.

## Scope

This decision authorizes only:

- coherent ob-dev database-control-plane implementation;
- owner-controlled restart and connector refresh after the coherent batch;
- migration and rollback specification files;
- disposable database lifecycle under protected naming and capability controls;
- exact-path, expected-SHA migration validation and disposable execution;
- allowlisted real-PostgreSQL hammer profiles;
- structured per-hammer proof records.

This decision does not authorize:

- creation of the governed Observatory database;
- governed roles or credentials;
- governed migration execution;
- synthetic or real governed persistence;
- provider calls, paid pulls, or ingestion;
- customer or private data;
- raw capture or artifact-store creation;
- production.

## Authority impact

```text
scope change: DB-3 closed; DB-4 disposable proof work activated
doctrine change: no
governed database authority: no
production authority: no
```

## Follow-up work

| Follow-up | Target milestone | Status |
|---|---|---|
| Implement coherent ob-dev database-control-plane batch | DB-4 | active |
| Create migration/rollback specification files | DB-4 | active |
| Prove disposable database lifecycle and real-Postgres hammers | DB-4 | active |
| Prepare DB-4 closure review and DB-5 owner gate | DB-4 | pending |

## Anti-drift notes

- Disposable proof is not governed bootstrap.
- Tool existence is not governed database authority.
- A successful disposable migration is not permission to run it against a governed database.
- DB-5 remains inactive until a separate owner decision.
