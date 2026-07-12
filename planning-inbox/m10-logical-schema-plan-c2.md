# M10 Logical Schema Plan — C2 Controlled Public Manual Observation Package

Status: planning / logical schema plan
Authority: none — planning draft only; roadmap and decisions remain authority
Milestone: M10 — Schema Planning Only
Date: 2026-07-10
Source decision: `decisions/2026-07-10-m9-first-slice-closure.md`
Accepted first slice: C2 — Controlled Public Manual Observation Package

---

## Purpose

This document defines the first M10 logical schema plan for the accepted C2 first evidence slice.

It translates the M9 accepted slice and M8 hammer gates into logical responsibilities that a later implementation can plan against.

This is schema planning only.

---

## Non-Authorization Boundary

This document does not authorize:

```text
physical DDL
migrations
implementation
Postgres changes
provider purchases
paid provider pulls
provider admission
API/MCP implementation
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
accepting any hammer as passed
manual capture as a production capture method
scraping
crawling
browser-extension capture
customer-facing reports
```

M10 may plan logical schema.

M10 may not run migrations.

---

## Accepted Slice Boundary

The only selected first slice is:

```text
Controlled Public Manual Observation Package
```

The slice represents one controlled public/manual observation package moving through the Observatory evidence spine:

```text
observed public artifact
  -> provenance
  -> scope
  -> rights
  -> retention
  -> raw support where allowed
  -> candidate observation
  -> admitted observation
  -> evidence identity
  -> read-time interpretation boundary
```

The slice may use controlled fixture/manual-public observation inputs only.

It is not production capture approval.

---

## Logical Model Overview

M10 should plan a minimal logical model with these responsibility groups:

| Logical responsibility | Purpose | Notes |
|---|---|---|
| Scope registry | Defines the safe scope context for a package | Must not store customer identity |
| Observation package | Admission envelope around the controlled manual observation | CapturePackage-style concept, not provider task execution |
| Observed artifact reference | Identifies the public artifact observed | Generic public/owner-controlled fixture only |
| Raw support manifest | Tracks raw support pointer/hash if raw support is included | Optional, rights/retention-gated |
| Candidate observation | Represents parsed/derived candidate observation before admission | Candidate is not evidence |
| Admitted observation | Represents validated observation as historical fact of observation | Append-only |
| Evidence identity | Stable evidence ID for admitted observation | Not a report-safe customer citation |
| Freshness / claim-use status | Captures point-in-time warning posture | No current truth overclaim |
| Audit event | Records consequential state transitions | Planning expectation only |
| Rejection reason | Captures why a package/input cannot be admitted | Useful for hammers and operator review |

These are logical responsibilities, not tables.

---

## Logical Entities

### 1. Scope Context

Purpose:

```text
Prove every observation package belongs to an explicit allowed scope without storing customer records or customer identity.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `scope_id` | Required; internal identifier only |
| `scope_class` | Required; allowed class only |
| `scope_label` | Optional human label; must not contain customer/private identity for first slice |
| `scope_status` | Active / inactive / blocked concept |
| `created_at` | Planning timestamp concept |

Allowed first-slice scope posture:

```text
internal fixture / owner-controlled planning scope
```

Blocked:

```text
customer email
customer order ID
SearchClarity engagement ID
private analytics account ID
marketplace seller account identity
```

Hammers:

```text
H1 Scope isolation
H4 Customer-private rejection as rejection fixture only
H5 No strategy/recommendation storage
```

---

### 2. Observation Package

Purpose:

```text
Hold the admission envelope for one controlled public/manual observation package.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `observation_package_id` | Required logical package identity |
| `scope_id` | Required |
| `source_family` | Required; first slice constrained to controlled public/manual fixture |
| `capture_method` | Required; manual controlled fixture label |
| `operator_intent` | Required; observation-purpose only |
| `captured_at` | Required for point-in-time evidence |
| `rights_class` | Required; fail closed if missing/unclear |
| `rights_basis` | Required enough to explain posture |
| `retention_class` | Required; fail closed if missing/unclear |
| `retention_basis` | Required enough to explain posture |
| `package_status` | Draft / blocked / candidate / admitted / rejected / purged planning states |
| `validation_status` | Pending / valid / invalid concept |
| `claim_use_warning` | Required for point-in-time evidence |

Package status vocabulary should remain conservative:

```text
draft
blocked
candidate_created
validated
admitted
rejected
purged
superseded
```

Blocked package states must not mint evidence IDs.

Hammers:

```text
H1 Scope isolation
H2 Rights fail-closed
H3 Retention enforcement
H5 No strategy/recommendation storage
H6 Observation envelope validation
H9 Freshness / point-in-time claim-use warning
H18 Hostile weird input
H21 Audit-first enforcement
```

---

### 3. Observed Artifact Reference

Purpose:

```text
Identify the public artifact observed without storing private customer data or treating the artifact as a recommendation target.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `artifact_reference_id` | Required logical identity |
| `observation_package_id` | Required |
| `artifact_uri_or_label` | Public/controlled fixture reference only |
| `artifact_type` | Public page / static fixture / controlled artifact |
| `artifact_access_posture` | Public / owner-controlled fixture / blocked |
| `artifact_redaction_status` | Required if raw support could contain risky content |
| `observed_at` | Same as or linked to `captured_at` |

Do not store:

```text
customer account URL behind login
private dashboard URL
GSC/GA4/export path
seller dashboard screenshot path
marketplace seller private data
report recommendation target
```

Hammers:

```text
H1 Scope isolation
H2 Rights fail-closed
H4 Customer-private rejection
H5 No strategy/recommendation storage
H18 Hostile weird input
```

---

### 4. Raw Support Manifest

Purpose:

```text
Represent raw support safely when rights and retention allow raw support.
```

Raw support is optional. If included, it must be manifest/hash based and retention-gated.

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `raw_support_id` | Required if raw support exists |
| `observation_package_id` | Required |
| `raw_pointer` | Required if raw support is retained |
| `raw_sha256` | Required if raw support is retained |
| `raw_bytes` | Optional / bounded planning field |
| `raw_media_type` | Required if raw support is retained |
| `retention_class` | Required; inherited or explicit |
| `purge_status` | Required if raw support can be purged |
| `redaction_status` | Required if raw may include risky content |
| `hash_verification_status` | Required before raw-supported admission |

Rules:

- raw support cannot exist without rights and retention posture;
- hash mismatch blocks admission;
- missing pointer blocks raw-supported evidence;
- `no_storage_overlay_only` and forbidden retention classes block raw persistence;
- manifest-only posture must not retain forbidden payload.

Hammers:

```text
H2 Rights fail-closed
H3 Retention enforcement
H12 Raw archive integrity
H18 Hostile weird input
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

---

### 5. Candidate Observation

Purpose:

```text
Represent a possible observation extracted from the package before it becomes admitted evidence.
```

Candidate observations are not evidence.

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `candidate_observation_id` | Required candidate identity |
| `observation_package_id` | Required |
| `candidate_type` | Required |
| `candidate_payload_pointer_or_summary` | Bounded; must not store recommendation/strategy |
| `candidate_status` | Pending / valid / invalid / rejected |
| `validation_errors` | Required if rejected |
| `raw_support_id` | Optional if candidate is raw-supported |
| `created_at` | Required planning timestamp concept |

Rules:

- candidate observation cannot be cited as evidence;
- candidate observation cannot become evidence without validation;
- candidate payload cannot preserve strategy, recommendation, report conclusion, or customer private data;
- rejected candidates should carry rejection reason, not become hidden evidence.

Hammers:

```text
H5 No strategy/recommendation storage
H6 Observation envelope validation
H15 Evidence ID / citation integrity
H18 Hostile weird input
```

---

### 6. Admitted Observation

Purpose:

```text
Represent the validated historical fact that an artifact was observed under a specific scope/context/time/rights/retention posture.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `observation_id` | Required stable observation identity |
| `observation_package_id` | Required |
| `candidate_observation_id` | Required source candidate link |
| `scope_id` | Required |
| `captured_at` | Required and immutable after admission |
| `source_family` | Required |
| `capture_method` | Required |
| `rights_class` | Required |
| `retention_class` | Required |
| `freshness_status` | Required or derivable |
| `observation_status` | Active / superseded / withdrawn / purged-status concept |
| `admitted_at` | Required planning timestamp concept |

Rules:

- admitted observations are append-only;
- corrections create superseding observations or status transitions, not in-place mutation;
- observations store what was observed, not what it means;
- observations do not store recommendations, strategies, or accepted conclusions.

Hammers:

```text
H1 Scope isolation
H2 Rights fail-closed
H3 Retention enforcement
H5 No strategy/recommendation storage
H9 Freshness / claim-use warning
H15 Evidence ID / citation integrity
H19 Append-only observations
H21 Audit-first enforcement
```

---

### 7. Evidence Identity

Purpose:

```text
Provide a stable evidence identifier for an admitted observation without confusing provider IDs, raw IDs, report-safe handles, or customer identities.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `evidence_id` | Required for admitted evidence |
| `observation_id` | Required |
| `evidence_status` | Active / superseded / withdrawn / purged |
| `citation_handle` | Internal/non-report-safe handle only unless later allowed |
| `created_at` | Required planning timestamp concept |

Rules:

- evidence ID is not a raw support ID;
- evidence ID is not a provider job ID;
- evidence ID is not a report-safe customer citation;
- evidence ID must not encode customer identity;
- evidence ID is created only after admission.

Hammers:

```text
H15 Evidence ID / citation integrity
H19 Append-only observations
H21 Audit-first enforcement
```

---

### 8. Freshness / Claim-Use Warning

Purpose:

```text
Prevent point-in-time observations from becoming overstrong current claims.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `freshness_status` | Required or derived from `captured_at` |
| `age_band` | Optional / derived |
| `claim_use_warning` | Required for point-in-time evidence |
| `current_claim_allowed` | Planning concept; default false unless freshness supports it later |
| `recapture_recommended` | Planning concept only; does not authorize capture |

Rules:

- stale evidence remains historical evidence;
- unknown captured_at blocks current-state claims;
- recapture warning does not authorize capture runner or provider pull;
- claim-use status does not store strategy or recommendation.

Hammers:

```text
H9 Freshness / point-in-time claim-use warning
H10 AI/GEO overclaim deferred unless surface is AI answer evidence
H15 Evidence ID / citation integrity
```

---

### 9. Audit Event

Purpose:

```text
Plan an audit-first expectation for consequential transitions without implementing audit tables in M10.
```

Candidate logical fields:

| Field concept | Requirement |
|---|---|
| `audit_event_id` | Required later for consequential changes |
| `event_type` | Admission / rejection / purge / supersession / withdrawal |
| `entity_type` | Package / candidate / observation / evidence / raw support |
| `entity_id` | Required |
| `event_time` | Required |
| `event_reason` | Required for rejection/purge/supersession |

Rules:

- later admission/purge/supersession should require audit evidence;
- read paths should not create audit events;
- audit events must not store strategy/recommendation output.

Hammers:

```text
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

---

## Rejection Paths M10 Must Preserve

M10 schema planning must support these rejection concepts without treating rejected material as evidence:

| Rejection | Required behavior |
|---|---|
| Missing scope | package rejected / blocked |
| Unknown scope class | package rejected / blocked |
| Customer/private identity present | package rejected / blocked |
| Missing rights class | package rejected / blocked |
| Unclear/restricted rights | package rejected / blocked |
| Missing retention class | package rejected / blocked |
| No-storage retention with raw payload | raw persistence blocked |
| Strategy/recommendation text | rejected, not stored as observation |
| Missing captured_at | current-claim use blocked; admission likely blocked depending path |
| Raw hash missing/mismatch | raw-supported admission blocked |
| Evidence ID requested before admission | rejected |
| Mutation of admitted observation | rejected; supersession path required |

---

## Deferred Schema Families

M10 must not plan schema for these families now:

| Family | Deferred to | Reason |
|---|---|---|
| Real provider tasks / DataForSEO pulls | M13 | Requires provider admission and spend controls |
| Provider disagreement ledger | M16 / owner ruling OR-A1 | Base observation path must exist first |
| Marketplace capture | M13/M15+ | Marketplace posture unresolved |
| Customer first-party overlays | M17 | Customer/private data is overlay-only |
| SearchClarity reports | M15 | Reports live in consumer layer |
| Typed read API/MCP tables/tools | M14 | Read tools not active in M10 |
| Recurring watch panels/scheduler | M18 | Recurring capture not approved |
| Dashboard/operator console state | deferred | Not needed for first slice |
| Strategy/recommendation store | forbidden | Violates core boundary |
| Cross-scope aggregate analysis | forbidden unless owner ruling | Leakage risk |

---

## Anti-Pattern Checks

Reject any M10 schema idea that stores:

```text
keyword recommendation
SEO strategy
GEO strategy
content rewrite suggestion
opportunity score as truth
provider winner
provider average truth score
customer order
customer identity
customer report state
private analytics series
LLM reasoning transcript as Observatory data
accepted business conclusion
agent task decision
```

If a schema concept stores what the observation means, it belongs outside Observatory.

---

## M10 Output Expectations

M10 should produce, before closure:

- a logical schema plan for C2 only;
- responsibility mapping from logical entities to contracts and hammers;
- explicit forbidden-family list;
- migration expectations without running migrations;
- M11/M12 handoff expectations;
- unresolved owner-ruling notes if needed.

This document is a first M10 schema planning draft, not M10 closure.

---

## Open Questions / Carry-Forward

- Should minimal query/panel context be included in the first schema plan, or deferred until after the base observation package is planned?
- Should raw support be mandatory in the first slice, or optional with manifest-only posture allowed?
- Which evidence ID shape should M10 plan around while OR-A4 remains open for report-safe citation behavior?
- What is the minimum audit event set needed for M11/M12 without overbuilding operations early?

---

## Recommended Next M10 Batch

Create a focused M10 review/checklist that answers:

```text
Does this logical schema plan satisfy M9 closure inputs?
Does it stay inside C2?
Does it avoid forbidden storage?
Does it give M11/M12 enough handoff shape?
Which details still need owner or steward review before M10 closure?
```

---

## Final Rule

```text
Plan the telescope frame.
Do not build it yet.
Do not let it become the astronomer.
```
