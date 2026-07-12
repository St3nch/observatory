# Decision — Accept Post-v1 Audit and Activate Database-Phase Roadmap Planning

Status: accepted decision
Date: 2026-07-12
Owner authority: explicit owner ruling in project chat

## Decision

The owner accepted the following exact posture:

```text
ACCEPT THE AUDIT AS HIGH-QUALITY ADVISORY INPUT.
PRESERVE OBSERVATORY V1 ACCEPTANCE.
AUTHORIZE POST-V1 AUDIT RECONCILIATION AND DATABASE-PHASE ROADMAP PLANNING.
DO NOT YET AUTHORIZE POSTGRES CREATION, DDL, OR MIGRATION EXECUTION.
```

The accepted advisory audit is:

```text
audits/observatory-post-v1-pre-database-deep-audit-2026-07-12.md
```

Audit SHA-256 at acceptance:

```text
e334ec8d1b54ddb6b0f66145702b967bf88e85a55840cc64ec0d8b716504ded5
```

## Effect

Observatory v1 remains accepted at the bounded proof-system ceiling.

The audit does not overturn, supersede, or weaken:

- `decisions/2026-07-12-observatory-v1-acceptance.md`;
- the M20 known-limit and deferred-capability register;
- the no-production and no-post-v1-implementation boundary;
- the telescope/astronomer doctrine;
- customer-data, strategy, recommendation, provider-truth, and direct-SQL prohibitions.

This decision activates a new planning sequence beginning with:

```text
DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
```

## DB-1 authorized work

DB-1 may:

- preserve and index the audit;
- route every N-01 through N-14 finding and O-1 through O-8 opportunity;
- correct stale authority pointers and documentation-truth defects;
- draft and review narrow typed-read contract/prototype corrections identified by N-01, N-08, N-11, N-13, and N-14;
- draft owner rulings for OR-B1, OR-B2, OR-C2, and OR-C4;
- draft hammer-matrix v0.2 and per-hammer result-register requirements;
- draft the consolidated physical data-contract-freeze milestone;
- define the database-phase roadmap and its separate owner gates.

## Explicit non-authorizations

This decision does not authorize:

```text
Postgres installation or creation
database roles or credentials
physical DDL
migration files
migration execution
schema creation
provider execution or paid pulls
real evidence ingestion
customer or private data
recurring capture
production API or MCP
cloud deployment
automatic backup jobs
destructive cleanup
strategy or recommendation persistence
```

## Gate separation

The database phase must preserve separate gates for:

```text
physical planning
logical data-contract freeze
physical schema specification
migration specification
local database creation
migration execution
synthetic persistence
real evidence ingestion
database-backed typed reads
database recovery proof
operational acceptance
production authorization
```

No earlier gate implies a later one.

## Final rule

```text
The audit opens reconciliation and planning.
It does not open Postgres.
Observatory v1 remains accepted.
The database must earn authority one gate at a time.
```
