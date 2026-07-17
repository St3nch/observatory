# DB-4 R5 Repeat Compatibility Review Authorization

Status: accepted
Date: 2026-07-17
Owner ruling: server restarted and tools refreshed; continue
Authorized operation classes: repository_edit, repository_test, repository_commit

## Decision

Authorize one review-only package to repeat the frozen `ob-dev` compatibility review against committed implementation `879529c27cad666099cf4f697eb7cbb56dec2279` and refreshed server version `0.5.0`.

This decision may record whether blockers G1–G5 are closed and may advance the gate only to `ready_for_owner_execution_decision`.

It does not authorize PostgreSQL execution, database creation, role creation, migration or rollback application, profile execution, backup or restore, campaign finalization, DB-4 closure, DB-5, providers, customer/private data, recurring work, or production work.

## Exact paths

```text
planning-inbox/db4-r5-repeat-ob-dev-compatibility-review.md
planning-inbox/db4-live-disposable-campaign-owner-decision-draft.md
database/db4-remediation-conformance-manifest.json
ACTIVE_CONTEXT.md
NEXT_SESSION_HANDOFF.md
ROADMAP.md
POST_V1_DATABASE_ROADMAP.md
decisions/README.md
tests/test_database_package.py
tools/check_database_package.py
tools/check_authority_sync.py
```

## Required evidence

- refreshed `ob-dev` health reports version `0.5.0`, 63 tools, no generic execution, and PostgreSQL mutation disabled;
- all profile tools require `campaign_id`;
- campaign-register finalizer is present;
- committed `ob-dev` tests pass;
- committed Observatory tests and authority sync pass;
- both source trees are clean except the protected unrelated Observatory audit file;
- no PostgreSQL operation is invoked.

## Stop condition

Stop before any live operation. A separate owner-accepted execution decision with exact operation classes remains mandatory.
