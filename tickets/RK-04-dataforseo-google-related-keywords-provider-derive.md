# RK-04 — DataForSEO Google Related Keywords Derivation Recipe and typed persistence

**Status:** draft — mandatory read-only technical review required before implementation  
**Owner:** [CLAUDE] implementation / [GPT] Steward review  
**Blocked by:** none; RK-03 closed  
**Draft base:** `1739147fadf5b666608d82cfa73b159781c323ea`  
**Product direction:** continue the bounded Related Keywords MVP slice; no provider call is needed  

## Purpose

Implement the first content-addressed Derivation Recipe, semantic Observation identities,
typed PostgreSQL persistence, and deterministic rebuild proof for the exact closed adapter:

    dataforseo-labs-google-related-keywords-live-paid-probe-v1

RK-04 is the semantic/persistence half of the Related Keywords vertical slice. RK-05 remains
the separate recipe-selection and consumer API boundary.

The job is to make the useful RK-02/RK-03 provider testimony durable without pretending the
Related Keywords response is a tree, without collapsing frontier strings into invented
enriched nodes, and without treating Keyword Overview look-alike structures as proven
cross-surface equivalents.

No provider exchange, credentials, spend, new Evidence, API, Strategy state, Ranked Keywords,
cross-surface normalization, recurring acquisition, or generic Labs framework is authorized.

This ticket is intentionally provisional until the designated Writer performs a code-first,
read-only adversarial review. No implementation may begin from this draft.

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

## Core semantic rule

**Related Keywords remains its own provider surface.** RK-04 must not reuse Keyword Overview
Observation kinds, semantic subject identity, reconciliation, or Recipe merely because
`keyword_info`, monthly searches, properties, backlinks, and intent have similar JSON
shapes. RK-02 explicitly found material differences in subject grain, relationship context,
SERP testimony, field availability, and sentinel-shaped clock behavior.

Mechanical provider-writer patterns may be reused. Cross-surface semantic equivalence is not
accepted in this ticket.

## Provisional three-kind model for adversarial review

The Writer must challenge this decomposition before implementation. The final ticket may
change it if repository evidence shows a cleaner or more faithful boundary.

### 1. Related Keywords keyword-data testimony

Candidate kind:

    dataforseo.google.related_keywords.keyword_data.v1

Candidate semantic identity axes:

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
such as array index or depth must not create a new semantic keyword-data Observation. The
technical review must decide the exact whole-unit rule for conflicting enrichment between
duplicate semantic keyword occurrences; the default candidate is fail-closed
`provider_envelope_rejected`, matching Search Mentions same-identity-content precedent rather
than choosing first/last testimony.

The technical review must also decide whether a returned item whose `keyword_data` is absent
or JSON null can be semantically admitted at all. The provisional rule is that a returned
item lacking a stated exact keyword cannot form the candidate semantic identity and therefore
rejects the Capture-stage semantic unit rather than being silently dropped.

### 2. Related Keywords monthly search-volume testimony

Candidate kind:

    dataforseo.google.related_keywords.monthly_search_volume.v1

Candidate semantic identity axes:

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
may collapse to one semantic monthly fact while all occurrences survive; conflicting values
provisionally reject the whole Capture-stage semantic unit. Unequal period windows may admit
the union when overlapping values agree. The technical review must verify this against
AI-05 and current complete-set mechanics rather than accepting it by analogy alone.

Current `keyword_info.search_volume` remains keyword-data detail and is never derived from the
newest monthly point. The frozen Capture has 63/80 returned items where those values differ.

### 3. Related Keywords relationship testimony

Candidate kind:

    dataforseo.google.related_keywords.relationship.v1

Candidate semantic identity axes:

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
The technical review must decide where those three source-level states belong in typed
persistence so a null/empty/absent list is not falsely represented as "no semantic edges"
with its state erased.

## `core_keyword` boundary

The provisional model does **not** add a fourth canonical/core relationship Observation.
`core_keyword` remains an exact field-state/value inside keyword-data testimony. This keeps
the provider's separate reference layer recoverable without claiming that it is canonical
identity, synonym equivalence, or a graph edge of the same semantics as `related_keywords`.

The technical review must explicitly challenge this choice. A separate semantic reference
kind is justified only if the current provider/Recipe substrate needs one to preserve a
materially distinct queryable fact without duplication or false equivalence.

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

The technical review must decide whether any result/Attempt disagreement should produce
`reconciliation_failed`. The default candidate is conservative: do not invent equality
requirements for result seed/location/language merely because RK-02 happened to agree, unless
the accepted contract or existing authority makes that reconciliation semantic and necessary.

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

The technical review must state the exact persistence naming for SERP clocks so the schema
does not accidentally teach downstream consumers that the year-1 value has resolved semantic
meaning.

## Outcome and failure behavior

Attempt-stage classification remains:

    authorized_unresolved

Candidate Capture-stage taxonomy is the accepted provider set:

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

Candidate rules:

- no-response/partial/non-admissible transport retain their existing transport outcomes;
- `RelatedKeywordsParseError` produces `provider_envelope_rejected` unless a narrower
  already-accepted mapping is proven by precedent;
- parser `PROVIDER_ERROR` produces `provider_error` with zero normal rows;
- semantic identity failure or conflicting same-identity detail produces
  `provider_envelope_rejected` for the entire Capture-stage unit;
- actual Recipe reconciliation failure produces `reconciliation_failed`;
- a successful result with no semantic Observations produces `observation_admitted_empty`;
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
7. revalidate the committed Attempt parameters using the accepted RK-01 parameter contract;
8. verify a complete Capture body through `EvidenceStore.read_capture_body`;
9. pass only verified parameters and verified body bytes into `parse_related_keywords`;
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

Under the provisional three-kind model the RK-02 fixture should yield:

- 81 semantic keyword-data Observations: one `seed_keyword_data` locus plus 80 unique
  `returned_item` keyword identities;
- 972 semantic monthly search-volume Observations: 12 seed-path points plus 960 item points;
- 477 semantic relationship Observations in this Capture because every observed source
  keyword is unique and no source array repeats a target;
- **1530 total semantic Observation envelopes** if the provisional model survives review.

These are frozen-Capture consequences, not provider invariants. Tests must independently
derive the counts from the fixture and separately prove duplicate/reorder behavior with
synthetic mutations.

The occurrence model must also make the following RK-02 facts independently recomputable
without storing them as semantic conclusions: 246 distinct relationship targets, 167
frontier-only target strings, returned-target depth deltas `+1:96, 0:96, -1:69, -2:21`, and
67 multiply referenced targets with maximum observed incoming occurrence count 26.

Do not persist centrality, in-degree, frontier classification, depth deltas, or importance as
new semantic facts in RK-04. They are recomputable consequences of provider testimony.

## Required adversarial review before implementation

[CLAUDE] must perform a code-first read-only review from the exact draft commit and return
`READY`, `RECONCILE`, or `NOT_READY` before implementation. At minimum challenge:

- whether the three-kind model preserves the materially useful testimony without either
  over-fragmenting Observations or hiding independent Data Period facts inside one blob;
- whether `locus` belongs in keyword/monthly semantic identity;
- whether `core_keyword` should remain detail only or earn a separate reference kind;
- whether Related Keywords may safely reuse **any** Keyword Overview Observation kind or
  whether doing so still makes an unsupported equivalence claim;
- duplicate returned-keyword semantics and exact occurrence/content-conflict handling;
- relationship semantic identity versus item/reference occurrence identity;
- preservation of absent/null/empty `related_keywords` source state;
- seed-path disagreement versus depth-0 item disagreement;
- request/result reconciliation and which disagreements, if any, are actual Recipe failures;
- SERP year-1 clock naming/semantics;
- current search volume versus monthly Data Period separation;
- array order/duplicate preservation for categories, foreign intents, SERP types, and
  relationships;
- the exact bounded schema shape, relation count, and foreign-key structure;
- complete-set and two-database equivalence coverage;
- changed-path allowlist sufficiency;
- false-green tests that could pass while losing frontier or occurrence testimony;
- whether any proposed rule accidentally turns a one-Capture pattern into an invariant.

The review may recommend a different semantic decomposition, but must not write code or
expand RK-04 into API, Ranked Keywords, Strategy, or cross-surface refactoring.

## Provisional changed-path allowlist

Implementation should fit inside:

- `src/observatory/dataforseo_google_related_keywords.py` — Recipe/kind constants and only
  bounded IR additions required for persistence;
- `src/observatory/google_related_keywords_derive.py` — new provider derive module;
- `src/observatory/migrate.py` — additive RK-04 schema only;
- `tests/test_dataforseo_google_related_keywords.py` — only if an accepted IR extension
  requires parser-level proof;
- `tests/test_dataforseo_google_related_keywords_derive.py` — new derivation/persistence tests;
- this ticket — status/report only.

If a recipe fixture or another production/helper path is genuinely required, stop and
reconcile the allowlist before implementation. Do not widen it opportunistically.

## Verification boundary

The final ticket must define a bounded targeted PostgreSQL/TDD loop after review. The Writer
also runs the repository-required checks before its implementation commit.

Known repository baseline at this draft base: full configured `uv run mypy` already has the
inherited 14 errors in five untouched test files recorded at RK-03 closure. RK-04 must add
zero new mypy errors and must not widen scope to repair that separate defect. The Writer must
report both targeted changed-file type checking and the full configured mypy comparison.

[CHAZ] supplies the final full-suite validation at the RK-04 closure gate under current
project process.

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
