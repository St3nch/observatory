# PF-02 — DataForSEO sandbox transport and Evidence smoke

**Status:** ready
**Parent spec:** docs/specs/capture-event-v2.md, “Provider HTTP event version 2”
**Authority:** D8, D9
**Kind:** provider-foundation implementation
**Blocked by:** none
**Approved by:** Project Steward
**Start commit:** `5bb4c3db9737431154f1001b8bcfd4c86677b537`

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
