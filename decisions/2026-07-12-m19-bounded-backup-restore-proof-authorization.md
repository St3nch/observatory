# Decision — M19 Bounded Backup and Restore Proof Authorization

Status: accepted decision
Date: 2026-07-12
Milestone: M19 — Hardening, Backup, Recovery, and Operations

## Decision

Authorize one exact owner-local repository archive and disposable restore proof under the accepted M19 policy and task proposal.

Authorization phrase:

```text
APPROVE M19 BOUNDED BACKUP AND RESTORE PROOF TASK
```

## Exact local roots

```text
source_repository: C:\dev\observatory
work_root: C:\dev\observatory-backup-work
restore_root: C:\dev\observatory-restore-proof
```

These roots are outside the source repository. The proof must block if either work root resolves inside `C:\dev\observatory`, overlaps a secret/raw-capture root, or contains unexpected pre-existing material that would make containment ambiguous.

## Authorized stages

1. Verify source repository branch, exact HEAD, clean working tree, and sync with `origin/main`.
2. Create a full-history Git bundle from Git objects only.
3. Record bundle bytes and SHA-256.
4. Record encryption readiness.
5. Restore the bundle into the disposable restore root.
6. Verify expected commit, clean tree, `git fsck --full`, and absence of prohibited ignored roots.
7. Run the complete unit-test suite in the restored repository.
8. Record non-secret evidence and limitations.
9. Preserve local artifacts pending a separate cleanup authorization.

## Encryption posture

No encryption tool or owner-controlled key path is authorized by this decision.

Required classification for this execution unless a separate accepted decision exists before execution:

```text
encryption_status: blocked_pending_owner_tool_and_key_path
```

A successful bundle/restore proof must not be represented as an encrypted-backup proof.

## Non-authorizations

This decision does not authorize:

- cloud upload;
- credential or key transfer;
- password-manager access;
- automatic scheduling;
- live database backup;
- Postgres work;
- customer/private-data handling;
- provider execution;
- recurring capture;
- production deployment;
- deletion of the archive, restore tree, or work root.

## Required evidence

Repository-tracked evidence is limited to:

- `planning-inbox/m19-backup-restore-local-evidence.md`
- `test-results/m19-backup-restore-result-register.json`
- `planning-inbox/m19-closure-readiness-review.md` after successful review

No bundle, restored repository, command log containing local secrets, or encryption material may be committed.
