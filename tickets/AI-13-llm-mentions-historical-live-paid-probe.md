# AI-13 — LLM Mentions Historical Live paid-probe adapter

**Status:** accepted — implementation authorization pending  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** separate [CHAZ] implementation authorization at the final committed ticket  
**Approved by:** [CHAZ] for provisional ticket drafting / [GPT] Steward reconciliation  
**Pre-implementation review:** GROK RECONCILE, completed read-only at
`c735542ab19a56617498a52031eec5419f578423`  
**Review base:** `c735542ab19a56617498a52031eec5419f578423`  
**Start commit:** not assigned

## Purpose

Implement one closed, Evidence-only DataForSEO AI Optimization LLM Mentions Historical
Live paid-probe adapter. The adapter commits and verifies an HTTP-v2 Attempt before its
only send-capable path, performs at most one bounded exchange, commits at most one Capture,
and exposes a byte-exact read-only inspect command.

This ticket makes no provider call and creates no Historical parser, conformance fixture,
Derivation Recipe, Outcome, Observation, PostgreSQL schema, selection, or API. A later
activation ticket owns the one operator invocation and its bounded F6 protection proof.

Historical is selected because it may preserve provider-stated monthly mention and
AI-search-volume testimony that Target Metrics cannot reconstruct. It is not an
answer/citation archive and must remain distinct from Search Mentions, Target Metrics,
Timeseries, Top Mentioned, Keyword Overview, and any strategy-layer time series.

GROK reviewed the provisional ticket read-only at the exact review base and returned
RECONCILE. GPT independently verified and incorporated the accepted corrections below.
This final ticket is not implementation authority until CHAZ separately authorizes
implementation at its exact committed HEAD. No second GROK ticket review is required.

## Authority and accepted Product locks

This boundary follows VISION, VOCABULARY, D2, D3, D8, D9, D11–D14, PF-09, the completed
Search Mentions and Target Metrics slices, and the current provider roadmap. F5, routine
F6, F12, and F13 remain deferred except for their accepted bounded satisfactions.

[CHAZ] fixes the first Historical contract to:

- keyword: exact UTF-8 string `generative engine optimization`;
- provider window: `2025-08-01` through `2026-07-31`, inclusive as requested;
- platform: `google`;
- location: United States, `location_code=2840`;
- language: English, `language_code="en"`;
- one included keyword target with `search_scope=["answer"]` and
  `match_type="word_match"`.

These locks authorize ticket design only. They do not authorize implementation, credentials,
transport, spend, Evidence creation, a provider call, or later reuse.

## Claimed provider contract — reviewed 2026-08-25

Official endpoint:

<https://docs.dataforseo.com/v3/ai_optimization/llm_mentions/historical/live/>

Official family overview, pricing, and terms:

- <https://docs.dataforseo.com/v3/ai_optimization-llm_mentions-overview/>
- <https://dataforseo.com/pricing/ai-optimization/llm-mentions>
- <https://dataforseo.com/terms-of-service>

Current documentation claims:

- Live-only `POST /v3/ai_optimization/llm_mentions/historical/live`;
- exactly one task per call and execution time up to 120 seconds;
- no asynchronous task/poll or GET contract, and no response-side filtering, ordering,
  limit, offset, continuation, or token contract;
- `date_from` and `date_to` are optional in the provider API, but this adapter requires
  both explicitly;
- historical data floor `2025-08-01`;
- omitted `platform` may return both `google` and `chat_gpt`, while Historical month
  items do not carry per-item platform identity, so this adapter requires `google`;
- a successful result contains `items_count` and `items[]`; each item contains integer
  `year`, integer `month`, and `metrics` with integer `mentions` and
  `ai_search_volume`;
- no Provider Update Time is documented; provider Data Period is calendar year/month and
  remains distinct from Capture acquisition time;
- published pricing states `$0.10` per request plus `$0.001` per row, but Historical
  billing-row grain is ambiguous.

The endpoint page, samples, product copy, and pricing page are claimed contract, not
Evidence. In particular:

- omitted-date defaults and current-month partiality are undocumented;
- a sample apparently includes a zero month before the documented floor;
- sample ordering is newest-first but no ordering guarantee is accepted;
- some language samples include fields absent from the Historical field table;
- pricing and sample cost do not settle whether a month is a billed row;
- zero metrics, an omitted month, empty `items`, `result_count=0`, provider error,
  partial response, and no response are different states.

AI-13 freezes only the request and transport contract. A later Recipe must be based on
verified Historical Evidence, not these claims or synthetic success.

## Accepted adapter contract

Adapter token:

`dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`

Transport:

- method: `POST`;
- scheme/host: `https://api.dataforseo.com`;
- path: `/v3/ai_optimization/llm_mentions/historical/live`;
- query: none;
- exactly one task in the JCS request array;
- reuse PF-09 bounded single-exchange transport, application-header equation, credential
  injection after Attempt commit, response-header retention/omission, redirect refusal,
  and complete/partial/no-response testimony;
- adapter-owned timeout:
  `httpx.Timeout(connect=30.0, read=120.0, write=30.0, pool=30.0)`;
- adapter-owned response ceiling: `8_388_608` bytes;
- no retry, resubmit after provider timeout, polling, GET, continuation, catalog lookup,
  response-derived follow-up, or second provider exchange.

The exact task object is:

```json
{
  "date_from": "2025-08-01",
  "date_to": "2026-07-31",
  "language_code": "en",
  "location_code": 2840,
  "platform": "google",
  "target": [
    {
      "keyword": "generative engine optimization",
      "match_type": "word_match",
      "search_filter": "include",
      "search_scope": ["answer"]
    }
  ]
}
```

Historical Attempt parameters are exactly the task fields above plus:

```json
{
  "contract": "dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1"
}
```

That fragment describes the additional key, not a second document. The complete parameters
map contains exactly `contract`, `date_from`, `date_to`, `language_code`,
`location_code`, `platform`, and `target`. `location_code` is the exact JSON integer
`2840`, not a boolean, float, or string. Request-body bytes are
`JCS([task])`, where `task` is the complete parameters map with only `contract`
removed.

The Historical validator exact-matches the frozen keyword and entire target object. It must
not reuse `_validate_mentions_target` or `_mentions_keyword` as its acceptance rule and
must not expose a keyword argument on closed constructors, the public capture function,
CLI, or deterministic parameter builders. Search Mentions and Target Metrics keyword
grammars are not Historical authority.

Top-level event dispatch may peek only the document schema and version before entering the
HTTP-v2 validator. Within HTTP-v2, the adapter token selects a branch only after closed
top-level validation. The selected Historical branch then revalidates the entire document,
complete parameters map, and exact JCS request-body bytes.

Reject every alternative keyword, missing or alternate date, omitted/alternate platform,
location/language name or alternate code, domain, multiple target, exclude, partial match,
other scope, ChatGPT, tag, any additional or top-level filter, ordering, limit, offset,
token, `internal_list_limit`, `initial_dataset_filters`, catalog request, continuation
key, and unknown parameter.

Policy:

- `mode="paid_probe"`;
- `policy_version="dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1"`;
- `pricing_basis="dataforseo-llm-mentions-historical-live-2026-08-25"`;
- `max_authorized_cost_micro_usd=200000`;
- public capture and the internal issuer require exact Python `int` `200000`; booleans,
  floats, strings, decimals, null, missing acknowledgement, and every other integer fail
  before Attempt creation or send.

The acknowledgement is a fail-closed ceiling, not expected cost, invoice proof, or
permission to retry.

## Event-v2 and Evidence requirements

- Add the adapter token as one explicit closed HTTP event-v2 branch.
- Preserve every published event-v1 and event-v2 byte vector and identifier.
- Attempt parameters contain the complete exact task plus `contract`, including both dates.
- Commit and fully read back the Attempt and exact request-body bytes before issuing a
  caller-unconstructible, one-use transport capability.
- Follow the final Target Metrics closure-owned issuance and consumption design: authority
  and replay state live in the issuer closure, consumption occurs before comparison or I/O,
  and the complete committed Attempt plus exact body bytes are revalidated immediately
  before exchange.
- Do not import, subclass, invoke, or mutate the Target Metrics paid-probe gate. Historical
  receives its own token, closed validator, one-shot state, and module.
- The one-shot guard scans the entire Evidence root and refuses a second committed Attempt
  for this exact adapter token, including unresolved, credential-echo, response-complete
  (at any HTTP status), response-partial, over-limit, or no-response paths. Neighbor
  adapter Evidence may coexist.
- Complete, partial, and no-response branches commit at most one verified Capture.
- Credential echo in the retained body or retained response-header values fails before
  Capture commit. Its committed Attempt consumes the one-shot.
- Inspect returns only the exact nonempty body of a verified complete Historical Capture,
  performs no network or mutation, and rejects wrong adapter, partial, no-response,
  zero-body, invalid ID, unknown version, or tamper.
- Mixed stores scrub clean. Existing fixture and provider Derivations skip valid Historical
  Evidence and write no PostgreSQL rows citing its IDs.

## Public surface

Module:

`observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe`

Capture:

```bash
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe capture \
  --evidence-root PATH \
  --authorize-max-micro-usd 200000
```

Inspect:

```bash
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe inspect \
  --evidence-root PATH \
  --capture-id 64_LOWERCASE_HEX
```

The public Python capture function and CLI take only a concrete Evidence Store/evidence-root
and exact-int `200000`. Issuance requires `type(store) is EvidenceStore`; a subclass
cannot issue. They expose no keyword, date, URL, host, path, headers, request JSON, client,
timeout, body ceiling, platform, location, language, target, filter, retry, continuation,
or alternate spend argument.

Internal deterministic Attempt-construction inputs may vary only `attempt_nonce`,
`authorized_at`, and `observatory_version`. They must not carry keyword, dates,
platform, location, language, target, path, or spend alternatives.

An internal deterministic test seam may replace the production endpoint only with:

`http://127.0.0.1:<1..65535>/v3/ai_optimization/llm_mentions/historical/live`

Reject every other scheme, host, implicit/missing port, path, query, fragment, and userinfo
before Attempt creation and again before exchange. The committed Attempt still names the
production HTTPS target.

## Fact grain and later consumer questions

One Capture is one acquisition exchange for one exact requested target tuple and date
window. One documented `items[]` object is one provider calendar-month candidate with
`mentions` and `ai_search_volume`. Capture time, provider year/month, and unstated
Provider Update Time remain distinct.

The first Evidence should later let a consumer ask what monthly values DataForSEO returned
for this exact target, platform, location, language, scope, match, and requested window.
It cannot answer which questions, answers, pages, or citations produced those aggregates.

The adapter and inspector make no admission or completeness claim. Later interpretation
must distinguish:

- present month with stated zero metrics;
- missing requested month;
- extra or duplicate month;
- empty result or empty items;
- provider error;
- partial/no-response/unresolved;
- requested window from returned period set;
- sample order from accepted ordering;
- provider Data Period from Capture time.

Do not infer global absence, provider-corpus completeness, monitoring cadence, causation,
recommendation, desired coverage, or an Observatory-owned panel. Do not combine Historical
with Target Metrics, Search Mentions, Timeseries, Top Mentioned, or Keyword Overview into a
universal metric or event time.

No Outcome, Observation, Recipe, history route, Measurement Outcomes route, or Holdings
route is authorized here. Their later need and shape depend on verified Evidence.

## Expected changed paths

Production:

- `src/observatory/capture_event.py`;
- `src/observatory/dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py` (new).

Tests:

- `tests/test_dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py` (new).

Ticket:

- this file, limited to [GROK]'s Start commit, Status, and Implementation report.

Stop before every other production, test, authority, specification, migration, schema,
fixture, Recipe, Derivation, selection, API, or ticket path.

## Required proof

- Independent literal JCS bytes and `hashlib.sha256` prove exact request body, fingerprint,
  Attempt, and representative complete Capture without deriving expected values from
  production constructors. Those vectors use the frozen keyword, dates, target, and
  singleton-task body with `contract` excluded.
- Constructors reproduce those vectors and all published adapter identities remain
  byte-identical.
- Closed validation accepts only the exact task/policy and rejects forbidden influence and
  unknown fields, including an alternate keyword, omitted/swapped dates, omitted platform,
  `chat_gpt`, `internal_list_limit`, `initial_dataset_filters`, and location/language
  names instead of the frozen codes.
- Dispatch proof preserves schema/version-only top-level peeking, closed HTTP-v2 selection,
  and complete Historical branch revalidation.
- Exact authorization, concrete `EvidenceStore`, commit, read-back, closure-owned
  capability, consumption, and pre-send revalidation gate every send-capable path.
- Genuine issued-capability mutation, copied/forged/pickled/subclassed/cross-adapter
  capability, used-flag reset, document/body replacement, and replay cannot change the sent
  body or authorize I/O. Object-pool body tamper with an intact bundle copy also fails
  closed before I/O.
- Mock and loopback prove exactly one POST, exact JCS body and sent-header equation, no
  redirects or extra exchange, and committed production target under the loopback seam.
- Complete nonempty/zero-byte/3xx/4xx/5xx, mid-body partial, 8 MiB boundary, connect/send/
  header no-response, duplicate retained headers, denylist omission, and credential echo
  follow HTTP-v2/PF-09.
- Every committed branch reads back, satisfies D8, and scrubs clean.
- Inspect emits byte-exact verified body with no newline, write, or network and rejects all
  forbidden states.
- Mixed fixture/sandbox/Keyword Overview/Organic/Search Mentions/Target Metrics/Historical
  stores scrub clean. `derive`, `derive_keyword_overview`, `derive_google_organic`,
  `derive_search_mentions`, and `derive_target_metrics` each skip Historical Evidence
  with zero integrity failures and zero PostgreSQL rows citing its Attempt/Capture IDs.
  Do not edit any Derivation module to achieve the skip.
- Tests do not parse `items[]`, assert newest-first ordering, pad missing months, calculate
  cost as `$0.001 * items_count`, or classify zero metrics, empty results, or provider
  code `40102`. Those remain later Evidence and Recipe questions.
- Ordinary tests use only `httpx.MockTransport` and loopback. A guard forbids public
  sockets and removes real credential environment variables.
- Targeted Historical/capture-event/mixed-store tests, Ruff, and mypy pass.

## GROK implementation report

Use the project-local `implement`, `tdd`, `codebase-design`, and `code-review` skills
and report their absolute paths.

Report:

- exact parent/child commits, changed paths, clean tree, no amend, no push;
- acceptance-criterion to test map and independent vector bytes/identities;
- exact closure-owned gate, one-shot, pre-send revalidation, request count/body/headers,
  transport accounting, mixed-store/zero-derive proof, and credential non-disclosure;
- strongest/weakest aspects, false greens, caller influence, coupling, provider/parser
  traps, closure blockers, and deferred work;
- what later adapters should reuse and what remains Historical-local;
- Evidence versus claimed contract versus synthetic proof;
- useful and unsafe strategy/data-model implications;
- zero provider/API-host/DNS calls, credentials, spend, live Evidence, retry, continuation,
  operator PostgreSQL mutation, or F12/F13 work.

Do not bury Product questions in the implementation report.

## Implementation verification

[GROK] runs on the VPS:

1. targeted Historical/capture-event/mixed-store tests;
2. `uv run ruff check .`;
3. `uv run mypy src`.

Do not run the full suite during ordinary implementation and do not test through the
ChatGPT MCP connector. After independent review/remediation settle, [GPT] gives [CHAZ]
one exact-HEAD VPS block for targeted tests, the full suite once, Ruff, mypy, and
initial/final HEAD/tree checks.

## Hard boundaries

- One ticket, one implementation commit from the later exact accepted start commit; do not
  amend or push.
- Only [GROK] edits `src/` and `tests/`. He may set this ticket to `review`, never
  `done`.
- No DataForSEO, sandbox, public network, DNS, account, credential, or paid-host request.
- Do not run the public capture with credentials or create live provider Evidence.
- Do not implement parser, fixture promotion, Recipe, Outcome, Observation, migration,
  schema, PostgreSQL relation, selection, API, report, strategy, schedule, backup
  automation, shared capability framework, generic Mentions writer, other platform/target/
  date, Timeseries, Top Mentioned, Multi-Target, Lite, TM Outcomes/Holdings, F12, or F13.
- Do not change or reuse an affected Search Mentions, Organic, Keyword Overview, or sandbox
  gate.

## Next boundary

The provisional review and Steward reconciliation are complete. After the final-ticket
commit, [CHAZ] separately authorizes implementation from that exact clean commit. After
the zero-network adapter implementation is independently reviewed, verified, closed, and
pushed, a separate operator activation ticket may propose exactly one invocation in one
fresh Evidence root. That later ticket must recheck contract and pricing, record the exact
operator command and Evidence root, obtain explicit [CHAZ] authorization, prohibit retries
and replacement roots, and complete the bounded encrypted F6 snapshot/fresh-restore proof.

This ticket itself never authorizes transport or spend.

