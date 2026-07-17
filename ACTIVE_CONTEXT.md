# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-14

---

## Current Phase

The independent DB-1 through DB-4 audit has been accepted as remediation input.

```text
DB-1 is trusted and complete.
DB-2 is trusted, accepted, and complete.
DB-3 is trusted, accepted, and complete as the physical-design authority.
DB-4 is active in remediation.
DB-5 is inactive.
```

Current authority:

```text
decisions/2026-07-17-db4-g1-g5-ob-dev-compatibility-correction-authorization.md
```

Accepted implementation authority remains bounded by:

```text
decisions/2026-07-14-db4-remediation-implementation-authorization.md
```

Current completion strategy and machine-readable baseline:

```text
audits/observatory-db4-drift-correction-and-completion-plan.md
database/db4-remediation-conformance-manifest.json
```

Source audits:

```text
audits/observatory-db1-through-db4-full-independent-audit.md
external post-remediation independent audit reviewed on 2026-07-15
```

Observatory v1 remains accepted at the bounded proof-system ceiling by `decisions/2026-07-12-observatory-v1-acceptance.md`.

---

## Active Milestone

```text
DB-4 — Database Hammer Harness and Migration Specification
```

State: exact bounded remediation implementation; PostgreSQL execution remains separately prohibited.

DB-4 is not closed. The prior disposable PostgreSQL runs are diagnostic evidence only and may not be promoted into closure evidence.

---

## Audit Ruling

The audit found that the current DB-4 implementation is not closure-grade because:

- the nine migration candidates do not faithfully implement accepted DB-3 physical responsibilities;
- migration history is mutable and not atomic with migration execution;
- mandatory hammer IDs are frequently mapped to structural catalog checks rather than hostile behavior;
- RLS and role behavior was not proven under bounded non-superuser execution;
- broken candidates did not traverse the real migration admission path;
- durable per-hammer result-register records do not exist;
- cleanup, failure preservation, security, and operational controls require hardening.

The current migrations, hammers, fixtures, profiles, and prior PostgreSQL output are retained only as diagnostic implementation evidence.

---

## Current Task

Execute the accepted Route C completion sequence without skipping batches:

```text
R0 reconciliation and honest baseline
R1 schema-hole correction
R2 real-spine behavioral proof
R3 hostile-candidate completion and redesign
R4 test/profile completion and retirement
R5 live-campaign gate preparation
separate owner execution decision
one disposable campaign
independent closure audit
```

Current batch:

```text
G1–G5 compatibility correction complete; connector refresh and repeat review pending
```

The exact-path correction is implemented in `ob-dev` commit `879529c27cad666099cf4f697eb7cbb56dec2279`. One connector refresh and a repeat frozen-compatibility review remain before the live gate can be reconsidered. PostgreSQL execution, acceptance of the live-campaign draft, DB-4 closure, and DB-5 remain prohibited.

Current authority:

```text
decisions/2026-07-17-db4-g1-g5-ob-dev-compatibility-correction-authorization.md
```

R5 gate evidence:

```text
planning-inbox/db4-r5-frozen-ob-dev-compatibility-review.md
planning-inbox/db4-live-disposable-campaign-owner-decision-draft.md
```

Gate state: `compatibility_corrections_committed_restart_pending`.

---

## Audit Finding Posture

All audit findings must be considered.

The MCP tool-count mismatch is a secondary governance/documentation reconciliation issue, not the primary technical blocker. The two additional bounded tools may remain if the later exact package accepts them.

The remediation program records six scoped disagreements or refinements:

- tool count is secondary;
- the thin schema may not simply be relabeled and deferred as the final DB-4 result;
- atomic migration/history is mandatory, but the exact implementation mechanism remains under design;
- durable result records are mandatory, but their exact storage/promotion path remains under design;
- data-driven profiles are prioritized while implementation hot reload is deferred;
- remote unauthenticated exposure is treated as a serious risk requiring verification and hardening, not as an unverified fact.

---

## Authorized Work

Authorized now under the exact package committed at `4d37a4f1fec51843a568dab00763f2e05da11ca2`:

- bounded Observatory and ob-dev implementation on the exact accepted paths;
- documentation and authority reconciliation;
- audit finding disposition and remediation planning;
- exact traceability design;
- migration/history architecture design;
- physical-schema remediation planning;
- behavioral-hammer mapping and hostile-test design;
- result-register emission and validation design;
- security and operational hardening design;
- data-driven profile and restart-reduction design;
- exact bounded implementation-package preparation;
- repository validation, exact staging, commits, and manual owner pushes.

No new PostgreSQL execution is authorized until a separate exact remediation execution package is accepted.

---

## Immediate Non-Goals and Prohibitions

Do not start or create:

- the governed database named `observatory`;
- governed or production roles, migrations, or persistence;
- new disposable PostgreSQL execution under the superseded happy-path campaign;
- production or production-like deployment;
- real evidence persistence;
- provider integration, provider calls, or paid pulls;
- ingestion, capture, or raw provider payload storage;
- customer records, customer first-party analytics, or private data;
- recurring capture or recurring work;
- autonomous spend;
- product API/MCP or dashboard work;
- strategy, recommendation, conclusion, score-as-truth, or report-state storage;
- DB-5 planning, activation, implementation, or execution;
- arbitrary shell, SQL, generic database tools, self-modifying behavior, or weakened fixed-root controls.

---

## Stop Conditions

Stop immediately on any:

- deviation from DB-2 or DB-3 without explicit owner ruling;
- schema responsibility with no traceability row;
- hammer ID that does not match its accepted hostile claim;
- structural precheck presented as a behavioral pass;
- migration and history executed in separate transactions;
- mutable accepted migration history;
- superuser-only proof of role or RLS behavior;
- fixture-name detector presented as semantic rejection;
- missing or overwritten failed result;
- secret exposure;
- unverified disposable marker or database identity;
- unauthenticated remote mutation surface;
- governed database, provider, customer/private data, production, recurring work, or DB-5 activity.

---

## Current Completion State

Trusted and closed:

```text
M0, M0.1, M1 through M20
DB-1
DB-2
DB-3
```

Active:

```text
DB-4 — remediation and exact implementation-package preparation
```

Inactive:

```text
DB-5 through DB-10
```

No milestone implies the next milestone.

---

## Tool Posture

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation, Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- Never push; the owner pushes manually.
- Owner actions remain owner actions. Tool availability never widens authority.
- Data-driven profiles and batched code changes are the preferred path to reducing restart churn.

---

## Boundary Posture

The Observatory stores observations, not conclusions. The connected LLM interprets at read time. Accepted conclusions promote out to the owning consumer.

Customer records and customer first-party analytics stay outside Observatory durable storage. Provider disagreement remains first-class evidence. Rights and retention fail closed. The database must physically enforce the telescope doctrine.
