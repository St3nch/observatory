# RANK-06 — DataForSEO Google Ranked Keywords Recipe selection and admitted-history API

**Status:** remediation — [GPT] Steward review found one bounded Recipe-metadata status-code defect; [CLAUDE] remains Writer  
**Owner:** [GPT] Steward review / [CLAUDE] designated and implementation-authorized Writer  
**Blocked by:** none; RANK-05 closed  
**Draft base:** `512525f78c20e49eb096b8ab98c0ed4ad2d64df0`  
**Pre-implementation review base:** `9aab9bf7c0884aa7c60f68276fc2d821285d35f5`  
**Pre-implementation reviewer:** [GROK] independent read-only code-first review  
**Pre-implementation recommendation:** `RECONCILE`; no Product question identified  
**Implementation authorization base:** `659a93d4d58ed5090574fe309c4be46cf005a1c5`  
**Implementation start SHA:** `dcbe91365d89e18d171ea929e3b7dd1595b1d261` — branch `main`, clean working tree, verified before any edit; the implementation commit is a direct child of this SHA  
**[CHAZ] implementation authority:** [CLAUDE] may implement this reconciled ticket; no provider calls, credentials, Evidence mutation, spend, amend, or push  
**Provider authority:** zero calls, zero spend, zero credentials, zero Evidence mutation; existing RANK-03 Evidence / RANK-04 Conformance fixture / RANK-05 rebuildable state only  

## Purpose

Complete the consumer-readable Ranked Keywords MVP vertical slice for the exact adapter:

    dataforseo-labs-google-ranked-keywords-live-paid-probe-v1

RANK-06 selects or pins the accepted RANK-05 Recipe and adds one exact-subject admitted-history
route. One outer list member is one admitted Ranked Capture document containing verified
Attempt request testimony, provider result context, all four semantic Observation families,
and the provider occurrence testimony that connects returned rows to semantic facts.

The API must preserve the RANK-05 distinctions instead of making Ranked easier to consume by
making it less true. In particular:

- target corpus aggregates are not the returned item set;
- `rank_group` and `rank_absolute` are independent rank systems;
- placement identity is not URL/Page identity;
- Ranked-local keyword enrichment is not Keyword Overview or Related Keywords identity;
- monthly `(year, month)` is Data Period, not acquisition time or a provider clock;
- provider movement/loss fields are provider comparison testimony, not Observatory
  Capture-to-Capture change;
- a returned provider item occurrence links a placement fact and a keyword-data fact without
  making `item_index` semantic identity;
- the API exposes exact request/provider count testimony without manufacturing completeness,
  truncation percentage, canonical Page, Strategy, score, recommendation, or trend semantics.

No provider exchange, credentials, spend, new Evidence, parser, Recipe, Derivation, schema,
migration, Measurement Outcomes, Holdings, pagination, canonical Page/domain identity,
cross-surface normalization, recurring acquisition, Strategy behavior, or push is authorized.

## Authority and accepted foundation

- VISION and VOCABULARY API-only consumer boundary, Evidence, Outcome, Observation,
  Derivation Recipe, Provider Update Time, Data Period, Holdings, and Strategy semantics;
- D2 and D3 — consumers use the versioned API; interpretation stays downstream;
- D8 — Evidence authority and verify-on-read;
- D11 — provider Recipe identity, strict semantic interpretation, independent time axes, and
  exact-content rebuild behavior;
- D12 — claimed contract plus bounded Evidence; one Capture proves testimony, not invariance;
- D14 — admitted history is separate from Measurement Outcomes and Holdings; bounded outer
  history discloses list scope/cardinality without one universal fact body;
- API-01 — verify-before-limit outer history semantics;
- AI-12, AI-17, and RK-05 — newer fully typed surface-local selected/pinned history readers;
- RANK-01 through RANK-05 — exact acquisition contract, protected live Evidence, strict
  parser, four-kind Recipe, twelve typed Ranked relations, exact-content/complete-set rebuild,
  and the four-pillar time model.

RANK-05 accepted implementation:

    3364a5926a7977ec84f904a10412048743a5827e

Accepted Ranked Recipe v1:

    c7573695db7ecaa0f5dfdc2fc3658e84b1673eec005a0d8003093e57408294a8

Accepted canonical Recipe byte length: `2825`.

Exact Recipe-v1 Observation kinds, in the **stored Recipe order**:

1. `dataforseo.google.ranked_keywords.corpus_metrics.v1`
2. `dataforseo.google.ranked_keywords.keyword_data.v1`
3. `dataforseo.google.ranked_keywords.monthly_search_volume.v1`
4. `dataforseo.google.ranked_keywords.ranked_result.v1`

Exact Recipe-v1 Capture-stage taxonomy, in the **stored Recipe order**:

1. `no_response`
2. `observation_admitted`
3. `provider_envelope_rejected`
4. `provider_error`
5. `response_partial`
6. `transport_complete_non_admissible`

`observation_admitted_empty` and `reconciliation_failed` are deliberately absent from Ranked
Recipe v1.

## Final Steward reconciliation lock — 2026-09-01

Grok independently reviewed the draft at exact clean HEAD
`9aab9bf7c0884aa7c60f68276fc2d821285d35f5` and returned `RECONCILE`. The Steward
independently verified the material findings against the Ranked Recipe, parser, derive logic,
PostgreSQL schema, provider Attempt route, shared history helper, and Related Keywords read
precedent. The reconciled rules below are final RANK-06 design authority and supersede any
contradictory provisional wording later in this ticket. No Product question remains.

The material reconciliation is:

- semantic identity is anchored to the **verified Attempt target**, never to a semantic row's
  self-claimed `requested_target`;
- context-anchored membership gets a reverse subject-membership proof so deletion of only the
  Ranked result-context row cannot silently shrink history;
- generic Observation-envelope provenance is checked explicitly because PostgreSQL does not
  foreign-key envelope `attempt_id`, `provider`, or `adapter_contract` to the cited Capture;
- Recipe-v1 state applicability is narrower than the generic SQL five-token field-state
  domain, including the `rank_group` converse to the schema's rank-absolute locus CHECK;
- every stated Ranked `se_type` and every returned-item occurrence `item_se_type` is exactly
  `google`;
- corpus `(aggregate_family, rank_system)` membership is the exact ten-element cross-product;
- exact-one Capture Outcome, duplicate-candidate rejection, stated-empty monthly-series
  validity, local outer-key closure, child-local `se_type` projection, and explicit
  selected/pinned Attempt-audit behavior are part of the served contract;
- deterministic ranked-result presentation is keyword-first so it is visibly distinct from
  the frozen provider `rank_group,asc` request order.

One residual integrity limit is accepted and disclosed rather than hidden: if damage deletes
the Ranked result-context row **and all four subject-bearing semantic parent families** while
leaving only generic Outcome/envelope rows, an exact-subject admitted-history route has no
remaining subject-bearing relational row from which to discover that Capture. Closing that
store-wide/failure-aware gap belongs to the separately deferred Ranked Measurement Outcomes /
Holdings work, not to RANK-06.

## Steward code-first review — reconciled technical boundary

This section records the reconciled technical contract derived from repository authority,
RANK-05 persistence/tests, generic Recipe selection, shared provider-history behavior, Related
Keywords, Historical LLM Mentions, Target Metrics, Measurement Outcomes, Holdings, current
API routing, and API test precedents. The pre-implementation challenge is complete; these
rules now govern implementation subject only to separate [CHAZ] authorization.

### 1. Exact route and exact subject

Exact route:

    GET /v1/providers/dataforseo/google/ranked-keywords/history

Query:

- `requested_target` — required exact string, `min_length=1`;
- `derivation_version_id` — optional exact Recipe pin;
- `limit` — default 20, minimum 1, maximum 100;
- `order` — `asc|desc`, default `asc`.

The history subject is the **exact requested target from verified Attempt Evidence**. It is
not result echo target, returned URL, domain, main domain, website name, keyword, canonical
site, Page, or Strategy entity.

Do **not** reuse the RANK-02 acquisition-time two-label ASCII target grammar on this read
query. That grammar deliberately bounded one paid adapter invocation; it is not a provider
semantic identity rule. An impossible exact subject is a normal empty-history miss under a
valid Recipe, not an HTTP 422 merely because the operator could not acquire it through v1.

Do not trim, case-fold, URL-normalize, apex/`www` collapse, redirect-resolve, registrable-
domain parse, or otherwise canonicalize the query.

### 2. Dedicated Ranked outer envelope; do not corrupt `requested_keyword`

The accepted shared `provider_history.history_list_response()` hard-codes the outer field
`requested_keyword`. Ranked's accepted subject is `requested_target`. Do not stuff a target
into a field named `requested_keyword` merely to reuse the helper, and do not rename the
already-published shared history contract for sibling surfaces in this ticket.

Use a dedicated strict `RankedKeywordsHistoryEnvelope` with exactly these outer keys:

- `provider`;
- `adapter_contract`;
- `requested_target`;
- `derivation_version_id`;
- `recipe_resolution`;
- `observation_kinds`;
- `captures`;
- `total_matching`;
- `returned_count`;
- `limit`;
- `order`;
- `has_more`.

The implementation may reuse `HISTORY_LIMIT_DEFAULT` / `HISTORY_LIMIT_MAX`; the smallest
accepted design computes the same outer list math locally rather than modifying
`provider_history.py`. Define a module-local closed twelve-key `RANKED_OUTER_HISTORY_KEYS` set and require exact
equality before model validation, preserving the existing outer-envelope key check.

Outer ordering remains complete whole-Capture ordering by
`(request_started_at, capture_id)`. `desc` reverses that complete key before limiting.
`has_more` describes omitted **Capture history**, not provider Ranked rows and not provider
pagination.

### 3. Recipe selection and exact stored-Recipe verification

Reuse `resolve_provider_recipe()` for the exact Ranked adapter. RANK-06 imports
`RANKED_KEYWORDS_RECIPE` / `RANKED_KEYWORDS_RECIPE_ID` from
`google_ranked_keywords_derive.py`; do not move the Recipe into the frozen parser module.

Accepted selection behavior:

- no selection and no pin -> HTTP 503 `provider_recipe_not_selected`;
- selected accepted v1 -> 200 with `recipe_resolution="selected"`;
- explicit accepted v1 pin -> 200 with `recipe_resolution="pinned"`, even if no current
  selection exists;
- malformed, unknown, wrong-adapter, or registered same-adapter non-v1 pin -> accepted 404
  provider-selection path;
- tampered/noncanonical/digest-disagreeing accepted-v1 Recipe bytes or provider/adapter/kind/
  taxonomy disagreement -> HTTP 409 `evidence_integrity_failure` with no partial envelope.

Before serving success, reread the stored Recipe bytes and require strict UTF-8 JSON, accepted
closed Recipe shape, exact JCS bytes, exact digest, provider `dataforseo`, exact Ranked
adapter, exact ordered `observation_kinds` list above, and exact six-class Capture taxonomy
above. Do not confuse that list with `observation_identity.kinds`, whose order differs inside
the same accepted Recipe document.

Define a surface-local `UnsupportedRankedKeywordsRecipe(ProviderRecipeSelectionError)` (or an
equivalent subclass carrying the same accepted selection taxonomy) so a registered
same-adapter non-v1 Recipe reaches the existing HTTP 404 path rather than escaping as 500.

Derivation registers the Recipe but must not automatically select it for the operator.

### 4. Candidate membership and verify-before-limit

Candidate history membership is anchored on `ranked_keywords_result_context`, filtered by
exact `requested_target` and accepted Recipe v1. LEFT JOIN `outcomes` on the full
`(derivation_version_id, attempt_id, capture_id)` tuple.

Do not put `o.classification`, Outcome non-nullness, or SQL `LIMIT` into candidate membership
in a way that can hide relational damage. Classification is inspected after the matching
context row reaches Python.

Every matching candidate is completely verified **before** sort/outer limit. Damage in a
matching Capture outside `limit=1` still fails the whole read with 409.

A matching context with missing Outcome, foreign-Attempt Outcome, duplicate Capture Outcome,
or a classification other than exact `observation_admitted` is integrity disagreement. It is
never silently omitted and never converted to empty history.

For every context-anchored candidate, separately query all Capture-stage Outcome rows for
`(Recipe v1, capture_id)` and require exactly one row. Its `attempt_id` must equal the
verified Attempt, its classification must be exactly `observation_admitted`, and its
`observation_count` must satisfy the complete-set rules below. The context LEFT JOIN alone is
not sufficient because PostgreSQL permits another Outcome for the same Capture under a
different Attempt identity.

Reject duplicate candidate `capture_id` values before counting or sorting even though the
current context primary key makes them unreachable under an undamaged schema.

Because candidate membership is context-anchored, also perform a reverse subject-membership
probe before sorting/limiting. Under Recipe v1, collect distinct Capture ids carrying the
exact queried `requested_target` from each subject-bearing semantic parent table:
`ranked_keywords_corpus_metrics`, `ranked_keywords_ranked_results`,
`ranked_keywords_keyword_data`, and `ranked_keywords_monthly_search_volume`. The union must
equal the context-anchored candidate Capture-id set; any difference is HTTP 409. This catches
deletion of only the result-context row while admitted semantic parents survive. Successful
zero-item Ranked Captures remain discoverable because Recipe v1 always persists ten corpus
parents.

For each candidate verify at minimum:

1. exact stored Recipe identity/bytes;
2. exact committed Attempt Evidence;
3. public `validate_ranked_keywords_http_parameters()` over the verified Attempt parameters;
4. exact committed Capture Evidence and Capture -> Attempt parentage;
5. provider/adapter identity on Attempt and Capture;
6. persisted request-context agreement with verified Attempt authority;
7. exact Capture Outcome classification/count;
8. complete Observation-envelope / semantic-parent / child / occurrence / context
   consistency for Recipe v1.

Result echo target/location/language/`se_type` is provider testimony and may disagree with the
verified Attempt request. Expose disagreement; do not repair it and do not use echo as
history membership.

### 5. One Capture document is five sibling testimony collections

One admitted Ranked history Capture should expose:

- verified request testimony;
- admitted Capture Outcome;
- provider result context;
- `corpus_metrics[]`;
- `ranked_results[]`;
- `keyword_data[]`;
- `monthly_search_volume[]`;
- `item_occurrences[]`.

The four semantic collections correspond to the four Observation kinds. `item_occurrences`
is subordinate provider occurrence testimony, not a fifth Observation kind.

Monthly item occurrences are nested under the monthly semantic fact they cite;
the returned-item occurrence bridge remains a sibling collection because one provider item
connects **two** semantic parents: one placement and one keyword-data identity.

Do not expose one generic mixed `observations[]` body merely because the generic envelope
exists in PostgreSQL. Surface-local typed siblings are the established AI-12/AI-17/RK-05
consumer precedent and preserve the different Ranked grains.

### 6. Request and result context

The Capture `request` block is projected from verified Attempt authority and contains exactly:

- `target`;
- `location_code`;
- `language_code`;
- ordered `item_types`;
- `ignore_synonyms`;
- `include_clickstream_data`;
- `limit`;
- `offset`;
- `load_rank_absolute`;
- `historical_serp_mode`;
- exact ordered `order_by`.

The persisted `request_*` context columns must agree exactly with that verified request.

The Capture `result_context` exposes provider result testimony only:

- `target` as exact state/value;
- `location_code` as exact state/value;
- `language_code` as exact state/value;
- `se_type` as exact state/value;
- provider `total_count`;
- provider `items_count`.

Do not add `complete`, `truncated`, `first_page`, `coverage_percent`, `corpus_exhausted`,
`has_more`, or an inferred provider continuation flag. Do not require arithmetic agreement
between `total_count`, aggregate buckets, corpus count, semantic fact counts, or rank systems.

Recipe v1 **does** require provider `items_count` to equal the number of returned-item
occurrence rows because RANK-05 creates exactly one occurrence for each returned provider
item. That equality is an Observatory persisted-structure invariant, not a claim that
`items_count == total_count`.

The frozen RANK-03 Capture is a golden `items_count=100`, `total_count=248`, request
`limit=100`, `offset=0` example. Those numbers are fixture facts, not production constants.

### 7. Corpus metrics projection

`corpus_metrics.v1` identity is exact:

    requested_target + aggregate_family + rank_system

Every admitted Recipe-v1 Capture must contain the complete cross-product of five aggregate
families and two rank systems: exactly ten corpus semantic parents, including all-zero
families and a successful zero-returned-item result. Collect
`(aggregate_family, rank_system)` and require exact set equality with that ten-element
cross-product, with no duplicate or missing combination.

Each typed corpus fact should expose:

- `observation_kind` and `within_capture_identity`;
- `requested_target`;
- `aggregate_family`;
- `rank_system`;
- a typed `position_buckets` object containing all twelve persisted bucket counts;
- a typed `movement_counts` object containing provider `is_new`, `is_up`, `is_down`, and
  `is_lost` aggregate counts;
- `count`, `etv`, and `estimated_paid_traffic_cost` as state/value testimony;
- clickstream ETV/gender/age state-only testimony.

For `rank_absolute`, count/ETV/cost remain Recipe-defined `inapplicable` with null values.
Never synthesize them from `rank_group`. The two rank systems remain independently stated
provider answers even when arithmetic appears reconcilable.

For `rank_group`, the converse is also exact Recipe-v1 authority: `count_state` is exactly
`stated`; `etv_state` and `estimated_paid_traffic_cost_state` are each only
`stated|json_null|absent`. `inapplicable` and `not_requested` are invalid on those rank-group
fields even though the generic SQL state CHECK would accept them.

Aggregate movement fields are provider counts. Their names do not make them booleans or
Capture-to-Capture deltas.

### 8. Ranked placement projection

`ranked_result.v1` uses accepted placement identity A:

    requested_target + keyword + serp_item_type + rank_group + rank_absolute

Exact URL is content, not identity.

Each typed placement fact should preserve every RANK-05 persisted content column and group
them according to their source-local provider structure:

- top-level identity axes above;
- `ranked_element` testimony: `se_type`, `check_url`, `se_results_count`, Ranked-element
  keyword difficulty, `is_lost`, ordered `serp_item_types`, current update clock, previous
  update clock, each with exact state/value semantics;
- `serp_item` testimony: required exact URL plus all persisted state/value fields for
  provider `se_type`, position text, xpath, domain, main domain, website name, relative URL,
  title, description, image/video/featured-snippet/malicious/AMP booleans, ETV, estimated
  paid traffic cost;
- `breadcrumb_state`, `pre_snippet_state`, and `highlighted_state` only — their text values
  remain Evidence-only under [CHAZ] Product Option 1;
- clickstream ETV state only;
- `rank_changes` enclosing state plus all persisted member state/value testimony;
- `rank_info` enclosing state plus page-rank and main-domain-rank member state/value
  testimony;
- state-only `about_this_result`, `backlinks_info`, `extended_snippet`, `links`, and
  `rating` testimony.

When an inline `rank_changes` / `rank_info` object is not stated, member states remain exact
Recipe-v1 `inapplicable`; do not erase those persisted states merely because there is no
enclosing value object.

Do not normalize URLs/hosts/domains, infer Page identity, or join these rows to Google Organic.
The same URL at two different accepted placements can be two facts. Same identity axes with
different URL/content is integrity disagreement, not "latest wins".

### 9. Ranked-local keyword-data projection

`keyword_data.v1` identity is exact:

    requested_target + keyword

It is Ranked-local testimony. Do not reuse Keyword Overview or Related Keywords kinds,
tables, response models, or semantic identity merely because nested provider JSON is similar.

The typed fact must expose every persisted RANK-05 keyword-data parent/child column:

- parent location/language/`se_type` state/value testimony;
- enclosing states for keyword info, keyword properties, average backlinks, search intent,
  and keyword SERP info;
- a fully typed child object exactly when the enclosing state is `stated`;
- keyword-info current demand, competition/CPC/bids/categories, monthly-series state,
  search-volume-trend state, signed trend member state/value testimony, keyword-info-local
  `se_type` state/value, and keyword-info source-local clock;
- properties including its own `se_type` state/value, exact provider `core_keyword`, algorithm
  label, keyword difficulty, detected language, and another-language testimony;
- exact decimal backlink averages plus their own `se_type` state/value and provider clock;
- search intent / ordered foreign intent plus its own `se_type` state/value and provider clock;
- keyword-SERP-local `se_type` state/value, URL, ordered item types, result count, and
  independent current/previous keyword-SERP clocks;
- Bing-normalized state and both request-disabled clickstream states.

Decimals serialize as exact plain decimal strings with no binary-float round trip. Ordered
arrays preserve order and duplicates.

Current `keyword_info.search_volume` is current provider testimony and must never be derived
from or replaced by the newest monthly fact.

### 10. Monthly Data-Period projection and occurrence binding

`monthly_search_volume.v1` identity is exact:

    requested_target + keyword + year + month

Expose each monthly semantic fact with:

- `observation_kind` / identity;
- exact requested target and keyword;
- `data_period: {year, month}`;
- nonnegative `search_volume`;
- complete ordered `occurrences: [{item_index}, ...]`.

Every monthly parent must have at least one occurrence. Every occurrence index must resolve
to an existing returned-item occurrence whose linked keyword-data parent has the monthly
fact's exact keyword. The matching Ranked keyword-data fact must exist, its `keyword_info`
must be stated, and its persisted `monthly_searches_state` must be stated. Do **not** require
the converse: a stated provider `monthly_searches: []` is valid Recipe-v1 testimony and yields
zero monthly semantic facts.

Equal duplicate monthly testimony may therefore appear once semantically with multiple item
occurrences. An occurrence index is never part of monthly identity.

`(year, month)` is Data Period only. It is not Capture time, a provider clock, recurrence,
or current search volume.

### 11. Returned-item occurrence bridge

Expose `item_occurrences[]` as exact typed subordinate testimony with every persisted bridge
column:

- `item_index`;
- `ranked_result_identity`;
- `ranked_result_kind`;
- `keyword_data_identity`;
- `keyword_data_kind`;
- `item_se_type`.

`item_index` values are globally unique and dense `0..n-1`, where
`n == result_context.items_count`. Presentation is `item_index` ascending.

Every occurrence must resolve to exactly one existing Ranked placement parent and exactly one
existing Ranked keyword-data parent in the same Capture/Recipe. The linked parents must carry
the same exact keyword. Every placement parent and every keyword-data parent must be reachable
from at least one returned-item occurrence; duplicate semantic testimony may therefore have
multiple occurrence rows.

`item_se_type` is exact provider item testimony and must be exactly `google`; the persisted
column has no SQL enum CHECK. Likewise, every stated `*_se_type` value in Ranked parent/child
testimony must equal `google`. These are Recipe-v1 integrity checks, not cross-surface engine
identity.

### 12. Observation-envelope complete set and count semantics

For every semantic parent, first require its stored `requested_target` to equal the **verified
Attempt target**. Then recompute identity with `observation_identity(...,
RANKED_KEYWORDS_RECIPE)` using that verified Attempt target plus the row's remaining persisted
identity axes. Never recompute from a row's own self-claimed target; changing both the stored
target and stored identity together must not become a false green.

Every generic `observation_envelopes` row for the Capture/Recipe must carry the verified
`attempt_id`, provider `dataforseo`, the exact Ranked adapter contract, and an
`observation_kind` in the exact four-kind Recipe-v1 set. Reject duplicate
`(within_capture_identity, observation_kind)` keys. No foreign key currently constrains the
envelope Attempt/provider/adapter columns to the cited Capture.

The union of the four semantic-parent `(within_capture_identity, observation_kind)` sets must
equal the complete generic `observation_envelopes` set for the Capture/Recipe, with no
duplicate keys or unknown kind.

`capture_outcome.observation_count` equals that semantic envelope cardinality:

    10 corpus metrics
    + distinct ranked-result semantic parents
    + distinct Ranked keyword-data semantic parents
    + distinct monthly semantic parents

It does **not** count provider items, item occurrences, monthly occurrences, provider
`items_count`, provider `total_count`, URLs, keywords, or rank buckets.

The frozen RANK-03 Capture's `1410` envelopes are a golden consequence only:

    10 + 100 + 100 + 1200 = 1410

Do not encode `1410`, `100`, `1200`, or `248` as general read invariants.

### 13. Ranked zero-item success is admitted, not admitted-empty

Recipe v1 never emits `observation_admitted_empty` because successful parser testimony
always includes the aggregate structures and therefore ten corpus Observations.

A synthetic successful result with `items=[]`, `items_count=0` must be representable as:

- `capture_outcome.classification = observation_admitted`;
- `observation_count = 10`;
- exactly ten corpus facts;
- zero ranked results;
- zero keyword-data facts;
- zero monthly facts;
- zero item/monthly occurrences;
- one valid result context.

Outer empty history is different again: it means no matching admitted Capture document under
this exact target and Recipe. It does not distinguish never measured, failed, unresolved, or
non-admitted activity.

### 14. Four-pillar time disclosure

Preserve the accepted Ranked four-pillar model in response shape and OpenAPI wording:

1. acquisition provenance — `authorized_at`, `request_started_at`, `transport_ended_at` from
   verified Evidence;
2. Data Period — monthly `{year, month}` only;
3. SERP/placement clocks — Ranked-element current/previous clocks and keyword-SERP
   current/previous clocks remain separate source-local paths;
4. enrichment clocks — keyword-info, avg-backlinks, and search-intent clocks stay inside
   their own structures.

No universal `last_updated`, `provider_update_time`, or synthetic event time is allowed.
Provider duration strings are not timestamps. Movement, `is_lost`, previous rank, and
provider clocks are provider comparison testimony, not Observatory history deltas.

### 15. Field-state and Evidence-only discipline

Use strict Ranked-local models with `extra="forbid"` and preserve the applicable Recipe-v1
state domain per persisted column. Do not trust the generic SQL field-state CHECK as proof
that every token is valid for every Ranked column.

Implementation must enforce and tests must cover the exact applicable domains for:

- ordinary optional state/value fields;
- rank-absolute `count`/ETV/cost exact `inapplicable` state and the rank-group converse
  (`count_state=stated`; group ETV/cost only `stated|json_null|absent`);
- clickstream request-disabled state-only fields;
- Bing normalized state;
- unsupported null-only child states;
- Product Option 1 state-only prose fields;
- inline-object member `inapplicable` coupling when `rank_changes`, `rank_info`, or
  `search_volume_trend` is not stated.

A value/state pair exposes `{state, value}` with value non-null exactly when state is
`stated`. State-only testimony exposes the exact lower-case state token and invents no value.
Enclosing child structures expose the enclosing state plus the typed child only when stated.

Recipe-v1 applicable state domains are narrower than SQL and must be rejected when violated:

- ordinary optional provider fields: `stated|json_null|absent`;
- corpus `rank_group.count_state`: exactly `stated`;
- corpus `rank_absolute` count/ETV/cost: exactly `inapplicable`;
- clickstream-disabled loci: exactly `not_requested`;
- unsupported null-only Ranked children and Bing-normalized state: `absent|json_null` only;
- inline `rank_changes`, `rank_info`, and search-volume-trend members: ordinary optional
  states only when the enclosing object is stated, otherwise exactly `inapplicable`.

Product Option 1 prose state-only fields may be `stated|json_null|absent`; only their text
values are withheld.

Do not re-read raw provider prose and promote it around the Recipe. `breadcrumb`,
`pre_snippet`, and `highlighted` text values remain Evidence-only. Task echo, task/root cost,
durations, UUID/path, provider version/status, and unsupported populated child schemas remain
Evidence/parser testimony outside this API contract.

### 16. Deterministic inner presentation is not identity

Accepted deterministic presentation:

- corpus metrics: accepted aggregate-family order
  `organic, paid, featured_snippet, local_pack, ai_overview_reference`, then rank-system
  presentation `rank_group, rank_absolute`, then identity tie-break;
- ranked results: `keyword, serp_item_type, rank_group, rank_absolute, identity` ascending;
- keyword data: `keyword, identity` ascending;
- monthly: `keyword, year, month, identity` ascending;
- item occurrences: `item_index` ascending;
- monthly occurrences inside a fact: `item_index` ascending.

These are API presentation rules only. Provider array order survives independently in
`item_occurrences`. Outer `order=desc` reverses Capture history only and never reverses inner
semantic collections. The ranked-result presentation order is deliberately not the frozen
provider `order_by=rank_group,asc`; any coincidence in one Capture is not provider-order echo.

### 17. Measurement Outcomes and Holdings are not RANK-06 scope

Current generic Outcomes/Holdings models are keyword-shaped and currently implement only the
accepted Keyword Overview / Google Organic / Search Mentions D14 resources. Related Keywords,
Target Metrics, and Historical demonstrate that an admitted-history API can close a surface
slice without simultaneously adding sibling Outcomes/Holdings.

Therefore the smallest RANK-06 boundary adds **admitted history only**. Do not modify
`provider_outcomes.py`, `provider_holdings.py`, or add Ranked `/outcomes` / Holdings routes in
this ticket.

The later seven-surface MVP closeout must document this exact availability gap and may propose
a separately reviewed Ranked Outcomes/Holdings ticket only if the Strategy-consumer fidelity
review shows it is a material MVP blocker. Do not scope-creep preemptively.

Ranked history OpenAPI must disclose the gap positively: empty admitted history cannot tell an
API-only consumer whether the target was never measured, failed, unresolved, or merely has no
admitted Capture under the resolved Recipe because Ranked Outcomes/Holdings are not exposed in
RANK-06.

### 18. Existing provider Attempt audit should recognize Ranked

`GET /v1/attempts/{attempt_id}` is the existing provider audit/provenance resource. Current
`api.py` does not include Ranked in `_PROVIDER_ATTEMPT_ADAPTERS`.

RANK-06 should add the exact Ranked adapter to that routing set so a Ranked Attempt uses the
existing generic provider Attempt reader under selected/pinned Recipe semantics. This is
audit routing only, not a new Ranked data model.

This is an observable contract change for existing Ranked Attempt Evidence: today Ranked is
not in `_PROVIDER_ATTEMPT_ADAPTERS` and falls through the fixture path; after RANK-06, a
Ranked Attempt with no selected Recipe and no pin must return 503
`provider_recipe_not_selected`, while selected/pinned accepted v1 routes through the generic
provider Attempt resource. Prove that behavior explicitly.

## Resolved code-first review questions

The read-only Grok review answered all twelve questions below at exact review HEAD
`9aab9bf7c0884aa7c60f68276fc2d821285d35f5`; the Steward independently reconciled the
material findings in the lock above. They remain here as the review record, not as an open
implementation gate:

1. Is a dedicated Ranked outer envelope/local list-math helper truly the smallest safe way to
   expose `requested_target`, or is there a narrower reuse that does not modify or misname the
   established `requested_keyword` contract?
2. Are the proposed five Capture sibling collections the smallest lossless shape? In
   particular, confirm sibling `item_occurrences` and nested monthly occurrences preserve the
   RANK-05 parentage better than nesting/duplicating the bridge under one semantic family.
3. Enumerate the exact applicable Recipe-v1 state domain for every Ranked persisted state
   column. Which generic SQL-allowed tokens must the reader reject as relational damage?
4. Confirm the exact complete-set checks needed among corpus/placement/keyword/monthly semantic
   parents, all five keyword child relations, generic envelopes, item occurrences, monthly
   occurrences, context, Outcome, and verified Evidence.
5. Which cross-family reachability checks are required beyond foreign keys — especially
   item-occurrence keyword agreement and monthly -> keyword-data/monthly-series agreement?
6. Confirm the exact ten corpus family/locus cross-product is a Recipe invariant while all
   RANK-03 cardinalities are golden-only facts.
7. Verify `items_count == item_occurrence cardinality` is Recipe-v1 persisted-structure truth
   while no arithmetic involving `total_count`, buckets, ranks, or semantic-family counts is
   justified.
8. Verify the proposed deterministic inner ordering never changes identity and does not lose
   provider occurrence order.
9. Confirm every RANK-05 persisted consumer-meaningful column can be represented by the typed
   projection above, including all state-only fields and every independent clock. Identify
   any persisted column the draft accidentally omits or any proposed API field that would
   synthesize meaning not present in persistence.
10. Confirm the stored Recipe's exact four-kind order and six-class taxonomy and that
    `RANKED_KEYWORDS_RECIPE` remains imported from `google_ranked_keywords_derive.py`.
11. Confirm the exact implementation path ceiling below is sufficient and identify any
    schema-sensitive/Attempt-audit/selection test that genuinely requires a bounded edit.
12. Report any genuine Product question. Do not promote a code-answerable implementation
    choice into Product scope.

## Final implementation path ceiling

Expected production changes after final ticket acceptance and **separate explicit [CHAZ]
implementation authorization**:

- new `src/observatory/ranked_keywords_read.py`;
- `src/observatory/api.py` — Ranked history route, response model import, Ranked provider
  Attempt-audit routing only;
- new `tests/test_api_ranked_keywords.py`;
- `tests/test_api_attempts.py` only if needed for the Ranked Attempt-audit routing proof;
- `tests/test_provider_recipe_selection.py` only if a genuinely missing isolated
  selection/pinning proof cannot live in the new Ranked API test module;
- this RANK-06 ticket — Writer start/status/report only.

Do not modify:

- `provider_history.py` unless the code-first review proves the dedicated-target envelope
  approach is worse and the Steward explicitly reconciles that finding before implementation;
- `provider_recipe_selection.py`;
- `google_ranked_keywords_derive.py`;
- `dataforseo_google_ranked_keywords.py`;
- `migrate.py` or any schema;
- RANK-04 fixture bytes;
- `provider_outcomes.py` / `provider_holdings.py`;
- another provider reader;
- Evidence, backup, acquisition, or Strategy code.

## Required acceptance proofs

The eventual implementation must include bounded zero-network tests proving at minimum:

### Recipe / route / OpenAPI

- exact route and query names/bounds;
- `requested_target` is the outer subject and `requested_keyword` does not appear as the
  Ranked subject field;
- selected/pinned/503/404/409 Recipe behavior above;
- exact Recipe v1 literal identity, four-kind order, and six-class taxonomy;
- strict fully typed Ranked envelope and nested models with `extra="forbid"`;
- OpenAPI descriptions positively distinguish Capture history, provider counts, occurrence
  testimony, zero-item admitted success, all four time pillars, URL-as-content, and
  Evidence-only prose.

### Golden accepted Capture

Use the frozen RANK-04 Conformance fixture / accepted RANK-05 derive on disposable PostgreSQL
for a bounded golden content proof. Independently project expected JSON from verified Evidence
plus persisted rows; do not use the production reader to construct its own expected value.

The golden proof may assert frozen-Capture consequences such as:

- 10 corpus metrics;
- 100 ranked results;
- 100 keyword-data facts;
- 1200 monthly facts;
- 1410 Observation envelopes;
- 100 item occurrences;
- 1200 monthly occurrences;
- provider `items_count=100`, `total_count=248`;
- request `limit=100`, `offset=0`, exact order;
- independent rank systems/clocks and current-vs-monthly disagreement present in the fixture.

Those remain golden facts only.

### Column-completeness / losslessness

As RK-05's API predecessor does, independently discover the RANK-05 relations/columns from
PostgreSQL `information_schema` (or equivalently independent schema testimony) and prove that
every persisted consumer-meaningful column is either:

- exposed in the typed Ranked API projection; or
- one of the explicitly accepted relational/provenance key columns validated but not
  redundantly surfaced.

The production reader's own column tuple must not be the only oracle for that proof.

The closed allowance for validated-but-not-redundantly-surfaced relational/provenance columns
is: `capture_id`, `derivation_version_id`, `within_capture_identity`, `observation_kind`, plus
result-context `attempt_id` and result-context duplicated `requested_target`. The proof must
not contain an open-ended "other relational column" escape hatch.

### Semantic / occurrence integrity

Synthetic tests must cover at least:

- identity-axis tamper for each of the four kinds, including self-consistent stored-target +
  identity substitution that must still fail against verified Attempt target;
- missing/extra/unknown Observation envelope;
- foreign-Attempt, foreign-provider, or foreign-adapter Observation envelope;
- missing/extra corpus/placement/keyword/monthly parent;
- deleted Ranked result-context row while matching subject-bearing semantic parents survive;
- missing/extra keyword child row and enclosing-state disagreement;
- corpus family/rank-system missing, duplicate, or extra combination;
- rank-group `count_state` not `stated`, rank-group ETV/cost `inapplicable` or
  `not_requested`, and rank-absolute count/ETV/cost not exactly `inapplicable`;
- item occurrence missing/extra/duplicate/non-dense index;
- item occurrence `item_se_type != google` and stated child/parent `*_se_type != google`;
- item occurrence referencing the wrong placement or keyword-data identity;
- item occurrence linking parents with different keywords;
- semantic parent with no required item occurrence;
- monthly occurrence missing/extra/wrong item index;
- monthly occurrence bound to a different returned keyword;
- monthly fact with no matching keyword-data parent, unstated keyword-info, or unstated
  `monthly_searches_state`;
- stated-empty `monthly_searches` with zero monthly facts remains valid and does not 409;
- wrong applicable state token, value/state disagreement, unstated inline-object member state
  not `inapplicable`, unsupported child incorrectly `stated`, or clickstream not
  `not_requested` where Recipe v1 freezes it;
- URL/content tamper under unchanged placement identity;
- source-local clock disagreement remains valid testimony rather than reconciliation;
- result echo target/locale disagreement remains visible valid testimony;
- persisted request context disagreement with verified Attempt returns 409;
- foreign/missing Attempt or Capture Evidence returns 409;
- matching context with missing/foreign/non-admitted Outcome returns 409, including a second
  Capture Outcome under a foreign Attempt;
- Outcome `observation_count` mismatch returns 409;
- damage in a matching Capture outside the returned outer `limit` still returns 409.

For FK-protected damage cases, tests may use the established isolated-PostgreSQL technique
`SET session_replication_role = replica` to disable referential triggers while leaving CHECK
constraints active. This is a test construction seam only, not a production write path.

### Zero-item success

Synthetic zero-item provider success must return one admitted Capture with exactly ten corpus
facts and no other semantic/occurrence facts. It must not produce
`observation_admitted_empty` and must not be mistaken for empty outer history.

### Selection / audit isolation

- derive registers Ranked Recipe v1 but does not auto-select it;
- selecting Ranked does not alter sibling adapter selections;
- a Ranked provider Attempt routes through the existing `/v1/attempts/{attempt_id}` provider
  audit path;
- with no Ranked selection and no pin, that routed Attempt returns 503
  `provider_recipe_not_selected`; selected/pinned accepted v1 succeeds;
- an unrelated valid Ranked Attempt/Capture in the same EvidenceStore never supplies
  request/provenance for another Capture.

### Read-only / network boundary

Tests perform zero provider/DNS/public-network activity, require no credentials, mutate only
isolated test Evidence/PostgreSQL, and prove read paths leave provider selections, Outcomes,
Observation rows, Ranked relations, and Evidence unchanged.

## No Product question remains

The read-only Grok review and Steward reconciliation found no unresolved Product choice.
RANK-05 already settled the material semantic questions: four kinds, placement identity A,
URL-as-content, independent rank systems, Ranked-local keyword enrichment, monthly Data Period
identity, whole-unit conflict behavior, Product Option 1 prose retention, zero-item semantics,
and the four-pillar time model.

The question-resolution gate is therefore complete for RANK-06. Implementation remains
blocked until [CHAZ] separately designates the Writer and explicitly authorizes implementation
from the exact clean reconciled-ticket HEAD. That authorization still grants no provider call,
credentials, Evidence mutation, spend, amend, or push.

## Implementation record — Writer lane

[CHAZ] explicitly authorized [CLAUDE] to implement this reconciled ticket from
`dcbe91365d89e18d171ea929e3b7dd1595b1d261`. The starting gate was verified before any edit:
branch `main`, HEAD exactly that SHA, clean working tree. No authorization-only commit was
made; the single implementation commit is a direct child of `dcbe913`.

### Changed paths

- `src/observatory/ranked_keywords_read.py` — new. Ranked-local typed models, applicable
  state domains, complete-set verification, and the dedicated outer envelope.
- `src/observatory/api.py` — Ranked history route, response-model import, and the exact
  Ranked adapter added to `_PROVIDER_ATTEMPT_ADAPTERS`. No other route changed.
- `tests/test_api_ranked_keywords.py` — new; 235 tests.
- this ticket — Writer status and implementation report only.

Nothing else was touched. `provider_history.py`, `provider_recipe_selection.py`,
`google_ranked_keywords_derive.py`, `dataforseo_google_ranked_keywords.py`, `migrate.py`,
the RANK-04 fixture bytes, `provider_outcomes.py`, `provider_holdings.py`, and every sibling
provider reader are byte-identical to the start commit. No schema or migration changed, so
no `PRE_*` migration baseline moved and no sibling test module needed a retarget.
`tests/test_api_attempts.py` and `tests/test_provider_recipe_selection.py` were **not**
edited: neither asserts an exhaustive route, path, or adapter set, and the Attempt-audit and
selection-isolation proofs live in the new Ranked module.

### Reconciled defects, as implemented

1. **Verified subject authority.** Every semantic parent's stored `requested_target` is
   compared to the verified Attempt target first, and identity is recomputed with
   `observation_identity(..., RANKED_KEYWORDS_RECIPE)` from that verified target plus the
   row's remaining axes. Rewriting a row's stored target *and* its identity together stays
   internally consistent and is still 409.
2. **Reverse subject-membership probe.** Distinct Capture ids carrying the queried
   `requested_target` are collected from `ranked_keywords_corpus_metrics`,
   `_ranked_results`, `_keyword_data`, and `_monthly_search_volume` and required to equal the
   context-anchored candidate set before sorting or limiting. Deleting only the result-context
   row is 409 rather than silent shrinkage of `total_matching`.
3. **Envelope provenance.** Envelope `attempt_id`, `provider`, `adapter_contract`, and kind
   are checked explicitly, with a duplicate-key guard. No foreign key constrains those columns.
4. **Exact-one Capture Outcome.** A separate probe over `(Recipe v1, capture_id)` requires
   exactly one row citing the verified Attempt. `outcomes_identity` is unique per Attempt, so
   a second Outcome for the same Capture under a foreign Attempt is legal SQL and is proved
   to fail.
5. **Rank-group converse.** The schema CHECK constrains only the rank-absolute direction, so
   the reader additionally requires `count_state = stated` and ETV/cost in
   `stated|json_null|absent` under `rank_group`.
6. **`se_type`.** Every stated `*_se_type` and every occurrence `item_se_type` must be
   exactly `google`; the occurrence column has no SQL enum CHECK.
7. **Stated-empty monthly series.** The monthly-to-keyword-data rule is one-way; a stated
   `monthly_searches: []` yielding zero monthly facts reads normally.
8. **Local outer-key closure.** A module-local twelve-key `RANKED_OUTER_HISTORY_KEYS` set is
   asserted before model validation, preserving the guard the shared helper provides without
   renaming the published `requested_keyword` contract.
9. **Keyword-first presentation.** `ranked_results` presents by keyword, SERP item type, then
   both rank axes, and a test proves the result differs from the frozen provider
   `order_by=rank_group,asc`.
10. **Attempt-audit behavior change.** Ranked in `_PROVIDER_ATTEMPT_ADAPTERS` moves a Ranked
    Attempt from the fixture fall-through to the generic provider reader; with no selection
    and no pin that is now 503 `provider_recipe_not_selected`. Selected and pinned success are
    both proved.

### Response shape

One Capture document exposes verified request testimony, the admitted Capture Outcome,
provider result context, and five sibling collections: `corpus_metrics[]`, `ranked_results[]`,
`keyword_data[]`, `monthly_search_volume[]`, and `item_occurrences[]`. Monthly occurrences
nest under their monthly fact; the returned-item bridge stays a sibling because one provider
item names two semantic parents. `ranked_element` and `serp_item` are separate source-local
objects, and `rank_changes`, `rank_info`, and `search_volume_trend` each expose their
enclosing state beside their persisted members so the `inapplicable` coupling is visible.

### Verification

- `uv run pytest -q tests/test_api_ranked_keywords.py` — **235 passed, 1 warning** in
  325.82s.
- `uv run pytest -q tests/test_api.py tests/test_api_attempts.py
  tests/test_api_related_keywords.py tests/test_provider_recipe_selection.py
  tests/test_dataforseo_google_ranked_keywords_derive.py` — **320 passed, 1 warning** in
  305.08s.
- `uv run ruff check .` — all checks passed.
- `uv run mypy` — **14 errors in 5 files (checked 96 source files)**, message-for-message and
  file-for-file identical to the `dcbe913` baseline of 14 errors in 5 files across 94 files.
  Zero new errors; only the checked-file count moved 94 → 96 for the two new modules. No
  inherited error was repaired.

The single warning in both runs is the inherited Starlette `TestClient`/`httpx` deprecation.

The golden proof derives the frozen RANK-04 Conformance fixture on disposable PostgreSQL and
compares the served document to an expected value built by this module's own projector, which
discovers relations and columns from `information_schema` rather than from the reader's
tuples. It confirms 10 corpus + 100 ranked results + 100 keyword-data + 1200 monthly = 1410
Observation envelopes, 100 returned-item occurrences, 1200 monthly occurrences, provider
`items_count=100` against `total_count=248`, request `limit=100`/`offset=0`, 57 unique URLs
across 100 distinct placements, and the 248-versus-244 organic rank-system disagreement, none
of which is encoded as a production invariant.

### Candid assessment

**Strongest parts.** The independent projector is the load-bearing proof: it is built from
schema testimony and hard-coded grouping rules, so a shared bug between it and the reader is
unlikely to manufacture a green. The state-domain enumeration and the two reconciled
membership defects (verified-target anchoring, reverse subject probe) each have a dedicated
adversarial test that fails without the corresponding guard.

**Weakest parts.** (a) The reverse subject-membership probe closes the single-row context
deletion, but the disclosed residual limit stands: deleting the context row *and* all four
subject-bearing parent families leaves no subject-bearing row from which an exact-subject
route could discover the Capture. That is the deferred Ranked Outcomes/Holdings boundary, not
a RANK-06 defect. (b) The probe adds four unindexed `requested_target` scans per read; that is
the same low-volume bridge posture D14 already accepts, and it will need an index before
F12-scale volume. (c) `items_count == occurrence cardinality` rests entirely on the RANK-04
parser rejecting `items_count != len(items)`; unlike Related Keywords there is no persisted
`derived_returned_item_count` second witness, so a future parser change would silently break
that equality's justification. (d) The `parent[0] != "stated"` monthly guard is unreachable in
practice because the child-presence check fires first; it is retained as a cheap defense.

**Deliberate duplication.** The ~25 lines of outer list math duplicated from
`provider_history.history_list_response` are intentional. Ranked is the first non-keyword
subject; if a third arrives, that helper should gain a subject-name parameter rather than
accumulate a third local copy.

**No false-green risk found in the URL test.** `test_url_is_content_not_identity` deliberately
asserts a 200: rewriting a stored URL changes no identity and the reader cannot detect it.
Same-identity URL contradiction is a RANK-05 derive-time whole-unit rejection and cross-Capture
URL comparison is downstream analysis; neither is a read-time check. The test documents that
boundary rather than pretending to enforce one.

No provider call, credential access, public-network activity, Evidence mutation, fixture
change, schema change, pagination, second acquisition, clickstream enablement, Measurement
Outcomes, Holdings, Strategy behavior, amend, rebase, or push was performed.

## Steward implementation review — remediation required

Independent [GPT] Steward review of implementation commit
`e7e883a856bdffff380048ac8c094d2ad6095cd8` against authorized parent
`dcbe91365d89e18d171ea929e3b7dd1595b1d261` found one blocking contract mismatch and no
second blocking defect in the reviewed load-bearing paths.

The implementation correctly preserves the reconciled target/identity, reverse-membership,
Outcome, envelope-provenance, corpus cross-product, state-domain, `se_type`, occurrence,
monthly, zero-item, ordering, Recipe-kind/taxonomy, and Attempt-audit boundaries. The Writer's
ticket-scoped checks are accepted as implementation evidence; the Steward did not execute
repository tests through MCP.

### Blocking finding — accepted-v1 Recipe adapter metadata damage must be 409

The final ticket explicitly requires tampered accepted-v1 Recipe provider/adapter metadata to
return HTTP 409 `evidence_integrity_failure`. Provider-column damage reaches the Ranked reader
and is correctly rejected as 409. Adapter-column damage does not: generic
`resolve_provider_recipe()` rejects the damaged registration before `_load_validated_v1_recipe`
can inspect it, yielding 503 on the selected path or 404 on an explicit accepted-v1 pin.

`tests/test_api_ranked_keywords.py::test_recipe_adapter_column_damage_serves_no_history`
currently accepts `{404, 409, 503}`, which is a false green against the locked contract.

Remediation is bounded to the Ranked reader/tests/ticket. Preserve generic Recipe-selection
semantics for sibling surfaces. Add the smallest Ranked-local pre-resolution integrity guard
needed so that when the exact accepted Ranked v1 registration is the selected Recipe, or the
caller explicitly pins that exact accepted v1 digest, a present registration row whose
stored adapter metadata disagrees with the accepted Ranked adapter is classified as
`IntegrityError` and therefore HTTP 409. Wrong-adapter pins for other registered Recipes and
registered same-adapter non-v1 Recipes must retain their accepted 404 behavior; true no-selection
must retain 503.

Replace the permissive adapter-damage proof with exact selected and pinned 409 proofs. Run only
the bounded affected RANK-06 tests/checks required for remediation, create one child commit,
do not amend, and do not push.

### Final closure gates after remediation

RANK-06 must not close immediately after the remediation commit. The required final sequence is:

1. [GPT] independently reviews the committed remediation and accepts or returns it;
2. [GROK] performs one final independent **read-only adversarial review** of the complete
   accepted RANK-06 implementation, including the remediation, and returns `READY` or a
   bounded finding report;
3. [GPT] reconciles any Grok findings against repository authority; any required code change
   returns to [CLAUDE], the existing Writer, as a bounded remediation rather than opening a
   second Writer lane;
4. once code review is settled, [CHAZ] supplies the final full-repository `uv run pytest -q`
   integration result at the exact candidate closure commit;
5. only then may [GPT] record RANK-06 closure.

The final Grok review performs no mutation, provider/network call, credential access, Evidence
mutation, spend, amend, or push. Full-suite integration remains [CHAZ] closure evidence, not a
Writer or Grok task.

## Explicit out of scope

- another RANK-03/provider request, retry, pricing/account call, credentials, spend, or
  Evidence mutation;
- Ranked Measurement Outcomes or Holdings;
- provider offset/second-page acquisition or provider pagination;
- an outer API cursor/offset or retrieval beyond the existing maximum 100 Capture documents;
- canonical Page/domain/site/brand/topic identity;
- URL normalization, redirect resolution, apex/`www` equivalence;
- cross-surface semantic unification with Google Organic, Keyword Overview, or Related
  Keywords;
- Capture-to-Capture rank/movement calculation;
- a universal provider update time or generic `last_updated`;
- clickstream-enabled acquisition;
- exact-page/subdomain target adapter expansion;
- generic Labs reader framework;
- Strategy scoring, opportunity, recommendation, prioritization, report, or consumer-owned
  state;
- F12 recurring acquisition;
- Cloudflare R2/F6 implementation — sequenced after RANK-06 closure;
- MVP seven-surface provider-testimony closeout — sequenced after routine F6 proof.

## One eventual implementation must prove

One API-only consumer can select or pin the exact accepted Ranked Recipe and read a bounded,
fully typed history of exact requested-target Capture documents whose corpus, placement,
Ranked-local keyword, monthly Data-Period, and occurrence testimony is completely checked
against rebuildable PostgreSQL and verified Evidence before limiting — while keeping provider
corpus counts separate from returned rows, preserving both rank systems and all four time
pillars, retaining exact URL strings without canonical Page semantics, and exposing no
Strategy interpretation or Evidence-only prose value.
