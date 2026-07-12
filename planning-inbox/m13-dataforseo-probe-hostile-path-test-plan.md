# M13 DataForSEO Probe Hostile-Path Test Plan

Status: planning test plan
Authority: none — not implementation approval or provider-call authority
Milestone: M13 — Provider Admission and Controlled Pull Plan
Date: 2026-07-12
Related:

- `planning-inbox/m13-dataforseo-probe-cli-requirements.md`
- `planning-inbox/m13-dataforseo-probe-implementation-task-proposal.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`

---

## Purpose

Define the hostile-path proof required before the one-shot DataForSEO probe can be considered implementation-ready.

All tests are fixture/mock only.

```text
No test may call DataForSEO.
No test may require credits.
No test may use real credentials.
```

---

## Acceptance Posture

The probe implementation fails acceptance if any test below is absent, skipped without written justification, flaky, or dependent on a real provider call.

M12 C2 hammer results do not automatically satisfy M13 provider-probe hammers.

---

## Test Matrix

| ID | Hostile path | Expected behavior | Hammer |
|---|---|---|---|
| P01 | Decision remains proposed | Execute command rejects before credentials/network | H21 |
| P02 | Accepted decision reference missing | Reject | H21 |
| P03 | Approval commit mismatch | Reject | H21/H19 |
| P04 | Endpoint differs by one character | Reject | H6/H7 |
| P05 | Request field added | Reject | H6/H7 |
| P06 | Request field removed | Reject | H6 |
| P07 | Keyword changed | Reject | H6 |
| P08 | Depth raised above 10 | Reject | H7 |
| P09 | Cost-bearing optional field present | Reject | H7 |
| P10 | Price proof missing | Reject | H7/H21 |
| P11 | Price proof stale or for another endpoint | Reject | H7 |
| P12 | Expected cost above $0.10 | Reject | H7 |
| P13 | Task ceiling above one | Reject | H7 |
| P14 | Request ceiling above one | Reject | H7 |
| P15 | Retry configured | Reject | H7 |
| P16 | Polling configured | Reject | H7 |
| P17 | Duplicate key exists | Reject | H7/H20 |
| P18 | Duplicate state unreadable | Fail closed | H20/H21 |
| P19 | Two execute processes race | At most one obtains execution lease | H20 |
| P20 | Credentials missing | Reject before network | H18/H21 |
| P21 | Credentials malformed | Reject before network | H18 |
| P22 | Exception contains credential text | Test fails; redact | H17/H18 |
| P23 | Evidence root not Git-ignored | Reject | H12/H21 |
| P24 | Evidence path escapes root | Reject | H18/H22 |
| P25 | Existing raw-response file present | Reject; no overwrite | H19 |
| P26 | Raw write interrupted | No finalized valid payload without hash | H12/H22 |
| P27 | Response hash mismatch | Block summarize | H12 |
| P28 | Provider auth error | Classify error; no observation | H8/H12 |
| P29 | Provider throttle/error shape | Classify error; no observation | H8/H12 |
| P30 | Unknown response shape | Fail closed | H12/H18 |
| P31 | Provider cost exceeds ceiling | Record breach; stop all further work | H7/H21 |
| P32 | Top-level and task-level costs disagree | Warning/block review | H7/H8 |
| P33 | Customer/private marker appears | Quarantine and stop | H4 |
| P34 | Field summary includes raw result text | Reject sanitized artifact | H4/H12 |
| P35 | Strategy/recommendation phrase emitted | Reject | H5 |
| P36 | Observation ingestion attempted | Reject/no code path | H5/H6 |
| P37 | Database import attempted | Reject/no dependency | H5/H17 |
| P38 | Second execution attempted | Reject | H7/H19/H20 |
| P39 | Purge target outside evidence root | Reject | H18/H22 |
| P40 | Purge without pre-purge hash | Reject | H12/H22 |
| P41 | Purge proof overwrite attempted | Reject; append-only/new file | H19/H22 |
| P42 | Raw retention deadline exceeded | Surface hard failure and purge due | H3/H21 |

---

## Network Call Proof

A fake transport must count calls.

Required assertions:

```text
preflight: 0 calls
show-recipe: 0 calls
summarize: 0 calls
purge: 0 calls
execute success: exactly 1 call
execute any preflight failure: 0 calls
execute transport failure: 1 call maximum
execute duplicate attempt: 0 calls
```

No retry library default may create hidden calls.

---

## Concurrency Proof

Use two local processes or threads against the same duplicate/lease state.

Pass condition:

```text
exactly one process may enter the transport call
all others fail closed before network
```

A simple check-then-write race is not acceptable.

---

## Secret Redaction Proof

Use unmistakable fake credentials such as test-only sentinel strings.

Search all produced output for those sentinels:

```text
stdout
stderr
logs
preflight.json
request.json
manifest.json
field-summary.md
shape-fingerprint.json
exception repr
```

Pass condition: zero occurrences.

---

## Raw Integrity and Purge Proof

Fixture flow:

```text
write fixture response
compute SHA-256
record bytes/media type
summarize from verified raw
attempt tamper
confirm summarize blocks
restore valid fixture
purge
confirm raw absent
confirm purge proof contains original hash, actor, time, reason
```

No test should delete outside a temporary test root.

---

## Provider Error Fixtures

Minimum fixture classes:

```text
normal documented-style envelope
authentication error envelope
task-level error envelope
throttle/limit envelope
empty tasks array
missing cost
cost type changed
missing result
unknown top-level shape
customer/private sentinel content
```

Error fixtures are audit evidence only and must never be treated as normal observations.

---

## No-Scope-Creep Static Checks

Implementation review should verify absence of:

```text
psycopg
sqlalchemy
migration tooling
FastAPI/Flask/Django server setup
MCP server setup
scheduler libraries
cron integration
provider registry abstraction
arbitrary endpoint CLI flag
arbitrary JSON payload CLI flag
repeat override
retry configuration
```

A dependency is not automatically forbidden, but any appearance requires explanation and must not broaden the accepted task.

---

## Required Test Commands

The implementation task must define reproducible commands, likely:

```text
python -m unittest discover -s tests
python -m unittest tests.test_dataforseo_probe_recipe
python -m unittest tests.test_dataforseo_probe_preflight
python -m unittest tests.test_dataforseo_probe_evidence
python -m unittest tests.test_dataforseo_probe_cli
```

Exact commands depend on the accepted implementation layout.

No live-test marker is permitted for M13 implementation acceptance.

---

## Evidence to Record

Implementation readiness must preserve:

```text
Python version
operating system/shell
commit tested
full command
full result summary
test count
failures/errors/skips
proof fake transport was used
proof no credentials were used
proof network was disabled or intercepted
```

---

## Stop Conditions

Stop implementation acceptance if:

- any hostile path fails;
- any test calls the real provider;
- concurrency proof is missing;
- secret sentinel leaks;
- duplicate prevention is non-atomic;
- raw tamper is not detected;
- a second request path exists;
- execution can proceed while the decision is proposed;
- implementation introduces Postgres, schema, migrations, API/MCP, recurring capture, or customer data.

---

## Final Rule

```text
The happy path proves almost nothing.
The probe is ready only when every cheap, dumb, accidental, repeated, leaked, mutated, and half-broken path fails safely.
```
