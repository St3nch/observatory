# M7 Contract Draft Set Review

Status: planning review
Authority: review note only; not doctrine; not contract acceptance; not M8 approval
Date: 2026-07-10
Reviewer: ChatGPT / Observatory Steward
Scope: Review the 13 drafted M7 contracts for consistency, owner-ruling carry-forward, boundary discipline, and readiness for M8 hammer planning.

---

## Executive summary

All 13 planned M7 contracts are now drafted and indexed in `contracts/README.md`.

This review finds the set is directionally coherent and suitable for an owner review pass before M8 hammer planning, with one important caveat:

```text
Drafted does not mean accepted.
Accepted contracts still require owner review/ruling.
M8 hammers should be planned against the draft set, but the contracts should not be treated as binding law until accepted.
```

No schema, migrations, provider admission, API/MCP implementation, dashboard work, customer data storage, recurring capture, paid provider pulls, or customer-facing report workflow should begin from this draft set alone.

---

## Reviewed contract set

The drafted M7 set is:

```text
1. scope-rights-retention.md
2. evidence-id-citation.md
3. freshness-staleness-volatility.md
4. claim-safety.md
5. query-panel.md
6. capturepackage-v0-1.md
7. raw-archive-provider-drift.md
8. provider-testimony.md
9. provider-cross-check.md
10. consumer-promotion.md
11. overlay.md
12. searchclarity-consumer-placeholder.md
13. typed-read-tool-skeleton.md
```

The index now records all 13 as drafted.

---

## Consistency review

### C1 — Core doctrine is preserved

The set consistently preserves the core Observatory doctrine:

```text
The Observatory stores observations.
The connected LLM interprets at read time.
Accepted conclusions promote out to the owning consumer.
```

The contracts repeatedly route meaning, recommendations, tasks, reports, workflow decisions, accepted conclusions, strategy, and customer-specific business records out to the owning consumer rather than into Observatory.

Result: pass.

---

### C2 — Boundary hierarchy is preserved

The set consistently treats `02-boundaries.md` as higher authority than individual draft contracts.

Repeated boundary themes are aligned:

- rights and retention fail closed;
- customer private data is not stored;
- customer first-party analytics are overlay-only unless future ruling changes law;
- provider output is testimony, not truth;
- provider disagreement must not be averaged into fake truth;
- read tools return shaped evidence packs, not direct SQL/raw rows;
- no implementation begins from contract drafts alone.

Result: pass.

---

### C3 — Non-schema discipline is preserved

The contracts use field lists as contract-level requirements rather than table designs.

The draft set does contain many candidate field names, statuses, and shapes, but those are framed as behavior and validation requirements. That is acceptable for M7 as long as M10 remains the first schema-planning milestone.

Risk to watch:

```text
Future agents may mistake required field lists for approved physical schema.
```

Required mitigation:

```text
M8/M10 handoff language must repeat: contract fields are not schema.
```

Result: pass with caution.

---

### C4 — Provider admission is not accidentally granted

The provider-related contracts preserve the distinction between:

```text
provider candidate
provider testimony
provider observation
provider cross-check
provider admission
provider spend approval
```

DataForSEO remains plausible planning input only. No provider is admitted. No paid pull is authorized. No raw payload retention is approved.

Result: pass.

---

### C5 — Consumer boundary is coherent

The consumer contracts divide responsibilities cleanly:

- `consumer-promotion.md` governs meaning promotion out to consumers.
- `overlay.md` governs read-time/no-storage overlay behavior.
- `searchclarity-consumer-placeholder.md` preserves SearchClarity-specific boundaries without approving the M15 proof workflow.
- `typed-read-tool-skeleton.md` sketches future read-tool shape without implementing M14.

Result: pass.

---

### C6 — Open rulings are not silently resolved

The contracts preserve the major owner-ruling candidates rather than deciding them by implication.

Key unresolved areas remain properly fail-closed:

- persisted Disagreement Ledger;
- AI visibility sample summaries;
- citation handle/report-safe reference behavior;
- customer first-party overlay admission into read tools;
- SearchClarity report-safe language;
- DataForSEO spend/use;
- raw payload retention;
- marketplace capture/report use;
- browser-extension capture;
- recurring capture;
- cross-scope aggregate reads;
- typed read-tool auth/access model.

Result: pass.

---

## Vocabulary alignment notes

### V1 — `scope_class`

Current draft vocabulary is stable:

```text
internal
customer_engagement
market_watch
```

No new scope class should be added without owner ruling.

---

### V2 — rights/retention language

The set consistently uses the rights/retention families established by `scope-rights-retention.md`.

Watch item:

Some later contracts may use shorthand phrases such as `retention_not_cleared` or blocker statuses for examples. Before contract acceptance, review should ensure these are either examples only or mapped cleanly to the retention vocabulary.

---

### V3 — evidence identity layers

The set keeps these layers separate:

```text
capture_id
provider_job_id
raw_payload_id
observation_id
evidence_id
citation_handle
report_safe_reference
external_overlay_reference
```

This is a strong spine and should carry into M8/M10.

---

### V4 — claim and warning language

The set consistently requires warnings for:

```text
freshness
volatility
provider attribution
sample-bound claims
absence claims
rights/retention limits
consumer promotion
incomparability
raw support limits
coverage/blind spots
```

This is ready for M8 hammer extraction.

---

## Owner-ruling review

### Group A — M7 closure-sensitive

Current Group A status from `planning-inbox/owner-ruling-tracker.md`:

| ID | Review finding | Default before ruling |
|---|---|---|
| OR-A1 | Persisted Disagreement Ledger remains unresolved | compute/read-time or fail closed; no persistence by assumption |
| OR-A2 | Sentiment/tone posture remains unresolved | provider-attributed only; mechanically derived sentiment blocked |
| OR-A3 | AI visibility sample summary remains unresolved | read-time only unless materialization test + owner ruling |
| OR-A4 | Citation/report-safe reference behavior remains unresolved | internal evidence IDs stable; report-safe exposure blocked |
| OR-A5 | NC3/NC5 audit disposition appears implemented as planned | owner should confirm or override |
| OR-A6 | Minimum M7 contract set closure remains open | owner should decide whether all 13 drafts are sufficient for M7 closure review |
| OR-A7 | audits folder already ruled | no action here |

Recommended next owner action:

```text
Resolve or explicitly defer OR-A1 through OR-A6 before declaring M7 closed.
```

---

### Groups B–F — later milestone gates

The remaining groups should stay open and fail-closed until their milestones:

- Group B before M8 hammers close;
- Group C before M13 provider/capture admission;
- Group D before M14 API/MCP/read-tool work;
- Group E before M15 SearchClarity proof;
- Group F before M17 overlay/internal telemetry proof.

Do not resolve these early unless the owner explicitly chooses to advance that decision.

---

## M8 readiness review

The draft set is sufficient to begin planning M8 hammer categories, because the contracts now define hostile paths around:

```text
missing scope
unknown rights
unknown retention
customer/private data contamination
strategy/recommendation storage
provider-as-truth claims
provider disagreement averaging
capture package validation failure
raw hash/pointer/drift failure
panel immutability failure
stale evidence current-claim overuse
AI/GEO overclaiming
marketplace boundary violations
overlay persistence
consumer workflow/report leakage
direct SQL/raw row exposure
```

Recommended M8 starting point:

```text
Create an M8 hammer planning document that maps each contract to required hostile-path tests and groups duplicate hammers into a consolidated matrix.
```

Do not implement hammers yet unless M8 explicitly opens that work.

---

## Acceptance blockers before M7 closure

Before declaring M7 complete, the owner should decide:

1. Are all 13 drafted contracts required for M7 closure, or are any merely placeholders for later review?
2. Is the NC3/NC5 disposition accepted as drafted?
3. Is provider disagreement persistence still fail-closed/read-time only?
4. Is AI visibility summary storage still blocked unless a materialization test + ruling allows it?
5. Is report-safe citation exposure still deferred to M15?
6. Are the draft skeleton/placeholder contracts acceptable as M7 outputs even though M14/M15 will own real bindings?

Until answered, the safe status is:

```text
M7 contract drafting complete.
M7 closure review pending.
M8 planning not yet authorized as implementation.
```

---

## No-action confirmations

This review does not authorize:

```text
schema design
migrations
provider admission
provider spend
DataForSEO account funding/use
raw payload retention
marketplace capture
browser extension capture
manual public observation capture
recurring capture
API/MCP implementation
typed read-tool implementation
SearchClarity customer-facing reports
customer data storage
customer first-party analytics storage
strategy/recommendation storage
```

---

## Recommended next steps

### Step 1 — owner M7 ruling pass

Owner reviews the M7 draft-set review and rules on OR-A1 through OR-A6, or explicitly defers them with fail-closed defaults.

### Step 2 — M7 closure note

If owner accepts the draft set as sufficient, create an M7 closure note / decision record that says M7 contract drafting is complete and names what remains deferred.

### Step 3 — M8 hammer planning

Create an M8 hammer matrix planning document that maps the 13 contracts to hammer families and hostile paths.

---

## Final review posture

```text
M7 produced the intended contract skeleton.
The contracts are coherent enough for owner review.
They are not yet accepted doctrine.
They are strong enough to seed M8 hammer planning after owner closure/ruling pass.
```
