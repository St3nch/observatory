# M19 Backup and Restore Policy v0.1

Status: planning proposal
Milestone: M19
Date: 2026-07-12

## Purpose

Define a bounded, manual, encrypted backup and restore-proof posture for the current Git-based Observatory without implying production deployment, database backup, automatic scheduling, or secret transfer.

## Protected unit

The protected unit is one exact Observatory Git repository state identified by:

```text
repository: observatory
branch
commit_sha
commit_subject
working_tree_clean
remote_tracking_state
created_at
```

A backup is invalid if the repository is dirty, the commit cannot be resolved, or the archive manifest does not identify the exact protected commit.

## Backup contents

Required:

- a Git bundle or equivalent full-history repository archive;
- a plain manifest with no secrets;
- archive byte count;
- SHA-256 hash of the unencrypted archive;
- SHA-256 hash of the encrypted artifact;
- creation timestamp and actor;
- declared exclusions.

Excluded:

```text
.env files
secrets and credentials
virtual environments
build/cache outputs
ignored raw captures and probe evidence
customer/private data
machine-wide configuration
unrelated repositories
```

## Encryption posture

The backup artifact must be encrypted before leaving the local work area.

Planning requirements:

- modern authenticated encryption;
- decryption material stored outside the repository;
- no passwords or private keys committed to Git;
- no plaintext archive retained after encrypted-artifact verification, unless a separately approved temporary working copy is required for the restore proof;
- encrypted artifact hash recorded before transfer.

M19 does not select or install an encryption tool and does not transfer credentials.

## Frequency posture

For the current non-operational repository:

- create one manual backup after accepted milestone closure or other significant accepted state;
- create another before any future high-risk structural change;
- no hourly/daily scheduler is justified;
- no automatic backup job is authorized.

## Retention posture

Planning minimum:

- retain at least two independently verifiable encrypted generations once such generations exist;
- do not delete the only verified generation;
- deletion requires a successor generation plus successful restore proof;
- retain manifests and hashes only when they contain no secret or excluded private material.

## Disposable restore proof

Restore into a new disposable directory outside the active repository.

Required proof sequence:

1. verify encrypted artifact hash;
2. decrypt to a temporary isolated location;
3. verify plaintext archive hash;
4. restore/clone the repository from the archive;
5. verify expected commit SHA and clean working tree;
6. run Git integrity checks;
7. run the project import check where the fixed environment supports it;
8. run the full test command:

```powershell
$env:PYTHONPATH = (Join-Path $PWD "src")
python -m unittest discover -s tests
```

9. record test count and result;
10. confirm ignored secret/raw paths were not introduced;
11. remove the disposable plaintext restore only after evidence is recorded and owner-authorized cleanup is available.

## Restore acceptance

A restore proof passes only when:

- hashes match;
- expected commit is restored;
- Git integrity passes;
- working tree is clean;
- full suite passes;
- no secrets or excluded raw/private material appear;
- limitations are recorded honestly.

## Failure handling

Any mismatch stops the proof. Do not repair the restored copy silently and call it successful.

Failures must record:

```text
failed_stage
expected_value
observed_value
artifact_identity
operator
occurred_at
cleanup_status
```

## Explicit non-authorizations

This policy does not authorize:

```text
automatic backup jobs
cloud connector setup
credential transfer
password-manager export
live database backup
Postgres creation or dump
customer/private-data backup
provider execution
production deployment
destructive deletion
```
