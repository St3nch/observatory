# RG10 — CapturePackage v0.1 Inputs

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What fields must every future capture package contain before raw payloads or observations can be admitted?

---

## Sources checked

Local/current sources checked during RG10:

- `02-boundaries.md`
- `01-harvest-register.md`
- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg2-scope-rights-retention-model.md`
- `research/rg3-evidence-id-citation-model.md`
- `research/rg4-query-panel-model.md`
- `research/rg5-freshness-staleness-volatility.md`
- `research/rg8-claim-safety-report-language.md`
- `research/rg9-provider-cross-check-disagreement-model.md`

No current external source was required for RG10 because this gate defines internal capture package inputs from prior gates. Provider/platform-specific additions remain deferred to provider/capture admission.

---

## Current source-grounded findings

### F1 — Capture inputs must prove scope, rights, retention, and provenance before observation storage

`02-boundaries.md` says future observations must be scoped, rights-labeled, retention-labeled, provenance-complete, captured through approved methods, and allowed by the active roadmap gate.

Implication:

- A CapturePackage cannot be a loose blob of provider response data.
- It must prove it is allowed to exist before any observation is admitted.
- Missing scope, rights, retention, or provenance must fail closed.

---

### F2 — Provider spend and duplicate capture need explicit controls

RG1 says DataForSEO remains plausible but not admitted, and later validation must include exact endpoint family, task count ceiling, dollar ceiling, duplicate prevention, stop conditions, and owner approval.

Implication:

- CapturePackage must carry cost and approval metadata for paid sources.
- Duplicate capture prevention must be part of the package contract.
- A capture package cannot silently spend or repeat provider tasks.

---

### F3 — Evidence IDs, raw payload pointers, and hashes are separate concerns

RG3 distinguishes capture IDs, raw payload IDs, observation IDs, evidence IDs, citation handles, and report-safe references.

Implication:

- CapturePackage should identify the capture event and raw support.
- Observation and evidence IDs may be produced after parsing/admission.
- Raw payload pointer/hash must be included when raw support exists and retention permits it.

---

### F4 — Query panels define the measurement context

RG4 says panel versions are immutable once used for observations, and panel runs connect panel versions to captures.

Implication:

- CapturePackage should reference query panel/version/run when applicable.
- CapturePackage should not mutate the panel.
- A capture package produced from an unknown or mismatched panel should be blocked or quarantined.

---

### F5 — Freshness and claim safety start at capture time

RG5 requires captured_at, provider-reported time where available, freshness status, volatility class, and recapture warnings. RG8 requires claim-use warnings.

Implication:

- CapturePackage must preserve timing enough for future read tools.
- CapturePackage must not merely store results; it must preserve context needed to avoid overclaims.

---

## Proposed CapturePackage v0.1 concept

A CapturePackage is the admission envelope around a capture attempt, raw payload, and any candidate observations.

It is not:

- a schema migration;
- a provider admission decision;
- a capture runner;
- a raw payload archive by itself;
- a strategy record;
- a recommendation;
- a customer report record.

Correct pattern:

```text
approved capture intent -> CapturePackage -> validation -> candidate observations -> admitted observations/evidence
```

Forbidden pattern:

```text
provider response blob -> hidden JSON table -> later we figure out rights/provenance
```

---

## Required top-level fields

Candidate minimum fields for M7 contract planning:

```text
capture_package_id
capture_id
capture_package_version
capture_status
capture_intent
operator_intent
created_at
captured_at
captured_by
capture_actor_type
scope_id
scope_class
source_family
provider_or_capture_instrument
capture_method
endpoint_or_surface
query_panel_id
query_panel_version_id
panel_run_id
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at
freshness_status
volatility_class
provider_reported_time
cost_ceiling
actual_cost
call_or_task_ceiling
calls_or_tasks_used
stop_conditions
stop_condition_triggered
approval_reference
raw_payload_id
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
candidate_observation_count
candidate_evidence_count
validation_errors
claim_use_warning
```

Rule:
Fields may be explicitly `not_applicable`, but must not be silently missing when required by the source family.

---

## Required validation groups

### Scope validation

Required:

```text
scope_id
scope_class
owning_consumer if applicable
```

Fail if:

- scope is missing;
- scope_class is unknown;
- customer identity is embedded in scope fields;
- consumer foreign keys are used as Observatory identity;
- scope_class conflicts with source family.

---

### Rights and retention validation

Required:

```text
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at when applicable
```

Fail if:

- rights are unknown;
- retention is unknown;
- ambiguous rights are treated as approval;
- customer first-party data is assigned durable retention;
- source-specific retention restrictions are missing.

Allowed fail-closed outputs:

```text
forbidden_no_capture
capture_and_purge
no_storage_overlay_only
provider_clarification_required
legal_review_required
```

---

### Provenance validation

Required:

```text
captured_by
operator_intent
source_family
provider_or_capture_instrument
capture_method
captured_at
```

Fail if:

- capture actor is missing;
- operator intent is missing;
- provider/capture instrument is not admitted for the source family;
- capture method does not match source rights;
- timestamps are missing.

---

### Cost and approval validation

Required for paid/provider captures:

```text
approval_reference
cost_ceiling
call_or_task_ceiling
stop_conditions
actual_cost if known
calls_or_tasks_used
```

Fail if:

- approval is absent;
- endpoint/surface is not explicitly allowed;
- dollar ceiling is missing;
- task ceiling is missing;
- duplicate capture check is missing;
- stop condition is triggered but capture continues.

---

### Raw support validation

Required when raw payload retention is admitted:

```text
raw_payload_id
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_created_at
```

Fail if:

- hash is missing;
- pointer is missing;
- raw payload is retained without rights;
- raw payload contains prohibited customer/private data;
- raw payload retention exceeds approved class.

If raw retention is not admitted:

```text
raw_payload_pointer: not_retained
retention_class: capture_and_purge or no_storage_overlay_only or forbidden_no_capture
```

---

## Capture status vocabulary

Candidate statuses:

| status | Meaning |
|---|---|
| `draft` | Package prepared but not approved/executed |
| `approved_for_capture` | Human-approved under later contract; not available until approval contract exists |
| `captured_pending_validation` | Payload/candidate observations exist but are not admitted |
| `validated` | Package passed contract checks |
| `admitted` | Observations/evidence admitted under later contract |
| `blocked` | Package failed validation before admission |
| `purged` | Payload/data purged according to retention rule |
| `failed` | Capture attempt failed |

Caution:
`approved_for_capture` and `admitted` require future contracts. RG10 does not create that authority.

---

## Invalid examples

### Invalid — provider blob with missing rights

```text
source_family: dataforseo_serp
raw_payload_pointer: /payloads/blob.json
rights_class: unknown
retention_class: retain_project_evidence
```

Why invalid:
Rights are unknown, but package tries durable retention.

---

### Invalid — customer first-party data stored as observation

```text
source_family: etsy_stats
scope_class: customer_engagement
retention_class: retain_project_evidence
raw_payload_pointer: etsy_stats_export.csv
```

Why invalid:
Customer first-party data is overlay-only under current law.

---

### Invalid — paid provider capture without ceiling

```text
provider_or_capture_instrument: dataforseo
approval_reference: missing
cost_ceiling: missing
call_or_task_ceiling: missing
```

Why invalid:
No human approval, no spend ceiling, no task ceiling.

---

### Invalid — marketplace capture without platform clearance

```text
source_family: etsy_marketplace_search
capture_method: browser_extension
rights_class: not_expressly_prohibited
```

Why invalid:
RG7 says Etsy automation is blocked by default unless expressly authorized.

---

### Invalid — strategy hidden inside capture intent

```text
capture_intent: find best keywords and recommend title changes
```

Why invalid:
Capture intent may state observation purpose, not strategy/recommendation output.

---

## Valid-ish planning examples

### Planning-only DataForSEO SERP validation package

```text
capture_status: draft
source_family: serp_observation
provider_or_capture_instrument: dataforseo_candidate
capture_method: provider_api_candidate
scope_class: internal
rights_class: provider_clarification_required
retention_class: retain_until_review
cost_ceiling: proposed_only
approval_reference: not_approved
```

Meaning:
This is planning metadata only. It cannot execute.

---

### Manual public observation candidate

```text
capture_status: draft
source_family: manual_public_observation
capture_method: human_manual_note_candidate
scope_class: market_watch
rights_class: not_expressly_prohibited
retention_class: retain_until_review
operator_intent: observe public result presence for research gate
```

Meaning:
May be a candidate only if later manual-capture contract admits it.

---

## Human approval hooks

Future CapturePackage contract should support approval references such as:

```text
approval_reference
approval_actor
approval_time
approved_endpoint_or_surface
approved_scope
approved_cost_ceiling
approved_task_ceiling
approved_retention_class
approved_stop_conditions
```

Approval must be explicit for:

- paid provider use;
- validation budget use;
- raw payload retention;
- capture-and-purge exceptions;
- marketplace public capture;
- AI answer-surface validation;
- recurring capture.

---

## Relationship to later milestones

### M7

Turns CapturePackage into contract language.

### M8

Hammers missing scope, missing rights, missing retention, missing provenance, duplicate paid task, cost ceiling, bad marketplace capture, and hidden strategy.

### M10

Uses the contract to plan schema, if earned.

### M13

Uses provider-admission decisions to fill provider-specific capture fields.

### M14

Read tools expose capture context and validation caveats.

---

## Non-goals

RG10 does not authorize:

- schema design;
- migrations;
- provider admission;
- paid provider pulls;
- marketplace capture;
- browser-extension capture;
- raw payload archive implementation;
- capture runner implementation;
- dashboard work;
- customer data handling;
- strategy/recommendation storage.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- finalizing CapturePackage required fields;
- allowing any capture package to execute;
- using validation budget;
- admitting raw payload retention;
- admitting manual public observation capture;
- admitting capture-and-purge exceptions;
- admitting any provider/capture instrument.

---

## Blockers carried forward

- M7 must convert CapturePackage v0.1 into contract.
- M8 must hammer fail-closed package validation.
- RG11 must refine raw archive and provider drift expectations.
- M13 must bind provider-specific fields before any provider use.

---

## Feeds later milestones

- M7 CapturePackage contract
- M8 capture validation hammers
- M10 schema planning
- M11 raw archive planning
- M13 provider/capture admission
- M14 typed read API / MCP contract

---

## Final RG10 rule

```text
A CapturePackage is not a payload dump.
It is the proof envelope around a capture attempt.
No scope, no rights, no retention, no provenance, no admission.
No approval, no spend.
No boundary clarity, no storage.
```
