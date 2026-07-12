# Contract - CapturePackage v0.1

Status: accepted — contract set v0.1 by `decisions/2026-07-12-m14-contract-and-read-boundary-rulings.md`
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 - Core Contract Planning
Source research: `research/rg10-capturepackage-v0-1-inputs.md`, supported by `research/rg1-dataforseo-rights-retention-cost.md`, `research/rg2-scope-rights-retention-model.md`, `research/rg3-evidence-id-citation-model.md`, `research/rg4-query-panel-model.md`, `research/rg5-freshness-staleness-volatility.md`, `research/rg8-claim-safety-report-language.md`, `research/rg9-provider-cross-check-disagreement-model.md`, `research/rg11-raw-archive-provider-drift.md`, existing M7 contracts, and root boundary law
Supersedes / superseded by: none

---

## Purpose

This contract defines CapturePackage v0.1 as the required admission envelope around any future capture attempt, payload, candidate observation, or evidence-producing run.

A CapturePackage exists to prove scope, rights, retention, provenance, source/capture posture, timing, cost controls, raw-support posture, and validation status before any observation or evidence can be admitted.

It is not a schema migration, capture runner, provider admission decision, raw archive implementation, API/MCP spec, dashboard, customer report record, strategy record, or provider-spend approval.

---

## Governing boundaries

This contract operationalizes these rules:

- Observatory stores observations, not conclusions.
- No scope, no rights, no retention, no provenance, no admission.
- Provider/capture instruments must be admitted before use.
- Provider output is testimony, not truth.
- Rights and retention fail closed.
- Customer/private first-party data is not stored in Observatory.
- Raw payload retention is not automatic.
- Paid provider use requires explicit owner approval, cost ceiling, task/call ceiling, duplicate prevention, and stop conditions.
- Query panels define measurement context; they do not authorize execution.
- Evidence IDs are minted only from admitted observations/evidence, not from failed or blocked packages.
- Recommendations, strategy, opportunity, and accepted conclusions live outside Observatory.

On conflict, `02-boundaries.md` and accepted higher-order contracts win.

---

## Definitions

### CapturePackage

The proof envelope around a capture attempt. It carries the facts needed to decide whether a payload or candidate observation may become Observatory evidence.

Correct pattern:

```text
approved capture intent -> CapturePackage -> validation -> candidate observations -> admitted observations/evidence
```

Forbidden pattern:

```text
provider blob -> store JSON now -> figure out rights later
```

### Capture attempt

A provider call, manual capture, future browser-extension action, API request, public snapshot, or other attempt to observe a source surface.

M7 does not authorize any capture attempt to execute.

### Candidate observation

A parsed or proposed observation produced by a package before admission.

Candidate observations are not durable Observatory evidence until validation and later admission rules allow them.

### Admitted observation

An observation accepted under scope, rights, retention, provenance, source-admission, freshness, evidence-ID, and claim-safety contracts.

### Raw support

A retained raw payload, manifest, hash, pointer, or purge proof that supports a candidate or admitted observation where source law allows.

### Approval reference

A future reference to explicit human or owner approval for a paid, risky, retention-sensitive, marketplace, AI/GEO, browser-extension, manual-capture, or recurring capture path.

Approval references are not invented by this contract. They must be created by a future owner ruling or admission contract.

---

## Contract rules

### R1. CapturePackage is mandatory before observation admission

No future payload, provider response, manual capture, panel run, or candidate observation may become admitted evidence unless it is associated with a valid CapturePackage or an accepted future equivalent.

### R2. CapturePackage is not execution authority

A draft or valid package does not authorize capture execution, provider spend, manual capture, browser-extension use, recurring capture, marketplace capture, raw retention, or customer data handling.

### R3. Scope validation is required

Every package must include:

```text
scope_id
scope_class
owning_consumer if applicable
```

Missing or invalid scope blocks package validation.

### R4. Rights and retention validation is required

Every package must include:

```text
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at when applicable
```

Unknown, missing, ambiguous, or conflicting rights/retention blocks admission.

### R5. Provenance validation is required

Every package must include:

```text
captured_by
operator_intent
source_family
provider_or_capture_instrument
capture_method
captured_at
```

Missing provenance blocks validation. Provider/capture instrument candidate status is not admission.

### R6. Capture intent must be measurement-only

`capture_intent` and `operator_intent` may describe what will be observed and why the observation is needed.

They must not store recommendations, strategy, opportunity scoring, accepted conclusions, customer tasks, or report prose.

### R7. Paid/provider captures require explicit controls

For paid/provider captures, a package must include or resolve:

```text
approval_reference
cost_ceiling
call_or_task_ceiling
stop_conditions
duplicate_capture_check
actual_cost if known
calls_or_tasks_used
```

If these are missing, execution/admission fails closed.

### R8. Stop conditions must stop

If a stop condition is triggered, package processing must not continue into admitted observations unless a later owner-approved exception explicitly allows safe partial handling.

### R9. Query panel context must match

When a capture is tied to a query panel, prompt panel, or panel run, the package must preserve:

```text
query_panel_id
query_panel_version_id
panel_run_id when applicable
```

A mismatched, unknown, mutable, or blocked panel/version blocks execution/admission.

### R10. Raw support must obey raw-retention posture

A package may include raw payload IDs, pointers, hashes, and byte sizes only when raw support is allowed by rights/retention/source rules.

If raw retention is not allowed, the package must say so with an explicit raw-support status such as `raw_not_retained`, `capture_and_purged`, or `no_raw_storage_allowed`.

### R11. Raw hashes are required when raw payloads are retained

If a raw payload is retained, the package must preserve:

```text
raw_payload_id
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_created_at
```

Missing hash or pointer blocks raw-supported admission.

### R12. Candidate observations are not evidence IDs

A package may count or list candidate observations, but it must not mint active evidence IDs unless the downstream admission path validates scope, rights, retention, provenance, source, parser/raw support, freshness, and claim-safety constraints.

### R13. Failed or blocked packages do not produce admitted evidence

A package with status `blocked`, `failed`, `purged`, or validation failure may preserve allowed audit/provenance facts, but it must not create normal observations/evidence as if capture succeeded.

### R14. Customer/private data contamination blocks package admission

If a package contains customer private analytics, seller dashboard exports, order data, report records, messages, private channel analytics, or other excluded customer/private data, it must be rejected, purged, or routed to no-storage overlay behavior under future overlay rules.

### R15. Marketplace, AI/GEO, browser extension, manual capture, and provider captures remain blocked until admitted

A package may preserve planning-only candidate posture for these source families, but it must not execute or admit observations until the relevant source/capture admission gates clear.

### R16. Provider errors are not observations

Provider error payloads, throttles, empty/error statuses, authentication failures, billing failures, or blocked responses must not be parsed as normal observations.

### R17. Validation errors must be visible

A package must preserve validation errors or blockers enough for future hammers/read tools to explain why admission failed.

### R18. CapturePackage fields are contract requirements, not schema

This contract lists behavior and required context. It does not define physical tables, migrations, file layout, object storage, API endpoints, or implementation.

---

## Required fields / shapes

These are contract-level requirements, not schema approval.

### Top-level CapturePackage shape

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
owning_consumer when applicable
source_family
provider_or_capture_instrument
capture_method
endpoint_or_surface
query_panel_id when applicable
query_panel_version_id when applicable
panel_run_id when applicable
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at when applicable
freshness_status
volatility_class
provider_reported_time when available
cost_ceiling when applicable
actual_cost when known
call_or_task_ceiling when applicable
calls_or_tasks_used when known
stop_conditions when applicable
stop_condition_triggered
duplicate_capture_check when applicable
approval_reference when required
raw_support_status
raw_payload_id when applicable
raw_payload_pointer when applicable
raw_payload_sha256 when applicable
raw_payload_bytes when applicable
candidate_observation_count
candidate_evidence_count
validation_errors
claim_use_warning
```

Fields may be explicitly `not_applicable` only when a contract explains why. Required fields must not be silently missing.

### Capture status vocabulary

```text
draft
approved_for_capture
captured_pending_validation
validated
admitted
blocked
purged
failed
```

Status rules:

- `draft` means planning only.
- `approved_for_capture` requires future approval contract/ruling.
- `captured_pending_validation` means capture happened but observations are not admitted.
- `validated` means package checks passed, not that evidence is accepted forever.
- `admitted` requires downstream evidence admission rules.
- `blocked` means fail closed.
- `purged` means payload/data was purged by retention rule.
- `failed` means capture attempt failed.

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
not_applicable
```

### Validation group requirements

Every package must be validated against these groups:

```text
scope_validation
rights_retention_validation
provenance_validation
source_admission_validation
cost_approval_validation when applicable
query_panel_validation when applicable
raw_support_validation when applicable
freshness_claim_validation
customer_private_data_validation
strategy_contamination_validation
```

---

## Fail-closed behavior

### Missing scope

If scope is missing, unknown, or customer/private identity is embedded as Observatory identity, package validation fails.

### Missing rights or retention

If rights or retention is unknown, ambiguous, expired, blocked, or inconsistent with source family, package validation fails.

### Missing provenance

If capture actor, method, source, or captured_at is missing, package validation fails.

### Unadmitted source or instrument

If the provider/capture instrument/source family is not admitted, package cannot execute or admit observations.

### Missing approval for paid/risky capture

If approval, cost ceiling, task/call ceiling, duplicate check, or stop conditions are missing for a paid/risky capture, package cannot execute or admit observations.

### Raw support invalid

If raw payload retention is not allowed, missing, hash-invalid, expired, rights-blocked, or contaminated, raw-supported admission fails.

### Customer/private contamination

If excluded customer/private data appears, package fails closed and must not mint Observatory observations/evidence.

### Strategy contamination

If capture intent or package metadata contains recommendations, opportunity scores, or accepted conclusions, package fails closed until rewritten as measurement-only.

---

## Forbidden patterns

This contract forbids:

```text
provider blob now, rights later
hidden JSON dump table
CapturePackage as schema shortcut
CapturePackage as provider admission
CapturePackage as paid-pull approval
CapturePackage as marketplace scraping approval
CapturePackage as browser-extension approval
CapturePackage as recurring scheduler
CapturePackage as customer report record
CapturePackage as strategy cache
CapturePackage as recommendation store
raw payload retained without rights
candidate observation treated as admitted evidence
failed provider response parsed as observation
customer first-party export stored as raw payload
missing cost ceiling for paid provider call
missing duplicate check for paid provider call
stop condition triggered but capture continues
```

Fake-mustache variants are also forbidden:

```text
capture_intent = recommendation rationale
operator_intent = strategy note
validation_errors hidden from read tools
raw_payload_pointer as evidence citation
provider_task_id as evidence ID
blocked package with active evidence IDs
manual capture used to launder automation
```

---

## Examples

### Valid planning-only provider package

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
raw_support_status: not_applicable
```

Why valid:

- It is clearly planning-only.
- Provider is candidate, not admitted.
- It cannot execute or admit observations.

### Invalid provider blob with missing rights

```text
source_family: dataforseo_serp
raw_payload_pointer: /payloads/blob.json
rights_class: unknown
retention_class: retain_project_evidence
```

Why invalid:

- Unknown rights are treated as durable storage approval.
- Raw retention is not admitted.

### Invalid customer first-party capture

```text
source_family: etsy_stats
scope_class: customer_engagement
raw_payload_pointer: etsy_stats_export.csv
retention_class: retain_project_evidence
```

Why invalid:

- Customer first-party analytics are outside Observatory storage.
- Current posture is overlay/no-storage only.

### Invalid strategy hidden inside intent

```text
capture_intent: find best keywords and recommend title changes
operator_intent: prepare customer action plan
```

Why invalid:

- Capture intent must describe observation purpose, not recommendations or strategy.

### Valid blocked marketplace candidate

```text
capture_status: blocked
source_family: marketplace_search
provider_or_capture_instrument: browser_extension_candidate
capture_method: browser_extension_candidate
rights_class: provider_clarification_required
retention_class: forbidden_no_capture
validation_errors:
  - marketplace automation not admitted
  - platform-specific review required
```

Why valid:

- It preserves why the package cannot proceed.
- It does not execute or store observations.

---

## Owner-ruling candidates

Open rulings carried forward:

- final CapturePackage required field set;
- any authority for a package to execute;
- validation budget approval;
- paid provider approval and budget ceilings;
- duplicate-task prevention standard;
- raw payload retention admission;
- manual public observation capture admission;
- browser-extension capture admission;
- marketplace capture admission;
- capture-and-purge exception handling;
- AI/GEO source/capture package execution;
- purge proof expectations.

Default until ruled:

```text
CapturePackage can be drafted and validated conceptually.
CapturePackage cannot execute captures.
CapturePackage cannot authorize spend.
CapturePackage cannot admit raw retention.
CapturePackage cannot store customer/private data.
```

---

## Deeper-research blockers

This contract is enough for M7 planning but blocked from execution by:

- DR1 - DataForSEO endpoint-by-endpoint admission research.
- DR2 - Raw payload retention and allowed-use interpretation.
- DR4 - GEO / AI citation measurement methodology.
- DR5 - Google AI Overview / AI Mode capture and visibility limits.
- DR6 - Marketplace platform evidence limits: Etsy.
- DR7 - Marketplace platform evidence limits: Fiverr.
- DR8 - Manual capture and browser-extension capture admissibility.
- DR13 - Raw archive layout and provider drift fingerprints.
- DR15 - Hammer matrix hostile-path expansion.
- DR17 - Provider credential and secret handling posture.

Provider-specific fields, credentials, endpoint recipes, real payload examples, raw archive layout, and execution behavior are later milestone work.

---

## Hammer expectations

M8+ must test this contract with hostile paths.

Required hammer categories:

- H1 - scope isolation;
- H2 - rights fail-closed;
- H3 - retention fail-closed;
- H4 - customer/private data rejection;
- H5 - no strategy/recommendation storage;
- H6 - CapturePackage validation;
- H7 - provider spend and duplicate task controls;
- H9 - freshness and volatility;
- H10 - AI/GEO overclaim rejection;
- H11 - marketplace restrictions;
- H12 - raw archive integrity;
- H13 - provider drift quarantine;
- H14 - query panel immutability where package references panel versions;
- H15 - evidence/citation integrity;
- H16 - overlay no-storage;
- H17 - LLM/agent access boundary;
- H18 - hostile weird input;
- H19 - append-only/no silent overwrite;
- H20 - concurrency for duplicate captures and stop conditions;
- H21 - audit-first enforcement.

Specific hostile paths:

```text
Package missing scope -> reject.
Package missing rights -> reject.
Package missing retention -> reject.
Package missing captured_at -> reject.
Package contains customer private analytics -> reject.
Package contains strategy in capture_intent -> reject.
Paid provider package without approval/cost ceiling/task ceiling -> reject.
Duplicate paid capture without duplicate check -> reject.
Stop condition triggered but package continues -> reject.
Unadmitted browser-extension marketplace package -> reject.
Raw payload retained without raw rights -> reject.
Raw hash missing or mismatched -> reject raw-supported admission.
Provider error payload parsed as observation -> reject.
Blocked package mints active evidence ID -> reject.
Panel version mismatch -> reject.
```

---

## Feeds milestones

This contract feeds:

- M8 - Hammer Matrix and Acceptance Gates.
- M9 - First Evidence Slice Definition.
- M10 - Schema Planning Only.
- M12 - First Evidence Slice Build.
- M13 - Provider Admission and Controlled Pull Plan.
- M14 - Typed Read API / MCP Contract and Prototype.
- M15 - SearchClarity Proof Workflow.
- M19 - Hardening, Backup, Recovery, and Operations.

---

## Non-authorizations

This contract does not authorize:

```text
schema design
migrations
provider admission
provider pulls
paid spend
credential handling
manual capture admission
browser-extension admission
marketplace capture
AI/GEO capture
raw archive implementation
object storage
parser implementation
capture runner implementation
recurring capture
API/MCP implementation
dashboard work
customer data handling
customer-facing reports
strategy/recommendation storage
```

---

## Final rule

```text
A CapturePackage is not a payload dump.
It is the proof envelope around a capture attempt.
No scope, no rights, no retention, no provenance, no admission.
No approval, no spend.
No boundary clarity, no storage.
```

---

## Change log

```text
0.1 - 2026-07-10 - initial draft from RG10 with supporting M7 contract and RG11 raw-support inputs
```
