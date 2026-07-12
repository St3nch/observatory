# Decision — M19 Closure and M20 Activation

Status: accepted decision
Date: 2026-07-12
Milestone transition: M19 -> M20

## Decision

Close M19 — Hardening, Backup, Recovery, and Operations — for the bounded repository-only Observatory v1 scope and activate M20 — Observatory v1 Acceptance — for planning and acceptance review only.

## Accepted M19 evidence

- repository-only protected unit accepted;
- manual encrypted-backup posture accepted for v1;
- restore proof required before backup acceptance;
- exact owner-local repository bundle/restore task authorized and executed;
- source and restored HEAD both verified as `fc7c69a4282419675548505282dbe8db49b4a85d`;
- full-history Git bundle verified;
- bundle SHA-256 recorded as `c2b245d5cf302065dfafe21e4d45c95bd967ea1586e6c5b76c114154f52dca86`;
- bundle byte count recorded as `1063828`;
- restored repository passed `git fsck --full`;
- prohibited ignored roots were absent;
- restored full suite passed: 184 tests in 0.167 seconds;
- local artifacts remain preserved because cleanup is not authorized.

## Honest limitation

Encryption remains blocked pending a separately approved local encryption tool and owner-controlled key path. M19 therefore proves repository archive and restore integrity, not encrypted-backup readiness or off-machine disaster recovery.

## M20 authority

M20 may review the complete v1 record against doctrine, contracts, hammers, evidence behavior, consumer usefulness, recovery proof, known limitations, and deferred capabilities.

M20 does not authorize:

```text
production deployment
provider execution
recurring capture
customer data or reports
live Postgres/schema/migrations
production API/MCP
credentials or secret transfer
cloud backup upload
automatic backup jobs
destructive cleanup
strategy or recommendation storage
```

## Next step

Prepare the Observatory v1 acceptance review and explicit accept/reject recommendation. No implementation widening is implied.
