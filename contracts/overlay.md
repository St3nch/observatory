# Contract - Overlay

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg12-consumer-contract-inputs.md`; supporting inputs from `contracts/scope-rights-retention.md`, `contracts/evidence-id-citation.md`, `contracts/freshness-staleness-volatility.md`, `contracts/claim-safety.md`, `contracts/consumer-promotion.md`, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract governs read-time overlays: temporary consumer-supplied context that may be aligned with Observatory evidence without being stored as Observatory observations, raw payloads, evidence IDs, reports, recommendations, or workflow state.

It exists before schema, API/MCP work, read tools, SearchClarity proof workflow, or owned telemetry work so customer first-party analytics, intervention timelines, private files, seller dashboards, and consumer workflow state do not leak into Observatory storage.

Overlay is a lens at read time. It is not evidence admission.

---

## Governing boundaries

This contract operationalizes these Observatory rules:

- Observatory stores observations, not conclusions.
- Customer first-party data is not stored in Observatory under current law.
- Customer first-party data may be supplied later as read-time overlay only, unless a future owner ruling changes project law.
- Accepted conclusions promote out to the owning consumer.
- Consumers own customer records, reports, workflow state, recommendations, and private analytics.
- Evidence IDs identify Observatory evidence, not overlay rows.
- Rights and retention fail closed.
- LLMs and agents receive shaped evidence packs, not direct SQL, raw credentials, or ungoverned private data.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### Overlay

An ephemeral read-time input supplied by a consumer or tool invocation so a read operation can compare, align, filter, or contextualize Observatory evidence.

An overlay is not an Observatory observation.

### Customer first-party overlay

Private or customer-controlled data supplied by a consumer, such as GSC, GA4, Bing Webmaster, Etsy Stats, Shopify analytics, YouTube Analytics, seller-dashboard exports, order/report metadata, conversion data, or customer-supplied business context.

Default posture: `no_storage_overlay_only`.

### Intervention timeline overlay

A consumer-owned timeline of actions, edits, campaign changes, report dates, task completions, publish dates, or other events used to align public observations with consumer-side context.

Default posture: ephemeral overlay only.

### External overlay reference

A temporary request-local label that lets one read response refer to an overlay input without giving it Observatory evidence identity.

### Overlay freshness metadata

Consumer-supplied timestamp and freshness context describing when the overlay was produced, exported, or believed current.

Observatory may use this at read time. It must not store it as evidence.

---

## Contract rules

### R1. Overlays are read-time only

An overlay may be used only during a read operation or future typed read-tool invocation.

It must not be persisted as:

```text
observation
evidence
raw payload
query panel item
capture package
report record
recommendation
workflow state
accepted conclusion
```

### R2. Overlay rows do not receive Observatory evidence IDs

No customer/private overlay row, value, file, screenshot, export, or timeline event may receive:

```text
observation_id
evidence_id
citation_handle
raw_payload_id
panel_run_id
capture_id as admitted capture
```

A request-local `external_overlay_reference` is allowed only to manage the read response.

### R3. Overlay data must be supplied by the consumer

A read tool may accept overlay data only from a consumer-side request path admitted by later consumer/read-tool contracts.

Observatory must not fetch customer first-party data directly under this contract.

### R4. Overlay metadata is required

Every overlay input must provide or explicitly mark:

```text
overlay_source_type
overlay_supplied_by_consumer
overlay_timestamp or exported_at
overlay_freshness_status supplied by consumer
overlay_scope_context
overlay_no_storage_assertion
overlay_discard_required
external_overlay_reference
```

If required metadata is absent, the overlay cannot support current or comparative read output.

### R5. Overlay freshness is consumer-supplied

Overlay freshness may be used only as consumer-supplied context.

Observatory must not treat overlay freshness as Observatory capture freshness or provider-reported time.

### R6. Overlay values cannot become Observatory observations

A read operation may align public evidence with overlay values, but must not promote overlay values into stored Observatory observations.

Allowed:

```text
Read-time comparison: public SERP observations aligned against a consumer-supplied GSC export window.
```

Forbidden:

```text
Store GSC clicks/impressions as Observatory evidence.
```

### R7. Overlay-driven conclusions promote out

If an overlay helps produce meaning, interpretation, recommendation, report language, task decisions, or accepted conclusions, the durable output belongs to the owning consumer.

Observatory may return evidence, warnings, and alignment support only.

### R8. Overlays cannot authorize capture or recapture

An overlay may reveal that evidence is stale, incomplete, or worth reviewing. That does not authorize provider pulls, manual capture, browser capture, recurring capture, or spend.

### R9. Overlay data must not define scope identity

Consumer/customer overlay identifiers must not become Observatory `scope_id`, evidence ID, citation handle, or raw payload identity.

### R10. Overlay handling must be discard-proven later

Future read-tool implementation must prove overlay discard/no-storage behavior through M8/M14/M17 hammers before customer or internal private overlays are accepted.

This draft does not implement discard proof.

### R11. Overlay use must carry warnings

Any response using an overlay must disclose that the overlay was consumer supplied, not stored, and not independently admitted as Observatory evidence.

Minimum warning concept:

```text
Overlay values were supplied by the consumer at read time and were not stored as Observatory evidence.
```

### R12. Internal overlays are not automatically admitted

Owner-internal first-party telemetry is still first-party telemetry. It requires explicit internal-scope overlay or telemetry admission before use.

### R13. Screenshots and files are not automatically overlays

Customer screenshots, CSV exports, PDFs, reports, or files remain private consumer artifacts unless a future contract admits a no-storage read-time path.

They must not be stored as raw payloads or evidence under this contract.

### R14. Overlay access must be least-necessary

Future read tools must accept only the overlay fields needed for the requested evidence alignment.

Bulk private exports, broad customer files, and unrelated private context are forbidden by default.

### R15. Overlay comparisons must preserve incompleteness

If overlay context is incomplete, stale, missing freshness metadata, or incomparable to Observatory evidence, read output must warn or block the comparison.

---

## Required fields / shapes

These are contract-level behavior requirements, not schema.

### Overlay input shape

```text
overlay_request_id
consumer_name
consumer_request_id
external_overlay_reference
overlay_source_type
overlay_supplied_by_consumer
overlay_timestamp
exported_at if applicable
overlay_freshness_status supplied by consumer
overlay_scope_context
overlay_no_storage_assertion
overlay_discard_required
overlay_allowed_use
overlay_field_manifest if allowed
private_data_indicator
```

### Overlay use shape in read output

```text
evidence_ids
citation_handles if available
external_overlay_reference
overlay_used: true/false
overlay_source_type
overlay_freshness_warning
overlay_no_storage_warning
overlay_incomparability_warning if applicable
consumer_promotion_required
```

### Overlay statuses

```text
accepted_for_read_time_use
blocked_missing_metadata
blocked_private_data_overreach
blocked_no_storage_not_asserted
blocked_by_scope_mismatch
blocked_by_incomparability
blocked_by_unknown_freshness
discard_required
discard_confirmed_future_only
```

`discard_confirmed_future_only` is a planning placeholder; actual discard proof belongs to later hammers and implementation.

---

## Fail-closed behavior

- Missing no-storage assertion blocks overlay use.
- Missing freshness metadata blocks current/comparative claims.
- Missing consumer/scope context blocks overlay use.
- Overlay values containing customer/private data beyond the requested need are rejected or require consumer-side reduction before use.
- Overlay identity cannot become Observatory scope identity.
- Overlay rows cannot receive evidence IDs.
- Overlay files cannot become raw payloads.
- Overlay-driven recommendations must promote out.
- Overlay data must be discarded after read use once future read tooling exists.
- If discard/no-storage cannot be proven, overlay path remains blocked.

---

## Forbidden patterns

This contract forbids:

```text
persist customer GSC/GA4/Bing/Etsy/Shopify/YouTube analytics
assign evidence IDs to overlay rows
store overlay CSV as raw payload
store customer screenshot as raw evidence
store intervention timeline as Observatory history
store recommendations from overlay alignment
use overlay customer ID as scope ID
use overlay export ID as evidence ID
use private overlay data for cross-scope aggregation
trigger recapture or agent task from overlay mismatch
cache overlay values for later convenience
```

Fake-mustache variants are also forbidden:

```text
temporary_overlay_cache
customer_analytics_evidence
overlay_observation_shadow
private_metric_hot_fields
overlay_based_opportunity_score
overlay_recapture_task
intervention_timeline_table inside Observatory
```

---

## Examples

### Valid example - customer analytics overlay for read-time comparison

```text
consumer_name: searchclarity
external_overlay_reference: overlay_req_123_gsc_window
overlay_source_type: customer_gsc_export
overlay_supplied_by_consumer: true
overlay_timestamp: 2026-07-10T10:00:00Z
overlay_no_storage_assertion: true
overlay_discard_required: true
claim_intent: report_support_request
```

Why valid as planning shape:

- The overlay is supplied by the consumer.
- It has freshness context.
- It is explicitly no-storage.
- It does not receive evidence identity.

### Invalid example - store customer GSC export

```text
raw_payload_id: raw_customer_gsc_20260710
retention_class: retain_project_evidence
evidence_id: ev_customer_gsc_clicks_20260710
```

Why invalid:

- Customer first-party analytics are overlay-only under current law.
- Overlay rows cannot become Observatory evidence.

### Valid example - intervention timeline overlay

```text
overlay_source_type: consumer_intervention_timeline
events:
  - title changed by consumer on 2026-06-20
overlay_no_storage_assertion: true
consumer_promotion_required: true
```

Why valid as read-time posture:

- The event can align public observations for consumer-side reasoning.
- Observatory does not store the intervention event as its own evidence.

### Invalid example - causal conclusion from overlay

```text
stored_observatory_claim: title change caused ranking improvement
```

Why invalid:

- Causality is consumer-owned interpretation.
- Observatory may support before/after evidence alignment only.

---

## Owner-ruling candidates

Open rulings carried forward:

- Whether SearchClarity may supply customer first-party overlays to read tools in M15.
- Whether internal first-party telemetry may use the overlay pattern before owned telemetry storage is considered.
- Whether intervention timelines can be supplied as ephemeral overlays for before/after support.
- What exact discard proof is required before any overlay path exists.
- Whether any non-private overlay manifest can be retained after payload discard.
- Whether screenshots can ever be used as no-storage read-time overlay inputs.

Default until ruled:

```text
Customer/private overlays are read-time only.
No overlay storage.
No overlay evidence IDs.
No overlay raw archive.
No customer-facing overlay workflow until M15/M17 hammers pass.
```

---

## Deeper-research blockers

Relevant blockers:

- DR9 - SearchClarity customer-facing report language validation.
- DR10 - Customer first-party overlay contract.
- DR11 - Owned internal first-party telemetry.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR16 - Consumer authentication / authorization model.

This draft is enough for M7 planning. It does not authorize implementation or customer overlay handling.

---

## Hammer expectations

M8+ hammers must prove:

- customer overlay rows cannot receive evidence IDs;
- overlay payloads cannot be stored as raw payloads;
- missing no-storage assertion blocks use;
- missing overlay freshness blocks current/comparative output;
- overlay identity cannot become scope identity;
- overlay values are discarded after read use;
- overlay data cannot create recommendations inside Observatory;
- overlay mismatch cannot trigger recapture/spend/task creation;
- customer screenshots/files are rejected unless an admitted no-storage path exists;
- direct SQL/raw row access cannot expose overlay values.

Relevant categories:

```text
H1 scope isolation
H3 retention enforcement
H4 customer-private rejection
H5 no recommendation storage
H9 freshness / volatility
H15 evidence/citation integrity
H16 overlay no-storage
H17 LLM/agent access boundary
H18 hostile input
H21 audit-first enforcement
```

---

## Feeds milestones

This contract feeds:

- M8 - overlay boundary hammers.
- M14 - typed read-tool contract.
- M15 - SearchClarity proof workflow.
- M17 - owned telemetry overlay/internal telemetry proof.

---

## Non-authorizations

This contract does not authorize:

```text
schema design
migrations
API/MCP implementation
customer data handling
customer file upload handling
customer first-party analytics storage
raw archive of overlay payloads
report automation
recommendation storage
workflow task storage
owned internal telemetry storage
recurring capture
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG12 and existing M7 consumer/evidence contracts
```
