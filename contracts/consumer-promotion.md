# Contract - Consumer Promotion

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg12-consumer-contract-inputs.md`, with supporting inputs from `research/rg2-scope-rights-retention-model.md`, `research/rg3-evidence-id-citation-model.md`, `research/rg4-query-panel-model.md`, `research/rg5-freshness-staleness-volatility.md`, `research/rg8-claim-safety-report-language.md`, `research/rg9-provider-cross-check-disagreement-model.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg11-raw-archive-provider-drift.md`, and existing M7 contracts
Supersedes / superseded by: none

---

## Purpose

This contract governs how Observatory evidence may be requested by downstream consumers and how any interpreted meaning, recommendation, workflow action, report language, or accepted conclusion must promote out of Observatory to the owning consumer.

It exists before schema, API/MCP implementation, consumer integrations, or SearchClarity proof work so Observatory does not become a customer database, strategy store, report system, agent workflow system, or conclusion database by accident.

Core rule:

```text
Evidence comes from Observatory.
Meaning promotes back to the consumer.
```

---

## Governing boundaries

This contract operationalizes these project rules:

- Observatory stores observations, not conclusions.
- The connected LLM interprets at read time.
- Accepted conclusions promote out to the owning consumer.
- Customer records, order records, report records, private files, consent records, delivery history, and private analytics stay outside Observatory.
- Customer first-party data is read-time overlay only unless a future owner ruling changes law.
- Evidence IDs cite observations, not consumer conclusions.
- Provider output remains attributed testimony.
- Rights, retention, freshness, and claim-safety caveats must travel with evidence.
- LLMs and agents receive shaped evidence packs, not direct SQL, credentials, or raw ungoverned payloads.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### `consumer`

A downstream system, service, governance process, or operator workflow that asks Observatory for governed evidence.

Initial consumer labels:

```text
searchclarity
neon_ronin
kaizen
internal
```

Adding a new durable consumer label requires owner ruling or later accepted consumer contract.

---

### `consumer_request`

A bounded request for evidence, evidence support, or claim-use safety from Observatory.

A consumer request is not a customer order, customer report, workflow task, accepted decision, recommendation, or strategy record.

---

### `evidence_pack`

A shaped response from Observatory containing observations, evidence IDs, citation handles where allowed, provenance, freshness, source, rights, retention, and claim-use warnings.

An evidence pack is not an accepted conclusion.

---

### `consumer_promotion`

The required handoff where interpreted meaning, recommendations, reports, task decisions, accepted conclusions, or workflow actions are stored and governed by the owning consumer, not Observatory.

---

### `consumer_owned_output`

Any durable output that contains meaning beyond observed evidence.

Examples:

```text
SEO recommendation
customer report paragraph
review queue item
implementation task packet
accepted decision
workflow action
report delivery state
strategy note
```

---

### `external_consumer_reference`

A minimal non-private locator supplied by a consumer to correlate a request or output with consumer-side systems.

It must not become Observatory identity, customer identity, or a foreign key that makes Observatory dependent on another business database.

---

## Contract rules

### R1. Observatory returns evidence support, not consumer meaning

Observatory may return evidence packs and claim-use warnings.

Observatory must not store or own the final recommendation, strategy, report paragraph, workflow task, accepted decision, or customer-facing conclusion.

---

### R2. Consumer identity is a boundary label, not customer identity

A consumer label such as `searchclarity`, `neon_ronin`, `kaizen`, or `internal` may identify the downstream owner of meaning.

It must not encode customer names, customer emails, report numbers, order IDs, private account IDs, or workflow/task IDs as Observatory identity.

---

### R3. Consumer request IDs are external locators only

A consumer may pass a request locator if allowed, but Observatory must not treat it as:

- customer record identity;
- report system identity;
- order identity;
- workflow task identity;
- evidence ID;
- citation handle;
- scope identity.

---

### R4. Consumer requests must declare claim intent

Consumer requests that ask for evidence support must identify the intended claim shape or use category, such as:

```text
historical_observation_claim
current_state_claim
comparative_claim
absence_claim
provider_metric_claim
report_support_request
```

Claim intent is used to select evidence and warnings. It does not authorize Observatory to store the final claim.

---

### R5. Forbidden consumer intents must be rejected or redirected

Forbidden request intents include:

```text
store_recommendation
make_customer_decision
choose_strategy
publish_report
trigger_agent_action
store_report_paragraph
store_customer_order
store_private_analytics
```

If a consumer asks for one of these, Observatory must fail closed or redirect the work to the consumer layer.

---

### R6. Evidence packs must preserve caveats

A consumer-facing evidence pack must include applicable warnings and support metadata, including:

```text
claim_use_warning
freshness_warning
rights_retention_warning
provider_attribution_required
sample_bound_warning
absence_warning
incomparability_warning
recapture_recommendation
consumer_promotion_required
raw_support_status
```

Caveats must not be stripped to make consumer output cleaner.

---

### R7. Consumer promotion is required for meaning-bearing outputs

Any output that interprets, recommends, decides, prioritizes, explains business meaning, creates a task, or becomes customer-facing must promote out.

Examples:

| Meaning-bearing output | Owning consumer |
|---|---|
| SEO recommendation | `searchclarity` |
| customer report paragraph | `searchclarity` |
| review queue item | `neon_ronin` |
| agent task decision | `neon_ronin` |
| implementation task packet | `kaizen` |
| accepted decision | `kaizen` or owning consumer |
| report delivery state | `searchclarity` |

---

### R8. SearchClarity owns customer-facing work

SearchClarity owns:

- customer identity;
- customer orders;
- customer reports;
- private files;
- consent records as business records;
- private analytics inputs;
- report conclusions;
- recommendations;
- deliverables;
- delivery history.

Observatory may support SearchClarity with governed evidence packs only after later SearchClarity/report-safe contracts admit that path.

---

### R9. Neon Ronin owns workflow and agent action state

Neon Ronin owns:

- workspace state;
- review queues;
- agent task records;
- schedules;
- action decisions;
- publishing/delivery status;
- project-management workflow.

Observatory must not create or store Neon Ronin workflow state.

---

### R10. Kaizen owns governance conclusions

Kaizen owns:

- governance records;
- accepted decisions;
- task packets;
- implementation returns;
- roadmap authority;
- project doctrine.

Observatory may provide evidence handles and evidence packs for Kaizen review, but Kaizen decisions remain Kaizen-owned.

---

### R11. Internal does not bypass source admission

Internal consumer requests may ask for owner-owned public-surface evidence or future internal telemetry only when the source family is admitted.

Owner-controlled does not mean automatically admitted, rights-cleared, retention-cleared, or schema-cleared.

---

### R12. Customer first-party overlays are not consumer promotion artifacts

Customer first-party overlays are read-time inputs under future overlay contract rules.

Overlay values must not be stored as Observatory observations, assigned evidence IDs, promoted into Observatory evidence, or persisted as report support.

The consumer owns any conclusion drawn from overlay alignment.

---

### R13. Consumer outputs must cite evidence, not raw internals

Consumer-owned outputs may cite Observatory evidence only through allowed evidence IDs, citation handles, or report-safe references once later contracts admit those references.

Forbidden citation surfaces:

- provider job IDs;
- raw payload IDs;
- raw file paths;
- database row IDs;
- customer/private IDs;
- query panel IDs alone;
- consumer request IDs alone.

---

### R14. Report-safe references remain blocked until M15

This contract does not approve customer-facing report references or final report language.

M15 must decide SearchClarity proof workflow, report-safe citation behavior, customer-facing caveat language, and final deliverable boundaries.

---

### R15. Consumer promotion must not mutate evidence

When a consumer creates a recommendation, task, decision, or report conclusion, it must not rewrite Observatory observations to make the conclusion look stronger.

Evidence remains append-only/status-aware under the evidence ID and raw/archive contracts.

---

### R16. Consumer-owned conclusions may reference evidence support

A consumer may store a conclusion that references Observatory evidence IDs or citation handles, if its own governance allows it.

Observatory must not store the reverse conclusion as an Observatory fact.

---

### R17. Cross-scope aggregate consumer reads are blocked by default

Consumer promotion must not use Observatory as a cross-customer aggregate intelligence store unless a future owner ruling and contract explicitly admit that behavior.

Default posture:

```text
single-scope or explicitly permitted scope-bound evidence only
```

---

### R18. Direct SQL and raw mystery rows are forbidden consumer interfaces

Future consumers must receive shaped evidence packs through typed read tools/contracts.

They must not receive direct SQL access, raw unmanaged rows, credentials, raw private paths, or write access that bypasses capture/evidence contracts.

---

## Required fields / shapes

These are contract-level requirements, not schema or API approval.

### Consumer request shape

```text
consumer_name
consumer_request_id
consumer_request_type
scope_id or scope_request
scope_class
consumer_reference_kind
consumer_reference_value if allowed
requested_evidence_families
query_panel_id or query_panel_request if applicable
claim_intent
current_or_historical_use
report_or_workflow_context if non-private
freshness_requirement
overlay_supplied
overlay_type if applicable
overlay_freshness_metadata if applicable
allowed_output_use
```

Rules:

- Consumer request shape is planning-only until M14/M15.
- Request context must not contain customer private data.
- `consumer_reference_value` must be minimal and non-private.
- `claim_intent` must not become final claim storage.

---

### Evidence response shape

```text
evidence_pack_id or response_id
evidence_ids
citation_handles if available
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

Rules:

- Evidence response shape is planning-only until M14 typed read-tool work.
- Evidence packs are support artifacts, not accepted conclusions.
- Consumer promotion warnings must travel with evidence when meaning-bearing output is likely.

---

### Promotion handoff shape

A consumer-owned output that cites Observatory evidence should preserve, on the consumer side:

```text
consumer_name
consumer_owned_output_id
consumer_owned_output_type
observatory_evidence_ids or citation_handles
observatory_caveats_preserved
consumer_author_or_agent
consumer_review_status
consumer_acceptance_status
consumer_storage_location
```

This shape belongs to the consumer, not Observatory.

Observatory may be referenced by evidence ID, but must not persist the consumer-owned output as Observatory evidence.

---

## Consumer-owned output classes

| output_class | Owner | Observatory posture |
|---|---|---|
| `seo_recommendation` | SearchClarity / Strategy layer | promote out |
| `customer_report_paragraph` | SearchClarity | promote out |
| `report_deliverable` | SearchClarity | promote out |
| `review_queue_item` | Neon Ronin | promote out |
| `agent_task_record` | Neon Ronin | promote out |
| `implementation_task_packet` | Kaizen | promote out |
| `accepted_decision` | Kaizen or owning consumer | promote out |
| `workflow_action` | Neon Ronin / owning consumer | promote out |
| `strategy_note` | Strategy layer / owning consumer | promote out |
| `evidence_pack` | Observatory | allowed as governed evidence support |
| `observation` | Observatory | allowed if admitted |

---

## Fail-closed behavior

### Unknown consumer

If `consumer_name` is unknown or not admitted, request fails closed.

### Customer/private request content

If a request contains customer private data, private analytics, report text, order IDs, or workflow state, Observatory must reject, scrub, or redirect before storage.

### Recommendation-like request

If a request asks Observatory to recommend, decide, prioritize, or create a workflow action, the request must fail closed or return evidence-only support with `consumer_promotion_required`.

### Missing claim intent

If claim intent is missing and the request needs claim-use evaluation, return evidence only with conservative warnings or block claim support.

### Missing caveats

If caveats cannot be produced, the evidence pack must not be used for report-support or strong consumer claims.

### Unknown scope or rights/retention

If scope, rights, retention, source admission, freshness, or evidence status is unclear, response fails closed under the relevant contract.

### Report-safe exposure requested too early

If a consumer asks for customer-facing report-safe references before M15 admission, block or return internal-only evidence references.

---

## Forbidden patterns

This contract forbids:

```text
Observatory as customer CRM
Observatory as report system
Observatory as strategy store
Observatory as task queue
Observatory as review queue
Observatory as SearchClarity order system
Observatory as Neon Ronin workflow state
Observatory as Kaizen decision store
Observatory as customer first-party analytics store
Observatory as recommendation memory
Observatory as report paragraph archive
Observatory as agent action logger
Observatory as raw customer file storage
```

Fake-mustache variants are also forbidden:

```text
evidence_interpretation_cache
recommendation_support_table
consumer_strategy_snapshot
report_draft_evidence
agent_decision_observation
customer_context_scope
workflow_context_payload
accepted_conclusion_metadata
```

---

## Examples

### Valid example - SearchClarity evidence request

```text
consumer_name: searchclarity
consumer_request_type: report_support_request
scope_class: customer_engagement
requested_evidence_families: public_serp_observation
claim_intent: historical_observation_claim
allowed_output_use: evidence_support_only
```

Why valid:

- It asks for evidence support.
- It keeps customer records outside Observatory.
- Report conclusions remain SearchClarity-owned.

---

### Invalid example - SearchClarity report storage

```text
consumer_name: searchclarity
consumer_request_type: store_customer_report
report_paragraph: Your listing should change its title because...
```

Why invalid:

- Customer report text and recommendations belong to SearchClarity.
- Observatory stores observations, not report paragraphs.

---

### Valid example - Neon Ronin asks for evidence for a review item

```text
consumer_name: neon_ronin
consumer_request_type: evidence_for_review
claim_intent: comparative_claim
allowed_output_use: create_consumer_owned_review_item
```

Why valid:

- Observatory may return evidence and caveats.
- Neon Ronin owns any review queue item.

---

### Invalid example - Observatory creates agent task

```text
consumer_name: neon_ronin
consumer_request_type: trigger_agent_action
requested_action: update product title
```

Why invalid:

- Agent action belongs to Neon Ronin or another consumer.
- Observatory may provide supporting evidence only.

---

### Valid example - Kaizen cites evidence in planning

```text
consumer_name: kaizen
consumer_request_type: evidence_citation_for_decision_review
claim_intent: historical_observation_claim
evidence_ids: ev_market_serp_20260710_d83a10
```

Why valid:

- Kaizen owns the decision.
- Observatory owns only the evidence handle and caveats.

---

### Invalid example - customer analytics as evidence

```text
consumer_name: searchclarity
overlay_type: customer_gsc_export
requested_action: store_as_observatory_evidence
```

Why invalid:

- Customer first-party data is overlay-only.
- Overlay values do not receive Observatory evidence IDs.

---

## Owner-ruling candidates

Open rulings carried forward:

- Which consumer labels are admitted beyond the initial set.
- Whether any consumer may request cross-scope aggregate reads.
- Whether SearchClarity report-safe citation handles are internal artifact-local or customer-facing.
- Whether consumer-owned output IDs may be referenced in Observatory audit logs.
- Whether a strategy layer / Evidence-to-Action Gateway becomes an admitted consumer.
- Whether Neon Ronin agents may call Observatory read tools directly or only through a strategy layer.
- Whether customer first-party overlays are admitted to read tools under M17/M15 conditions.

Default until ruled:

```text
No cross-scope aggregate reads.
No durable consumer conclusions in Observatory.
No customer-facing report-safe references.
No direct agent write path.
No customer private overlay storage.
```

---

## Deeper-research blockers

This contract is blocked from implementation-specific behavior by:

- DR9 - SearchClarity customer-facing report language validation.
- DR10 - Customer first-party overlay contract.
- DR11 - Owned internal first-party telemetry.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR16 - Consumer authentication / authorization model.
- Future strategy layer / Evidence-to-Action Gateway planning.

M14 owns typed read-tool behavior.
M15 owns SearchClarity proof workflow and customer-facing report boundary.
M17 owns owned telemetry / overlay proof if still on roadmap.

---

## Hammer expectations

M8+ hammers must prove:

- consumer request with customer private data is rejected;
- consumer request asking for recommendation storage is rejected;
- consumer request asking for agent action is rejected;
- consumer request using customer/order/report ID as scope identity is rejected;
- evidence pack includes required caveats;
- consumer promotion warning appears when output is meaning-bearing;
- SearchClarity report-safe references fail closed before M15;
- Neon Ronin task storage is not written to Observatory;
- Kaizen accepted decisions are not stored as Observatory observations;
- overlays remain no-storage;
- consumer request cannot bypass source/rights/retention/freshness gates;
- direct SQL/raw mystery row consumer access is unavailable;
- cross-scope aggregate read fails closed without owner ruling.

Relevant hammer categories:

```text
H1 scope isolation
H2 rights fail-closed
H3 retention fail-closed
H4 customer/private data rejection
H5 no recommendation storage
H8 provider attribution/disagreement
H9 freshness/volatility
H15 evidence/citation integrity
H16 consumer request / overlay no-storage
H17 LLM/agent access boundary
H18 hostile input
H19 append-only/no silent overwrite
H21 audit-first enforcement
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates.
- M10 - Schema Planning Only.
- M14 - Typed Read API / MCP Contract and Prototype.
- M15 - SearchClarity Proof Workflow.
- M17 - Owned Telemetry Overlay Proof.
- Future strategy layer / Evidence-to-Action Gateway planning.

---

## Non-authorizations

This contract does not authorize:

- schema design;
- migrations;
- API/MCP implementation;
- consumer authentication implementation;
- SearchClarity report generation;
- customer-facing report language;
- report-safe citation exposure;
- customer data storage;
- overlay storage;
- Neon Ronin workflow integration;
- Kaizen decision writes;
- strategy layer implementation;
- agent actions;
- provider admission;
- paid pulls;
- capture runners.

---

## Final rule

```text
Consumers may ask Observatory for governed evidence packs.
Consumers may not use Observatory as their customer database, workflow store, strategy store, or report system.
Evidence comes from Observatory.
Meaning promotes back to the consumer.
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG12 and existing M7 evidence contracts
```
