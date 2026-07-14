# Decision — Database-Phase Recovery to Last Trusted DB-1 Checkpoint

Status: accepted; amended by explicit owner ruling 2026-07-13
Date: 2026-07-13
Owner ruling: accepted explicitly in project conversation
Related milestone: DB-1 trusted closure; DB-2 reconciliation
The untrusted later-milestone artifacts formerly present in the active repository were permanently retired and deleted by explicit owner ruling. Git history is sufficient archival retention.

---

## Decision

The owner accepted the following recovery posture:

```text
ESTABLISH DB-1 AS THE LAST TRUSTED COMPLETED DATABASE MILESTONE.

REOPEN DB-2 FOR RECONCILIATION AND OWNER REVIEW ONLY.

DB-2 REMAINS ACTIVE FOR RECONCILIATION AND OWNER REVIEW ONLY.

DB-3 AND DB-4 ARE INACTIVE. NO DB-3 OR DB-4 ARTIFACT IS
ACTIVE OR AUTHORITATIVE.

ANY FUTURE DB-3 WORK MUST BE CREATED FRESH AFTER AN EXPLICIT DB-2 OWNER GATE.

DO NOT AUTHORIZE POSTGRESQL WORK, MIGRATIONS, DATABASE TOOLS,
PERSISTENCE, PROVIDER CALLS, CUSTOMER DATA, OR PRODUCTION.
```

## Evidence for recovery

The canonical DB-2 freeze claims accepted v0.1.1 status but does not contain all accepted v0.1.1 classification corrections.

It still contains compound primary classifications despite its own singular-classification rule. It also describes DB-2 as closed while retaining pre-activation non-authorization language.

Later-milestone work relied on the unsupported claim that the canonical freeze was complete and conflict-free. That work is not retained in the active repository and grants no present or future authority.

## Trusted state

```text
Observatory v1: accepted at the bounded proof-system ceiling
DB-1: closed and trusted
DB-2: active for reconciliation and owner review only
DB-3: inactive; no active or authoritative artifact
DB-4: inactive; no active or authoritative artifact
DB-5 through DB-10: planned / inactive
```

## Artifact classification

| Artifact class | Recovery status |
|---|---|
| DB-1 decisions and accepted DB-1 outputs | trusted |
| DB-2 freeze and correction package | candidate under reconciliation |
| DB-2 closure-readiness review | historical assessment; not closure authority |
| DB-3 and DB-4 artifacts | permanently retired and deleted from the active repository; Git history only |
| DB-3 and DB-4 work authority | none |

No deleted artifact may be restored, salvaged, or treated as candidate authority. Future DB-3 work starts fresh only after an explicit DB-2 owner gate.

## Allowed recovery work

- reconcile the DB-2 canonical freeze with its proposed correction package;
- audit DB-2 concept classifications and boundaries from the trusted DB-1 checkpoint;
- correct current-state and navigation documents;
- add Codex project instructions and deterministic authority-drift checks;
- prepare a fresh DB-2 owner review package.

## Non-authorizations

```text
No PostgreSQL database creation.
No role or credential creation.
No SQL or DDL.
No migration files or execution.
No disposable database lifecycle.
No real-PostgreSQL hammers.
No database-control-plane expansion.
No synthetic or real persistence.
No provider calls, paid pulls, or ingestion.
No customer or private data.
No raw capture.
No production API/MCP.
No recurring capture.
No strategy, recommendation, conclusion, or report-state persistence.
```

## Tool posture

Codex native local tools own ordinary PowerShell, filesystem, Git, and test work.

`ob-dev-mcp` remains limited to its current bounded file-oriented surface during recovery. The old `ob-dev` service receives no new project authority.

## Next owner gate

DB-2 may close only after:

1. the canonical freeze is actually reconciled;
2. the reconciled text passes a fresh boundary and classification audit;
3. the owner reviews the exact resulting artifact;
4. a new explicit decision closes DB-2 and separately decides whether fresh DB-3 work activates.

## Final rule

```text
Trust stops at DB-1.
DB-2 must be proven coherent in the file itself, not declared coherent by a later note.
No later milestone survives on paperwork momentum.
```
