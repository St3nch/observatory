# Post-v1 / Pre-Database Audit Response Tracker

Status: active planning authority for audit routing only; subordinate to accepted decisions and root boundaries
Date: 2026-07-12
Audit: `audits/observatory-post-v1-pre-database-deep-audit-2026-07-12.md`
Acceptance decision: `decisions/2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md`

## Routing rule

No finding or opportunity may be silently omitted, partially cherry-picked, or treated as authority merely because it appears in the audit.

Allowed dispositions:

```text
accept_apply_db1
accept_assign_future_gate
accept_limit_visible
needs_owner_ruling
reject_with_reason
opportunity_parked
```

## Executive disposition

```text
v1 acceptance: preserved
audit quality: accepted as high-quality advisory input
database planning: authorized
database creation / DDL / migrations: not authorized
```

## Finding ledger

| ID | Severity | Disposition | Required action | Gate |
|---|---|---|---|---|
| N-01 | High | accept_apply_db1 | Correct typed-read ceiling disclosure contract and prototype; add over-ceiling adversarial test; route database silent-partial-view hammer | Blocks DB-backed reads, not physical planning |
| N-02 | High | needs_owner_ruling | Rule OR-B1 and OR-B2; accept hammer matrix/policy v0.2; define per-hammer result register | Blocks migration execution and real ingestion |
| N-03 | High | accept_assign_future_gate | Create one consolidated owner-accepted physical data contract before physical schema specification | DB-2 exit / DB-3 entry |
| N-04 | High | accept_assign_future_gate | Build clone-stable decision-linked provider authority, duplicate, budget, attempt-lifecycle, and idempotency enforcement before real ingestion | Blocks real ingestion |
| N-05 | Medium | accept_apply_db1 | Remove stale phase restatements from `README.md` and `LLM_START_HERE.md`; use authority pointers only | Documentation truth |
| N-06 | Medium | needs_owner_ruling | Rule OR-C2 retention posture per source family and OR-C4 raw archive layout | Blocks raw-support physical specification |
| N-07 | Medium | accept_assign_future_gate | Require encrypted off-machine database backup and semantic restore proof before real evidence persistence | DB recovery / real ingestion gate |
| N-08 | Medium | accept_apply_db1 | Implement and test cursor expiration required by typed-read contract | Blocks DB-backed reads |
| N-09 | Low | accept_apply_db1 | Correct stale Hermes-lineage statement in accepted typed-read contract with version/change-log note | Contract hygiene |
| N-10 | Low | accept_assign_future_gate | Replace mutable fixture dictionaries with repository/storage interfaces for persistence work; do not copy fixture pattern | DB implementation pattern |
| N-11 | Low | accept_apply_db1 | Define and test nested authorization/capability composition for `freshness_check` | Typed-read correctness |
| N-12 | Low | accept_assign_future_gate | Move cursor/signing secret to managed secret with rotation posture before DB/network-backed reads | DB-backed read / production gate |
| N-13 | Low | accept_apply_db1 | Compute `consumer_promotion_required`; add forcing fixture/test | Typed-read contract proof |
| N-14 | Low | accept_apply_db1 | Document conservative claim-intent translation between M15 and M14 | Consumer contract hygiene |

## Opportunity ledger

| Audit opportunity | Disposition | Current route |
|---|---|---|
| Historical observation replay / as-of reads | opportunity_parked | Design-preservation input for DB-2/DB-3; no implementation authority |
| Provider shape-drift histories | opportunity_parked | Preserve fingerprint/event extensibility; data requires later provider gates |
| SERP feature evolution / rare-feature archive | opportunity_parked | Requires separately authorized recurrence and source-family admission |
| Multi-provider disagreement histories | opportunity_parked | Persist provider testimony only; disagreement remains compute-on-read under OR-A1 |
| Claim-safe absence histories | opportunity_parked | Requires repeated governed sampling and claim-safety review |
| Freshness-aware evidence packs | opportunity_parked | Derived read model; never stored as conclusion |
| Provider cost and evidence-yield analysis | opportunity_parked | Future read-time operational analysis over capture/cost evidence |
| Rights-aware evidence reuse | opportunity_parked | Core design objective; consumers remain external |

## Accepted correction order

```text
1. Preserve/index audit and activate DB-1.
2. Correct stale authority pointers and accepted-contract truth defects.
3. Correct typed-read truncation, cursor expiry, authorization composition,
   promotion flag, and claim-intent mapping proof gaps.
4. Rule OR-B1, OR-B2, OR-C2, and OR-C4.
5. Accept hammer matrix / gate policy v0.2 and per-hammer register contract.
6. Freeze one consolidated physical data contract.
7. Specify Postgres operational boundary and physical schema.
8. Build disposable real-Postgres hammer harness before migration execution.
```

## DB-1 exit criteria

DB-1 may close only when:

- N-01 through N-14 each have a committed disposition and evidence path;
- N-05 and N-09 documentation-truth corrections are complete;
- N-01/N-08/N-11/N-13/N-14 corrections are implemented and locally proven, or explicitly split by a separately accepted bounded task;
- OR-B1/B2/C2/C4 have owner-ready ruling proposals;
- hammer v0.2 and per-hammer register proposals exist;
- the DB-2 physical data-contract-freeze package is fully specified;
- no Postgres, DDL, or migration execution has occurred.

## Non-authorizations

```text
No Postgres creation.
No DDL.
No migration files or execution.
No real ingestion.
No provider calls.
No production or customer work.
```
