# RG3 — Evidence ID / Citation Model

Status: research output
Authority: source-grounded research input; not doctrine by itself; not schema approval
Milestone: M6 — Research Gate Execution
Date: 2026-07-07

---

## Gate question

What ID and citation-handle model lets Observatory evidence be stable, human-citable, raw-payload-linked, and safe for LLM evidence packs?

---

## Sources checked

Local/current sources checked during RG3:

- `research/m5-research-gate-plan.md`
- `planning-inbox/repo-first-research-triage.md`
- `02-boundaries.md`
- `01-harvest-register.md`
- `research/rg2-scope-rights-retention-model.md`

No current external source was required for this gate because RG3 defines an internal evidence/citation model. External citation standards can be researched later if a consumer contract requires a specific report or compliance format.

---

## Current source-grounded findings

### F1 — Evidence IDs are already a planned day-one need

The harvest register names evidence citation IDs as a planned capability:

```text
Every read-tool response carries stable observation IDs so reports and Kaizen artifacts cite evidence durably.
```

Implication:

- Evidence IDs are not cosmetic.
- They are part of the core read-contract spine.
- M7 should treat ID/citation behavior as a contract, not as incidental schema naming.

---

### F2 — Local triage already distinguishes multiple ID concepts that must not collapse

The repo-first research triage says the open problem is the difference between:

- capture ID
- observation ID
- evidence ID
- provider job ID
- citation handle
- report-safe reference

Implication:

- A single `id` field will not be enough.
- Different lifecycle layers need different identifiers.
- Read tools must know which ID is stable for citation and which ID is only source/provider context.

---

### F3 — IDs must link evidence to raw payloads without exposing raw mystery blobs as the user-facing citation surface

RG2 proposed observation-level fields such as raw payload pointer, raw payload hash, freshness status, and evidence ID.

Implication:

- Evidence IDs should point through a controlled evidence model to raw payloads or raw pointers.
- Consumer-facing reports should not have to cite raw file paths, provider job IDs, or database row IDs directly.

---

### F4 — IDs must preserve Observatory's customer-data boundary

`02-boundaries.md` forbids customer records, customer identities, customer workflow state, and customer first-party analytics storage.

Implication:

- Evidence IDs must not encode customer names, emails, order IDs, report IDs, or private consumer database IDs.
- Customer-facing references should be stable and useful without becoming customer records.

---

### F5 — Evidence IDs must survive schema evolution

The triage note explicitly asks how evidence IDs survive schema family changes.

Implication:

- Evidence IDs should be treated as logical evidence handles, not direct table-row IDs.
- Physical storage can change while citation handles continue resolving through a registry or lookup contract.

---

## Proposed identifier layers

This section proposes the model M7 should turn into contracts. It is not schema approval.

### `capture_id`

Purpose:
Identifies a capture event or attempt.

Used for:

- provider pull attempts;
- manual/operator captures;
- batch/capture-package grouping;
- cost and duplicate-task controls;
- retry/stop-condition analysis.

Not used for:

- customer-facing citation;
- proof that a specific observation is valid;
- report-safe reference.

Recommended shape:

```text
cap_<date>_<shortid>
```

Example:

```text
cap_20260707_8f3a21
```

Notes:
A capture may produce zero, one, or many observations. A failed capture may still need an audit or cost record later, but not necessarily evidence.

---

### `provider_job_id`

Purpose:
Stores the provider's own task/job/request ID where available.

Used for:

- provider reconciliation;
- cost tracking;
- support/debugging;
- raw payload matching;
- provider-side export or audit.

Not used for:

- stable Observatory evidence identity;
- customer-facing report citation;
- cross-provider comparison identity.

Recommended shape:
Use the provider's original value as a provider-attributed field, not as the Observatory primary ID.

Example:

```text
provider: dataforseo
provider_job_id: 123456789
```

Notes:
Provider job IDs are provider testimony/context. They are not Observatory truth keys.

---

### `raw_payload_id`

Purpose:
Identifies a stored raw payload or immutable raw payload bundle, if raw retention is later admitted.

Used for:

- raw archive lookup;
- hash verification;
- provider drift analysis;
- re-parsing structured observations;
- audit evidence.

Not used for:

- public/customer-facing citation by default;
- strategy interpretation;
- proof without hash/manifest context.

Recommended shape:

```text
raw_<sourcefamily>_<date>_<shortid>
```

Example:

```text
raw_dataforseo_serp_20260707_4c91aa
```

Required companion fields:

```text
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_created_at
retention_class
rights_class
```

Notes:
RG1 did not approve long-term raw DataForSEO retention. This ID layer is a contract-planning placeholder.

---

### `observation_id`

Purpose:
Identifies one structured observation extracted from a raw payload, manual capture, page snapshot, or provider response.

Used for:

- internal traceability;
- structured observation retrieval;
- read-tool evidence assembly;
- joining observations to query panels/freshness/scope;
- hammer testing scope isolation and provenance.

Not used for:

- provider job identity;
- capture event identity;
- final customer-facing reference by default.

Recommended shape:

```text
obs_<family>_<date>_<shortid>
```

Examples:

```text
obs_serp_20260707_a13f22
obs_ai_mention_20260707_c8941e
obs_marketplace_listing_20260707_7bd912
```

Required companion fields:

```text
scope_id
scope_class
source_family
capture_id
provider_or_capture_instrument
captured_at
rights_class
retention_class
freshness_status
raw_payload_id or raw_payload_pointer when available
```

Notes:
An observation may be too granular for report citation. A report may need to cite an evidence bundle rather than one row.

---

### `evidence_id`

Purpose:
Provides the stable logical handle for evidence used by read tools, reports, audits, Kaizen artifacts, or downstream consumer claims.

Used for:

- LLM evidence packs;
- claim-to-evidence linking;
- customer-facing or internal report support;
- cross-observation evidence bundles;
- durable citations across schema changes.

Not used for:

- provider task identity;
- raw file identity;
- customer identity;
- strategy recommendation storage.

Recommended shape:

```text
ev_<scopeclass>_<family>_<date>_<shortid>
```

Examples:

```text
ev_market_serp_20260707_d83a10
ev_customer_public_listing_20260707_a92ff1
ev_internal_ai_surface_20260707_f22b8c
```

Rules:

- An evidence ID may point to one observation or an evidence bundle.
- Evidence IDs should resolve through a controlled evidence lookup contract.
- Evidence IDs must not encode customer identity.
- Evidence IDs must not encode conclusions.
- Evidence IDs must preserve provenance, rights, retention, freshness, and raw support.

---

### `citation_handle`

Purpose:
Provides a short, human-usable reference for reports, notes, and LLM responses.

Used for:

- readable report footnotes;
- LLM evidence-pack references;
- claim review;
- human QA.

Not used for:

- database primary keys;
- raw payload lookup without resolution;
- provider identity.

Recommended shape:

```text
E-YYYYMMDD-NNN
```

Example:

```text
E-20260707-004
```

Rules:

- Citation handles map to evidence IDs.
- They can be scoped to a report/evidence pack or globally unique, depending on M7/M15 contract choice.
- They should be stable within the artifact that cites them.

Open design choice:
Should `citation_handle` be globally stable, or artifact-local but backed by globally stable `evidence_id`?

Recommended posture:
Use globally stable `evidence_id`; allow artifact-local `citation_handle` for readability.

---

### `report_safe_reference`

Purpose:
Provides a customer-facing reference that supports claims without leaking internal IDs, provider job IDs, raw paths, or customer database references.

Used for:

- SearchClarity report evidence references;
- client-safe audit trails;
- report QA.

Not used for:

- raw archive lookup by customers;
- provider debugging;
- internal row identity.

Recommended posture:
M7/M15 should decide whether report-safe references are:

1. the same as artifact-local citation handles;
2. derived from evidence IDs through a report evidence map;
3. a separate public-facing reference class.

RG3 recommendation:
Keep `report_safe_reference` separate as a concept until SearchClarity consumer contract decides.

---

## Required evidence-resolution behavior

A future read API/MCP evidence lookup should resolve:

```text
evidence_id -> evidence record / evidence bundle
citation_handle -> evidence_id -> evidence record / evidence bundle
report_safe_reference -> report evidence map -> evidence_id
```

The returned evidence pack should include:

```text
evidence_id
citation_handle if applicable
scope_id
scope_class
source_family
provider_or_capture_instrument
captured_at
provider_reported_time if available
freshness_status
rights_class
retention_class
observation_ids
raw_payload_ids or raw_payload pointers if permitted
provenance summary
caveats
```

The returned evidence pack must not include:

```text
customer private identity
customer first-party analytics payloads
provider credentials
raw payloads when rights/retention do not allow exposure
strategy recommendations
accepted conclusions
```

---

## Stability rules

Evidence IDs should be stable even if:

- a raw payload is re-parsed;
- hot-path fields move between schema families;
- read-tool output shape evolves;
- provider-specific fields change;
- report wording changes;
- a consumer regenerates a report from the same evidence.

Evidence IDs may need to be deprecated, superseded, or withdrawn if:

- rights or retention later forbid use;
- source corruption is discovered;
- hash verification fails;
- the observation was created under an invalid capture method;
- the evidence was mistakenly tied to the wrong scope.

Future contract should define statuses such as:

```text
active
superseded
withdrawn
expired_by_retention
blocked_by_rights
invalidated
```

---

## Candidate evidence-status vocabulary

| status | Meaning |
|---|---|
| `active` | Evidence may be cited under current rights/retention/freshness constraints |
| `superseded` | Evidence remains historical but a newer evidence handle should be used for current claims |
| `withdrawn` | Evidence should not be used due to discovered problem |
| `expired_by_retention` | Evidence no longer usable/stored because retention window ended |
| `blocked_by_rights` | Rights no longer allow use or exposure |
| `invalidated` | Capture/provenance/hash/scope error invalidated the evidence |

---

## Claim-to-evidence relationship

Observatory should support downstream claim review by returning evidence handles and caveats.

Observatory should not store the downstream claim as an accepted conclusion.

Correct pattern:

```text
Consumer claim -> cites evidence_id / citation_handle -> Observatory returns evidence pack
```

Forbidden pattern:

```text
Observatory stores accepted report conclusion or recommendation as evidence
```

---

## Examples

### Example 1 — one SERP result observation cited in a report

```text
capture_id: cap_20260707_8f3a21
provider_job_id: dataforseo:123456789
raw_payload_id: raw_dataforseo_serp_20260707_4c91aa
observation_id: obs_serp_20260707_a13f22
evidence_id: ev_customer_public_serp_20260707_d83a10
citation_handle: E-20260707-004
report_safe_reference: SC-EVID-004
```

Meaning:
A report cites the evidence handle, not the provider job or raw file path.

---

### Example 2 — AI answer-surface mention bundle

```text
capture_id: cap_20260707_b31f90
raw_payload_id: raw_dataforseo_ai_20260707_2d0a7c
observation_ids:
  - obs_ai_mention_20260707_001a
  - obs_ai_citation_20260707_001b
evidence_id: ev_market_ai_surface_20260707_7db811
citation_handle: E-20260707-009
```

Meaning:
One evidence ID can cite a bundle of related observations.

---

### Example 3 — customer first-party overlay

```text
external_overlay_reference: supplied at read time
observation_id: none in Observatory for overlay payload
evidence_id: only for Observatory external observations, not the overlay itself
```

Meaning:
Customer first-party overlay data is not stored or assigned Observatory evidence IDs under current law.

---

## Non-goals

RG3 does not authorize:

- schema design;
- migrations;
- raw payload retention;
- provider admission;
- report automation;
- customer record storage;
- customer first-party storage;
- strategy/recommendation storage;
- API/MCP implementation.

---

## Owner-ruling candidates

Owner ruling or later contract decision is required before:

- choosing final ID formats;
- deciding whether citation handles are global or artifact-local;
- deciding whether report-safe references are separate from citation handles;
- defining evidence withdrawal/deprecation behavior;
- exposing any raw payload pointers outside internal tools;
- using evidence IDs in customer-facing reports.

---

## Blockers carried forward

- M7 must turn this into an evidence ID / citation contract.
- M8 must hammer citation resolution, scope isolation, rights blocking, retention expiration, and no customer-identity leakage.
- M14 must expose evidence through typed read tools only.
- M15 must decide SearchClarity report-safe reference behavior.

---

## Feeds later milestones

- M7 evidence ID and citation contract
- M8 citation / rights / retention / scope hammers
- M10 schema planning
- M14 typed read API / MCP contract
- M15 SearchClarity proof workflow

---

## Final RG3 rule

```text
Provider IDs explain where evidence came from.
Observation IDs identify what was observed.
Evidence IDs are what downstream claims cite.
Citation handles make evidence human-readable.
None of them may smuggle customer identity or conclusions into Observatory.
```
