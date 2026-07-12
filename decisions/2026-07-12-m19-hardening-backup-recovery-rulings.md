# Decision — M19 Hardening, Backup, and Recovery Rulings

Status: accepted decision
Date: 2026-07-12
Milestone: M19 — Hardening, Backup, Recovery, and Operations

## Decision

Accept the M19 backup, restore, secret-review, cleanup, and bounded-proof rulings prepared in `planning-inbox/m19-owner-ruling-proposals.md`.

## Accepted rulings

### Protected unit

The Observatory v1 protected unit is the exact Git repository state and full Git history.

The protected unit does not include:

- the entire workstation;
- credentials or secret stores;
- virtual environments or dependency caches;
- ignored raw capture roots;
- customer/private data;
- unrelated repositories;
- a hypothetical or future database.

### Backup mode

Observatory v1 uses manual encrypted repository backups only.

No scheduler, cron job, Windows task, background service, automatic backup worker, or recurring backup automation is authorized.

### Backup timing

A manual backup is expected after significant accepted milestone closure and before future high-risk structural work.

This is an owner-reviewed event-driven posture, not clock-driven recurrence.

### Retention generations

Retain at least two independently verifiable encrypted generations once two are available.

The only verified generation may not be deleted. A generation may be removed only after a verified successor exists and that successor has passed restore proof.

### Restore proof

A backup is not accepted until it has been restored into a disposable separate directory and verified through:

- archive/content hashes;
- exact expected commit identity;
- clean Git state;
- Git integrity checks;
- the full repository test suite;
- explicit recorded limitations.

### Secret posture

M19 may inspect tracked and staged repository content for likely secret patterns and retain only redacted finding metadata.

M19 may not:

- read password-manager contents;
- transfer or expose credentials;
- print secret values;
- inspect unrelated machine locations;
- rotate credentials automatically.

### Cleanup posture

No destructive cleanup is authorized by this decision.

Any purge or disposable-restore deletion requires:

- one exact target;
- containment proof;
- pre-operation evidence;
- post-operation evidence;
- separate exact owner authorization.

### Bounded proof eligibility

One exact local repository archive/restore proof task may be proposed after this decision.

Eligibility does not authorize implementation. Any proof implementation remains separately gated and must preserve these limits:

- repository-only archive/bundle;
- explicitly ignored local work root;
- non-secret manifest and hashes;
- encryption only with an already-approved local tool and owner-controlled key path;
- honest stop at readiness-only status if encryption prerequisites are unavailable;
- disposable separate restore root;
- commit, Git integrity, and full-suite verification;
- no cloud upload;
- no credential transfer;
- no database operation;
- no provider call;
- no scheduling;
- no deletion without separate exact authorization.

## Still unauthorized

```text
backup execution
encryption-key or credential transfer
password-manager access
cloud upload
automatic backup jobs
live database backup
Postgres creation, schema, or migrations
customer/private-data backup
provider execution
recurring capture
production deployment
production API/MCP
destructive cleanup
```

## Result

The M19 planning policy and rulings are accepted. The exact bounded archive/restore proof remains a separate implementation gate.
