# DB-4 Post-Audit SQLSTATE Path Amendment

Status: accepted
Date: 2026-07-17
Owner basis: approved correction package requiring real observed SQLSTATE capture
Authorized operation classes: repository_edit, repository_test, repository_commit

## Decision

Amend `decisions/2026-07-17-db4-post-audit-evidence-integrity-correction-authorization.md` only to add the exact `ob-dev` session paths required to expose and test structured PostgreSQL SQLSTATE evidence.

Additional authorized paths:

```text
src/ob_dev/postgres_psql_session.py
tests/test_postgres_psql_session.py
```

No other scope changes. PostgreSQL execution and all previously prohibited work remain prohibited.
