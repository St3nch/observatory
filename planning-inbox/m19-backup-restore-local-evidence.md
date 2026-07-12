# M19 Backup and Restore Local Evidence — Pending Owner Execution

Status: authorized; not yet executed
Date: 2026-07-12
Authority: `decisions/2026-07-12-m19-bounded-backup-restore-proof-authorization.md`
Runbook: `planning-inbox/m19-backup-restore-owner-local-runbook.md`

No archive, restore, integrity, or functional pass is claimed yet.

Expected strongest result under current authorization:

```text
passed_repository_archive_and_restore_proof
encryption_status: blocked_pending_owner_tool_and_key_path
```

The proof must run from the clean, synced source repository and preserve all local work/restore artifacts afterward because cleanup is not authorized.

Required evidence to record after execution:

- source branch and exact HEAD;
- upstream sync result;
- bundle verification;
- bundle SHA-256 and byte count;
- restored exact HEAD;
- clean restored working tree;
- `git fsck --full` result;
- absence of prohibited ignored roots;
- full unit-test count, duration, and result;
- encryption readiness status;
- artifact-preservation/cleanup status;
- limitations.
