# Decision — DB-4 R1 Schema-Hole Correction Authorization

Date: 2026-07-16
Status: accepted
Authority: owner ruling
Milestone: DB-4 drift correction and completion, Batch R1

## Decision

The owner authorizes Batch R1 from the accepted Route C completion sequence established by:

```text
decisions/2026-07-16-db4-remediation-reconciliation-and-r0-authorization.md
audits/observatory-db4-drift-correction-and-completion-plan.md
```

R0 is complete at commit:

```text
28770849f9a36c6a8758e729ff292b8a78b5730d
```

DB-1 remains complete.
DB-2 remains complete.
DB-3 remains complete as physical-design authority.
DB-4 remains active and incomplete.
DB-5 remains inactive.
PostgreSQL execution remains prohibited.

## Authorized R1 corrections

R1 is limited to the three documented schema reconciliation items below.

### R1-A — Scope-derived child-table RLS

Add `ENABLE ROW LEVEL SECURITY`, `FORCE ROW LEVEL SECURITY`, and explicit scope-derived policies to these currently unprotected scope-derived relations:

```text
obs_evidence.observed_artifact_reference
obs_evidence.admission_transition
obs_evidence.observation_transition
obs_evidence.evidence_identity
obs_evidence.citation_handle
obs_raw.raw_payload_identity
obs_raw.opaque_artifact_token
obs_raw.raw_integrity_observation
```

Policies must derive scope through accepted project lineage to `obs_evidence.observation.scope_key` or `obs_capture.capture_package.scope_key`.

Policies must use explicit `USING` and `WITH CHECK` expressions where the role has write authority. No policy may use `USING (true)` or treat row existence as scope authorization.

The matching rollback must remove the new policies and disable RLS in dependency-safe order.

### R1-B — Narrow DB-4 cleanup escape

Replace the whole-row substring test in `obs_meta.reject_mutation()` with a bounded test-only exception that:

- remains available only for `DELETE`;
- requires the table owner;
- requires transaction-local `ob.db4_cleanup = authorized`;
- examines only an explicit allowlist of named identity/key columns;
- accepts only exact DB-4 probe/test key grammars;
- does not scan arbitrary row text;
- does not permit ordinary non-probe rows to masquerade as cleanup rows because another text field happens to contain `db4-`.

Normal `UPDATE` and `DELETE` remain denied.

### R1-C — Internal-key reconciliation

The DB-4 traceability matrix statement that every internal primary key must be UUID is superseded by this bounded physical-design clarification:

- stable domain identities use constrained, non-aliasing text keys where the accepted schema defines them;
- internal transition, assignment, audit, and history rows may use generated bigint surrogate keys;
- public/internal citation, evidence, observation, candidate, capture, scope, target, and raw identities remain separate namespaces with strict grammar;
- no identity may be polymorphic or reused across responsibilities;
- this clarification does not authorize mutable natural keys, customer identifiers, external locators, or unconstrained text identifiers.

The implemented constrained text-key design is accepted; a UUID conversion is not required for DB-4.

## Exact authorized paths

```text
decisions/2026-07-16-db4-r1-schema-hole-correction-authorization.md
planning-inbox/db4-db3-implementation-traceability-matrix.md
database/migrations/001_identity_namespaces.sql
database/migrations/007_scope_rls_roles.sql
database/rollbacks/007_scope_rls_roles.sql
tools/check_database_package.py
tests/test_database_package.py
ACTIVE_CONTEXT.md
ROADMAP.md
POST_V1_DATABASE_ROADMAP.md
NEXT_SESSION_HANDOFF.md
decisions/README.md
```

No other path is authorized by R1 without a revised decision.

## Explicitly prohibited

R1 does not authorize:

- migration 010 surrogate-probe removal or behavioral rewiring;
- active profile changes;
- hostile fixture creation or redesign;
- stale profile/test deletion;
- `ob-dev` changes;
- PostgreSQL connection or execution;
- DB-5, governed database, providers, ingestion, customer/private data, recurring work, production, or strategy persistence.

## Validation requirements

R1 must add static checks proving:

- each named child relation has both enabled and forced RLS;
- each named relation has an explicit scope-derived policy;
- writable child policies include `WITH CHECK`;
- the cleanup trigger no longer scans `to_jsonb(OLD)::text` or uses `LIKE '%db4-%'`;
- the traceability matrix contains the accepted text-key/bigint-key ruling;
- existing package and authority checks remain green.

Static validation does not prove runtime PostgreSQL behavior and may not be described as a hammer pass.

## R1 exit criteria

R1 closes only when:

- all three authorized corrections are committed;
- rollback coverage matches the added RLS objects;
- authority and package validation pass;
- the full Observatory test suite passes;
- no R2, R3, R4, R5, `ob-dev`, or PostgreSQL work occurred.

No batch implies the next batch.
