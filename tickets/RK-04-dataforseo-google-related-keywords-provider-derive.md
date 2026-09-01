# RK-04 — DataForSEO Google Related Keywords Derivation Recipe and typed persistence

**Status:** review — [CLAUDE] implementation complete; awaiting [GPT] Steward review and [CHAZ] closure  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** none inside RK-04; implementation remains bounded to the accepted allowlist and no-network/provider boundary  
**Draft base:** `1739147fadf5b666608d82cfa73b159781c323ea`  
**Review base:** `5d79327d1dfebd40c6aa067ed411ece735c18826`  
**Claude pre-implementation review:** `RECONCILE`  
**Grok independent pre-implementation review:** `RECONCILE`  
**Steward reconciliation:** accepted below; no Product question remains  
**Implementation authorization:** [CHAZ] explicitly authorized RK-04 implementation from exact accepted-ticket HEAD `fecc743a61ba36d87952d3184433f4be90b68bf8`  
**Implementation start commit:** `9eee309bda9111f6a6446189ac2bbb1a050574f6` — clean `main`, authorization-only child of the accepted-ticket HEAD  
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
[CHAZ] explicitly authorized [CLAUDE] implementation from exact accepted-ticket HEAD
`fecc743a61ba36d87952d3184433f4be90b68bf8`. That authorization is limited to this ticket's
final semantic/persistence contract and changed-path allowlist; it authorizes no provider call,
credential use, Evidence mutation, API/RK-05 work, Ranked Keywords work, Strategy work, amend,
or push.

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

## Implementation report — [CLAUDE], 2026-09-01

### Commit boundary

- Implementation parent: `9eee309bda9111f6a6446189ac2bbb1a050574f6` (clean `main`). Its parent
  `fecc743a61ba36d87952d3184433f4be90b68bf8` is the accepted-ticket HEAD; `9eee309` records
  [CHAZ]'s authorization only and changed no implementation semantics.
- Child: the single implementation commit carrying this report. No amend, no push, no rebase.

### Changed paths

Exactly the accepted allowlist; no widening was needed.

| Path | Change |
|---|---|
| `src/observatory/dataforseo_google_related_keywords.py` | +143 lines: kind/locus constants and the Recipe document. No parser admission change. |
| `src/observatory/google_related_keywords_derive.py` | new, 1388 lines |
| `src/observatory/migrate.py` | +517 lines: twelve additive relations plus `PRE_RK04_SCHEMA_STATEMENTS` layering |
| `tests/test_dataforseo_google_related_keywords_derive.py` | new, 2129 lines, 84 tests |
| `tests/test_dataforseo_ai_optimization_target_metrics_derive.py` | 2 lines: migration-baseline retarget only |
| `tests/test_dataforseo_ai_optimization_llm_mentions_historical_derive.py` | 2 lines: migration-baseline retarget only |
| this ticket | status + this report |

`tests/test_dataforseo_google_related_keywords.py` was **not** touched: no IR addition was
required. `capture_event.py`, `provider_recipe.py`, `derive.py`, API/selection modules,
`AGENTS.md`, and every existing fixture are unchanged.

### Recipe identity

- Canonical JCS byte length: **2398**
- `derivation_version_id`:
  **`a85abbe1d9780a3a66cc9fe01adc539e8568144a067b0345ec06cec700dc2669`**
- Independent recomputation proven in
  `test_recipe_bytes_and_digest_recompute_independently`: raw `hashlib.sha256` over the
  published bytes, `recipe_bytes`, `recipe_derivation_version_id`, and a fresh
  `related_keywords_recipe()` all agree, and the digest differs from `CORE_RECIPE_ID`.

Recipe v1 fixes: adapter contract `dataforseo-labs-google-related-keywords-live-paid-probe-v1`;
parser contract `dataforseo-labs-google-related-keywords-live-parser-v1`; the fourteen closed
provider objects with no extension-permitted object and `fail_closed` drift; `exact_decimal`
numerics; the five-state field vocabulary; `data_period.rule =
provider_stated_year_month_1_9999` with `never_from_capture`; `provider_update_time.rule =
structure_local_clocks_no_universal_update_time` with `never_from_capture_or_sibling`;
`reconciliation.rule = verified_attempt_authority_result_echo_is_testimony`; the three
Observation kinds with their identity axes; and the eight-classification closed Capture-stage
taxonomy. The recipe bytes contain no `keyword_overview` substring
(`test_recipe_is_related_keywords_specific_and_not_keyword_overview`).

### Twelve-relation schema

`PRE_RK04_SCHEMA_STATEMENTS` is the exact pre-RK-04 tuple (40 statements: `PRE_AI16` plus the
three Historical statements). `SCHEMA_STATEMENTS` is `PRE_RK04_SCHEMA_STATEMENTS +
RK04_SCHEMA_STATEMENTS` (52). The Historical delta measured from `PRE_RK04_SCHEMA_STATEMENTS`
is still exactly 3, so both existing migration tests keep their original meaning with a
two-line retarget and no weakened assertion.

| # | Relation | Grain / binding |
|---|---|---|
| 1 | `related_keywords_keyword_data` | semantic parent, `locus`, six enclosing-object states + Bing/clickstream states; envelope FK |
| 2 | `related_keywords_keyword_info` | 1:1 when STATED; metrics, categories, `monthly_searches_state`, `search_volume_trend_state`, signed trend members, keyword-info clock |
| 3 | `related_keywords_keyword_properties` | 1:1 when STATED; `core_keyword` state/value, clustering, difficulty, language |
| 4 | `related_keywords_avg_backlinks` | 1:1 when STATED; NUMERIC values plus its own clock |
| 5 | `related_keywords_search_intent` | 1:1 when STATED; open intent vocabulary, ordered `TEXT[]` foreign intent, own clock |
| 6 | `related_keywords_serp_info` | 1:1 when STATED; exact check URL, ordered SERP types, result count, SERP-last and SERP-previous clocks |
| 7 | `related_keywords_monthly_search_volume` | semantic monthly fact, `year 1..9999`, `month 1..12`; envelope FK |
| 8 | `related_keywords_relationship` | semantic source→target edge; envelope FK |
| 9 | `related_keywords_keyword_data_item_occurrences` | returned-item only; index, depth, item `se_type`, `related_keywords_state`; FK to relation 1 |
| 10 | `related_keywords_monthly_item_occurrences` | returned-item monthly occurrence; FK to relation 7 |
| 11 | `related_keywords_relationship_occurrences` | source item index + target index identity, source depth as content; FK to relation 8 |
| 12 | `related_keywords_result_context` | one row per `(capture_id, derivation_version_id)`; FK to `outcomes(derivation_version_id, attempt_id, capture_id)` and `provider_recipes` |

Relations 2–6 and 9 foreign-key to the keyword-data parent through
`(capture_id, derivation_version_id, within_capture_identity, observation_kind)`, never to an
arbitrary envelope; 10 and 11 key to their own semantic parent. Every relation carries a
kind CHECK. Ordinary UNIQUE/PRIMARY KEY suffices throughout because the seed locus
deliberately has no occurrence row, so no nullable occurrence column exists and no
`UNIQUE NULLS NOT DISTINCT` or sentinel index was introduced.

RK-04 defines a short-named `_rk04_consistency` helper rather than reusing
`_state_value_consistency`: the latter derives its constraint name from the table name, which
would exceed PostgreSQL's 63-byte identifier limit for several RK-04 relations and be
silently truncated (a real collision risk). The generated CHECK is semantically identical.

No RK-04 relation exposes a generic `provider_update_time` column; that is asserted both
statically (`test_no_rk04_relation_exposes_a_generic_provider_update_time`) and against the
live catalog (`test_no_rk04_column_is_named_provider_update_time`).

### Frozen-Capture results

The RK-02 fixture derives to **81 keyword-data + 972 monthly + 477 relationship = 1530**
semantic envelopes, with 80 item occurrences, 960 monthly occurrences, 477 relationship
occurrences, and one result-context row. Child-relation counts are keyword-info 81,
properties 81, backlinks 60, intent 81, SERP 63.

Every count is recomputed from the fixture inside the test module and appears nowhere in
production code. The 80-vs-81 asymmetry is the accepted seed-locus rule, asserted explicitly.

### Acceptance → proving test

| Accepted requirement | Proving test |
|---|---|
| Recipe bytes/digest, independent recomputation | `test_recipe_bytes_and_digest_recompute_independently` |
| Exactly three kinds; locus axes; no locus on relationship | `test_recipe_declares_exactly_three_kinds_with_locus_axes` |
| No Keyword Overview kind/table/semantics reuse | `test_recipe_is_related_keywords_specific_and_not_keyword_overview`, `test_monthly_year_bound_is_the_parser_range_not_keyword_overview` |
| Closed Capture-stage taxonomy incl. declared `reconciliation_failed` | `test_recipe_declares_the_closed_capture_outcome_taxonomy` |
| migrate kind constants match the parser module | `test_migrate_kind_constants_match_the_parser_module` |
| PRE_RK04 layering, Historical delta still 3, twelve additive statements | `test_pre_rk04_layering_is_additive_and_preserves_the_historical_delta`, `test_populated_pre_rk04_schema_then_related_keywords_derive`, and the two retargeted suites |
| No generic provider_update_time anywhere | `test_no_rk04_relation_exposes_a_generic_provider_update_time`, `test_no_rk04_column_is_named_provider_update_time` |
| Frozen fixture identity unchanged | `test_frozen_fixture_identity_is_unchanged` |
| 81 + 972 + 477 = 1530 independently derived | `test_golden_counts_are_independently_derived_from_the_fixture` |
| Same seed string, two distinct loci and digests; seed locus has no occurrence | `test_golden_seed_and_returned_loci_are_distinct_identities_for_one_keyword` |
| Frontier target is an edge with no invented node; 246/167 recomputable | `test_golden_frontier_target_is_an_edge_without_an_invented_keyword_data_row` |
| Five independent structure-specific depth-0 clocks | `test_golden_depth_zero_clocks_stay_structure_specific_and_independent` |
| Year-1 SERP text exact, no sentinel | `test_golden_hollow_serp_keeps_the_year_one_string_as_stated_text` |
| Category order and duplicates; null categories | `test_golden_categories_preserve_provider_order_and_duplicates` |
| Current volume never derived from monthly (63/80) | `test_golden_current_volume_is_never_derived_from_monthly_testimony` |
| `core_keyword` is properties testimony only, no fourth kind | `test_golden_core_keyword_stays_properties_testimony` |
| Enrichment state counts 59/21, 62/18, clickstream not_requested | `test_golden_enrichment_state_counts_match_the_capture` |
| `related_keywords_state` on the occurrence; depth distribution | `test_golden_related_keywords_state_lives_on_the_item_occurrence` |
| Context carries Attempt authority and labelled derived counts | `test_golden_context_records_attempt_authority_and_derived_counts` |
| Duplicate keyword, identical enrichment → one Observation, all occurrences | `test_identical_duplicate_returned_keyword_collapses_with_both_occurrences` |
| Conflicting enrichment → whole-unit rejection | `test_conflicting_duplicate_enrichment_rejects_the_whole_unit`, `test_rejected_unit_leaves_zero_rows_in_every_rk04_relation` |
| Occurrence-only differences never conflict | `test_occurrence_only_differences_do_not_conflict` |
| Monthly array *state* disagreement still conflicts | `test_state_disagreement_on_the_monthly_array_still_conflicts` |
| Equal / conflicting / non-overlapping monthly windows | `test_equal_overlapping_monthly_periods_collapse`, `test_conflicting_overlapping_monthly_volumes_reject_the_unit`, `test_non_overlapping_monthly_windows_union_when_overlaps_agree` |
| Duplicate target in one array → one edge, every occurrence | `test_duplicate_target_in_one_source_array_keeps_every_occurrence` |
| Repeated edge across duplicate sources; self/backward edges | `test_repeated_edge_across_duplicate_sources_collapses_with_occurrences`, `test_self_and_backward_references_remain_admissible_occurrences` |
| `related_keywords` ABSENT/JSON_NULL/STATED-empty with zero edges | `test_related_keywords_absent_null_and_empty_stay_distinct_with_zero_edges` |
| `monthly_searches` ABSENT/null/empty vs stated zero | `test_monthly_absent_null_empty_and_stated_zero_stay_distinct` |
| `search_volume_trend_state` and inapplicable members | `test_search_volume_trend_absent_marks_members_inapplicable` |
| Enrichment ABSENT/JSON_NULL/STATED; child rows only when STATED | `test_enrichment_objects_absent_null_and_stated_emit_child_rows_only_when_stated` |
| Foreign-intent and SERP-type array states, duplicates, empties | `test_array_states_and_duplicates_survive_for_intent_and_serp` |
| Seed vs depth-0 disagreement is two valid identities | `test_seed_disagreement_with_depth_zero_item_is_two_valid_identities` |
| Missing depth-0 row valid; missing/null seed data valid | `test_missing_depth_zero_item_is_valid_testimony`, `test_missing_or_null_seed_keyword_data_does_not_reject` |
| Item without stated `keyword_data` rejects the unit | `test_item_without_stated_keyword_data_rejects_the_whole_unit` |
| Empty / U+0000 / lone-surrogate identity and target strings reject without a crash | `test_inadmissible_identity_keyword_rejects_without_a_crash`, `test_inadmissible_relationship_target_rejects_without_a_crash`, `test_inadmissible_non_identity_text_also_rejects` |
| Stated-empty `core_keyword` remains exact testimony | `test_empty_core_keyword_remains_exact_non_identity_testimony` |
| admitted_empty writes context only; stated seed + empty items is admitted | `test_empty_result_without_seed_data_is_admitted_empty_with_context`, `test_stated_seed_data_with_empty_items_is_ordinary_admitted_testimony`, `test_admitted_empty_writes_subject_bearing_context_and_nothing_else` |
| Parser PROVIDER_ERROR → repository `provider_error`, zero rows | `test_provider_error_becomes_repository_provider_error_with_zero_rows` |
| Body/parser error → `provider_envelope_rejected` | `test_body_parse_failure_is_provider_envelope_rejected` |
| Residual `/attempt` parser failure → integrity failure, not provider fault | `test_residual_attempt_parser_failure_is_integrity_not_provider_fault` |
| Trusted-validator `DocumentError` → integrity failure; Attempt Outcome survives | `test_attempt_validation_document_error_is_an_integrity_failure` |
| Result/echo disagreement stays testimony, never `reconciliation_failed` | `test_result_echo_disagreement_stays_testimony_and_never_reconciliation_failed` |
| Transport states keep their classifications | `test_transport_states_keep_their_existing_classifications`, `test_complete_transport_with_empty_body_is_non_admissible` |
| Full fixture into real PostgreSQL, all twelve relations, content spot checks | `test_derive_rk02_fixture_into_real_postgres` |
| Attempt-stage `authorized_unresolved` without a Capture | `test_attempt_stage_outcome_exists_without_a_capture` |
| Exact-content idempotent re-derivation | `test_rederiving_the_same_capture_is_exact_content_idempotent` |
| Two-database equivalence across all twelve relations | `test_two_databases_are_logically_equivalent_across_all_twelve_relations` |
| Planted extra occurrence/envelope rows fail complete-set | `test_planted_extra_occurrence_rows_fail_complete_set`, `test_planted_extra_envelope_fails_complete_set` |
| Conflicting stored content fails closed | `test_conflicting_stored_detail_content_fails_closed` |
| Missing rebuildable rows restored exactly | `test_missing_rebuildable_rows_are_restored_exactly` |
| Wrong-kind / orphan / state-consistency refused by PostgreSQL | `test_wrong_kind_child_rows_are_refused_by_postgresql`, `test_orphan_child_rows_are_refused_by_postgresql`, `test_state_value_consistency_is_enforced_by_postgresql` |
| Unrelated Attempt cannot influence another Capture's subject | `test_unrelated_attempt_cannot_influence_another_captures_subject` |
| Other adapters skipped; concrete store required | `test_other_provider_adapters_are_skipped`, `test_derive_requires_the_concrete_evidence_store` |
| Zero public network, no credentials | autouse `_no_public_network` guard on every test in the module |

### Verification results

- `uv run pytest -q tests/test_dataforseo_google_related_keywords.py
  tests/test_dataforseo_google_related_keywords_derive.py` → **285 passed** (73.28s);
  201 pre-existing parser tests unchanged, 84 new derivation tests.
- `uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py
  tests/test_dataforseo_ai_optimization_llm_mentions_historical_derive.py` →
  **52 passed** (35.45s).
- Additional unrequested integration check on the schema-sensitive suites
  (`test_provider_recipe`, `test_derive_admitted_results`, `test_keyword_overview_derive`,
  `test_keyword_overview_extended_derive`, `test_dataforseo_google_organic_derive`,
  `test_dataforseo_ai_optimization_search_mentions_derive`, `test_derive_matrix`,
  `test_provider_holdings`) → **131 passed** (147.60s, exit 0); the single warning is the pre-existing
  Starlette/httpx deprecation. This was run because adding twelve relations and re-layering
  `SCHEMA_STATEMENTS` is exactly the change that could break another surface's schema test.
- `uv run ruff check .` → **All checks passed!**
- Targeted mypy over `src` plus every changed test file → **Success: no issues found in 45
  source files**. (Running mypy on the changed test files alone is misleading: without `src`
  on the path every `observatory.*` import reports `import-untyped`.)
- Full configured `uv run mypy` → **14 errors in 5 files (checked 86 source files)**. Compared
  message-for-message and file-for-file against a `git archive` extraction of
  `9eee309bda9111f6a6446189ac2bbb1a050574f6` in a scratch directory, which reports **14 errors
  in 5 files (checked 84 source files)**: the two sorted error lists are **identical**. RK-04
  therefore adds zero mypy errors and repairs none. The five files remain
  `tests/test_grok_dispatcher.py`, `tests/test_github_queue_controller.py`,
  `tests/test_dataforseo_ai_optimization_llm_mentions_historical_paid_probe.py`,
  `tests/test_api_target_metrics.py`, and `tests/test_api_llm_mentions_historical.py` — none of
  them an RK-04 changed path. The 84→86 file delta is the two new RK-04 modules.
- The full suite was not run per this ticket's verification boundary; [CHAZ] supplies final
  full-suite validation at the closure gate.

### Exact semantic decisions implemented

- **Locus.** `seed_keyword_data` and `returned_item` are identity axes for keyword-data and
  monthly kinds, absent from relationship identity because `related_keywords` is an item-level
  member (`_ITEM_KEYS`) that can never appear inside `keyword_data` (`_KEYWORD_DATA_KEYS`).
- **Conflict tuple.** The comparison key for a duplicate returned keyword is the exact set of
  rows that occurrence would persist. Monthly points are therefore excluded *structurally* —
  they live in the separate monthly kind and appear in no keyword-data row — while
  `monthly_searches_state` stays inside the compared keyword-info row. Unequal period windows
  are admissible; a STATED-vs-null series disagreement is still a real conflict. This makes
  "what we compared" and "what we persist" the same object rather than a hand-maintained list.
- **Monthly reconciliation.** Overlapping periods with equal volumes collapse to one
  Observation with every returned-item occurrence preserved; unequal overlapping volumes reject
  the whole unit; non-overlapping windows union.
- **Occurrence content vs identity.** `depth` is occurrence *content* on both the item and
  relationship occurrence relations, not an identity axis, so a contradictory depth for the
  same index fails closed through `_write_closed_row` instead of silently writing two rows.
- **Attempt authority.** The derive revalidates the Capture-cited Attempt through the existing
  public `validate_related_keywords_http_parameters` and passes only the validator-returned
  closed document into `parse_related_keywords`. No third RK-01 validator exists and
  `capture_event.py` is untouched.
- **Integrity vs provider fault.** `parse_related_keywords` validates Attempt context before it
  decodes the body, so a residual `RelatedKeywordsParseError` whose `path` is `/attempt` or
  starts with `/attempt/` is validator divergence or Evidence damage. It returns `None` from
  `plan_related_keywords_capture`, increments `integrity_failures`, and writes no Capture-stage
  row. All 17 `/attempt` paths in the parser live inside `_request_context`, so the
  discriminator is exact. Every other parse failure is `provider_envelope_rejected`.
- **Inadmissible provider text.** `_require_text` rejects U+0000 and lone surrogates anywhere in
  any persisted string; `_require_identity_text` additionally rejects the empty string for
  identity axes. Verified before this rule existed: RK-03 parses all three hostile strings
  cleanly, `canonical_json` raises `DocumentError` on a lone surrogate, and a NUL reaches
  psycopg. Both would have escaped the derive run as uncaught exceptions.
- **Trend members.** When `search_volume_trend` is not STATED its three members are recorded as
  `inapplicable` with NULL values — the recipe-defined state for "the enclosing structure did
  not state this field", rather than reusing the enclosing object's own state.

### Weakest / most fragile areas

1. **The `_comparable` conflict key is the load-bearing rule and is structural, not explicit.**
   It compares the whole planned payload. That is deliberate — it cannot drift out of sync with
   what gets persisted — but it also means *any* future column added to a keyword-data relation
   silently joins the conflict tuple. If a genuinely occurrence-local field is ever added to one
   of relations 1–6, duplicate returned keywords would start rejecting. The rule belongs in the
   Recipe semantics, so such a change already requires new Recipe bytes; still, this is the
   single place where a well-meaning schema edit could change admission behaviour.
2. **`inapplicable` for unstated trend members is a Recipe invention, not provider testimony.**
   It is defensible under D11's "recipe-defined inapplicability", and `search_volume_trend_state`
   independently preserves the enclosing state, but a consumer could misread the member state.
   No frozen-Capture row exercises it — only synthetics do.
3. **Performance.** One full-fixture derive writes 1530 envelopes, 1530 semantic details, 366
   child rows, and 1517 occurrence rows. `write_observation_envelope` re-reads and re-validates
   the stored Recipe per envelope (~0.9 ms each, measured), so a single derive is several
   seconds. The RK-04 module runs 84 tests in ~73 s with only five full-fixture derives; every
   other PostgreSQL test uses a two-item synthetic body. This is a shared-substrate cost, not an
   RK-04 defect, and `provider_recipe.py` was deliberately left untouched per the ticket.
4. **The provider-error branch remains entirely synthetic.** No real Related Keywords error
   envelope has ever been observed; RK-02 returned `20000`.
5. **`test_derive_requires_the_concrete_evidence_store`** builds its subclass instance by
   copying `__dict__`, which is a slightly artificial construction of an object the production
   path would never see.

### False-green risks I deliberately closed

- Counting envelopes alone would pass if `locus` were dropped (80/960 instead of 81/972), so the
  golden test asserts both loci exist for the identical string `conspiracy theories`, that their
  two digests differ, and that each digest equals the recipe's own identity document recomputed
  independently.
- `count(distinct target) == 246` would pass with all 167 frontier strings replaced, so the test
  asserts the exact set difference and pins `conspiracy theories podcast - youtube` by name with
  its source, depth, target index, and the absence of any keyword-data or monthly row for it.
- Every relationship and monthly occurrence is 1:1 with its semantic row in this Capture, so the
  occurrence layer is untestable from the fixture alone. Synthetic duplicate-keyword,
  duplicate-target, and repeated-edge proofs exist precisely to catch an implementation that
  emitted occurrences from the semantic list instead of the provider array.
- All five depth-0 clocks are distinct in the fixture, so "distinct" proves nothing about
  attribution; the test pins each named clock to its exact per-structure value, and a second
  test asserts no `provider_update_time` column exists in the live catalog.
- `monthly_searches`, `related_keywords`, and the enrichment objects are uniform across all 80
  fixture rows, so their state columns would be invisible to golden tests; each branch has a
  dedicated synthetic proof.

### Explicit unproven limits

This commit proves Recipe-v1 interpretation and persistence of one Capture plus synthetic
mutations. It does **not** establish: any provider invariance behind the 1530 counts; stable
ordering, fanout, or tie-break behaviour; the meaning of `related_keywords: null`; why 167
targets lack enriched rows; twelve-row monthly recurrence; field nullability across Captures;
closure of any provider vocabulary; the semantic status of the year-1 SERP clock; real
provider-error envelope shape; `limit`/`offset` pagination; a billing formula; or any
cross-surface equivalence with Keyword Overview. It decides nothing about recipe selection, the
read API, canonical keyword identity, graph union across Captures, centrality, importance, or
Strategy — all RK-05 or later. `reconciliation_failed` is declared in the closed taxonomy but
has no emission path in Recipe v1 and is therefore untested as a produced Outcome.

### Zero provider / network / credential / Evidence confirmation

No DataForSEO or other provider request was made and no public-network I/O occurred: the derive
test module installs an autouse guard that fails any non-loopback `socket.create_connection`,
and the parser module's existing guard is unchanged. No credentials were read; the guard also
deletes both DataForSEO environment variables. The protected RK-02 Evidence root was never
opened — every test reads only the committed Conformance fixture and Evidence stores created
under `tmp_path`. No Evidence was created, mutated, or deleted outside those temporary stores.
PostgreSQL use was limited to per-test disposable databases from the existing `postgres_dsn` /
`postgres_second_dsn` fixtures. No restic, rclone, or backup operation ran. Nothing was amended
and nothing was pushed.
