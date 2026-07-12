# Contract - Owned Telemetry Overlay Proof v0.1

Status: ready for owner acceptance
Authority: proposed M17 proof contract; does not authorize real customer/private telemetry, files, screenshots, persistence, canonical ingestion, provider execution, Postgres, schema, migrations, production API/MCP, reports, or production integration
Version: 0.1
Date: 2026-07-12
Milestone: M17 - Owned Telemetry Overlay Proof

---

## Purpose

Define one bounded proof surface for aligning synthetic owned/internal or customer first-party telemetry with Observatory evidence at read time while proving that overlay values never become Observatory observations, evidence, raw payloads, durable logs, caches, workflow state, recommendations, or accepted conclusions.

Overlay is a temporary lens. It is not evidence admission.

---

## Governing rules

- All M17 proof inputs are synthetic and request-local.
- Real customer analytics, owner-private telemetry, account identifiers, exports, files, screenshots, and external references remain blocked.
- Overlay inputs never receive Observatory observation IDs, evidence IDs, citation handles, capture IDs, raw payload IDs, or scope identities.
- Observatory may return alignment facts and caveats only.
- Recommendations, causality, report prose, tasks, and accepted conclusions promote out to the owning consumer.
- Overlay processing must be deterministic, in-memory, no-side-effect, and discarded after response construction.
- No manifest of values, hashes of values, field inventory containing private names, or derived private summary may persist.

---

## Admitted synthetic proof classes

```text
synthetic_internal_telemetry_series
synthetic_customer_first_party_series
synthetic_intervention_timeline
```

These classes exist only as proof fixtures. They do not admit real inputs.

---

## Closed request types

```text
overlay_alignment_check
overlay_before_after_alignment
overlay_coverage_alignment
```

No free-form report context, file path, URL, account identifier, or arbitrary field projection is admitted.

---

## Required request fields

```text
contract_version
request_id
request_type
caller_class
scope_id
external_overlay_reference
overlay_source_type
overlay_supplied_by_consumer
overlay_timestamp
overlay_freshness_status
overlay_scope_context
overlay_no_storage_assertion
overlay_discard_required
overlay_allowed_use
claim_intent
series_manifest
```

`series_manifest` is a closed synthetic structure containing only declared fixture fields. It is not a file manifest.

---

## Required response fields

```text
contract_version
request_id
response_id
scope_id
external_overlay_reference
overlay_used
alignment_disposition
alignment_units
required_caveats
coverage_blind_spots
overlay_no_storage_warning
overlay_freshness_warning
overlay_incomparability_warning
overlay_discard_status
consumer_promotion_required: true
overlay_persisted: false
overlay_evidence_identity_created: false
customer_facing_output_authorized: false
```

No overlay values are echoed except the minimum synthetic alignment values explicitly allowed by the fixture contract.

---

## Alignment dispositions

```text
aligned_with_caveat
partially_aligned
blocked_missing_metadata
blocked_unknown_freshness
blocked_scope_mismatch
blocked_incomparability
blocked_private_data
blocked_not_admitted
```

Missing, stale, or materially mismatched time windows cannot support causal or current-state wording.

---

## Discard proof

For the bounded proof, discard means:

- request data exists only in function-local immutable values;
- no module-level mutable cache or registry receives overlay values;
- no file, environment variable, subprocess, network, database, logger payload, or external repository is touched;
- fixtures are unchanged after the call;
- repeated calls depend only on supplied inputs and return deterministic output;
- response contains `overlay_discard_status: discarded_after_response_build`;
- tests inspect the package for forbidden imports and write paths.

This proves bounded local discard behavior only. It does not prove production runtime memory erasure, process isolation, framework logging, crash dumps, tracing systems, or deployment infrastructure.

---

## Synthetic internal telemetry posture

Synthetic internal telemetry follows the same overlay law as synthetic customer first-party telemetry:

- no canonical admission;
- no special owner bypass;
- no evidence IDs;
- no persistence;
- no cross-scope aggregation;
- no automatic task, recapture, recommendation, or strategy creation.

Real internal telemetry remains separately gated.

---

## Intervention timelines

Synthetic intervention timelines may support before/after alignment only.

They may not support stored causality, such as:

```text
change X caused outcome Y
```

Allowed output is limited to temporal alignment and caveats.

---

## Files and screenshots

Files, screenshots, CSV/PDF exports, URLs, file contents, and external references remain blocked in M17.

The first proof accepts only closed in-memory synthetic fixtures. No file parser, upload path, connector, or screenshot reader is implemented.

---

## Retained metadata

The proof retains no overlay-derived metadata after the call.

Repository proof records may retain only:

```text
contract version
implementation commit
test command
test count
proof classification
limitations
```

They must not retain overlay references used in runtime fixtures, values, hashes, field names derived from private data, or alignment outputs.

---

## Forbidden behavior

```text
persist overlay values
cache overlay values
log overlay values
hash overlay values for later matching
create evidence identity
create raw payload identity
promote overlay rows into observations
use customer/account identity as scope
read files or screenshots
fetch private analytics
cross-scope aggregation
causal conclusion storage
recommendation or task creation
trigger recapture or provider spend
report generation
```

Fake temporary names do not change the prohibition.

---

## Fail-closed behavior

Reject when:

- caller or request type is not admitted;
- required overlay metadata is missing;
- no-storage or discard assertions are false;
- scope context mismatches;
- freshness is unknown for current/comparative use;
- values contain identity, account, order, report, payment, file, URL, credential, or private-export structures;
- request asks for persistence, evidence promotion, causality, recommendations, tasks, recapture, reports, or cross-scope use.

Errors must not echo supplied private values.

---

## Proof boundary

A later separately authorized proof may implement a local synthetic in-memory adapter and tests only.

It does not authorize:

```text
real customer data
real internal telemetry
files/screenshots/exports
connectors
provider calls
persistence
Postgres
schema or migrations
production API/MCP
consumer integration
report generation
```
