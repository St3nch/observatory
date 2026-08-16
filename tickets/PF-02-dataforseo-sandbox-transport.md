# PF-02 — DataForSEO sandbox transport and Evidence smoke

**Status:** done
**Parent spec:** docs/specs/capture-event-v2.md, “Provider HTTP event version 2”
**Authority:** D8, D9
**Kind:** provider-foundation implementation
**Blocked by:** none
**Approved by:** Project Steward
**Start commit:** `cb84dd6a02c895f7ed6ff23474d9f12c6104ecf1`

## Why this ticket exists

PF-01 made HTTP-v2 Attempt and Capture documents durable and verifiable, but deliberately
left transport unreachable. This ticket adds the smallest real provider path authorized by
D9: one authenticated, no-spend POST to DataForSEO's sandbox, preceded by a committed and
fully verified Attempt and followed by at most one committed Capture.

DataForSEO is the first provider, not an Observatory-wide transport abstraction. Keep this
implementation isolated so future Ahrefs or Semrush adapters can receive their own
contracts without changing this adapter's Evidence identity. Do not add either future
provider here.

## Fixed adapter and operator entrypoint

Implement only
`dataforseo-serp-google-organic-live-advanced-sandbox-v1`:

- one POST to
  `https://sandbox.dataforseo.com/v3/serp/google/organic/live/advanced`;
- exactly one task;
- caller supplies only `keyword`, `location_code`, and `language_code`;
- `depth=10`, `device=desktop`, and `os=windows` are fixed;
- policy remains `sandbox_no_spend / dataforseo-sandbox-v1`;
- no redirect and no retry.

Provide this service-owned CLI:

    uv run python -m observatory.dataforseo_sandbox \
      --evidence-root PATH \
      --keyword "observatory test" \
      --location-code 2840 \
      --language-code en

The CLI creates a format-2 store only when `FORMAT.json` is absent; otherwise it opens the
existing store normally. It generates a fresh 256-bit nonce, uses live UTC timestamps in
the normative six-fractional-digit `Z` form, and records the installed package version as
`software.observatory_version`. On success it prints only `attempt_id` and
`capture_id`. It must not print a response body, headers, credentials, request
exceptions, or provider messages.

## Credential boundary

Load exactly:

- `OBSERVATORY_DATAFORSEO_LOGIN`
- `OBSERVATORY_DATAFORSEO_PASSWORD`

Both must be non-empty. Missing/empty credentials fail before Attempt creation. Values are
memory-only secrets: never Evidence, URL/query/body/parameters, stdout/stderr, logs,
exception text/repr, dataclass or settings repr, or test snapshots. Do not accept
credentials as CLI arguments.

After the Attempt has committed and passed full D5 read-back, construct
`Authorization: Basic <base64(login:password)>` in the gated send path. Never add it to
or mutate the committed request document. Use `trust_env=False`, TLS verification on,
HTTP/2 off, redirects disabled, and a fixed 30-second connect/write/read/pool timeout.
Ambient proxy and certificate environment variables must not affect the client.

## Structural gate and one-exchange rule

The DataForSEO HTTP send primitive must be unreachable without a closure-held,
caller-unconstructible capability issued by this sequence:

1. validate the closed parameters and construct the exact JCS singleton request body;
2. construct the credential-free HTTP-v2 Attempt;
3. `EvidenceStore.commit_attempt(..., request_body=exact_bytes)`;
4. `EvidenceStore.read_attempt(attempt_id)` and require the exact verified document/body
   facts;
5. freeze those verified facts in the issued capability.

Require the exact concrete `EvidenceStore`, matching the existing fixture gate's
anti-subclass rule. The send primitive accepts only an object issued by its own closure and
sends the frozen body exactly once. No public helper may accept an arbitrary URL, request,
Attempt mapping, or credential-bearing header set and reach the network.

One CLI/service invocation creates exactly one committed Attempt and performs at most one
HTTP exchange. It commits zero or one Capture. It never follows a redirect, retries,
polls, calls task_post/task_get, or makes a second request.

## Exact wire request

Use the five committed application headers in their identity-bearing order. The complete
sent-header multiset is exactly:

- the committed five headers, unchanged;
- one injected `authorization`;
- one protocol-computed `host`;
- one protocol-computed `content-length`.

No `transfer-encoding`, proxy header, SDK default, tracing header, cookie, or additional
accept/user-agent header may be sent. The entity bytes on the wire equal the committed
`request.body` byte-for-byte and `content-length` equals their length.

## Bounded response testimony

For this ticket, “raw bounded HTTP testimony” is refined to an exact
`MAX_RESPONSE_BODY_BYTES = 8_388_608` (8 MiB) per exchange.

- Stream raw entity bytes after transfer framing and before content decoding.
- `accept-encoding: identity` remains mandatory; do not call text/JSON/content-decoding
  convenience accessors.
- EOF at or below the bound is `response_complete`, including a zero-byte body.
- A genuine truncation/read failure after headers is `response_partial` with exactly the
  raw prefix received.
- If a response would exceed the bound, retain exactly the first 8 MiB, stop reading,
  close the exchange, and commit `response_partial` with
  `{"phase":"receive_body","code":"read_failed"}`.
- A failure before headers is `no_response`; a failure after headers is partial. Map
  only to D9's closed phase/code pairs. Never persist or expose exception text.

For response headers, consume raw header pairs, lowercase names, decode values by exact
ISO-8859-1 round trip, preserve retained pair order and duplicates, and apply the complete
`http-headers-v1` secret denylist. Omission objects contain only sorted name/count
markers. Capture the HTTP status/version and timestamps required by event v2. A completed
3xx/4xx/5xx exchange is complete testimony, not a transport failure.

Construct Capture v2 through the PF-01 validators, commit it with the exact retained raw
body (including a zero-byte or partial body), then require full D5 read-back. Do not parse,
classify, derive, summarize, or otherwise interpret the provider envelope.

## Required automated proof

Ordinary tests perform no provider or public-network call.

- Unit tests independently prove closed parameter construction, exact JCS request bytes,
  fresh nonce shape, and timestamp format/order.
- Structural tests prove no send occurs before both durable commit and full read-back;
  forged capability, subclassed store, failed commit, failed verification, wrong adapter,
  paid host/policy, and unknown event version cannot reach the send primitive.
- Header tests prove the exact sent-header equation and absence of every unintended client
  default. Sentinel login/password values are absent from persisted bytes, captured
  stdout/stderr, repr/exception surfaces, and snapshots.
- Deterministic mock tests cover complete non-empty, complete zero-byte, completed
  3xx/4xx/5xx, connect/send/header failures, partial-body failures, duplicate retained
  response headers, every denylisted header, and the 8 MiB boundary at
  `limit-1`, `limit`, and `limit+1`.
- A deterministic loopback server, reached only through an internal dependency-injection
  seam unavailable to the CLI/service API, records the genuine on-wire request. It proves
  byte equality, content length, exact headers, one request only, redirects disabled, and
  a deliberately truncated response becoming a partial Capture. The loopback exercises
  the same post-gate send/read primitive; it does not weaken the production target check.
- Every response branch commits at most one Capture whose parent Attempt and body copies
  verify. Scrub is clean for successful cases. Tampered/unknown events still fail closed.
- Existing fixture capture, mixed-store scrub/derive behavior, event-v1 bytes, and
  published HTTP-v2 vectors remain unchanged.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

The loopback test proves HTTP/1.1 framing behavior only. It does not prove TLS, HTTP/2,
timeout realism, DNS, DataForSEO behavior, or production reachability.

## Operator sandbox smoke required for closure

After deterministic code acceptance, [CHAZ] runs exactly one CLI call with real API
credentials against the sandbox. Before closure, record:

- the committed `attempt_id` and `capture_id`;
- verified read-back of both;
- exact target/policy and one-task/depth-10 facts from the Attempt;
- a real sandbox HTTP response captured as raw Evidence;
- `scrub_store(store) == []`;
- confirmation that the Evidence tree and captured terminal surfaces contain neither
  credential sentinel/value.

The smoke is free dummy data according to DataForSEO's sandbox contract. It proves only
authentication, TLS/DNS reachability at that time, one real response, Evidence commit, and
scrub. It does not prove production data, paid mode, rates, costs, provider semantics,
retries, or historical data.

## Scope constraints

- One implementation commit; do not amend or push.
- Implementer may change only:
  - one new `src/observatory/dataforseo_sandbox.py`;
  - `src/observatory/settings.py`;
  - `pyproject.toml` and `uv.lock`, only to make the already-selected HTTP client a
    runtime dependency;
  - one new focused `tests/test_dataforseo_sandbox.py`;
  - existing tests only when directly required for a regression assertion;
  - this ticket's Status and Implementation report.
- Do not edit `capture.py`, `capture_event.py`, `evidence_store.py`, `derive.py`,
  the fixture API, authority documents, another ticket, or provider strategy.
- If the accepted PF-01 interfaces cannot implement the ticket without one of those
  forbidden edits, stop and report the exact seam; do not widen scope silently.

## Out of scope

- `api.dataforseo.com`, any paid call, credit/budget logic, pricing, or user-data API
- historical SERP, search-volume, Labs, keyword, backlink, OnPage, or other endpoints
- response-envelope interpretation, provider Outcome/Observation/Derivation/API resource
- generic provider registry, Ahrefs, Semrush, or cross-provider comparison
- retry/replay lineage, asynchronous task methods, polling, webhooks, or scheduling
- HTTP/2 support, configurable targets/headers/depth/device/OS, or redirects
- concurrency, crash/power-loss, multi-process writer, or off-host recovery claims

## Verification and implementation report

Review compares the exact Start commit through the one implementation commit. The
implementer must report changed paths, acceptance criterion → proving test mapping,
command output, exact sent headers/body from loopback, failure mapping, row/scrub
accounting, weakest area, unproven limits, and any authority disagreement. Status becomes
`review`, not `done`; only the Project Steward closes the ticket after [CHAZ]'s smoke.

## Implementation report

**End commit:** recorded in the implementation commit (parent
`cb84dd6a02c895f7ed6ff23474d9f12c6104ecf1`).

**Changed paths:** `src/observatory/dataforseo_sandbox.py` (new),
`src/observatory/settings.py` (credential names + memory-only loader),
`tests/test_dataforseo_sandbox.py` (new), `pyproject.toml` and `uv.lock` (httpx
promoted to runtime). No edits to `capture.py`, `capture_event.py`,
`evidence_store.py`, `derive.py`, the fixture API, or other tickets.

**Structural gate:** `_build_transport_gate()` issues a closure-held
`_VerifiedAttempt` only after `type(store) is EvidenceStore`,
`commit_attempt`, full `read_attempt` + request-body byte match, and
sandbox target/policy/version checks. `_exchange` accepts only an issued
instance, marks it used, and sends the frozen body once. Public
`capture_dataforseo_sandbox` has no URL/header/client parameters. CLI
never reaches `_run_gated_capture`'s injection seam.

### Acceptance → proving tests (`tests/test_dataforseo_sandbox.py`)

| Criterion | Test |
|---|---|
| Closed parameters, JCS request bytes, nonce, timestamps | `test_closed_parameters_and_independent_jcs_request_bytes`, `test_fresh_nonce_shape_and_timestamp_format`, `test_caller_cannot_override_fixed_depth_device_os` |
| No send before commit + D5 read-back; forged/subclass/failed commit/read-back/wrong adapter/paid host/policy/unknown version cannot send | `test_forged_capability_cannot_reach_send`, `test_subclassed_store_cannot_issue`, `test_failed_commit_prevents_send`, `test_failed_readback_prevents_send`, `test_wrong_adapter_paid_host_and_unknown_version_cannot_issue` |
| One invocation / one exchange | `test_issue_then_send_is_one_exchange` |
| Sent-header equation + exact body | `test_mock_sent_headers_and_body_equation`, `test_loopback_on_wire_headers_body_and_single_request` |
| Credentials absent from Evidence, stdout/stderr, repr, exceptions | `test_credentials_absent_from_evidence_stdout_repr_and_exceptions`, `test_missing_credentials_fail_before_attempt` |
| Complete nonempty/zero-byte/3xx/4xx/5xx | `test_complete_nonempty_zero_byte_and_status_classes` |
| Connect/send/header failures → no_response | `test_connect_send_and_header_failures_are_no_response` |
| Partial body + 8 MiB bound | `test_partial_body_read_failure`, `test_eight_mib_boundary` |
| Duplicate retained + full denylist | `test_duplicate_retained_and_every_denylisted_header` |
| Loopback on-wire, one request, no redirect, truncated partial | `test_loopback_on_wire_headers_body_and_single_request`, `test_loopback_redirect_is_complete_and_not_followed`, `test_loopback_truncated_body_is_partial` |
| One Capture, D5, scrub | `test_each_branch_commits_one_verified_capture` |
| Event-v1 bytes unchanged | `test_event_v1_bytes_remain_unchanged` |
| CLI prints only ids; no credential args | `test_cli_prints_only_ids`, `test_cli_rejects_credential_arguments` |
| Public API has no URL injection | `test_public_api_has_no_url_or_header_injection` |

### Loopback sent headers (HTTP/1.1, 127.0.0.1)

`accept: application/json`, `accept-encoding: identity`, `connection: close`,
`content-type: application/json`, `user-agent: observatory-dataforseo-v1`,
`authorization: Basic <sentinel>`, `host: 127.0.0.1:<port>`,
`content-length: 119`. Entity bytes equal the 119-byte JCS task array.
Committed Attempt still names `sandbox.dataforseo.com`.

### Failure mapping

- Before headers: `no_response`; connect timeout/error; send write/timeout;
  header protocol/read/timeout.
- After headers: `response_partial` + `receive_body` +
  timeout/protocol_failed/read_failed.
- Bound `limit+1`: retain 8_388_608 bytes, `receive_body`/`read_failed`.
- Completed 3xx/4xx/5xx: `response_complete`, failure null.

### Row / scrub accounting

Successful mock/loopback cases: exactly one committed Attempt and one
Capture; parent + both body copies verify; `scrub_store(store) == []`.
No provider Derivation or PostgreSQL rows.

### Commands

- `uv run pytest -q` — 595 passed, 1 warning
- `uv run ruff check .` — All checks passed
- `uv run mypy` — Success: no issues found in 24 source files

### Review

Two-axis review vs `cb84dd6…`:
- Standards: no hard violations. Duplicated denylist/JCS helpers left because
  PF-01 modules are frozen.
- Spec: paid-policy + WriteTimeout proofs added; Capture read-back now checks
  document/body parity; outer-path `response_headers_at` uses headers-received
  time. At that review point, operator smoke remained for Steward closure.

### Weakest remaining area

httpx exception → D9 phase/code mapping is a best-effort classification of
client errors. Loopback proves HTTP/1.1 framing only.

### Exact unproven limits

- No HTTP/2 or timeout-realism claims beyond the successful sandbox smoke
- No crash/fsync, multi-process writer, or off-host recovery claims
- No paid host, production data, rates, or provider semantics

### Confirmation

Ordinary tests use MockTransport or 127.0.0.1 loopback;
`socket.create_connection` to any other host fails the suite. Sentinel
credentials only. The closure smoke made one real sandbox request and no paid
request.

### Disagreements / authority ambiguities

Ticket Start commit was pre-filled as `5bb4c3db…` (PF-01 close). The assigned
work prompt required start at `cb84dd6a…` (PF-02 authorize), which is this
session's clean HEAD. Recorded start is `cb84dd6a…`.

### Remediation (on `9d2a1aa1301d6d2b5edb902777f74b60f3e20e2f`)

Steward review required three fail-closed fixes. At remediation time, status
remained `review`.

1. **Loopback override allowlist.** `_require_loopback_endpoint` accepts only
   `http://127.0.0.1:<1..65535>/v3/serp/google/organic/live/advanced` (no
   query, fragment, userinfo, other host/scheme, or implicit port). Checked in
   `_run_gated_capture` before Attempt creation and again in `_exchange`
   before the client handler. Public/CLI still have no `endpoint`.
   `test_paid_and_remote_endpoint_override_rejected_before_attempt` proves
   `https://api.dataforseo.com/...` and another remote host raise `StoreError`
   with zero handler calls, zero Attempts, and zero Captures.
2. **Credential-echo fail-closed.** Before Capture construction, scan the
   would-be body and retained header values for login, password, `Basic`
   value, and bare token. Match raises `StoreError("response contained
   credential material")` and commits no Capture. No redaction. Proven by
   `test_credential_echo_in_body_commits_no_capture` and
   `test_credential_echo_in_retained_header_commits_no_capture`.
3. **Empty credentials on the object.** `DataForSEOCredentials` rejects
   `login == ""` or `password == ""` with `CredentialError` and fixed
   non-secret text. Proven by
   `test_direct_empty_credentials_fail_before_attempt`.

## Steward closure

**Closed:** 2026-08-16 by the Project Steward after [CHAZ]'s one authorized
DataForSEO sandbox smoke.

**Accepted commits:** implementation
`9d2a1aa1301d6d2b5edb902777f74b60f3e20e2f`; remediation
`c4f97a39cef25367053a98abe26f3451a17de960`.

**Deterministic review:** the baseline suite passed with 600 tests, Ruff and
mypy clean. The final formal Steward review added 17 adversarial cases for
endpoint rejection, genuine streaming credential echoes, and direct empty
credentials; all 617 tests passed.

**Operator smoke Evidence root:**
`/home/chaz/.local/share/vedaops/observatory/pf02-smoke-20260816T144311Z`

- Attempt:
  `ad118d034193dfaa248dae77b9ad2d4d6e5a995530a6781d56fa1daa26f37916`
- Capture:
  `d72438ceb977737f35dbb7790b3634c3abd6706e61f6ffddcc6993c36a0cfc39`
- Full verified read-back reproduced both IDs.
- The verified Attempt retained the fixed HTTPS sandbox target,
  `sandbox_no_spend / dataforseo-sandbox-v1` policy, exactly one task,
  and fixed depth 10.
- A real sandbox response was committed as 39,334 raw body bytes.
- Format inspection reported `format-2 ok`; store status and scrub both
  exited 0.
- Credential scan reported `clean`; the captured terminal output disclosed
  neither credential value.
- Capture, verification, store, and scrub statuses were all 0.

This closes only the sandbox transport claim: authentication, TLS/DNS
reachability at the smoke time, one real sandbox response, durable Evidence,
verified read-back, credential non-disclosure, and clean scrub. It does not
claim paid-host behavior, production data or semantics, rates/costs, retries,
historical data, HTTP/2, timeout realism, or broader provider support.
