# Decision M13-D1 — DataForSEO Controlled Probe Approval

Status: accepted — fixture-only implementation authority; funding and provider execution remain pending
Date: 2026-07-11
Owner ruling: accepted 2026-07-12 for bounded no-network CLI implementation and fixture/mock testing only
Related milestone: M13 — Provider Admission and Controlled Pull Plan
Related files:

- `planning-inbox/m13-dataforseo-admission-and-probe-plan.md`
- `planning-inbox/m13-dataforseo-probe-plan-review.md`
- `planning-inbox/m13-dataforseo-probe-cli-requirements.md`
- `planning-inbox/m13-dataforseo-official-verification-2026-07-11.md`
- `planning-inbox/m13-controlled-probe-approval-readiness-review.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `contracts/provider-testimony.md`
- `contracts/scope-rights-retention.md`
- `contracts/capturepackage-v0-1.md`
- `contracts/raw-archive-provider-drift.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`

---

## Decision

Accepted owner ruling:

```text
Authorize bounded fixture-only, no-network implementation and fixture/mock testing for the one-shot DataForSEO SERP probe described in this decision.

Bind the implementation to the single endpoint, request recipe, cost ceiling, task/request ceilings, duplicate controls, credential boundaries, and capture-and-purge posture named here.

Do not authorize account funding, use of existing credits, real credentials, network execution, provider tasks, or raw provider capture yet.

Funding and one-request execution require a later explicit owner ruling after implementation and hostile-path evidence are reviewed.
```

Current authority:

```text
CLI source implementation: authorized, fixture-only and no-network.
Fixture/mock hostile-path tests: authorized.
Credits: not authorized.
Use of existing credits: not authorized.
Real credentials: not authorized.
API request: not authorized.
Provider task: not authorized.
Raw provider payload capture: not authorized.
Postgres: not authorized.
Schema: not authorized.
Migrations: not authorized.
```

---

## Context

M12 proved the bounded fixture-based C2 observation path locally. M13 is active to plan admission of the first real provider through rights, retention, cost, recipe, duplicate-prevention, raw-support, and stop-condition gates.

The M13 probe plan and review concluded that a tiny DataForSEO response-shape probe is coherent enough for a concrete owner decision proposal, but not yet approved for money, code, or execution.

The purpose of the proposed probe is not to collect useful SEO intelligence. It is to inspect one real provider response envelope and payload shape before later persistence or schema decisions.

Provider output remains testimony, not truth. Raw JSON remains probe evidence, not schema approval.

## Official Verification Status — 2026-07-11

Fresh official verification confirmed:

```text
endpoint exists
live advanced is a one-request flow with one task per call
keyword, location_code, language_code, device, os, and depth fields are valid
location_code 2840 and language_code en remain official examples
desktop/windows is a valid pairing
depth 10 is valid and avoids the documented above-10 surcharge risk
minimum payment remains $50
identical tasks remain a documented user-side error
provider-side API task retention remains 365 days
SERP usage restrictions remain in current Terms
```

The exact current price for the exact proposed request was not reliably available in retrievable official page text.

Owner timing ruling recorded 2026-07-12:

```text
Exact request pricing may be verified after credits are added, using the authenticated account interface or official calculator, but it must be confirmed before the paid request is sent.
```

This timing ruling does not itself accept this proposed decision or authorize funding, CLI implementation, credentials, or a provider request.

All unnamed optional fields must be omitted. No optional cost-bearing feature may be enabled. Top-level and task-level response cost fields must both be recorded.

---

## Proposed Narrow Admission

| Field | Proposed binding value |
|---|---|
| Provider | DataForSEO |
| Admission scope | One controlled payload-inspection probe only |
| Provider status before acceptance | Candidate; blocked for execution |
| Endpoint family | SERP API |
| Search engine | Google |
| Result type | Organic |
| Request mode | Live advanced |
| Proposed endpoint | `/v3/serp/google/organic/live/advanced` |
| Business purpose | Inspect response envelope, status/cost fields, nested field paths, and shape fingerprint |
| Customer use | Forbidden |
| Recurring use | Forbidden |
| Second request | Forbidden without a new or amended accepted owner decision |

The exact endpoint must be rechecked against current official DataForSEO documentation immediately before owner acceptance. If the endpoint is unavailable, renamed, differently priced, or materially changed, this proposal must be amended rather than silently substituted.

---

## Proposed Request Recipe

Recipe ID:

```text
m13-dataforseo-serp-probe-v0-1
```

Proposed request fields:

```text
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
```

Proposed request envelope:

```json
[
  {
    "keyword": "observatory test page",
    "location_code": 2840,
    "language_code": "en",
    "device": "desktop",
    "os": "windows",
    "depth": 10
  }
]
```

Every value above is a proposal until this decision is accepted.

Pre-acceptance verification must confirm that:

- the endpoint accepts every named field;
- `location_code: 2840` still represents the intended United States context;
- `language_code: en` is valid for the endpoint;
- `device: desktop` and `os: windows` are valid together;
- `depth: 10` is supported and does not cause unexpected cost;
- no unnamed provider default materially changes cost, scope, or response shape;
- the endpoint does not require another cost-bearing call.

No implementation may invent, omit, or substitute request values.

---

## Funding and Cost Controls

### Proposed funding amount

```text
The current official DataForSEO minimum account payment only.
Expected planning value: $50.
```

The official minimum must be freshly verified before owner acceptance and again immediately before funding if funding does not occur the same day.

If the official minimum differs from the accepted decision value:

```text
Stop. Amend the decision. Do not fund.
```

### Proposed probe spend ceiling

```text
Maximum actual provider-reported cost: $0.10
```

This ceiling is intentionally far below the expected funded balance.

If current official endpoint pricing cannot be verified or indicates the request could exceed `$0.10`:

```text
Do not submit.
```

### Proposed task and request ceilings

```text
Billable task ceiling: 1
Total API request ceiling: 1
Retry ceiling: 0
Polling/status request ceiling: 0
Repeat submission ceiling: 0
Second-pull authority: none
```

A request mode that requires task creation plus polling or result retrieval is outside this proposal.

### Account-level controls

Before any accepted execution, the operator must enable the narrowest available account-level spending or usage limits that do not exceed the approved funding and probe ceilings.

If account-level controls are unavailable, that fact must be recorded in the preflight evidence. It does not weaken the CLI/request ceiling.

---

## Duplicate Prevention

The normalized request payload must be serialized deterministically and hashed with SHA-256 before submission.

The duplicate-prevention key must include:

```text
provider_name
endpoint
normalized_request_payload_sha256
approval_reference
```

For this first probe:

```text
Any existing matching duplicate-prevention key blocks submission.
No repeat override is allowed.
```

A missing duplicate registry or inability to prove no prior matching submission is a stop condition.

---

## Credential and Secret Handling

Proposed credential source:

```text
local environment variables or local ignored configuration only
```

Binding requirements before implementation or execution:

- credential names must be defined in the later CLI requirements or implementation task;
- credentials must never be committed;
- credentials must never be written to raw response, manifest, field summary, logs, exception output, or command history where avoidable;
- authentication headers and credential-bearing request fields must be redacted before evidence output;
- missing or malformed credentials must fail before any network request;
- credentials may not be passed to an LLM, agent prompt, API/MCP response, or report.

This decision does not create credentials, request credentials from the owner, or authorize CLI implementation while proposed.

---

## Rights and Allowed Use

Proposed rights posture:

```text
rights_class: provider_limited_internal_probe
rights_basis: DataForSEO official terms, privacy materials, endpoint documentation, and accepted M13 owner decision
allowed_use: internal payload-shape inspection and later planning input only
```

The probe output may not be used as:

- broad SERP republication;
- a search-engine substitute;
- customer-facing evidence;
- a recommendation;
- a strategy record;
- a provider-quality verdict;
- proof of endpoint stability;
- proof of schema completeness;
- permission for recurring capture;
- permission for a second provider request.

Fresh official terms and documentation must be checked before owner acceptance. Any unresolved allowed-use or raw-retention ambiguity fails closed.

---

## Raw Payload and Retention Posture

Proposed posture:

```text
capture_and_purge_raw
```

Proposed local evidence path:

```text
probe-evidence/dataforseo/2026-07-11/<probe-id>/raw-response.json
probe-evidence/dataforseo/2026-07-11/<probe-id>/manifest.json
probe-evidence/dataforseo/2026-07-11/<probe-id>/field-summary.md
```

The actual execution date must replace `2026-07-11` if execution occurs later.

Binding raw rules:

- `probe-evidence/` remains local and Git-ignored;
- raw JSON must never be committed;
- raw JSON must never enter Postgres or another database;
- raw JSON must never be uploaded to cloud storage under this decision;
- raw JSON must be hashed with SHA-256 immediately after write;
- byte count and media type must be recorded;
- raw content must be reviewed only for payload shape, unexpected sensitive content, and required field summary;
- raw JSON must be purged no later than seven calendar days after capture;
- raw JSON must be purged sooner after the owner accepts the field summary and manifest as sufficient;
- purge date, reason, actor, and pre-purge hash must be recorded in the manifest;
- a sanitized manifest and sanitized field summary may be proposed for Git only after human review confirms they contain no credentials, raw result content, customer/private data, or disallowed provider content;
- committing any sanitized artifact requires a separate exact-path review and commit; it is not automatic.

Proposed manifest survival:

```text
A sanitized manifest may survive raw purge if provider rights and retention review permit it.
```

If even minimal manifest retention is unclear:

```text
Purge the raw payload and retain no provider-derived artifact beyond an owner-authored local execution note permitted by the accepted decision.
```

---

## Required Probe Outputs

A successful probe must produce, subject to the accepted retention posture:

```text
probe_id
recipe_id
approval_reference
provider_name
endpoint
normalized_request_payload_sha256
submitted_at
completed_at
operator
rights_class
rights_basis
retention_class
retention_basis
spend_ceiling
actual_provider_reported_cost
billable_task_ceiling
billable_tasks_used
API_request_ceiling
API_requests_used
duplicate_prevention_key
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

The field summary must answer:

- What top-level keys were returned?
- What task, status, error, and cost fields were returned?
- What nested result paths were returned?
- Which timestamps were present and what did they appear to represent?
- Which fields were provider scores, estimates, or model outputs?
- Which fields appeared stable, volatile, optional, or result-specific?
- Which fields might later deserve structured promotion?
- Which fields should remain raw-support-only?
- Were undocumented or unexpected fields observed?
- Was the response a normal result shape, provider error shape, throttle shape, or unknown shape?

The field summary is evidence about one payload shape. It is not schema approval.

---

## Stop Conditions

The future probe must stop before submission if:

- this decision is still proposed;
- the owner has not explicitly accepted every binding value;
- current official minimum funding or endpoint pricing is unverified;
- the official endpoint differs from the accepted endpoint;
- any request field differs from the accepted recipe;
- estimated cost could exceed `$0.10`;
- billable task count could exceed one;
- API request count could exceed one;
- the selected mode requires polling, retrieval, or a second request;
- credentials are missing or malformed;
- duplicate-prevention evidence is missing;
- a matching duplicate key exists;
- customer/private markers are present;
- raw-retention or rights posture is unclear;
- the local evidence destination is not Git-ignored;
- required preflight evidence cannot be recorded.

The future probe must stop after response receipt if:

- provider-reported cost exceeds `$0.10`;
- the provider returns an authentication, throttle, malformed, or unknown response shape;
- customer/private or unexpected sensitive content appears;
- raw payload hashing fails;
- required manifest or field-summary evidence cannot be produced safely;
- any second request would be required.

There is no automatic retry.

---

## Preflight Evidence Required Before Execution

Even after owner acceptance, no paid request may be sent until a preflight record proves:

```text
accepted decision path and commit
fresh official minimum-payment verification
fresh official endpoint-pricing verification
fresh official endpoint/request-field verification
account-level control posture
exact normalized request payload
request payload SHA-256
estimated maximum cost
billable task count
API request count
no-duplicate result
Git-ignore status of local raw destination
credential-source presence without revealing secrets
rights/retention check
operator confirmation
```

The CLI or operator procedure must present the complete preflight summary before an explicit paid-execution confirmation.

---

## Post-Pull Review Gate

After the one allowed response, M13 must stop and review the probe before any further provider work.

Required review questions:

```text
Did actual cost stay within the accepted ceiling?
Did billable task and API request counts stay within ceiling?
Did the exact approved request execute without substitution?
Did the response match a normal, error, throttle, or unknown shape?
Did raw handling comply with the accepted retention posture?
Did the response contain customer/private or unexpected sensitive data?
Were SHA-256, byte count, manifest, field summary, and shape fingerprint produced?
Did provider output remain provider-attributed testimony?
Did any field suggest parser or schema risk?
Was raw data purged by the accepted deadline?
Is another probe justified?
```

No answer to the last question creates authority for another request.

A second request requires a new or amended proposed decision followed by explicit owner acceptance.

---

## Options Considered

| Option | Summary | Result | Reason |
|---|---|---|---|
| A | Continue planning without an approval decision proposal | Rejected for next-step purposes | The plan review found enough information to draft a concrete gate |
| B | Propose one live advanced SERP request | Selected as proposal | It can return one response in one API request and avoids polling/task-retrieval expansion |
| C | Propose task-post plus result retrieval | Rejected | It introduces multiple requests, polling/retrieval ambiguity, and a larger accidental-spend surface |
| D | Probe multiple endpoint families | Rejected | Too broad for first provider microscope slide |
| E | Build first, decide values later | Rejected | Violates audit-first, cost, rights, and owner-approval gates |
| F | Create Postgres/schema before payload inspection | Rejected | Raw JSON must inform later planning; one sample still cannot approve schema |

---

## Scope

This proposed decision applies only to:

- one DataForSEO Google organic live advanced payload-inspection request;
- the exact proposed request recipe;
- the exact proposed funding, cost, task, request, raw, and purge ceilings;
- local probe evidence needed to inspect one response shape;
- later owner review of whether the proposal should be accepted, amended, or rejected.

This proposed decision does not apply to:

- broad DataForSEO admission;
- any other DataForSEO endpoint;
- AI Optimization API;
- marketplace, backlink, Labs, Merchant, Reviews, Business Data, Domain Analytics, or Content Analysis APIs;
- customer or SearchClarity data;
- useful business data collection;
- recurring capture;
- a second request;
- provider clients beyond the eventual bounded probe;
- Postgres;
- schema or migrations;
- observation ingestion;
- API/MCP exposure;
- dashboards;
- reports;
- strategy or recommendations.

---

## Authority Impact

```text
scope change only if accepted
```

While proposed, this file has no authority impact.

If accepted, it creates only a narrow one-probe exception inside M13. It does not alter Observatory doctrine or broadly admit DataForSEO.

---

## Follow-up Work

| Follow-up | Target milestone | Target file(s) | Status |
|---|---|---|---|
| Owner reviews every binding proposal value | M13 | this decision | pending |
| Fresh official endpoint, field, minimum-payment, pricing, terms, and retention verification | M13 | preflight or decision amendment | blocked until owner chooses to advance proposal |
| Draft bounded CLI requirements | M13 | `planning-inbox/m13-dataforseo-probe-cli-requirements.md` | allowed as requirements only after this proposal exists; no implementation |
| Implement bounded CLI | M13 or explicit task | later implementation files | forbidden until owner accepts decision and implementation gate |
| Fund account | M13 | external owner action | forbidden until accepted decision and fresh verification |
| Execute one probe | M13 | local probe evidence | forbidden until accepted decision, implementation proof, and preflight pass |
| Review probe and decide whether M13 can close | M13 | later readiness review/decision | blocked until lawful probe evidence exists or owner closes M13 without execution |

---

## Anti-Drift Notes

Future agents must not infer:

- proposed means accepted;
- an exact endpoint in this file may be called while status is proposed;
- the owner has approved `$50` funding or `$0.10` spend;
- existing credits may be used;
- CLI implementation is authorized;
- credentials may be requested or stored;
- one probe admits DataForSEO broadly;
- one response defines the database schema;
- raw JSON may be committed;
- temporary raw retention permits durable archive;
- a successful response authorizes a second request;
- M12 fixture hammers automatically pass provider-probe hammers;
- Postgres, schema, or migrations are authorized;
- provider output is truth;
- customer data boundaries are weakened.

No fake-mustache interpretation is valid.

---

## Supersession

If superseded later, record:

```text
Superseded by:
Date:
Reason:
```

---

## Final Rule

```text
This is a proposed key, not an unlocked door.
Until the owner accepts it, the provider machine stays off.
No credits. No calls. No CLI. No Postgres. No schema goblin jazz.
```
