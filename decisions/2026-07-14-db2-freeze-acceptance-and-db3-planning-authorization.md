# Decision — DB-2 Freeze Acceptance and DB-3 Planning Authorization

Status: accepted decision
Date: 2026-07-14
Owner authority: three explicit owner decisions recorded in project conversation
Related milestone: DB-2 closure / fresh DB-3 planning activation

## Decision

The owner answered the three independent DB-2 owner-gate questions affirmatively.

### OR-H1 — accept the exact DB-2 freeze

The owner accepts these exact immutable bytes as the sole normative DB-2 input to
fresh DB-3 planning:

```text
path: planning-inbox/db2-physical-data-contract-freeze-specification.md
version: 0.2.1
sha256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
```

The artifact's historical candidate self-description remains part of the accepted
bytes. Authority comes from this decision's exact path/version/hash binding; the
accepted artifact must not be edited in place.

### OR-H2 — close DB-2

DB-2 — Physical Data-Contract Freeze is closed successfully. DB-2 is trusted, accepted, complete, and is now the last trusted completed database milestone. DB-1 remains trusted and complete.

### OR-H3 — authorize fresh DB-3 planning

The owner activates the canonical milestone:

```text
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

DB-3 authority is planning and specification only. Fresh DB-3 work must derive
solely from accepted DB-1 authority, the exact accepted DB-2 freeze bound above,
accepted roadmaps/contracts/decisions, and this decision.

## Allowed DB-3 planning work

DB-3 may prepare only:

- specifications;
- diagrams;
- constraint matrices;
- migration plans;
- rollback plans;
- operational-boundary decisions;
- physical-schema specifications derived from the accepted DB-2 freeze;
- the exact future `ob-dev` database control-plane contract.

These are planning outputs. They are not executable implementation artifacts and
do not create authority by their existence.

## Permanently retired artifacts

The following five untrusted DB-3/DB-4 artifacts remain permanently retired and
deleted from the active repository:

```text
decisions/2026-07-13-db2-closure-and-db3-activation.md
decisions/2026-07-13-db3-closure-and-db4-activation.md
planning-inbox/db3-postgres-operational-boundary-specification.md
planning-inbox/db3-physical-schema-specification.md
planning-inbox/db3-specification-readiness-review.md
```

They must not be restored, salvaged, reused, copied, paraphrased, reconstructed
from memory, or treated as planning input. Fresh DB-3 work starts only from the
accepted authority named in this decision.

## DB-4 and implementation boundary

DB-4 remains inactive. No DB-4 artifact is authorized. A separate future owner
gate is required before DB-4 or any implementation activity.

This decision does not authorize:

```text
PostgreSQL creation or startup
database creation
roles
credentials or credential handling
executable DDL
executable migration files
SQL execution
migration execution
physical-schema implementation
database tooling implementation or activation
dormant PostgreSQL MCP tool registration
ingestion
providers
capture
persistence
customer or private data
raw storage
recurring work
production
DB-4
```

## Authority impact

```text
scope change: yes — explicit owner decision
doctrine change: no
implementation authority: no
database authority: no
```

## Final rule

```text
DB-2 freezes the accepted logical contract.
DB-3 may specify how a future database would preserve it.
Nothing in this decision authorizes the database to exist or execute.
```
