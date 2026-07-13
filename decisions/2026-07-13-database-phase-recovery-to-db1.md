# Decision — Database-Phase Recovery to Last Trusted DB-1 Checkpoint

Status: accepted
Date: 2026-07-13
Owner ruling: accepted explicitly in project conversation
Related milestone: DB-1 trusted closure; DB-2 reconciliation
Supersedes current-state claims from:

- `decisions/2026-07-13-db2-closure-and-db3-activation.md`
- `decisions/2026-07-13-db3-closure-and-db4-activation.md`

---

## Decision

The owner accepted the following recovery posture:

```text
ESTABLISH DB-1 AS THE LAST TRUSTED COMPLETED DATABASE MILESTONE.

REOPEN DB-2 FOR RECONCILIATION AND OWNER REVIEW ONLY.

SUSPEND DB-2 CLOSURE, DB-3 ACTIVATION/CLOSURE, AND DB-4 ACTIVATION
PENDING REVALIDATION UNDER CODEX.

PRESERVE LATER ARTIFACTS AS UNTRUSTED CANDIDATES, NOT AUTHORITY.

DO NOT AUTHORIZE POSTGRESQL WORK, MIGRATIONS, DATABASE TOOLS,
PERSISTENCE, PROVIDER CALLS, CUSTOMER DATA, OR PRODUCTION.
```

## Evidence for recovery

The canonical DB-2 freeze claims accepted v0.1.1 status but does not contain all accepted v0.1.1 classification corrections.

It still contains compound primary classifications despite its own singular-classification rule. It also describes DB-2 as closed while retaining pre-activation non-authorization language.

The later DB-3 readiness review states that no conflict exists with an accepted reconciled DB-2 v0.1.1 freeze. That claim is not supported by the canonical freeze content.

Therefore DB-2 closure, DB-3 activation/closure, and DB-4 activation cannot be relied upon without fresh reconciliation.

## Trusted state

```text
Observatory v1: accepted at the bounded proof-system ceiling
DB-1: closed and trusted
DB-2: active for reconciliation and owner review only
DB-3: suspended / inactive
DB-4: suspended / inactive
DB-5 through DB-10: planned / inactive
```

## Artifact classification

| Artifact class | Recovery status |
|---|---|
| DB-1 decisions and accepted DB-1 outputs | trusted |
| DB-2 freeze and correction package | candidate under reconciliation |
| DB-2 closure-readiness review | historical assessment; not closure authority |
| DB-2 closure / DB-3 activation decision | suspended |
| DB-3 specifications | untrusted candidates; may be salvaged only after DB-2 revalidation |
| DB-3 closure / DB-4 activation decision | suspended |
| DB-4 work authority | none |

Suspension preserves history. It does not delete or silently rewrite the later artifacts.

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
4. a new explicit decision closes DB-2 and separately decides whether DB-3 activates.

## Final rule

```text
Trust stops at DB-1.
DB-2 must be proven coherent in the file itself, not declared coherent by a later note.
No later milestone survives on paperwork momentum.
```
