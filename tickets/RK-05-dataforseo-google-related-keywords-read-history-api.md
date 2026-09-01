# RK-05 — DataForSEO Google Related Keywords Recipe selection and admitted-history API

**Status:** review — [CLAUDE] implementation complete; awaiting [GPT] Steward review, [GROK] adversarial review, and [CHAZ] full-suite closure  
**Start commit:** `988e7b03cf788c51455ec59e8e5f46e884cf434f`  
**Reconciled contract:** `ab42c0df1196fac8769eb272928da5ae0baf802a` — [CHAZ] explicitly authorized [CLAUDE] implementation from that reconciled ticket  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** none; RK-04 closed  
**Draft base:** `be194e99573d6c6f8a9ecb12d23d35c563bce446`  
**Pre-implementation reviewer:** [GROK] independent read-only code-first review  
**Pre-implementation review result:** `RECONCILE` at exact review HEAD `e70d94b55cb2295f6fc5e6928859678137033e6b`  
**Reconciled contract HEAD:** `ab42c0df1196fac8769eb272928da5ae0baf802a`  
**Implementation authorization:** [CHAZ] explicitly authorized the reconciled RK-05 contract; this ticket-only authorization record authorizes no provider call, credentials, Evidence mutation, schema/Recipe/Derivation work, Outcomes/Holdings work, Ranked work, Strategy work, amend, or push  
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

## Steward reconciliation lock — 2026-09-01

Grok independently reviewed this draft at exact clean HEAD
`e70d94b55cb2295f6fc5e6928859678137033e6b` and returned `RECONCILE`. The Steward independently
verified the material findings against the current Recipe, RK-04 schema, derive logic, D14,
and the newer typed reader precedents. The rules below are final RK-05 design authority and
supersede every provisional challenge/question later in this draft. No Product question
remains.

### Exact Recipe-v1 and query boundary

- RK-05 serves only exact Recipe v1
  `a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669`.
- Selected or pinned non-v1 identity returns the accepted provider-selection 404 path.
  Tampered/non-canonical/digest-disagreeing v1 bytes or provider/adapter/kind/taxonomy
  disagreement returns HTTP 409 `evidence_integrity_failure`.
- Validate stored Recipe bytes as UTF-8 JSON, accepted closed Recipe, exact JCS, exact digest,
  provider `dataforseo`, exact Related Keywords adapter, exact ordered three-kind list, and
  exact stored Capture taxonomy in this order:
  `no_response`, `observation_admitted`, `observation_admitted_empty`,
  `provider_envelope_rejected`, `provider_error`, `reconciliation_failed`,
  `response_partial`, `transport_complete_non_admissible`.
- `requested_keyword` is `Query(min_length=1)` only. Do not apply RK-01's 80-character
  operator bound or seed regex to the history query. An impossible exact subject is an empty
  history miss under a valid Recipe, not a 422. Do not apply RK-01 seed constraints to inner
  returned keyword, source/target, `core_keyword`, or URL testimony.

### Exact membership and Evidence boundary

- Candidate membership is anchored on `related_keywords_result_context` and LEFT JOINed to
  `outcomes` by the full `(derivation_version_id, attempt_id, capture_id)` tuple.
- `context.attempt_id` is the candidate Attempt. It must equal the verified Capture parent and
  the matching Outcome/Envelope provenance.
- Matching context with a missing, foreign-Attempt, or non-admitted Outcome is integrity
  disagreement and returns 409; it is never silently converted into empty history.
- Verify every matching candidate before sort/limit: resolved Recipe → verified Attempt →
  `validate_related_keywords_http_parameters` → verified Capture/full bodies → exact
  provider/adapter/parent → persisted request-context agreement → capture-wide PostgreSQL
  consistency. Damage outside `limit=1` still fails the whole read.
- Result echo testimony (`result_seed_keyword`, result location/language/se_type) may disagree
  with verified Attempt testimony and remains API-visible provider result context. Only the
  persisted `request_*` context columns must agree with the verified Attempt.

### Exact lossless state/value projection

RK-05 uses a dedicated fully typed Related-Keywords-local envelope with strict models and
`extra="forbid"`. It does not expose generic/untyped JSON. Freeze these projection rules:

1. A scalar/array persisted as `<value column> + <state column>` is always exposed as
   `{state, value}`. `value` is non-null exactly when state is `stated`; stated-empty arrays
   are `{state: "stated", value: []}`. Stated-empty strings remain exact testimony where
   RK-04 permits them.
2. An enclosing object state plus optional 1:1 child row is always exposed as
   `{state, value}` where `value` is the fully typed child object exactly when the enclosing
   state is `stated`, otherwise null. Child-row absence is never itself interpreted as state.
3. State-only testimony such as `monthly_searches_state`, `search_volume_trend_state`,
   `related_keywords_state`, Bing-normalized state, and clickstream states is exposed as the
   closed lower-case state token without a fake value.
4. Ordinary typed testimony such as monthly `search_volume`, relationship strings,
   item/depth/index occurrence values, and immutable identity axes is exposed directly.

The closed state vocabulary is the applicable subset of `stated`, `json_null`, `absent`,
`not_requested`, and `inapplicable`. Do not collapse unstated trend members:
`search_volume_trend_state` preserves the enclosing provider state while its unstated member
states remain Recipe-v1 `inapplicable`.

The keyword-data projection must account for **every persisted RK-04 column** across the
semantic parent and all five 1:1 child relations, including structure-local `se_type`, current
metrics/bids/categories, monthly/trend states and signed trend members, properties and
`core_keyword`, exact NUMERIC backlinks, intent and ordered foreign intents, SERP URL/
item-types/result-count, all structure-local clock strings, Bing state, and clickstream
states. Decimal values serialize with `format(value, "f")`, never binary float.

### Exact identity, occurrence, and presentation rules

- Recompute semantic identities from persisted axes using the Recipe's exact axis names:
  `requested_seed`, `locus`, `keyword`, `year`, `month`, `source_keyword`, and
  `target_keyword` as applicable. Outer API `requested_keyword` is the same exact Attempt seed
  under API-01 naming; do not substitute that name inside Recipe identity documents.
- Seed locus has zero item/monthly occurrence rows. Every returned-item keyword-data parent
  has at least one item occurrence; every returned-item monthly parent has at least one
  monthly occurrence; every relationship parent has at least one relationship occurrence.
- Returned-item indexes are globally complete across the Capture: collect the **multiset** of
  all keyword-data item-occurrence `item_index` values. Its size is `n` and its unique values
  are exactly `0..n-1`, where `n == items_count == derived_returned_item_count`. This is a
  Recipe-v1/parser invariant, not an RK-02 coincidence. Never require `total_count == n`.
- Relationship `target_index` density is checked **per `source_item_index` across all
  relationship parents for that source occurrence**, never per semantic relationship parent.
  For each source item whose `related_keywords_state` is `stated`, target indexes are the
  unique dense set `0..m-1`; absent/json-null/stated-empty states have zero relationship
  occurrences. This explicitly permits duplicate semantic source keywords at different item
  indexes with different related arrays.
- Every relationship occurrence `source_depth` must equal the keyword-data item-occurrence
  depth for the same `source_item_index`.
- Returned-item monthly occurrence `item_index` and relationship `source_item_index` must
  resolve to an existing returned-item occurrence in the same Capture/Recipe.
- Inner presentation uses explicit locus rank: `seed_keyword_data` first, then
  `returned_item`, then keyword/period/identity tie-breaks. Never rely on lexical locus order.
  Ordering is presentation only, never semantic identity.

### Exact classification and admitted-empty rules

- `observation_admitted` requires a positive semantic envelope set and exact count agreement.
- `observation_admitted_empty` requires one subject-bearing result-context row,
  `observation_count == 0`, zero semantic parent/detail/occurrence rows, and no invented facts.
- A stated seed `KeywordData` with `items=[]` remains ordinary admitted testimony, not
  admitted-empty.
- Empty outer history, admitted-empty Capture history, failure, never-measured, and "no
  related keywords" are distinct states and must be described separately in OpenAPI.

### Golden facts versus Recipe-v1 invariants

The RK-02 values `81`, `972`, `477`, `1530`, the `63/80` current-vs-monthly disagreement,
`167` frontier targets, value-equal seed path versus depth-0 item in that Capture, and exact
category duplicates are golden test facts only. Do not turn them into production validation.

Recipe-v1 read invariants include `items_count == derived_returned_item_count`, the global
returned-item occurrence index set, structure-child presence matching enclosing state,
source-depth agreement, semantic-parent/envelope complete-set equality, occurrence-parent
requirements, and the classification-gated admitted/admitted-empty rules above.

### Final implementation and proof boundary

Production changes are limited to new `src/observatory/related_keywords_read.py` plus the
Related Keywords history route and Attempt-adapter routing addition in `src/observatory/api.py`.
Tests are new `tests/test_api_related_keywords.py`, with bounded edits to
`tests/test_api_attempts.py` and/or `tests/test_provider_recipe_selection.py` only if needed
for routing/selection proof. Prefer proving selection isolation in the new RK-05 test module.
This ticket may carry Writer status/report updates.

Do not modify `provider_history.py`, `provider_recipe_selection.py`, RK parser/Recipe/
Derivation, migrate/schema, fixtures, Evidence, Outcomes/Holdings modules, or sibling readers.
Use a dedicated strict `RelatedKeywordsHistoryEnvelope`; `history_list_response` may supply
outer list math but nested Capture bodies remain fully Related-Keywords typed.

The golden test must independently project persisted PostgreSQL rows plus verified Evidence
into expected JSON without calling the production reader/assembler to construct expected
values. Add synthetic proofs for duplicate source keyword with unequal related arrays,
duplicate semantic target occurrences, duplicate keyword occurrences, admitted-empty, all
relevant absent/null/stated-empty states, foreign/missing/non-admitted Outcome, missing child
rows, missing/extra occurrence rows, identity-axis tamper, source-depth disagreement,
result-echo disagreement, and read damage outside limit. Read-only proof snapshots
`provider_recipes`, `provider_recipe_selections`, `outcomes`, `observation_envelopes`, all
twelve RK-04 tables, and Evidence operation logs. Two independently derived disposable
PostgreSQL databases must return equal non-empty history JSON.

Reserve full RK-02 PostgreSQL derivation for bounded golden/content proofs; use small synthetic
Captures for most adversarial tests. Current inherited mypy baseline at the review HEAD is
14 errors in five unrelated files. RK-05 must add zero errors: targeted mypy over changed
files is clean and full configured mypy matches the exact review/start baseline. Do not repair
that inherited debt.

No Product question remains. Failure-aware activity remains a future Outcomes concern;
subject inventory remains Holdings. Neither is RK-05 scope.

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

## Exact route and query contract

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

`requested_keyword` carries only `min_length=1`. It intentionally does not carry RK-01's
80-character operator bound or seed regex; impossible exact subjects remain normal empty-history
misses under a valid Recipe rather than HTTP-schema rejection.

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
- `observation_admitted`;
- `observation_admitted_empty`;
- `provider_envelope_rejected`;
- `provider_error`;
- `reconciliation_failed`;
- `response_partial`;
- `transport_complete_non_admissible`.

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

## Fully typed Capture document

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

The exact JSON wrapping convention is frozen by the Steward reconciliation lock above:
state/value columns use always-present `{state, value}` wrappers; enclosing object states use
always-present `{state, value}` wrappers whose value is the fully typed child only when stated;
state-only testimony remains a closed lower-case state token. Child-row absence is never
interpreted as a state signal.

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
7. require the multiset of item-occurrence `item_index` values has size `items_count`, its
   unique values are exactly dense `0..items_count-1`, and `items_count` equals
   `derived_returned_item_count`;
8. require every returned-item monthly semantic parent has at least one monthly occurrence,
   every seed-locus monthly fact has zero item occurrences, and every monthly occurrence refers
   to a valid returned item index;
9. require every relationship semantic parent has at least one relationship occurrence;
10. require every relationship occurrence source item index exists and its `source_depth`
    equals that item's persisted depth; group relationship occurrences across all semantic
    relationship parents by `source_item_index`; ABSENT/JSON_NULL/STATED-empty
    `related_keywords_state` requires zero occurrences, while STATED-nonempty requires the
    unique target indexes for that source occurrence to be exact dense `0..n-1`;
11. require `derived_relationship_occurrence_count` equals total stored relationship occurrence
    rows;
12. require `items_count == derived_returned_item_count` but do not infer completeness from
    `total_count`;
13. enforce classification-gated emptiness:
    `observation_admitted_empty` means zero envelopes, zero semantic/detail/occurrence rows and
    one valid subject-bearing context; `observation_admitted` means a positive envelope count
    and a nonempty exact semantic set.

Checks 4–10 are frozen by the Steward reconciliation lock and must be implemented against the
actual RK-04 duplicate/occurrence semantics. No additional read invariant may be inferred merely
because it holds in RK-02 unless repository authority makes it Recipe-v1 behavior.

GET must not re-run RK-03 parsing or RK-04 Derivation, repair rows, or compare typed values to
raw provider JSON. Accepted read integrity is verified Evidence plus complete rebuildable-state
consistency; coordinated value corruption preserving all accepted invariants remains an honest
limit unless a later decision adds stronger digests.

## Deterministic presentation order

Outer Capture ordering is `(request_started_at, capture_id)`.

Inside one Capture, presentation order is deterministic but never identity:

- keyword-data: explicit locus rank (`seed_keyword_data` first, `returned_item` second), then
  `keyword`, `within_capture_identity`;
- keyword-data occurrences: `item_index`;
- monthly facts: the same explicit locus rank, then `keyword`, `year`, `month`,
  `within_capture_identity`;
- monthly occurrences: `item_index`;
- relationships: `source_keyword`, `target_keyword`, `within_capture_identity`;
- relationship occurrences: `source_item_index`, `target_index`.

Lexical locus ordering is forbidden because it would put `returned_item` before
`seed_keyword_data`. The explicit presentation rank must be stated and tested.

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

## Final changed-path allowlist

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
reader, README/spec/decision authority, or any Strategy/Ranked file. If implementation proves another
path is necessary, stop and reconcile the allowlist before widening scope.

## Verification boundary

Writer verification should be targeted first because Related Keywords PostgreSQL tests are
already expensive. Before the implementation commit, run the new API suite plus directly
affected shared Attempt/selection suites, Ruff, and targeted mypy over every changed Python
file. Then run full configured mypy and compare against the exact draft/start baseline; RK-05
must add zero errors and must not repair unrelated inherited debt.

[CHAZ] supplies the final full `uv run pytest -q` closure run after independent implementation
review/remediation. Do not spend that full-suite run before the implementation is accepted as
the closure candidate.

## Pre-implementation review — completed

Grok completed the required independent code-first read-only review from exact clean HEAD
`e70d94b55cb2295f6fc5e6928859678137033e6b` and returned `RECONCILE`. The Steward independently
checked and accepted the material findings into the reconciliation lock above: v1 taxonomy
order, exact state/value projection, per-source-item target-index density, global item-index
multiset completeness, source-depth agreement, explicit seed-first locus presentation, complete
RK-04 column projection, query min-length-only behavior, and the final proof/allowlist boundary.

No additional pre-implementation review is required unless implementation exposes a genuine
contradiction with repository authority. This ticket is not implementation-authorized until
[CHAZ] separately authorizes the exact reconciled-ticket HEAD.

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

## Implementation report — [CLAUDE]

### Parent and changed paths

Implementation parent (exact start commit): `988e7b03cf788c51455ec59e8e5f46e884cf434f`.
One implementation commit, not amended, not pushed.

Changed paths, all inside the final allowlist:

- `src/observatory/related_keywords_read.py` — new surface-local reader (Recipe v1
  validation, strict typed models, context-anchored membership, capture-wide integrity
  checks, lossless projection, deterministic presentation);
- `src/observatory/api.py` — the exact history route plus the Related Keywords adapter in
  the existing generic provider-Attempt routing set;
- `tests/test_api_related_keywords.py` — new, 134 tests;
- this ticket (Status and this report only).

No other path was touched. `provider_history.py`, `provider_recipe_selection.py`,
`migrate.py`, the RK-03 parser, the RK-04 Recipe/Derivation, fixtures, Evidence code,
Outcomes/Holdings modules, sibling readers, README/spec/decision authority, Ranked, and
Strategy files are unmodified. `tests/test_api_attempts.py` and
`tests/test_provider_recipe_selection.py` were not edited: the Attempt-routing and
selection-isolation proofs live in the new RK-05 suite, as the ticket preferred.

### Route, query, and schema

    GET /v1/providers/dataforseo/google/related-keywords/history

Query is exactly `requested_keyword` (required, `Query(min_length=1)` only),
`derivation_version_id` (optional pin), `limit` (default 20, 1..100), `order`
(`asc`/`desc`, default `asc`). RK-01's 80-character operator bound and seed regex are
deliberately absent: an impossible exact subject is a normal empty-history miss, proved by
`test_long_operator_subject_is_an_empty_history_miss_not_422`. No depth, frontier, keyword,
volume, cursor, offset, or continuation parameter exists; the generated OpenAPI parameter
set is asserted to be exactly those four.

The response model is a dedicated strict `RelatedKeywordsHistoryEnvelope`. Every nested
model is `extra="forbid"`, `strict=True`, and fully typed; no nested Capture body is a
generic dictionary. `history_list_response` supplies the outer twelve-key list math without
changing `provider_history.py`. The outer envelope is validated once in the reader and once
again by the route's response model.

### Recipe selection and stored-Recipe verification

`resolve_provider_recipe` is used unchanged for the exact Related Keywords adapter. No
selection is ever written by production code.

- no selection and no pin → 503 `provider_recipe_not_selected`;
- selection → `recipe_resolution = "selected"`; accepted pin → `"pinned"`;
- malformed, empty, uppercase, short, unknown, wrong-adapter, or registered-but-non-v1 pin →
  404, including a second Recipe registered for this same adapter;
- selecting a non-v1 Recipe for this adapter → 404.

After resolution the reader independently re-validates the registered Recipe: UTF-8 JSON,
`validate_recipe`, exact JCS re-canonicalisation, exact digest equal to
`a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669`, provider `dataforseo`
across the constant, the resolution, the column, and the document, the exact adapter across
the same four sources, the exact ordered three-kind list, and the exact stored Capture
taxonomy in its stored order (`no_response`, `observation_admitted`,
`observation_admitted_empty`, `provider_envelope_rejected`, `provider_error`,
`reconciliation_failed`, `response_partial`, `transport_complete_non_admissible`). Damage to
any of those yields 409 `evidence_integrity_failure` with no history envelope. A taxonomy
re-ordering that keeps the same members is proved to fail.

### Membership and provenance

Membership is context-anchored: `related_keywords_result_context` for the exact
`requested_seed` and Recipe v1, LEFT JOINed to `outcomes` on the full
`(derivation_version_id, attempt_id, capture_id)` tuple. A matching context with a missing
Outcome, an Outcome citing a foreign Attempt, or any non-admitted classification is
integrity damage and returns 409; it is never silently converted into empty history. The
reader additionally requires exactly one Outcome row per matching `capture_id` and requires
its Attempt, classification, and `observation_count` to agree, which closes the
foreign-Attempt case from both directions.

Every matching candidate is verified before any sort or limit: Recipe v1 → committed
Attempt via `EvidenceStore.read_attempt` → provider/adapter on Attempt and Capture →
`validate_related_keywords_http_parameters` → committed Capture via
`EvidenceStore.read_capture` → exact parent identity → persisted `request_*` context
agreement → the capture-wide PostgreSQL checks below. `total_matching` counts unique
verified Capture documents; ordering is `(request_started_at, capture_id)` reversed whole
for `desc`; `limit` applies to whole Capture documents only. Damage on a Capture outside
`limit=1` still fails the entire read
(`test_damage_outside_the_limit_still_fails_the_whole_read`).

Result echo (`result_seed_keyword`, result location/language/se_type) is exposed as provider
testimony and may disagree with the verified Attempt; only the `request_*` duplicates must
agree. Proved with a body whose echo really disagrees, not with planted PostgreSQL damage.

### Field-state projection

The frozen projection is implemented exactly:

1. value+state column pairs are always `{state, value}`; `value` is non-null exactly when
   `state == "stated"`, enforced by a model validator on every wrapper. Stated-empty arrays
   are `{"state": "stated", "value": []}`; stated-empty permitted strings survive exactly.
2. Enclosing object states (`keyword_info`, `keyword_properties`, `avg_backlinks`,
   `search_intent`, `serp_info`) are always `{state, value}` whose `value` is the fully typed
   child object exactly when the state is `stated`, otherwise null. Child-row absence is
   never read as a state signal: a missing row under a stated state is 409, and a present
   row under a non-stated state is 409.
3. State-only testimony (`monthly_searches_state`, `search_volume_trend_state`,
   `related_keywords_state`, `bing_normalized_state`, `clickstream_normalized_state`,
   `clickstream_keyword_info_state`, `seed_keyword_data_state`) is the exact lower-case
   token with no fabricated value.
4. Ordinary semantic and occurrence values (`keyword`, `locus`, `requested_seed`,
   monthly `search_volume`, `data_period`, relationship strings, `item_index`, `depth`,
   `item_se_type`, `source_item_index`, `source_depth`, `target_index`) are direct typed
   values.

`absent`, `json_null`, `stated`, `not_requested`, and `inapplicable` are never collapsed;
`test_unstated_trend_members_stay_inapplicable` pins the Recipe-v1 rule that unstated trend
members keep `inapplicable` while the enclosing `search_volume_trend_state` keeps the real
provider state. Decimal-capable NUMERIC values serialize with `format(value, "f")`; the
reader refuses any non-`Decimal` value in a NUMERIC position and
`RelatedKeywordsDecimalField` refuses a binary float outright.

Every persisted RK-04 content column across the eleven non-context relations is projected.
`test_reader_projects_every_persisted_rk04_column` compares the reader's column tuples to
`information_schema` and reconciles every context column against either the exposed
`result_context`, the verified `request` block, or provenance — so nested `se_type`, trend
member states, all five structure-local clocks, Bing and clickstream states, exact NUMERIC
backlinks, ordered duplicate categories/foreign intents/SERP item types, and SERP result
counts cannot be silently dropped.

### Twelve-relation consistency

For each `(capture_id, derivation_version_id)` before presentation:

1. envelope keys loaded; kinds must be Recipe-v1 kinds; envelope `attempt_id`, provider, and
   adapter must match the verified candidate; envelope cardinality must equal Outcome
   `observation_count`;
2. the union of the three semantic parent key sets must equal the envelope key set exactly,
   with no missing, extra, duplicate, or cross-kind identity;
3. every semantic identity is recomputed from persisted axes using the Recipe's exact axis
   names — `requested_seed`, `locus`, `keyword` for keyword-data; those plus `year`, `month`
   for monthly; `requested_seed`, `source_keyword`, `target_keyword` for relationship — and
   must equal the stored digest. The outer API name `requested_keyword` is never substituted
   into an identity document;
4. each STATED child state requires exactly one child row; each non-STATED state requires
   zero; orphan child rows are rejected;
5. seed locus has zero item occurrences; every returned-item keyword-data parent has at
   least one;
6. the multiset of all keyword-data item-occurrence `item_index` values has size `n`, its
   unique values are exactly `0..n-1`, and `n == items_count == derived_returned_item_count`.
   Global, not per parent;
7. every returned-item monthly parent has at least one monthly occurrence, every seed-locus
   monthly fact has none, and every monthly occurrence resolves to a real returned item;
8. every relationship parent has at least one relationship occurrence; every occurrence's
   `source_item_index` resolves to a real item occurrence and its `source_depth` equals that
   item's persisted depth;
9. relationship target indexes are grouped **per `source_item_index` across all semantic
   relationship parents** and must be unique and dense `0..m-1`; a non-STATED
   `related_keywords_state` requires zero occurrences, and a STATED-empty array legitimately
   has zero;
10. `derived_relationship_occurrence_count` equals total stored relationship occurrences;
11. `items_count == derived_returned_item_count` is required; `total_count == items_count`
    is explicitly **not** required, and a disagreeing `total_count` is served as testimony;
12. classification gating: `observation_admitted_empty` requires zero envelopes, zero
    semantic parents, zero child rows, zero occurrences, and the one subject-bearing context;
    `observation_admitted` requires a positive envelope count and a non-empty semantic set.

Presentation uses an explicit locus rank (`seed_keyword_data` = 0, `returned_item` = 1) then
keyword/period/identity; `test_presentation_ranks_seed_before_returned_item` asserts the
result differs from lexical ordering. GET re-runs no parsing, no Derivation, and no repair.

### Golden proof

`test_golden_rk02_capture_matches_persisted_state_and_evidence` derives the accepted
177,120-byte RK-02 fixture (SHA-256 verified in-test) into disposable PostgreSQL and
compares the API response to an expected document built by this suite's **own** projector.
That projector discovers each relation's columns from `information_schema`, groups
value/state pairs by column naming alone, applies the five enclosing-state mappings, and
sorts with the contract's explicit rank. It never calls `related_keywords_read` or
`history_list_response`, so a shared bug cannot manufacture a green.

The same test then re-proves, from the API projection alone: 81 keyword-data, 972 monthly,
477 relationship facts and 1530 envelopes; 80 item, 960 monthly, and 477 relationship
occurrences; child rows 81/81/60/81/63 both in PostgreSQL and as STATED structures in the
projection; `conspiracy theories` present under both loci as two distinct identities with the
seed locus carrying no occurrence and the depth-0 item carrying depth 0; the exact frontier
target `conspiracy theories podcast - youtube` present as relationship testimony with no
keyword-data or monthly node; the duplicated ordered category array `[10013, 10013, 10106,
13566]`; all five exact depth-zero structure clocks; a stated year-1 SERP clock; and an
independently recomputed current-vs-newest-monthly disagreement count of 63 across the 80
returned items. All of these are asserted as fixture facts in the test module only — no
production code contains them.

### Adversarial proof map

134 tests, all passing. Coverage against the ticket's required list:

- selection/pin/404/503/409 Recipe cases, including registered non-v1 and taxonomy-order
  damage;
- Related Keywords Attempt audit routing through the existing generic provider reader, with
  selected and pinned behaviour, no fixture `observations` field, and 404 for unknown or
  non-hex identities;
- duplicate returned keyword collapsing semantically while both item and monthly occurrences
  survive; duplicate target collapsing while both edge occurrences survive; duplicate source
  keyword at two item indexes with **unequal** related arrays producing one keyword-data
  identity, three relatedness pairs, and per-source dense target indexes;
- `related_keywords` ABSENT / JSON_NULL / STATED-empty / STATED-nonempty with correct
  occurrence behaviour; monthly ABSENT / JSON_NULL / STATED-empty / STATED-zero remaining
  distinguishable through keyword-info plus the monthly family;
- seed-vs-depth-0 disagreement as two valid histories in one Capture (synthetic and golden);
- frontier target with no invented node; admitted-empty with one subject-bearing context and
  empty families; stated seed with `items: []` remaining ordinary `observation_admitted`;
- missing, foreign-Attempt, and six non-admitted Outcome classifications behind a matching
  context → 409;
- missing Capture Evidence, missing Attempt Evidence, cross-linked Attempt provenance, a
  context row planted over foreign-adapter (Historical) Evidence, and damage on a Capture
  outside `limit=1` → 409;
- missing / extra / wrong-kind / unknown-kind / cross-linked (attempt, provider, adapter)
  envelopes → 409; missing and extra semantic parents → 409;
- missing child row under a stated state and unexpected child row under a non-stated state →
  409;
- missing item occurrence, extra item occurrence breaking global density, missing monthly
  occurrence, monthly occurrence without a returned item, missing relationship occurrence,
  per-source target-index density violation, duplicate target index across two parents, and
  non-stated `related_keywords` carrying occurrences → 409;
- seven identity-axis tampers across all three families → 409; relationship `source_depth`
  disagreement → 409;
- wrong `observation_count` in both directions, wrong `items_count`,
  `derived_returned_item_count`, and `derived_relationship_occurrence_count`, and an
  admitted-empty classification over semantic rows → 409; `total_count` disagreement served
  as testimony;
- persisted `request_*` disagreement with the verified Attempt (ints, flags, `order_by`) →
  409, while result echo disagreement is served;
- xmin plus complete content snapshots preserved across `provider_recipes`,
  `provider_recipe_selections`, `outcomes`, `observation_envelopes`, and all twelve RK-04
  relations; Evidence file digests and the store operation log unchanged across history,
  desc, empty-history, and Attempt-audit reads;
- two independently derived disposable PostgreSQL databases returning byte-equal non-empty
  history JSON;
- the actual generated OpenAPI document: exact four parameters, `minLength: 1` with no
  pattern or maxLength, limit bounds, closed schemas at every level, frozen request literals,
  the three-kind `prefixItems`, typed nested structures rather than free-form objects, and
  the required consumer distinctions present as text (with graph vocabulary appearing only
  inside explicit denials);
- isolation: sibling Keyword Overview, Organic, Search Mentions, Target Metrics, and
  Historical history routes remain unselected 503 while Related Keywords serves 200; exactly
  one new path is added; history is bound to its exact subject and does not case-fold;
- fail-closed model proofs for malformed envelopes, state/value disagreement, classification
  pairing, and binary floats in a decimal position.

### Verification results

- `uv run pytest -q tests/test_api_related_keywords.py` → **134 passed** (126s).
- `uv run pytest -q tests/test_api_attempts.py tests/test_provider_recipe_selection.py
  tests/test_api.py` → **24 passed**. Neither shared test file was modified; they were run
  because `api.py` changed.
- `uv run ruff check .` → clean.
- Targeted `uv run mypy src/observatory/related_keywords_read.py src/observatory/api.py
  tests/test_api_related_keywords.py` → **Success: no issues found in 3 source files**.
- Full `uv run mypy` → **14 errors in 5 files (checked 88 source files)**, identical to the
  inherited baseline measured at `988e7b03cf788c51455ec59e8e5f46e884cf434f` (14 errors, 5
  files, 86 source files; the two added files are clean). RK-05 adds zero errors and repairs
  none of the unrelated debt.
- The full repository suite was deliberately **not** run; [CHAZ] owns that closure run.

### Strongest and weakest seams

Strongest: the golden proof's independent `information_schema`-driven projector, which makes
a silently dropped column or a wrong wrapper shape a hard failure rather than a matching
bug on both sides; the per-source-item relationship density and `source_depth` agreement
checks, which are the rules most likely to be got wrong and are proved with duplicate
sources carrying unequal arrays; and verify-all-before-limit, proved with real damage on a
Capture the limit would have hidden.

Weakest: `_capture_families` is one long function carrying most of the twelve-relation
contract. It is heavily tested but it is the place a future Recipe change will be hardest to
extend safely. The synthetic bodies duplicate RK-04's test builders rather than importing
them; that duplication is deliberate (the allowlist forbids touching the RK-04 suite, and a
cross-suite import would couple two independent proofs) but it is real duplication a later
surface should consider hoisting only under an explicit Steward decision.

### False-green risks

- The reader's own `IntegrityError` messages are not asserted; every negative test asserts
  only HTTP 409 with the `evidence_integrity_failure` detail. A check could fire for the
  wrong reason and still look green. This is consistent with the accepted signal boundary but
  it does weaken diagnosis.
- Several damage cases legitimately trip more than one invariant at once (for example
  deleting a relationship occurrence breaks both the parent-has-an-occurrence rule and
  `derived_relationship_occurrence_count`). Where it mattered I chose an `UPDATE` that leaves
  counts intact so the density and duplicate-target rules are proved in isolation.
- PostgreSQL CHECK constraints survive `session_replication_role = replica`, so some damage
  classes are unreachable from a test: a semantic row cannot be given a foreign
  `observation_kind`, `depth` cannot exceed 4, a state token cannot leave the closed set, and
  a value/state pair cannot be desynchronised in storage. The corresponding reader checks are
  therefore defence in depth proved only at the model level, not end to end.
- The synthetic Captures are small. Ordering, density, and duplicate rules are proved on two
  or three items plus the 80-item golden Capture; no Capture with thousands of items was
  exercised.

### Honest limits and one item for Steward attention

The ticket says a stored-Recipe "relational metadata disagreement" returns 409. One such
disagreement is not reachable through the accepted resolution path: if
`provider_recipes.adapter_contract` is rewritten to a foreign adapter, `resolve_provider_recipe`
already refuses — the selection no longer resolves (503) and an explicit pin is a
wrong-adapter miss (404). No history envelope is produced either way, so the fail-closed
requirement holds, but the status code is the accepted provider-selection code rather than
409. `test_recipe_adapter_column_damage_serves_no_history` documents this exactly, and the
reader keeps its adapter-metadata check as defence in depth. This needs no contract change in
my judgement, but the Steward should confirm the reading rather than expect a 409 there.

Otherwise the ticket's stated limits stand unchanged. This implementation does not claim
provider invariance behind 81/972/477/1530, `total_count` completeness or pagination,
relationship traversal or tree behaviour, why frontier targets lack enrichment, cross-Capture
graph identity, canonical identity from `core_keyword`, similarity/centrality/importance,
monthly recurrence beyond stated Data Periods, a universal Provider Update Time, value
equality to the raw body without re-Derivation, detection of coordinated internally
consistent PostgreSQL value rewrites, prior Recipe-pointer history, production auth or
non-loopback exposure, or recurring acquisition and concurrent capture writers.
Verify-all-before-limit remains O(all matching Captures) and no outer cursor was added.

### Boundary confirmation

No provider call, no DataForSEO credentials, no DNS or public-network activity (every test
module in this suite installs the loopback-only `socket.create_connection` guard and deletes
provider credential environment variables), no protected Evidence-root access, no new or
live Evidence, no schema or migration change, no Recipe or Derivation change, no Outcomes or
Holdings work, no Ranked Keywords work, no Strategy work, no F12/F13 work, and no automatic
operator Recipe selection. All Evidence in tests is created in `tmp_path`; all PostgreSQL is
a disposable per-test database.

One implementation commit whose parent is exactly
`988e7b03cf788c51455ec59e8e5f46e884cf434f`. Not amended. Not pushed.
