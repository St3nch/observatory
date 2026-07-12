# M13 DataForSEO Probe Implementation Task Proposal

Status: proposed implementation task
Authority: none — planning only; not implementation approval, funding approval, credential-use approval, or provider-call authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12
Depends on:

- `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`
- `planning-inbox/m13-dataforseo-probe-cli-requirements.md`
- `planning-inbox/m13-dataforseo-official-verification-2026-07-11.md`
- `planning-inbox/m13-controlled-probe-approval-readiness-review.md`

---

## Purpose

Define the exact bounded implementation task that may be authorized later for the one-shot DataForSEO probe.

This proposal exists so implementation does not improvise endpoint, payload, credentials, cost controls, evidence paths, or retry behavior.

It does not authorize implementation.

---

## Entry Gate

Implementation may begin only after an accepted owner decision explicitly authorizes:

```text
one-probe DataForSEO admission
minimum account funding or approved use of existing credits
exact endpoint and request recipe
$0.10 maximum request cost
one billable task
one API request
zero retries
zero polling
capture-and-purge raw posture
CLI implementation
```

Until then:

```text
No source files.
No provider client.
No credentials.
No network call.
```

---

## Proposed Implementation Scope

Create a small, provider-specific one-shot probe under a dedicated module.

Candidate paths:

```text
src/observatory_dataforseo_probe/__init__.py
src/observatory_dataforseo_probe/config.py
src/observatory_dataforseo_probe/recipe.py
src/observatory_dataforseo_probe/preflight.py
src/observatory_dataforseo_probe/evidence.py
src/observatory_dataforseo_probe/cli.py
tests/test_dataforseo_probe_recipe.py
tests/test_dataforseo_probe_preflight.py
tests/test_dataforseo_probe_evidence.py
tests/test_dataforseo_probe_cli.py
```

Exact file layout may be adjusted by the accepted implementation decision, but scope must remain provider-specific and one-shot.

Do not create:

```text
generic provider framework
provider registry implementation
capture scheduler
recurring runner
Postgres adapter
migration folder
API server
MCP tool
web dashboard
customer workflow
```

---

## Required Constants

The implementation must hard-code or decision-bind these accepted values rather than accepting arbitrary CLI overrides:

```text
provider: DataForSEO
endpoint: /v3/serp/google/organic/live/advanced
method: POST
keyword: observatory test page
location_code: 2840
language_code: en
device: desktop
os: windows
depth: 10
billable_task_ceiling: 1
API_request_ceiling: 1
retry_ceiling: 0
polling_ceiling: 0
repeat_ceiling: 0
maximum_expected_cost: 0.10 USD
```

All unnamed optional request fields must be omitted.

The CLI must not expose arbitrary endpoint, payload, keyword, location, language, device, operating-system, depth, or optional-feature flags.

---

## Credential Boundary

Proposed environment variables:

```text
DATAFORSEO_LOGIN
DATAFORSEO_PASSWORD
```

Rules:

- read only at execution time;
- never print values;
- never serialize values;
- never include credentials in exception messages;
- never include authorization headers in evidence;
- fail before network activity if either value is absent;
- redact provider URLs if credentials are embedded accidentally;
- no `.env` file committed;
- no interactive credential prompt;
- no credential storage in operating logs.

Environment-variable names are not secrets. Values are secrets.

---

## CLI Commands

The proposed CLI should expose only bounded modes:

```text
python -m observatory_dataforseo_probe.cli show-recipe
python -m observatory_dataforseo_probe.cli preflight
python -m observatory_dataforseo_probe.cli execute --confirm-paid-request <request-sha256>
python -m observatory_dataforseo_probe.cli summarize --probe-id <probe-id>
python -m observatory_dataforseo_probe.cli purge --probe-id <probe-id>
```

### show-recipe

Must display:

- accepted decision reference;
- endpoint;
- sanitized request body;
- request hash;
- task/request/retry ceilings;
- raw-retention posture;
- all active stop conditions.

Must not access credentials or network.

### preflight

Must validate:

- accepted decision marker exists;
- exact recipe matches accepted values;
- request payload hash;
- credentials are present without printing them;
- evidence root is local and Git-ignored;
- no duplicate key exists;
- exact account/calculator price has been recorded and is at or below `$0.10`;
- account-level limits are recorded if available;
- no optional cost-bearing fields exist;
- one request is sufficient;
- retention and purge deadline are defined.

Must not send a provider request.

### execute

Must require the exact request SHA-256 shown by preflight.

Must reject:

- missing or stale preflight;
- mismatched hash;
- decision still proposed;
- price evidence absent;
- cost above ceiling;
- duplicate key present;
- evidence root not ignored;
- any payload deviation;
- any second execution attempt.

Must send at most one HTTP request.

### summarize

Must operate only on already captured local evidence.

Must produce a sanitized field summary and shape fingerprint.

Must not parse provider output into Observatory observations.

### purge

Must hash the raw payload before purge, remove it, and append purge evidence to the manifest.

Must refuse purge when the target path is outside the approved evidence root.

---

## Network Boundary

Implementation must centralize the provider request in exactly one function.

That function must:

- accept only the immutable recipe object;
- use a finite timeout;
- disable automatic retries;
- send one request only;
- never poll;
- never follow an alternate provider workflow;
- record response status safely;
- write the response once to a temporary path;
- atomically finalize the raw file after hashing if practical;
- preserve error payloads as error evidence, not normal observations.

No general HTTP wrapper should be exposed for arbitrary use.

---

## Evidence Root

Proposed local ignored root:

```text
probe-evidence/dataforseo/<execution-date>/<probe-id>/
```

Candidate files:

```text
preflight.json
request.json
raw-response.json
manifest.json
field-summary.md
shape-fingerprint.json
purge-proof.json
```

Rules:

- `probe-evidence/` must be Git-ignored before execution;
- raw provider content must never be staged;
- request evidence must exclude credentials;
- sanitized summaries may enter Git only through a later exact-path review;
- no cloud sync under the first-probe decision;
- no database write;
- raw response purged by accepted deadline.

---

## Manifest Requirements

The implementation must record at least:

```text
probe_id
recipe_id
approval_reference
approval_commit
implementation_commit
provider_name
endpoint
request_payload_sha256
duplicate_prevention_key
preflight_completed_at
submitted_at
completed_at
HTTP_requests_used
billable_tasks_reported
maximum_expected_cost
provider_top_level_cost
provider_task_level_cost
provider_status_code
provider_status_message
response_class
raw_payload_pointer
raw_payload_sha256
raw_payload_bytes
raw_payload_media_type
shape_fingerprint
field_path_count
stop_condition_triggered
retention_deadline
purge_status
claim_use_warning
```

Audit events must be append-only.

---

## Response Classification

Allowed classes:

```text
normal_provider_response
provider_authentication_error
provider_request_error
provider_throttle_or_limit
provider_error_shape
unknown_shape
local_transport_failure
local_evidence_failure
```

Only `normal_provider_response` may proceed to field summarization.

No response class may produce admitted Observatory observations in M13.

---

## Duplicate Prevention

The duplicate key must include:

```text
provider
endpoint
normalized_request_payload_sha256
approval_reference
```

The implementation must persist a local execution marker before or atomically with submission so a crash cannot make a second execution look unused.

If duplicate-state integrity is uncertain:

```text
Do not submit.
```

No `--allow-repeat` option is permitted.

---

## Required Tests Before Network Authority

At minimum, tests must prove:

- proposed decision blocks execution;
- missing acceptance marker blocks execution;
- payload mutation blocks execution;
- endpoint mutation blocks execution;
- missing credentials block before network;
- credentials are redacted from errors and evidence;
- missing price proof blocks execution;
- price above `$0.10` blocks execution;
- optional cost-bearing field blocks execution;
- non-ignored evidence root blocks execution;
- duplicate key blocks execution;
- second execution blocks execution;
- retry path does not exist;
- polling path does not exist;
- only one network call is possible;
- provider error is not parsed as observation;
- unknown shape fails closed;
- raw hash is recorded;
- purge stays inside evidence root;
- purge proof records the pre-purge hash;
- no database, schema, migration, API, MCP, or recurring path exists.

All tests should use fixtures/mocks only. Tests must not call DataForSEO.

---

## Implementation Acceptance Evidence

Before credits are required for execution, the implementation batch should provide:

```text
source diff
test diff
full local test output
focused hostile-path test output
credential-redaction proof
one-request mock proof
duplicate-block proof
price-ceiling block proof
raw hash/purge fixture proof
no-network test proof
implementation-readiness review
```

The tested CLI may exist before credits are added only if an accepted owner decision explicitly authorizes no-network implementation.

---

## Non-Authorizations

This proposal does not authorize:

```text
implementation
funding
credentials
provider request
raw provider capture
second request
provider abstraction
Postgres
schema
migrations
observation ingestion
API/MCP
dashboard
customer workflow
recurring capture
```

---

## Completion Rule

The implementation task is complete only when:

- exact bounded code exists;
- all hostile-path tests pass locally;
- no network request has occurred during implementation/testing;
- implementation-readiness review confirms the accepted decision is enforced;
- the owner is told explicitly when credits are actually needed;
- execution remains separately gated.

---

## Final Rule

```text
Build a dead-simple one-shot microscope, not a provider platform.
The code may know one recipe.
It may send one request only after every gate is real.
It must be easier to stop than to spend.
```
