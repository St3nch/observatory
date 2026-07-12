# M13 DataForSEO Admission and Probe Plan

Status: planning draft
Authority: none — advisory M13 planning only; decision record required before spend, provider use, or pull execution
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-10
Owner approval required before credits: yes
Owner approval required before any provider call: yes

---

## Purpose

This document activates the parked D11 concept from `planning-inbox/m7-owner-rulings-and-dependency-parking-lot.md` as an M13 planning draft.

The goal is to plan a tiny DataForSEO evidence probe so The Observatory can inspect real provider JSON before designing persistent storage or broader provider workflows.

This plan exists to answer:

```text
What does DataForSEO actually return for a tiny controlled pull, and what does Observatory need to preserve before database design or provider admission expands?
```

---

## Current Status

```text
DataForSEO remains a candidate provider.
DataForSEO is not admitted yet.
Credits must not be added yet.
No provider call is authorized yet.
No paid pull is authorized yet.
No CLI implementation is authorized yet.
```

M13 may plan the probe. A later owner decision must approve funding/use before credits are added or any request is sent.

---

## Source Inputs

This plan is based on:

- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `contracts/provider-testimony.md`
- `contracts/scope-rights-retention.md`
- `contracts/capturepackage-v0-1.md`
- `contracts/raw-archive-provider-drift.md`
- `planning-inbox/m7-owner-rulings-and-dependency-parking-lot.md`
- `decisions/2026-07-10-m12-first-slice-closure.md`
- `ACTIVE_CONTEXT.md`

---

## Why a Probe Is Needed

Documentation alone is not enough.

The Observatory needs controlled real payload evidence to understand:

- actual JSON shape;
- status/error fields;
- task IDs and cost metadata;
- timing fields;
- provider-reported timestamps;
- request/response envelope structure;
- nested result structure;
- field volatility;
- what raw payload metadata must be promoted into structured storage later;
- what can stay raw-support-only;
- what must never become strategy/recommendation data.

This probe is not designed to collect useful SEO data yet.

It is designed to inspect provider response shape safely.

---

## Provider Candidate

```text
Provider candidate: DataForSEO
Admission status: candidate only
Likely first endpoint family: SERP API
Secondary endpoint family: AI Optimization API, only if separately approved
```

The first probe should stay smaller than a useful business workflow.

Recommended initial scope:

```text
one tiny SERP API validation sample only
```

Optional later M13 add-on, only after review:

```text
one tiny AI Optimization validation sample
```

Do not include marketplace, backlink, Labs, Merchant, Reviews, Business Data, Domain Analytics, Content Analysis, or broad multi-family pulls in the first probe.

---

## Credit and Spend Gate

RG1 records DataForSEO's public minimum payment posture as `$50`, but this plan does not authorize funding or use.

Credit rule:

```text
Do not add DataForSEO credits until a decision record explicitly approves:
- funding/use of DataForSEO account;
- maximum validation budget;
- endpoint list;
- task count ceiling;
- stop conditions;
- raw payload handling posture;
- owner approval before the CLI sends any request.
```

Recommended first funding posture, if later approved:

```text
Funding amount: minimum required account credit only, expected to be $50 if still current at purchase time
Spend ceiling for first probe: materially lower than funded balance
Task ceiling: 1 task unless explicit owner decision allows a second task
```

Fresh price check required:

```text
Before adding credits, re-check current DataForSEO pricing and minimum payment from official DataForSEO pages.
```

---

## Controlled Pull Recipe Draft

### Recipe ID

```text
m13-dataforseo-serp-probe-v0-1
```

### Goal

```text
Inspect one real DataForSEO SERP API response envelope and payload shape.
```

### Proposed task ceiling

```text
1 paid task
```

### Proposed dollar ceiling

```text
First probe spend ceiling to be set by owner decision before funding/use.
Default planning placeholder: no spend authorized.
```

### Proposed endpoint family

```text
SERP API only, exact endpoint to be selected before implementation.
```

### Proposed query shape

Use one deliberately boring, non-customer, non-sensitive, non-business-critical query.

Candidate query options for owner review:

```text
observatory test page
weather today
example domain search
```

Do not use:

- a real SearchClarity customer;
- a private business target;
- a client domain;
- a marketplace seller/listing;
- a sensitive local query;
- a query intended to make a recommendation.

### Proposed location/device/language

To be selected before implementation, but must be fixed and recorded.

Planning placeholder:

```text
language: English
location: United States or a clearly recorded DataForSEO location code
device: desktop if endpoint requires a device choice
```

### Duplicate prevention

The CLI must refuse to submit the same request twice unless an explicit `--allow-repeat` or equivalent operator override exists and the operator records a reason.

For the first probe:

```text
No repeat submission allowed.
```

---

## CLI Probe Requirements Before Implementation

A tiny CLI probe may be implemented only after this plan is accepted or converted into an explicit decision/task.

Required behavior:

- reads credentials only from local environment variables or local ignored config;
- never commits credentials;
- prints estimated/declared task count before submit;
- requires an explicit confirmation flag for paid call execution;
- enforces task ceiling;
- enforces endpoint allowlist;
- writes raw JSON to a local probe evidence path only if retention posture permits;
- writes a manifest next to raw JSON;
- computes SHA-256 hash of raw JSON;
- writes field-path summary after pull;
- writes top-level status/cost/task fields summary;
- refuses recurring mode;
- refuses customer/private input markers;
- refuses broad endpoint families not in allowlist;
- exits after one probe;
- does not parse into observations automatically;
- does not write to Postgres;
- does not create migrations;
- does not expose API/MCP.

---

## Proposed Probe Output Files

If later authorized, probe output should be local evidence only.

Candidate path pattern:

```text
probe-evidence/dataforseo/YYYY-MM-DD/<probe-id>/raw-response.json
probe-evidence/dataforseo/YYYY-MM-DD/<probe-id>/manifest.json
probe-evidence/dataforseo/YYYY-MM-DD/<probe-id>/field-summary.md
```

Important:

```text
probe-evidence/ is not yet created.
This plan does not authorize creating or committing raw provider payloads.
```

Before any raw payload is committed or archived, retention posture must be explicit.

Safer default:

```text
Raw JSON stays local and ignored until provider/raw-retention decision is explicit.
A sanitized field summary may be committed if it contains no raw provider payload and no customer data.
```

---

## CapturePackage Metadata Required for Probe

The probe manifest should preserve enough context to feed later CapturePackage design.

Minimum candidate manifest fields:

```text
probe_id
recipe_id
provider_name
provider_family
endpoint_or_surface
request_payload_sha256
request_context_pointer
submitted_at
completed_at
operator
approval_reference
credits_authorized
spend_ceiling
actual_cost_reported
call_or_task_ceiling
calls_or_tasks_used
duplicate_prevention_key
rights_class
rights_basis
retention_class
retention_basis
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_media_type
shape_fingerprint
field_path_count
top_level_keys
provider_status_fields
provider_error_fields
stop_condition_triggered
claim_use_warning
```

Fields may be marked `not_applicable` only when genuinely not applicable.

They must not be silently missing.

---

## Raw Payload / Shape Summary Requirements

After the probe, produce a field summary that answers:

- What are the top-level response keys?
- What are the task/status/error/cost keys?
- What nested result paths exist?
- Which fields look stable identity/provenance fields?
- Which fields look volatile or result-specific?
- Which fields look like provider scores or provider model output?
- Which fields contain timestamps?
- Which fields contain search/result URLs?
- Which fields could become structured observation fields later?
- Which fields should remain raw-support-only?
- Did the provider return unexpected or undocumented fields?

The field summary is evidence about payload shape, not a schema decision.

---

## Stop Conditions

The probe must stop immediately if:

- estimated task count exceeds approved ceiling;
- estimated spend exceeds approved ceiling;
- endpoint is outside allowlist;
- credentials are missing or malformed;
- request contains customer/private markers;
- request uses marketplace/customer/search-report terms not approved for probe;
- duplicate request key already exists;
- provider returns authentication error;
- provider returns unexpected charge/cost metadata;
- provider response shape cannot be summarized safely;
- raw payload retention posture is unclear;
- any result appears to contain customer/private data.

No retry loop is allowed in the first probe.

---

## Explicit Non-Authorizations

This plan does not authorize:

```text
adding credits
using existing credits
provider calls
paid pulls
DataForSEO task execution
provider admission execution
Postgres creation
schema migrations
raw payload long-term retention
committing raw JSON
API/MCP exposure
dashboard work
customer data handling
customer-facing reports
marketplace scraping
browser-extension capture
recurring capture
strategy/recommendation storage
```

---

## Owner Approval Gate

The owner should add credits only after a later decision says something like:

```text
Approve DataForSEO minimum account funding for the M13 probe.
Approve max spend: <amount>.
Approve exact endpoint: <endpoint>.
Approve max tasks: <count>.
Approve raw payload handling: <retain local only / manifest only / commit sanitized summary only / other>.
```

Until that exists:

```text
Do not add credits yet.
```

---

## Recommended Next Step

Create an M13 review of this plan.

That review should decide whether this plan is ready to become an owner approval decision or whether the exact endpoint/cost/retention details need another pass first.

---

## Final Rule

```text
We are planning the first provider microscope slide.
We are not turning on the provider machine yet.
```
