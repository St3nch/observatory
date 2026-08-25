# AI-17 — LLM Mentions Historical Recipe selection and admitted-history API

**Status:** accepted  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** explicit [CHAZ] implementation authorization from the exact final accepted ticket commit  
**Authorized workstream:** [CHAZ] approved the next Historical boundary after pushed AI-16 closure  
**Draft base:** `817dd4c5b8bcb57bbd0125f3816816a254a1c1ba`  
**Pre-implementation review:** GROK `RECONCILE`, completed read-only at `4e4a737ffd7c2f03335d071c3b7c0e56f9343249`  
**Implementation start commit:** not yet authorized  

## Purpose

Complete the first consumer-readable Historical slice for the exact adapter:

`dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`.

AI-17 proves isolated Recipe selection/pinning for the accepted Historical Recipe and adds
one fully typed admitted-history route. One returned `captures[]` item is one verified,
admitted Historical Capture document containing exact request context, Capture Outcome,
monthly typed facts, and non-Observation unreturned-requested-period context.

Consumer question:

> What monthly Historical values did DataForSEO return for this exact keyword and closed
> request context under Recipe v1, and which requested periods were not returned?

This ticket does not add Historical Measurement Outcomes or Holdings, Target Metrics
Outcomes/Holdings, provider activity, schema/migration changes, parser/Recipe/Derivation
changes, F12/F13 work, strategy/scoring, pagination beyond the existing bounded history
envelope, or a generic Mentions/history fact model.

This provisional ticket is not implementation authority. GROK must review it read-only,
GPT must reconcile that review, and [CHAZ] must later authorize implementation from the
exact final accepted clean commit.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Observation, Derivation, Provenance, Data Period, and
  strategy boundaries.
- D11 — immutable Recipe-addressed interpretation and semantic Observation identity.
- D12 — claimed contract, verified Evidence, Derivation, and consumer API remain separate.
- D14 — History is admitted subject-bound typed facts; failed/unresolved activity belongs to
  Measurement Outcomes; Evidence-backed subject/scope inventory belongs to Holdings.
- API-01 — shared 12-key admitted-history outer envelope, bounded limits, deterministic
  Capture ordering, `has_more` disclosure, and verify-before-limit semantics.
- AI-12 — closest fully typed provider-history precedent: v1-only Recipe resolution,
  LEFT JOIN result context to Outcome, Evidence-authoritative provenance, strict nested
  Pydantic models, and isolated Recipe selection proof.
- Search Mentions / Google Organic history — accepted precedent that subject-bearing
  `observation_admitted_empty` Captures remain valid history members.
- AI-16 — accepted Historical Recipe, typed persistence, extra-period Product lock,
  unreturned-requested-period semantics, and explicit statement that the later API assembles
  one Capture document from Outcome + context + monthly facts + unreturned periods.

Accepted Historical Recipe:

`fe3e105f3f90c667df0294a2af12e5a27492bfe6eb63a0664b5326619f62d385`

AI-17 authorizes no provider, DNS, credential, account, spend, restic, rclone, live Evidence,
operator PostgreSQL mutation, automatic Recipe selection, or public-network activity.

## Question-resolution lock

GROK completed the required code-first review read-only at clean pushed
`817dd4c5b8bcb57bbd0125f3816816a254a1c1ba` and returned `READY_FOR_TICKET_DRAFT`.
GPT independently verified the material selection, history-envelope, Target Metrics reader,
API error-mapping, Attempt-audit, and admitted-empty premises.

No Product question remains.

Locked technical choices:

- one history item is one admitted Historical Capture document;
- v1 history includes both `observation_admitted` and `observation_admitted_empty`;
- route membership starts from Historical result-context rows and LEFT JOINs the full
  matching Outcome identity so damaged context cannot silently disappear;
- every matching candidate is verified before outer sort/limit;
- exact keyword is the only subject filter;
- selected/pinned Recipe resolution reuses `resolve_provider_recipe` without new generic
  selection machinery;
- only the accepted Historical v1 Recipe may be decoded by this reader;
- extra returned months remain ordinary monthly facts; no `is_extra` field is invented;
- unreturned requested periods remain non-Observation completeness context;
- inner monthly serialization is deterministic Data Period order, never provider array order.

## Route and query

Add exactly:

`GET /v1/providers/dataforseo/google/ai-optimization/llm-mentions-historical/history`

Query:

- `requested_keyword`: required exact string with FastAPI `min_length=1`;
- `derivation_version_id`: optional exact Recipe pin;
- `limit`: default 20, minimum 1, maximum 100;
- `order`: `asc` or `desc`, default `asc`.

Do not trim, case-fold, normalize, or replace the requested keyword with provider echo.
Add no platform, location, language, date/window, scope, cursor, offset, continuation, or
other query parameter. The closed adapter already fixes platform/location/language/window;
adding them as API filters would invent independently selectable axes that v1 does not have.

## Outer history envelope and list grain

Reuse `history_list_response()` unchanged. Do not edit `provider_history.py`.

The dedicated Historical typed envelope must preserve the existing exact 12 outer keys:

- `provider`;
- `adapter_contract`;
- `requested_keyword`;
- `derivation_version_id`;
- `recipe_resolution`;
- `observation_kinds`;
- `captures`;
- `total_matching`;
- `returned_count`;
- `limit`;
- `order`;
- `has_more`.

List grain is admitted Capture documents, not months, Observation envelopes, metric values,
or provider corpus counts.

`total_matching` is the number of unique verified matching admitted Capture documents before
the output limit. `returned_count == len(captures)`. `has_more` only discloses an omitted
outer tail; it is not pagination, a cursor, or authorization to fetch beyond 100.

Verify all matching candidates before sorting/limiting. A damaged matching Capture outside
`limit=1` still yields HTTP 409 and no partial history envelope.

Outer deterministic order is `(request_started_at, capture_id)`. Descending reverses the
complete key before limiting. Outer order does not alter inner monthly order.

## Dedicated typed models

Add a Historical-specific read module with dedicated Pydantic models. Nested models must use
strict validation and `extra="forbid"`; malformed PostgreSQL/Evidence projection is an
integrity failure, not coercible output.

Do not reuse the pass-through `HistoryListEnvelope` as the route response model and do not
create a universal provider-history fact body.

### Capture document

One `captures[]` item contains exactly:

- `attempt_id`;
- `capture_id`;
- `provider`;
- `adapter_contract`;
- `derivation_version_id`;
- `authorized_at`;
- `request_started_at`;
- `transport_ended_at`;
- `request`;
- `capture_outcome`;
- `result_context`;
- `monthly`.

IDs are exact lowercase 64-hex. `provider`, adapter contract, Recipe ID, frozen request
constants, Observation kind, and admitted classification values should be typed as Literals
where the accepted v1 contract permits.

## Request model

`request` is verified Attempt testimony, not task echo. It contains exactly:

- `keyword` — exact Attempt target keyword;
- `match_type = "word_match"`;
- `search_filter = "include"`;
- `search_scope = ["answer"]`;
- `platform = "google"`;
- `location_code = 2840`;
- `language_code = "en"`;
- `date_from = "2025-08-01"`;
- `date_to = "2026-07-31"`.

Read the verified Attempt and pass its parameters through
`validate_historical_http_parameters`. The validator-closed request must agree exactly with
persisted Historical result context. Provider task echo, cost, task path, and response-array
position are not API request truth.

Keep `date_from`/`date_to` as exact strings. Do not synthesize `YYYY-MM`, DATE/TIMESTAMPTZ,
event time, Provider Update Time, or current-month semantics.

## Capture Outcome model and history membership

History membership requires a Historical result-context row under Recipe v1 whose full
matching Outcome identity `(derivation_version_id, attempt_id, capture_id)` has classification
exactly one of:

- `observation_admitted`;
- `observation_admitted_empty`.

Use a LEFT JOIN from context to Outcome, matching the Target Metrics typed-history safety
pattern. Missing Outcome or any other classification for a matching context row is HTTP 409;
do not use an INNER JOIN that silently turns damaged context into empty history.

`capture_outcome` contains:

- `classification` — one of the two admitted v1 values;
- `observation_count` — I-JSON integer `0..9007199254740991`.

Under Recipe v1:

`observation_count == len(monthly) == result_context.items_count`

because every parsed returned monthly point is admitted and duplicate periods already fail in
the strict parser. This equality is an integrity property of v1; it is not requested-window
completeness, mention volume, rank, or provider corpus size.

## Monthly fact model

`monthly` is a list of fully typed Historical monthly Observation facts. Each element has
exactly:

- `observation_kind = dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1`;
- `within_capture_identity` — lowercase 64-hex;
- `requested_keyword`;
- `year` — integer 1..9999;
- `month` — integer 1..12;
- `mentions` — integer 0..9007199254740991;
- `ai_search_volume` — integer 0..9007199254740991.

Recompute every `within_capture_identity` using the accepted AI-16 Recipe and exact axes:
`requested_keyword + year + month`. Every matching generic envelope must agree on
Attempt/provider/adapter/kind/identity.

Load the exact complete typed set for the Capture/Recipe. Duplicate, missing, extra,
wrong-kind, wrong-Attempt, wrong-provider/adapter, identity/content disagreement, or envelope
cardinality disagreement is HTTP 409.

Response serialization order is deterministic:

`ORDER BY year, month, within_capture_identity`

This is Data Period presentation order, not provider response order, rank, or Observation
identity. Outer `order=desc` never reverses this inner array.

A stated returned month with `mentions=0` and `ai_search_volume=0` remains an ordinary monthly
fact.

## Result context and unreturned requested periods

`result_context` contains exactly:

- `items_count` — provider returned cardinality, I-JSON integer;
- `unreturned_requested_periods` — ordered list of closed `{year, month}` objects.

Each unreturned period contains only:

- `year` — 1..9999;
- `month` — 1..12.

No metric, zero, state token, failure flag, `is_extra`, or `within_requested_window` field is
permitted.

The reader must independently recompute the AI-16 completeness relation from primary
testimony:

1. use verified Attempt `date_from`/`date_to` and the AI-16 inclusive calendar-month rule;
2. derive the requested `(year, month)` set;
3. derive `returned_in_window_periods` from the verified complete monthly typed set;
4. compute `requested_periods - returned_in_window_periods`;
5. require exact set equality with persisted
   `llm_mentions_historical_unreturned_requested_periods` rows.

Compare exact `(year, month)` sets, not only counts. A count-preserving wrong/swapped period
is HTTP 409.

Consumer distinctions remain primary-testimony based:

- returned stated zero → monthly row with `0/0` metrics;
- unreturned requested period → present in `unreturned_requested_periods`, absent from
  monthly for that period;
- extra out-of-window return → ordinary monthly row whose year/month is outside
  `request.date_from/date_to`.

Do not add an extra-period table or derived API flag.

## `observation_admitted_empty`

Historical differs from Target Metrics and must preserve subject-bearing admitted empty
Capture documents.

For `observation_admitted_empty` require exactly:

- `observation_count = 0`;
- `monthly = []`;
- verified `request` remains fully populated;
- `result_context.items_count = 0`;
- `unreturned_requested_periods` equals the complete requested 12-month set for adapter v1.

Do not require an Observation envelope for membership. Any leftover envelope/monthly row,
missing/wrong unreturned period, or count disagreement is HTTP 409.

An outer empty history response (`total_matching=0`) means only that there are no matching
admitted Capture documents for the exact keyword and resolved Recipe. It does not mean never
measured, failed measurement, provider zero, or absence from a provider corpus.

## Recipe resolution, validation, and selection proof

Reuse existing `select_provider_recipe()` and `resolve_provider_recipe()` unchanged.

AI-17 must prove in isolated PostgreSQL only:

- no selection + no pin → HTTP 503 `provider_recipe_not_selected`;
- selected accepted v1 → HTTP 200, `recipe_resolution="selected"`;
- exact accepted v1 pin → HTTP 200, `recipe_resolution="pinned"` even without selection;
- malformed pin → HTTP 404;
- unknown pin → HTTP 404;
- wrong-adapter pin → HTTP 404;
- registered Historical Recipe other than accepted v1 → HTTP 404 through a dedicated
  `UnsupportedHistoricalRecipe` selection error;
- tampered/non-UTF8/non-JSON/non-closed/non-JCS/digest-disagreeing accepted-v1 Recipe bytes →
  HTTP 409;
- registered provider/adapter/Recipe-document metadata disagreement → HTTP 409;
- observation-kinds or closed Capture-classification array disagreement with accepted AI-16
  Recipe → HTTP 409.

Serve only Recipe:

`fe3e105f3f90c667df0294a2af12e5a27492bfe6eb63a0664b5326619f62d385`.

The validated accepted v1 Recipe must have exactly one Observation kind `MONTHLY_KIND` and
the exact AI-16 ordered Capture classification array including
`observation_admitted_empty`.

Derivation must never auto-select Recipe state. AI-17 tests selection only in isolated test
PostgreSQL; do not inspect or mutate operator selection state.

## Evidence and PostgreSQL provenance join

PostgreSQL supplies candidate membership, Outcome classification/count, context, monthly typed
facts, envelopes, and unreturned rows. Evidence remains authoritative for Attempt/Capture
identity and transport/request timestamps.

For every matching candidate, verify before limiting:

- Capture Evidence exists and passes Evidence-store integrity;
- Attempt Evidence exists and passes Evidence-store integrity;
- `capture.attempt_id == context.attempt_id == outcome.attempt_id`;
- Attempt and Capture provider/adapter are exactly Historical/DataForSEO;
- Attempt parameters pass `validate_historical_http_parameters`;
- verified Attempt request equals persisted context;
- `authorized_at` comes from verified Attempt;
- `request_started_at` and `transport_ended_at` come from verified Capture;
- all matching envelopes carry the same Attempt/provider/adapter/kind as the verified chain;
- resolved Recipe, context, Outcome, envelopes, facts, and response all use accepted v1.

A second valid Historical Attempt in the store must never cross-link into another Capture's
history document.

Do not re-parse provider body bytes or re-run Derivation in the read path.

## HTTP error mapping

Reuse existing API error signals. Do not invent a new public taxonomy.

- FastAPI empty `requested_keyword` → HTTP 422;
- `ProviderRecipeNotSelected` → HTTP 503 `provider_recipe_not_selected`;
- malformed/unknown/wrong-adapter pin or unsupported registered Historical Recipe → HTTP 404
  `not found` through the existing Recipe mapping;
- Evidence damage/missing backing, Recipe-byte integrity failure, context/Outcome mismatch,
  wrong classification/count, fact/envelope identity/content mismatch, unreturned-set
  disagreement, foreign Attempt, malformed stored field types, or Pydantic projection failure
  → HTTP 409 `evidence_integrity_failure`;
- no matching admitted Captures → HTTP 200 empty typed envelope.

Failed/unresolved Captures must not appear here. Their later representation is a separate
Measurement Outcomes concern and is not AI-17 scope.

## Attempt audit membership

Add `HISTORICAL_ADAPTER_CONTRACT` to the existing `_PROVIDER_ATTEMPT_ADAPTERS` set in
`api.py` and prove `GET /v1/attempts/{attempt_id}` routes Historical Attempts through the
existing generic provider Attempt reader.

Do not redesign the Attempt resource or add Historical-specific fact bodies to it.

## OpenAPI requirements

OpenAPI must expose the exact route/query contract and fully typed Historical response.

At minimum prove:

- required `requested_keyword` with `minLength: 1`;
- optional `derivation_version_id`;
- limit default 20, min 1, max 100;
- order default `asc`, enum `asc|desc`;
- exact provider/adapter/Recipe constants;
- exact one-element `observation_kinds` value;
- Capture/Observation 64-hex ID bounds/patterns;
- `capture_outcome.classification` enum of admitted + admitted-empty only;
- `observation_count`, `items_count`, metrics, year, month integer bounds;
- frozen request Literals;
- required `monthly` array and required `unreturned_requested_periods` array;
- closed `{year, month}` unreturned element model;
- descriptions that state Capture list grain, admitted-empty meaning, returned `0/0` versus
  unreturned versus extra, Data Period year/month, `has_more` non-pagination, and lack of an
  `is_extra` flag.

## Required golden and adversarial proofs

Use isolated PostgreSQL and committed/synthetic test Evidence only. No operator selection or
operator AI-14 Evidence root.

At minimum prove:

- selected v1 success and pinned v1 success;
- unselected 503;
- malformed/unknown/wrong-adapter pin 404;
- unsupported registered Historical Recipe 404;
- tampered accepted-v1 Recipe bytes 409;
- exact AI-14 admitted Capture: 12 monthly points, exact frozen request window,
  `items_count=12`, `observation_count=12`, unreturned `[]`;
- admitted-empty Capture: zero monthly, zero observation_count/items_count, all 12 requested
  periods unreturned;
- returned `0/0` month remains monthly and is not unreturned;
- extra 2026-08 remains monthly with request window unchanged;
- mixed extra+dropped case retains extra and exposes only the dropped requested month as
  unreturned;
- shuffled persistence/provider lexical order still serializes monthly by
  `(year, month, within_capture_identity)`;
- `items_count`, `observation_count`, envelope count, and monthly count disagreement → 409;
- exact unreturned set disagreement, including count-preserving wrong period → 409;
- context without Outcome or non-admitted Outcome → 409;
- foreign Attempt cross-link → 409;
- missing/corrupt Attempt or Capture Evidence and parent mismatch → 409;
- verified Attempt request vs PostgreSQL context disagreement → 409;
- envelope provider/adapter/Attempt/kind/identity disagreement → 409;
- verify-before-limit: damaged matching Capture outside `limit=1` still 409;
- exact keyword subject filter;
- deterministic asc/desc Capture order and total/returned/has_more semantics;
- empty keyword 422;
- exact OpenAPI route/models/descriptions;
- Historical Attempt-audit routing;
- derive does not auto-select and isolated selection/pinning behaves generically;
- existing fixture hashes remain unchanged;
- no schema/provider/network/credential/Evidence/operator-PostgreSQL activity.

Tests must not describe a socket `create_connection` guard as universal proof of all network
absence.

## Expected implementation allowlist

When and only when this ticket is final and [CHAZ] separately authorizes implementation,
GROK may modify exactly:

Production:

- `src/observatory/llm_mentions_historical_read.py` — new;
- `src/observatory/api.py` — one history route/import and Historical Attempt-audit membership.

Tests:

- `tests/test_api_llm_mentions_historical.py` — new;
- `tests/test_api_attempts.py` — bounded Historical Attempt-audit routing only;
- `tests/test_provider_recipe_selection.py` — bounded isolated Historical selection/pinning
  proof only.

Ticket:

- this file for Start commit, status, and implementation report.

No other path is authorized. In particular do not edit:

- `provider_history.py`;
- `migrate.py`;
- Historical parser or parser tests;
- Historical Recipe/Derivation module or derive tests;
- Search Mentions, Organic, Target Metrics readers/tests;
- provider selection production machinery;
- authority/roadmap files during implementation.

If another path appears required, stop and ask the Steward before mutation.

## Implementation verification after later authorization

GROK may run bounded targeted tests during implementation. Expected targeted command:

```bash
uv run pytest -q \
  tests/test_api_llm_mentions_historical.py \
  tests/test_api_attempts.py \
  tests/test_provider_recipe_selection.py
```

Then:

- `uv run ruff check .`;
- `uv run mypy src`.

Do not run the full suite during ordinary implementation. After implementation review and
any remediation settle, the Steward owns the exact-HEAD full-suite validation gate; [CHAZ]
may run it over SSH if the governed runner is unavailable or unreliable.

## Mandatory GROK provisional-ticket review

Before AI-17 can become implementation authority, GROK must review this exact provisional
ticket read-only against current authority and code.

Challenge especially:

- LEFT JOIN context-before-classification and admitted-empty membership;
- v1 Recipe-byte validation and HTTP mapping;
- request-vs-result-context split;
- exact unreturned-period recomputation and monthly completeness;
- inner month ordering versus outer Capture ordering;
- Evidence-authoritative timestamps/provenance;
- verify-before-limit and foreign-Attempt defenses;
- strict Pydantic/OpenAPI model contract;
- Attempt-audit membership;
- whether the five implementation/test paths above are sufficient and minimal;
- accidental Outcomes/Holdings/schema/provider_history/shared-reader/F12/F13 widening;
- missing adversarial tests or false-green integrity checks.

Do not edit files, select Recipes, mutate PostgreSQL/Evidence, implement, call providers,
use credentials, perform public-network/DNS/restic/rclone activity, commit, amend, or push.

Return `READY`, `RECONCILE`, or `NOT_READY`, separating genuine Product questions from
technical corrections. No second major code-first review is required unless this ticket
introduces a genuinely new unresolved premise.

## Hard boundaries

- Historical Recipe selection/pinning + one fully typed admitted-history route only.
- No Historical Outcomes or Holdings.
- No Target Metrics Outcomes/Holdings.
- No other LLM Mentions / AI Optimization family.
- No provider activity, credentials, spend, retry, continuation, or recapture.
- No schema, migration, parser, Recipe, Derivation, identity, or persistence change.
- No automatic Recipe selection.
- No `provider_history.py` change.
- No cursor/offset/token or retrieval beyond 100.
- No strategy, scoring, recommendation, cadence, panel, or project-specific state.
- No generic Mentions model or generic read-framework extraction.
- No F12 or F13 work.
- Only GROK writes `src/` and tests after separate implementation authorization.
- No amend or push without [CHAZ] authorization.

## Stop point

AI-17 remains provisional until GROK's read-only ticket review is reconciled and the final
ticket is committed. Even then implementation remains blocked until [CHAZ] separately
authorizes GROK from that exact clean final-ticket commit.
