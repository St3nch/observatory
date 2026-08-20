# AI-02 — Search Mentions Live bounded paid-probe adapter

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** mandatory pre-implementation technical review and Steward reconciliation  
**Approved by:** Project Steward  
**Start commit:** set by [GROK] from the reconciled ticket HEAD  

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
9. Provide a read-only inspect operation that verifies the target Capture and returns or
   summarizes the exact complete nonempty response bytes without parsing provider semantics
   or mutating Evidence.
10. Permit an exact `http://127.0.0.1:<port>` path override only through the private test
    seam. Reject every other override shape.
11. Keep all ordinary tests local and credential-free. They must not perform DNS, provider
    network, paid-gate, or external HTTP activity.
12. Update this ticket to `review` in the one implementation commit and provide the
    required report.

## Acceptance behavior

- Exact deterministic request parameters and body bytes are proved.
- Attempt is durably committed and verified before the test server observes a request.
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
- Inspect refuses wrong adapter, damaged Evidence, partial/no-response Capture, missing or
  zero-byte body, and malformed Capture ID; successful inspect is byte-exact and read-only.
- Existing fixture, Keyword Overview, Google Organic, selection, Derivation, migration, and
  API behavior remains unchanged.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` exit 0.

## Required adversarial tests

At minimum, prove:

- exact singleton task and JCS bytes;
- every frozen-field rejection class above;
- exact authorization ceiling and Python type handling;
- concrete-store requirement and read-back identity/body verification;
- Attempt-before-request ordering;
- one-shot behavior for complete, partial, no-response, and unresolved paths;
- capability construction, mutation, copying, replay, and cross-adapter misuse resistance;
- strict production URL and exact loopback override;
- no redirects, environment proxy use, retry, continuation, or second request;
- credential absence from committed Attempt/Capture and response headers;
- credential-echo rejection;
- 120-second read timeout configuration and 32 MiB bound;
- complete, partial-prefix, zero-byte, over-limit, timeout, and unsupported-protocol paths;
- byte-exact verify-on-read inspection and no mutation;
- existing adapter identities and frozen fixture bytes remain unchanged.

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

GROK must return exactly one verdict:

- `PROCEED UNCHANGED`;
- `AMEND TICKET`;
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
