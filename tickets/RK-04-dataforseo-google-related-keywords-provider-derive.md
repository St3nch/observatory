# RK-04 — DataForSEO Google Related Keywords Derivation Recipe and typed persistence

**Status:** accepted — independent pre-implementation reviews reconciled; awaiting explicit [CHAZ] implementation authorization  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** explicit [CHAZ] implementation authorization from the final accepted-ticket HEAD  
**Draft base:** `1739147fadf5b666608d82cfa73b159781c323ea`  
**Review base:** `5d79327d1dfebd40c6aa067ed411ece735c18826`  
**Claude pre-implementation review:** `RECONCILE`  
**Grok independent pre-implementation review:** `RECONCILE`  
**Steward reconciliation:** accepted below; no Product question remains  
**Product direction:** continue the bounded Related Keywords MVP slice; no provider call is needed  

## Purpose

Implement the first content-addressed Derivation Recipe for this Related Keywords adapter,
semantic Observation identities, typed PostgreSQL persistence, and deterministic rebuild
proof for the exact closed adapter:

    dataforseo-labs-google-related-keywords-live-paid-probe-v1

RK-04 is the semantic/persistence half of the Related Keywords vertical slice. RK-05 remains
the separate recipe-selection and consumer API boundary.

The job is to make the useful RK-02/RK-03 provider testimony durable without pretending the
Related Keywords response is a tree, without collapsing frontier strings into invented
enriched nodes, and without treating Keyword Overview look-alike structures as proven
cross-surface equivalents.

No provider exchange, credentials, spend, new Evidence, API, Strategy state, Ranked Keywords,
cross-surface normalization, recurring acquisition, or generic Labs framework is authorized.

The required code-first Claude and independent Grok reviews are complete and reconciled below.
Implementation may begin only after separate explicit [CHAZ] authorization from the final
accepted-ticket HEAD.

## Authority and accepted foundation

- VISION data doctrine and survival requirement.
- VOCABULARY definitions of Evidence, Outcome, Observation, Derivation, Derivation Recipe,
  Provider Update Time, Data Period, Conformance fixture, and Strategy.
- D11 — provider Derivation is recipe-addressed, typed, and time-explicit.
- D12 — claimed contract plus bounded real Evidence; one Capture proves existence, not
  invariance.
- D14 — consumer resources remain explicit and surface-aware; API work is not RK-04.
- PF-04/PF-06/PF-07 — provider Recipe/envelope/write substrate.
- PF-12 — semantic identity versus provider occurrence plus complete-set precedent.
- PF-14/PF-15 — read-integrity and additive-migration precedent.
- AI-05/AI-11/AI-16 — newer provider-specific Recipe, reconciliation, typed-context,
  occurrence, and deterministic-rebuild precedents.
- RK-01 — exact closed Related Keywords acquisition contract.
- RK-02 — accepted live Evidence and full-body testimony reconciliation.
- RK-03 — strict parser, typed IR, exact Conformance fixture, and adversarial field-state/
  occurrence preservation.

RK-03 closed at Steward commit:

    1739147fadf5b666608d82cfa73b159781c323ea

Fixed RK-02 fixture identity:

- `tests/fixtures/dataforseo_google_related_keywords_rk02.json`
- `177120` bytes
- SHA-256 `e128f2f81d51479237f1bd7e51feee3dfffcae4596558ebff67365f03cd1decb`

Fixed parser contract:

    dataforseo-labs-google-related-keywords-live-parser-v1

One body proves existence, not invariance. The live Capture contains 80 returned item
occurrences, 477 relationship occurrences, 246 distinct relationship targets, 167 frontier
targets without enriched returned rows, 960 item-level monthly rows plus the separately
retained seed path's 12 monthly rows, and multiple independent structure-local clocks.

## Steward reconciliation lock — 2026-09-01

Claude and Grok independently returned `RECONCILE` from review HEAD
`5d79327d1dfebd40c6aa067ed411ece735c18826`. The Steward rechecked their material claims
against current code, migration tests, D11/D12/D14, and the RK-03 parser. The rules in this
section are final RK-04 implementation authority and supersede every provisional question or
default candidate elsewhere in this ticket.

### Final semantic decomposition

Recipe v1 keeps exactly three Observation kinds:

- `dataforseo.google.related_keywords.keyword_data.v1`;
- `dataforseo.google.related_keywords.monthly_search_volume.v1`;
- `dataforseo.google.related_keywords.relationship.v1`.

Do not split keyword-data into Keyword Overview-like kinds and do not reuse any
`dataforseo.google.keyword_overview.*` kind or table. Related Keywords has a different
subject grain, locus, relationship context, SERP testimony, parser year bounds, and field
semantics. `core_keyword` remains a field-state/value inside keyword properties, not a fourth
Observation kind or canonical identity.

`locus` is an identity axis for keyword-data and monthly kinds and is exactly
`seed_keyword_data` or `returned_item`. It is absent from relationship identity because
`related_keywords` exists only on returned items.

### Final identity and occurrence rules

Keyword-data identity is exact requested seed + locus + exact provider keyword string.
Monthly identity is exact requested seed + locus + exact provider keyword string + year +
month. Relationship identity is exact requested seed + exact source keyword string + exact
target string.

Returned-item array index, returned-item depth, item-level `se_type`, and relationship target
array index are occurrence/content testimony, never semantic identity. Seed locus has no
item occurrence row. Therefore the frozen Capture has 80 returned-item occurrence rows for
81 keyword-data Observations. Monthly occurrence rows are also returned-item-only; the seed
monthly locus needs no separate occurrence row because it has no item-array occurrence.

Duplicate returned keywords with semantically identical keyword-data detail collapse to one
returned-item keyword-data Observation while every item occurrence survives. Occurrence-only
`related_keywords` differences do not conflict with the semantic keyword-data parent.
Conflicting same-identity enrichment rejects the whole Capture-stage unit as
`provider_envelope_rejected` with zero normal RK-04 rows. Monthly series is excluded from the
keyword-data conflict tuple: duplicate returned-keyword occurrences may contribute unequal
period windows; overlapping periods with equal volumes collapse, unequal overlapping volumes
reject the whole unit, and non-overlapping periods union. Duplicate relationship targets
collapse semantically while every source/target occurrence survives.

A returned item whose `keyword_data` is ABSENT or JSON null cannot form the required source
identity and rejects the whole Capture-stage unit; it is never silently dropped. A missing or
JSON-null result-level `seed_keyword_data` is valid testimony and does not by itself reject.
A missing depth-0 returned item is not a Recipe failure.

Identity-bearing keyword and relationship-target strings must be nonempty. Any provider
string that must be persisted to PostgreSQL/JCS and contains U+0000, a lone surrogate, or
another code point rejected by the accepted canonical-I-JSON boundary rejects the whole unit
as `provider_envelope_rejected`; this must never escape as an uncaught JCS/psycopg failure.
Empty non-identity content remains exact testimony when the parser permits it, including a
stated-empty `core_keyword` or diagnostic URL string.

### Attempt authority and classification

Production Derivation revalidates the exact Capture-cited Attempt parameters through the
existing public `validate_related_keywords_http_parameters` boundary from `capture_event.py`.
Do not create another RK-01 validator and do not edit `capture_event.py` merely to share
validation. A `DocumentError` from that trusted Attempt validation is an Evidence integrity
failure and produces no Capture-stage RK rows.

`parse_related_keywords` validates Attempt context before body JSON. After the public Attempt
validator succeeds, a remaining `RelatedKeywordsParseError` under `/attempt` is treated as
validator-divergence/integrity failure, not provider testimony. Other body/parser
`RelatedKeywordsParseError` failures are `provider_envelope_rejected`. Parser
`PROVIDER_ERROR` becomes repository `provider_error` with zero normal RK rows.

Well-typed result `seed_keyword`, location, language, or task-echo disagreement with the
verified Attempt remains typed provider testimony and does not produce
`reconciliation_failed`. Recipe v1 declares the accepted closed Outcome taxonomy including
`reconciliation_failed` for substrate compatibility, but has no ordinary semantic emission
path for it after RK-03 parsing and trusted Attempt validation. Do not invent a disagreement
rule merely to exercise that classification.

A successful parse with zero stated `KeywordData` at both seed and returned-item loci is
`observation_admitted_empty`; it writes one subject-bearing result-context row and zero
Observation/detail/occurrence rows. A stated seed `KeywordData` with `items=[]` is admitted,
not empty.

### Field-state and clock preservation

No subordinate row may ambiguously mean ABSENT, JSON null, and stated-empty. Preserve the
RK-03 state vocabulary explicitly. In particular:

- `keyword_info`, `keyword_properties`, `avg_backlinks_info`, `search_intent_info`, and
  `serp_info` states live on the keyword-data semantic parent; structure child rows exist only
  when the enclosing object is STATED;
- `monthly_searches_state` and `search_volume_trend_state` live on the stated keyword-info
  child so absent/null/stated-empty monthly arrays remain distinguishable even when they emit
  zero monthly Observations;
- `related_keywords_state` lives on each returned-item occurrence because it is item-level,
  not `keyword_data`-level; ABSENT, JSON null, and stated-empty therefore remain recoverable
  even when zero relationship Observations exist;
- arrays such as categories, foreign intents, and SERP item types preserve provider order and
  duplicates; stated-empty remains a stated empty SQL array rather than an absent child;
- clickstream fields remain `NOT_REQUESTED` under the frozen false request flag; Bing-normalized
  absent/null stays independent and populated Bing remains an RK-03 parser-version trigger.

The bundled keyword-data kind does **not** create one universal provider clock. No RK-04
column may be named merely `provider_update_time`. Preserve exact structure-specific columns
and field states such as `keyword_info_last_updated_time`,
`avg_backlinks_last_updated_time`, `search_intent_last_updated_time`,
`serp_last_updated_time`, and `serp_previous_updated_time`. Monthly `(year, month)` is Data
Period only. The exact SERP value `0001-01-01 00:00:00 +00:00` remains STATED exact text and
is never mapped to null, `never_updated`, Capture time, or a usability enum.

### Final PostgreSQL shape

Add exactly twelve RK-04 typed relations, in addition to existing generic Recipe/Outcome/
envelope/diagnostic tables:

1. `related_keywords_keyword_data` — semantic keyword-data parent, locus, root/nested object
   states and request-disabled/Bing states;
2. `related_keywords_keyword_info` — one-to-one when `keyword_info` is STATED, including
   current metrics, categories, `monthly_searches_state`, `search_volume_trend_state`, signed
   trend member state/values, and the keyword-info clock;
3. `related_keywords_keyword_properties` — one-to-one when STATED, including `core_keyword`
   state/value and clustering/difficulty/language testimony;
4. `related_keywords_avg_backlinks` — one-to-one when STATED, exact Decimal-capable values
   and its own clock;
5. `related_keywords_search_intent` — one-to-one when STATED, open intent vocabulary,
   ordered foreign-intent array, and its own clock;
6. `related_keywords_serp_info` — one-to-one when STATED, exact check URL text, ordered SERP
   types, result count, and SERP-specific clocks;
7. `related_keywords_monthly_search_volume` — semantic monthly fact, calendar year `1..9999`
   and month `1..12`;
8. `related_keywords_relationship` — semantic source-to-target edge;
9. `related_keywords_keyword_data_item_occurrences` — returned-item only, nonnegative item
   index, depth, item-level `se_type`, and `related_keywords_state`;
10. `related_keywords_monthly_item_occurrences` — returned-item monthly occurrence testimony;
11. `related_keywords_relationship_occurrences` — source item index, source depth, target
   array index;
12. `related_keywords_result_context` — one admitted/admitted-empty row bound to the exact
   Capture Outcome.

All three semantic parent relations are kind-bound to matching `observation_envelopes`.
Occurrence relations foreign-key to their matching semantic parent, not merely an arbitrary
envelope. Result context foreign-keys through full Recipe/Attempt/Capture Outcome provenance.
Depth is occurrence content, not an occurrence identity axis. Ordinary UNIQUE keys are
sufficient because seed locus deliberately has no nullable occurrence row; do not introduce
sentinel indexes or `UNIQUE NULLS NOT DISTINCT` unless the accepted model itself changes.

### Migration layering and changed-path correction

Current `SCHEMA_STATEMENTS` is the pre-RK-04 schema and consists of
`PRE_AI16_SCHEMA_STATEMENTS` plus exactly three Historical statements. Introduce
`PRE_RK04_SCHEMA_STATEMENTS` equal to that current pre-RK-04 tuple, then append RK-04
statements to form the new `SCHEMA_STATEMENTS`.

The existing Target Metrics and Historical derive migration tests currently calculate the
Historical delta from `SCHEMA_STATEMENTS` and assert it is exactly three. RK-04 must retarget
those calculations to `PRE_RK04_SCHEMA_STATEMENTS` so the assertion continues proving the
same historical fact; do not weaken `== 3` or inflate it by the RK-04 statement count.

### Required adversarial and golden proof

In addition to ordinary schema/atomicity/idempotency tests, implementation must prove:

- identical duplicate returned keyword → one semantic keyword-data envelope plus multiple
  item occurrences; conflicting enrichment → whole-unit rejection and zero rows across all
  RK-04 relations;
- equal/conflicting overlapping monthly periods across duplicate item occurrences and union
  of non-overlapping windows;
- duplicate target in one source array → one relationship envelope plus multiple occurrences;
- `related_keywords` ABSENT vs JSON null vs stated-empty remain recoverable with zero edges;
- `monthly_searches` ABSENT/JSON-null/stated-empty versus a stated zero monthly point;
- enrichment objects ABSENT/JSON-null/STATED, including hollow SERP;
- categories duplicate order, foreign-intent absent/null/empty/nonempty, and SERP item-type
  duplicate/empty preservation;
- seed-vs-depth0 disagreement and missing depth-0 row remain valid independent testimony;
- empty identity, U+0000, lone surrogate/JCS-invalid provider strings reject deterministically
  without a Derivation crash;
- planted extra rows fail complete-set comparison; rejected units leave zero rows in every
  RK-04 typed/context/occurrence relation; two independent PostgreSQL rebuilds are logically
  equivalent across all twelve RK-04 relations.

Golden tests must pin content, not only counts: prove the same exact seed string has distinct
seed and returned-item identities; pin frontier target
`conspiracy theories podcast - youtube` as relationship testimony with no invented
keyword-data row; pin exact independent depth-0 structure clocks; pin a duplicate-preserving
category tuple; and independently derive `81 + 972 + 477 = 1530`. Those counts are fixture
consequences only and must never appear as production semantic constants.

### Performance and verification lock

The current provider Recipe/envelope substrate may be expensive at 1530 envelopes, but that
is not an RK-04 correctness defect. Do not edit `provider_recipe.py` or add a cache/framework
in this ticket. Use small synthetic bodies for most adversarial tests and limit full-fixture
PostgreSQL derives to the bounded golden/rebuild proofs needed for confidence.

RK-04 must add zero mypy errors. The accepted baseline is 14 inherited errors in the same five
unrelated files recorded at RK-03 closure. Writer proof is: targeted mypy over changed RK-04
files is clean, and full configured `uv run mypy` has the same 14 messages/files as an exact
start-commit baseline comparison. Do not repair those inherited errors here.

No Product question, new provider call, or additional Evidence is required by this
reconciliation.

## Core semantic rule

**Related Keywords remains its own provider surface.** RK-04 must not reuse Keyword Overview
Observation kinds, semantic subject identity, reconciliation, or Recipe merely because
`keyword_info`, monthly searches, properties, backlinks, and intent have similar JSON
shapes. RK-02 explicitly found material differences in subject grain, relationship context,
SERP testimony, field availability, and sentinel-shaped clock behavior.

Mechanical provider-writer patterns may be reused. Cross-surface semantic equivalence is not
accepted in this ticket.

## Accepted three-kind model

The independent reviews and Steward reconciliation retain this decomposition as final RK-04
Recipe-v1 authority.

### 1. Related Keywords keyword-data testimony

Kind:

    dataforseo.google.related_keywords.keyword_data.v1

Semantic identity axes:

- exact requested seed from the verified Attempt;
- closed provider locus: `seed_keyword_data` or `returned_item`;
- exact provider keyword string from that `keyword_data` object.

The locus is load-bearing. RK-02 observed result-level `seed_keyword_data` to be value-equal
to the depth-0 item's `keyword_data`, but RK-03 deliberately preserves those as two provider
paths and synthetic disagreement is valid parser testimony. RK-04 must therefore never
deduplicate or reconcile one path into the other merely because the frozen Capture agrees.

For `returned_item` locus, provider item array index and provider-stated depth are occurrence
testimony, not semantic identity. Persist every returned occurrence in a subordinate typed
relation so duplicate returned keyword strings survive without making array order identity.

The semantic keyword-data detail should preserve the materially useful typed RK-03 content,
including its field states, without inventing a universal keyword metric:

- exact keyword, location/language/se_type testimony;
- `keyword_info` state and current search-volume/competition/CPC/bid/category testimony;
- signed search-volume trend values and exact category order/duplicates;
- `keyword_properties` state, exact `core_keyword` state/value,
  `synonym_clustering_algorithm`, difficulty, detected-language, and other-language flag;
- `avg_backlinks_info` state and exact decimal-capable values;
- `search_intent_info` state, open provider intent vocabulary, ordered foreign-intent array;
- `serp_info` null/stated distinction, exact check URL text, ordered SERP item types,
  result-count state, and exact last/previous clock strings;
- request-disabled clickstream states and the separate Bing-normalized absent/null state.

Do not create canonical keyword identity, topic membership, cluster identity, Page identity,
URL normalization, importance, centrality, or Strategy interpretation.

If duplicate semantic `returned_item` keyword identities occur, occurrence-only differences
such as array index, depth, or `related_keywords` state/content do not create a new semantic
keyword-data Observation. Identical semantic enrichment collapses to one keyword-data
Observation while all item occurrences survive; conflicting same-identity enrichment rejects
the whole Capture-stage unit as `provider_envelope_rejected`. Monthly series values are
reconciled only by the separate monthly kind.

A returned item whose `keyword_data` is absent or JSON null cannot form the required semantic
identity and rejects the Capture-stage unit rather than being silently dropped.

### 2. Related Keywords monthly search-volume testimony

Kind:

    dataforseo.google.related_keywords.monthly_search_volume.v1

Semantic identity axes:

- exact requested seed;
- exact locus: `seed_keyword_data` or `returned_item`;
- exact provider keyword string;
- provider-stated year;
- provider-stated month.

Persist exact nonnegative search volume and retain enough occurrence testimony to prove where
the monthly point came from. Data Period is the explicit `(year, month)` only. It never
inherits Capture time or a structure-local update clock.

RK-03 already rejects duplicate `(year, month)` within one monthly array. If duplicate
semantic returned-keyword occurrences produce overlapping monthly periods, matching values
collapse to one semantic monthly fact while all returned-item monthly occurrences survive;
conflicting values reject the whole Capture-stage semantic unit. Unequal period windows admit
the union when overlapping values agree.

Current `keyword_info.search_volume` remains keyword-data detail and is never derived from the
newest monthly point. The frozen Capture has 63/80 returned items where those values differ.

### 3. Related Keywords relationship testimony

Kind:

    dataforseo.google.related_keywords.relationship.v1

Semantic identity axes:

- exact requested seed;
- exact source keyword string from the returned item's stated `keyword_data.keyword`;
- exact target string from one `related_keywords` occurrence.

Persist every provider occurrence in a subordinate relation with at minimum:

- source returned-item array index;
- source provider-stated depth;
- target array index.

The relationship is **provider relatedness testimony**, not parent/child traversal, BFS,
semantic similarity, topic membership, canonical-keyword membership, or importance.

Repeated, duplicate, backward, same-depth, and self references remain admissible occurrence
testimony. The semantic source→target pair may have multiple occurrences. Array order and
depth are content/occurrence testimony, never semantic identity.

A target does not need a matching enriched returned keyword row. Frontier strings must remain
valid relationship targets without invented keyword-data facts. The frozen Capture has 167
distinct frontier targets, including 14 distinct targets referenced from sources still
inside the remaining requested depth budget.

`related_keywords` absent, JSON null, and stated-empty remain distinct source-item testimony.
Persist that state on the returned-item occurrence row so a null/empty/absent list is never
falsely represented as merely "no semantic edges" and duplicate semantic keyword-data rows
can carry different occurrence-level neighborhood states without false conflict.

## `core_keyword` boundary

Recipe v1 does **not** add a fourth canonical/core relationship Observation.
`core_keyword` remains an exact field-state/value inside keyword-data testimony. This keeps
the provider's separate reference layer recoverable without claiming that it is canonical
identity, synonym equivalence, or a graph edge of the same semantics as `related_keywords`.

## Result context and request authority

Persist exactly one Related Keywords result-context row per admitted Capture and Recipe,
structurally bound to the matching Capture Outcome.

Typed context should preserve at minimum:

- exact requested seed and the frozen Attempt depth/limit/offset/order/boolean flags;
- verified Attempt location/language;
- exact provider result `seed_keyword`;
- result location/language/se_type field states and values;
- `total_count` and `items_count` independently;
- `seed_keyword_data` field state;
- returned item count and relationship occurrence count as rebuildable derived counts only
  where clearly labeled as Observatory derivation counts rather than provider claims.

The verified Attempt remains request authority. Task echo and result disagreement stay
provider testimony and must not overwrite Attempt context.

Well-typed result seed/location/language disagreement with the verified Attempt remains typed
provider testimony and does not produce `reconciliation_failed`. Recipe v1 has no ordinary
semantic reconciliation-failure path after trusted Attempt validation and RK-03 parsing; do
not invent one merely because the frozen Capture happened to agree.

Provider root/task cost, duration, task UUID/path, and request echo remain typed parser IR and
raw Evidence only unless the review identifies a concrete persistence requirement. Do not add
a generic provider-envelope JSON dump.

## Time semantics

Time remains explicitly multi-axis:

- Capture/acquisition time is Evidence provenance only;
- monthly `(year, month)` is Data Period only;
- `keyword_info.last_updated_time`, `avg_backlinks_info.last_updated_time`, and
  `search_intent_info.last_updated_time` are structure-local provider update clocks and never
  inherit from one another;
- SERP `last_updated_time` / `previous_updated_time` remain exact SERP-specific clock
  testimony.

The two observed SERP objects carrying `0001-01-01 00:00:00 +00:00` must remain exact stated
values. Recipe v1 must not map that value to null, `never_updated`, Capture time, or an
ordinary usable Provider Update Time merely because it is syntactically calendar-valid.

Persist these clocks under structure-specific names only: keyword-info, avg-backlinks,
search-intent, SERP-last, and SERP-previous clock columns. No RK-04 relation may expose a
single generic `provider_update_time` column.

## Outcome and failure behavior

Attempt-stage classification remains:

    authorized_unresolved

Capture-stage taxonomy is the accepted provider set:

- `no_response`
- `response_partial`
- `transport_complete_non_admissible`
- `provider_error`
- `provider_envelope_rejected`
- `reconciliation_failed`
- `observation_admitted`
- `observation_admitted_empty`

Repository Outcome is created by the Recipe, never copied from RK-03's parser-local
`ParseClassification` string.

Rules:

- no-response/partial/non-admissible transport retain their existing transport outcomes;
- trusted Attempt-validation `DocumentError`, integrity damage, or a residual parser error
  under `/attempt` produces no Capture-stage RK rows and increments the derivation integrity
  failure count rather than assigning provider fault;
- body/parser `RelatedKeywordsParseError` produces `provider_envelope_rejected`;
- parser `PROVIDER_ERROR` produces `provider_error` with zero normal rows;
- invalid persisted identity/content strings, missing returned-item keyword identity, or
  conflicting same-identity semantic detail produces `provider_envelope_rejected` for the
  entire Capture-stage unit;
- `reconciliation_failed` remains declared but Recipe v1 has no ordinary emission path;
- a successful result with zero stated seed/item KeywordData Observations writes one
  subject-bearing context row, zero normal rows, and `observation_admitted_empty`;
- otherwise an admitted unit writes one atomic complete set and `observation_admitted`.

Rejected/failed units write zero normal Related Keywords Observation/detail/occurrence/context
rows. Do not partially admit "good" returned items around a conflicting semantic unit.

## Verified production Evidence boundary

Production derive must follow the newer provider authority chain, not a test helper:

1. require concrete `EvidenceStore`;
2. verify-on-read one committed Related Keywords Capture;
3. require the exact Related Keywords adapter on the Capture;
4. obtain the exact Attempt ID cited by that Capture;
5. verify-on-read that exact committed Attempt;
6. require the same adapter on the cited Attempt;
7. revalidate the committed Attempt parameters through the existing public
   `validate_related_keywords_http_parameters` boundary and treat `DocumentError` as Evidence
   integrity failure;
8. verify a complete Capture body through `EvidenceStore.read_capture_body`;
9. pass only the validator-returned closed parameters and verified body bytes into
   `parse_related_keywords`;
10. plan and atomically persist the Recipe's exact semantic unit.

An unrelated valid Related Keywords Attempt in the same store must never influence subject,
request context, or provenance for a Capture that cites another Attempt.

Integrity failure produces no Capture-stage provider rows. A separately verified Attempt-stage
Outcome may remain valid.

## Recipe contract

Add one closed canonical I-JSON Derivation Recipe through the accepted provider recipe
substrate. Its `derivation_version_id` is SHA-256 of exact JCS Recipe bytes. Publish final
byte length and digest and prove independent recomputation.

The final Recipe must fix at least:

- exact provider and adapter contract;
- exact RK-03 parser contract;
- verified Attempt as request authority;
- closed-object parser drift policy;
- exact Decimal/integer semantics;
- field-state semantics;
- structure-local clock and monthly Data Period semantics;
- final Observation kinds and identity axes;
- relationship occurrence semantics;
- duplicate semantic-content behavior;
- Capture Outcome taxonomy;
- exact-content and complete-set write behavior.

Any semantic change requires different Recipe bytes and identity. Do not modify RK-03 parser
admission merely to implement Recipe policy unless the technical review proves a parser
defect; that would require explicit ticket reconciliation before implementation.

## PostgreSQL and complete-set requirements

Use existing `provider_recipes`, `outcomes`, `observation_envelopes`, and
`derivation_diagnostics`. Add only bounded Related Keywords typed relations required by the
final model.

Requirements:

- every semantic typed detail is structurally bound to its exact generic envelope and kind;
- every occurrence relation is bound to the correct semantic parent, not merely an arbitrary
  envelope;
- result context is bound to the exact matching Capture Outcome and Recipe provenance;
- exact arrays preserve provider order and duplicates where the parser says they are
  occurrence testimony;
- field-state/value CHECKs preserve stated zero/empty values versus JSON null/absence/
  request-disabled states;
- BIGINT bounds remain I-JSON safe for provider structural integers;
- Decimal-capable provider values use NUMERIC without binary-float round trip;
- schema changes are additive and idempotent over the accepted current schema;
- complete-set comparison is scoped by `(capture_id, derivation_version_id)` and rejects
  extra/conflicting Outcome/context/envelope/detail/occurrence/diagnostic rows;
- missing rebuildable planned rows may be restored only when the final stored set exactly
  equals the intended semantic unit;
- `outcomes.observation_count` equals both intended and stored semantic envelope count;
- two fresh PostgreSQL databases rebuilt from the same verified Evidence and Recipe are
  logically equivalent across every RK-04 relation.

Do not hide semantic disagreement with `ON CONFLICT DO NOTHING`, first/last wins, or
count-only equality.

## Frozen-Capture expectations to recompute, not blindly hard-code

Under the accepted three-kind model the RK-02 fixture should yield:

- 81 semantic keyword-data Observations: one `seed_keyword_data` locus plus 80 unique
  `returned_item` keyword identities;
- 972 semantic monthly search-volume Observations: 12 seed-path points plus 960 item points;
- 477 semantic relationship Observations in this Capture because every observed source
  keyword is unique and no source array repeats a target;
- **1530 total semantic Observation envelopes** for this frozen Capture under the accepted model.

These are frozen-Capture consequences, not provider invariants. Tests must independently
derive the counts from the fixture and separately prove duplicate/reorder behavior with
synthetic mutations.

The occurrence model must also make the following RK-02 facts independently recomputable
without storing them as semantic conclusions: 246 distinct relationship targets, 167
frontier-only target strings, returned-target depth deltas `+1:96, 0:96, -1:69, -2:21`, and
67 multiply referenced targets with maximum observed incoming occurrence count 26.

Do not persist centrality, in-degree, frontier classification, depth deltas, or importance as
new semantic facts in RK-04. They are recomputable consequences of provider testimony.

## Pre-implementation adversarial review — completed

Claude and Grok independently reviewed this exact draft base and both returned `RECONCILE`.
Their accepted findings are resolved by the Steward reconciliation lock above. No additional
pre-implementation technical review is required unless implementation exposes a genuine
contradiction with repository authority.

## Final changed-path allowlist

After explicit [CHAZ] implementation authorization, [CLAUDE] may modify exactly:

- `src/observatory/dataforseo_google_related_keywords.py` — Recipe/kind constants and only
  bounded IR additions genuinely required for persistence;
- `src/observatory/google_related_keywords_derive.py` — new provider derive module;
- `src/observatory/migrate.py` — PRE_RK04 layering plus the twelve additive RK-04 relations;
- `tests/test_dataforseo_google_related_keywords.py` — only if an accepted bounded IR addition
  requires parser-level proof;
- `tests/test_dataforseo_google_related_keywords_derive.py` — new derivation/persistence tests;
- `tests/test_dataforseo_ai_optimization_target_metrics_derive.py` — minimal migration-baseline
  retarget from `SCHEMA_STATEMENTS` to `PRE_RK04_SCHEMA_STATEMENTS`, preserving `== 3`;
- `tests/test_dataforseo_ai_optimization_llm_mentions_historical_derive.py` — the same minimal
  migration-baseline retarget, preserving its original Historical assertion;
- this RK-04 ticket — implementation Start/status/report only.

Do not edit `capture_event.py`, `provider_recipe.py`, `derive.py`, API/selection files,
AGENTS.md, existing fixtures, or another provider surface. If any other path is truly
necessary, stop and report the exact need for Steward reconciliation rather than widening on
the fly. The eventual `google_related_keywords_derive` command listing in AGENTS.md is a
Steward documentation follow-up, not Writer scope.

## Verification boundary

Use small synthetic bodies for most TDD. The bounded ticket-scoped verification before the
single implementation commit is:

    uv run pytest -q tests/test_dataforseo_google_related_keywords.py tests/test_dataforseo_google_related_keywords_derive.py
    uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py tests/test_dataforseo_ai_optimization_llm_mentions_historical_derive.py
    uv run ruff check .

Run targeted mypy over every changed RK-04 Python/test file and require it to be clean. Then
run full configured `uv run mypy` and compare it against an exact start-commit baseline: RK-04
must add zero messages and preserve the inherited 14 errors in the same five unrelated files.
Do not repair those errors here.

The Writer does not need to run the entire pytest suite before its commit unless a concrete
integration issue requires it. [CHAZ] supplies the final `uv run pytest -q` full-suite
validation at the RK-04 closure gate under current project process.

Ordinary RK-04 tests must perform zero provider/DNS/public-network activity and require no
credentials or protected Evidence root.

## Out of scope

- another DataForSEO request or any provider/account/pricing call;
- Evidence creation, mutation, backup, restore, or acquisition orchestration;
- RK-05 recipe selection/read/history API;
- Keyword Overview Observation unification or migration;
- canonical keyword, topic, Page, brand, or graph-node identity across surfaces;
- graph union across Captures;
- frontier enrichment or synthetic node creation;
- semantic similarity, centrality, importance, scoring, opportunity ranking, or Strategy;
- Ranked Keywords;
- generic DataForSEO Labs derive/parser framework;
- recurring acquisition/F12 or unrelated gate hardening;
- repairing inherited repository-wide mypy errors.

## One implementation commit must eventually prove

One verified Related Keywords Capture can be deterministically re-derived under one exact
content-addressed Recipe into typed, provenance-bound keyword, monthly Data-Period, and
relationship testimony while preserving seed-vs-item locus, provider occurrence order/depth,
frontier targets, field states, independent clocks, and exact-content rebuild semantics —
without inventing graph meaning or cross-surface equivalence.
