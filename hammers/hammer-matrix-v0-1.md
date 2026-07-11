# Hammer Matrix v0.1

Status: draft
Authority: M8 hammer planning draft; not executable proof; not implementation authorization
Milestone: M8 — Hammer Matrix and Acceptance Gates
Source inputs:

- `research/rg13-hammer-matrix-inputs.md`
- `contracts/README.md`
- all thirteen M7 contract drafts in `contracts/`
- `planning-inbox/m7-contract-draft-set-review.md`
- `planning-inbox/owner-ruling-tracker.md`
- `02-boundaries.md`

---

## Purpose

This document converts the M7 contract draft set and RG13 hammer inputs into a first M8 hammer matrix.

The matrix defines hostile-path tests Observatory must eventually pass before accepting implementation, provider admission, typed read tools, SearchClarity proof workflows, provider cross-check proof, overlays, recurring capture planning, or v1 acceptance.

This is a planning document. It does not implement hammers.

---

## Non-Authorization Boundary

This hammer matrix does not authorize:

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

---

## Result Vocabulary

Planned hammer results use this vocabulary:

| Result | Meaning | Counts as pass? |
|---|---|---|
| `pass` | Hammer executed against the required surface and proved the expected behavior | yes |
| `fail` | Hammer executed and boundary failed | no |
| `blocked_not_implemented` | Required implementation surface does not exist yet | no |
| `blocked_contract_missing` | Needed accepted contract is missing | no |
| `blocked_owner_ruling_required` | Needed owner ruling is unresolved | no |
| `blocked_provider_not_admitted` | Hammer requires a provider that is not admitted | no |
| `blocked_manual_review_required` | Hammer requires human review before execution | no |

Rules:

- Planned hammers do not pass anything by existing.
- Mock-only hammers may inform planning but do not close implementation acceptance unless explicitly allowed by OR-B1.
- Anything touching an open owner ruling fails closed.

---

## Gate Classes

| Gate class | Meaning |
|---|---|
| `planning_gate` | Must be defined before the target milestone can plan safely |
| `schema_gate` | Must influence M10 schema planning |
| `implementation_gate` | Must pass before implementation acceptance |
| `provider_admission_gate` | Must pass before real provider pull/admission |
| `read_tool_gate` | Must pass before typed read API/MCP acceptance |
| `consumer_gate` | Must pass before SearchClarity/customer-facing proof |
| `operations_gate` | Must pass before hardening/v1 acceptance |

---

## Owner-Ruling Dependencies

Open owner rulings that matter for M8:

| Ruling | Impact |
|---|---|
| OR-A1 | Disagreement Ledger persistence is blocked until owner rules persisted vs compute-on-read |
| OR-A2 | Sentiment/tone hammers must assume provider-attributed-only until ruled otherwise |
| OR-A3 | AI visibility sample summary storage is blocked until ruled |
| OR-A4 | Citation/report-safe reference behavior remains limited until final citation ruling |
| OR-B1 | Mock/stub level for pre-implementation hammers is unresolved |
| OR-B2 | Which hammers are hard gates for each milestone is unresolved |
| OR-B3 | Freshness classes that automatically block customer-facing report use are unresolved |

Fail-closed rule:

```text
If a hammer would need one of these rulings, the hammer can be planned but cannot be considered pass until the ruling is recorded or the hammer is scoped around it.
```

---

## Matrix Summary

| ID | Hammer Area | Primary Contracts | Primary Risk | Gate Classes | Earliest Target |
|---|---|---|---|---|---|
| H1 | Scope isolation | `scope-rights-retention.md`, `consumer-promotion.md`, `typed-read-tool-skeleton.md` | Scope leakage or consumer IDs become Observatory identity | planning, schema, read tool, consumer | M8/M10/M14 |
| H2 | Rights fail-closed | `scope-rights-retention.md`, `capturepackage-v0-1.md` | Unclear rights treated as permission | planning, schema, provider admission | M8/M10/M13 |
| H3 | Retention enforcement | `scope-rights-retention.md`, `raw-archive-provider-drift.md`, `overlay.md` | Data retained when retention forbids it | schema, implementation, operations | M10/M12/M19 |
| H4 | Customer-private rejection | `consumer-promotion.md`, `overlay.md`, `searchclarity-consumer-placeholder.md` | Customer records/private analytics contaminate Observatory | planning, consumer, read tool | M8/M15/M17 |
| H5 | No strategy/recommendation storage | `claim-safety.md`, `consumer-promotion.md`, `typed-read-tool-skeleton.md` | Recommendations/conclusions sneak into storage | planning, schema, implementation, read tool | M8/M10/M14 |
| H6 | CapturePackage validation | `capturepackage-v0-1.md`, `query-panel.md`, `scope-rights-retention.md` | CapturePackage becomes a payload dump loophole | schema, implementation, provider admission | M10/M12/M13 |
| H7 | Provider spend/duplicate tasks | `capturepackage-v0-1.md`, `provider-testimony.md`, `raw-archive-provider-drift.md` | Provider spend or duplicate paid task without approval | provider admission | M13 |
| H8 | Provider attribution/disagreement | `provider-testimony.md`, `provider-cross-check.md`, `claim-safety.md` | Provider output becomes truth or disagreement is averaged | read tool, provider proof | M14/M16 |
| H9 | Freshness/volatility/claim use | `freshness-staleness-volatility.md`, `claim-safety.md` | Stale/volatile evidence supports overstrong claims | read tool, consumer | M14/M15 |
| H10 | AI/GEO overclaim | `claim-safety.md`, `freshness-staleness-volatility.md`, `typed-read-tool-skeleton.md` | Sampled AI evidence becomes universal visibility/trust claim | consumer, read tool | M14/M15 |
| H11 | Marketplace evidence ceiling | `scope-rights-retention.md`, `claim-safety.md`, `searchclarity-consumer-placeholder.md` | Marketplace/private seller evidence captured without clearance | provider/capture, consumer | M13/M15 |
| H12 | Raw archive integrity | `raw-archive-provider-drift.md`, `evidence-id-citation.md`, `capturepackage-v0-1.md` | Raw storage bypasses rights or corrupts evidence | schema, implementation, provider admission | M10/M12/M13 |
| H13 | Provider drift/parser safety | `raw-archive-provider-drift.md`, `provider-testimony.md` | Provider shape drift silently corrupts observations | provider admission, implementation | M12/M13 |
| H14 | Query panel immutability | `query-panel.md`, `capturepackage-v0-1.md` | Panel versions mutate after use | schema, implementation, read tool | M10/M12/M14 |
| H15 | Evidence ID/citation integrity | `evidence-id-citation.md`, `typed-read-tool-skeleton.md`, `searchclarity-consumer-placeholder.md` | Evidence IDs, provider IDs, raw IDs, and report-safe handles get confused | schema, read tool, consumer | M10/M14/M15 |
| H16 | Consumer request/overlay | `consumer-promotion.md`, `overlay.md`, `searchclarity-consumer-placeholder.md` | Consumers use Observatory as CRM/report/workflow/overlay store | read tool, consumer, overlay | M14/M15/M17 |
| H17 | LLM/agent access | `typed-read-tool-skeleton.md`, `consumer-promotion.md` | LLMs get SQL, credentials, CRUD, or mutation paths | read tool | M14 |
| H18 | Hostile weird input | `capturepackage-v0-1.md`, `raw-archive-provider-drift.md`, `typed-read-tool-skeleton.md` | Formatting/injection/path tricks bypass validation | implementation, read tool | M11/M12/M14 |
| H19 | Append-only observations | `evidence-id-citation.md`, `raw-archive-provider-drift.md` | Admitted observations overwritten or backdated | schema, implementation, operations | M10/M12/M19 |
| H20 | Concurrency safety | `capturepackage-v0-1.md`, `query-panel.md`, `raw-archive-provider-drift.md` | Races double-admit, double-spend, or corrupt state | implementation, provider admission | M12/M13 |
| H21 | Audit-first enforcement | `capturepackage-v0-1.md`, `raw-archive-provider-drift.md`, `evidence-id-citation.md` | Consequential change persists without audit evidence | implementation, operations | M12/M19 |
| H22 | Migration rollback/recovery | `raw-archive-provider-drift.md`, `evidence-id-citation.md` | Migrations/restore break evidence integrity | schema, operations | M10/M19 |

---

## Detailed Hammer Requirements

### H1 — Scope Isolation

Must prove:

- missing `scope_id` is rejected;
- unknown `scope_class` is rejected;
- customer email/name/order ID cannot become Observatory identity;
- consumer foreign key cannot become Observatory primary key;
- cross-scope read is blocked by default;
- cross-scope aggregate read is rejected unless a later owner ruling creates a governed exception.

Expected failure mode:

```text
blocked_scope_invalid
blocked_scope_identity_private
blocked_cross_scope_not_allowed
```

Hard gates:

- M10 schema planning must model scope isolation.
- M14 read tools must prove scope-safe reads.
- M15 consumer proof must not leak across customers/projects.

---

### H2 — Rights Fail-Closed

Must prove:

- missing `rights_class` blocks capture/admission;
- `provider_clarification_required` blocks capture/admission;
- `legal_review_required` blocks capture/admission;
- `not_expressly_granted` cannot durable-store by default;
- source-specific restrictions override generic classes;
- marketplace capture with unclear platform rights rejects.

Expected failure mode:

```text
blocked_rights_missing
blocked_rights_unclear
blocked_source_restriction
```

Hard gates:

- M13 provider admission cannot proceed without rights pass.
- M12 implementation cannot accept observations without rights validation.

---

### H3 — Retention Enforcement

Must prove:

- missing `retention_class` blocks admission;
- `no_storage_overlay_only` cannot persist payload;
- `capture_and_purge` requires purge deadline;
- expired retention blocks current use;
- purge updates raw support status;
- manifest-only retention does not retain forbidden payload.

Expected failure mode:

```text
blocked_retention_missing
blocked_no_storage_overlay_only
blocked_retention_expired
```

Hard gates:

- M10 schema planning must account for retention states.
- M19 operations must prove purge/restore behavior.

---

### H4 — Customer-Private Data Rejection

Must reject:

```text
customer records
customer identity
customer order/report records
GSC exports
GA4 exports
Etsy Stats exports
Shopify analytics
seller dashboard screenshots
private conversion data
customer report conclusions
report delivery state
```

Expected failure mode:

```text
blocked_customer_private_data
blocked_customer_workflow_record
blocked_first_party_storage
```

Hard gates:

- M15 SearchClarity proof cannot proceed without customer-private rejection expectations.
- M17 overlay proof must prove no-storage behavior.

---

### H5 — No Strategy / Recommendation Storage

Must reject durable storage of:

```text
recommendation
strategy
action plan
opportunity score as truth
accepted conclusion
experiment plan
agent task decision
report conclusion
best keyword to target
rewrite title to X
```

Also test hidden strategy in:

```text
notes
operator_intent
raw payload metadata
nested payloads
temporary candidate cache
```

Expected failure mode:

```text
blocked_strategy_storage
blocked_recommendation_storage
blocked_conclusion_storage
```

Hard gates:

- M10 schema plan must not include strategy/recommendation tables.
- M14 read tools must return evidence packs, not stored recommendations.

---

### H6 — CapturePackage Validation

Must reject CapturePackage admission when missing or invalid:

```text
scope_id
scope_class
source_family
provider_or_capture_instrument
capture_method
operator_intent
captured_at
rights_class
retention_class
approval_reference when paid
cost ceiling when paid
raw hash when raw retained
```

Must also prove:

- unknown panel version blocks capture;
- candidate observations cannot admit before validation;
- hidden strategy intent is rejected;
- raw retention is blocked unless retention posture allows it.

Expected failure mode:

```text
blocked_capturepackage_invalid
blocked_capturepackage_missing_required_field
blocked_candidate_admission_before_validation
```

Hard gates:

- M12 first evidence slice must satisfy CapturePackage validation.
- M13 provider pull plan must satisfy paid-capture fields.

---

### H7 — Provider Spend / Duplicate Tasks

Must prove:

- paid capture without approval rejected;
- missing dollar ceiling rejected;
- missing task/call ceiling rejected;
- duplicate task rejected before spend;
- stop condition prevents further tasks;
- endpoint outside approved recipe rejected;
- budget exhaustion blocks capture.

Expected failure mode:

```text
blocked_provider_approval_missing
blocked_cost_ceiling_missing
blocked_duplicate_task
blocked_provider_endpoint_not_approved
```

Hard gates:

- M13 cannot admit provider/pull plan without these hammers planned.
- Real provider calls remain forbidden until M13 owner approval.

---

### H8 — Provider Attribution / Disagreement

Must prove:

- provider metric cannot display without provider attribution;
- proprietary difficulty/authority/confidence scores cannot become facts;
- two provider values cannot average into truth;
- provider winner logic is rejected;
- incomparable metrics warn or classify as unresolved;
- provider disagreement is preserved in read output.

Expected failure mode:

```text
blocked_provider_truth_claim
blocked_provider_average_truth
blocked_provider_winner_logic
```

Hard gates:

- M16 provider cross-check proof must satisfy this.
- M14 read tools must preserve provider identity.

OR-A1 note:

- Persisted Disagreement Ledger remains blocked until owner rules.
- Compute-on-read disagreement output can be planned if it does not persist conclusions.

---

### H9 — Freshness / Volatility / Claim Use

Must prove:

- unknown `captured_at` fails current claim;
- stale evidence returns historical-only or recapture-required warning;
- high-volatility evidence requires caveat;
- update-window evidence requires warning;
- current-state claim blocks when freshness is insufficient;
- absence claim requires sample-bound warning.

Expected failure mode:

```text
blocked_freshness_unknown
blocked_current_claim_stale
blocked_absence_claim_uncaveated
```

Hard gates:

- M14 read outputs must expose freshness/caveats.
- M15 report support must not overclaim stale evidence.

OR-B3 note:

- Which freshness classes automatically block customer-facing report use is unresolved.

---

### H10 — AI / GEO Overclaim

Must reject claims such as:

```text
you rank X in AI
you are absent from AI search
AI trusts this source
citation caused the answer
guaranteed AI citations
AI visibility score as truth
```

Must allow only bounded statements about:

```text
sampled mention observation
sampled citation observation
sampled absence observation
surface/prompt/date-bound evidence
```

Expected failure mode:

```text
blocked_ai_visibility_overclaim
blocked_ai_causality_claim
blocked_ai_universal_absence_claim
```

Hard gates:

- M15 GEO/SearchClarity proof must satisfy safe language expectations.

OR-A2/OR-A3 notes:

- Sentiment/tone and AI sample-summary storage remain fail-closed until ruled.

---

### H11 — Marketplace Evidence Ceiling

Must prove:

- Etsy browser-extension capture rejected by default;
- Etsy scraping/crawling rejected by default;
- Fiverr automated capture rejected/not-cleared;
- seller dashboard screenshots rejected or overlay-only;
- marketplace rank claim requires point-in-time caveat;
- marketplace traffic/sales inference rejected.

Expected failure mode:

```text
blocked_marketplace_capture_not_admitted
blocked_marketplace_private_data
blocked_marketplace_inference_overclaim
```

Hard gates:

- M13 marketplace capture admission cannot proceed without source-specific rulings.
- M15 marketplace report support remains caveated and bounded.

---

### H12 — Raw Archive Integrity

Must prove:

- raw retained without rights rejected;
- raw payload without SHA-256 rejected;
- hash mismatch blocks parse/admission;
- missing pointer blocks raw-supported evidence;
- retained payload past retention is blocked/purged;
- forbidden private data in raw payload is rejected.

Expected failure mode:

```text
blocked_raw_rights_invalid
blocked_raw_hash_missing
blocked_raw_hash_mismatch
blocked_raw_private_data
```

Hard gates:

- M12 first slice must verify raw support expectations if raw support exists.
- M13 provider pull must include raw/hash/retention posture.

---

### H13 — Provider Drift / Parser Safety

Must prove:

- new shape quarantined;
- breaking shape blocks admission;
- provider error payload not parsed as observation;
- missing required field does not become fake value;
- field type change blocks or warns;
- parser version recorded;
- drift status surfaces to read tools.

Expected failure mode:

```text
blocked_provider_shape_unknown
blocked_provider_shape_breaking
blocked_provider_error_payload
blocked_parser_required_field_missing
```

Hard gates:

- M13 provider admission must include drift safety expectations.
- M14 read tools must surface drift warnings when relevant.

---

### H14 — Query Panel Immutability

Must prove:

- used panel version cannot be edited in place;
- new query/item requires new panel version;
- run cannot attach to missing panel version;
- stale evidence does not mutate panel version;
- result changes do not create hidden panel mutation;
- panel cannot include recommendation fields.

Expected failure mode:

```text
blocked_panel_version_mutation
blocked_panel_version_missing
blocked_panel_strategy_field
```

Hard gates:

- M9 first-slice selection must know panel/version expectations.
- M12 implementation must keep panel versions immutable once used.

---

### H15 — Evidence ID / Citation Integrity

Must prove:

- provider job ID cannot be evidence ID;
- raw payload ID cannot be report-safe reference;
- evidence ID remains stable across reads;
- withdrawn/superseded/expired evidence status respected;
- customer identity not encoded in citation handle;
- report-safe references do not expose private identifiers.

Expected failure mode:

```text
blocked_id_layer_confusion
blocked_report_safe_reference_unavailable
blocked_private_identifier_in_citation
```

Hard gates:

- M10 schema planning must respect ID layers.
- M14 read tools must expose safe evidence IDs.
- M15 report support cannot expose report-safe handles until allowed.

OR-A4 note:

- Final global/artifact-local/report-safe handle ruling remains open.

---

### H16 — Consumer Request / Overlay

Must prove:

- customer order/report record rejected;
- report conclusion rejected;
- workflow task rejected;
- overlay accepted only as ephemeral input if contract allows;
- overlay not persisted;
- consumer request with private context rejected;
- response includes `consumer_promotion_required` when meaning leaves Observatory.

Expected failure mode:

```text
blocked_consumer_record_storage
blocked_overlay_persistence
blocked_private_consumer_context
```

Hard gates:

- M15 SearchClarity proof must satisfy consumer boundaries.
- M17 overlay proof must satisfy no-storage hammers.

---

### H17 — LLM / Agent Access

Must prove:

- no direct PostgreSQL credentials exposed;
- no arbitrary SQL tool exposed;
- no table CRUD tool exposed;
- no schema mutation tool exposed;
- no direct observation write tool exposed;
- provider spend tool requires human approval;
- read tools return shaped evidence packs only.

Expected failure mode:

```text
blocked_direct_sql
blocked_credentials_exposure
blocked_arbitrary_crud_tool
blocked_direct_observation_write
```

Hard gates:

- M14 typed read API/MCP contract cannot expose SQL/credentials.

---

### H18 — Hostile Weird Input

Must prove:

- path traversal rejected;
- absolute paths rejected where not allowed;
- huge payload rejected or bounded;
- malformed JSON rejected;
- unexpected encoding rejected;
- control characters handled safely;
- duplicate IDs rejected;
- hidden recommendation text in nested objects rejected.

Expected failure mode:

```text
blocked_path_traversal
blocked_payload_too_large
blocked_malformed_payload
blocked_hidden_strategy_payload
```

Hard gates:

- M11/M12 implementation must use bounded input handling.
- M14 read tools must avoid unsafe raw output.

---

### H19 — Append-Only Observations

Must prove:

- admitted observation cannot be overwritten;
- `captured_at` and provenance fields cannot be mutated;
- raw-linked fields cannot be mutated;
- correction creates superseding record, not in-place edit;
- deletion occurs only through governed retention/purge paths.

Expected failure mode:

```text
blocked_observation_mutation
blocked_provenance_mutation
blocked_raw_link_mutation
```

Hard gates:

- M10 schema planning must model append-only expectations.
- M12 first-slice build must satisfy append-only behavior.

---

### H20 — Concurrency Safety

Must prove:

- concurrent identical capture submissions cannot both pass duplicate check;
- concurrent admission of same CapturePackage cannot double-admit;
- purge racing read leaves consistent state;
- concurrent panel-version creation cannot fork same version label.

Expected failure mode:

```text
blocked_concurrent_duplicate_capture
blocked_double_admission
blocked_panel_version_race
```

Hard gates:

- M12 first-slice acceptance must include concurrency proof if the surface can race.
- M13 provider spend safety requires duplicate/race protection.

OR-B1 note:

- Sequential simulation is not enough for final implementation acceptance unless owner rules otherwise.

---

### H21 — Audit-First Enforcement

Must prove:

- admission requires same-transaction audit record;
- purge requires same-transaction audit record;
- supersession requires same-transaction audit record;
- withdrawal requires same-transaction audit record;
- rights/retention-status change requires same-transaction audit record;
- injected audit-write failure rolls back the change;
- read paths create no events.

Expected failure mode:

```text
blocked_missing_required_audit_record
blocked_audit_write_failure
blocked_read_event_side_effect
```

Hard gates:

- M12 implementation acceptance must include audit-first behavior for consequential changes.
- M19 operations must reconcile audit and persisted state.

---

### H22 — Migration Rollback / Recovery

Must prove once migrations exist:

- every migration has tested rollback;
- rollback preserves admitted observations and evidence-ID resolution;
- restore-from-backup proves evidence/raw-pointer/hash integrity;
- failed mid-migration state is recoverable.

Expected failure mode:

```text
blocked_migration_without_rollback
blocked_restore_hash_mismatch
blocked_evidence_resolution_after_restore
```

Hard gates:

- M10 schema plan must specify rollback expectations.
- M19 hardening must prove restore and recovery.

---

## Milestone Gate Mapping

| Milestone | Required M8 output before milestone can close |
|---|---|
| M9 | First-slice selection must name applicable hammers from H1–H22 |
| M10 | Schema plan must map tables/constraints to H1–H6, H12, H14, H15, H19, H22 |
| M11 | Implementation foundation must include test harness strategy for applicable hammers |
| M12 | First evidence slice must execute applicable implementation hammers before acceptance |
| M13 | Provider admission must satisfy H2, H6, H7, H8, H11, H12, H13, H20 |
| M14 | Typed read API/MCP must satisfy H1, H5, H8, H9, H10, H15, H16, H17, H18 |
| M15 | SearchClarity proof must satisfy H4, H5, H9, H10, H11, H15, H16 |
| M16 | Provider cross-check proof must satisfy H8 and OR-A1 fail-closed posture |
| M17 | Overlay proof must satisfy H3, H4, H16 |
| M18 | Recurring watch planning must satisfy H2, H3, H6, H7, H9, H14, H20 |
| M19 | Hardening/operations must satisfy H3, H12, H19, H21, H22 |
| M20 | v1 acceptance must review all executed hammer outcomes and unresolved blockers |

---

## M8 Closure Blockers

M8 should not close until:

- OR-B1 is resolved or explicitly deferred with a fail-closed rule;
- OR-B2 is resolved enough to know hard gates by milestone;
- OR-B3 is resolved or left as a customer/report fail-closed blocker;
- hammer matrix is reviewed against all thirteen M7 contract drafts;
- hammers are indexed in `hammers/README.md`;
- `ACTIVE_CONTEXT.md` and `NEXT_SESSION_HANDOFF.md` are updated when M8 closes.

---

## Anti-Drift Notes

Do not infer from this matrix that:

- hammers are implemented;
- hammers have passed;
- provider pulls are allowed;
- schema design is allowed;
- M9 first-slice selection is complete;
- customer-facing reports are safe;
- typed read tools exist;
- unresolved owner rulings are resolved.

---

## Final Rule

```text
If Observatory claims a boundary, M8 must try to break it.
Happy-path tests do not prove Observatory safe.
```
