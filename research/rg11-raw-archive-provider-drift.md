# RG11 — Raw Archive / Provider Drift

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What raw archive and provider drift rules are needed before provider payloads, parsers, or observations can be trusted?

---

## Sources checked

Local/current sources checked during RG11:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg8-claim-safety-report-language.md`
- `research/rg9-provider-cross-check-disagreement-model.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/deep-research-backlog.md`

No current external source was required for RG11 because this gate defines internal raw archive and provider drift contract inputs. Provider-specific drift behavior and raw payload examples remain deeper research/admission work.

---

## Current source-grounded findings

### F1 — Raw payloads are evidence support, not the observation model itself

The harvest register carries forward a raw / structured / derived three-layer rule, plus bucket/blob posture for large payloads using pointer + hash + promoted hot fields.

Implication:

- Raw payloads should support observations; they should not become mystery JSON storage.
- Structured observations should promote needed fields from raw payloads.
- Derived/read-time outputs should remain separate from raw and structured evidence.

---

### F2 — Rights and retention decide whether raw payloads may survive

RG2 says rights and retention fail closed. RG10 says raw support validation must fail if raw payloads are retained without rights or if retention exceeds approved class.

Implication:

- Raw payload retention is not automatic.
- Some sources may allow durable raw payload retention.
- Some sources may require capture-and-purge or no-storage overlay.
- Raw archive policy must be source-family and provider/instrument specific.

---

### F3 — Hashes and pointers are required for auditability when raw support exists

RG10 requires raw payload IDs, pointers, SHA-256 hashes, byte size, and creation time when raw payload retention is admitted.

Implication:

- Raw support must be content-addressable or at least hash-verifiable.
- Evidence should be able to prove which raw payload supported an observation.
- Raw payload mutation after capture should be treated as a serious integrity failure.

---

### F4 — Provider payloads can drift

The deep research backlog preserves raw archive layout and provider drift fingerprints as DR13. Provider payloads may change shape over time, and drift should become evidence instead of breakage.

Implication:

- Provider drift must be detectable.
- Parser failures caused by shape changes should not silently corrupt observations.
- New payload shapes should produce quarantine/review behavior before admission.

---

### F5 — Provider output remains testimony

RG9 says provider observations, provider scores, and provider values remain provider-attributed output, not web truth.

Implication:

- Raw payload archive must preserve provider identity, endpoint/surface, provider-reported timestamps, and request context.
- Provider drift is evidence about the provider/capture instrument, not automatic truth about the market.

---

## Proposed raw archive concept

A raw archive is the governed storage or pointer layer for original provider/capture payloads when retention is allowed.

It is not:

- a free JSON dump;
- a schema bypass;
- a strategy cache;
- a customer data lake;
- an implementation shortcut;
- permission to retain everything forever.

Correct pattern:

```text
CapturePackage -> raw payload pointer/hash if allowed -> parser -> candidate observations -> admitted observations/evidence
```

Forbidden pattern:

```text
raw blob -> keep forever -> parse later -> maybe figure out rights someday
```

---

## Proposed raw payload manifest fields

Candidate M7/M10 inputs:

```text
raw_payload_id
capture_package_id
capture_id
provider_or_capture_instrument
source_family
endpoint_or_surface
request_context_pointer
captured_at
provider_reported_time
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_media_type
raw_payload_encoding
retention_class
retention_basis
retention_expires_at
rights_class
rights_basis
redaction_status
purge_status
purged_at
shape_fingerprint
parser_version_first_seen
parser_status
validation_status
```

Rule:
A raw payload manifest may survive even when the payload itself must be purged, if rights/retention permit keeping the minimal manifest.

---

## Raw retention posture candidates

| posture | Meaning |
|---|---|
| `retain_raw_payload` | Payload retained under explicit rights/retention contract |
| `retain_manifest_only` | Payload purged or not stored; minimal manifest retained if allowed |
| `capture_and_purge_raw` | Payload temporarily retained then purged by deadline |
| `no_raw_storage` | Payload never persisted; only structured observation or overlay behavior allowed if permitted |
| `forbidden_no_capture` | Capture and storage blocked |

Rules:

- Default posture for unclear rights is `forbidden_no_capture`.
- If capture is approved but raw retention is not, use `retain_manifest_only`, `capture_and_purge_raw`, or `no_raw_storage` as source law allows.
- `retain_raw_payload` requires explicit source-family/provider retention clearance.

---

## Provider drift concept

Provider drift is a material change in provider/capture output that affects parsing, interpretation, comparability, or evidence integrity.

Examples:

- field added;
- field removed;
- field renamed;
- field type changed;
- enum vocabulary changed;
- nested object shape changed;
- timestamp semantics changed;
- score scale changed;
- endpoint/surface behavior changed;
- provider stops returning an expected field;
- provider starts returning a new source/citation format.

Provider drift is not automatically bad. It is evidence that the provider/capture surface changed.

---

## Proposed shape fingerprint fields

Candidate M7/M10 inputs:

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

Rule:
Shape fingerprints are for drift detection and parser safety. They are not claims about market reality.

---

## Drift statuses

| drift_status | Meaning | Behavior |
|---|---|---|
| `known_shape` | Payload shape matches accepted parser expectations | Eligible for normal parsing if rights/retention pass |
| `new_shape_seen` | New shape observed but not reviewed | Quarantine or parse in safe mode |
| `compatible_extension` | New fields added without breaking required fields | Preserve raw; parser may ignore until reviewed |
| `breaking_change` | Required fields missing/renamed/type-changed | Block observation admission |
| `semantic_change_suspected` | Same fields but meaning may have changed | Require review before claims |
| `provider_error_shape` | Provider returned error/throttle/invalid payload shape | Do not parse as normal observation |
| `unknown_unclassified` | Shape cannot be classified | Fail closed |

---

## Parser behavior rules

A parser should:

- verify raw payload hash before parse;
- verify expected provider/source family;
- verify shape fingerprint or known safe shape;
- produce candidate observations only when required fields are present;
- preserve parser version;
- attach validation warnings;
- block admission on breaking drift;
- never silently coerce missing fields into fake values;
- never parse provider error payloads as observations;
- never drop provider attribution.

A parser should not:

- infer missing timestamps;
- infer missing ranks/scores;
- replace missing citations with absence claims;
- treat new provider fields as admitted hot-path fields automatically;
- hide drift from read tools.

---

## Drift impact on evidence IDs

Initial rule candidates:

- Existing evidence IDs remain valid historical handles if the original observation was valid when admitted.
- New drift does not rewrite old evidence.
- If drift invalidates a parser bug, affected evidence may need `invalidated` status under RG3-style evidence status.
- If a new payload shape cannot be parsed safely, no new evidence IDs should be admitted from it.
- Shape changes should create provider/capture review work, not silent schema mutation.

---

## Purge and retention expectations

Raw archive contract must support:

```text
retention_expires_at
purge_due_at
purged_at
purge_reason
purge_actor
purge_proof_hash or manifest proof if available
payload_unavailable_reason
manifest_retained
```

Purge behavior must preserve enough audit trail to explain why raw support is unavailable, if retention law allows manifest retention.

If even manifest retention is not allowed, the package must record only what the active contract permits.

---

## Relationship to CapturePackage

RG10 CapturePackage is the admission envelope.

RG11 raw archive is the payload support and drift-safety layer inside or beside that envelope.

A CapturePackage should not be validated as raw-supported unless:

- raw payload retention posture is known;
- raw payload hash/pointer rules are satisfied;
- provider/capture shape is known or quarantined;
- parser status is safe;
- retention/purge expectations are clear.

---

## Relationship to Provider Cross-Check

Provider Cross-Check depends on trustworthy provider observations.

Raw archive and drift metadata help explain disagreement caused by:

- provider shape change;
- provider timestamp/freshness change;
- endpoint behavior change;
- missing fields;
- parser version differences;
- source coverage shifts.

Read tools should expose such caveats when comparing providers.

---

## No-nonsense checks

Before raw payloads or parsed observations are trusted, the system should answer:

1. Is raw retention allowed for this source?
2. What retention class applies?
3. Is the raw payload hash recorded?
4. Is the raw payload pointer recorded if retained?
5. Can the payload be verified against its hash?
6. What provider/capture instrument produced it?
7. What endpoint/surface produced it?
8. What shape fingerprint was observed?
9. Is the shape known, new, compatible, breaking, or unknown?
10. What parser version handled it?
11. Did parsing produce validation warnings?
12. Is this a provider error payload?
13. Does drift block observation admission?
14. If purged, is purge proof or manifest status recorded?
15. Does any raw payload include forbidden customer/private data?

If these cannot be answered, raw payload use must fail closed.

---

## Non-goals

RG11 does not authorize:

- schema design;
- migrations;
- object storage implementation;
- raw archive implementation;
- provider admission;
- paid provider pulls;
- raw payload retention;
- marketplace capture;
- parser implementation;
- recurring capture;
- customer data handling.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- choosing filesystem/object-store/database raw archive layout;
- admitting durable raw payload retention;
- defining manifest-only retention rules;
- admitting shape fingerprint implementation;
- deciding what purge proof is required;
- deciding whether raw archive is local-only or cloud-backed;
- allowing any provider-specific raw payload recipe.

---

## Deeper research carried forward

DR13 remains active for deeper raw archive layout and provider drift fingerprint proof.

DR2 remains active for raw payload retention and allowed-use interpretation.

DR1 remains active for DataForSEO endpoint-by-endpoint payload behavior.

RG11 answers enough for M7 contract planning, not enough for implementation.

---

## Blockers carried forward

- M7 must turn raw archive and drift expectations into contract language.
- M8 must hammer hash verification, retention fail-closed, purge behavior, new-shape quarantine, breaking-change rejection, and no mystery JSON storage.
- M10 must use the contract before schema planning.
- M13 must bind provider-specific payload and drift behavior before provider admission.

---

## Feeds later milestones

- M7 raw archive / provider drift contract
- M8 raw archive and parser drift hammers
- M10 schema planning
- M11 raw archive planning
- M13 provider/capture admission
- M14 typed read API / MCP contract

---

## Final RG11 rule

```text
Raw payloads are evidence support, not a loophole.
If raw support exists, it must be hashed, pointed to, rights-cleared, retention-governed, and parser-safe.
Provider drift must become visible evidence, not silent corruption.
```
