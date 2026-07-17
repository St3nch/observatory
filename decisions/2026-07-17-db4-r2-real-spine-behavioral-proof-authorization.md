# Decision — DB-4 R2 Real-Spine Behavioral Proof Authorization

Date: 2026-07-17
Status: accepted
Authority: owner ruling expressed by “proceed” after R1 was committed and synchronized
Milestone: DB-4 drift correction and completion, Batch R2

## Decision

Batch R1 is complete at:

```text
b27973b0604799588c046d2d26198fc1a9b47bda
```

The owner authorizes Batch R2 only, following:

```text
audits/observatory-db4-drift-correction-and-completion-plan.md
```

R2 must move the accepted behavioral proof from surrogate relations onto the real Observatory evidence spine without changing doctrine or widening capability.

DB-1 remains complete.
DB-2 remains complete.
DB-3 remains complete and is the physical-design authority.
DB-4 remains active and incomplete.
DB-5 remains inactive.
PostgreSQL execution remains separately prohibited.

## Authorized R2 corrections

### Real admission-gate proof

Rewrite the fixed SQL functions called by the active behavioral profile so that:

- missing rights attempts a real `obs_evidence.observation` insert;
- missing retention attempts a real `obs_evidence.observation` insert;
- the real `obs_evidence.enforce_accepted_admission()` trigger rejects the mismatch with SQLSTATE `23514`;
- the failed attempt leaves no observation or evidence identity;
- the trigger uses null-safe comparison so NULL cannot bypass the binding check.

### Real evidence-identity proof

Rewrite duplicate-evidence proof so it attempts a second `obs_evidence.evidence_identity` for an already admitted real observation and receives SQLSTATE `23505` from the real uniqueness boundary.

### Real append-only proof

Rewrite append-only proof so it attempts UPDATE and DELETE against a seeded real `obs_evidence.observation`, receives SQLSTATE `42501`, and verifies the original row remains unchanged.

### Real concurrent mint proof

Rewrite the forced-overlap identity worker so both workers attempt the same real `obs_evidence.evidence_identity` for one admitted observation. Exactly one worker may commit and the other must receive the accepted uniqueness/serialization rejection. The existing advisory-lock migration-serialization probe remains in place.

### Surrogate removal

Remove the persistent surrogate relations that currently stand in for project relations:

```text
obs_meta.db4_admission_probe
obs_meta.db4_evidence_probe
obs_meta.db4_concurrent_identity_probe
```

Remove all SQL paths and cleanup logic that depend on them.

The following migration-specific control-plane probes may remain during R2 because they exercise migration atomicity/serialization rather than substituting for an Observatory evidence relation:

```text
obs_meta.db4_migration_probe_effect
obs_meta.db4_migration_probe_history
obs_meta.db4_concurrent_migration_effect
obs_meta.db4_concurrent_migration_history
```

Their later disposition remains governed by the migration-history and hostile-candidate batches.

## Frozen ob-dev compatibility

`ob-dev` remains unchanged.

R2 may preserve the fixed callable function names already used by the frozen operation registry while replacing their SQL bodies and substrate. Preserving a fixed callable name is not preserving a surrogate proof if the implementation now acts on real project relations.

## Authorized paths

R2 may modify only the exact paths required for:

- this decision and authority synchronization;
- `database/migrations/004_evidence_identity.sql`;
- `database/migrations/010_recovery_verification.sql`;
- matching rollback files when object inventory changes;
- active profile JSON files for expected outcomes/SQLSTATEs;
- the conformance/package validator and its unit tests;
- current-state, roadmap, handoff, and decision indexes.

## Not authorized

R2 does not authorize:

- new or redesigned `009_*` hostile fixtures;
- deletion of stale profiles or stale PostgreSQL tests;
- creation of the six R4 tests;
- `ob-dev` edits or restart;
- PostgreSQL connection or execution;
- live proof claims;
- DB-5, governed database creation, providers, customer/private data, recurring work, production, or strategy persistence.

## R2 exit criteria

R2 is complete only when:

- the three project-relation surrogate tables are absent;
- H2 and H3 use real observation admission and record expected `23514`;
- duplicate evidence proof uses real `obs_evidence.evidence_identity` and records expected `23505`;
- append-only proof mutates a real protected relation and records expected `42501`;
- concurrent identity proof races a real evidence mint with actual overlap;
- cleanup removes all R2 seed and result residue through the bounded DB-4 cleanup path;
- active profile definitions name the real relation and expected SQLSTATE/outcome;
- static validation passes;
- no PostgreSQL or `ob-dev` execution occurred.

No R2 static result closes DB-4 or earns a live proof class.
