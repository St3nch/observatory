# Draft — DB-4 Live Disposable Campaign Owner Decision

Status: draft — not accepted
Date drafted: 2026-07-17
Current authority: `decisions/2026-07-17-db4-r5-live-campaign-gate-preparation-authorization.md`
Authorized operation classes: none

This draft authorizes nothing. It may be promoted into `decisions/` only after every blocker in `planning-inbox/db4-r5-frozen-ob-dev-compatibility-review.md` is closed and a repeat compatibility review returns ready.

## Proposed decision

Authorize one bounded disposable DB-4 proof campaign using exact clean Observatory and `ob-dev` commits, one unique campaign identifier, one newly created `observatory_test_*` database, bounded test roles, accepted profiles and fixtures, append-only result records, and independent review.

## Preconditions before acceptance

- both working trees are clean;
- exact commits and server identity are recorded;
- the disposable marker is verified before every operation;
- the accepted authority file and exact operation classes are enforced;
- all eight active profiles and all sixteen concrete fixtures are supported and SHA-bound;
- all six test roles satisfy the accepted privilege posture;
- direct cross-scope behavior includes the backup role;
- append-only campaign-register emission and validation exist;
- secret/redaction review is enabled;
- the owner has reviewed the final bounded sequence and acceptance checklist.

## Proposed bounded sequence

1. Record clean code and server identity.
2. Create and mark one disposable database.
3. Create and verify bounded test roles.
4. Apply forward migrations atomically with matching history.
5. Execute all active profiles and hostile candidates.
6. Verify rejection behavior, SQLSTATEs, concurrency, scope isolation, and zero residue.
7. Create and semantically verify backup/restore evidence.
8. Apply reverse rollback and verify the accepted empty state.
9. Remove test roles and disposable databases.
10. Emit append-only result and campaign records for independent review.

## Failure rule

Stop on any marker or authority mismatch, dirty tree, unknown profile or fixture, unexpected SQLSTATE, scope leak, residue, secret exposure, failed cleanup, or incomplete record. Preserve failed and blocked records; never overwrite them.

## Closure boundary

Campaign execution does not close DB-4. Independent review and a separate owner DB-4 closure decision remain mandatory. DB-5 stays inactive.

## Current blockers

```text
G1 profile execution lacks marker verification
G2 accepted authority and operation-class enforcement is unused
G3 eight R3 fixtures lack executor support
G4 backup cross-scope behavior lacks direct proof
G5 campaign-register and clean-tree preconditions are incomplete
```

The full mandatory acceptance criteria are maintained in `planning-inbox/db4-live-disposable-campaign-acceptance-checklist.md`.
