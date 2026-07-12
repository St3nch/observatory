# Acceptance Gate Policy v0.1

Status: draft
Authority: M8 hammer acceptance-gate planning draft; not executable proof; not implementation authorization
Milestone: M8 — Hammer Matrix and Acceptance Gates
Source inputs:

- `hammers/hammer-matrix-v0-1.md`
- `research/rg13-hammer-matrix-inputs.md`
- `contracts/README.md`
- all thirteen M7 contract drafts in `contracts/`
- `planning-inbox/owner-ruling-tracker.md`
- `ROADMAP.md`
- `02-boundaries.md`

---

## Purpose

This document turns `hammer-matrix-v0-1.md` into an acceptance-gate policy for M8 planning.

It answers:

```text
Which hammer expectations must exist before M9?
Which hammer expectations must shape M10/M11/M12?
Which hammer expectations are blocked by owner rulings?
Which hammer expectations wait for real implementation surfaces?
```

This policy does not implement hammers and does not mark any hammer as passed.

---

## Non-Authorization Boundary

This policy does not authorize:

```text
schema design
migrations
implementation
provider purchases
paid provider pulls
provider admission
API/MCP implementation
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
```

M8 may define acceptance gates. It may not execute later milestone work.

---

## Acceptance Level Vocabulary

| Level | Meaning | Can satisfy M8 planning? | Can satisfy implementation acceptance? |
|---|---|---:|---:|
| `defined` | Hammer is described with source contracts, failure mode, target milestone, and expected evidence | yes | no |
| `mapped` | Hammer is mapped to milestone gates and blockers | yes | no |
| `blocked_owner_ruling_required` | Hammer depends on unresolved owner ruling | yes, if fail-closed | no |
| `blocked_not_implemented` | Hammer needs a surface that does not exist yet | yes, if later target is named | no |
| `mock_planning_only` | Mock/stub can help design, but is not final proof | maybe, pending OR-B1 | no unless owner rules |
| `fixture_executable` | Hammer can run against controlled fixtures after implementation exists | no, not yet | only after execution |
| `real_surface_executable` | Hammer must run against real implementation/provider/read surface | no, not yet | only after execution |
| `passed` | Hammer executed on required surface and proved expected behavior | no M8 assumption | yes when required milestone executes it |

Core rule:

```text
M8 can close on defined and mapped gates.
Later milestones can close only on executed proof where that milestone requires execution.
```

---

## M8 Closure Standard

M8 is a planning milestone. It may close when the hammer system is clear enough for M9 to choose a first evidence slice without guessing.

M8 closure requires:

- hammer categories H1-H22 defined;
- acceptance result vocabulary defined;
- each hammer mapped to source contracts or boundary law;
- each hammer mapped to future milestone gates;
- owner-ruling dependencies identified;
- M9 first-slice gate rules defined;
- unresolved rulings preserved as fail-closed;
- no schema, migration, provider, API/MCP, dashboard, or customer-data work started.

M8 closure does not require:

- executing hammers;
- passing hammers;
- choosing the first evidence slice;
- designing schema;
- creating test implementation;
- admitting providers;
- creating typed read tools.

---

## M9 Entry Gate

M9 may start first evidence slice definition only after M8 defines enough hammer policy to evaluate candidates.

A proposed M9 first slice must name:

| Requirement | M9 expectation |
|---|---|
| Applicable hammers | Which H1-H22 apply to the slice |
| Non-applicable hammers | Which H1-H22 do not apply yet and why |
| Hard gates for M10 | Which hammers must shape schema planning |
| Hard gates for M12 | Which hammers must execute before first-slice acceptance |
| Provider dependency | Whether provider admission or paid pulls are needed; default no |
| Customer dependency | Whether customer/private data is involved; default no |
| Raw support dependency | Whether raw payload support is needed |
| Read-tool dependency | Whether typed read output is needed |
| Owner-ruling dependency | Which OR items block or constrain the slice |

Default M9 candidate filter:

```text
Prefer a first slice that exercises core observation/provenance/scope/rights/retention/evidence-ID behavior without requiring paid provider pulls, customer private data, marketplace capture, API/MCP implementation, or dashboard work.
```

---

## Gate Groups

### Group 1 — Core Observatory Safety Gates

These gates must shape any first slice, schema plan, implementation foundation, and v1 acceptance.

| Hammer | Gate reason | Earliest required planning | Earliest executable proof |
|---|---|---|---|
| H1 Scope isolation | Prevents scope/customer identity leakage | M9/M10 | M12/M14 |
| H2 Rights fail-closed | Prevents unclear rights becoming permission | M9/M10 | M12/M13 |
| H3 Retention enforcement | Prevents forbidden persistence | M9/M10 | M12/M19 |
| H5 No strategy/recommendation storage | Preserves telescope/astronomer boundary | M9/M10 | M12/M14 |
| H6 CapturePackage validation | Prevents payload-dump loophole | M9/M10 | M12/M13 |
| H12 Raw archive integrity | Prevents raw bypass/corruption | M9/M10 | M12/M13 |
| H15 Evidence ID/citation integrity | Prevents ID layer confusion | M9/M10 | M12/M14 |
| H19 Append-only observations | Prevents historical evidence mutation | M9/M10 | M12 |
| H21 Audit-first enforcement | Prevents unaudited consequential changes | M10/M11 | M12/M19 |

Policy:

- M9 must identify which of these gates are in the first slice.
- M10 must account for every included core safety gate in schema planning.
- M12 cannot accept the first slice until included executable gates pass.

---

### Group 2 — Provider and Capture Admission Gates

These gates are mostly M13+ unless the first slice uses fixtures to simulate provider payloads without real provider calls.

| Hammer | Gate reason | Owner-ruling pressure | Earliest executable proof |
|---|---|---|---|
| H7 Provider spend/duplicate tasks | Prevents unauthorized spend and duplicate paid tasks | OR-C1, OR-C9, OR-C11 | M13 |
| H8 Provider attribution/disagreement | Prevents provider-as-truth and fake averaging | OR-A1 | M14/M16 |
| H11 Marketplace evidence ceiling | Prevents unclear marketplace capture/private seller contamination | OR-C5, OR-C6, OR-C7, OR-E2 | M13/M15 |
| H13 Provider drift/parser safety | Prevents silent corrupt parsing | OR-C2, OR-C4 | M12/M13 |
| H20 Concurrency safety | Prevents double-admission/double-spend/race corruption | OR-B1 for proof level | M12/M13 |

Policy:

- M9 should avoid real provider dependency unless explicitly chosen and owner-approved.
- Provider-adjacent fixture hammers may be planned, but real provider execution remains forbidden until M13.
- Paid capture hammers cannot pass until provider admission and spend approval exist.

---

### Group 3 — Read Tool / API / MCP Gates

These gates are mostly M14+ but must influence M9/M10 decisions if the first slice expects readable evidence packs.

| Hammer | Gate reason | Owner-ruling pressure | Earliest executable proof |
|---|---|---|---|
| H8 Provider attribution/disagreement | Read output must preserve attribution/caveats | OR-A1 | M14/M16 |
| H9 Freshness/volatility/claim use | Read output must not overclaim stale/volatile evidence | OR-B3, OR-D4 | M14/M15 |
| H10 AI/GEO overclaim | Prevents universal AI visibility/trust/causality claims | OR-A2, OR-A3, OR-E3 | M14/M15 |
| H15 Evidence ID/citation integrity | Read output must not confuse evidence/raw/report IDs | OR-A4, OR-D2, OR-D3 | M14/M15 |
| H16 Consumer request/overlay | Read output must promote meaning out, not store it | OR-F1, OR-F3 | M14/M15/M17 |
| H17 LLM/agent access | Prevents SQL/credentials/CRUD/tool escalation | OR-D1 | M14 |
| H18 Hostile weird input | Prevents malformed/path/injection-like bypass | OR-B1 for proof level | M11/M12/M14 |

Policy:

- M8 can define read-tool hammers now.
- M9 may choose a slice that only needs future read-tool planning, not a full read API.
- M14 owns actual typed read API/MCP contract/prototype acceptance.

---

### Group 4 — Consumer / SearchClarity / Overlay Gates

These gates are mostly M15/M17+ and should not drag customer workflow into M9.

| Hammer | Gate reason | Owner-ruling pressure | Earliest executable proof |
|---|---|---|---|
| H4 Customer-private rejection | Prevents customer data contamination | OR-F1, OR-E2 | M15/M17 |
| H9 Freshness/claim use | Prevents stale evidence from supporting unsafe reports | OR-B3, OR-E5 | M15 |
| H10 AI/GEO overclaim | Prevents report language overclaiming AI evidence | OR-E3 | M15 |
| H11 Marketplace evidence ceiling | Keeps marketplace evidence caveated and rights-safe | OR-C5, OR-C6, OR-C7, OR-E2 | M15 |
| H16 Consumer request/overlay | Prevents Observatory from becoming CRM/report/workflow system | OR-D1, OR-F1, OR-F3 | M15/M17 |

Policy:

- Customer/private data must stay out of M9 first-slice candidates by default.
- SearchClarity proof remains M15 and cannot be smuggled into M8/M9.
- Overlay behavior may be planned, but no customer overlay storage is approved.

---

### Group 5 — Operations / Recovery Gates

These gates mostly wait for implementation or operations milestones, but M10/M12 must not design in ways that make them impossible.

| Hammer | Gate reason | Earliest planning impact | Earliest executable proof |
|---|---|---|---|
| H3 Retention enforcement | Purge/no-storage/manifest behavior must be possible | M10 | M12/M19 |
| H12 Raw archive integrity | Hash/pointer/manifest checks must be possible | M10 | M12/M13/M19 |
| H19 Append-only observations | Mutation/correction/purge paths must be separate | M10 | M12/M19 |
| H21 Audit-first enforcement | Consequential changes need same-transaction audit | M10/M11 | M12/M19 |
| H22 Migration rollback/recovery | Migrations must not make evidence fragile | M10 | M19 |

Policy:

- M10 schema planning must include rollback/recovery expectations even though migrations are not run in M10.
- M19 owns full hardening/backup/restore acceptance.

---

## Hard Gate Defaults by Milestone

### M9 — First Evidence Slice Definition

M9 closure should require a first-slice decision that names:

```text
core applicable hammers
excluded/deferred hammers and reasons
owner-ruling blockers
M10 schema-gate hammers
M12 execution-gate hammers
provider/customer/read-tool dependencies
```

M9 should not close on a slice that requires unresolved provider spend, customer private data, marketplace capture, or direct read-tool/API implementation unless the owner explicitly changes the roadmap.

---

### M10 — Schema Planning Only

M10 closure should require schema planning to map against:

```text
H1 scope isolation
H2 rights fail-closed
H3 retention enforcement
H5 no strategy/recommendation storage
H6 CapturePackage validation
H12 raw archive integrity if raw support exists
H14 query panel immutability if panels exist
H15 evidence ID/citation integrity
H19 append-only observations
H21 audit-first expectations
H22 rollback/recovery expectations
```

M10 still may not run migrations.

---

### M11 — Implementation Foundation

M11 closure should require a test-harness strategy for first-slice hammers, especially:

```text
H18 hostile weird input
H20 concurrency if applicable
H21 audit-first if consequential writes exist
```

M11 should not implement provider calls, dashboards, strategy storage, or read-tool exposure beyond its own gate.

---

### M12 — First Evidence Slice Build

M12 closure should require execution of all first-slice hammers that touch the built surface.

At minimum, any real first-slice implementation should prove:

```text
scope isolation
rights fail-closed
retention fail-closed
no strategy/recommendation storage
CapturePackage validation or equivalent admission envelope
evidence ID integrity
append-only behavior
audit-first for consequential changes
hostile weird input rejection
```

If raw support exists, H12 must execute.

If panels exist, H14 must execute.

If concurrent write risk exists, H20 must execute.

---

### M13 — Provider Admission and Controlled Pull Plan

M13 closure should require provider/capture gates before any real provider pull:

```text
H2 rights fail-closed
H6 CapturePackage paid-capture fields
H7 provider spend and duplicate task controls
H8 provider attribution/no truth collapse
H11 marketplace/provider-specific ceiling where applicable
H12 raw hash/pointer/retention posture
H13 provider drift/parser safety
H20 duplicate/race protection for paid tasks
```

Real paid pulls remain forbidden until provider admission, recipe, cost ceiling, stop conditions, and owner approval exist.

---

### M14 — Typed Read API / MCP Contract and Prototype

M14 closure should require read-tool gates:

```text
H1 scope-safe reads
H5 no stored recommendations in output path
H8 provider attribution/disagreement preservation
H9 freshness/volatility/claim caveats
H10 AI/GEO overclaim blocking
H15 evidence ID/citation safety
H16 consumer-promotion/overlay boundaries
H17 no SQL/credentials/CRUD access
H18 hostile input handling
```

M14 must not expose direct SQL, credentials, or table CRUD.

---

### M15 — SearchClarity Proof Workflow

M15 closure should require consumer/report gates:

```text
H4 customer-private rejection
H5 no strategy storage
H9 freshness/report-use caveats
H10 AI/GEO safe claim language
H11 marketplace caveats/rights posture
H15 report-safe citation limits
H16 consumer-promotion boundary
```

SearchClarity report output remains outside Observatory.

---

### M16 — Provider Cross-Check Proof

M16 closure should require:

```text
H8 provider attribution/disagreement preservation
OR-A1 fail-closed posture for persisted disagreement ledger
no averaging into fake truth
no provider winner logic
```

If OR-A1 is still open, persisted disagreement ledger behavior is blocked and compute-on-read posture remains the safe default.

---

### M17 — Owned Telemetry Overlay Proof

M17 closure should require:

```text
H3 no-storage/retention behavior
H4 customer/private rejection
H16 overlay no-persistence and discard proof
```

Customer first-party data remains read-time overlay only unless future owner ruling changes boundary law.

---

### M18 — Recurring Watch Panel Planning

M18 closure should require recurring-capture planning gates:

```text
H2 rights fail-closed
H3 retention/cadence implications
H6 CapturePackage repeated-run validation
H7 budget/stop-condition/no-duplicate controls
H9 freshness/staleness/cadence caveats
H14 panel immutability/versioning
H20 concurrency/duplicate-task controls
```

Recurring capture execution is not automatically approved by M18 planning.

---

### M19 — Hardening, Backup, Recovery, and Operations

M19 closure should require operations gates:

```text
H3 retention cleanup proof
H12 raw hash/pointer integrity after restore
H19 append-only/supersession/purge integrity
H21 audit-first reconciliation
H22 rollback/restore proof
```

---

### M20 — Observatory v1 Acceptance

M20 should review:

```text
all executed hammer outcomes
all unresolved blocked hammers
all owner-ruling dependencies
all provider/customer/read-tool boundaries
whether Observatory stayed a telescope
```

---

## Owner-Ruling Policy

### OR-B1 — Mock/stub level

Default until ruled:

```text
Mock/stub hammers may support planning but cannot satisfy final implementation acceptance.
```

M8 may close with this fail-closed default.

### OR-B2 — Hard gates by milestone

This document proposes milestone hard-gate defaults. Until the owner accepts or revises them:

```text
The mappings are draft policy.
Later milestone closure must explicitly confirm applicable hammers.
```

M8 may close if the gate mapping is clear enough for M9 and unresolved details are carried forward.

### OR-B3 — Freshness class blocking report use

Default until ruled:

```text
Unknown, stale, volatile, or insufficiently sampled evidence cannot support strong current/customer-facing claims without caveat or block.
```

M15 report support remains fail-closed where freshness/claim-use is unresolved.

---

## M9 Candidate Quick Filter

A candidate first slice is M9-friendly if it can answer yes to most of these:

```text
Can it avoid customer private data?
Can it avoid paid provider pulls?
Can it avoid marketplace capture ambiguity?
Can it exercise scope/rights/retention/provenance/evidence IDs?
Can it use fixtures or public/manual observations without pretending they are provider admission?
Can it avoid requiring a dashboard?
Can it avoid requiring full typed API/MCP implementation?
Can it produce enough shape for M10 schema planning and M12 hammers?
```

A candidate is M9-risky if it requires:

```text
DataForSEO paid pull before M13
customer GSC/GA4/Etsy/Shopify private data
marketplace scraping or browser-extension capture
SearchClarity report generation
LLM direct SQL access
strategy/recommendation persistence
recurring capture
```

---

## Anti-Drift Notes

Do not infer from this policy that:

- any hammer has passed;
- mock-only proof is accepted for implementation;
- M9 first slice is chosen;
- schema is authorized;
- migrations are authorized;
- provider pulls are authorized;
- API/MCP work is authorized;
- customer-facing SearchClarity workflow is authorized;
- unresolved owner rulings are resolved.

---

## Final Rule

```text
M8 can decide what must be proven.
M8 cannot pretend it has already been proven.
```
