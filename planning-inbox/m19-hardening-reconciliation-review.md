# M19 Hardening, Backup, Recovery, and Operations Reconciliation Review

Status: planning
Milestone: M19
Date: 2026-07-12

## Purpose

Reconcile the actual Observatory repository and evidence footprint against accepted raw-archive, retention, purge, hammer, and no-production boundaries before any backup or recovery implementation.

## Current durable footprint

The current durable Observatory system consists of:

- Git-tracked doctrine, roadmap, decisions, contracts, research, planning, source, tests, and result registers;
- a GitHub remote used as the primary repository replication path;
- bounded synthetic/local proof implementations;
- sanitized manifests, hashes, purge proof, and local-test evidence where accepted;
- no production database, object store, scheduler, service, customer dataset, or recurring capture system.

## Current intentionally non-durable footprint

The repository intentionally ignores:

```text
.env and secret files
secrets/
.venv and build/cache directories
captures/
raw-captures/
probe-evidence/
*.local.json
```

This means the repository backup cannot be treated as a backup of secrets, local environments, or transient raw provider payloads.

The M13 paid probe raw response was captured under a temporary capture-and-purge posture and purged with proof. M19 must not recreate or preserve that deleted raw payload.

## Backup classes

### Class A — Canonical repository state

Include:

- all Git-tracked files;
- full Git history, branches, tags, and commit metadata;
- repository configuration needed to verify history;
- a manifest of the backed-up commit and archive hash.

### Class B — Accepted operation evidence outside Git

Currently none is required for Observatory v1 closure beyond accepted Git-tracked proof records.

Any future non-Git operation evidence must be separately inventoried before backup admission.

### Class C — Explicitly excluded material

Exclude:

- credentials, tokens, `.env`, secrets, password-manager exports;
- customer/private telemetry;
- transient raw provider payloads whose retention is not admitted;
- caches, virtual environments, build outputs;
- arbitrary machine-wide files;
- other project repositories.

## Reconciliation conclusions

1. GitHub replication is useful but is not by itself a complete recovery proof.
2. A separate encrypted repository bundle/archive can prove independent recoverability without widening project scope.
3. Restore proof should occur in a disposable directory and verify commit identity, working-tree integrity, importability where supported, and the full 184-test suite.
4. Backup automation is unnecessary and unauthorized for the current small, non-operational footprint.
5. Manual backup after accepted milestone transitions is sufficient planning posture for v1.
6. Destructive retention cleanup must remain separately authorized; M19 may define purge proof but must not delete live material by default.
7. Secret scanning should inspect tracked content and staged changes for likely credentials without reading or exporting actual secrets.

## M19 planning recommendation

Accept a bounded manual encrypted-backup and disposable-restore policy for the Git repository only.

Do not create automatic jobs, cloud connectors, live database backups, secret-transfer workflows, or destructive cleanup tooling in M19 without a separate exact task and owner authorization.
