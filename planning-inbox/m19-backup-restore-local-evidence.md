# M19 Backup and Restore Local Evidence

Status: passed — bounded repository archive and disposable restore proof
Date: 2026-07-12
Authority: `decisions/2026-07-12-m19-bounded-backup-restore-proof-authorization.md`
Runbook: `planning-inbox/m19-backup-restore-owner-local-runbook.md`

## Verified result

```text
result: passed_repository_archive_and_restore_proof
source_branch: main
source_head: fc7c69a4282419675548505282dbe8db49b4a85d
restored_head: fc7c69a4282419675548505282dbe8db49b4a85d
bundle_sha256: c2b245d5cf302065dfafe21e4d45c95bd967ea1586e6c5b76c114154f52dca86
bundle_bytes: 1063828
encryption_status: blocked_pending_owner_tool_and_key_path
restore_integrity: passed
full_suite: passed
cleanup_status: not_authorized_artifacts_preserved
```

## Execution evidence

- source repository was clean and synced with upstream;
- full-history Git bundle creation succeeded;
- `git bundle verify` reported a complete history and a valid bundle;
- bundle SHA-256 was rechecked before restore;
- restored repository HEAD exactly matched source HEAD;
- restored working tree was clean;
- `git fsck --full` completed successfully over 1067 objects;
- prohibited ignored roots did not appear in the restore;
- restored full suite completed with `Ran 184 tests in 0.167s` and `OK`;
- expected blocked-path messages from preserved M13 safety tests appeared without provider execution or spend;
- local bundle, manifest, and restored repository remain preserved because cleanup is not authorized.

## Honest classification

This is a successful repository archive and restore proof. It is not an encrypted-backup proof because no separately approved encryption tool and owner-controlled key path were available. It does not prove cloud storage, database backup, customer/private-data recovery, automatic scheduling, production disaster recovery, or deployment recovery.
