# Decision — DB-4 Remediation Reconciliation and R0 Authorization

Date: 2026-07-16
Status: accepted
Authority: owner ruling
Milestone: DB-4 drift correction and completion, Batch R0

## Decision

The owner accepts Route C from:

```text
audits/observatory-db4-drift-correction-and-completion-plan.md
```

as the governing completion strategy for DB-4.

The audit plan remains advisory evidence. This decision promotes only the bounded rulings and R0 work stated below into authority.

DB-1 remains trusted and complete.
DB-2 remains trusted, accepted, and complete.
DB-3 remains trusted, accepted, and complete as the physical-design authority.
DB-4 remains active and incomplete.
DB-5 remains inactive.
PostgreSQL execution remains separately prohibited.

## Reconciled baseline

The implementation at commit `da15bd529ae7b6304bc5c7d473e3b769590df1e6` substantially completed the DB-3-faithful physical candidate rebuild and the current data-driven profile/proof-schema package.

It did not complete the accepted hostile-candidate and PostgreSQL test manifests:

```text
hostile candidates delivered: 8 of 23
hostile candidates named but absent: 15
PostgreSQL tests delivered: 5 of 11
current delivered tests that are stale pre-remediation relics: 5
planned PostgreSQL tests absent: 6
current active profiles: 8
retired-profile candidates still present: 5
```

The delivered rollback paths use `database/rollbacks/<version>_<name>.sql`, while the earlier implementation manifest named `.down.sql` paths. The delivered `.sql` naming is accepted for DB-4 completion. This is a path reconciliation, not permission to create duplicate rollback families.

The surrogate `obs_meta.db4_*` proof tables and functions in migration 010 violate the accepted behavioral-remapping rule that no control-plane probe table may substitute for project relations. They remain diagnostic implementation evidence pending Batch R2 and may not earn behavioral closure credit.

## Route ruling

Route A, blind conformity to every old manifest filename, is rejected.

Route B, amending the manifest downward to ratify what happened to be built, is rejected.

Route C is accepted:

1. establish one honest, machine-readable conformance manifest;
2. record every present, absent, stale, folded, deferred, and required artifact explicitly;
3. fix schema defects before writing proof against them;
4. move mandatory behavioral proof onto real project relations;
5. complete the required hostile-candidate and test set;
6. prepare a separately owner-gated disposable campaign;
7. close DB-4 only on accepted live evidence.

## Missing hostile-candidate disposition

The fifteen named-but-absent candidates are dispositioned from the accepted DB-3 responsibilities and hammer meanings as follows.

### Required SQL hostile candidates for Batch R3

```text
database/hammer-fixtures/009_search_path_hijack.sql
database/hammer-fixtures/009_owner_bypass_rls.sql
database/hammer-fixtures/009_rls_without_force.sql
database/hammer-fixtures/009_missing_with_check.sql
database/hammer-fixtures/009_default_privilege_leak.sql
database/hammer-fixtures/009_public_schema_create.sql
database/hammer-fixtures/009_not_valid_constraint.sql
database/hammer-fixtures/009_cross_scope_foreign_key.sql
```

These remain standalone candidates because they challenge migration/schema admission or security posture that must be inspected as a candidate package.

### Fold into real behavioral or sabotage checks

```text
009_history_rewrite.sql
009_duplicate_version_changed_sha.sql
009_history_without_schema.sql
009_schema_without_history.sql
009_disable_trigger_attempt.sql
009_duplicate_evidence_mint.sql
009_concurrent_migration_without_lock.sql
```

These are stronger when executed against the real migration history, append-only relation, evidence identity, or migration serialization path. They must be represented in the active behavioral profile/manifest with exact expected outcomes and may not disappear merely because no loose SQL fixture is created.

### Explicit deferrals

```text
none
```

No named hostile obligation is silently dropped.

## Existing hostile-candidate disposition

The eight current candidates remain present but diagnostic. Batch R3 must classify and redesign each as PostgreSQL-native rejection or bounded runner-detected rejection, with invariant, rejection point, expected SQLSTATE/outcome, history state, residue state, and cleanup verification.

## Test and profile disposition

The following five profile files are stale pre-remediation artifacts and must be retired in Batch R4:

```text
database/hammer-profiles/db4_invariants_v1.json
database/hammer-profiles/db4_migration_v1.json
database/hammer-profiles/db4_roles_v1.json
database/hammer-profiles/db4_concurrency_v1.json
database/hammer-profiles/db4_restore_verification_v1.json
```

The five current `tests/postgres/test_db4_*.py` files that load those profiles are stale tests and must be rewritten or removed in Batch R4.

The following six tests remain required for Batch R4:

```text
tests/postgres/test_db4_history_atomicity.py
tests/postgres/test_db4_profile_manifest.py
tests/postgres/test_db4_broken_candidate_manifest.py
tests/postgres/test_db4_result_register.py
tests/postgres/test_db4_cleanup.py
tests/postgres/test_db4_security_posture.py
```

## Machine-readable conformance authority

The accepted current conformance manifest is:

```text
database/db4-remediation-conformance-manifest.json
```

The database package validator must:

- reject any unnamed migration, rollback, fixture, profile, proof path, or PostgreSQL test;
- reject a named artifact whose declared current-state expectation does not match reality;
- permit an absent artifact only when its manifest status explicitly says it is expected absent until a named future batch or is folded into a named behavioral obligation;
- retain stale artifacts only when explicitly marked for a named retirement batch;
- prevent duplicate rollback naming families;
- ensure all fifteen missing hostile obligations have a non-silent disposition;
- ensure all eleven planned PostgreSQL test obligations have a non-silent disposition.

## Authorized Batch R0 work

Authorized now:

- commit this decision;
- commit the advisory completion plan under `audits/`;
- add the machine-readable conformance manifest;
- extend `tools/check_database_package.py` and `tests/test_database_package.py` to enforce it;
- update current-state, roadmap, handoff, decision index, audit index, and related folder indexes so the R0 authority is discoverable;
- run repository validation, exact-stage, and commit the bounded R0 package;
- manual owner push.

## Explicitly not authorized by R0

- SQL migration or rollback changes;
- role, grant, RLS, trigger, view, function, or schema changes;
- deletion or rewriting of stale profiles/tests before Batch R4;
- creation of missing hostile candidates before Batch R3;
- behavioral-probe rewiring before Batch R2;
- any `ob-dev` change;
- PostgreSQL connection or execution;
- DB-5, governed database, provider, ingestion, customer/private data, recurring work, production, or strategy persistence.

## Completion sequence

```text
R0 reconciliation and honest baseline
R1 schema-hole correction
R2 real-spine behavioral proof
R3 hostile-candidate completion and redesign
R4 test/profile completion and retirement
R5 live-campaign gate preparation
separate owner execution decision
one disposable campaign
independent closure audit
```

No batch implies the next batch.

## R0 exit criteria

R0 closes only when:

- the decision and advisory plan are tracked;
- the conformance manifest exactly describes current reality and all future obligations;
- the validator rejects unnamed or silently missing artifacts;
- all current-state authority files point to this decision and Route C sequence;
- validation passes without pretending missing future artifacts already exist;
- no SQL, `ob-dev`, or PostgreSQL execution occurred.

## Final boundary

The Observatory stores observations, not conclusions.

A green suite may not substitute for a real hostile proof, and a manifest may not claim completeness that the repository has not earned.
