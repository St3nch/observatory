# AI-13 — LLM Mentions Historical Live paid-probe adapter

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none  
**Approved by:** [CHAZ] for provisional ticket drafting / [GPT] Steward reconciliation  
**Closure authorized by:** [CHAZ] after exact-HEAD operator verification  
**Pre-implementation review:** GROK RECONCILE, completed read-only at
`c735542ab19a56617498a52031eec5419f578423`  
**Review base:** `c735542ab19a56617498a52031eec5419f578423`  
**Start commit:** `a2ec25eecbf13310b180bc83348cf9c416a51899`

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

## Implementation report

**Parent:** `a2ec25eecbf13310b180bc83348cf9c416a51899`  
**Child:** this implementation commit  
**Status:** `review`  
**AI-13 only:** yes. Nothing pushed. No amend.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

Branch `main`, tracking `origin/main` identical at the start commit. Working tree clean after this commit.

### Changed-path allowlist

- `src/observatory/capture_event.py` (sixth exact HTTP-v2 adapter branch)
- `src/observatory/dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py` (new)
- `tests/test_dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py` (new)
- this ticket (Start commit, Status, Implementation report)

### Adapter token

`dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`

Production POST `https://api.dataforseo.com/v3/ai_optimization/llm_mentions/historical/live`

Frozen request: keyword `generative engine optimization`, `date_from=2025-08-01`,
`date_to=2026-07-31`, `platform=google`, `location_code=2840`, `language_code=en`,
one include target, `search_scope=["answer"]`, `match_type=word_match`.

### Independent vectors

Fixed inputs: nonce `8888…88`, `authorized_at=2026-08-25T20:00:00.000000Z`,
`observatory_version=conformance-llm-mentions-historical-paid-probe-v1`.
Independent `hashlib.sha256` of literal JCS bytes (`test_independent_literal_vectors`);
constructors reproduce them (`test_closed_request_vector_and_attempt_identity`).
`contract` is in Attempt parameters and absent from the POST body.

| Artifact | Value |
|---|---|
| request body | `[{"date_from":"2025-08-01","date_to":"2026-07-31","language_code":"en","location_code":2840,"platform":"google","target":[{"keyword":"generative engine optimization","match_type":"word_match","search_filter":"include","search_scope":["answer"]}]}]` |
| request SHA-256 | `9f40139201acaa18f72fc14d6ae7b2f582317474bbc9e90f0661a5360740f480` |
| fingerprint | `6b4977c1630976a3c6c55680adb5566f3d496aee99abe7614ffbcbd07f02bbb0` |
| Attempt ID | `8f8694807187c47a68b7fcb82185a36df8cddde6f6ec222ca9a11720c4652444` |
| complete Capture ID (`{"ok":true}`) | `7b3311189261e0906ea6d6f7dd438c2be2b79615aaa1f63017579e85b35c5084` |

Previously published sandbox / Keyword Overview / Organic / Search Mentions / Target Metrics
Attempt IDs remain byte-identical.

### Closure-owned gate, one-shot, pre-send revalidation

- Public capture and `_issue_verified_attempt` require `type is int` and value exactly
  `200000` before Attempt commit or send.
- `type(store) is EvidenceStore`; subclass cannot issue.
- `_historical_attempt_exists` scans every committed Attempt in the root for this adapter
  token (including unresolved).
- Refuse at `_open_or_create`, `_run_gated_capture`, and issuer.
- Capability is unconstructible, immutable, one-use. Transport authority lives in the
  issuer closure. Consumption sets `consumed=True` before field comparison, Evidence
  revalidation, or `perform_bounded_http_exchange`.
- Immediate pre-send: identity + consumed record, visible-field match, `read_attempt` +
  `verify_attempt_directory`, bundle `request.body` equality, `validate_historical_http_parameters`,
  recomputed JCS, `_require_historical_target`, send closure-owned bytes only.
- Neighbors (fixture, sandbox, KO, Organic, Search Mentions, Target Metrics) coexist and
  do not consume this one-shot.
- Historical module does not import, subclass, invoke, or mutate the Target Metrics gate.
- Historical validator exact-matches the frozen keyword and does not call
  `_validate_mentions_target` or `_mentions_keyword`.

### Mock/loopback request

One POST to `/v3/ai_optimization/llm_mentions/historical/live`, exact JCS body above, sent
headers: `accept`, `accept-encoding: identity`, `connection: close`, `content-type`,
`user-agent: observatory-dataforseo-v1`, `host: api.dataforseo.com`,
`content-length: 247`, `authorization: Basic <sentinel>`.
Loopback override only `http://127.0.0.1:<port>/v3/ai_optimization/llm_mentions/historical/live`.
Committed Attempt still names production HTTPS. Redirects not followed (302 is complete Capture).

### Transport accounting

- Adapter ceiling `8_388_608`; shared transport does not own it.
- Default ceiling: `8_388_608+1` body → `response_partial` of exactly 8 MiB.
- 200/302/404/500 nonempty → `response_complete`.
- Zero-byte 200 → complete, `present_zero_bytes`.
- Mid-body timeout → `response_partial`.
- `ConnectError` → `no_response`.
- Duplicate `x-request-id` retained; denylist names omitted.
- Credential echo in body or retained header: no Capture; Attempt remains; one-shot consumed.

### Mixed-store / derive

Fixture + sandbox + KO + Organic + Search Mentions + Target Metrics + Historical:
`scrub_store` empty. `derive`, `derive_keyword_overview`, `derive_google_organic`,
`derive_search_mentions`, and `derive_target_metrics` skip Historical Evidence; zero
PostgreSQL `outcomes` rows cite its Attempt/Capture IDs. No Derivation module was edited.

### Credential non-disclosure

Sentinel login/password/basic never appear in committed manifests or retained headers.
Authorization is injected only after the capability is issued. Ordinary tests delete
credential env vars and fail any non-loopback `socket.create_connection`.

### Acceptance criterion to proving-test map

| Criterion | Tests |
|---|---|
| Independent literals + hashlib | `test_independent_literal_vectors`, `test_closed_request_vector_and_attempt_identity` |
| contract excluded from POST, present in parameters | `test_closed_request_vector_and_attempt_identity` |
| Constructors reproduce; old IDs unchanged | `test_closed_request_vector_and_attempt_identity`, `test_existing_adapter_identities_unchanged` |
| Frozen keyword/dates/platform; unknown fields | `test_frozen_fields_are_rejected`, `test_missing_required_keys_are_rejected`, `test_wrong_policy_fields_are_rejected`, `test_confused_contracts_are_rejected` |
| Schema/version-only peek | `test_http_v2_dispatch_peeks_schema_and_version_only` |
| Auth/concrete-store/commit/read-back/capability | `test_authorization_required_before_attempt`, `test_subclassed_store_cannot_issue`, `test_attempt_is_committed_before_first_handler`, `test_failed_attempt_commit_never_reaches_handler` |
| One-shot complete/unresolved/echo/partial/neighbors | `test_one_shot_is_adapter_specific_and_allows_neighbors`, `test_unresolved_attempt_blocks_second_invocation`, `test_credential_echo_leaves_unresolved_one_shot`, `test_over_limit_partial_consumes_one_shot`, `test_default_8mib_ceiling_is_partial` |
| Forged/copied/pickled/replayed/cross-adapter | `test_forged_copied_mutated_and_replayed_capability_cannot_transport`, `test_cross_adapter_capabilities_are_isolated` |
| Issued body/document replacement; `_used` reset | `test_issued_request_body_replacement_cannot_transport`, `test_issued_document_replacement_cannot_transport`, `test_closure_owned_replay_protection_ignores_used_attribute` |
| Pool tamper with intact bundle | `test_pre_send_verifies_committed_attempt_and_request_body` |
| One request, JCS, headers, Historical path, no redirect | `test_attempt_is_committed_before_first_handler`, `test_loopback_server_sees_attempt_and_does_not_follow_redirect`, `test_token_in_body_is_still_one_exchange` |
| Complete/partial/no-response/8 MiB | `test_complete_status_classes_and_zero_byte`, `test_mid_body_timeout_and_no_response`, `test_default_8mib_ceiling_is_partial`, `test_secret_headers_omitted` |
| Inspect | `test_inspect_emits_exact_bytes_without_mutation`, `test_inspect_rejects_wrong_adapter_partial_zero_and_tamper` |
| Mixed scrub / all-Derivation skip | `test_one_shot_is_adapter_specific_and_allows_neighbors`, `test_fixture_and_provider_derive_skip_historical` |
| No public network / no real credentials | autouse `_no_public_network`, `_isolate_credentials` |
| Public surface has no subject/date injection | `test_public_cli_and_function_have_no_injection_seams` |

### Code-review

**Standards:** 0 hard / 3 judgement. Worst: Historical transport gate duplicates the Target
Metrics closure-owned pattern by ticket requirement; extracting a shared capability
framework is forbidden. The test module is large because the proof list is large.

**Spec:** no missing required proof, no parser/Recipe/API creep, no TM-gate import.
Public capture takes only concrete `EvidenceStore` and exact-int `200000`. Closed
constructors take no keyword/date arguments.

### Strongest / weakest

Strongest: frozen-keyword validator distinct from `_mentions_keyword`; independent JCS with
`contract` stripped; adapter-keyed whole-root one-shot including unresolved and
credential-echo; pool-object tamper with original bundle body; TM derive skip without
editing Derivation modules.

Weakest: send/header-phase no-response still ConnectError-only (matching TM/PF-09);
inspect unknown-version not planted (cannot commit an invalid v2 Capture through
constructors); capability `_used` is still written as a non-authoritative mirror.

### Remaining caller-controlled influence

These cannot change the sent Historical request body through capability attributes:

- `_exchange` still takes `client`, `endpoint`, and `max_response_body_bytes` (approved
  test seam). A holder can deliver the **verified** body to loopback/mock, not a substitute
  body.
- `_commit_historical_capture` still reads capability attributes after transport.
  Post-exchange `object.__setattr__` on `document` / `attempt_id` can still affect Capture
  construction, not the HTTP body.
- `_Issuance` lives in `_exchange.__closure__`. Same-process closure mutation is accepted
  for this adapter as for AI-08; this is not F7.
- `argparse type=int` CLI path is not the same as `type is int` on the public Python
  function; CLI still requires `--authorize-max-micro-usd 200000`.

Public capture/CLI expose no keyword, date, platform, location, language, target, URL,
timeout, ceiling, retry, or continuation argument.

### Architecture drift / coupling

- Historical is a new `capture_event` HTTP-v2 branch plus a Historical-local module.
- PF-09 `perform_bounded_http_exchange` is reused; timeout and 8 MiB ceiling stay adapter-owned.
- Target Metrics gate is not imported. Search Mentions keyword grammar is not Historical
  admission.
- Do not later fold Historical months into TM `total.v1` / `source_domain.v1` or SM item
  kinds.

### Provider / parser traps (deferred)

- Dual-platform omission, default dates, pre-floor zero months, newest-first sample order,
  billing-row grain, zero vs missing vs `40102` remain claimed-contract, not Recipe.
- This ticket does not parse `items[]`.

### Closure blockers and deferred work

- No live provider call. Real envelope, month list, and billed `cost` remain a later
  activation ticket plus F6 one-shot protection.
- F12, F13, parser, Recipe, schema, API, Outcomes, Holdings, Timeseries, Top Mentioned
  remain out of scope.
- AGENTS.md does not yet list this module entrypoint (Steward-owned).

### Reuse vs Historical-local

Reuse later: PF-09 exchange, HTTP-v2 Attempt/Capture spine, closure-owned issuance copied
from TM **as a pattern**, Evidence inspect/scrub, adapter-keyed derive skip.

Remain Historical-local: path, dates, frozen target, parser IR, Recipe, Observation kinds,
completeness vs requested window, paid-probe module and one-shot token.

### Evidence vs claimed contract vs synthetic proof

Synthetic tests prove Observatory's closed request, transport, and Evidence accounting.
They do not prove the provider's month topology, ordering, or billing grain. Official docs
remain claimed contract. A later Capture is the only Empirical Historical Evidence.

### Useful and unsafe downstream implications

Useful later: a consumer can ask what monthly `mentions` and `ai_search_volume` DataForSEO
returned for this exact tuple and window in one Capture.

Unsafe: treating this adapter as monitoring cadence, treating a missing month as zero,
equating the latest month with Target Metrics `total.mentions`, or treating the series as
an answer/citation archive.

### Command evidence

```
uv run pytest -q \
  tests/test_dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py \
  tests/test_capture_event.py
```

exit 0, **141 passed**.

```
uv run ruff check .
```

exit 0, all checks passed.

```
uv run mypy src
```

exit 0, no issues in 35 source files.

### Confirmation

Zero DataForSEO / sandbox / DNS / paid-host / account / public-network requests.
Zero real credentials. Zero live Evidence. Zero credit spend.
Zero retry, continuation, operator PostgreSQL mutation, F12, or F13 work.
No parser, fixture promotion, Recipe, Derivation edit, schema, API, ChatGPT branch,
domain target, Timeseries, Top Mentioned, generic Mentions writer, other ticket, or
authority document except this ticket's implementer fields.
No amend. No push. No operator activation command.

## Closure

CHAZ explicitly authorized closure after the implementation review settled without a
remediation requirement. GPT independently reviewed the exact implementation parent/child
comparison through LinuxVedaOpsMCP and added the implemented module entrypoint in a separate
Steward-owned documentation commit.

Accepted lineage:

- accepted implementation boundary:
  `a2ec25eecbf13310b180bc83348cf9c416a51899`;
- implementation:
  `e347fcb59002e2e066f0e0caedd8d59a8931d28f`;
- Steward entrypoint alignment and operator-verified HEAD:
  `d51e4d5a75278189ec2fe8b4909ecf1612378d56`.

CHAZ's exact-HEAD VPS operator verification:

- initial exact-HEAD and clean-tree guards passed;
- targeted AI-13/Capture Event suite passed under the guarded operator block;
- full suite, run once: **1336 passed, 1 skipped**, 1 warning;
- Ruff: passed;
- mypy: passed with 35 source files;
- final HEAD: exact `d51e4d5a75278189ec2fe8b4909ecf1612378d56`;
- final tree: clean.

The warning is the known Starlette/`httpx` TestClient deprecation and is accepted as
non-blocking. This closure changes only this ticket. Per the accepted workflow, tests are
not repeated after the ticket-only closure commit.

No provider call, activation, credentials, spend, retry, continuation, live Evidence
mutation, operator PostgreSQL mutation, F12, or F13 activity occurred. AI-13 closes with
the zero-network Historical Live adapter and inspect path only; empirical provider
activation, parser, Recipe, schema, Derivation, and consumer resources remain separate
future boundaries.
