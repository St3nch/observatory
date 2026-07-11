# Contract - SearchClarity Consumer Placeholder

Status: draft placeholder
Authority: placeholder contract (does not bind customer-facing behavior; subordinate to `02-boundaries.md` and future M15 owner approvals)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg12-consumer-contract-inputs.md`; supporting inputs from `contracts/consumer-promotion.md`, `contracts/overlay.md`, `contracts/evidence-id-citation.md`, `contracts/claim-safety.md`, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This placeholder marks the boundary for future SearchClarity consumption of Observatory evidence without prematurely creating customer-facing report language, service claims, customer workflows, or implementation contracts.

SearchClarity may later use Observatory evidence packs to support SEO/GEO/SERP/marketplace/video visibility proof work. But SearchClarity owns customer identity, reports, recommendations, deliverables, orders, consent records, private analytics, report delivery history, and accepted customer-facing conclusions.

This placeholder exists so M7 can preserve the consumer boundary now while leaving final SearchClarity proof workflow to M15.

---

## Governing boundaries

This placeholder operationalizes these rules:

- Observatory stores observations, not conclusions.
- SearchClarity owns customer records, orders, reports, recommendations, and deliverables.
- Customer first-party analytics remain outside Observatory storage.
- Evidence IDs and citation handles support proof; they do not become customer report records by themselves.
- Final report-safe language is not admitted by M7.
- Customer-facing claims require future M15 validation.
- Rights, retention, freshness, provider attribution, absence, and sample-bound caveats must be preserved.

On conflict, `02-boundaries.md`, accepted contracts, and future M15 owner approvals win.

---

## Definitions

### SearchClarity

The customer-facing service consumer that may later request Observatory evidence packs for visibility audits, report support, marketplace observations, SERP/GEO evidence, and provider-attributed metrics.

### SearchClarity customer record

Any customer identity, order, report, private file, consent record, communication, payment, delivery, revision, or engagement-management record.

These remain outside Observatory.

### SearchClarity report artifact

A customer-facing deliverable owned by SearchClarity. It may cite Observatory evidence if future M15 contracts allow report-safe references, but the report itself is not an Observatory record.

### SearchClarity recommendation

Any suggested action, strategy, title rewrite, keyword target, content change, listing edit, competitive response, or customer-facing advice.

Recommendations belong to SearchClarity, not Observatory.

### Report-safe reference

A future customer-facing evidence reference class. Its final behavior remains blocked until M15 decides whether it is separate from, derived from, or mapped to internal evidence IDs/citation handles.

---

## Contract rules

### R1. This is a placeholder, not customer-facing approval

This contract does not approve SearchClarity report templates, customer-facing language, automated delivery, customer onboarding, or customer data handling.

### R2. SearchClarity may request evidence packs later

A future SearchClarity read path may request scoped evidence packs only after M14/M15 contracts define typed read tools, access behavior, report-safe references, and proof workflow boundaries.

### R3. SearchClarity owns all customer records

The following must remain outside Observatory:

```text
customer identity
customer email/name/company/shop identity as business record
orders
report records
private files
consent records as business records
report delivery history
revision history
payment records
customer messages
private analytics exports
seller dashboard data
```

### R4. SearchClarity owns recommendations and reports

Any recommendation, report paragraph, strategy statement, task, customer-facing action, accepted conclusion, or deliverable belongs to SearchClarity.

Observatory may provide evidence, caveats, and support warnings only.

### R5. Customer first-party data is overlay-only

SearchClarity may later supply customer first-party data as a read-time overlay only if the overlay contract and future M15/M17 hammers admit that path.

It must not be stored as Observatory evidence.

### R6. Evidence support must preserve caveats

Any SearchClarity evidence pack must preserve:

```text
rights_retention_warning
freshness_warning
provider_attribution_required
sample_bound_warning
absence_warning
incomparability_warning
consumer_promotion_required
raw_support_status
```

SearchClarity may decide how to explain these caveats in customer-facing language after M15 validation.

### R7. Report-safe references remain blocked

Customer-facing report-safe evidence references are not admitted by this placeholder.

Until M15 resolves report-safe reference behavior, internal evidence IDs/citation handles remain planning/support handles, not final customer-facing references.

### R8. SearchClarity requests must be customer-clean

A future request may include non-private scoped locators, claim intent, requested evidence families, and allowed output use.

It must not include unnecessary customer private data.

### R9. SearchClarity cannot use Observatory as file storage

Customer screenshots, exports, PDFs, reports, notes, and private files must not be stored in Observatory as raw payloads, overlays, or evidence under this placeholder.

### R10. SearchClarity cannot use Observatory as workflow state

Observatory must not store:

```text
Fiverr/Upwork order state
report delivery state
revision state
customer approval state
recommendation acceptance
customer tasks
service package state
client notes
```

### R11. SearchClarity cannot launder strategy into evidence metadata

Fields like `scope_label`, `operator_intent`, `panel_purpose`, `include_reason`, `claim_intent`, or `notes` must not contain recommendations, report conclusions, or strategy rationale.

### R12. SearchClarity evidence requests must fail closed

If scope, rights, retention, source admission, freshness, provider attribution, overlay handling, customer privacy, or report-safe exposure is unclear, the SearchClarity path remains blocked or returns evidence with caveats only.

---

## Required fields / shapes

These are future contract-level requirements, not schema/API approval.

### Future SearchClarity request shape

```text
consumer_name: searchclarity
consumer_request_id
consumer_request_type
scope_id or scope_request
scope_class
consumer_reference_kind
consumer_reference_value if allowed and non-private
requested_evidence_families
query_panel_id or query_panel_request if applicable
claim_intent
current_or_historical_use
report_support_context if non-private
freshness_requirement
overlay_supplied
overlay_type if applicable
allowed_output_use
```

### Future SearchClarity evidence response shape

```text
evidence_pack_id or response_id
evidence_ids
citation_handles if available
report_safe_reference if later admitted
scope_id
scope_class
source_families
provider_or_capture_instruments
query_panel_id
query_panel_version_id
panel_run_id
captured_at values
provider_reported_times if available
freshness_status
volatility_class
rights_retention_warning
claim_use_warning
provider_attribution_required
sample_bound_warning
absence_warning
recapture_recommendation
raw_support_status
consumer_promotion_required
```

### Placeholder statuses

```text
placeholder_only
blocked_until_m15
ready_for_m15_design_input
report_safe_reference_blocked
overlay_blocked_until_hammered
customer_data_rejected
```

---

## Fail-closed behavior

- Customer private data in a request blocks or requires consumer-side reduction.
- Customer first-party analytics storage is rejected.
- Report-safe reference exposure is blocked until M15.
- Report language generation is blocked until M15.
- Recommendation storage is rejected.
- Workflow-state storage is rejected.
- Overlay use is blocked until overlay/read-tool hammers admit the path.
- Unknown rights/retention/source admission blocks evidence use.
- Evidence without required caveats cannot support SearchClarity output.

---

## Forbidden patterns

This placeholder forbids:

```text
SearchClarity customer table in Observatory
SearchClarity order/report table in Observatory
SearchClarity recommendations in Observatory
customer report paragraph stored as Observatory evidence
customer GSC/GA4/Etsy/Shopify/YouTube exports stored as evidence
Fiverr/Upwork workflow state in Observatory
report-safe citation exposure before M15
customer screenshots stored as raw archive
AI visibility score sold from Observatory evidence
provider disagreement turned into customer recommendation inside Observatory
```

Fake-mustache variants are also forbidden:

```text
searchclarity_customer_scope_id
report_strategy_cache
customer_audit_result_record
recommendation_evidence_bundle
report_delivery_evidence
client_private_overlay_archive
```

---

## Examples

### Valid future request shape - public evidence support

```text
consumer_name: searchclarity
consumer_request_type: report_support_request
scope_class: customer_engagement
requested_evidence_families:
  - public_serp_observation
  - provider_metric_claim
claim_intent: report_support_request
allowed_output_use: evidence_pack_for_consumer_owned_report
```

Why valid as planning shape:

- It requests evidence support.
- It does not ask Observatory to store the report or recommendation.
- Customer details are not embedded.

### Invalid - store customer order/report state

```text
consumer_name: searchclarity
store_order_id: fiverr_order_123
report_status: delivered_to_customer
recommendation_status: accepted
```

Why invalid:

- This is SearchClarity workflow state.
- Observatory is not the customer/report system.

### Valid future overlay posture

```text
overlay_source_type: customer_gsc_export
overlay_no_storage_assertion: true
overlay_discard_required: true
claim_intent: report_support_request
```

Why valid only as future posture:

- Overlay is no-storage and read-time only.
- The actual path remains blocked until overlay/M15 hammers admit it.

### Invalid - final report language stored by Observatory

```text
stored_observatory_record: Your Etsy listing should target lavender soy candle gift because it has strong opportunity.
```

Why invalid:

- It is recommendation/report language.
- It belongs to SearchClarity.

---

## Owner-ruling candidates

M15 or owner ruling must decide:

- final SearchClarity evidence-pack request/response shape;
- whether report-safe references are artifact-local, derived, or separate;
- what evidence references may appear in customer-facing reports;
- whether customer first-party overlays are accepted into SearchClarity proof workflow;
- how SearchClarity preserves caveats in report language;
- whether screenshots can be used as no-storage read-time inputs;
- how customer consent is represented without becoming Observatory's customer system;
- whether any SearchClarity proof workflow needs additional scope classes.

Default until ruled:

```text
Placeholder only.
No customer-facing report-safe behavior.
No customer data storage.
No overlay execution.
No recommendation/report storage.
```

---

## Deeper-research blockers

Relevant blockers:

- DR9 - SearchClarity customer-facing report language validation.
- DR10 - Customer first-party overlay contract.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR16 - Consumer authentication / authorization model.

This placeholder is not sufficient for implementation or launch.

---

## Hammer expectations

M8/M15 must prove:

- customer IDs/order/report IDs cannot become Observatory identity;
- customer reports cannot be stored as Observatory evidence;
- recommendations cannot be stored in Observatory;
- customer analytics are overlay-only/no-storage;
- report-safe references fail closed before admission;
- SearchClarity request context is customer-clean;
- evidence packs preserve caveats;
- consumer promotion warnings are present when output approaches report/recommendation language;
- direct SQL/raw rows are not exposed to SearchClarity.

Relevant categories:

```text
H1 scope isolation
H4 customer-private rejection
H5 no recommendation storage
H8 provider attribution and disagreement
H9 freshness / volatility
H10 AI/GEO overclaim rejection
H11 marketplace boundary enforcement
H15 evidence/citation integrity
H16 overlay no-storage
H17 LLM/agent access boundary
H21 audit-first enforcement
```

---

## Feeds milestones

This placeholder feeds:

- M8 - consumer boundary hammers.
- M14 - typed read API / MCP contract.
- M15 - SearchClarity proof workflow.
- M17 - overlay/internal telemetry proof.

---

## Non-authorizations

This placeholder does not authorize:

```text
SearchClarity implementation
customer onboarding
customer data storage
report generation
report delivery
report-safe reference exposure
service claim language
provider pulls
paid spend
API/MCP implementation
schema design
migrations
```

---

## Change log

```text
0.1 - 2026-07-10 - initial placeholder from RG12 and M7 consumer contracts; final behavior deferred to M15
```
