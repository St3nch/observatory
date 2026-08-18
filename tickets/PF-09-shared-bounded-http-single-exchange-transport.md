# PF-09 — Shared bounded HTTP single-exchange transport substrate

**Status:** planned
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** provider foundation / zero-network refactor
**Blocked by:** Steward transition to `ready` after the current authority baseline is confirmed pushed
**Approved by:** Project Steward for planning only
**Start commit:** implementer fills when assigned

## What to build

Extract the provider-neutral mechanics that are already duplicated by the accepted
DataForSEO sandbox and Keyword Overview paid-probe transports into one internal bounded
single-exchange HTTP substrate, without widening either adapter contract or changing any
Evidence semantics.

This ticket exists to prevent each future one-exchange adapter from copying HTTP streaming,
header omission, failure mapping, response-body bounding, and result-shaping code. It is a
refactor of accepted behavior, not a generic provider runner and not authorization for a new
surface.

## Authority

- D8 — Attempt/Capture Evidence boundary and verify-on-read remain unchanged.
- D9 — HTTP event version 2, committed credential-free request, no redirect follow-up,
  secret-header omission, and one logical exchange remain authoritative.
- D10 — Keyword Overview paid-probe target, one-shot authorization/spend gate, and exact
  request contract remain unchanged.
- D12 — adapter contracts remain deliberate and provider-specific; shared mechanics do not
  create standing authorization for another adapter.
- D13 — broad useful coverage is product direction, but activation remains bounded.
- F3 remains unfired for routine broad rollout.
- F7 remains deferred; this ticket proves no multi-process writer safety.
- F9 remains deferred; no HTTP write API or generic capture endpoint is added.
- F12 remains deferred; no scheduler, cadence, subject-set policy, or orchestration is added.

## Required boundary

The shared module is an **internal library seam only**. It must not expose a CLI, API route,
caller-supplied provider endpoint, arbitrary request body, arbitrary headers, retry policy,
or generic "run this URL" capability.

Each adapter continues to own and validate, before transport:

- exact `provider` and `adapter_contract`;
- closed request parameters and exact request-body construction;
- exact production host/path/method/query and any loopback-only test override;
- credential type/injection policy;
- paid authorization/spend gate and one-shot rules where applicable;
- adapter-specific response-body byte bound;
- Attempt construction and read-back verification;
- one-use verified-Attempt capability issuance;
- Capture document construction, commit, and read-back verification;
- any provider-specific post-capture inspection behavior.

The shared substrate may own only mechanics that are semantically identical across the two
accepted HTTP-v2 adapters, including as appropriate:

- immutable exchange-result representation;
- production `httpx` client construction with `trust_env=False`, redirects disabled, and
  the accepted connection/timeout behavior;
- exact sent-header assembly after adapter authorization has supplied the credential value;
- HTTP-version validation;
- closed response-header normalization and secret-class omission policy;
- response body-state construction;
- HTTP exception → closed transport phase/code mapping;
- one bounded request/response streaming exchange;
- complete / partial / no-response exchange-result construction.

Do not move adapter authorization or target validation into a generic registry merely for
symmetry. The caller that reaches the shared exchange function must already be inside an
adapter-owned, verified, one-use transport path.

## Contract-scoped response bounds

The shared streaming mechanic must accept the response-body byte ceiling from the calling
adapter rather than owning one universal Observatory limit.

For the two accepted adapters in this ticket:

- sandbox remains exactly `8_388_608` bytes;
- Keyword Overview paid probe remains exactly `8_388_608` bytes;
- the value is adapter-owned/internal and is not a new CLI/API/user-controlled option;
- exceeding the bound preserves the existing HTTP-v2 `response_partial` testimony and
  existing closed `receive_body` failure semantics; this ticket does not invent a new
  Capture failure enum or event version.

Future adapters may choose a different bound only in their own separately authorized
contract/ticket.

## Evidence compatibility

This refactor must not change any accepted serialized Evidence contract.

- HTTP event version remains `2`.
- Existing request-fingerprint, Attempt, Capture, request-body, and response-body identity
  rules remain unchanged.
- Published sandbox and paid-probe conformance vectors/digests remain byte-for-byte stable.
- Existing header order, omission counts, HTTP status/version testimony, timestamps,
  `transport_state`, response `completeness`, and failure phase/code behavior remain
  logically identical for the same deterministic exchange.
- No migration or reinterpretation of historical Evidence is permitted.

## Structural isolation

The refactor must preserve the fact that a verified capability issued by one adapter cannot
be used by the other adapter's transport path.

At minimum:

- a sandbox capability cannot execute the paid adapter;
- a paid capability cannot execute the sandbox adapter;
- an unissued/fabricated capability cannot reach transport;
- a used capability cannot execute a second exchange;
- paid authorization remains checked before the paid Attempt is created/sent;
- sandbox remains `sandbox_no_spend` and cannot target production API host/path semantics;
- public CLIs retain their current argument surfaces and cannot supply arbitrary endpoints.

## Acceptance criteria

- [ ] Shared single-exchange HTTP mechanics live in one internal module instead of being
      duplicated in both adapter modules.
- [ ] Adapter-specific target, request, policy, credentials, authorization, spend, one-shot,
      Attempt, and Capture rules remain adapter-owned.
- [ ] Existing sandbox and paid-probe public entrypoints and CLI argument surfaces are
      logically unchanged.
- [ ] Existing HTTP-v2 sandbox conformance request/fingerprint/Attempt/Capture bytes and
      published IDs remain unchanged.
- [ ] Existing paid-probe request/fingerprint/Attempt/Capture conformance bytes/digests
      remain unchanged.
- [ ] Complete response behavior is unchanged for both adapters.
- [ ] Mid-body read failure remains `response_partial` with the accepted retained prefix.
- [ ] Response-body bound exceed remains `response_partial` with exactly the bounded prefix
      and the existing closed HTTP-v2 failure semantics.
- [ ] Pre-header connection/write/protocol/timeout failures retain their accepted
      `no_response` phase/code mapping.
- [ ] Secret-class response-header values remain absent from Evidence; retained header
      ordering/duplicates and omission counts remain unchanged.
- [ ] Sentinel credential material cannot enter Evidence, stdout/stderr, exception text, or
      committed headers/bodies through the shared seam.
- [ ] Sandbox and paid one-use capability isolation remains structurally tested.
- [ ] Existing adapters continue to use an adapter-owned 8 MiB bound; the shared module has
      no hard-coded global 8 MiB policy.
- [ ] No provider network, DNS, credentials, or spend occurs in ordinary tests/review.
- [ ] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are green.

## Required tests

- Existing `tests/test_dataforseo_sandbox.py` regressions remain green.
- Existing `tests/test_dataforseo_paid_probe.py` regressions remain green.
- Direct tests of the shared internal exchange mechanic cover at least:
  - complete non-empty response;
  - complete zero-byte response where the accepted event contract permits it;
  - response-header secret omission with duplicate/order preservation for retained fields;
  - timeout/protocol/read failure mapping before and after headers;
  - body-limit truncation at `limit + 1` and exact retained prefix;
  - supplied adapter-owned limit actually controls truncation (use a small deterministic
    test limit; do not allocate an 8 MiB fixture merely to prove parameterization);
  - redirects are not followed;
  - `trust_env=False`/ambient proxy behavior remains guarded by the production-client seam.
- Cross-adapter capability misuse / second-use rejection remains tested at the adapter gate.
- A conformance regression recomputes the published HTTP-v2 and paid-probe identities after
  the refactor rather than trusting constants alone.

## Out of scope

- A new provider or DataForSEO surface
- Firecrawl, OnPage, LLM Mentions, SERP, YouTube, backlinks, or another adapter
- Any real provider probe/call
- Generic adapter registration or dynamic provider plugins
- Caller-supplied arbitrary URL/body/header execution
- Retry, redirect follow-up, polling, pagination, continuation, task-get, or multi-exchange
  provenance
- Changing or extending HTTP-v2 `transport_failure` enums
- New Capture/Attempt event version
- Corpus/logical provider completeness modeling beyond existing transport completeness
- F7 locking, F8 auth/non-loopback API exposure, F9 HTTP writes, F10 projections
- F12 acquisition orchestration
- Strategy, recommendations, panels, cadence, or current-knowledge retrieval

## One implementation commit must prove

The two accepted HTTP-v2 adapters use one internal bounded single-exchange transport
mechanic without changing their serialized Evidence, authorization boundaries, public
entrypoints, or one-exchange guarantees, and future adapters are no longer forced to copy
the transport loop merely to obtain the same testimony discipline.

## Implementer report requirements

In addition to the normal implementation report, GROK must explicitly report:

- the exact shared-vs-adapter ownership split after the refactor;
- every deleted duplicated helper and where its accepted behavior now lives;
- proof that no generic endpoint/runner escaped into a public seam;
- proof that both 8 MiB bounds remain adapter-owned and behaviorally unchanged;
- conformance IDs/digests before/after;
- the weakest remaining duplication or coupling that he deliberately did **not** generalize;
- any reason the shared seam would make a third one-exchange adapter unsafe or awkward.

## Steward amendment after adversarial review

This amendment is normative for PF-09 and supersedes any earlier wording that implies a
universal transport or one Observatory-wide timeout policy.

- Reuse is limited to a later separately authorized adapter that fits the same accepted
  one-request/one-response HTTP-v2 mechanics. PF-09 does not create a universal provider
  transport.
- Each adapter owns its timeout profile in addition to its response-body byte ceiling.
  Sandbox and Keyword Overview keep their existing `httpx.Timeout(30.0)` behavior.
  The shared production-client mechanic accepts the adapter-owned timeout profile and does
  not hard-code one global timeout.
- The shared exchange seam receives only already-resolved transport inputs from an
  adapter-owned verified one-use path: exact resolved URL, exact request-body bytes, the
  adapter-supplied committed credential-free application-header list, an already-built
  Authorization value, the adapter-owned timeout profile, the adapter-owned response-body
  ceiling, and an optional injected client for deterministic tests.
- The shared module must not receive a provider credential object, import one global
  `HTTP_HEADERS` list as Observatory law, choose a provider target, expose a caller URL, or
  own Attempt/capability/Capture/spend/target validation.
- Cross-module capability isolation is explicit: a sandbox-issued capability cannot execute
  the paid exchange path and a paid-issued capability cannot execute the sandbox exchange
  path. Existing second-use rejection remains adapter-local.
- Direct shared-seam tests must prove adapter-supplied timeout and response-limit
  parameterization without changing existing conformance bytes/IDs.
- Do not add continuation hooks, async workflow state, retry policy, pagination, task-get,
  or another transport-failure enum in this refactor.

The intended implementation remains “finish the proven extraction”: shared exchange-result,
production-client mechanics, sent-header assembly from adapter-supplied application headers,
HTTP-version validation, secret-header omission, body-state construction, exception mapping,
and one bounded streaming exchange. Everything else stays adapter-owned.
