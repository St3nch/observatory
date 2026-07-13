# Contract - SearchClarity Proof Workflow v0.1.1

Status: accepted v0.1.1 by `decisions/2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md`
Authority: binding M15 SearchClarity evidence-support contract within its declared scope; does not authorize proof implementation, customer data, overlays, report generation, production integration, provider execution, or persistence
Version: 0.1.1
Date: 2026-07-12
Milestone: M15 - SearchClarity Proof Workflow
Source authority:
- `02-boundaries.md`
- accepted contract set v0.1
- `contracts/searchclarity-consumer-placeholder.md`
- `contracts/consumer-promotion.md`
- `contracts/claim-safety.md`
- `contracts/overlay.md`
- `contracts/typed-read-api-mcp-v0-1.md`
- `decisions/2026-07-12-m14-closure-and-m15-activation.md`
Supersedes / superseded by: intended to supersede `contracts/searchclarity-consumer-placeholder.md` for M15 behavior after owner acceptance

---

## Purpose

Define the evidence-support boundary through which SearchClarity may use Observatory evidence while SearchClarity remains the sole owner of customers, engagements, private inputs, report prose, recommendations, deliverables, consent records, delivery state, and accepted conclusions.

This contract governs evidence-pack-to-report-support behavior. It does not authorize Observatory to create, store, deliver, or approve a customer report.

Core rule:

```text
Observatory supplies governed evidence support.
SearchClarity owns interpretation, recommendations, reports, review, acceptance, and delivery.
```

---

## Governing boundary

Observatory is not:

```text
SearchClarity CRM
customer database
order system
report system
report archive
recommendation store
consent register
delivery tracker
private analytics store
customer file store
```

SearchClarity may consume shaped evidence only through an admitted internal caller path. No public or customer-facing caller is admitted by M15.

Customer first-party analytics remain outside Observatory. No overlay implementation is admitted by this contract.

---

## Definitions

### SearchClarity internal caller

The admitted typed-read caller class `searchclarity_internal` acting through authenticated, explicit scope and request-type grants.

It is not a customer identity and cannot self-assert or widen scope.

### Report-support request

A bounded request for evidence and caveats that may support a SearchClarity-owned report artifact.

It is not a request for Observatory to write, approve, store, or deliver the report.

### Report-support pack

A shaped, scope-safe response derived from the accepted typed-read contract. It contains evidence units, claim-use metadata, caveats, coverage limits, and a report-support disposition.

It is not report prose and is not customer-facing by default.

### Report-safe reference

A consumer-facing reference generated or mapped by SearchClarity from an allowed Observatory support reference after owner admission.

A report-safe reference must not reveal internal evidence handles, provider job IDs, raw pointers, filesystem paths, database identities, or customer identifiers.

### Report-support disposition

A deterministic evidence-side status stating whether the available evidence may support a named claim class under the declared use.

Allowed values:

```text
supportable_with_required_caveats
historical_support_only
insufficient_evidence
blocked_by_freshness
blocked_by_rights
blocked_by_retention
blocked_by_claim_safety
blocked_by_scope
blocked_by_private_data
blocked_not_admitted
```

This disposition is not approval of report wording.

---

## Contract rules

### R1. SearchClarity requests evidence support only

M15 admits only these SearchClarity request types:

```text
report_support_evidence_lookup
report_support_observation_package
report_support_freshness_check
report_support_coverage_check
```

Forbidden request types include:

```text
write_report
store_report
approve_report
publish_report
deliver_report
store_recommendation
choose_strategy
store_customer
store_order
store_consent
store_private_analytics
run_provider
run_capture
```

### R2. Requests must be customer-clean

The request may include:

- authenticated caller identity supplied by the access layer;
- authorized Observatory scope ID;
- closed claim intent;
- requested evidence families;
- current or historical use;
- bounded non-private report-support purpose code;
- freshness requirement;
- allowed output use.

The request must not include:

- customer name, email, company, shop, marketplace account, or contact details;
- order, gig, invoice, payment, report, delivery, or revision IDs;
- customer messages;
- private analytics values;
- private screenshots or files;
- report prose or recommendations.

Private or customer workflow content is a hard failure, not a field to silently store or repurpose.

### R3. Customer identity cannot become Observatory scope identity

SearchClarity customer, order, report, shop, account, and engagement identifiers must not become Observatory scope IDs, evidence IDs, citation handles, report-safe references, or durable foreign keys.

M15 proof may use synthetic non-customer scope fixtures only.

### R4. Evidence packs preserve mandatory caveats

Every report-support pack must preserve applicable:

```text
provider attribution
captured-at context
provider-reported time if available
freshness status
volatility class
rights and retention status
evidence status
claim-use warning
sample-bound warning
absence warning
incomparability warning
raw-support status
coverage blind spots
consumer-promotion requirement
```

No caller, projection, template, or token budget may remove mandatory caveats while retaining the qualified evidence.

### R5. Claim intent is closed and evidence-side only

Allowed M15 claim intents:

```text
historical_observation
current_state_observation
comparative_observation
sampled_absence
provider_metric_observation
ai_geo_sample_observation
marketplace_public_observation
coverage_statement
```

Predictive, causal, recommendation, guarantee, endorsement, universal-absence, winner-provider, and strategy intents are forbidden.

The evidence-side claim intent does not authorize storage of the final customer-facing claim.

The bounded prototype uses conservative adapter aliases for two M15 intents before calling the narrower M14 typed-read surface:

```text
provider_metric_statement -> historical_observation
ai_geo_sampled_observation -> historical_observation
```

This translation is evidence-selection only. It does not erase the original M15 claim intent, strengthen the claim, authorize current-use language, or convert provider/AI testimony into fact. Future consumer adapters must declare any claim-intent translation explicitly in their contract and tests; silent translation is forbidden.

### R6. Report-support dispositions fail closed

A report-support pack must block or downgrade support when:

- evidence is missing, withdrawn, invalidated, rights-blocked, or retention-expired;
- current-state use relies on stale or unknown freshness;
- required provider attribution is absent;
- absence context is incomplete;
- AI/GEO sampling context is insufficient or not admitted;
- marketplace source/capture/rights posture is not admitted;
- provider values are not meaningfully comparable;
- required caveats cannot travel with the evidence;
- private/customer content appears in the request or output.

### R7. Observatory does not generate report prose

Observatory may return controlled evidence-side labels and warnings.

It must not return:

- polished customer report paragraphs;
- recommendations;
- priorities;
- strategy;
- customer-facing conclusions;
- guarantees;
- calls to action;
- service-delivery language.

Those are SearchClarity-owned outputs and must promote out.

### R8. Report-safe references are separate from internal handles

The M15 contract direction is:

```text
internal evidence handle != report-safe reference
```

A future report-safe reference must be:

- opaque;
- non-enumerable;
- status-aware;
- customer-safe;
- resolvable by SearchClarity through an admitted internal path;
- incapable of revealing raw support paths, provider IDs, internal storage identities, or another scope.

Until the owner accepts the final reference posture, the proof workflow uses synthetic artifact-local references only.

### R9. SearchClarity owns the report-support handoff

A SearchClarity-owned artifact may preserve, outside Observatory:

```text
searchclarity_output_id
report_safe_references
required_caveats_preserved
consumer_author_or_agent
human_review_status
customer_facing_wording
recommendations
acceptance_status
delivery_status
```

Observatory must not persist this handoff artifact or its report prose.

### R10. Human review remains required

No M15 output is customer-facing merely because evidence support is `supportable_with_required_caveats`.

SearchClarity must own human review of:

- evidence relevance;
- claim wording;
- caveat translation;
- recommendation logic;
- customer-facing clarity;
- final acceptance and delivery.

### R11. Provider disagreement remains attributed

If customer-facing provider disagreement is later admitted, SearchClarity must present values as provider-attributed testimony with methodology and incomparability caveats.

Observatory must not select a winner, average disagreement into truth, or create a composite authority/opportunity score.

M15 proof may demonstrate side-by-side evidence support only if the exact fixture is admitted. It may not create customer-facing prose.

### R12. AI/GEO evidence remains sample-bound

AI/GEO support must preserve prompt/query, surface, locale/device if relevant, capture time, sample count, recurrence context, and absence limitations.

Citation does not mean trust, endorsement, authority, recommendation, or influence.

A single run cannot support a durable visibility score or universal absence claim.

### R13. Marketplace evidence remains admission-bound

Marketplace report support is blocked unless platform, public/private classification, capture method, rights, retention, and claim ceiling are admitted.

No marketplace scraping, private dashboard inference, traffic/sales inference, or customer-behavior inference is authorized.

### R14. Overlays remain deferred

M15 may define overlay decision points but does not admit real customer first-party overlays.

Any future overlay path must prove:

- consumer-supplied input;
- minimum necessary fields;
- no storage;
- no evidence IDs;
- no raw archive;
- no logs containing private values;
- request-local reference only;
- deterministic discard;
- consumer-owned conclusions;
- no trigger of capture, spend, reports, tasks, or writes.

Until that proof exists, overlay requests return `blocked_not_admitted`.

### R15. Screenshots and files remain blocked

Customer screenshots, PDFs, CSVs, analytics exports, and private files are not admitted M15 inputs.

A later no-storage file/screenshot path requires a separate owner ruling and hostile-path proof.

### R16. Consent remains SearchClarity-owned

Customer consent is a SearchClarity business record. Observatory may receive only a request assertion that the consumer path is authorized to use a non-private input class after that class is admitted.

Observatory must not store consent records, signatures, customer identity, or consent documents.

### R17. Reads cannot trigger work

Report-support reads must not:

- call providers;
- schedule capture;
- reserve or spend budget;
- write reports;
- create recommendations;
- create tasks;
- persist overlays;
- mutate evidence;
- store customer or workflow state.

### R18. Cross-scope aggregation remains forbidden

SearchClarity may not use M15 to aggregate customer engagements or infer cross-customer patterns.

Single authorized scope only. Any future aggregate research scope requires a separate owner ruling and cannot reuse customer identity.

### R19. Errors are deterministic and non-leaking

Customer-clean errors use the accepted typed-read taxonomy and must not reveal:

- hidden handle existence;
- other scopes;
- customer identity;
- record counts;
- raw paths;
- provider secrets;
- storage internals.

### R20. M15 proof remains local and synthetic

A later M15 proof may use only:

- committed Observatory fixture evidence;
- sanitized provider evidence already admitted for structural use;
- synthetic SearchClarity request/report-support fixtures with no real customer identity, private analytics, report prose, or external files.

It proves contract behavior only, not production SearchClarity integration or customer-facing correctness.

---

## Required request shape

```text
contract_version
request_id
caller_class: searchclarity_internal
request_type
scope_id
claim_intent
current_or_historical_use
requested_evidence_families
freshness_requirement
report_support_purpose_code
allowed_output_use: searchclarity_internal_report_support
```

Optional, closed-vocabulary fields:

```text
evidence_handles
coverage_dimensions
requested_reference_mode: internal_only | synthetic_report_safe_fixture
```

No free-text report context is required or admitted in the first proof.

---

## Required response shape

```text
contract_version
request_id
response_id
scope_id
claim_intent
report_support_disposition
evidence_units[]
required_caveats[]
coverage_blind_spots[]
reference_mode
report_support_references[]
consumer_promotion_required: true
customer_facing_output_authorized: false
truncated
omitted_evidence_unit_count
```

Each evidence unit retains the accepted typed-read fields and adjacency rules.

---

## Forbidden outbound fields

```text
customer_name
customer_email
customer_company
customer_shop
order_id
invoice_id
payment_id
report_id
delivery_status
revision_status
consent_record
private_analytics
private_file_path
raw_payload_path
provider_secret
recommendation
strategy
customer_report_paragraph
```

Presence is a hard failure.

---

## Prototype entry gates

Before an implementation task may be proposed:

- this contract is accepted by owner decision;
- OR-E1 through OR-E5 receive explicit dispositions;
- OR-F1 is either deferred to M17 or accepted under an exact no-storage proof boundary;
- DR9 and DR10 are routed with explicit proof/defer decisions;
- M15 hostile-path plan is accepted;
- the task uses synthetic customer-clean fixtures only;
- implementation authority is granted separately for the exact task.

---

## Explicit non-authorizations

This contract does not authorize:

```text
customer data
customer records
private analytics
real overlays
screenshots or file intake
report generation
report storage
report delivery
recommendations
SearchClarity production integration
public/customer-facing caller
Postgres
schema or migrations
provider calls
recurring capture
production API/MCP
strategy storage
automatic conclusion promotion
```

---

## Change log

```text
0.1.1 - 2026-07-12 - DB-1 corrective amendment documenting conservative M15-to-M14 claim-intent translation and forbidding silent semantic remapping
0.1 - 2026-07-12 - full M15 SearchClarity proof-workflow contract drafted from accepted consumer, claim-safety, overlay, and typed-read contracts
```
