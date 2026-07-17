# DB-4 G1–G5 ob-dev Compatibility Correction Authorization

Status: accepted
Date: 2026-07-17
Owner ruling: continue after successful R5 push
Authorized operation classes: repository_edit, repository_test, repository_commit

## Decision

Authorize one exact-path compatibility-correction batch to close R5 blockers G1–G5 before any disposable PostgreSQL execution.

This decision authorizes source, profile, schema-contract, and test changes only. It does not authorize PostgreSQL execution, connector restart, live-campaign acceptance, DB-4 closure, DB-5, providers, governed database creation, customer/private data, recurring work, or production work.

## Required outcomes

- G1: every live profile, broken-candidate, backup, restore, and result-emission path verifies the existing disposable marker and binds evidence to that verified identity.
- G2: every live mutation/proof path loads an accepted authority file and requires its exact operation class.
- G3: all sixteen concrete hostile fixtures are represented in the SHA-bound broken-candidate profile and executable through bounded native or semantic rejection logic with zero history and residue.
- G4: backup-role same-scope and cross-scope behavior is directly exercised and recorded under `SET LOCAL ROLE`.
- G5: one owner-selected campaign ID is supplied across profile tools; clean-tree preconditions are enforced; one append-only campaign register binds emitted execution IDs; failed/blocked records remain preserved.

## Exact Observatory paths

```text
database/hammer-profiles/db4-broken-candidates.json
database/hammer-profiles/db4-role-rls.json
database/proof/campaign-register.schema.json
database/db4-remediation-conformance-manifest.json
tests/postgres/test_db4_broken_candidate_manifest.py
tests/postgres/test_db4_profile_manifest.py
tests/postgres/test_db4_result_register.py
tests/postgres/test_db4_security_posture.py
tests/test_database_package.py
tools/check_database_package.py
tools/check_authority_sync.py
ACTIVE_CONTEXT.md
NEXT_SESSION_HANDOFF.md
ROADMAP.md
POST_V1_DATABASE_ROADMAP.md
decisions/README.md
```

## Exact ob-dev paths

```text
src/ob_dev/postgres_authority.py
src/ob_dev/postgres_control.py
src/ob_dev/postgres_hammers.py
src/ob_dev/postgres_broken_candidates.py
src/ob_dev/postgres_operations.py
src/ob_dev/postgres_backup.py
src/ob_dev/postgres_result_emission.py
src/ob_dev/postgres_result_register.py
src/ob_dev/postgres_campaign_register.py
src/ob_dev/server.py
tests/test_postgres_authority.py
tests/test_postgres_control.py
tests/test_postgres_hammers.py
tests/test_postgres_broken_candidates.py
tests/test_postgres_roles.py
tests/test_postgres_backup.py
tests/test_postgres_result_emission.py
tests/test_postgres_result_register.py
tests/test_postgres_campaign_register.py
tests/test_server.py
```

No other path is authorized without a new owner decision.

## Validation

Required before commit:

```text
Observatory full pytest
Observatory authority sync
ob-dev full pytest
ob-dev Ruff
git diff --check in both repositories
exact changed-path review in both repositories
```

## Restart boundary

No connector/server restart occurs during implementation. One restart and tool refresh may occur only after both repositories are committed and all pre-restart validation is green.

## Stop conditions

Stop on path expansion, arbitrary SQL, caller-selected executable paths, missing SHA binding, missing marker verification, merely syntactic authority validation, mutable result/campaign records, incomplete failed-result preservation, dirty-tree acceptance, PostgreSQL execution, or any work outside DB-4 compatibility correction.
