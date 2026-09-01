# RANK-02 — DataForSEO Google Ranked Keywords Live paid-probe adapter

**Status:** provisional review — awaiting independent [GROK] read-only pre-implementation review  
**Owner:** [GPT] Steward reconciliation; implementation Writer not yet designated  
**Blocked by:** none; RANK-01 closed at `d10349bb036905daf9dd53eeac0cffbe2c1e7118`  
**Draft base:** `d10349bb036905daf9dd53eeac0cffbe2c1e7118`  
**Product direction:** implement the bounded Evidence-only Ranked Keywords transport/inspect adapter; no provider call is authorized  

## Purpose

Implement one closed DataForSEO Labs Google Ranked Keywords Live adapter that can later perform
exactly one explicitly authorized provider exchange under the accepted HTTP-v2 Evidence
boundary. The adapter commits and verifies an Attempt before any send-capable path, performs at
most one bounded exchange, commits at most one Capture, and exposes a byte-exact read-only
inspect operation.

This ticket performs **no real provider call**. It creates no live Evidence, parser,
Conformance fixture, Derivation Recipe, Observation, schema/migration, PostgreSQL row, consumer
API, Measurement Outcomes/Holdings surface, Strategy behavior, ranking recommendation, panel,
cadence, or recurring acquisition.

The analytical purpose inherited from RANK-01 is domain-ranking testimony: preserve what
DataForSEO reports about which queries a domain ranks or previously ranked for, which exact
ranked SERP element/page is attached, provider rank/movement/loss testimony, target-level
ranking distributions/traffic estimates, and rich keyword measurements without collapsing
those facts into Observatory conclusions.

## Authority and Product locks

This ticket follows VISION, VOCABULARY, D2, D3, D8–D13, the DataForSEO surface roadmap, PF-09,
the hardened PF-16/PF-17 and newer provider-probe transport patterns, and closed RANK-01.

RANK-01 Product resolution fixes the first later live-capture candidate as exact domain:

    theconspiratory.com

and accepts preservation of the exact Ranked Keywords provider response body as immutable
Evidence even when that body contains SERP titles, descriptions/snippets, XPath, or AI Overview
reference text. That retention choice does not authorize API exposure or semantic promotion of
those text fields.

The first later live candidate is **not** a provider-call authorization and is not frozen as a
hard-coded production constant by RANK-02. The adapter accepts one operator-supplied target only
under the conservative closed domain grammar below. A later Evidence-activation ticket must
freeze the exact live target again and separately authorize credentials, spend, transport, and
Evidence creation.

## Claimed provider contract — rechecked 2026-09-01

Official provider authority used for this draft:

- `https://docs.dataforseo.com/v3/dataforseo_labs-google-ranked_keywords-live/`
- `https://dataforseo.com/pricing/dataforseo-labs/dataforseo-google-api`

These pages are claimed contract only, not Evidence or Observatory interpretation authority.
Current documentation claims:

- one Live `POST /v3/dataforseo_labs/google/ranked_keywords/live` request with exactly one task;
- `target` may represent domain, subdomain, or webpage, with materially different syntax;
- omitting location/language requests all available locations/languages;
- `ignore_synonyms=false` by default;
- documented `item_types` are `organic`, `paid`, `featured_snippet`, `local_pack`, and
  `ai_overview_reference`; if non-organic types are requested, array order affects returned
  ordering;
- `include_clickstream_data=false` by default and enabling it doubles request price;
- `limit` default 100, maximum 1000; `offset` default 0;
- `load_rank_absolute=true` adds result-level `metrics_absolute`;
- `historical_serp_mode` supports `live`, `lost`, and `all`;
- default ordering is `ranked_serp_element.serp_item.rank_group,asc`;
- data is described as updated weekly, while nested structures expose independent provider
  update times;
- the response contains result context/aggregate metrics and item-level `keyword_data` plus
  `ranked_serp_element` testimony.

Current pricing describes Ranked Keywords under Labs Google “all other endpoints”: `$0.012`
per Live task plus `$0.00012` per returned item, with a 2x multiplier when clickstream is
enabled. At this contract's `limit=100` and clickstream disabled, the published arithmetic is
approximately `$0.024`; pricing must be freshly rechecked before any later live authorization.

Documentation contains known suspicious/contradictory prose around some nested fields. RANK-02
must preserve raw bytes and must not encode response semantics. Parser/Recipe work begins only
after real Evidence is inspected.

## Exact adapter contract

Adapter identity:

    dataforseo-labs-google-ranked-keywords-live-paid-probe-v1

Production exchange:

- method: `POST`;
- scheme/host: `https://api.dataforseo.com`;
- path: `/v3/dataforseo_labs/google/ranked_keywords/live`;
- query: none;
- exactly one task in canonical JCS UTF-8 JSON array bytes;
- timeout: `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`;
- adapter-owned response-body ceiling: `33_554_432` bytes (32 MiB);
- redirects, environment proxies, HTTP/2, retry, polling, continuation, offset follow-up,
  response-derived follow-up, and automatic second requests: disabled;
- maximum exchanges under one invocation and one fresh Evidence root: one;
- exact authorization acknowledgement: `50000` micro-USD.

The exact provider task is:

```json
{
  "target": "<one operator-supplied closed domain>",
  "location_code": 2840,
  "language_code": "en",
  "ignore_synonyms": false,
  "item_types": [
    "organic",
    "paid",
    "featured_snippet",
    "local_pack",
    "ai_overview_reference"
  ],
  "include_clickstream_data": false,
  "limit": 100,
  "offset": 0,
  "load_rank_absolute": true,
  "historical_serp_mode": "all",
  "order_by": ["ranked_serp_element.serp_item.rank_group,asc"]
}
```

`filters`, `tag`, location/language names, and all other task keys are absent, not sent as
null/empty placeholders. `contract` is Evidence context in committed Attempt parameters and is
not sent to DataForSEO.

The validator requires the exact key set and fixed values above. It rejects alternate locale,
item-type membership/order, clickstream, limit/offset, absolute-rank setting, historical mode,
sorting, filters, tag, unknown keys, booleans where exact integers are required, multiple
tasks, alternate paths, or continuation/follow-up forms.

### Conservative first-adapter target grammar

RANK-01 established that provider domain/subdomain/page syntax is semantically dangerous. This
first adapter therefore accepts only a deliberately narrow Observatory-chosen two-label ASCII
domain form suitable for the selected first candidate; it is **not** a claimed provider limit
or a general registrable-domain parser.

Provisional grammar for Grok review:

- lowercase ASCII only;
- exactly two DNS-style labels separated by one dot;
- each label 1..63 characters;
- total length at most 253 characters;
- labels begin/end with `a-z` or `0-9`;
- internal label characters limited to `a-z`, `0-9`, and `-`;
- TLD label must begin with `a-z` and contain only `a-z`/`0-9`/`-` under the same DNS bounds;
- reject a leading `www.` form, scheme, slash/path, port, query, fragment, credentials,
  whitespace, Unicode/IDNA input, uppercase, trailing dot, empty labels, underscore, or more
  than one dot.

This intentionally accepts `theconspiratory.com` and intentionally excludes subdomains,
webpage URLs, multi-label public suffix forms such as `example.co.uk`, and internationalized
domains. If future Product work needs those subjects, it gets a separately reviewed contract
instead of silently broadening this first paid-probe grammar.

## Cost and policy boundary

Proposed closed Evidence policy:

```json
{
  "max_authorized_cost_micro_usd": 50000,
  "mode": "paid_probe",
  "policy_version": "dataforseo-labs-google-ranked-keywords-live-paid-probe-v1",
  "pricing_basis": "dataforseo-labs-google-ranked-keywords-live-2026-09-01"
}
```

The exact Python `int` `50000` is a fail-closed operator acknowledgement with headroom over the
current published approximately `$0.024` maximum for 100 returned items. It is not expected
cost, invoice truth, standing spend authorization, permission to retry, or a provider-enforced
cap. RANK-02 authorizes **zero spend and zero provider transport**.

## Required implementation

1. Add one explicit Ranked Keywords HTTP-v2 adapter branch without changing existing adapter
   tokens, published request vectors, identities, or semantics.
2. Add one Ranked Keywords-local paid-probe module with public `capture` and `inspect`
   operations following current provider-probe CLI conventions.
3. Reuse PF-09 `perform_bounded_http_exchange`; do not introduce a generic provider runner or
   generic transport-capability framework.
4. Build the gate hardened from birth with Ranked-local closure-owned issuance/consumption
   authority binding capability identity, concrete `EvidenceStore`, committed `attempt_id`,
   canonical committed Attempt preimage/document, exact committed request bytes, and consumed
   state. Caller-visible capability fields are mirrors only.
5. Preserve accepted ordering: validate credential availability and exact endpoint before
   closure-owned consumption; after those validations, consume before visible-field
   comparison, committed-Evidence revalidation, Authorization construction, or send.
6. Immediately pre-send, reread the exact committed Attempt by closure identity, verify event
   identity/commit marker/body identity/body size, validate the Ranked-specific closed
   parameters, recompute exact JCS request bytes, and require equality across recomputed,
   committed, and closure-owned bytes.
7. Send only closure-owned bytes through PF-09 with the fixed timeout, response ceiling,
   credentials boundary, production path, and test client seam.
8. Require exact Python `int` `50000`. Missing, lower, higher, boolean, float, string, Decimal,
   null, or other values fail before Attempt creation/send.
9. Commit and read back the Attempt/request body before any send-capable capability exists.
10. Refuse a second committed Attempt for this adapter token in the same Evidence root,
    including when the first is unresolved, complete, partial, over-limit, credential-echo,
    or no-response. Neighbor adapter Evidence may coexist.
11. Inject credentials only after request/store/authorization gates pass. Credentials must
    never enter Attempt/Capture Evidence, logs, URLs, status text, or retained response/header
    testimony. Credential echo must fail before Capture commit and still consume the one-shot.
12. Commit at most one verified Capture preserving PF-09 complete/partial/no-response
    transport testimony. Capture parentage and returned `attempt_id` remain closure-owned and
    cannot be redirected by post-exchange mutation of visible capability mirrors.
13. `inspect` is read-only, accepts only this adapter's verified complete Capture, and writes
    exact response-body bytes to stdout or the established bounded destination seam without
    normalization/parsing/provider access.
14. Keep first implementation Evidence-only. Do not add parser, fixture, Recipe, Derivation,
    schema, PostgreSQL, selection, API, Outcomes/Holdings, Ranked strategy, or recurring work.

## Required proofs

All ordinary tests are zero-provider-network with sentinel credentials and mock/loopback
transport only. At minimum prove:

- exact task/JCS request vector, request fingerprint/Attempt parameter contract, fixed path,
  headers, timeout and 32 MiB ceiling;
- strict target grammar acceptance for `theconspiratory.com` and representative valid
  synthetic two-label domains, plus rejection of schemes, `www.`, paths, subdomains,
  uppercase, Unicode, ports, query/fragment, whitespace, trailing dot, malformed labels,
  multi-label suffix examples, and unknown forms;
- all fixed request fields and exact `item_types` ordering are immutable and fail closed on
  omission/addition/change;
- exact `50000` authorization typing/value and failure before Attempt creation;
- Attempt-before-send and committed request-body equality;
- closure-owned refusal of request-body replacement, document replacement, attempt-id
  replacement, consumed-flag reset/replay, forged/unissued capability, and committed Attempt /
  request-body tamper immediately before send, with zero handler calls on refusal;
- one-adapter-Attempt-per-root behavior across unresolved/complete/partial/no-response/
  over-limit/credential-echo first attempts and coexistence with neighbor adapter Evidence;
- credentials injected only for transport and absent from preserved Evidence/error text;
- complete, partial, no-response, response-over-limit, transport exception, and header/body
  secret-echo behavior through the existing Evidence contract;
- byte-exact `inspect` for the correct complete Capture and refusal of wrong adapter,
  partial/no-response, tampered event/body, or uncommitted material;
- no redirects, proxies, HTTP/2, retries, polling, continuation, offset follow-up, or hidden
  provider preflight calls;
- existing adapter validators/vectors remain unchanged.

Tests must not assert response semantic shapes, provider counts, pricing as provider truth,
or the presence of live/lost/non-organic/AIO rows before real Evidence exists.

## Changed-path allowlist

Provisional exact implementation paths:

- `src/observatory/capture_event.py`;
- `src/observatory/dataforseo_google_ranked_keywords_paid_probe.py` (new);
- `tests/test_dataforseo_google_ranked_keywords_paid_probe.py` (new);
- `tickets/RANK-02-dataforseo-google-ranked-keywords-live-paid-probe.md`.

No other source, test, decision, roadmap, migration, fixture, or API file is authorized. If the
Writer proves another path is technically necessary, stop and return `RECONCILE`; do not widen
scope silently.

## Writer verification

The eventual designated Writer must run and report:

- the new Ranked Keywords paid-probe test module;
- relevant capture-event / PF-09 regression tests affected by the new adapter branch;
- `uv run ruff check .`;
- targeted mypy for changed source/test files;
- full configured mypy compared against the inherited baseline, without repairing unrelated
  baseline errors;
- no full repository pytest unless [CHAZ]/Steward later assigns that closure gate.

No test may contact DataForSEO or another public host.

## Mandatory implementation report

The Writer must candidly report:

- exact commit/parent and changed paths;
- test/lint/typecheck evidence;
- strongest and weakest implementation points;
- possible false greens and untested private-seam mutation cases;
- any caller influence that remains over transport/Capture parentage;
- architecture drift/coupling and what was deliberately kept Ranked-local;
- provider-contract assumptions that remain unproven without real Evidence;
- whether the provisional two-label domain grammar is stronger than provider authority and
  what later subjects it excludes;
- deferred work and why it stays deferred;
- explicit confirmation of zero provider call, credentials use against DataForSEO, spend,
  live Evidence, parser/Recipe/schema/API work, amend, and push.

The implementation ends in one commit with ticket status `review`; never mark it closed/done.

## Hard boundaries

- This ticket authorizes implementation only after the provisional ticket passes independent
  review, Steward reconciliation, final ticket acceptance, exact start commit, and explicit
  Writer designation by [CHAZ].
- No DataForSEO API request of any kind during implementation, including Sandbox, account,
  Status, Locations/Languages, pricing API, or Ranked Keywords.
- No real credentials may be used for provider transport. Tests use sentinels only.
- No live Evidence root or protected existing Evidence is read or mutated for implementation.
- No provider spend.
- No parser, Conformance fixture, Recipe, Derivation, schema/migration, PostgreSQL, selection,
  API, Outcomes/Holdings, Strategy, scoring, recommendation, recurring acquisition, or F12.
- No amend or push.

## Independent pre-implementation review questions

Before acceptance, [GROK] must inspect actual authority/code/tests and challenge at least:

1. whether the exact four-path allowlist is sufficient and minimal;
2. whether a new Ranked-local gate can be implemented without reusing an F13-affected private
   gate or introducing generic capability machinery;
3. whether the provisional two-label ASCII target grammar is technically honest, too narrow,
   too broad, or falsely described as registrable-domain validation;
4. whether exact `item_types` ordering, `historical_serp_mode=all`, `load_rank_absolute=true`,
   clickstream off, limit 100, offset 0, and explicit sort are correctly frozen as request
   testimony rather than parser semantics;
5. whether the 32 MiB ceiling, 120-second read timeout, one-Attempt-per-adapter-root rule, and
   exact 50,000 micro-USD acknowledgement match current transport precedent without importing
   unrelated assumptions;
6. whether post-exchange capability mutation can still redirect Capture parentage or returned
   identity under the proposed closure-owned design;
7. likely false-green tests, missing adversaries, or contract claims that should wait for real
   Evidence;
8. any Product question that genuinely remains before implementation rather than live
   activation.

Return `RECOMMENDATION: READY | RECONCILE | STOP`. Do not implement or mutate anything during
the review.
