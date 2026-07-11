# Contract - Evidence ID and Citation

Status: draft
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg3-evidence-id-citation-model.md`; supporting inputs from `research/rg2-scope-rights-retention-model.md`, `research/rg8-claim-safety-report-language.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg11-raw-archive-provider-drift.md`, `research/rg12-consumer-contract-inputs.md`, `02-boundaries.md`, `01-harvest-register.md`, and `contracts/scope-rights-retention.md`
Supersedes / superseded by: none

---

## Purpose

This contract defines the non-schema identifier and citation rules that let Observatory evidence be stable, traceable, human-citable, raw-support-aware, and safe for downstream consumers.

It exists before schema or implementation so future tables, read tools, evidence packs, SearchClarity reports, Kaizen references, and Neon Ronin workflows do not confuse provider job IDs, raw payload IDs, observation IDs, evidence IDs, citation handles, or customer/report references.

This contract does not authorize schema design, migrations, API/MCP implementation, report automation, provider admission, raw payload retention, customer-data storage, or strategy/recommendation storage.

---

## Governing boundaries

This contract operationalizes these project rules:

- Observatory stores observations, not conclusions.
- Evidence may support a downstream claim; evidence does not become the claim.
- Accepted conclusions promote out to the owning consumer.
- Provider output is provider-attributed testimony, not truth.
- Customer records and customer first-party data stay outside Observatory.
- Cross-system references are locators, never foreign keys into Kaizen, Neon Ronin, SearchClarity, or provider systems.
- Rights and retention fail closed.
- Raw payloads are support artifacts, not the user-facing evidence identity.
- Future LLM/agent access is through typed evidence packs, not direct SQL or raw mystery rows.

On conflict, `02-boundaries.md` and accepted owner rulings win.

---

## Definitions

### `capture_id`

Identifies a capture event or capture attempt.

Used for:

- grouping provider/API/manual capture attempts;
- associating attempts with approval, cost ceiling, stop conditions, and duplicate checks;
- explaining why a capture produced zero, one, or many observations.

Not used for:

- stable evidence citation;
- customer-facing report references;
- proof that a specific observation is valid.

Candidate shape:

```text
cap_<YYYYMMDD>_<shortid>
```

Example:

```text
cap_20260710_8f3a21
```

---

### `provider_job_id`

Stores the provider's own task, job, request, or transaction ID where available.

Used for:

- provider reconciliation;
- provider support/debugging;
- cost attribution;
- raw payload matching;
- provider export/audit.

Not used for:

- Observatory evidence identity;
- customer-facing citation;
- cross-provider comparison identity.

Rule:
Provider IDs remain provider-attributed context. They must never become Observatory primary evidence IDs.

---

### `raw_payload_id`

Identifies a stored raw payload or immutable raw payload bundle, only if raw retention is later admitted by the relevant source/rights/retention contract.

Used for:

- raw archive lookup;
- hash verification;
- provider drift review;
- parser safety;
- audit support.

Not used for:

- customer-facing citation by default;
- provider truth claims;
- strategy interpretation;
- bypassing rights/retention.

Candidate shape:

```text
raw_<sourcefamily>_<YYYYMMDD>_<shortid>
```

Example:

```text
raw_dataforseo_serp_20260710_4c91aa
```

Required companion context when applicable:

```text
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_created_at
rights_class
retention_class
raw_support_status
```

---

### `observation_id`

Identifies one structured observation extracted from a valid capture, raw payload, manual capture candidate, provider response, or public snapshot.

Used for:

- internal traceability;
- evidence assembly;
- scope/provenance/freshness joins;
- hammer testing;
- parser and drift review.

Not used for:

- provider job identity;
- raw payload identity;
- final report-safe reference by default.

Candidate shape:

```text
obs_<family>_<YYYYMMDD>_<shortid>
```

Examples:

```text
obs_serp_20260710_a13f22
obs_ai_mention_20260710_c8941e
obs_marketplace_listing_20260710_7bd912
```

---

### `evidence_id`

Provides the stable logical handle for evidence used by read tools, audits, Kaizen artifacts, SearchClarity report support, and downstream claim review.

Used for:

- LLM evidence packs;
- durable claim-to-evidence linking;
- cross-observation evidence bundles;
- citation resolution across schema evolution;
- status-aware reads.

Not used for:

- provider job identity;
- raw file identity;
- customer identity;
- accepted conclusions;
- recommendations;
- strategy records.

Candidate shape:

```text
ev_<scopeclass>_<family>_<YYYYMMDD>_<shortid>
```

Examples:

```text
ev_market_serp_20260710_d83a10
ev_customer_public_listing_20260710_a92ff1
ev_internal_ai_surface_20260710_f22b8c
```

Rule:
An evidence ID may resolve to one observation or to a bundle of observations. It must preserve scope, provenance, rights, retention, freshness, caveats, and raw support status.

---

### `citation_handle`

Provides a short human-readable reference for reports, LLM responses, notes, and QA.

Used for:

- readable report footnotes;
- evidence-pack references;
- human QA;
- claim review.

Not used for:

- database primary identity;
- raw payload lookup without controlled resolution;
- provider identity;
- customer identity.

Candidate shape:

```text
E-YYYYMMDD-NNN
```

Example:

```text
E-20260710-004
```

Default posture:
`evidence_id` is globally stable. `citation_handle` may be artifact-local for readability, but must resolve to a stable `evidence_id` through a controlled evidence map.

Final global-vs-artifact-local citation behavior remains an owner/M7 contract decision until accepted.

---

### `report_safe_reference`

Provides a customer-facing or consumer-facing reference that supports report QA without exposing internal IDs, provider job IDs, raw paths, customer private IDs, or database row identity.

Used for:

- SearchClarity report support;
- client-safe evidence references;
- consumer QA.

Not used for:

- raw archive lookup by customers;
- provider debugging;
- internal row identity;
- customer account/order/report identity.

Default posture:
`report_safe_reference` remains a concept until M15 SearchClarity proof work decides whether it is the same as an artifact-local citation handle, derived from `evidence_id`, or a separate public reference class.

---

### `external_overlay_reference`

Identifies a consumer-supplied read-time overlay without assigning Observatory evidence identity to the overlay itself.

Used for:

- ephemeral read-time customer first-party overlays;
- ephemeral intervention timeline alignment;
- consumer-owned context supplied to read tools.

Not used for:

- Observatory observation identity;
- evidence IDs;
- persistent customer records;
- raw payload retention.

Rule:
Customer/private overlays are not assigned Observatory evidence IDs under current doctrine.

---

## Contract rules

### R1 - Identifier layers must not collapse

The following identity layers must remain distinct:

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

A future schema may physically store them however M10 earns, but the logical contract must not collapse them into one generic `id` or let one layer impersonate another.

---

### R2 - Evidence IDs are the durable citation spine

Downstream claims, evidence packs, Kaizen artifacts, SearchClarity support references, and LLM evidence responses must cite stable `evidence_id` values or citation handles that resolve to stable `evidence_id` values.

Provider job IDs, raw payload IDs, capture IDs, file paths, database row IDs, report IDs, and customer IDs are not acceptable substitutes for evidence IDs.

---

### R3 - Citation handles are convenience handles, not truth keys

Citation handles may exist to make reports and LLM responses readable. They must resolve through a controlled mapping to evidence IDs.

A citation handle must not expose:

- customer identity;
- customer order/report IDs;
- provider job IDs;
- raw payload paths;
- internal database row IDs;
- strategy or conclusion text.

---

### R4 - Evidence IDs must carry evidence context, not meaning

An evidence ID may identify what was observed and the evidence bundle supporting it. It must not encode or imply:

- winner/loser status;
- rank truth;
- opportunity value;
- recommendation;
- accepted conclusion;
- provider trust;
- customer result;
- strategy priority.

Bad pattern:

```text
ev_best_keyword_20260710_abc123
```

Good pattern:

```text
ev_market_serp_20260710_abc123
```

---

### R5 - Evidence resolution must be status-aware

Evidence lookup must respect evidence status. Future read tools must not treat withdrawn, blocked, expired, invalidated, or rights-blocked evidence as normal active evidence.

Candidate evidence statuses:

```text
active
superseded
withdrawn
expired_by_retention
blocked_by_rights
invalidated
```

Status semantics:

| status | Meaning |
|---|---|
| `active` | Evidence may be cited under current rights, retention, and freshness constraints |
| `superseded` | Evidence remains historical but a newer handle should be used for current claims |
| `withdrawn` | Evidence should not be used due to a discovered problem |
| `expired_by_retention` | Evidence is no longer usable or exposed because retention ended |
| `blocked_by_rights` | Rights no longer allow use or exposure |
| `invalidated` | Capture, provenance, scope, parser, or hash failure invalidated the evidence |

---

### R6 - Evidence IDs must survive schema evolution

Evidence IDs are logical handles, not direct table-row addresses.

They must remain resolvable even if:

- raw payload storage moves;
- hot-path fields move between schema families;
- read-tool output shape changes;
- provider-specific fields change;
- report wording changes;
- a consumer regenerates an evidence-backed report.

M10 schema planning must preserve this property.

---

### R7 - Raw payloads support evidence; they are not the citation surface

When raw retention is allowed, evidence resolution may include raw payload IDs, hashes, manifests, and pointers. But raw payload IDs and paths are not report-safe citation handles by default.

Raw payload information exposed by read tools must obey rights, retention, and access rules.

If raw retention is not allowed, evidence may still resolve to structured observation context and raw support status such as:

```text
raw_not_retained
manifest_only
capture_and_purged
no_raw_storage_allowed
raw_blocked_by_rights
raw_expired_by_retention
```

---

### R8 - Customer/private overlays do not receive Observatory evidence IDs

Customer first-party data, customer analytics, seller dashboards, private reports, order records, and consumer workflow state remain outside Observatory.

If such data is supplied later as an ephemeral read-time overlay, it may receive an external overlay reference supplied by the consumer or tool invocation, but it must not receive:

- `observation_id`;
- `evidence_id`;
- `citation_handle` as Observatory evidence;
- raw payload ID;
- durable Observatory identity.

---

### R9 - Provider job IDs remain provider context

Provider job IDs may be preserved where allowed, but they must remain attached to provider name, endpoint/surface, capture context, and capture time.

They must not be reused as Observatory IDs, evidence IDs, citation handles, or report-safe references.

---

### R10 - Evidence bundles are allowed; hidden conclusions are not

An evidence ID may point to a bundle of related observations, such as an AI answer-surface mention plus citation observations from one run.

The bundle may group observations. It must not store an interpretive summary that becomes a conclusion, recommendation, opportunity score, provider winner, strategy note, or customer report paragraph.

Any derived/materialized evidence summary requires the V6 materialization test and explicit owner ruling before persistence.

Default behavior: compute summaries at read time.

---

### R11 - Evidence lookup must return caveat-ready packs

Future read tools that resolve evidence IDs must return enough context for safe downstream use.

Minimum evidence-pack context candidates:

```text
evidence_id
citation_handle if applicable
scope_id
scope_class
source_family
provider_or_capture_instrument
capture_method
captured_at
provider_reported_time if available
freshness_status
volatility_class
rights_class
retention_class
evidence_status
observation_ids
raw_support_status
raw_payload_ids or pointers only if permitted
provenance_summary
claim_use_warning
rights_retention_warning
consumer_promotion_required
```

This is an evidence response shape requirement, not an API implementation spec.

---

### R12 - Report-safe references remain blocked until consumer contracts decide exposure

SearchClarity/customer-facing report-safe reference behavior is not admitted by this draft.

Until M15 decides report-safe reference exposure, customer-facing report references must fail closed or remain in consumer-owned report artifacts outside Observatory.

---

### R13 - IDs must not encode customer identity or private business records

No Observatory identifier may encode:

```text
customer name
customer email
customer order ID
customer report ID
private account ID
seller dashboard ID
workflow task ID
Neon Ronin workspace state
Kaizen decision state as primary evidence identity
```

External consumer references may be accepted later only as locators under consumer contracts, not as Observatory primary evidence identity.

---

### R14 - Withdrawals and supersession must not silently overwrite history

If evidence is corrected, superseded, withdrawn, or invalidated, the system must preserve status-aware history rather than silently mutating old evidence into new truth.

M8 append-only hammers must try to overwrite or backdate evidence-linked records.

---

## Required fields / shapes

This section lists contract-level requirements, not schema.

### Identifier context for admitted evidence

A future admitted evidence record or evidence bundle must be able to resolve to:

```text
evidence_id
evidence_status
scope_id
scope_class
source_family
capture_id
provider_or_capture_instrument
capture_method
captured_at
rights_class
retention_class
freshness_status
volatility_class
observation_ids
raw_support_status
```

When available/applicable:

```text
provider_job_id
raw_payload_id
raw_payload_pointer
raw_payload_sha256
query_panel_id
query_panel_version_id
panel_run_id
citation_handle
report_safe_reference
provider_reported_time
```

---

### Resolution paths

Future read behavior should support these logical paths:

```text
citation_handle -> evidence_id -> evidence pack
report_safe_reference -> report evidence map -> evidence_id -> evidence pack
evidence_id -> evidence pack
evidence_id -> observation_ids -> observation context
evidence_id -> raw_payload_id -> raw manifest, if allowed
```

Unsupported or forbidden:

```text
provider_job_id -> customer-facing citation
raw_payload_id -> customer-facing citation
customer_order_id -> evidence_id
database_row_id -> report reference
recommendation_id -> evidence_id
```

---

### Evidence status vocabulary

Initial status vocabulary:

```text
active
superseded
withdrawn
expired_by_retention
blocked_by_rights
invalidated
```

M10/M14 may refine status mechanics, but must preserve the fail-closed meanings.

---

### Raw support status vocabulary

Initial raw support status vocabulary:

```text
raw_retained
manifest_only
capture_and_purged
raw_not_retained
no_raw_storage_allowed
raw_blocked_by_rights
raw_expired_by_retention
raw_hash_mismatch
raw_missing_or_unavailable
```

Read tools must expose raw support limits when the absence of raw support affects claim strength or auditability.

---

## Fail-closed behavior

### Missing required identity context

If evidence cannot resolve to scope, source, capture/provenance, rights, retention, and at least one observation context, then it cannot be admitted as active evidence.

Allowed fail-closed result candidates:

```text
blocked_missing_scope
blocked_missing_source_family
blocked_missing_provenance
blocked_missing_rights
blocked_missing_retention
blocked_no_observation_context
blocked_identity_layer_conflict
```

---

### Ambiguous identifier use

If a request supplies a provider job ID, raw payload ID, report ID, or customer ID where an evidence ID is required, the request must be rejected or redirected to the proper lookup path.

Default:

```text
reject_identifier_layer_mismatch
```

---

### Rights or retention conflict

If evidence status conflicts with rights or retention, rights/retention wins.

Examples:

```text
active evidence + expired retention -> block current exposure
active evidence + blocked rights -> block current exposure
raw_retained + no_raw_storage_allowed -> invalid state, block exposure
```

---

### Customer/private data detected in ID

If any generated or supplied Observatory ID contains customer identity, order/report identity, private account identity, or consumer workflow identity, the ID is invalid and must not be admitted.

Default:

```text
blocked_private_identity_in_identifier
```

---

### Report-safe reference unresolved

If a report-safe reference cannot resolve through an approved consumer/report evidence map to an evidence ID, it must not be used as evidence.

Default:

```text
blocked_unresolved_report_safe_reference
```

---

## Forbidden patterns

The following are forbidden:

```text
Use provider_job_id as evidence_id.
Use raw_payload_id as citation_handle.
Use database row ID as report-safe reference.
Encode customer email/name/order/report ID in evidence_id.
Encode recommendation/opportunity/strategy in evidence_id.
Assign Observatory evidence_id to customer first-party overlay rows.
Store SearchClarity report paragraphs as evidence bundles.
Persist AI visibility summary as evidence without materialization test and owner ruling.
Persist provider disagreement summary as truth or winner logic.
Expose raw payload pointers to customers by default.
Treat citation_handle as proof without resolving evidence_id and caveats.
Silently mutate an evidence ID from one observation to another.
Reuse a withdrawn/invalidated evidence ID as active evidence.
```

Fake-mustache variants are also forbidden, including:

```text
best_keyword_evidence_id
winning_provider_evidence_id
recommended_action_evidence
customer_report_evidence
strategy_support_id
truth_score_evidence
```

---

## Examples

### Valid planning example - SERP provider observation

```text
capture_id: cap_20260710_8f3a21
provider: dataforseo_candidate
provider_job_id: dataforseo:123456789
raw_payload_id: raw_dataforseo_serp_20260710_4c91aa
observation_id: obs_serp_20260710_a13f22
evidence_id: ev_market_serp_20260710_d83a10
citation_handle: E-20260710-004
scope_class: market_watch
rights_class: provider_clarification_required
retention_class: retain_until_review
raw_support_status: manifest_only
```

Why valid as planning shape:
Identifier layers are distinct. Provider job ID, raw payload ID, observation ID, evidence ID, and citation handle are not collapsed.

Why not executable yet:
DataForSEO is not admitted, raw retention is not admitted, and provider-specific bindings wait for M13.

---

### Valid planning example - AI answer-surface bundle

```text
capture_id: cap_20260710_b31f90
observation_ids:
  - obs_ai_mention_20260710_001a
  - obs_ai_citation_20260710_001b
evidence_id: ev_market_ai_surface_20260710_7db811
citation_handle: E-20260710-009
```

Why valid:
One evidence ID may represent a bounded bundle of related observations.

Required caveat:
The evidence bundle must not store a conclusion like `AI trusts this source` or `brand has AI authority`.

---

### Invalid - provider ID used as evidence ID

```text
evidence_id: dataforseo:123456789
provider_job_id: dataforseo:123456789
```

Why invalid:
Provider job identity and Observatory evidence identity are collapsed.

---

### Invalid - customer identity in citation

```text
evidence_id: ev_customer_jane-doe-order-1044_serp_20260710
citation_handle: SC-JANE-ORDER-1044-EVID-001
```

Why invalid:
Customer/order identity is encoded in Observatory evidence/citation identity.

---

### Invalid - recommendation masquerading as evidence

```text
evidence_id: ev_recommend_change_title_to_blue_widget_20260710
```

Why invalid:
The identifier encodes strategy/recommendation meaning. Recommendations belong to the owning consumer, not Observatory.

---

### Invalid - overlay promoted to evidence

```text
external_overlay_reference: customer_gsc_export_july
evidence_id: ev_customer_gsc_export_july_20260710
```

Why invalid:
Customer first-party overlay data is not stored in Observatory and does not receive Observatory evidence IDs under current doctrine.

---

## Owner-ruling candidates

Open rulings linked to `planning-inbox/owner-ruling-tracker.md`:

- OR-A4 / citation handle behavior: decide whether `citation_handle` is globally stable or artifact-local backed by stable `evidence_id`.
- OR-A4 / report-safe reference behavior: decide whether report-safe references are separate, derived from evidence IDs, or artifact-local citation handles under SearchClarity proof work.
- Evidence withdrawal/deprecation final behavior: decide final status mechanics before M14/M15 exposure.
- Raw pointer exposure: decide whether any raw payload pointer can be exposed outside internal tools.
- Customer-facing evidence handles: decide which reference class, if any, appears in SearchClarity reports.

Default until ruled:

```text
evidence_id: stable internal logical handle
citation_handle: allowed as draft concept; must resolve to evidence_id
report_safe_reference: blocked until consumer/report contract
raw pointer exposure: internal only unless later allowed
```

---

## Deeper-research blockers

Relevant backlog items:

- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR9 - SearchClarity customer-facing report language validation.
- DR10 - Customer first-party overlay contract.
- DR13 - Raw archive layout and provider drift fingerprints.
- DR16 - Consumer authentication / authorization model.

Blocks carried forward:

- M15 must decide report-safe customer-facing evidence references.
- M14 must define typed read-tool resolution and access behavior.
- M10 must preserve evidence ID stability during schema planning.
- M13/M11/M12 must not expose raw payload paths or provider IDs as evidence identity.

---

## Hammer expectations

M8+ must prove at least these hostile paths:

### H1 - Scope isolation hammers

- evidence ID cannot encode customer identity;
- evidence lookup cannot cross scopes without explicit allowance;
- external consumer IDs cannot become Observatory evidence IDs.

### H3 - Retention enforcement hammers

- expired retention blocks evidence exposure;
- raw payload support status reflects purge/expiration;
- evidence status changes do not silently delete context.

### H4 - Customer-private data rejection hammers

- customer GSC/GA4/Etsy Stats/YouTube Analytics exports cannot receive evidence IDs;
- customer report/order IDs cannot become citation handles.

### H5 - No strategy/recommendation storage hammers

- recommendation-like evidence IDs rejected;
- hidden strategy names in notes/citation/reference fields rejected.

### H12 - Raw archive integrity hammers

- raw hash mismatch blocks raw-supported evidence use;
- missing raw pointer cannot masquerade as raw-supported evidence;
- raw IDs cannot become report citations.

### H15 - Evidence ID / citation integrity hammers

- provider job ID cannot be used as evidence ID;
- raw payload ID cannot be used as report-safe reference;
- evidence ID remains stable across read calls;
- withdrawn/superseded/expired evidence status is respected;
- customer identity not encoded in citation handle;
- report-safe references do not expose private identifiers.

### H16 - Consumer request / overlay hammers

- overlays remain no-storage;
- overlay rows do not receive evidence IDs;
- report references fail closed if unresolved.

### H17 - LLM / agent access hammers

- read tools return shaped evidence packs, not raw mystery rows or direct SQL identity;
- no credentials or raw private paths appear in evidence response.

### H19 - Append-only observation hammers

- evidence-linked observations cannot be silently overwritten;
- corrections create status/supersession behavior, not invisible mutation.

---

## Feeds milestones

This contract feeds:

- M8 - hammer matrix and acceptance gates;
- M10 - schema planning only;
- M12 - first evidence slice build;
- M14 - typed read API / MCP contract;
- M15 - SearchClarity proof workflow;
- M16 - Provider Cross-Check proof;
- M17 - overlay/internal telemetry proof.

---

## Non-goals

This contract does not authorize:

- schema design;
- migrations;
- API/MCP implementation;
- provider admission;
- paid pulls;
- raw payload retention;
- report automation;
- customer data storage;
- report-safe reference exposure;
- direct SQL access;
- recommendation storage;
- strategy storage.

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG3 and supporting boundary/contracts inputs
```
