# M19 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Milestone: M19
Date: 2026-07-12

## Purpose

Present the minimum rulings required before any bounded backup, restore, secret-exposure, or retention-cleanup proof task can be authorized.

## M19-R1 — Protected unit

Proposed ruling:

```text
The M19 v1 protected unit is the exact Git repository state and full Git history, not the whole machine, secrets, virtual environment, ignored raw capture roots, or a hypothetical database.
```

## M19-R2 — Backup mode

Proposed ruling:

```text
Use manual encrypted repository backups only for Observatory v1.
```

No scheduled or automatic backup job is authorized.

## M19-R3 — Backup timing

Proposed ruling:

Create a manual backup after significant accepted milestone closure and before future high-risk structural work. Frequency is event-driven by owner-reviewed project state, not clock-driven automation.

## M19-R4 — Retention generations

Proposed ruling:

Retain at least two independently verifiable encrypted generations once available. The only verified generation may not be deleted. Deletion requires a verified successor and successful restore proof.

## M19-R5 — Restore proof

Proposed ruling:

A backup is not accepted until restored into a disposable separate directory and verified by hashes, exact commit identity, clean Git state, integrity checks, and the full test suite.

## M19-R6 — Secret posture

Proposed ruling:

M19 may inspect tracked/staged content for likely secret patterns and record only redacted finding metadata. It may not read password-manager contents, transfer credentials, print secrets, or perform automatic rotation.

## M19-R7 — Cleanup posture

Proposed ruling:

No destructive cleanup occurs in the planning package. Any purge or disposable-restore deletion requires an exact target, containment proof, pre/post evidence, and separate owner authorization.

## M19-R8 — Bounded proof eligibility

After accepting the policy and rulings, M19 may propose one exact local proof task that:

- creates a repository-only archive/bundle in an explicitly ignored local work root;
- records hashes and a non-secret manifest;
- encrypts only if an already-approved local tool and owner-supplied key path are available;
- otherwise stops at a dry-run/readiness proof;
- restores into a disposable separate root;
- verifies commit, Git integrity, and the full suite;
- performs no cloud upload, credential transfer, database operation, provider call, or automatic scheduling;
- does not delete artifacts without separate exact authorization.

Implementation remains separately gated.

## Recommended decision bundle

```text
ACCEPT repository-only protected-unit boundary
ACCEPT manual encrypted backup posture for v1
ACCEPT milestone/high-risk-event backup timing
ACCEPT minimum two verified generations once available
ACCEPT disposable restore proof as mandatory
ACCEPT redacted tracked/staged secret inspection only
ACCEPT no destructive cleanup without separate exact authorization
ACCEPT one bounded M19 proof-task proposal, not implementation
```

## Deferred

- automatic backups;
- cloud storage selection and upload;
- credential/key delivery;
- live database backup;
- machine image or full workstation backup;
- operational alerting;
- production deployment and disaster recovery;
- destructive cleanup execution.
