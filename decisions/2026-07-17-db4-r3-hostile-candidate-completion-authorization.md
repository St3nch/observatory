# DB-4 R3 Hostile-Candidate Completion Authorization

Status: accepted owner decision
Date: 2026-07-17
Milestone: DB-4 — Database Hammer Harness and Migration Specification
Parent authority: `decisions/2026-07-16-db4-remediation-reconciliation-and-r0-authorization.md`
Completed predecessor: `decisions/2026-07-17-db4-r2-real-spine-behavioral-proof-authorization.md`
Completion plan: `audits/observatory-db4-drift-correction-and-completion-plan.md`

## Decision

The owner instruction to proceed authorizes Route C Batch R3 only.

R3 completes and redesigns the hostile-candidate fixture and manifest layer established by R0. It does not authorize a PostgreSQL campaign or imply that fixture presence is behavioral proof.

## Authorized work

R3 may:

1. redesign the eight diagnostic fixtures recorded by R0 so every fixture declares its violated invariant, rejection class, expected rejection point, expected SQLSTATE where PostgreSQL-native, residue relation, history expectation, and cleanup expectation;
2. create the eight fixtures recorded by R0 as required and absent;
3. classify each fixture as `postgresql_native` or `runner_detected`;
4. prefer PostgreSQL-native rejection whenever PostgreSQL can enforce the invariant directly;
5. update the machine-readable conformance manifest so all sixteen concrete fixtures are present and classified;
6. update SHA-bound rows for the original eight checks in `db4-broken-candidates.json`;
7. add static conformance checks and tests for fixture metadata, exact inventory, classification, and SHA binding;
8. synchronize current-state authority documents to R3.

## Frozen control-plane boundary

`ob-dev` remains frozen.

The current frozen executor recognizes the original eight broken-candidate check IDs. R3 may not alter that executor or claim that the eight new fixtures are runnable through it. New executor/check wiring is deferred to the documented R4/R5 compatibility review and requires a separate bounded decision if the frozen capability is insufficient.

This is an honest blocked capability statement, not permission to omit fixtures or mislabel file presence as execution proof.

## Required concrete fixtures

The completed concrete set is:

```text
009_dirty_constraint_seed.sql
009_excess_role_privilege.sql
009_missing_audit_pair.sql
009_missing_scope_boundary.sql
009_mutable_evidence.sql
009_partial_migration_failure.sql
009_schema_version_divergence.sql
009_unbounded_raw_locator.sql
009_search_path_hijack.sql
009_owner_bypass_rls.sql
009_rls_without_force.sql
009_missing_with_check.sql
009_default_privilege_leak.sql
009_public_schema_create.sql
009_not_valid_constraint.sql
009_cross_scope_foreign_key.sql
```

The seven obligations folded into behavioral profiles by R0 remain folded and are not recreated as duplicate fixture files.

## Required fixture metadata

Every concrete fixture must declare:

```text
fixture_id
violated_invariant
rejection_class
rejection_point
expected_sqlstate
residue_relation
history_expectation
cleanup_expectation
```

Allowed rejection classes:

```text
postgresql_native
runner_detected
```

`expected_sqlstate` must be a five-character PostgreSQL SQLSTATE for native rejection and `none` for runner-detected rejection.

## Prohibitions

R3 does not authorize:

- R4 stale profile/test retirement or creation of the six R4 PostgreSQL tests;
- arbitrary new fixture names outside the reconciled set;
- changes to `ob-dev`;
- PostgreSQL connections or execution;
- creating roles or databases;
- DB-5;
- providers, customer/private data, recurring work, or production work;
- claiming a fixture passed because its file exists or static validation is green.

## Exit conditions

R3 is complete only when:

1. all sixteen concrete fixture files exist;
2. every fixture has complete closed metadata;
3. every fixture is classified native versus runner-detected;
4. the original eight active profile rows are SHA-bound to their redesigned fixtures;
5. the conformance manifest records zero required-absent R3 fixtures;
6. static validators reject missing, unnamed, unclassified, malformed, or SHA-drifted fixtures;
7. Observatory and frozen `ob-dev` unit/static validation remain green;
8. no PostgreSQL execution has occurred.

R3 completion does not authorize R4. A later owner instruction is required.
