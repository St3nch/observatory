# M19 Bounded Backup and Restore Proof Task Proposal

Status: authorized exact owner-local proof task
Milestone: M19
Date: 2026-07-12

## Goal

Prove that one exact clean Observatory Git state can be archived, independently hashed, restored into a disposable separate directory, and verified without including secrets, ignored raw captures, customer/private data, databases, provider activity, or automatic scheduling.

## Preconditions

- M19 policy and owner rulings accepted;
- repository clean and synced;
- exact HEAD recorded;
- local work root explicitly outside the repository or ignored;
- no suspected secret exposure;
- no unclassified raw/private material;
- owner separately authorizes this exact task.

## Allowed task outputs

Repository-tracked proof metadata only:

```text
planning-inbox/m19-backup-restore-local-evidence.md
test-results/m19-backup-restore-result-register.json
planning-inbox/m19-closure-readiness-review.md
```

Local untracked work artifacts only under an explicitly approved work root:

```text
repository bundle/archive
plain manifest
optional encrypted artifact
restored disposable repository
command output logs with no secrets
```

No backup artifact is committed to Git.

## Exact proof stages

### Stage 1 — Preflight

Record:

- branch and HEAD;
- clean working tree;
- remote tracking state;
- Git version and Python version;
- declared local work and restore roots;
- exclusion posture;
- proof authorization reference.

Block on dirty state, ambiguous paths, missing authorization, or suspected secrets/private data.

### Stage 2 — Repository archive

Create a full-history Git bundle or equivalent repository-only archive.

Record:

- filename;
- byte count;
- SHA-256;
- source commit;
- creation timestamp.

The archive must derive from Git objects, not an indiscriminate filesystem zip.

### Stage 3 — Encryption readiness or encryption

If an already-approved encryption tool and owner-controlled key path are available under a separate accepted ruling, create an encrypted artifact and record its hash.

Otherwise:

```text
encryption_status: blocked_pending_owner_tool_and_key_path
```

Do not invent passwords, read password-manager contents, or transfer credentials. A dry-run/readiness result is acceptable and must not be represented as an encrypted-backup pass.

### Stage 4 — Disposable restore

Restore from the repository archive into a new separate directory.

Verify:

- archive hash before use;
- expected commit;
- clean working tree;
- Git fsck/integrity result;
- no ignored secret/raw paths introduced.

### Stage 5 — Functional proof

Run:

```powershell
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

Record exact test count, duration, and result.

### Stage 6 — Evidence recording

Record only non-secret metadata, hashes, paths reduced to approved root labels where necessary, limitations, and cleanup status.

### Stage 7 — Cleanup gate

Do not delete the restored copy, plaintext archive, or other artifacts automatically.

Prepare a containment-checked cleanup proposal. Deletion requires separate exact owner authorization.

## Required hostile paths

- dirty repository -> block;
- archive path inside tracked repository -> block;
- work root overlaps secret/raw roots -> block;
- hash mismatch -> block restore;
- wrong restored commit -> fail;
- Git integrity failure -> fail;
- full suite failure -> fail;
- secret/raw ignored path appears in restore -> fail;
- encryption unavailable -> readiness-only, not pass;
- cleanup requested without exact authorization -> block.

## Proof classification

Possible outcomes:

```text
passed_repository_archive_and_restore_proof
passed_encrypted_backup_and_restore_proof
blocked_encryption_readiness
failed_integrity
failed_functional_restore
```

A repository archive/restore pass is not an encrypted-backup pass unless encryption and encrypted-artifact verification actually occur.

## Explicit non-authorizations

```text
automatic scheduling
cloud upload
credential transfer
password-manager access
secret rotation
live database backup
Postgres work
customer/private data handling
provider execution
recurring capture
production deployment
destructive cleanup
```

## Proposed owner authorization phrase

```text
APPROVE M19 BOUNDED BACKUP AND RESTORE PROOF TASK
```
