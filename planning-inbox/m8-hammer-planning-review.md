# M8 Hammer Planning Review

Status: planning review / closure-readiness note
Authority: none — advisory review only; roadmap and decisions remain authority
Purpose: review the M8 hammer matrix and acceptance-gate policy for readiness to support M9 first-slice definition without pretending hammers have executed
Date: 2026-07-10
Reviewer: ChatGPT / Observatory Steward

---

## Review Question

Can M8 safely move from raw hammer drafting toward closure preparation, while preserving the boundary that M8 defines what must be proven but does not prove it yet?

---

## Source Files Reviewed

- `ROADMAP.md`
- `02-boundaries.md`
- `research/rg13-hammer-matrix-inputs.md`
- `contracts/README.md`
- all M7 contract drafts by index coverage
- `hammers/README.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `planning-inbox/owner-ruling-tracker.md`
- `planning-inbox/m7-contract-draft-set-review.md`

---

## Current M8 Outputs

M8 currently has:

- an earned `hammers/` folder with README/index;
- `hammers/hammer-matrix-v0-1.md` defining H1-H22 hammer categories;
- `hammers/acceptance-gate-policy-v0-1.md` defining acceptance levels, milestone gate defaults, and the M9 entry filter;
- `REPO_MAP.md` updated to show `hammers/` as active as of M8.

These outputs are planning artifacts. They do not implement hammers and do not mark any hammer as passed.

---

## Review Result

```text
M8 is substantially complete as a planning milestone, but closure should still preserve OR-B1 through OR-B3 as unresolved unless the owner records a decision.
```

The current M8 docs are strong enough to let M9 evaluate first-slice candidates without guessing the core acceptance criteria.

They are not enough to accept implementation, schema, provider admission, read tools, consumer workflows, or v1.

---

## What Is Strong Enough

### 1. Hammer category coverage

`hammer-matrix-v0-1.md` covers the RG13 H1-H22 categories:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H4  Customer-private rejection
H5  No strategy / recommendation storage
H6  CapturePackage validation
H7  Provider spend / duplicate tasks
H8  Provider attribution / disagreement
H9  Freshness / volatility / claim use
H10 AI / GEO overclaim
H11 Marketplace evidence ceiling
H12 Raw archive integrity
H13 Provider drift / parser safety
H14 Query panel immutability
H15 Evidence ID / citation integrity
H16 Consumer request / overlay
H17 LLM / agent access
H18 Hostile weird input
H19 Append-only observations
H20 Concurrency safety
H21 Audit-first enforcement
H22 Migration rollback / recovery
```

This satisfies the M8 need to define boundary-breaking hammer families.

### 2. Result vocabulary is clear

The result vocabulary distinguishes planning states from proof states:

```text
pass
fail
blocked_not_implemented
blocked_contract_missing
blocked_owner_ruling_required
blocked_provider_not_admitted
blocked_manual_review_required
```

The gate policy further separates:

```text
defined
mapped
mock_planning_only
fixture_executable
real_surface_executable
passed
```

This is important because it prevents future agents from treating a planned hammer as a passed hammer.

### 3. M9 entry filter exists

`acceptance-gate-policy-v0-1.md` gives M9 a candidate filter:

- avoid customer private data by default;
- avoid paid provider pulls by default;
- avoid marketplace capture ambiguity by default;
- exercise scope, rights, retention, provenance, and evidence IDs;
- avoid dashboard/API/MCP dependency where possible;
- name applicable hammers and deferred hammers.

This is enough for M9 to compare first-slice candidates responsibly.

### 4. Later milestone gates are mapped

The policy maps gate expectations across M9-M20. This gives later milestones a target without letting M8 perform their work.

### 5. Boundary law remains intact

The M8 docs preserve:

- no schema design;
- no migrations;
- no implementation;
- no provider purchases;
- no paid provider pulls;
- no provider admission;
- no API/MCP implementation;
- no dashboard work;
- no customer data handling;
- no strategy or recommendation storage.

---

## What Remains Open

### OR-B1 — Mock/stub level

Current default in `acceptance-gate-policy-v0-1.md`:

```text
Mock/stub hammers may support planning but cannot satisfy final implementation acceptance.
```

Closure posture:

- M8 may close with this default if explicitly carried forward.
- Later implementation milestones still need real execution where required.
- No mock-only pass should become implementation acceptance without owner ruling.

### OR-B2 — Which hammers are hard gates for which milestone

Current default:

- `acceptance-gate-policy-v0-1.md` proposes hard gate defaults by milestone.
- M9 must still name applicable hammers for the chosen first slice.
- Later milestone closure must explicitly confirm and execute applicable hammers.

Closure posture:

- M8 may close with the proposed mapping as draft gate policy.
- If owner wants the mapping to be binding authority, record a decision.

### OR-B3 — Freshness classes blocking customer-facing report use

Current default:

```text
Unknown, stale, volatile, or insufficiently sampled evidence cannot support strong current/customer-facing claims without caveat or block.
```

Closure posture:

- M8 may close with this fail-closed default.
- M15 / SearchClarity proof must revisit report-facing claim rules before any customer-facing output.

---

## M9 Readiness Assessment

M9 can safely start if it is framed as first-slice definition only.

M9 should be allowed to:

- compare first-slice candidates;
- choose the smallest useful evidence slice;
- name applicable hammers;
- name non-applicable/deferred hammers;
- name M10 schema-planning gates;
- name M12 implementation-execution gates;
- reject candidates that require provider spend, customer private data, marketplace ambiguity, dashboard, or API/MCP implementation too early.

M9 should not be allowed to:

- design schema;
- run migrations;
- build the slice;
- call providers;
- admit providers;
- create API/MCP tools;
- handle customer private data;
- create reports;
- store recommendations or strategy.

---

## Recommended M8 Closure Path

Recommended next batch:

1. Create an M8 closure decision record.
2. Mark M8 closed and M9 active in `ROADMAP.md`.
3. Refresh `ACTIVE_CONTEXT.md` and `NEXT_SESSION_HANDOFF.md` to M9.
4. Update `owner-ruling-tracker.md` only if the owner accepts explicit OR-B1/OR-B2/OR-B3 decisions; otherwise leave them open with references to the M8 policy defaults.
5. Keep all M8 docs as planning, not executable proof.

---

## Anti-Drift Notes

Do not infer from this review that:

- hammers have passed;
- implementation is authorized;
- schema is authorized;
- migrations are authorized;
- provider pulls are authorized;
- customer workflows are authorized;
- SearchClarity reports are authorized;
- API/MCP work is authorized;
- OR-B1, OR-B2, or OR-B3 are ruled unless a decision record says so.

---

## Closure Recommendation

```text
Recommend closing M8 if the owner accepts that OR-B1 through OR-B3 may remain open as fail-closed defaults carried into M9 and later milestones.
```

This means M9 can start first-slice definition, but M9 must use the M8 hammer matrix and acceptance-gate policy as its candidate filter.
