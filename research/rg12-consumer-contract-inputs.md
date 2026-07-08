# RG12 — Consumer Contract Inputs

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What must downstream consumers provide to and receive from Observatory without turning Observatory into their customer database, strategy store, or workflow system?

---

## Sources checked

Local/current sources checked during RG12:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg8-claim-safety-report-language.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `research/deep-research-backlog.md`

No current external source was required for RG12 because this gate defines internal consumer-boundary contract inputs. Consumer-specific report/service validation remains deeper work, especially for SearchClarity.

---

## Current source-grounded findings

### F1 — Consumers own conclusions, workflows, and customer records

`02-boundaries.md` says Observatory stores observations, not conclusions. Accepted conclusions promote out to the owning consumer.

It also says SearchClarity owns customer identity, order/report records, private files, consent records, report delivery history, and private first-party analytics inputs.

Implication:

- Consumer contracts must clearly distinguish evidence requests from workflow records.
- Observatory may provide evidence packs.
- The consumer owns recommendations, reports, accepted conclusions, task decisions, and customer workflows.

---

### F2 — Customer first-party data is overlay-only

`02-boundaries.md` says customer first-party series may be supplied to read tools as read-time overlays, and Observatory does not store the customer first-party series.

Implication:

- Consumer contracts must define ephemeral overlay behavior.
- Overlays must include freshness/source context supplied by the consumer.
- Observatory must not assign durable evidence IDs to customer private overlays under current law.

---

### F3 — Evidence packs need claim-use warnings

RG8 says read tools should return evidence plus claim-use warnings, freshness, volatility, provider attribution requirements, sample-bound warnings, rights/retention warnings, and consumer-promotion requirements.

Implication:

- Consumer contracts must define output shape for safe evidence packs.
- The consumer must not treat evidence packs as ready-made recommendations.
- The consumer must preserve caveats when using Observatory evidence in reports or decisions.

---

### F4 — Scope is local to Observatory and not a consumer foreign key

RG2 says scope is flat, Observatory-owned, and not a customer/project foreign key.

Implication:

- Consumer contracts may pass external locators, but Observatory owns `scope_id`.
- Consumer IDs must not become Observatory identity or customer database keys.
- Consumer references should be minimal and non-private.

---

### F5 — CapturePackage and raw support must stay governed

RG10 and RG11 say capture attempts and raw payloads require scope, rights, retention, provenance, hashes/pointers, validation, and drift handling.

Implication:

- Consumers cannot submit arbitrary payloads and ask Observatory to store them.
- Consumer-submitted evidence or overlays require a source/capture contract.
- Raw payload support must obey source-family rules.

---

## Consumer categories

### `searchclarity`

Purpose:
Customer-facing SEO/GEO/marketplace visibility service work.

Can ask Observatory for:

- scoped public evidence packs;
- SERP/ranking/AI/marketplace observations if admitted;
- freshness/volatility/caveat metadata;
- provider-attributed metrics;
- evidence IDs/citation handles;
- read-time alignment against customer-supplied overlays.

Must own outside Observatory:

- customer records;
- order/report records;
- customer identity;
- private first-party analytics;
- report conclusions;
- recommendations;
- deliverables;
- consent records as business records;
- report delivery history.

---

### `neon_ronin`

Purpose:
Workflow orchestration and review queues across projects.

Can ask Observatory for:

- scoped evidence packs for public surface observations;
- claim-use warnings;
- provider disagreement summaries;
- freshness/recapture warnings;
- evidence references for review tasks.

Must own outside Observatory:

- workspace operational state;
- review queues;
- agent task records;
- workflow decisions;
- accepted actions;
- scheduling;
- publishing/delivery state.

---

### `kaizen`

Purpose:
Governance, decisions, task packets, implementation returns, and project intelligence.

Can ask Observatory for:

- evidence packs cited by Kaizen docs;
- evidence/citation handles;
- claim-use warnings;
- provider/source provenance;
- freshness and drift context.

Must own outside Observatory:

- governance records;
- accepted decisions;
- task packets;
- implementation returns;
- roadmap authority;
- project doctrine.

---

### `internal`

Purpose:
Owner-internal market watch, owned-site visibility, and future internal telemetry.

Can ask Observatory for:

- internal-scope public evidence packs;
- market-watch panels;
- owner-owned public surface observations;
- future internal first-party telemetry only after explicit contract.

Must not assume:

- owner-controlled means automatically admitted;
- internal telemetry can skip rights/retention/access controls;
- cross-scope aggregation is allowed by default.

---

## Consumer request contract inputs

A future consumer request should include:

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

- Consumer request IDs are external locators, not Observatory primary business records.
- Request context must not contain customer private data.
- `claim_intent` is used to determine evidence/caveat needs, not to store the final claim.
- Recommendations must not be submitted as Observatory storage payloads.

---

## Consumer output contract inputs

A future Observatory evidence response should include:

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

- Evidence packs may support consumer reasoning.
- Evidence packs are not accepted conclusions.
- If a recommendation is produced, it must be stored by the consumer, not Observatory.

---

## Overlay contract inputs

Customer first-party overlays should be handled as ephemeral inputs.

Required overlay metadata:

```text
overlay_source_type
overlay_supplied_by_consumer
overlay_timestamp
overlay_freshness_status supplied by consumer
overlay_scope_context
overlay_no_storage_assertion
overlay_discard_required
```

Forbidden overlay behavior:

```text
persist customer analytics series
assign Observatory evidence IDs to private overlay rows
store customer screenshots as raw payloads without future ruling
promote overlay values into Observatory observations
use overlay identity as Observatory scope identity
```

Allowed posture:

```text
Consumer supplies overlay at read time.
Observatory aligns public evidence against it.
Observatory returns analysis support/caveats.
Overlay is discarded.
Consumer owns any final conclusion.
```

---

## Consumer promotion rule

When a connected LLM or downstream consumer interprets evidence and creates meaning, the durable output must promote out.

Examples:

| Output | Owner |
|---|---|
| SEO recommendation | SearchClarity |
| customer report paragraph | SearchClarity |
| review queue item | Neon Ronin |
| implementation task packet | Kaizen |
| accepted decision | Kaizen or owning consumer |
| workflow action | Neon Ronin |
| report delivery state | SearchClarity |

Observatory may keep only evidence and allowed metadata.

---

## Forbidden consumer patterns

```text
Send customer order and ask Observatory to store it.
Send GSC/GA4/Etsy Stats export and ask Observatory to persist it.
Ask Observatory to store final report conclusions.
Ask Observatory to store recommendations.
Ask Observatory to create agent tasks.
Ask Observatory to remember strategy session notes.
Use Observatory scope_id as customer database ID.
Use raw payload archive as customer file storage.
Use provider disagreement output as provider winner logic.
```

---

## Claim-intent handling

Consumer requests may include claim intent so Observatory can decide what evidence/caveats are needed.

Allowed claim intent examples:

```text
historical_observation_claim
current_state_claim
comparative_claim
absence_claim
provider_metric_claim
report_support_request
```

Forbidden claim intent examples:

```text
store_recommendation
make_customer_decision
choose_strategy
publish_report
trigger_agent_action
```

If a consumer asks for a forbidden claim intent, Observatory should reject or redirect the request to consumer-side workflow.

---

## Read-tool behavior requirements

Consumer-facing read tools should:

- return shaped evidence packs;
- include source/provenance/capture context;
- include freshness/volatility warnings;
- include provider attribution requirements;
- include rights/retention warnings;
- include sample-bound and absence warnings where relevant;
- state when recapture is required;
- state when consumer promotion is required;
- refuse to store or return recommendations as Observatory records.

They should not:

- expose direct SQL;
- expose raw mystery rows;
- expose credentials;
- mutate observations directly;
- hide caveats;
- produce accepted conclusions;
- store recommendations;
- store customer workflow state.

---

## No-nonsense checks

Before accepting a consumer request or returning a response, the system should ask:

1. Which consumer is asking?
2. What scope and scope_class apply?
3. Is the request for evidence or for a conclusion?
4. Does request context include private/customer data?
5. Does the request require an overlay?
6. If overlay exists, is it no-storage?
7. Is the requested evidence family admitted?
8. Are rights and retention valid?
9. Is freshness sufficient for the claim intent?
10. Are provider attribution and disagreement warnings needed?
11. Does output need a sample/absence warning?
12. Does this create a recommendation or workflow task?
13. Where must any durable conclusion promote?
14. Does the response expose only shaped evidence packs?
15. Are hammers required before this path can exist?

If unclear, fail closed or route to owner/consumer-side handling.

---

## Non-goals

RG12 does not authorize:

- API implementation;
- MCP tool implementation;
- schema design;
- migrations;
- customer data storage;
- report automation;
- provider admission;
- paid provider pulls;
- raw payload retention;
- strategy/recommendation storage;
- consumer workflow storage.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- finalizing consumer request/response schemas;
- enabling SearchClarity evidence-pack consumption;
- allowing any customer-scoped public observation workflow;
- accepting customer first-party overlays into read tools;
- exposing report-safe citation handles;
- defining consumer authentication/authorization;
- allowing cross-scope aggregate reads;
- admitting internal first-party telemetry.

---

## Deeper research carried forward

Relevant deep-research backlog items remain active:

- DR9 — SearchClarity customer-facing report language validation
- DR10 — Customer first-party overlay contract
- DR11 — Owned internal first-party telemetry
- DR14 — Evidence ID, citation handle, and report-safe reference finalization

RG12 answers enough for M7 consumer contract planning, not enough for customer-facing implementation.

---

## Blockers carried forward

- M7 must convert consumer request/response inputs into contracts.
- M8 must hammer customer data rejection, overlay no-storage, no recommendation storage, no direct SQL, and consumer promotion behavior.
- M14 must expose typed read tools that return shaped evidence packs only.
- M15 must validate SearchClarity customer-facing report language and proof workflow.

---

## Feeds later milestones

- M7 consumer contract
- M8 consumer boundary hammers
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow
- M17 overlay/internal telemetry proof

---

## Final RG12 rule

```text
Consumers may ask Observatory for governed evidence packs.
Consumers may not use Observatory as their customer database, workflow store, strategy store, or report system.
Evidence comes from Observatory.
Meaning promotes back to the consumer.
```
