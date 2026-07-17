# DB-4 Post-Audit Evidence-Integrity Correction Authorization

Status: accepted
Date: 2026-07-17
Owner ruling: approved in chat after independent Claude audit
Authorized operation classes: repository_edit, repository_test, repository_commit

## Decision

Authorize one exact-path, cross-repository correction batch to close the blocking evidence-integrity defects identified by the independent audit before any live disposable PostgreSQL campaign is accepted or executed.

This decision does not authorize PostgreSQL execution, database or role creation, migration application, rollback, backup, restore, profile execution, campaign finalization, DB-4 closure, DB-5, providers, customer/private data, recurring work, or production work.

## Required corrections

1. Add a dedicated broken-candidate rejection exception and fail closed on non-detection, detector errors, malformed output, and unexpected exceptions.
2. Capture real observed SQLSTATE for PostgreSQL-native hostile fixtures; never copy expected SQLSTATE into observed evidence.
3. Derive dirty-tree and secret-review evidence from actual measurements; never hard-code pass claims.
4. Permit only current-campaign untracked append-only additions under `database/hammer-results/`; reject modified, staged, deleted, renamed, foreign-campaign, or arbitrary evidence paths.
5. Require non-empty campaign execution IDs and verify every ID resolves to an emitted result record with the same campaign; require coverage of declared profiles.
6. Add direct backup-role same-scope and cross-scope behavior against representative real protected base relations, including evidence and raw-token surfaces.
7. Strengthen semantic detectors for search-path hijack, unbounded raw locators, and missing `WITH CHECK`.
8. Add hostile tests proving non-detection, detector errors, modified evidence, fabricated execution IDs, empty execution IDs, and incomplete profile coverage fail closed.

## Exact Observatory paths

```text
decisions/2026-07-17-db4-post-audit-evidence-integrity-correction-authorization.md
decisions/README.md
planning-inbox/db4-live-disposable-campaign-owner-decision-draft.md
planning-inbox/db4-r5-repeat-ob-dev-compatibility-review.md
database/db4-remediation-conformance-manifest.json
database/hammer-profiles/db4-role-rls.json
database/proof/campaign-register.schema.json
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
```

## Exact ob-dev paths

```text
src/ob_dev/postgres_broken_candidates.py
src/ob_dev/postgres_operations.py
src/ob_dev/postgres_result_emission.py
src/ob_dev/postgres_result_register.py
src/ob_dev/postgres_campaign_register.py
src/ob_dev/postgres_redaction.py
src/ob_dev/server.py
tests/test_postgres_broken_candidates.py
tests/test_postgres_roles.py
tests/test_postgres_result_emission.py
tests/test_postgres_result_register.py
tests/test_postgres_campaign_register.py
tests/test_server.py
```

No other path is authorized without a new owner decision.

## Validation required before commit

```text
ob-dev full pytest
ob-dev Ruff
Observatory full pytest
Observatory authority sync
git diff --check in both repositories
exact changed-path review in both repositories
```

## Restart boundary

Do not restart the MCP server during implementation. After both repositories are committed and all validations are green, perform one normal server restart and tool refresh, then repeat an independent compatibility audit before owner consideration of the live campaign.

## Stop conditions

Stop on path expansion, PostgreSQL execution, fabricated evidence, copied expected values presented as observations, mutable prior evidence acceptance, unresolved campaign IDs, incomplete base-relation role proof, weakened authority or marker enforcement, protected-audit modification, or any work outside this exact correction package.
