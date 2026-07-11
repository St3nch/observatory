# Contract - Raw Archive / Provider Drift

Status: draft
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg11-raw-archive-provider-drift.md`, with supporting inputs from `research/rg1-dataforseo-rights-retention-cost.md`, `research/rg2-scope-rights-retention-model.md`, `research/rg3-evidence-id-citation-model.md`, `research/rg8-claim-safety-report-language.md`, `research/rg9-provider-cross-check-disagreement-model.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `contracts/scope-rights-retention.md`, `contracts/evidence-id-citation.md`, `contracts/capturepackage-v0-1.md`, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract defines raw archive and provider drift behavior before any provider payload, parser, raw store, schema, API, MCP tool, or capture runner is implemented.

Raw payloads are evidence support. They are not the observation model, not a permission shortcut, not a strategy cache, not a customer data lake, and not a mystery JSON dumping ground.

Provider drift is a material change in provider or capture output that affects parsing, interpretation, comparability, or evidence integrity. Drift must become visible evidence and review context, not silent corruption.

---

## Governing boundaries

This contract operationalizes these rules:

- Observatory stores observations, not conclusions.
- Raw payloads support observations; they are not conclusions or strategy.
- Rights and retention fail closed.
- Customer/private data remains outside Observatory storage.
- Provider data is provider-attributed testimony, not truth.
- Raw retention is not automatic and requires source/rights/retention clearance.
- Evidence IDs and citation handles must not collapse into raw payload IDs or provider job IDs.
- Parser and provider drift must not silently mutate historical evidence.
- LLMs and agents receive shaped evidence packs, not raw mystery blobs or credentials.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### Raw payload

The original provider response, browser/manual capture artifact, public snapshot artifact, API response, or capture output supporting candidate observations.

A raw payload may be retained only when rights and retention allow.

### Raw archive

The governed storage or pointer layer for retained raw payloads, manifests, hashes, purge evidence, and support status.

This contract defines behavior only. It does not choose filesystem, object store, database, cloud, local path, bucket layout, or table design.

### Raw payload manifest

A minimal metadata record that describes a raw payload and its support status. A manifest may sometimes survive when the raw payload itself must be purged, but only if rights and retention permit manifest retention.

### Raw support status

A label describing whether raw support exists, is retained, is manifest-only, is purged, is blocked, or is unavailable.

### Shape fingerprint

A provider/capture-output fingerprint used to detect material payload shape changes. Shape fingerprints support parser safety and drift review; they are not claims about market reality.

### Provider drift

A material change in provider/capture output, including added fields, removed fields, renamed fields, type changes, enum changes, timestamp semantic changes, score scale changes, endpoint behavior changes, provider error payload changes, or source/citation format changes.

### Parser status

A label describing whether a parser can safely produce candidate observations from a raw payload under the known shape, source, rights, retention, and CapturePackage context.

---

## Contract rules

### R1. Raw payloads are support artifacts only

Raw payloads may support observations and evidence. They must not become:

- strategy records;
- recommendations;
- customer report records;
- provider truth stores;
- accepted conclusions;
- hidden JSON schema bypasses;
- customer data lakes.

### R2. Raw retention requires explicit rights and retention clearance

Raw payload retention is blocked unless the CapturePackage and scope/rights/retention contracts can prove:

```text
rights_class
rights_basis
retention_class
retention_basis
source_admission_status
raw_retention_posture
```

Unknown, ambiguous, missing, stale, or conflicted rights fail closed.

### R3. Raw archive does not authorize capture

A raw archive contract does not authorize provider use, paid pulls, manual capture, browser-extension capture, marketplace capture, recurring capture, API/MCP implementation, parser implementation, or schema work.

### R4. Raw payload identity must remain separate

`raw_payload_id` is not an `evidence_id`, `citation_handle`, `provider_job_id`, `capture_id`, database row ID, report-safe reference, or customer-facing citation.

Raw payload IDs and pointers must not be exposed outside allowed internal/read contexts.

### R5. Retained raw payloads require hash verification

If a raw payload is retained, it must have a content hash or equivalent integrity proof before it can support admitted observations.

Minimum contract expectation:

```text
raw_payload_sha256
raw_payload_bytes
raw_payload_pointer
raw_payload_created_at or captured_at
```

If the hash is missing, mismatched, unverifiable, or stale relative to the pointer, raw-supported admission fails closed.

### R6. Manifest-only posture must be explicit

If a payload is not retained or is purged, the manifest must clearly say why raw support is unavailable.

Allowed support-status examples:

```text
manifest_only
capture_and_purged
raw_not_retained
no_raw_storage_allowed
raw_blocked_by_rights
raw_expired_by_retention
```

Manifest-only status must not pretend raw support exists.

### R7. Raw payloads containing customer/private data are blocked

If a raw payload contains prohibited customer records, private analytics, seller dashboards, order data, private messages, report workflow state, credentials, or other excluded data, it must not enter durable raw archive.

The package must fail closed or purge according to the applicable contract.

### R8. Provider and capture output must remain attributed

Raw payload manifests must preserve enough attribution to explain:

```text
provider_or_capture_instrument
source_family
endpoint_or_surface
capture_method
captured_at
provider_reported_time if available
request or panel context where allowed
```

Provider output must never be treated as unqualified truth.

### R9. Shape fingerprints gate parser safety

Where raw payloads are parser candidates, the system must record or resolve a shape fingerprint before normal parsing/admission.

Unknown or unreviewed shapes must not silently produce admitted observations.

### R10. Provider error payloads are not normal observations

Error, throttle, quota, auth failure, empty invalid, blocked, or malformed provider responses must be classified as capture/provider status, not parsed as normal observations.

### R11. Breaking drift blocks observation admission

If required fields are missing, renamed, type-changed, semantically changed, or otherwise unsafe, candidate observation admission must be blocked until review.

### R12. Compatible extensions do not automatically become hot-path fields

New provider fields may be preserved in retained raw payloads when retention allows, but they are not automatically admitted as structured observation fields, metrics, claims, or reportable evidence.

### R13. Parser output must preserve parser version and warnings

A parser that produces candidate observations must preserve:

```text
parser_name or parser_family
parser_version
shape_fingerprint
parser_status
validation_status
validation_warnings
```

Parser warnings must not be hidden from future read/hammers when they affect evidence fitness.

### R14. Parser must not invent missing values

A parser must not infer missing timestamps, ranks, scores, citations, URLs, provider metrics, or absences merely because expected fields are missing.

Missing required values produce warnings, quarantine, or block behavior.

### R15. Drift does not rewrite history

Existing evidence IDs remain historical handles if they were valid when admitted. New provider drift does not silently mutate old evidence.

If drift reveals a parser bug or invalid historical evidence, the affected evidence must route through status/supersession/invalidated behavior, not invisible overwrite.

### R16. Raw purge behavior must be auditable where allowed

If raw payloads must be purged, the system should preserve purge status and proof only to the extent rights/retention permit.

Candidate fields:

```text
purge_due_at
purged_at
purge_reason
purge_actor
payload_unavailable_reason
manifest_retained
```

### R17. Raw archive cannot hide strategy or recommendations

No raw archive manifest, notes, parser warning, drift note, or request context field may store recommendations, opportunity scores, accepted conclusions, strategy, customer workflow state, or agent action decisions.

### R18. Raw archive access must be shaped and bounded

Future typed read tools may expose raw support status, hashes, and caveats where allowed. They must not expose credentials, internal unrestricted file paths, private customer data, or raw payload content by default.

### R19. Field lists are behavior requirements, not schema

All fields in this contract are contract-level requirements. M10 may derive schema only after contracts and hammers justify it.

---

## Required fields / shapes

### Raw payload manifest shape

```text
raw_payload_id
capture_package_id
capture_id
provider_or_capture_instrument
source_family
endpoint_or_surface
request_context_pointer if allowed
captured_at
provider_reported_time if available
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_media_type
raw_payload_encoding
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at
raw_retention_posture
raw_support_status
redaction_status
purge_status
purged_at
shape_fingerprint
shape_fingerprint_version
parser_version_first_seen
parser_status
validation_status
validation_warnings
```

### Raw retention posture vocabulary

```text
retain_raw_payload
retain_manifest_only
capture_and_purge_raw
no_raw_storage
forbidden_no_capture
```

### Raw support status vocabulary

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

### Drift status vocabulary

```text
known_shape
new_shape_seen
compatible_extension
breaking_change
semantic_change_suspected
provider_error_shape
unknown_unclassified
```

### Parser status vocabulary

```text
not_parsed
parse_ready
parsed_with_warnings
parsed_validated
blocked_unknown_shape
blocked_breaking_change
blocked_provider_error_shape
blocked_hash_failure
blocked_rights_or_retention
blocked_private_data
```

### Shape fingerprint shape

```text
shape_fingerprint
shape_fingerprint_version
schema_family_guess
field_path_set_hash
field_type_set_hash
enum_value_set_hash if applicable
required_field_presence
optional_field_presence
sample_payload_sha256
first_seen_at
last_seen_at
provider_version if available
endpoint_version if available
```

---

## Fail-closed behavior

### Missing rights or retention

If rights or retention are missing, unknown, ambiguous, or incompatible with raw retention:

```text
raw_retention_posture: forbidden_no_capture or no_raw_storage
raw_support_status: raw_blocked_by_rights
observation_admission: blocked
```

### Missing hash for retained raw

If raw payload is retained but hash is missing or unverifiable:

```text
raw_support_status: raw_hash_mismatch or raw_missing_or_unavailable
parser_status: blocked_hash_failure
observation_admission: blocked
```

### Unknown payload shape

If shape fingerprint is unknown:

```text
drift_status: unknown_unclassified
parser_status: blocked_unknown_shape
observation_admission: blocked or quarantine-only
```

### Breaking provider drift

If breaking drift is detected:

```text
drift_status: breaking_change
parser_status: blocked_breaking_change
observation_admission: blocked
```

### Provider error shape

If payload is an error/throttle/quota/auth/invalid payload:

```text
drift_status: provider_error_shape
parser_status: blocked_provider_error_shape
observation_admission: blocked
```

### Private/customer data detected

If raw payload contains prohibited customer/private data:

```text
parser_status: blocked_private_data
raw_retention_posture: no_raw_storage or forbidden_no_capture
purge_required: true where allowed
observation_admission: blocked
```

### Purged payload

If payload was purged according to retention:

```text
raw_support_status: capture_and_purged or manifest_only
payload_unavailable_reason: purge_by_retention
```

Read tools must not imply raw support is still available.

---

## Forbidden patterns

This contract forbids:

```text
raw blob now, rights later
keep every provider response forever
mystery JSON table
raw payload as observation
raw payload as strategy cache
raw archive as customer data lake
raw payload ID as citation handle
provider job ID as evidence ID
parser inventing missing timestamps
parser treating missing citation field as absence proof
provider error payload parsed as normal result
new provider field automatically becoming product metric
silent parser coercion
silent schema mutation from provider drift
silent overwrite of historical evidence after drift
raw path exposed to customer report
raw archive retaining customer first-party exports
```

Fake-mustache variants are also forbidden:

```text
raw_evidence_truth_store
provider_truth_json
strategy_payload_archive
customer_overlay_archive
ai_visibility_raw_truth
rank_truth_payload
opportunity_raw_cache
```

---

## Examples

### Valid planning example - raw retained only after clearance

```text
raw_payload_id: raw_dataforseo_serp_20260710_4c91aa
source_family: serp_observation
provider_or_capture_instrument: dataforseo_candidate
rights_class: provider_clarification_required
retention_class: retain_until_review
raw_retention_posture: retain_manifest_only
raw_support_status: manifest_only
```

Why valid as planning shape:
It does not claim durable raw retention. It records that provider clarification is needed before stronger retention or admission.

### Invalid - raw retained while rights unknown

```text
rights_class: unknown
retention_class: retain_project_evidence
raw_payload_pointer: /raw/provider/full-response.json
raw_support_status: raw_retained
```

Why invalid:
Unknown rights cannot support durable raw retention.

### Valid - provider drift blocks parser

```text
drift_status: breaking_change
parser_status: blocked_breaking_change
validation_warnings: required rank field missing from provider response shape
```

Why valid:
The payload is treated as drift/review evidence, not silently parsed into fake observations.

### Invalid - provider error parsed as observation

```text
provider_response: quota_exceeded
parser_status: parsed_validated
candidate_observation_count: 1
```

Why invalid:
A quota error is capture/provider status, not a SERP observation.

### Valid - purged raw with manifest only

```text
raw_support_status: capture_and_purged
purged_at: 2026-07-10T15:00:00Z
payload_unavailable_reason: retention_class_capture_and_purge
manifest_retained: true
```

Why valid:
The raw support limitation is explicit and does not pretend the payload remains available.

### Invalid - customer analytics raw archive

```text
source_family: customer_gsc_export
scope_class: customer_engagement
raw_payload_pointer: /raw/customer/gsc-export.csv
retention_class: retain_project_evidence
```

Why invalid:
Customer first-party data is overlay-only under current law and must not be stored as raw Observatory evidence.

---

## Owner-ruling candidates

Open rulings carried forward:

- durable raw payload retention posture by source family;
- manifest-only retention rules;
- capture-and-purge exceptions;
- purge proof requirements;
- raw archive layout choice;
- local-only versus cloud-backed raw archive posture;
- provider-specific raw payload recipes;
- raw pointer exposure outside internal tools;
- provider drift fingerprint implementation admission.

Default until ruled:

```text
raw retention is not admitted
manifest-only may be planned but not implemented
provider-specific recipes are blocked until M13
raw pointer exposure is internal/blocked
parser implementation is not authorized
```

---

## Deeper-research blockers

Relevant blockers:

- DR1 - DataForSEO endpoint-by-endpoint payload behavior.
- DR2 - Raw payload retention and allowed-use interpretation.
- DR8 - Manual capture and browser-extension capture admissibility.
- DR13 - Raw archive layout and provider drift fingerprints.
- DR14 - Evidence ID, citation handle, and report-safe reference finalization.
- DR17 - Provider credential and secret handling posture.

This contract is enough for M7 planning and M8 hammer input. It is not enough for provider admission, parser implementation, object storage, or raw archive build.

---

## Hammer expectations

M8+ must prove this contract with hostile-path hammers.

Required categories:

- H2 - rights fail-closed;
- H3 - retention fail-closed;
- H4 - customer/private data rejection;
- H5 - no strategy/recommendation storage;
- H6 - CapturePackage validation;
- H7 - provider spend and duplicate task controls where raw capture is paid;
- H8 - provider attribution/disagreement;
- H12 - raw archive integrity;
- H15 - evidence/citation integrity;
- H17 - LLM/agent access boundary;
- H18 - hostile/weird input;
- H19 - append-only/no silent overwrite;
- H20 - concurrency;
- H21 - audit-first enforcement;
- H22 - migration rollback/recovery once implementation is allowed.

Specific hostile paths:

```text
retain raw with unknown rights -> reject
retain raw beyond retention class -> reject
missing hash for retained raw -> reject
hash mismatch -> block raw-supported evidence
provider error payload parsed as observation -> reject
unknown shape parsed normally -> reject
breaking drift admitted -> reject
parser invents missing rank/timestamp/citation -> reject
new provider field becomes metric automatically -> reject
customer GSC/Etsy Stats export retained as raw -> reject
raw payload ID used as citation handle -> reject
raw pointer exposed to customer report -> reject
strategy note hidden in raw manifest -> reject
old evidence silently overwritten after drift -> reject
purged raw still represented as raw_retained -> reject
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates;
- M10 - Schema Planning Only;
- M11 - Raw Archive Planning;
- M12 - First Evidence Slice Build;
- M13 - Provider Admission and Controlled Pull Plan;
- M14 - Typed Read API / MCP Contract and Prototype;
- M16 - Provider Cross-Check Proof;
- M19 - Hardening, Backup, Recovery, and Operations.

---

## Non-authorizations

This contract does not authorize:

```text
schema design
migrations
object storage implementation
raw archive implementation
parser implementation
provider admission
paid provider pulls
manual capture
browser-extension capture
marketplace capture
recurring capture
customer data handling
raw pointer exposure
API/MCP implementation
strategy/recommendation storage
```

---

## Final rule

```text
Raw payloads are evidence support, not a loophole.
If raw support exists, it must be hashed, pointed to, rights-cleared, retention-governed, and parser-safe.
Provider drift must become visible evidence, not silent corruption.
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG11 with supporting RG10 and existing M7 spine contracts
```
