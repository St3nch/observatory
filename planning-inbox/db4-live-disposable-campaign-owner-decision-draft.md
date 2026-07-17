# Draft — DB-4 Live Disposable Campaign Owner Decision

Status: draft — not accepted
Date drafted: 2026-07-17
Current authority: `decisions/2026-07-17-db4-post-audit-evidence-integrity-correction-authorization.md`
Authorized operation classes: none

This draft authorizes nothing. The first repeat review’s readiness claim was invalidated by the later independent audit. The bounded corrections are committed, but one MCP restart, tool refresh, and repeat independent review remain mandatory before this draft may be reconsidered.

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

## Current compatibility state

```text
Independent audit blockers corrected in ob-dev commit e6ba04da17bd5b27f0c3eaf9c3f71bc228bfc86b
MCP restart pending
Tool refresh pending
Repeat independent review pending
```

The gate is not ready for owner execution consideration until the restarted implementation passes repeat independent review. The draft remains unaccepted and authorizes no operations. The full mandatory acceptance criteria are maintained in `planning-inbox/db4-live-disposable-campaign-acceptance-checklist.md`.
