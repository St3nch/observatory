# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the DB-4 audit-remediation posture
Last updated: 2026-07-14

---

## Current State

```text
DB-1 — trusted and complete
DB-2 — trusted, accepted, and complete
DB-3 — trusted, accepted, and complete as physical-design authority
DB-4 — active in remediation and exact implementation-package preparation
DB-5 through DB-10 — inactive
```

Current authority:

```text
decisions/2026-07-17-db4-g1-g5-ob-dev-compatibility-correction-authorization.md
```

Accepted implementation authority remains:

```text
decisions/2026-07-14-db4-remediation-implementation-authorization.md
```

Current completion strategy and conformance baseline:

```text
audits/observatory-db4-drift-correction-and-completion-plan.md
database/db4-remediation-conformance-manifest.json
```

Source audits:

```text
audits/observatory-db1-through-db4-full-independent-audit.md
external post-remediation independent audit reviewed on 2026-07-15
```

The prior DB-4 disposable campaign is diagnostic only. DB-4 is not closed. DB-5 remains inactive.

---

## Active Milestone

```text
DB-4 — Database Hammer Harness and Migration Specification
```

State: exact bounded remediation implementation; PostgreSQL execution separately prohibited.

---

## Mandatory Root Read Path

1. `README.md`
2. `LLM_START_HERE.md`
3. `ACTIVE_CONTEXT.md`
4. `ROADMAP.md`
5. `ROADMAP_RULES.md`
6. `REPO_MAP.md`
7. `00-project-overview.md`
8. `01-harvest-register.md`
9. `02-boundaries.md`
10. `NEXT_SESSION_HANDOFF.md`

Then read:

1. `audits/observatory-db1-through-db4-full-independent-audit.md`
2. `decisions/2026-07-14-db4-audit-acceptance-and-remediation-activation.md`
3. `planning-inbox/db4-audit-remediation-program-v0-1.md`
4. accepted DB-2 and DB-3 artifacts indexed in `planning-inbox/README.md`
5. `POST_V1_DATABASE_ROADMAP.md`

If authority files disagree, stop and report the conflict.

---

## Current Task

Follow the accepted Route C sequence exactly:

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

The independent audit found blocking evidence-integrity defects after the first repeat review. The bounded corrections are committed in `ob-dev` at `e6ba04da17bd5b27f0c3eaf9c3f71bc228bfc86b`. One normal MCP restart, tool refresh, and repeat independent review remain mandatory. PostgreSQL execution, acceptance of the live-campaign draft, DB-4 closure, and DB-5 remain prohibited.

Current authority:

```text
decisions/2026-07-17-db4-post-audit-evidence-integrity-correction-authorization.md
```

Required R5 evidence:

```text
planning-inbox/db4-r5-frozen-ob-dev-compatibility-review.md
planning-inbox/db4-r5-repeat-ob-dev-compatibility-review.md
planning-inbox/db4-live-disposable-campaign-owner-decision-draft.md
```

No PostgreSQL execution begins until all blockers are closed and the owner separately accepts the execution decision.

---

## Accepted Finding Posture

All Claude audit findings must be considered.

The MCP tool-count issue is secondary. Reconcile it, but do not allow it to distract from:

- schema fidelity;
- atomic immutable migration history;
- real role/RLS enforcement;
- behavioral hammers;
- real broken-candidate admission tests;
- durable result records;
- marker, authority, redaction, and network hardening;
- restart reduction through data-driven profiles.

Scoped disagreements/refinements are recorded in the remediation plan. Do not silently substitute Claude’s preferred implementation mechanism where the plan leaves an architecture choice open.

---

## Authorized Scope

Authorized now:

- read-only inspection and audit reconciliation;
- planning and exact package preparation;
- current-state and roadmap updates;
- traceability, migration, hammer, proof, security, and restart-reduction design;
- bounded repository edits, validation, staging, and commits;
- manual owner pushes.

Not authorized:

```text
governed database observatory
new disposable PostgreSQL proof execution
DB-5 planning or implementation
providers, ingestion, capture, paid pulls
customer/private data
recurring work or autonomous spend
production or product API/MCP/dashboard work
strategy/recommendation/conclusion/report persistence
arbitrary shell or SQL
weakened fixed-root or authority controls
```

---

## Tool Discipline

- Use only `ob-dev` for local repository work.
- Never push.
- Preserve the protected untracked `audits/kaizen_to_slash_goal_prompt.md` file untouched.
- Use optimistic SHA control, diff review, fixed validation, exact staging, and manifest-locked commits.
- Batch code changes to reduce restarts.
- Prefer data-driven profile behavior over Python changes when safe and exact.

---

## Final Boundary

The Observatory stores observations, not conclusions. The connected LLM interprets at read time. Accepted conclusions promote out to the owning consumer.

DB-4 remediation does not create the governed database and does not activate DB-5.
