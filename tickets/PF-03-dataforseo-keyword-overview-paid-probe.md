# PF-03 — DataForSEO Keyword Overview bounded paid probe

**Status:** ready
**Parent spec:** docs/specs/capture-event-v2.md, “Paid Keyword Overview probe adapter”
**Authority:** D8, D9, D10; HAM-01 closure
**Kind:** bounded paid-provider implementation
**Blocked by:** none for implementation/review; live operator call blocked by F6
**Approved by:** Project Steward
**Start commit:** the clean authority commit named in the Steward handoff

## Why this ticket exists

PF-02 proved one authenticated free sandbox exchange and HAM-01 proved the relevant
process-death boundaries. The sandbox response is dummy data. This ticket implements the
smallest paid request that can preserve real keyword metrics for later inspection while
keeping spend, request shape, and transport count closed.

DataForSEO remains the only current provider. Do not add Ahrefs, Semrush, a provider
catalog, or a generic HTTP runner.

## Exact adapter

Implement only
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`:

- one POST to
  `https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live`;
- exactly one task and one exchange;
- one to five ordered, unique keywords;
- fixed `location_code=2840`, `language_code=en`;
- fixed `include_serp_info=false` and `include_clickstream_data=false`;
- exact JCS singleton task-array body;
- no redirect, retry, poll, second request, price/account preflight, or endpoint override;
- exact paid policy and 20,000 micro-USD acknowledgement from the normative spec.

Use the existing credential environment names and memory-only credential object. The
public entrypoint accepts no credentials, URL, host, path, headers, arbitrary JSON,
location, language, enrichments, timeout, retry, or alternate ceiling.

## CLI and one-shot guard

Provide a service-owned capture mode equivalent to:

    uv run python -m observatory.dataforseo_paid_probe capture \
      --evidence-root PATH \
      --keyword "seo api" \
      --keyword "keyword research" \
      --authorize-max-micro-usd 20000

The authorization value must be exactly integer `20000`; missing, malformed, smaller,
or larger values fail before Attempt creation. Credential presence alone is not paid-call
authorization.

Before Attempt creation, inspect the store and fail if it already has a committed Attempt
for this paid adapter. Valid fixture and sandbox events may coexist. This prevents a
second sequential paid call in the same root. Do not claim it prevents simultaneous
processes; F7 remains deferred.

Capture success prints only `attempt_id` and `capture_id`. It never prints the response,
credentials, request exceptions, provider messages, price claims, or a success
classification.

Provide a separate read-only inspection mode equivalent to:

    uv run python -m observatory.dataforseo_paid_probe inspect \
      --evidence-root PATH \
      --capture-id 64_HEX

It performs no network and no mutation. It must require full D5 read-back of a complete
Capture for this exact adapter and emit the exact stored response-body bytes to stdout,
unchanged and with no added newline. It rejects partial/no-response, zero/absent body,
wrong adapter/version, invalid/tampered Evidence, and extra arguments. Diagnostics are
fixed and go to stderr. It is an operator inspection surface, not Derivation, an API,
Outcome, Observation, or second authority.

## Closed event construction

Extend event-version-2 validation by exact adapter-contract dispatch. Schema/version
dispatch remains the existing two-field peek; after it selects v2, the v2 validator must
select one of the two recognized closed adapters and then revalidate schema, version,
provider, adapter, request, parameters, policy, and every cross-field rule. Unknown or
confused combinations fail closed.

Do not change event-v1 or the existing sandbox contract, vectors, constructors, or IDs.
Use adapter-specific paid constructors/validators with names that do not silently change
the sandbox functions' meaning.

Keyword rules are exactly normative: array length 1..5, order preserved, no duplicates,
and each keyword matches the spec's printable-ASCII/length/boundary rule. Request-body
bytes equal JCS of one task formed by removing only `contract` from parameters.

## Structural send gate

Use a paid-adapter-specific caller-unconstructible one-use capability. It must require the
exact concrete `EvidenceStore` and this order:

1. validate authorization, one-shot store state, closed parameters, and exact body;
2. construct the credential-free paid HTTP-v2 Attempt;
3. commit Attempt plus exact request body;
4. read back and fully verify document identity, body bytes, adapter, paid policy, target,
   task count, enrichments off, and authorization ceiling;
5. only then issue the capability and inject Basic Authorization;
6. perform exactly one exchange;
7. commit at most one Capture and require full read-back.

The send primitive accepts only its own issued capability and frozen bytes. It must not
accept arbitrary mappings or public client/endpoint arguments. For deterministic tests,
an internal seam may accept only
`http://127.0.0.1:<1..65535>/v3/dataforseo_labs/google/keyword_overview/live`,
checked before Attempt and again immediately before exchange. It is unreachable from the
public capture mode.

Use the same exact sent-header equation, `trust_env=False`, TLS verification, HTTP/2
setting, redirects-disabled behavior, timeouts, raw streaming, 8 MiB limit,
`http-headers-v1` omission policy, timestamp rules, transport-failure table, and
credential-echo fail-closed rule as PF-02. Share code only when the resulting adapter
checks remain explicit and closed; do not introduce a generic provider transport API.

Completed 3xx/4xx/5xx is still complete HTTP testimony. Provider status is not transport
status. If the response echoes login, password, full Basic value, or bare token in its
retained body/header testimony, fail closed and commit no Capture.

## Paid-call prohibition during implementation

Implementation, ordinary tests, focused tests, formal review, and the implementer's report
must make zero DataForSEO/public-network calls and spend zero credit. Use only
`httpx.MockTransport` and a real `127.0.0.1` loopback server. An autouse network guard
must fail any non-loopback connection.

The implementer must not run the public CLI with real credentials. A live operator
command is not part of this implementation ticket's execution authority. F6 must close
first; afterward the Steward will recheck current official pricing and issue one exact
command to [CHAZ].

## Required automated proof

At minimum:

- independent test literals reproduce the paid vector's five byte lengths/digests/IDs;
- existing event-v1 and sandbox HTTP-v2 bytes/IDs remain unchanged;
- valid mixed stores containing fixture, sandbox, and paid event-v2 Evidence verify and
  scrub clean;
- fixture derive writes exactly its prior rows and skips both valid provider adapters with
  zero provider rows and no integrity failure;
- paid parameter boundaries, duplicates, keyword character/length rules, fixed booleans,
  fixed location/language, exact policy, and exact task bytes are closed;
- sandbox/paid adapter, host, path, policy, parameter, and body-confusion cases fail;
- missing/wrong authorization acknowledgement fails before Attempt, handler, or credential
  injection;
- a store with one committed paid Attempt refuses another before handler/send, including
  when the first Attempt has no Capture;
- forged/subclass/failed-commit/failed-readback/tampered-capability cases cannot send;
- loopback proves one request, exact on-wire body/content-length/header equation, no
  redirect, no retry, and a verified committed Attempt at request time;
- complete, partial, no-response, status classes, 8 MiB boundary, duplicate/denylisted
  headers, and credential echo retain PF-02 semantics;
- each branch commits at most one verified Capture and scrub is clean;
- read-only inspect emits exact verified bytes and performs zero writes/network;
- inspect rejects wrong adapter, partial/no-response/zero/absent body, unknown version,
  invalid ID, and tampered Evidence without emitting body bytes;
- credentials and Basic forms are absent from Evidence and terminal/exception surfaces;
- public CLI has no endpoint/client/header/credential/enrichment/location/language/retry
  arguments.

Tests should reuse existing PF-02 coverage where truthful, but acceptance cannot rest on
untested assumptions that the sandbox constants also protect the paid adapter.

## Scope constraints

One implementation commit; do not amend or push. The implementer may change only:

- `src/observatory/capture_event.py`;
- new `src/observatory/dataforseo_paid_probe.py`;
- `src/observatory/dataforseo_sandbox.py` only for the smallest explicitly reported
  shared-helper extraction that keeps both adapter gates closed;
- new `tests/test_dataforseo_paid_probe.py`;
- existing `tests/test_http_event_v2.py` only for mixed-adapter/vector regressions;
- this ticket's Status and Implementation report only.

No dependency changes are expected. Do not change Evidence Store format/layout,
`evidence_store.py`, fixture capture/derive/API code, settings or credential environment
names, PostgreSQL schema, another ticket, or authority documents.

If an unlisted production path is genuinely necessary, stop and report the exact
authority/technical conflict instead of editing it.

## Out of scope

- real provider/sandbox/DNS/TLS call by the implementer or automated suite;
- live paid operator smoke before F6 closure;
- DataForSEO User Data, balance, pricing, catalog, Suggestions, Related Keywords, SERP,
  Google Ads Search Volume, Standard/asynchronous, task-post/task-get, or bulk runners;
- provider envelope normalization, schema catalog, Outcome, Observation, Derivation,
  PostgreSQL, or HTTP API;
- response-dependent follow-up, retry, replay, scheduling, batching beyond five keywords;
- Ahrefs, Semrush, generic provider interfaces, or strategy-layer work;
- F6 off-host implementation, F7 concurrency, power-loss/device-cache claims.

## Verification and report

Run:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy`

Set Status to `review`, never `done`. Report:

- loaded skill paths;
- exact parent/child SHAs and changed paths;
- acceptance criterion to proving-test map;
- independently recomputed paid and unchanged sandbox/vector bytes and IDs;
- exact structural gate and one-shot-store mechanism;
- mock/loopback request counts and sent-header/body evidence;
- mixed-store scrub and exact PostgreSQL row accounting;
- inspect-mode byte equality and zero-write/network proof;
- credential non-disclosure evidence;
- full command results;
- weakest/most-fragile area, exact unproven limits, and authority disagreements;
- explicit zero-provider-call/zero-credit confirmation.

Only the Project Steward may close PF-03 after review and the later authorized operator
sequence.

## Implementation report

<!-- Implementer fills. Status may become review; never done. -->
