# M13 DataForSEO Probe Plan Review

Status: planning review
Authority: none — advisory M13 review only; not provider admission, funding approval, pull authorization, implementation approval, or schema approval
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-11
Reviewed artifact: `planning-inbox/m13-dataforseo-admission-and-probe-plan.md`

---

## Review Purpose

This review tests the current DataForSEO admission and probe plan against the governing M13 roadmap boundary, the parked D11 probe concept, existing research, contracts, and hammer expectations.

It answers three questions:

```text
1. What is ready?
2. What remains unresolved?
3. What must a later owner approval decision name before funding or any request is allowed?
```

This review does not authorize:

```text
DataForSEO credits
use of existing credits
provider calls
paid pulls
DataForSEO task execution
CLI implementation
Postgres creation
schema design
schema changes
migrations
provider clients
capture runners
raw payload retention
committing raw JSON
API/MCP exposure
dashboard work
customer data handling
customer-facing reports
marketplace scraping
browser-extension capture
recurring capture
strategy or recommendation storage
```

Endpoint, query, location, language, and device details discussed below are proposal fields only. They are not execution approval.

---

## Sources Reviewed

Primary review inputs:

- `ACTIVE_CONTEXT.md`
- `ROADMAP.md`
- `NEXT_SESSION_HANDOFF.md`
- `planning-inbox/m13-dataforseo-admission-and-probe-plan.md`
- `planning-inbox/m7-owner-rulings-and-dependency-parking-lot.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `contracts/provider-testimony.md`
- `contracts/scope-rights-retention.md`
- `contracts/capturepackage-v0-1.md`
- `contracts/raw-archive-provider-drift.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- `decisions/2026-07-10-m12-first-slice-closure.md`

---

## Review Disposition

```text
The M13 plan is coherent enough to proceed to owner-approval decision drafting.
It is not concrete enough to approve funding or send a request yet.
```

The plan correctly establishes a tiny, non-customer, non-recurring DataForSEO payload-inspection probe with a one-task default ceiling, duplicate prevention, raw-support controls, field-summary requirements, and a mandatory owner gate before any spend or call.

The plan also correctly keeps the probe separate from provider admission expansion, useful SEO collection, Postgres, schema, migrations, recurring capture, API/MCP, dashboards, customer workflows, and strategy/recommendation storage.

However, several execution-binding values remain placeholders. Those values must be named in a later owner approval decision before credits are added, existing credits are used, CLI implementation begins, or any request is sent.

---

## What Is Ready

### 1. Purpose and scope are ready

The probe purpose is narrow and legitimate:

```text
inspect one real provider response envelope and payload shape
```

The plan does not pretend the first pull will prove business value, market truth, provider reliability, schema completeness, or broad provider admission.

This aligns with Observatory doctrine:

```text
Provider output is testimony, not truth.
Raw JSON is probe evidence, not schema approval.
```

### 2. Provider status is correctly fail-closed

The plan clearly states:

```text
DataForSEO is a candidate only.
DataForSEO is not admitted.
No credits, provider call, paid pull, or CLI implementation are authorized.
```

This satisfies the provider-testimony contract rule that naming or researching a provider does not admit it.

### 3. First-probe size is appropriately bounded

The default proposal is:

```text
one SERP API task
no retry loop
no repeat submission
no broad endpoint-family sampling
```

This is consistent with RG1's tiny-validation posture and its warning that repeated identical tasks are chargeable user-side errors.

### 4. Cost and duplicate-control concepts are ready

The plan already requires:

- owner approval before funding or use;
- an explicit task ceiling;
- an explicit spend ceiling;
- duplicate-request prevention;
- endpoint allowlisting;
- stop conditions;
- actual provider-reported cost capture;
- review before any second pull.

These are the correct M13 control categories.

### 5. Non-customer input posture is ready

The plan excludes:

- SearchClarity customers;
- client domains;
- private business targets;
- marketplace sellers/listings;
- sensitive local queries;
- customer/private markers;
- recommendation-oriented capture intent.

This is consistent with the no-customer-data boundary and CapturePackage validation expectations.

### 6. Raw-support posture is directionally ready

The plan correctly distinguishes:

```text
raw provider payload
manifest
field-path summary
shape fingerprint
structured observations
schema decisions
```

It also correctly defaults to keeping raw JSON local and ignored until rights and retention are explicitly decided.

The proposed SHA-256, byte count, media type, pointer, manifest, and shape-summary requirements align with RG10 and RG11.

### 7. Payload inspection outputs are ready

The required post-pull analysis is appropriately bounded to evidence about provider shape:

- top-level keys;
- task/status/error/cost fields;
- nested field paths;
- timestamps;
- URLs;
- provider scores/model outputs;
- stable-looking versus volatile fields;
- unexpected or undocumented fields;
- shape fingerprint;
- candidate structured fields versus raw-support-only fields.

The plan correctly states that this output is not schema approval.

### 8. Stop-condition categories are ready

The current stop conditions cover the important hostile paths:

- ceiling exceeded;
- endpoint outside allowlist;
- missing/malformed credentials;
- customer/private input detected;
- duplicate request detected;
- authentication failure;
- unexpected cost metadata;
- unclear raw-retention posture;
- unsafe or unclassifiable response shape;
- customer/private data appearing in results.

No retry loop for the first probe is the correct default.

### 9. CLI boundary requirements are ready as planning inputs

The plan has enough requirements to support a later CLI requirements document or implementation decision:

- local environment/ignored credential source;
- explicit paid-call confirmation;
- endpoint and task allowlists;
- ceiling enforcement;
- duplicate prevention;
- one-shot exit;
- no recurring mode;
- no Postgres;
- no parsing directly into observations;
- no API/MCP exposure.

These are ready as requirements only. They are not permission to build.

---

## What Remains Unresolved

### 1. Exact endpoint remains unresolved

Current proposal:

```text
SERP API only
```

That is an endpoint family, not an executable endpoint binding.

A later owner decision must name the exact DataForSEO endpoint and request mode. The decision must not rely on phrases such as:

```text
some SERP endpoint
standard SERP task
whatever is cheapest
```

The exact endpoint must be checked against current official documentation and pricing immediately before approval/funding because endpoint names, request modes, prices, and required fields can change.

### 2. Query remains unresolved

Current candidates:

```text
observatory test page
weather today
example domain search
```

These are proposals only.

The later decision must choose one exact query string and explain why it is:

- non-customer;
- non-sensitive;
- non-business-critical;
- not a marketplace target;
- not intended to generate recommendations;
- suitable only for payload-shape inspection.

A volatile query such as `weather today` may create avoidable freshness/location variability. A boring, stable, clearly artificial query is preferable unless endpoint requirements make that unsuitable.

### 3. Location remains unresolved

Current placeholder:

```text
United States or a clearly recorded DataForSEO location code
```

The later decision must name the exact location value or location code accepted by the chosen endpoint.

The decision must also state whether the location is:

- country-level;
- state/region-level;
- city-level;
- coordinate-based;
- endpoint default.

No implicit provider default should be used when the endpoint supports explicit location context.

### 4. Language remains unresolved

Current placeholder:

```text
English
```

The later decision must name the exact language value or code accepted by the chosen endpoint and preserve it in the request context and probe manifest.

### 5. Device remains unresolved

Current placeholder:

```text
desktop if endpoint requires a device choice
```

The later decision must name the exact device value or explicitly state `not_applicable` when the chosen endpoint does not accept a device parameter.

No implementation should silently rely on a provider default.

### 6. Search engine / result type remains unresolved

A SERP endpoint may require or imply additional request context beyond query/location/language/device, such as:

- search engine;
- result type;
- operating system;
- depth;
- priority/mode;
- live versus task-based flow;
- domain or URL fields;
- optional filters.

The later approval decision must name every request field that materially affects cost, scope, response shape, or repeatability. Unused optional fields should be explicitly omitted rather than populated from vibes.

### 7. Funding amount remains unresolved

RG1 recorded a public `$50` minimum payment during research. That is stale-able planning evidence, not current authorization.

Before funding, the later decision must record:

- current official minimum payment;
- approved funding amount;
- whether existing account balance may be used;
- account-level budget/limit control to be enabled if available;
- who performs the funding action.

No credits are needed during this review or approval-draft stage.

### 8. Probe spend ceiling remains unresolved

The plan correctly says the first probe spend ceiling must be materially lower than the funded balance, but it does not name a dollar amount.

The later decision must name:

```text
maximum authorized cost for the single request
```

It should also state how the ceiling is checked before submission and what happens if current pricing cannot be verified.

Default fail-closed behavior:

```text
If price cannot be verified, do not submit.
```

### 9. Exact task/call accounting remains unresolved

The plan proposes one task, but the chosen endpoint may distinguish between:

- task creation call;
- task retrieval call;
- live call;
- polling/status calls;
- result-download call;
- provider-internal task count;
- billable versus non-billable requests.

The later decision must define both:

```text
billable task ceiling
HTTP/API request ceiling
```

This avoids accidentally authorizing one paid task plus an unlimited polling carnival.

### 10. Raw payload retention posture remains unresolved

The current safer default is:

```text
raw JSON local and ignored
sanitized field summary potentially committable
```

That is directionally safe but incomplete.

The later decision must choose one exact posture:

```text
retain_raw_payload_local_only
capture_and_purge_raw
retain_manifest_only
no_raw_storage
other explicitly named posture
```

It must also name:

- local destination;
- whether the path is Git-ignored;
- retention duration or review deadline;
- purge trigger;
- whether the manifest survives purge;
- whether raw JSON may ever be committed;
- whether sanitized summaries may be committed;
- redaction expectations;
- hash/pointer requirements;
- backup posture, if any.

Unknown raw retention must block capture.

### 11. Rights basis remains unresolved at provider-specific binding level

RG1 partially cleared continued planning but did not grant broad long-term raw retention or provider admission.

The later decision must state the specific rights basis and allowed-use posture for:

- making the selected request;
- inspecting the returned payload internally;
- temporarily or durably retaining raw JSON;
- retaining a manifest;
- committing a sanitized field summary;
- using the sample to inform later schema planning.

If the rights basis remains ambiguous, the approved posture must be stricter, not optimistic.

### 12. Approval-reference mechanics remain unresolved

The later decision must become the exact approval reference carried into any probe manifest or CLI invocation.

A vague conversational approval is not enough. The executable gate must point to a committed decision file and accepted owner ruling.

### 13. Credential-handling binding remains unresolved

The plan correctly requires environment variables or local ignored configuration, but the later decision or CLI requirements must name:

- expected environment variable names or credential source;
- forbidden logging/output behavior;
- redaction expectations;
- no credential persistence in probe evidence;
- no credentials in command history when avoidable;
- failure behavior when credentials are missing.

This is not a request to create credentials or implement the CLI now.

### 14. Duplicate-prevention key remains unresolved

The later decision or CLI requirements must define the duplicate key inputs, likely including:

- provider;
- exact endpoint;
- normalized request payload hash;
- query;
- location;
- language;
- device;
- search engine/result type;
- approval reference.

For the first probe, any previously recorded matching key must block submission. No repeat override should be authorized in the first approval decision.

### 15. Success and failure evidence remains unresolved

The later decision must define what files or facts prove:

- request was approved;
- request matched the approved payload;
- ceiling checks passed;
- only the allowed number of calls/tasks occurred;
- provider-reported cost was recorded;
- raw handling followed the approved posture;
- SHA-256 and byte count were recorded when raw was retained;
- field summary was produced;
- no observation ingestion occurred;
- no second pull occurred.

### 16. Post-pull review gate remains unresolved

The plan requires review before any second pull, but the later decision must say who reviews and what questions must be answered.

Minimum review questions:

```text
Did actual cost stay within ceiling?
Did request count stay within ceiling?
Did the response match the approved endpoint and request context?
Did raw handling comply with the chosen retention posture?
Did the provider return customer/private or unexpected sensitive data?
Was the response a normal result, error shape, throttle shape, or unknown shape?
Was a shape fingerprint and field summary produced?
Did any undocumented or breaking field behavior appear?
Is a second probe justified, or should M13 stop?
```

No second request should inherit approval automatically.

---

## Proposal Fields for Later Owner Review

The following fields may be drafted as proposals before approval. Drafting them does not authorize execution.

| Field | Current planning posture | Required before execution |
|---|---|---|
| Provider | DataForSEO candidate | Explicit limited admission/use ruling for this probe |
| Endpoint family | SERP API | Exact official endpoint and request mode |
| Query | Candidate list only | One exact approved query string |
| Location | United States/code placeholder | Exact approved location value/code |
| Language | English placeholder | Exact approved language value/code |
| Device | Desktop placeholder | Exact approved value or `not_applicable` |
| Search engine/result type | Unnamed | Exact approved values where applicable |
| Optional request fields | Unnamed | Explicit approved values or omission |
| Funding amount | Expected minimum only | Current verified amount and owner approval |
| Spend ceiling | No spend authorized | Exact maximum dollar amount |
| Billable task ceiling | Proposed one task | Exact ceiling |
| API request ceiling | Not fully defined | Exact ceiling including polling/result retrieval |
| Duplicate policy | No repeat | Exact duplicate key and fail behavior |
| Raw posture | Local/ignored safer default | Exact retention/purge/manifest policy |
| Output paths | Candidate pattern | Exact local paths and Git posture |
| Sanitized summary | Potentially committable | Exact permitted content and review gate |
| Approval reference | Missing | Committed accepted decision path |
| Stop conditions | Categories drafted | Final binding list |
| Post-pull review | Required | Named reviewer and acceptance questions |

---

## What the Later Owner Approval Decision Must Name

Before funding, use of existing credits, CLI implementation for paid execution, or any request, a later owner approval decision must explicitly name all of the following.

### A. Authority and narrow admission

```text
provider_name
provider_admission_scope
approval_reference
approval_actor
approval_date
one-probe-only rule
no inherited approval for a second pull
```

### B. Funding and cost controls

```text
current verified minimum payment
approved funding amount
whether existing credits may be used
account-level budget/limit control
maximum probe spend
billable task ceiling
API request ceiling
actual-cost recording requirement
```

### C. Exact request recipe

```text
exact official endpoint
request mode
query
location value/code
language value/code
device value or not_applicable
search engine/result type
all other cost/scope/shape-relevant request fields
explicitly omitted optional fields
normalized request payload or payload hash
```

All of these remain proposals until the owner accepts the decision.

### D. Duplicate and retry controls

```text
duplicate-prevention key
pre-submit duplicate check
no repeat override
no automatic retry
no retry after auth, cost, shape, or retention failure
```

### E. Credential and secret handling

```text
credential source
environment/config naming
no logging of credentials
no credential material in evidence files
redaction behavior
missing-credential failure behavior
```

### F. Rights, retention, and raw-support handling

```text
rights_class
rights_basis
allowed-use statement
retention_class
retention_basis
raw payload posture
raw local destination
Git ignore/commit posture
retention duration or purge deadline
manifest retention rule
SHA-256 requirement
byte-count/media-type requirement
redaction rule
sanitized-summary rule
backup rule if applicable
```

### G. Required outputs

```text
probe manifest
raw response if permitted
request payload hash
raw payload hash if retained
field-path summary
shape fingerprint
top-level status/error/cost summary
actual task/call count
actual provider-reported cost
stop-condition result
claim-use warning
```

### H. Stop conditions

At minimum:

```text
price cannot be verified
estimated spend exceeds ceiling
billable task count exceeds ceiling
API request count exceeds ceiling
endpoint or request field differs from approval
credentials missing or malformed
customer/private marker detected
duplicate key detected
provider authentication error
unexpected charge/cost metadata
provider throttle/error/unknown shape
raw-retention posture unclear
customer/private data appears in response
required evidence output cannot be produced safely
```

### I. Post-pull gate

```text
named review requirement
review questions
no observation ingestion
no Postgres write
no schema/migration decision from one sample
no second pull without a new or amended owner decision
```

---

## Hammer and Acceptance-Gate Implications

Before any executable probe is accepted, the later CLI/task must prove or demonstrate the relevant hostile paths at its own bounded scope.

Minimum applicable expectations:

```text
H2  rights fail closed
H3  retention fails closed
H4  customer/private input rejection
H5  no strategy/recommendation storage
H6  CapturePackage/probe manifest validation
H7  provider cost, task, request, and duplicate controls
H8  provider attribution preserved
H9  timing/freshness context preserved
H12 raw integrity and shape/drift handling
H18 hostile/weird input rejection
H20 duplicate/concurrent submission resistance where applicable
H21 audit/approval before execution
H22 rollback/recovery expectations for local probe evidence where applicable
```

M12's accepted local C2 hammer evidence does not automatically pass these provider-probe paths.

The later probe approval and implementation work must name which tests or manual proofs are required before the paid execution flag can be used.

---

## Review Conclusion

### Ready now

```text
The planning concept is coherent.
The probe is correctly tiny and non-customer.
The provider remains candidate-only.
The one-task/no-repeat/no-retry posture is sound.
The raw-manifest/hash/field-summary concepts are sound.
The next safe document is a proposed owner approval decision or a CLI requirements spec.
```

### Not ready now

```text
Funding is not approved.
Credits must not be added.
Existing credits must not be used.
No endpoint is approved.
No query/location/language/device recipe is approved.
No CLI implementation is approved.
No provider call is approved.
Raw JSON retention is not approved.
No Postgres, schema, or migrations are approved.
```

### Required next gate

A later proposed owner decision may now be drafted, but it must remain unaccepted until the owner explicitly rules on the concrete fields listed in this review.

The decision must be exact enough that an implementation cannot invent missing endpoint, request, cost, retention, or stop-condition values.

---

## Final Rule

```text
The plan is ready for a concrete approval-gate draft.
It is not ready for money, code, or a request.
Proposal fields remain proposals until the owner accepts every binding value.
No credits. No calls. No Postgres. No schema goblin jazz.
```
