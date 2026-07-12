# M18 Recurring Watch Panel Reconciliation Review

Status: planning
Milestone: M18 - Recurring Watch Panel Planning
Date: 2026-07-12

## Purpose

Reconcile accepted provider, query-panel, freshness, rights, cost, duplicate-prevention, and hammer boundaries before any recurring-capture decision.

## Accepted authority

M18 inherits these rules:

- query panels are measurement programs, not schedulers;
- a panel run never implies recurrence;
- provider admission and spend approval remain separate;
- rights and retention fail closed;
- stale or incomplete evidence must carry warnings;
- duplicate paid work must be blocked before execution;
- blocked or failed runs do not create observations;
- provider disagreement remains attributed evidence;
- customer/private data and strategy remain outside Observatory.

## Reconciled posture

### Planning is meaningful

A recurring watch panel can be described responsibly because the repo now contains:

- one bounded provider admission/probe precedent;
- explicit cost and stop-condition patterns;
- query-panel/version rules;
- freshness, staleness, and volatility rules;
- cross-provider disagreement proof;
- hostile-path requirements.

### Execution is not yet justified

M18 should not authorize recurring execution in v1 because:

- only one narrow DataForSEO pull family has been validated;
- no production scheduler, credential posture, persistence, operations, backup, or recovery layer is accepted;
- no recurring budget has been approved;
- source-family coverage remains incomplete;
- marketplace and AI/GEO execution remain blocked or methodology-limited;
- M19 hardening has not occurred.

## Required plan components

A responsible recurring plan must define:

- one scope and one immutable panel version;
- admitted source family and provider/capture instrument;
- cadence class tied to volatility/freshness need;
- per-run and rolling budget ceilings;
- duplicate-prevention key and collision behavior;
- retry and polling ceilings;
- rights/retention revalidation before each run;
- stop conditions and failure budget;
- manual review checkpoints;
- stale, incomplete, blind-spot, and timing warnings;
- explicit owner enablement and disablement.

## Recommendation

```text
APPROVE M18 planning output.
REJECT recurring capture execution for Observatory v1 at this time.
```

A later roadmap change may reconsider execution only after M19 operational hardening and a separate owner decision.
