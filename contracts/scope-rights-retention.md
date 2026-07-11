# Contract — Scope / Rights / Retention

Status: draft
Authority: contract (binds only when accepted; subordinate to `02-boundaries.md`)
Version: 0.1
Date: 2026-07-10
Milestone: M7 — Core Contract Planning
Source research: `research/rg2-scope-rights-retention-model.md`
Supporting inputs: `02-boundaries.md`, `01-harvest-register.md`, `research/rg1-dataforseo-rights-retention-cost.md`, `research/rg7-marketplace-evidence-ceiling.md`, `research/rg10-capturepackage-v0-1-inputs.md`, `research/rg11-raw-archive-provider-drift.md`, `research/rg12-consumer-contract-inputs.md`, `research/rg13-hammer-matrix-inputs.md`, `planning-inbox/m7-owner-rulings-and-dependency-parking-lot.md`, `planning-inbox/owner-ruling-tracker.md`
Supersedes / superseded by: none

---

## Purpose

This contract defines the scope, source-admission posture, rights, and retention behavior that every future Observatory observation must satisfy before it can be admitted, stored, cited, or exposed through read tools.

It exists before schema, provider admission, capture runners, API/MCP work, or consumer integration so the project does not accidentally store data whose scope, rights, retention, or source posture is unknown.

This is a non-schema contract. It does not authorize tables, migrations, provider pulls, provider purchases, manual capture, browser-extension capture, raw archives, customer data handling, or implementation.

---

## Governing boundaries

This contract operationalizes these boundary-law rules from `02-boundaries.md`:

- Observatory stores observations, not conclusions.
- In-scope observations must be scoped, rights-labeled, retention-labeled, provenance-complete, and captured through approved methods.
- Customer records and customer private first-party data stay outside Observatory.
- Customer first-party data may be supplied later only as read-time overlay unless explicit owner ruling changes project law.
- Internal first-party telemetry is not admitted merely because it is owned; it requires explicit internal-scope handling.
- Provider data is observed testimony, not truth.
- Rights and retention fail closed.
- LLMs and agents receive shaped evidence packs, not direct database access or credentials.
- Hammer tests are a hard gate before implementation acceptance.

On conflict, `02-boundaries.md` wins.

---

## Definitions

### `scope`

An Observatory-local label or identifier that says where an observation belongs.

A scope is not a customer record, consumer database foreign key, report record, order record, or workflow record.

### `scope_class`

Initial allowed values, imported from RG2:

| scope_class | Meaning | Current posture |
|---|---|---|
| `internal` | Owner-controlled internal properties, experiments, or market evidence programs | Valid scope class; internal first-party telemetry still requires future explicit handling |
| `customer_engagement` | Public evidence observed for, about, or around a customer engagement while customer records remain in the consumer system | Valid only for public observations under approved methods; not customer records/private analytics |
| `market_watch` | Non-customer or pre-project watch scope for observing a market, niche, SERP set, topic, platform, or evidence panel | Valid for public/market evidence under source and rights rules; not a cross-customer aggregation exception |

Adding a new `scope_class` requires owner ruling.

### `owning_consumer`

The consumer boundary that owns downstream meaning, workflow, reports, or decisions. Examples include `searchclarity`, `neon_ronin`, `kaizen`, `internal`, or `observatory`.

The owning consumer may be referenced as a boundary label or external locator. It must not become an Observatory foreign key to another system's customer/project/workflow table.

### `source_family`

A broad category of source or surface, such as SERP observation, AI/GEO answer surface, public page snapshot, marketplace public observation, provider API testimony, customer overlay, or internal telemetry candidate.

### `provider_or_capture_instrument`

The provider, API, manual process, browser extension, CLI probe, or other capture instrument that produced or would produce the observation.

A named provider or instrument is not admitted merely because it is named.

### `source_admission_status`

Contract-level status describing whether a source family or capture instrument may be used.

Candidate values:

| status | Meaning |
|---|---|
| `admitted` | Source/instrument is admitted by the relevant future decision/contract/gate |
| `candidate` | Source/instrument is under consideration only |
| `blocked` | Source/instrument is blocked under current boundaries or source rules |
| `owner_ruling_required` | Cannot proceed until explicit owner ruling |
| `provider_clarification_required` | Cannot proceed until provider/platform clarification |
| `legal_review_required` | Cannot proceed until legal review or equivalent owner decision |
| `not_applicable_overlay` | Source is overlay-only and not stored by Observatory |
| `not_yet_reviewed` | No admission review exists; fail closed |

### `rights_class`

Initial rights vocabulary, imported from RG2:

| rights_class | Meaning | Default behavior |
|---|---|---|
| `expressly_permitted` | Source/provider/platform explicitly permits capture/storage/reuse under defined conditions | Allowed only within stated conditions |
| `expressly_restricted` | Source/provider/platform explicitly restricts relevant capture/storage/reuse | Block or purge as required |
| `not_expressly_prohibited` | No explicit prohibition found, but no explicit grant either | Requires caution and source-specific handling; not broad storage permission |
| `not_expressly_granted` | Permission is not clear enough for intended use | Fail closed unless owner-approved capture-and-purge applies |
| `provider_clarification_required` | Terms/docs are ambiguous and provider clarification is needed | Block until clarified |
| `legal_review_required` | Risk or ambiguity is high enough that legal review or explicit owner risk decision is needed | Block until resolved |

### `retention_class`

Initial retention vocabulary, imported from RG2:

| retention_class | Meaning | Notes |
|---|---|---|
| `retain_until_review` | Preserve only until human/provider-rights review resolves retention | Temporary planning/review posture; not durable evidence approval |
| `retain_with_source_terms` | Retain according to provider/platform/source terms | Requires source-specific term binding |
| `retain_project_evidence` | Retain as durable Observatory evidence | Requires rights clearance and owner-approved contract |
| `capture_and_purge` | Capture temporarily, then purge within explicit window | Requires purge deadline and approval |
| `no_storage_overlay_only` | Do not store; use only as ephemeral read-time overlay | Required for customer first-party data under current law |
| `forbidden_no_capture` | Do not capture or store | Default for prohibited/high-risk cases |

### `rights_basis` / `retention_basis`

The source, ruling, contract, provider term, capture rule, or review note that explains the assigned rights or retention class.

These fields must not contain customer private data, recommendations, strategy, or accepted conclusions.

---

## Contract rules

R1. Every stored Observatory observation must have a `scope`, `scope_class`, `rights_class`, `rights_basis`, `retention_class`, and `retention_basis` before admission.

R2. Scope identity is Observatory-local. Customer names, customer emails, customer order IDs, customer report IDs, seller account IDs, or consumer database primary keys must not be used as Observatory scope identity.

R3. The only initial `scope_class` values are `internal`, `customer_engagement`, and `market_watch`. New values require owner ruling.

R4. `customer_engagement` may describe public evidence observed for or around an engagement, but it must not store customer records, private files, customer first-party analytics, orders, report records, consent records as primary system of record, seller dashboards, private messages, or customer workflow state.

R5. Customer first-party data is `no_storage_overlay_only` under current law. Observatory must not persist the overlay series, assign durable Observatory evidence IDs to private overlay rows, or promote overlay values into stored observations.

R6. `internal` is not a free pass. Owner-internal first-party telemetry requires future internal-scope rules, access controls, read behavior, and hammers before storage. Until then, internal scope may only support allowed public/internal market observations under normal source rules.

R7. `market_watch` does not authorize cross-customer aggregation or reusable business intelligence across customer scopes. Cross-scope aggregate analysis remains forbidden by default unless owner ruling creates a governed exception.

R8. Unknown, missing, ambiguous, or stale rights do not permit durable storage. Rights fail closed.

R9. `not_expressly_prohibited` is not broad permission. It may support narrow review only if the source family, capture method, retention posture, and owner-approved caution are explicit.

R10. Source-specific restrictions override generic rights and retention classes.

R11. `provider_clarification_required`, `legal_review_required`, `not_expressly_granted`, and `expressly_restricted` block capture/admission unless a narrower owner-approved path such as `capture_and_purge` is explicitly allowed.

R12. `capture_and_purge` requires a purge deadline, purge expectation, and approval basis. Without those, it fails closed.

R13. `no_storage_overlay_only` forbids persistence of the supplied payload or series. Later read-tool overlay behavior must prove discard/no-storage under hammers.

R14. `forbidden_no_capture` blocks capture, storage, raw retention, evidence ID minting, and read-tool use as Observatory evidence.

R15. Raw payload retention is not admitted by this contract. Durable raw retention requires rights/retention clearance plus the later raw archive/provider drift contract and relevant owner rulings.

R16. Provider/capture-instrument candidate status is not admission. DataForSEO, Ahrefs, Semrush, YouTube APIs, marketplace APIs, browser extensions, Hermes, manual capture workflows, or any other source/instrument require later admission before use.

R17. Paid provider capture additionally requires owner approval, exact endpoint/surface list, cost ceiling, task/call ceiling, duplicate-task prevention, stop conditions, and credential/secret posture. This contract does not approve spend.

R18. Strategy, recommendations, opportunity scores, accepted conclusions, customer workflow state, or agent task decisions must not be stored in `scope_label`, `notes`, `operator_intent`, `rights_basis`, `retention_basis`, raw payloads, or any adjacent metadata.

R19. If rights, retention, scope, or source-admission posture changes after evidence is admitted, current use must fail closed until later evidence-status, purge, supersession, or withdrawal rules decide the safe path.

R20. All fields and shapes in this contract are behavior requirements, not schema. M10 may derive schema only after contracts and hammers justify it.

---

## Required fields / shapes

These are contract-level requirements, not tables.

### Minimum stored-observation gate

A future stored observation must be able to answer:

```text
scope_id
scope_class
scope_label or scoped locator
owning_consumer when applicable
source_family
source_admission_status
provider_or_capture_instrument
capture_method
captured_at
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at when applicable
public/private surface classification
customer_private_data_indicator or equivalent rejection signal
```

Fields may be explicitly `not_applicable` only where a contract explains why. Required fields must not be silently absent.

### Scope concept shape

A future scope concept should be able to preserve:

```text
scope_id
scope_class
scope_label
owning_consumer
consumer_reference_kind
consumer_reference_value
status
created_at
notes
```

`consumer_reference_value` is a locator only. It must not become a customer database key or contain customer private data.

### Retention-expiring shape

Any retention posture that expires or purges must preserve enough information later to prove:

```text
retention_class
retention_basis
retention_expires_at or purge_due_at
purge expectation
payload_unavailable_reason if purged
manifest-retention permission if applicable
```

---

## Fail-closed behavior

- Missing `scope_id` or `scope_class` blocks admission.
- Unknown `scope_class` blocks admission.
- Customer identity in scope fields blocks admission or requires rejection/redaction before any storage path.
- Missing `rights_class` or `rights_basis` blocks admission.
- Missing `retention_class` or `retention_basis` blocks admission.
- Ambiguous rights default to `forbidden_no_capture` unless an explicit owner-approved `capture_and_purge` or `retain_until_review` path exists.
- `provider_clarification_required` and `legal_review_required` block durable evidence use.
- `no_storage_overlay_only` blocks persistence.
- Expired retention blocks current use and must route to later purge/withdrawal/status handling.
- Source family not admitted blocks observation admission.
- Boundary conflict blocks the lower-authority path; `02-boundaries.md` wins.

---

## Forbidden patterns

This contract forbids:

- using customer identity as scope identity;
- using consumer foreign keys as Observatory primary identity;
- storing customer records, orders, reports, consent records, or workflow state;
- storing customer GSC/GA4/Etsy Stats/Shopify analytics/seller dashboard/private conversion data;
- treating owner-internal first-party telemetry as automatically admitted;
- treating `market_watch` as a cross-customer aggregate exception;
- treating public visibility as storage permission;
- treating an API key or provider account as source admission;
- using `not_expressly_prohibited` as broad durable-storage approval;
- retaining raw payloads until rights are figured out;
- hiding recommendations, strategy, opportunity, or accepted conclusions in metadata;
- using rights/retention basis fields as legal theater after the fact;
- letting LLMs/agents bypass scope, rights, retention, or source-admission validation.

---

## Examples

### Valid contract shape — admitted public observation later

```text
scope_class: market_watch
source_family: public_page_snapshot
source_admission_status: admitted
capture_method: admitted_manual_capture
rights_class: expressly_permitted
rights_basis: accepted source-family rule
retention_class: retain_project_evidence
retention_basis: accepted source-family rule
```

Why valid:
The shape declares where the observation belongs, how it was captured, why it may be stored, and how it may be retained. This example is valid only after the referenced source family and capture method are actually admitted by later contract/ruling.

### Valid overlay posture — customer first-party data

```text
scope_class: customer_engagement
overlay_source_type: customer_gsc_export
retention_class: no_storage_overlay_only
source_admission_status: not_applicable_overlay
```

Why valid:
The data is not stored as Observatory evidence. It may only be supplied later to read tools as ephemeral overlay if a future overlay contract admits that behavior.

### Invalid — customer first-party data stored as evidence

```text
scope_class: customer_engagement
source_family: gsc_export
retention_class: retain_project_evidence
raw_payload_pointer: customer-gsc-export.csv
```

Why invalid:
Customer first-party analytics are outside Observatory storage under current boundary law.

### Invalid — unknown rights treated as permission

```text
source_family: public_marketplace_page
rights_class: not_expressly_granted
retention_class: retain_project_evidence
```

Why invalid:
Unclear rights fail closed. Durable retention is not allowed.

### Invalid — customer identity in scope

```text
scope_id: customer_jane_doe_etsy_shop_123
scope_class: customer_engagement
```

Why invalid:
Customer identity and account/workflow identifiers must not become Observatory scope identity.

### Invalid — provider candidate treated as admitted

```text
provider_or_capture_instrument: dataforseo
source_admission_status: candidate
capture_status: admitted
retention_class: retain_project_evidence
```

Why invalid:
Candidate status is not admission. Provider admission, endpoint recipe, rights, retention, spend, and stop conditions are later M13 work.

---

## Owner-ruling candidates

Open rulings relevant to this contract include:

| Ruling | Source tracker | Default before ruling |
|---|---|---|
| New `scope_class` beyond `internal`, `customer_engagement`, `market_watch` | OR-G3 | blocked |
| Cross-scope aggregate analysis exception | OR-G1 | forbidden by default |
| Capture-and-purge exceptions for unclear rights | OR-C10 / OR-M7-5 | blocked unless explicitly approved |
| DataForSEO funding/use and endpoint recipe | OR-C1 | blocked |
| Long-term raw payload retention posture | OR-C2 / OR-M7-5 | not admitted |
| Manual public observations as Observatory evidence | OR-C8 / OR-M7-7 | not admitted |
| Browser-extension capture instrument | OR-C6 | not admitted |
| Customer first-party overlay acceptance into read tools | OR-F1 | overlay only; not stored |
| Internal first-party telemetry admission | OR-F2 | not admitted |
| Manual screenshot retention and report redistribution | OR-M7-6 | not admitted |
| Public comments/UGC retention exclusion/default | OR-M7-8 | excluded or review-required by default |

A future accepted version of this contract may keep open rulings only if affected behavior fails closed until ruled.

---

## Deeper-research blockers

The following backlog items block later activation of parts of this contract:

- DR1 — DataForSEO endpoint-by-endpoint admission research.
- DR2 — Raw payload retention and allowed-use interpretation.
- DR6 — Marketplace platform evidence limits: Etsy.
- DR7 — Marketplace platform evidence limits: Fiverr.
- DR8 — Manual capture and browser-extension capture admissibility.
- DR10 — Customer first-party overlay contract.
- DR11 — Owned internal first-party telemetry.
- DR13 — Raw archive layout and provider drift fingerprints.
- DR17 — Provider credential and secret handling posture.

Targeted terms/pricing/source verification remains required before any load-bearing provider/capture admission decision.

---

## Hammer expectations

M8+ must prove this contract with hostile-path hammers including:

- H1 — scope isolation hammers.
- H2 — rights fail-closed hammers.
- H3 — retention enforcement hammers.
- H4 — customer-private data rejection hammers.
- H5 — no strategy / recommendation storage hammers.
- H6 — CapturePackage validation hammers.
- H7 — provider spend and duplicate task hammers.
- H11 — marketplace evidence hammers.
- H12 — raw archive integrity hammers.
- H16 — consumer request / overlay hammers.
- H17 — LLM / agent access hammers.
- H18 — hostile path / weird input hammers.
- H19 — append-only observation hammers.
- H20 — concurrency hammers.
- H21 — audit-first hammers.
- H22 — migration rollback / recovery hammers once schema/migration work is allowed.

Specific hostile paths:

- observation admitted without scope;
- unknown scope class accepted;
- customer email/name/order/report ID accepted as scope identity;
- unknown rights treated as permission;
- `not_expressly_granted` durable-stored;
- `no_storage_overlay_only` persisted;
- `capture_and_purge` accepted without purge deadline;
- source-specific restriction ignored;
- marketplace capture stored before admission;
- raw payload retained without rights;
- strategy/recommendation hidden in metadata;
- cross-scope aggregate read allowed without owner ruling;
- provider spend allowed without approval/ceiling.

---

## Feeds milestones

- M8 — Hammer Matrix and Acceptance Gates.
- M10 — Schema Planning Only.
- M13 — Provider Admission and Controlled Pull Plan.
- M14 — Typed Read API / MCP Contract and Prototype.
- M15 — SearchClarity Proof Workflow.
- M17 — Owned Telemetry Overlay Proof.
- M19 — Hardening, Backup, Recovery, and Operations.

---

## Change log

```text
0.1 — 2026-07-10 — initial draft from RG2, boundary law, and M7 parking-lot inputs
```
