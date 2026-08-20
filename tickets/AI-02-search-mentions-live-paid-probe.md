# AI-02 — Search Mentions Live bounded paid-probe adapter

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; mandatory technical review reconciled at the ticket start gate  
**Approved by:** Project Steward  
**Start commit:** `3cf3f4ad9e5b5779c0f24221aedca73fc285708a`  

## Purpose

Implement one Evidence-only, one-exchange adapter for the first accepted AI Optimization
contract. The adapter prepares and records one exact Search Mentions Live request, commits
Attempt before transport, commits at most one Capture after transport, and exposes a
verify-on-read operator inspection seam.

This ticket builds the guarded instrument. It does not authorize using it against the
provider, does not freeze real response bytes, and does not interpret Search Mentions into
Outcomes or Observations.

## Authority and accepted review

- D8 — Attempt precedes transport; Capture is transport testimony; exact bodies live in the
  Evidence Store.
- D9/D10 — one guarded HTTP exchange, explicit spend ceiling, credential-safe Evidence,
  one-shot store, local test override, and no live calls from ordinary tests.
- D12 — claimed contract, bounded real Evidence, and a later Derivation Recipe are distinct.
- D13 — one individually authorized adapter does not fire routine broad rollout.
- AI-01 — Search Mentions Live is accepted as the first AI Optimization foundation; Target
  Metrics and every other AI surface remain separate.

Official claimed contract:
<https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/search_mentions/live/>

## Exact adapter contract

Adapter identity:

`dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`

Production exchange:

- method: `POST`
- scheme/host: `https://api.dataforseo.com`
- path: `/v3/ai_optimization/llm_mentions/search_mentions/live`
- query: empty
- request body: canonical JCS UTF-8 JSON containing exactly one task
- content type: JSON using the accepted HTTP header policy
- response-body ceiling: 33,554,432 bytes
- timeout: connect 30 s, read 120 s, write 30 s, pool 30 s
- redirects, environment proxies, HTTP/2, retries, and automatic follow-ups: disabled
- authorization ceiling recorded and required by the CLI: exactly 200,000 micro-USD
- maximum exchanges under one invocation and one fresh Evidence root: one

The exact task is:

```json
{
  "target": [
    {
      "keyword": "<one operator-supplied keyword>",
      "search_filter": "include",
      "search_scope": ["answer"],
      "match_type": "word_match"
    }
  ],
  "location_code": 2840,
  "language_code": "en",
  "platform": "google",
  "offset": 0,
  "limit": 5
}
```

The HTTP body is a singleton array containing that task. The adapter contract identifier is
recorded in Evidence parameters but is not sent in the provider body.

The validator must require exactly those task keys and values. It must reject unknown keys,
bools where integers are required, omitted or extra target entries, a domain target,
`search_filter` other than `include`, any search scope other than exactly `["answer"]`,
a match type other than `word_match`, omitted or non-Google platform, any location or
language other than 2840/`en`, nonzero offset, any limit other than 5, filters, ordering,
`search_after_token`, `tag`, and any continuation or multi-platform form.

The provider documentation contains examples with a typographical space in `"match_type "`;
the accepted request key is `match_type` as named by the field contract. The technical
review must verify this interpretation before implementation.

The closed Evidence `parameters` keys are exactly `contract`, `target`,
`location_code`, `language_code`, `platform`, `offset`, and `limit`. The sole target object
has exactly `keyword`, `search_filter`, `search_scope`, and `match_type`. Reject `domain`,
`include_subdomains`, a trailing-space key, and every other missing or extra parameter or
target key.

The operator keyword is 1..80 printable ASCII characters and at most 10 ASCII-space
separated words. It begins and ends with ASCII alphanumeric. Internal characters are
limited to `A-Z a-z 0-9 space & ' ( ) + , . / : -`. This adapter does not inherit the
Google Organic query-operator deny set.

The closed Evidence policy is exactly:

```json
{
  "max_authorized_cost_micro_usd": 200000,
  "mode": "paid_probe",
  "policy_version": "dataforseo-ai-optimization-search-mentions-live-paid-probe-v1",
  "pricing_basis": "dataforseo-llm-mentions-live-2026-08-20"
}
```

The first live-call candidate keyword is `generative engine optimization`. Naming it here
does not authorize transport, spend, credentials, or Evidence creation, and the adapter
remains a one-keyword operator entrypoint rather than embedding that phrase in product code.

## Required implementation

1. Add the adapter constants, closed parameter validation, Attempt/Capture builders, and
   Evidence validators to the existing HTTP-v2 capture-event boundary without changing any
   accepted adapter identity.
2. Add one dedicated module entrypoint:
   `python -m observatory.dataforseo_ai_optimization_search_mentions_paid_probe`.
3. Reuse `perform_bounded_http_exchange` and the accepted concrete-EvidenceStore transport
   capability pattern. Do not extract or invent a generic paid-provider framework.
4. Require exact explicit authorization of 200,000 micro-USD. Reject missing, lower, higher,
   boolean, float, string, and otherwise non-exact values before Attempt commit.
5. Commit and verify the Attempt and exact request body before transport becomes possible.
   The issued capability is internal, immutable, unforgeable through the public module
   surface, and usable once.
6. Refuse a second Attempt for this adapter in the same Evidence root, including after an
   unresolved first Attempt. No retry, continuation, or second exchange is automatic.
7. Use production credentials only after all store, request, authorization, and target gates
   pass. Prevent credential material from entering committed bodies or retained headers.
8. Commit at most one Capture preserving complete, partial, and no-response transport
   testimony exactly as the shared HTTP seam supplies it. Provider status codes or JSON
   status fields do not redefine transport completeness.
9. Provide a read-only inspect operation that verifies the target Capture and writes the
   exact complete nonempty response bytes to stdout. It must not parse, pretty-print,
   summarize, normalize, or mutate Evidence.
10. Permit an exact `http://127.0.0.1:<port>` path override only through the private test
    seam. Reject every other override shape.
11. Keep all ordinary tests local and credential-free. They must not perform DNS, provider
    network, paid-gate, or external HTTP activity.
12. Update this ticket to `review` in the one implementation commit and provide the
    required report.

## Acceptance behavior

- Exact deterministic request parameters and body bytes are proved.
- Attempt is durably committed and verified before the test server observes a request.
- The decisive ordering test reads the committed Attempt and exact request-body bytes from
  inside the first local request handler; a forced Attempt-commit failure proves the
  handler is never reached.
- A forged, copied, reconstructed, mutated, or reused capability cannot transport.
- Any pre-transport validation failure leaves no Attempt and performs no exchange.
- Process/test exceptions after Attempt commit preserve honest authorized/unresolved state
  and a second invocation refuses another Attempt in that root.
- Complete, partial, no-response, body-limit, timeout, protocol, and connection paths retain
  the accepted HTTP-v2 testimony without pretending semantic provider success.
- A complete response containing `search_after_token`, more available results, or
  `total_count > items_count` produces one Capture and no subsequent request.
- Response headers omit credential-bearing names under the shared header policy.
- Credential echo in returned body or retained header is rejected before Capture commit.
- Credential echo leaves the committed Attempt without a Capture. An over-limit response
  preserves its bounded prefix in a `response_partial` Capture. Both consume the adapter
  one-shot, and a second invocation in that root is refused.
- Inspect refuses wrong adapter, damaged Evidence, partial/no-response Capture, missing or
  zero-byte body, and malformed Capture ID; successful inspect is byte-exact and read-only.
- Existing fixture, Keyword Overview, Google Organic, selection, Derivation, migration, and
  API behavior remains unchanged.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` exit 0.

## Required adversarial tests

At minimum, prove:

- exact singleton task and JCS bytes;
- every frozen-field rejection class above;
- the closed top-level and target key sets, including domain, include-subdomains,
  trailing-space `match_type `, missing-key, and extra-key rejection;
- exact authorization ceiling and Python type handling;
- concrete-store requirement and read-back identity/body verification;
- Attempt-before-request ordering;
- one-shot behavior for complete, partial, no-response, and unresolved paths;
- capability construction, mutation, copying, replay, and cross-adapter misuse resistance;
- strict production URL and exact loopback override;
- no redirects, environment proxy use, retry, continuation, or second request;
- a complete response carrying a continuation token and
  `total_count > items_count` still causes exactly one POST and one Capture;
- credential absence from committed Attempt/Capture and response headers;
- credential-echo rejection;
- 120-second read timeout configuration and 32 MiB bound;
- complete, partial-prefix, zero-byte, over-limit, timeout, and unsupported-protocol paths;
- byte-exact verify-on-read inspection and no mutation;
- existing adapter identities and frozen fixture bytes remain unchanged;
- neighboring accepted adapters coexist in one Evidence root while one-shot enforcement
  remains adapter-specific.

Use the smallest decisive test substrate. Ordinary tests may use a local loopback server and
temporary Evidence Store. No provider host, credentials, DNS, or paid endpoint is permitted.

## Explicitly out of scope

- Any real provider call, account access, credentials, spend, or operator Evidence root.
- A sandbox adapter unless the technical review proves an official sandbox contract useful
  for this exact endpoint and the Steward separately amends the ticket.
- Freezing or committing a Search Mentions conformance fixture.
- JSON parsing beyond the existing generic operator inspection boundary.
- Provider semantic reconciliation, Outcome classification, Observation identities,
  occurrence modeling, Derivation Recipe, PostgreSQL schema, selection, history, or API.
- ChatGPT, domain/source target searches, multiple targets, filters, ordering, pagination,
  continuation, historical/timeseries, Target Metrics, AI Keyword Data, LLM Responses, or
  any provider product named LLM Scraper.
- Shared AI abstractions, generic provider frameworks, acquisition orchestration, recurring
  capture, automated backup, or another acquisition surface.
- Changes to `AGENTS.md`, `VISION.md`, decisions, specs, or roadmaps.
- F3, F6, F7, F8, F9, F10, or F12 activation.
- Push.

## Mandatory pre-implementation technical review

Before editing any file, GROK must load the project-local research, codebase-design, and
code-review skills; re-read authority, AI-01, this ticket, the three accepted HTTP adapters,
`capture_event.py`, `http_single_exchange.py`, Evidence Store commit/verify behavior,
credential handling, and the relevant tests.

The review must verify:

- the exact official request field names and whether the provider's contradictory examples
  change the accepted task;
- whether the chosen request is one honest contract and can produce materially useful Google
  AIO indexed-mention testimony;
- whether 32 MiB and the timeout shape are defensible for `limit=5`;
- every capture-event branch that must recognize the new adapter;
- the smallest reuse boundary that avoids both copy-paste omissions and an unauthorized
  generic refactor;
- how to prove no continuation or accidental second exchange;
- how an unresolved Attempt, response limit, credential echo, and wrong-adapter capability
  behave;
- likely parser/cardinality/identity traps exposed for a later ticket without designing that
  parser now;
- false-green risks, weak tests, hidden coupling, and any premise requiring authority change.

GROK returned `AMEND TICKET`. The Steward reconciled that review before implementation:

- the governing capture-event-v2 spec now explicitly accepts this fourth adapter branch;
- the parameter, target, keyword, policy, timeout, body-limit, credential, loopback,
  one-shot, and byte-exact inspection contracts are closed above;
- the Attempt-before-handler, commit-failure, unresolved, credential-echo, over-limit,
  continuation, and neighboring-adapter proofs are required;
- implementation remains explicit adapter dispatch, not a registry or generic framework;
- the paid-adapter module may reuse the Organic shape and shared HTTP/capability/Evidence
  mechanics but must not inherit the Organic operator deny set;
- this Evidence-only adapter must not enter Derivation or API provider dispatch;
- likely parser traps are report-only: paging-key contradiction, result/task count
  distinctions, returned question/answer versus requested keyword, source identity,
  Google-null ChatGPT fields, continuation non-identity, ordering, timestamps, and exact
  numeric cost normalization.

No authority decision was required. No implementation, provider activity, Evidence
creation, or full suite occurred during the review.

GROK must return exactly one verdict:

- `PROCEED UNCHANGED`;
- `AMEND TICKET` (returned and reconciled);
- `AUTHORITY DECISION REQUIRED`.

The review report must be candid: strongest and weakest seams, what genuinely generalizes,
what must remain surface-specific, expensive mistakes, untested assumptions, and concrete
improvements. No implementation, edit, commit, full suite, provider call, credentials,
Evidence creation, or push occurs during this review. Implementation begins only after
Steward reconciliation.

## Implementer report required

The one implementation commit must record exact parent/child, changed paths,
acceptance-to-test mapping, targeted and full command evidence, and loaded skill paths. It
must report:

- final exact request bytes and adapter identity;
- authorization, one-shot, capability, and credential gates;
- transport timeout/body-limit behavior;
- all capture-event dispatch/validation branches changed;
- evidence that continuation and second exchange cannot occur;
- strongest and weakest tests and remaining false-green risk;
- what the real payload is expected to teach a later parser;
- any finding that should change the live-call operator plan;
- confirmation that no provider/DNS/credential/paid-gate activity occurred;
- confirmation of no parser, fixture, recipe, schema, Derivation, API, other surface, or
  push.

Stop at `review` for Steward verification.

## Implementation report

**Parent:** `3cf3f4ad9e5b5779c0f24221aedca73fc285708a`
**Child:** this implementation commit
**Status:** `review`
**AI-02 only:** yes. Nothing pushed.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/capture_event.py` (fourth exact HTTP-v2 branch)
- `src/observatory/dataforseo_ai_optimization_search_mentions_paid_probe.py` (new)
- `tests/test_dataforseo_ai_optimization_search_mentions_paid_probe.py` (new)
- this ticket (Start commit, Status, Implementation report)

### Adapter token

`dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`

### Deterministic vector

Fixed inputs: keyword `observatory test`, nonce `6666…66`,
`authorized_at=2026-08-20T20:00:00.000000Z`,
`observatory_version=conformance-search-mentions-paid-probe-v1`.

| Artifact | Value |
|---|---|
| request body | `[{"language_code":"en","limit":5,"location_code":2840,"offset":0,"platform":"google","target":[{"keyword":"observatory test","match_type":"word_match","search_filter":"include","search_scope":["answer"]}]}]` |
| request SHA-256 | `f0299125e69fe6712cbea5e99ec4e23bbf2a71a357c356dcc96fed469e6494d4` |
| fingerprint | `63f64b7284f4d94214e02beb3710256d056614e03d60535fa57dca9ccc7db2bd` |
| Attempt ID | `5cf959940bec672f8f67bf1f7b5ad18aee2b86fd89e33dd00280f4092cf2741e` |
| sample complete Capture ID | `37966993c0075e5de8a3cab063d34e37b46e69d3c115c4a9b598c31c09306658` |

The operator live-call candidate `generative engine optimization` is accepted by the
closed keyword grammar and is not embedded in product code.

### Capture-event dispatch/validation branches changed

Explicit fourth branch, not a registry. Else still means sandbox.

- `_recognized_http_v2_adapter`
- fingerprint v2 request dispatch
- Attempt v2 request/parameters/policy/body-equation dispatch
- Capture v2 request dispatch
- new builders: `mentions_http_request`, `mentions_http_fingerprint_document`,
  `mentions_http_attempt_document`, `mentions_http_capture_document`
- new validators: `validate_mentions_http_parameters`, `validate_mentions_http_request`,
  plus closed target-object validation

Existing sandbox, Keyword Overview, and Google Organic validators and identities are
untouched.

### Gates

- Authorization: exact Python `int` `200000` before Attempt. Rejects missing, other ints,
  `True`, `200000.0`, and `"200000"`.
- Attempt-before-transport: first mock handler and the loopback accept thread both read
  the committed Attempt and exact `request.body` bytes before responding. Failed
  `commit_attempt` never reaches the handler.
- Capability: constructor refused; `object.__new__` forgery not in the issued list;
  `copy.copy` hits immutability; pickle restore is not issued; replay is one-exchange;
  sandbox/KO/Organic capabilities cannot call this `_exchange` and vice versa.
- One-shot: keyed by this adapter token. Fixture, sandbox, KO, and Organic Attempts in the
  same root do not block it. Unresolved, credential-echo, and over-limit paths refuse a
  second Attempt.
- Credentials: nonempty env may fail before Attempt. Authorization header is injected only
  after the issued capability. Echo in body or retained header blocks Capture commit.
- Timeout/body-limit: adapter-owned `httpx.Timeout(connect=30.0, read=120.0, write=30.0,
  pool=30.0)` and `33_554_432`. Shared HTTP module still has neither constant. Tests
  truncate with a 16-byte private override.
- Inspect: byte-exact stdout, verify-on-read, no parse/pretty-print/summary/mutation.
  Refuses wrong adapter, partial, no-response, bad IDs, and tampered bodies.

### Continuation

A complete JSON body with `search_after_token` and `total_count > items_count` still
produces exactly one POST and one Capture. The request bytes do not contain
`search_after_token`. The adapter never decodes JSON to decide a follow-up.

### Acceptance-to-test mapping

| Acceptance | Test |
|---|---|
| exact singleton JCS bytes | `test_closed_request_vector_and_attempt_identity` |
| frozen field/key-set rejections | `test_frozen_fields_are_rejected`, `test_missing_required_keys_are_rejected` |
| concrete-store requirement | `test_subclassed_store_cannot_issue` |
| keyword grammar; no Organic deny set | `test_keyword_grammar_rejects_invalid_forms`, `test_operator_keywords_are_not_denied` |
| exact authorization types | `test_authorization_required_before_attempt` |
| Attempt-before-handler | `test_attempt_is_committed_before_first_handler`, `test_loopback_server_sees_attempt_and_does_not_follow_redirect` |
| failed commit never transports | `test_failed_attempt_commit_never_reaches_handler` |
| capability forgery/copy/mutation/replay | `test_forged_copied_mutated_and_replayed_capability_cannot_transport` |
| cross-adapter isolation | `test_cross_adapter_capabilities_are_isolated` |
| one-shot + neighbors | `test_one_shot_is_adapter_specific_and_allows_neighbors`, `test_unresolved_attempt_blocks_second_invocation` |
| continuation still one POST | `test_continuation_token_response_is_still_one_exchange` |
| credential echo unresolved | `test_credential_echo_leaves_unresolved_one_shot`, `test_credential_echo_in_retained_header_is_refused` |
| over-limit one-shot | `test_over_limit_partial_consumes_one_shot` |
| complete/partial/zero/no-response | `test_mid_body_timeout_zero_byte_and_no_response` |
| inspect byte-exact | `test_inspect_emits_exact_bytes_without_mutation`, `test_inspect_rejects_wrong_adapter_partial_zero_and_tamper` (includes no-response and zero-byte) |
| existing identities | `test_existing_adapter_identities_unchanged` |
| derive/API isolation | `test_fixture_and_provider_derive_skip_search_mentions` |

### Checks

Targeted: `uv run pytest -q tests/test_dataforseo_ai_optimization_search_mentions_paid_probe.py` — 56 passed in 5.00s after spec-review test additions

`uv run pytest -q`: 965 passed, 1 skipped, 1 warning in 161.63s

`uv run ruff check .`: clean

`uv run mypy`: clean after one test annotation fix

Leftover `observatory-ce05-*` containers: none.

### Strongest / weakest tests and false-green risk

Strongest: Attempt identity and request bytes asserted *inside* the first mock handler and
inside the loopback accept thread; failed commit with handler spy; continuation call
count; credential-echo then one-shot; neighbor coexistence.

Weakest: unknown HTTP version / unsupported-protocol is proved in the shared exchange
module, not re-driven through this adapter with a forged `http_version`. Capability
`_used` can still be flipped with `object.__setattr__`, matching accepted Organic/KO
limits; tests prove the public-surface constructor, copy, pickle, and identity list.

Copying Organic paid-probe tests after-the-fact Attempt existence would have been
false-green; this ticket does not do that.

### What generalized / what stayed surface-specific

Generalized: HTTP-v2 envelope, `perform_bounded_http_exchange`, credential object,
capability/one-shot/inspect shape, header omission, loopback override grammar.

Surface-specific: nested `target` object, `platform=google`, `offset`/`limit`,
`search_scope=["answer"]`, `match_type` (no trailing-space key), policy/pricing_basis,
path `/v3/ai_optimization/llm_mentions/search_mentions/live`, keyword grammar without
Organic operator denial, 200000 micro-USD.

### Parser traps for a later Derivation ticket (not implemented)

Paging-key contradiction (`current_offset` vs example `offset`); `total_count` vs
`items_count` vs `result_count`; requested keyword vs returned `question`/`answer`;
Google `sources` vs Organic AIO `references`; ChatGPT-only fields expected null;
`search_after_token` is opaque continuation, not identity; default ordering because
`order_by` is forbidden; `first_response_at`/`last_response_at` vs Capture time vs
monthly periods; provider `cost` as JSON float.

### Live-call operator plan

No change required to sequencing: F6, fresh official price check, exact
`--authorize-max-micro-usd 200000`, and explicit [CHAZ] authorization still gate any
real POST. If credential-echo occurs, that root is consumed (unresolved); use a new
Evidence root. `limit=5` is learning, not completeness. Do not follow
`search_after_token`.

Over-limit retains a `response_partial` Capture (shared HTTP testimony, item 8) and
consumes one-shot. Credential-echo commits no Capture. Both refuse a second Attempt in
that root.

### Confirmations

- No provider host, DNS, real credentials, account access, paid gate, or external HTTP.
- Ordinary tests autouse-block non-loopback `socket.create_connection` and delete
  credential env vars.
- No parser, conformance fixture freeze, Recipe, schema, Derivation, selection, API,
  history, recurring acquisition, or second surface.
- No `AGENTS.md`, spec, decision, or vocabulary edits.
- Nothing pushed.

## Steward closure

**Reviewed implementation:** `69528a431bd865c35c3ae2a007d3bda9fc2b114e`  
**Implementation parent:** `3cf3f4ad9e5b5779c0f24221aedca73fc285708a`  
**Disposition:** accepted

The Steward independently reviewed the exact single-child diff and found no hard standards
or specification defect. The adapter remains an explicit fourth HTTP-v2 branch, preserves
the existing adapter identities, and remains Evidence-only. The governing HTTP-v2 contract
requires an over-limit prefix to survive as a `response_partial` Capture; the stale
acceptance sentence above was corrected at closure to match that authority and the accepted
implementation.

Independent static gates on the implementation child:

- `uv run ruff check .` — exit 0, all checks passed
- `uv run mypy` — exit 0, 50 source files clean

[CHAZ] independently ran the final full suite on the exact implementation child:

- UTC start: `2026-08-20T17:16:51Z`
- UTC end: `2026-08-20T17:19:25Z`
- `uv run pytest -q` — 967 passed, 1 skipped, 1 warning in 152.81 s; exit 0
- wall time: 153.22 s
- tree clean before and after
- no remaining `observatory-ce05-*` container

This final committed-child run supersedes the earlier 965-test implementation-report run.
No provider host, DNS, credentials, account access, paid gate, external HTTP, or Evidence
creation occurred during Steward review. No provider call is authorized by closure.
Nothing was pushed.
