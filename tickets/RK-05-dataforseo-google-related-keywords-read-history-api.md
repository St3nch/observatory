# RK-05 — DataForSEO Google Related Keywords Recipe selection and admitted-history API

**Status:** draft — independent read-only technical review required before implementation  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** none; RK-04 closed  
**Draft base:** `be194e99573d6c6f8a9ecb12d23d35c563bce446`  
**Pre-implementation reviewer:** [GROK] independent read-only code-first review  
**Product direction:** complete the bounded Related Keywords MVP vertical slice without another provider call  

## Purpose

Complete the first consumer-readable Related Keywords fact slice for the exact adapter:

    dataforseo-labs-google-related-keywords-live-paid-probe-v1

RK-05 selects or pins the accepted RK-04 Recipe and adds one exact-subject admitted-history
route. One returned outer list member is one admitted Capture document containing verified
Attempt request testimony, provider result context, typed keyword-data testimony, monthly
Data-Period facts, provider-relatedness facts, and their occurrence testimony.

This is the consumer half of the Related Keywords vertical slice. It must expose RK-04 facts
without turning provider relatedness into a tree, `core_keyword` into canonical identity,
current search volume into a monthly fact, or structurally similar Keyword Overview fields
into cross-surface equivalence.

No provider exchange, credentials, spend, new Evidence, parser, Recipe, Derivation, schema,
migration, Measurement Outcomes, Holdings, Ranked Keywords, Strategy behavior, recurring
acquisition, or generic provider-read framework is authorized.

## Authority and accepted foundation

- VISION and VOCABULARY API-only consumer boundary, provenance, Evidence, Outcome,
  Observation, Derivation Recipe, Provider Update Time, and Data Period semantics;
- D2 and D3 — consumers use the versioned API; analysis/strategy remains downstream;
- D8 — Evidence integrity and verify-on-read;
- D11 — provider interpretation is Recipe-addressed and time-explicit;
- D12 — bounded Evidence proves observed testimony, not provider invariance;
- D14 — admitted history is distinct from Measurement Outcomes and Holdings; outer history
  lists disclose `total_matching`, `returned_count`, `limit`, deterministic `order`, and
  `has_more` without creating one universal fact body;
- PF-08 — adapter-aware Recipe selection/pinning and provider Attempt audit substrate;
- API-01 — shared outer admitted-history list semantics and verify-before-limit;
- AI-12 and AI-17 — newer fully typed, strict, surface-local history/OpenAPI precedent;
- RK-01 through RK-04 — exact acquisition contract, accepted live Evidence, strict parser,
  three-kind Recipe, twelve typed relations, complete-set persistence, and deterministic
  rebuild.

RK-04 closed at Steward commit:

    be194e99573d6c6f8a9ecb12d23d35c563bce446

Accepted Related Keywords Recipe v1:

    a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669

Canonical Recipe bytes: `2398`.

Exact Observation kinds, in Recipe order:

1. `dataforseo.google.related_keywords.keyword_data.v1`
2. `dataforseo.google.related_keywords.monthly_search_volume.v1`
3. `dataforseo.google.related_keywords.relationship.v1`

## Existing persistence facts

RK-04 already owns all persistence required by this ticket. RK-05 must not add another table,
index, projection, stored completeness marker, or read cache.

The twelve RK-04 relations are:

1. `related_keywords_keyword_data`;
2. `related_keywords_keyword_info`;
3. `related_keywords_keyword_properties`;
4. `related_keywords_avg_backlinks`;
5. `related_keywords_search_intent`;
6. `related_keywords_serp_info`;
7. `related_keywords_monthly_search_volume`;
8. `related_keywords_relationship`;
9. `related_keywords_keyword_data_item_occurrences`;
10. `related_keywords_monthly_item_occurrences`;
11. `related_keywords_relationship_occurrences`;
12. `related_keywords_result_context`.

Generic `provider_recipes`, `provider_recipe_selections`, `outcomes`, and
`observation_envelopes` already exist. Selection tests may change the operational selection
pointer only inside isolated disposable PostgreSQL. RK-05 must never select the operator's
live Recipe automatically.

## Frozen RK-02 / RK-04 facts for the golden API proof

The accepted Conformance fixture remains:

- `tests/fixtures/dataforseo_google_related_keywords_rk02.json`;
- 177,120 bytes;
- SHA-256 `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`;
- requested seed `conspiracy theories`.

Under Recipe v1 that Capture derives to:

- 81 keyword-data semantic parents: one seed locus plus 80 returned-item identities;
- 972 monthly semantic parents: 12 seed-locus points plus 960 returned-item points;
- 477 relationship semantic parents;
- 1530 Observation envelopes total;
- 80 returned-item keyword-data occurrences;
- 960 returned-item monthly occurrences;
- 477 relationship occurrences;
- child rows: keyword-info 81, properties 81, backlinks 60, intent 81, SERP 63;
- one result-context row.

These are frozen-Capture consequences only. API code must not use them as production
constants or provider invariants.

## Proposed exact route and query contract

Implement exactly:

    GET /v1/providers/dataforseo/google/related-keywords/history

Query:

- `requested_keyword` — required exact string, `min_length=1`;
- `derivation_version_id` — optional exact Recipe pin;
- `limit` — default 20, minimum 1, maximum 100;
- `order` — `asc` or `desc`, default `asc`.

Do not trim, case-fold, normalize, synonym-expand, replace with `core_keyword`, or treat a
relationship target as the requested subject. Add no depth filter, frontier filter, keyword
filter, current-volume filter, relationship cursor, outer offset/cursor, continuation token,
or undeclared query parameter.

The independent technical review must challenge whether `requested_keyword` should also carry
the adapter's 80-character upper bound at the HTTP schema. Do not add the RK-01 seed regex to
the query unless review proves that rejecting an impossible subject is preferable to an exact
empty-history miss.

## Recipe selection and stored-Recipe verification

Use the existing adapter-aware `resolve_provider_recipe` substrate for the exact Related
Keywords adapter.

- no selection and no pin → HTTP 503 `provider_recipe_not_selected`;
- selected Recipe → `recipe_resolution = selected`;
- accepted explicit pin → `recipe_resolution = pinned`;
- malformed, unknown, wrong-adapter, or unsupported Recipe pin → accepted HTTP 404 behavior;
- tampered/non-canonical/digest-disagreeing stored v1 Recipe bytes or relational metadata
  disagreement → HTTP 409 `evidence_integrity_failure` with no history envelope.

This route serves only the accepted RK-04 Recipe v1 identity above. A future Recipe that
changes identity, field semantics, kinds, or persistence must receive a separately reviewed
API contract rather than silently flowing through this v1 projection.

After resolution, independently verify the registered Recipe's provider, exact adapter,
canonical JCS bytes, digest, exact ordered three-kind list, and exact accepted Capture
classification vocabulary:

- `no_response`;
- `response_partial`;
- `transport_complete_non_admissible`;
- `provider_error`;
- `provider_envelope_rejected`;
- `reconciliation_failed`;
- `observation_admitted`;
- `observation_admitted_empty`.

## Membership and provenance

History membership is context-anchored, not envelope-anchored.

Load `related_keywords_result_context` rows for exact `requested_seed` and the resolved Recipe,
then LEFT JOIN the matching Capture Outcome on the full:

    (derivation_version_id, attempt_id, capture_id)

tuple.

Context exists only for admitted/admitted-empty Recipe-v1 Captures. Therefore a matching
context row with a missing Outcome, a foreign-Attempt Outcome, or any classification other
than `observation_admitted` / `observation_admitted_empty` is PostgreSQL integrity damage and
must return HTTP 409. Do not silently omit it and report empty history.

Rejected, provider-error, transport-failure, reconciliation-failure, unresolved Attempt-stage
activity, and other no-context activity remain outside normal history. RK-05 does not add
Measurement Outcomes or Holdings merely to expose those states.

## Verify every matching candidate before outer limit

Within one read-only PostgreSQL boundary, for every matching context candidate before sort or
limit:

1. resolve and validate Recipe v1;
2. verify the exact committed Attempt through `EvidenceStore.read_attempt`;
3. require provider `dataforseo` and the exact Related Keywords adapter;
4. validate Attempt parameters with existing public
   `validate_related_keywords_http_parameters`;
5. verify the exact committed Capture through `EvidenceStore.read_capture`, including parent
   and referenced body integrity;
6. require the same provider/adapter on Capture and exact parent Attempt identity;
7. require persisted request/result context to agree with the verified Attempt wherever
   context duplicates request testimony;
8. perform the complete PostgreSQL semantic/occurrence checks below;
9. compute `total_matching` from the complete verified Capture set;
10. sort by `(request_started_at, capture_id)`;
11. reverse the complete order for `order=desc` when requested;
12. apply `limit` to whole Capture documents only;
13. compute `returned_count` and `has_more` using the shared outer-list semantics.

Any matching damage, including a later Capture outside `limit=1`, yields HTTP 409 with no
partial normal history envelope.

## Verified Attempt request block

Each Capture document exposes one closed `request` object from the verified Attempt, not from
task echo or result echo:

- `keyword` — exact requested seed;
- `location_code` — frozen 2840;
- `language_code` — frozen `en`;
- `depth` — frozen 3;
- `limit` — frozen 1000;
- `offset` — frozen 0;
- `order_by` — exact ordered one-member array
  `keyword_data.keyword_info.search_volume,desc`;
- `include_seed_keyword` — true;
- `include_serp_info` — true;
- `include_clickstream_data` — false;
- `ignore_synonyms` — false;
- `replace_with_core_keyword` — false.

The API/OpenAPI may use Literals for frozen request fields, but the reader must still run the
accepted Attempt parameter validator. Literals document the closed adapter; they do not
replace Evidence validation.

## Proposed fully typed Capture document

Use a dedicated strict Related Keywords history envelope in a new surface-local reader. Do
not expose nested Capture bodies merely as `dict[str, Any]` and do not create one universal
provider fact schema.

One Capture contains exactly:

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
- `keyword_data`;
- `monthly_search_volume`;
- `relationships`.

All nested models must be strict and `extra="forbid"`. Exact 64-hex identities retain their
bounds/patterns. Decimal-capable PostgreSQL `NUMERIC` values must serialize without any
binary-float round trip; use an exact decimal string convention consistent with accepted
provider readers.

### Capture Outcome

History permits exactly:

- `observation_admitted` with `observation_count > 0`;
- `observation_admitted_empty` with `observation_count == 0`.

`observation_count` is Observation-envelope cardinality only. It is not provider
`total_count`, provider `items_count`, returned-item count, monthly point count, relationship
occurrence count, graph node count, or completeness.

### Result context

Expose the RK-04 context testimony with clear grain labels:

- provider result `seed_keyword`;
- result `location_code`, `language_code`, and `se_type` as exact state/value fields;
- provider `total_count` and `items_count` independently;
- result-level `seed_keyword_data_state`;
- `derived_returned_item_count` explicitly labeled Observatory-derived;
- `derived_relationship_occurrence_count` explicitly labeled Observatory-derived.

Do not repeat the entire verified Attempt request inside result context; the Capture `request`
block is the request authority. `total_count == items_count` in RK-02 is one-Capture testimony,
not a provider completeness rule.

For every admitted/admitted-empty Recipe-v1 Capture, parser/Derivation authority permits the
reader to require `items_count == derived_returned_item_count`. Do not require
`total_count == items_count`.

### Keyword-data family

Each semantic keyword-data parent contains at minimum:

- `observation_kind`;
- `within_capture_identity`;
- `requested_seed`;
- `locus` exactly `seed_keyword_data` or `returned_item`;
- exact provider `keyword`;
- location/language/se_type state/value testimony;
- enclosing states for keyword-info, properties, backlinks, intent, and SERP;
- Bing-normalized state;
- clickstream-normalized state;
- clickstream-keyword-info state;
- optional typed `keyword_info`, `keyword_properties`, `avg_backlinks`, `search_intent`, and
  `serp_info` objects only when the corresponding enclosing state is STATED;
- complete ordered returned-item `occurrences` for `returned_item` locus; seed locus has an
  empty occurrence list because it is not an item-array occurrence.

The independent review must challenge the exact JSON wrapping convention for enclosing
object states. The semantic requirement is fixed: consumers must be able to distinguish
ABSENT, JSON null, STATED-empty/value, NOT_REQUESTED, and Recipe-defined INAPPLICABLE wherever
RK-04 persists those distinctions, and the API must not use child-row absence by itself as a
state signal.

`keyword_info` preserves exact current metrics, exact ordered/duplicate categories,
`monthly_searches_state`, `search_volume_trend_state`, signed trend member state/values, and
the structure-specific keyword-info update clock. Current `search_volume` is current provider
testimony and must never be computed from a monthly point.

`keyword_properties` preserves `core_keyword` state/value,
`synonym_clustering_algorithm`, difficulty, detected language, and other-language flag.
`core_keyword` is provider field testimony, not canonical identity, synonym equivalence, or a
relationship edge.

`avg_backlinks` preserves exact Decimal-capable values and its own update clock.
`search_intent` preserves open provider intent vocabulary, ordered/duplicate foreign-intent
array state/value, and its own update clock.
`serp_info` preserves exact `check_url`, ordered/duplicate SERP item types, result count, and
separate last/previous clock fields. Exact `0001-01-01 00:00:00 +00:00` remains ordinary
STATED text with no sentinel interpretation.

Returned-item occurrence objects contain exactly the provider-placement testimony persisted by
RK-04:

- `item_index`;
- `depth`;
- `item_se_type`;
- `related_keywords_state`.

Depth and item index are occurrence testimony, not keyword identity or tree parentage.

### Monthly search-volume family

Each semantic monthly fact contains:

- `observation_kind`;
- `within_capture_identity`;
- `requested_seed`;
- `locus`;
- exact provider `keyword`;
- `data_period` exactly `{year, month}`;
- exact nonnegative `search_volume`;
- complete returned-item `occurrences` as `{item_index}`.

Seed-locus monthly facts have no returned-item occurrence. Returned-item monthly facts have at
least one occurrence. Do not expose a provider monthly-array position that RK-04 did not
persist. Data Period is independent of Capture time and all structure-local provider clocks.

### Relationship family

Each semantic relationship contains:

- `observation_kind`;
- `within_capture_identity`;
- `requested_seed`;
- exact `source_keyword`;
- exact `target_keyword`;
- every occurrence as `{source_item_index, source_depth, target_index}`.

The relation means provider **relatedness testimony** only. API descriptions/tests must not
call it parent/child traversal, BFS, semantic similarity, topic membership, canonical identity,
importance, centrality, or completeness. Frontier targets need no keyword-data row.

## Capture-wide PostgreSQL consistency checks

For each exact `(capture_id, derivation_version_id)` before presentation:

1. load all generic envelope keys and require envelope cardinality equals Capture Outcome
   `observation_count`;
2. load all three semantic parent key sets and require their union equals the complete envelope
   key set with no missing, extra, wrong-kind, or duplicate semantic parent;
3. require every envelope's `attempt_id`, provider, and adapter agree with the verified
   candidate provenance;
4. recompute each semantic `within_capture_identity` from its persisted Recipe-v1 identity axes
   and require exact digest agreement;
5. require each keyword-data STATED child-object state to have exactly one matching child row
   and each non-STATED enclosing state to have zero child rows;
6. require seed locus has zero item occurrences and every returned-item semantic parent has at
   least one item occurrence;
7. require item occurrence `item_index` values collectively form the exact dense
   `0..items_count-1` returned array and equal `derived_returned_item_count`;
8. require every returned-item monthly semantic parent has at least one monthly occurrence,
   every seed-locus monthly fact has zero item occurrences, and every monthly occurrence refers
   to a valid returned item index;
9. require every relationship semantic parent has at least one relationship occurrence;
10. require every relationship occurrence source item index exists; for each source item,
    `related_keywords_state` ABSENT/JSON_NULL implies zero relationship occurrences, while
    STATED permits zero or more and any present target indexes must be exact dense `0..n-1`;
11. require `derived_relationship_occurrence_count` equals total stored relationship occurrence
    rows;
12. require `items_count == derived_returned_item_count` but do not infer completeness from
    `total_count`;
13. enforce classification-gated emptiness:
    `observation_admitted_empty` means zero envelopes, zero semantic/detail/occurrence rows and
    one valid subject-bearing context; `observation_admitted` means a positive envelope count
    and a nonempty exact semantic set.

The technical review must challenge checks 4–10 against the actual RK-04 schema and duplicate
semantics. Do not add an API invariant merely because it holds in RK-02 if RK-04 does not make
it authoritative.

GET must not re-run RK-03 parsing or RK-04 Derivation, repair rows, or compare typed values to
raw provider JSON. Accepted read integrity is verified Evidence plus complete rebuildable-state
consistency; coordinated value corruption preserving all accepted invariants remains an honest
limit unless a later decision adds stronger digests.

## Deterministic presentation order

Outer Capture ordering is `(request_started_at, capture_id)`.

Inside one Capture, presentation order is deterministic but never identity:

- keyword-data: `locus`, `keyword`, `within_capture_identity`;
- keyword-data occurrences: `item_index`;
- monthly facts: `locus`, `keyword`, `year`, `month`, `within_capture_identity`;
- monthly occurrences: `item_index`;
- relationships: `source_keyword`, `target_keyword`, `within_capture_identity`;
- relationship occurrences: `source_item_index`, `target_index`.

The reviewer must challenge whether seed locus should sort before returned-item locus explicitly
rather than relying on lexical string order. Whichever rule is chosen must be stated and tested.

## Shared outer history envelope semantics

Successful responses disclose exactly the D14/API-01 outer grain:

- provider;
- adapter_contract;
- requested_keyword;
- derivation_version_id;
- recipe_resolution;
- observation_kinds;
- captures;
- total_matching;
- returned_count;
- limit;
- order;
- has_more.

Use the existing `history_list_response` math or an equivalent call path without changing
`provider_history.py`. `total_matching` counts unique verified matching Capture documents,
not Observations, keywords, monthly points, edges, occurrences, or provider `total_count`.
`has_more` discloses an unavailable outer tail; it is not pagination or authority for another
provider request.

Empty 200 history means only no matching admitted/admitted-empty Capture under the exact query
and resolved Recipe. It does not mean never measured, failed, no related keywords, or zero
provider corpus.

## Provider Attempt audit

Add the exact Related Keywords adapter to the existing provider-Attempt routing set so:

    GET /v1/attempts/{attempt_id}

uses the existing generic provider Attempt reader with selected/pinned Recipe behavior.
Do not redesign Attempt audit, expose Related Keywords fact families there, or harden unrelated
Attempt-count behavior in this ticket.

## Typed OpenAPI

Create a dedicated `RelatedKeywordsHistoryEnvelope` and fully typed nested Related Keywords
models in the surface-local read module. Every model is strict and `extra="forbid"`.

OpenAPI tests must inspect actual generated schemas rather than merely testing Python response
objects. Descriptions/constants must make at least these distinctions explicit to an API-only
consumer:

- Capture-list grain vs Observation / item / relationship / provider counts;
- requested seed vs returned keyword vs frontier target;
- `locus` vs item occurrence;
- current search volume vs monthly Data Period;
- structure-local provider clocks vs Capture time;
- relatedness vs tree/importance/similarity;
- `core_keyword` provider testimony vs canonical identity;
- provider `total_count` / `items_count` vs Observatory-derived counts;
- admitted-empty vs empty outer history vs failure/never-measured;
- `has_more` vs pagination;
- exact field states including stated-empty arrays and request-disabled clickstream states.

Malformed projection must fail closed rather than be silently stripped or coerced by Pydantic.

## Required adversarial proof

Use isolated temporary Evidence and disposable PostgreSQL. Ordinary tests perform zero public
network, provider, DNS, credential, or protected-Evidence activity.

At minimum prove:

- selected and pinned Recipe v1; unselected 503; malformed/unknown/wrong-adapter/unsupported
  pin 404; stored Recipe metadata/JCS/digest damage 409;
- exact Related Keywords provider Attempt audit routing without fixture fields;
- frozen RK-02 Capture projects 81 keyword-data + 972 monthly + 477 relationships, 1530
  envelopes, exact occurrence counts, one context, and the accepted child-row counts;
- same `conspiracy theories` string appears under two distinct loci/identities;
- exact frontier target `conspiracy theories podcast - youtube` appears as relationship
  testimony with no invented keyword-data/monthly node;
- one exact current-volume/newest-monthly disagreement and the independently recomputed 63/80
  disagreement count survive API projection without synthesis;
- category order/duplicate IDs survive;
- exact independent depth-zero clocks survive and year-1 SERP remains stated text;
- `related_keywords_state` ABSENT / JSON_NULL / STATED-empty and edge-bearing STATED survive
  with correct occurrence behavior through synthetic admitted Captures;
- monthly absent/null/empty/stated-zero states remain distinguishable through keyword-info plus
  monthly family projection;
- seed-vs-depth0 semantic disagreement remains two valid histories inside one Capture;
- duplicate returned keyword collapses semantically while every item/monthly occurrence
  survives; duplicate target collapses semantically while every edge occurrence survives;
- admitted-empty returns one subject-bearing context and empty semantic families;
- planted non-admitted/missing/foreign-Attempt Outcome behind a matching context yields 409;
- damaged/cross-linked/wrong-adapter Attempt or Capture Evidence yields 409 even outside
  `limit=1`;
- missing/extra/wrong-kind/cross-linked envelopes or semantic parents yield 409;
- missing/unexpected child row relative to enclosing state yields 409;
- missing/extra item, monthly, or relationship occurrences yield 409 when the accepted
  completeness rules require detection;
- tampered identity axes that no longer recompute to `within_capture_identity` yield 409;
- wrong `observation_count`, derived item count, derived relationship-occurrence count, or
  classification/emptiness pairing yields 409;
- reads preserve xmin/content for Recipe/selection/Outcome/envelope and all twelve RK-04
  relations and preserve Evidence operation logs;
- two independently derived nonempty PostgreSQL databases return equal Related Keywords
  history JSON;
- Keyword Overview, Organic, Search Mentions, Target Metrics, Historical, and fixture Attempt
  behavior remain isolated.

Golden tests must compare persisted rows to API projection independently enough that using the
same production assembler on both sides cannot create a false green.

## Honest limits

Do not claim:

- provider invariance behind 81/972/477/1530;
- `total_count` completeness or pagination semantics;
- relationship traversal/tree/BFS behavior;
- why frontier targets lack enrichment;
- cross-Capture graph identity;
- canonical identity from `core_keyword`;
- semantic similarity, centrality, importance, opportunity, or Strategy meaning;
- monthly recurrence beyond stated Data Periods;
- universal Provider Update Time;
- value equality to raw body without re-Derivation;
- detection of coordinated internally consistent PostgreSQL value rewrites;
- prior Recipe-pointer history;
- production auth/non-loopback exposure;
- recurring acquisition or concurrent capture writers.

Verify-all-before-limit remains O(all matching Captures). No outer cursor is added.

## Proposed changed-path allowlist

Production:

- `src/observatory/related_keywords_read.py` — new surface-local Recipe validation, typed
  models, membership, integrity checks, projection;
- `src/observatory/api.py` — exact history route and Related Keywords provider Attempt routing.

Tests:

- `tests/test_api_related_keywords.py` — new;
- `tests/test_api_attempts.py` — only if bounded Related Keywords Attempt-routing proof belongs
  in the shared suite;
- `tests/test_provider_recipe_selection.py` — only if bounded Related Keywords selection
  isolation proof cannot live entirely in the new API suite.

Ticket:

- `tickets/RK-05-dataforseo-google-related-keywords-read-history-api.md`.

Do not change `provider_history.py`, `provider_recipe_selection.py`, `migrate.py`, RK-03 parser,
RK-04 Derivation/Recipe, fixtures, Evidence code, Outcomes/Holdings modules, another provider
reader, README/spec/decision authority, or any Strategy/Ranked file. If review proves another
path is necessary, reconcile the allowlist before implementation.

## Verification boundary

Writer verification should be targeted first because Related Keywords PostgreSQL tests are
already expensive. Before the implementation commit, run the new API suite plus directly
affected shared Attempt/selection suites, Ruff, and targeted mypy over every changed Python
file. Then run full configured mypy and compare against the exact draft/start baseline; RK-05
must add zero errors and must not repair unrelated inherited debt.

[CHAZ] supplies the final full `uv run pytest -q` closure run after independent implementation
review/remediation. Do not spend that full-suite run before the implementation is accepted as
the closure candidate.

## Required pre-implementation review

[GROK] must perform an independent code-first read-only review from the exact committed draft
HEAD before [CHAZ] implementation authorization. Treat this ticket as provisional where it
explicitly asks for a challenge.

At minimum review:

- exact route/query and whether subject max-length belongs in HTTP validation;
- v1-only Recipe verification and selection/pinning error mapping;
- context-before-classification membership and admitted-empty behavior;
- full Attempt/Capture verify-before-limit chain;
- whether the proposed nested state/value JSON shape is the clearest lossless API projection;
- all identity recomputation rules;
- item/monthly/relationship occurrence completeness rules under duplicate semantic identities;
- whether dense target indexes are provable per source occurrence from RK-04 rows;
- child-row presence checks relative to enclosing states;
- context count equalities that are true Recipe-v1 invariants versus one-Capture coincidences;
- deterministic family ordering, especially locus ordering;
- exact strict OpenAPI model shape and Decimal serialization;
- Attempt-audit routing and adapter isolation;
- read-only/xmin proof coverage for all twelve relations;
- two-database equality and independent-projection false-green risk;
- exact changed-path allowlist;
- inherited mypy baseline at the draft HEAD;
- any assumption imported from Keyword Overview, Search Mentions, Target Metrics, or Historical
  that is not actually valid for Related Keywords.

Return `READY`, `RECONCILE`, or `NOT_READY`. Do not implement during this review.

## Out of scope

- another DataForSEO request, provider account/pricing call, credentials, or spend;
- Evidence creation/mutation/backup/restore;
- Measurement Outcomes or Holdings for Related Keywords;
- generic `/observations` or graph endpoint;
- provider relationship traversal, frontier enrichment, or another acquisition exchange;
- Keyword Overview unification or shared keyword metric schema;
- canonical keyword/topic/Page/brand identity;
- URL normalization or interpretation of SERP check URLs;
- centrality, importance, similarity, opportunity ranking, recommendations, or Strategy;
- Ranked Keywords;
- recurring acquisition/F12, F13 hardening, auth/exposure, or concurrency work;
- inherited repository-wide typecheck repair.

## One implementation commit must eventually prove

One verified Related Keywords Capture can be consumed only through the versioned, read-only,
Recipe-aware API as one complete subject-bound Capture document whose three semantic families,
field states, independent time axes, seed-vs-item locus, provider occurrences, frontier
relationships, and provenance exactly match the accepted rebuildable RK-04 state — without
inventing graph meaning, cross-surface equivalence, completeness, or Strategy interpretation.
