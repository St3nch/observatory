# M13 DataForSEO Probe CLI Requirements

Status: planning specification
Authority: none — requirements only; not implementation approval, provider admission, funding approval, or request authorization
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-11
Related decision proposal: `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`

---

## Purpose

This document defines the minimum behavior of a future one-shot DataForSEO probe CLI if the owner later accepts a concrete controlled-probe decision and separately opens implementation.

The CLI exists only to enforce a narrow approved request recipe, capture auditable response-shape evidence, and stop safely.

It is not:

- a general DataForSEO client;
- a reusable provider SDK;
- a capture runner;
- a recurring job;
- an observation ingester;
- a parser pipeline;
- a Postgres writer;
- an API/MCP tool;
- a dashboard backend;
- a customer workflow;
- a strategy or recommendation engine.

Until the related decision is accepted and implementation is separately authorized:

```text
Do not implement this CLI.
Do not add credits.
Do not use existing credits.
Do not call DataForSEO.
```

---

## Governing Inputs

The future CLI must conform to:

- `02-boundaries.md`
- `ROADMAP.md`
- `planning-inbox/m13-dataforseo-admission-and-probe-plan.md`
- `planning-inbox/m13-dataforseo-probe-plan-review.md`
- `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`
- `research/rg1-dataforseo-rights-retention-cost.md`
- `research/rg10-capturepackage-v0-1-inputs.md`
- `research/rg11-raw-archive-provider-drift.md`
- `contracts/provider-testimony.md`
- `contracts/scope-rights-retention.md`
- `contracts/capturepackage-v0-1.md`
- `contracts/raw-archive-provider-drift.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`

If these conflict, root boundary law and an accepted decision win.

---

## Authority Model

The CLI must require an accepted, committed decision file as its execution authority.

Planning defaults:

```text
accepted decision required: yes
accepted decision path required: yes
accepted decision commit required: yes
execution disabled when decision status is proposed: yes
```

The CLI must not infer approval from:

- a filename containing `approval`;
- a chat message;
- environment variables;
- account balance;
- existing credentials;
- an implementation task;
- a successful dry run;
- a previous probe;
- an operator confirmation alone.

The accepted decision must bind the exact provider, endpoint, request payload, cost ceiling, request ceiling, task ceiling, retention posture, stop conditions, and one-probe scope.

---

## Command Surface

The future CLI should expose the smallest useful command surface.

Candidate commands:

```text
probe preflight
probe execute
probe summarize
probe purge
probe verify
```

No command may imply broad provider functionality.

Forbidden commands or modes:

```text
watch
schedule
repeat
bulk
batch
sync
ingest
parse-all
retry
poll
serve
api
mcp
write-db
```

The first implementation may combine commands if doing so reduces accidental execution surface, but the behavioral gates below remain mandatory.

---

## Required Execution States

The CLI must model explicit states:

```text
draft
preflight_blocked
preflight_passed
execution_confirmed
request_sent
response_received
summary_pending
summary_complete
purge_pending
purged
failed
```

Rules:

- `preflight_passed` does not authorize execution by itself.
- `execution_confirmed` must be tied to the exact request hash shown during preflight.
- Any request mutation after confirmation resets state to `preflight_blocked`.
- A failed or ambiguous state must never silently become retryable.
- `response_received` does not mean observation admission.

---

## Configuration Requirements

The CLI must separate immutable decision-bound values from local runtime values.

Decision-bound values include:

```text
provider
endpoint
request method
request payload
normalized request payload SHA-256
billable task ceiling
API request ceiling
retry ceiling
spend ceiling
raw retention posture
purge deadline
allowed local destination pattern
required outputs
stop conditions
```

Local runtime values may include:

```text
credential source
execution timestamp
probe ID
local destination root
operator identity
```

Local runtime values must not broaden or override decision-bound values.

No general-purpose config file may enable alternate endpoints or arbitrary payloads.

---

## Credential Requirements

Credentials must come only from local environment variables or local ignored configuration named by the later implementation task.

Required behavior:

- check credential presence before any network operation;
- validate only enough format to fail obvious missing/malformed cases;
- never print credential values;
- never write credential values to files;
- never include credentials in exceptions, tracebacks, manifests, request snapshots, field summaries, or hashes intended for sharing;
- redact authorization headers and credential-bearing fields before logging;
- avoid credential values in command-line arguments and shell history;
- never expose credentials to LLMs, agents, API/MCP output, or customer artifacts.

Missing or malformed credentials must produce a local failure with zero network requests.

---

## Request Binding and Normalization

The CLI must construct exactly one request from the accepted decision.

It must not accept arbitrary query, endpoint, location, language, device, depth, engine, result-type, operating-system, or mode flags during paid execution.

Before submission it must:

1. construct the request from the accepted decision binding;
2. serialize the request deterministically;
3. compute SHA-256 of the normalized request payload;
4. compare it to the accepted request hash or generate a reviewable hash if the accepted decision requires one at preflight;
5. refuse execution if any field differs from the accepted recipe;
6. show the complete non-secret normalized request to the operator;
7. require explicit confirmation bound to that exact hash.

Any mutation between preflight and submission must invalidate confirmation.

---

## Cost and Request Controls

The CLI must enforce all accepted ceilings before sending a request.

Required controls:

```text
billable task ceiling
API request ceiling
retry ceiling
polling ceiling
repeat-submission ceiling
provider-reported cost ceiling
```

For the first proposed probe, planning values are:

```text
billable tasks: 1
API requests: 1
retries: 0
polling requests: 0
repeat submissions: 0
```

These values remain proposals until owner acceptance.

The CLI must refuse an endpoint mode that requires a second call to retrieve results.

It must not silently retry on:

- timeout;
- authentication failure;
- provider error;
- malformed response;
- rate limit;
- connection reset;
- unknown status;
- write failure.

One attempt means one attempt. The API beast does not get bonus lives.

---

## Duplicate Prevention

The CLI must maintain local duplicate-prevention evidence before submission.

Minimum duplicate key:

```text
provider_name
endpoint
normalized_request_payload_sha256
approval_reference
```

Required behavior:

- check for an existing matching key before execution;
- fail closed if the duplicate registry cannot be read or trusted;
- record the key before or atomically with request-attempt evidence so concurrent/manual repeat attempts cannot slip through;
- never provide `--allow-repeat` for the first probe;
- treat a previous failed network attempt conservatively unless evidence proves no request left the machine.

No matching request may be resubmitted under the first approval.

---

## Preflight Requirements

The CLI must produce a preflight record before paid execution.

The record must contain no secrets and must prove:

```text
accepted decision path
accepted decision commit
provider and endpoint
exact normalized request payload
request payload SHA-256
verified current pricing reference/date
estimated maximum cost
spend ceiling
billable task ceiling
API request ceiling
retry/poll/repeat ceilings
no-duplicate result
credential source present without revealing value
local destination
Git-ignore proof for raw destination
rights class and basis
retention class and basis
purge deadline
operator
preflight timestamp
```

A preflight record is invalid if any required field is missing or marked with vague language such as `probably`, `default`, `TBD`, or `whatever provider uses`.

---

## Explicit Paid-Execution Confirmation

Execution must require a deliberate confirmation step after preflight.

The confirmation must display:

```text
provider
endpoint
request payload
request hash
maximum spend
maximum tasks
maximum requests
raw-retention posture
purge deadline
accepted decision reference
```

The confirmation must require an explicit typed token or equivalent non-accidental action.

The token must be valid only for:

- the exact request hash;
- the current preflight record;
- the current process invocation;
- a short local validity window.

A generic `--yes` flag alone is insufficient unless an accepted implementation decision specifically permits it and equivalent safeguards remain.

---

## Network Boundary

The CLI must have one narrow outbound network path to the accepted DataForSEO endpoint.

It must not:

- discover alternate endpoints;
- follow provider-supplied links;
- call pricing endpoints automatically unless separately approved as non-billable and necessary;
- poll;
- retry;
- make telemetry calls;
- upload probe evidence;
- contact Postgres;
- expose a listening server;
- invoke API/MCP tools.

The HTTP method, host, endpoint path, content type, and timeout must be explicit in implementation review.

---

## Response Handling

The CLI must treat the response first as provider testimony and raw probe evidence.

Required behavior:

- record HTTP status and provider status/error fields separately;
- distinguish normal response, provider error, authentication error, throttle shape, malformed shape, and unknown shape;
- never parse an error response as a successful observation;
- never infer missing values;
- never transform provider scores into truth;
- never create recommendations or strategy;
- never automatically ingest response content into structured observations;
- never write to Postgres or another database.

If the response cannot be classified safely, mark it unknown and stop.

---

## Local Evidence Layout

Subject to an accepted decision, candidate layout:

```text
probe-evidence/dataforseo/YYYY-MM-DD/<probe-id>/
  preflight.json
  request-manifest.json
  raw-response.json
  manifest.json
  field-summary.md
  purge-record.json
```

Rules:

- `probe-evidence/` must be Git-ignored before execution;
- raw provider response must never be committed;
- no file may contain credentials;
- filenames must not contain query text or secrets;
- writes should be atomic where practical;
- partial writes must be detectable;
- file hashes and byte counts must be recorded.

The actual accepted retention posture may remove or alter files. The CLI must follow the accepted decision, not this candidate list.

---

## Manifest Requirements

The manifest must record at least:

```text
probe_id
recipe_id
approval_reference
approval_commit
provider_name
endpoint
request_payload_sha256
submitted_at
completed_at
operator
rights_class
rights_basis
retention_class
retention_basis
retention_expires_at
spend_ceiling
actual_provider_reported_cost
billable_task_ceiling
billable_tasks_used
API_request_ceiling
API_requests_used
retry_count
poll_count
duplicate_prevention_key
HTTP_status
provider_status_fields
provider_error_fields
response_class
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_media_type
shape_fingerprint
field_path_count
stop_condition_triggered
claim_use_warning
purge_status
```

Required fields may use explicit `not_applicable`; they must not silently disappear.

---

## Field Summary Requirements

The CLI may generate a mechanical field-path inventory, but the resulting summary must remain evidence about payload shape only.

Minimum summary sections:

- top-level keys;
- field paths and observed value types;
- task/status/error/cost paths;
- timestamp paths;
- URL/domain paths;
- provider score/estimate/model-output paths;
- repeated-array/object shapes;
- null/optional fields;
- unexpected fields;
- response classification;
- shape fingerprint inputs;
- fields potentially worth later structured review;
- fields that should remain raw-support-only;
- limitations of one sample.

The CLI must not label any field as an approved schema column.

---

## Shape Fingerprint Requirements

The first implementation may use a simple versioned fingerprint, but it must be deterministic and documented.

Candidate inputs:

```text
sorted field-path set
observed JSON value-type per path
required top-level status/cost field presence
array/object boundary markers
fingerprint version
```

The fingerprint must not include raw values that could leak content or credentials.

A new or unknown fingerprint is evidence for review, not automatic parser/schema mutation.

---

## Purge Requirements

If the accepted posture is `capture_and_purge_raw`, the CLI must support deterministic purge evidence.

Required behavior:

- compute and record the pre-purge raw SHA-256;
- delete only the exact approved raw file path;
- refuse broad directory deletion;
- record purge timestamp, actor, reason, original hash, and deletion result;
- verify the raw file no longer exists;
- preserve only the sanitized manifest/summary artifacts allowed by the accepted decision;
- fail closed if the target path escapes the approved evidence root.

The purge command must never delete unrelated files or entire date/probe roots casually.

---

## Verification Requirements

A `verify` operation should be able to confirm locally:

- decision reference exists and was accepted at execution time;
- request hash matches manifest;
- response hash matches retained raw payload when present;
- task/request/retry counts stayed within ceiling;
- actual cost stayed within ceiling;
- raw destination was local and Git-ignored;
- required summary/manifest fields exist;
- purge deadline and status are coherent;
- no database or API/MCP output occurred;
- no second probe record exists under the same approval.

Verification must not require another provider request.

---

## Failure and Exit Behavior

The CLI must use distinct non-zero exit codes or equivalent structured failure classes for:

```text
approval missing or proposed
approval mismatch
pricing unverified
request mismatch
cost ceiling failure
task/request ceiling failure
duplicate detected
credential failure
rights/retention failure
raw destination unsafe
network failure
provider error
unknown response shape
hash/write failure
summary failure
purge failure
```

Failures must be concise, non-secret, and actionable.

No failure may trigger an automatic retry.

---

## Audit Requirements

The CLI must produce audit evidence before and after any network attempt.

Minimum audit events:

```text
preflight_started
preflight_blocked or preflight_passed
execution_confirmation_requested
execution_confirmed
request_attempt_recorded
request_sent
response_received
response_classified
raw_written
raw_hashed
summary_written
stop_condition_triggered if any
purge_due
purge_completed or purge_failed
verification_completed
```

Audit evidence must be append-only for the probe and must not silently overwrite prior events.

---

## Testing and Hammer Requirements

Before paid execution, implementation must prove at least:

```text
proposed decision blocks execution
missing decision blocks execution
request-field mutation blocks execution
wrong endpoint blocks execution
cost above ceiling blocks execution
second API request blocks execution
retry request blocks execution
duplicate key blocks execution
missing credentials block before network
credentials never appear in outputs
unsafe/non-ignored raw path blocks execution
customer/private marker blocks execution
provider error shape does not become observation
unknown shape fails closed
raw hash mismatch fails verification
purge path traversal is rejected
strategy/recommendation fields are never produced
Postgres/API/MCP paths do not exist
```

M12 fixture test results do not satisfy these provider-probe hammers automatically.

The implementation task must identify which tests are automated and which require owner-local manual proof.

---

## Explicit Non-Requirements

The future first CLI does not need:

- reusable provider abstraction;
- plugin architecture;
- async task orchestration;
- queueing;
- scheduler;
- database persistence;
- schema/migrations;
- web UI;
- API server;
- MCP server;
- customer account support;
- multiple endpoints;
- multiple queries;
- retries;
- polling;
- observation ingestion;
- report generation.

Adding these would be scope failure, not helpful engineering.

---

## Implementation Gate

Implementation may begin only after all are true:

```text
1. The owner accepts a concrete controlled-probe decision.
2. Fresh official endpoint, field, pricing, minimum-payment, terms, and retention verification is recorded.
3. The accepted decision names exact request and ceilings.
4. A bounded implementation task names exact files and tests.
5. The owner or roadmap explicitly opens CLI implementation.
```

Until then, this document is requirements only.

---

## Final Rule

```text
Build a one-shot safety cage, not a provider platform.
The CLI may send exactly what was approved, once, and then stop.
No approval means no code. No accepted gate means no request.
```
