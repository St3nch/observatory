# RANK-05 — DataForSEO Google Ranked Keywords Derivation Recipe and typed persistence

**Status:** provisional Steward draft — [CHAZ] designated [CLAUDE] as Writer; awaiting code-first [CLAUDE] review, independent [GROK] review, and Steward reconciliation; no implementation authorization  
**Owner:** [CLAUDE] designated Writer / [GPT] Steward / [GROK] independent reviewer  
**Blocked by:** no technical blocker; RANK-04 closed at `ecfd6cfb90e7162081f64ae02e410e0cf056eaf4`  
**Draft base:** `ecfd6cfb90e7162081f64ae02e410e0cf056eaf4`  
**Provider authority:** zero calls, zero spend; existing protected RANK-03 Evidence and frozen RANK-04 Conformance fixture only  

## Purpose

Design and, only after the full review/authorization sequence, implement the first
content-addressed Derivation Recipe, semantic Observation identities, typed PostgreSQL
persistence, and deterministic rebuild proof for the exact closed Ranked Keywords adapter:

    dataforseo-labs-google-ranked-keywords-live-paid-probe-v1

RANK-05 is the semantic/persistence half of the Ranked Keywords vertical slice. A later
separately reviewed ticket owns Recipe selection and read/history API behavior.

The job is to make the materially useful RANK-03/RANK-04 testimony rebuildable while keeping
four boundaries honest:

1. target-level corpus aggregates are not the returned 100-row prefix;
2. provider rank-group and absolute-rank testimony are distinct and unreconciled;
3. embedded Ranked keyword enrichment is not automatically Keyword Overview or Related
   Keywords semantic identity;
4. exact URLs/domains/hosts remain provider strings, not canonical Page identity or Strategy.

No provider exchange, credentials, spend, new Evidence, API, recipe selection, Strategy,
scoring, recommendation, canonical-page policy, cross-surface normalization, pagination,
recurring acquisition, or generic Labs framework is authorized by this ticket draft.

## Authority and accepted foundation

- VISION data doctrine and survival requirement.
- VOCABULARY definitions of Evidence, Outcome, Observation, Derivation, Derivation Recipe,
  Provider Update Time, Data Period, Conformance fixture, and Strategy.
- D11 — provider Derivation is recipe-addressed, typed, exact-content, and time-explicit.
- D12 — claimed contract + bounded real Evidence; one Capture proves testimony, not invariance.
- D13 — useful measurement coverage is product direction, not standing acquisition authority.
- D14 — later consumer resources remain surface-explicit; Strategy is an ordinary downstream
  API consumer and does not own Observatory persistence semantics.
- PF-12 — semantic Observation versus provider occurrence and exact complete-set precedent.
- PF-14/PF-15 — verify-on-read and additive migration precedent.
- AI-11 — provider aggregate facts may be Observations while request/grouping restatements stay
  typed context.
- RK-04 — surface-local keyword-data/monthly semantics, duplicate reconciliation, exact field
  states, structure-local clocks, and deterministic rebuild precedent.
- RANK-01 — activation analysis and explicit rank/aggregate/keyword-data identity traps.
- RANK-02 — exact closed Attempt contract.
- RANK-03 — protected real Evidence and full-body data review.
- RANK-04 — strict parser, exact Conformance fixture, and parser-only testimony boundary.

Fixed RANK-03/RANK-04 body:

- `tests/fixtures/dataforseo_google_ranked_keywords_rank03.json`;
- `390955` bytes;
- SHA-256 `5b0e7cb6a03a921039a2845c62bd6a91eba9d61e2b54240e9af15414ba1fbc84`.

Fixed parser contract:

    dataforseo-labs-google-ranked-keywords-live-paid-probe-parser-v1

The accepted Capture is a **100-of-248 returned prefix**, ordered by provider
`rank_group,asc`, with five requested target-level aggregate families, 100 unique returned
keyword strings, 57 unique exact URLs, 1200 monthly rows across two row-local windows, and
independent Ranked-element / keyword-SERP clocks. Those are fixture facts, never production
constants.

## Provisional semantic decomposition — review target, not implementation authority

The smallest currently defensible model appears to have **four semantic families**. The
reviews must try to disprove this decomposition before accepting it.

### Candidate 1 — target corpus metrics

Candidate kind:

    dataforseo.google.ranked_keywords.corpus_metrics.v1

Provisional semantic identity:

- exact requested target from the verified Attempt;
- exact requested/result aggregate family name:
  `organic|paid|featured_snippet|local_pack|ai_overview_reference`.

One candidate Observation should preserve both independently stated aggregate loci for that
family:

- `metrics.<family>` — 12 rank-group buckets + count + ETV + estimated paid traffic cost +
  movement counts + clickstream states;
- `metrics_absolute.<family>` — 12 absolute-rank buckets + movement counts + clickstream
  states, with **no synthesized count/ETV/cost**.

The two structures must remain separately addressable and may disagree arithmetically. The
fixture's organic 248-versus-244 bucket behavior remains testimony only. No bucket-sum,
family-sum, count, returned-prefix, movement, or total-count equation belongs in Recipe v1.

The reviews must explicitly decide whether one Observation carrying two sibling structures is
the right fact grain, or whether rank-group and absolute-rank aggregates require separate
kinds/locus axes. Do not split them merely because their SQL shapes differ.

### Candidate 2 — returned ranked placement/result testimony

Candidate kind:

    dataforseo.google.ranked_keywords.ranked_result.v1

This is the largest unresolved semantic question in RANK-05.

The provider row simultaneously states exact keyword, target page URL, open `serp_item.type`,
`rank_group`, `rank_absolute`, layout/host/text attributes, movement/loss testimony,
SERP-composition testimony, rank-info values, and structure-local clocks. Provider array index
is occurrence/order testimony and must never be Observation identity.

Two identity candidates are technically defensible and **must be adjudicated by review**:

**A. Placement-snapshot identity (Organic-like):**

- exact requested target;
- exact provider keyword;
- exact open `serp_item.type`;
- exact `rank_group`;
- exact `rank_absolute`.

Exact URL remains content. This treats a provider rank placement as the semantic fact and
allows the same URL to occupy different placements without conflict.

**B. Target-keyword-page identity:**

- exact requested target;
- exact provider keyword;
- exact `serp_item.url`;
- exact open `serp_item.type`.

Ranks become measured content. This gives a stable same-page grain across Captures but risks
declaring two legitimate same-keyword/same-URL placements to be conflicting testimony.

Reviewers must choose the smallest faithful model from authority + parser + Evidence +
synthetic branches. Do not choose B merely because Strategy will later want rank history, and
do not choose A merely because Google Organic already uses placement axes. RANK-04 explicitly
made Organic a negative structural precedent where the real Ranked testimony differs.

Whichever identity wins, every returned array occurrence must remain recoverable with its
nonnegative `provider_array_index`. Exact apex/`www`, URL, relative URL, domain, main domain,
website name, title/text, position, rank changes, rank info, SERP composition, and both
Ranked-element clocks remain exact typed testimony. No URL/host normalization or inferred Page
identity is allowed.

### Candidate 3 — Ranked-local keyword-data testimony

Candidate kind:

    dataforseo.google.ranked_keywords.keyword_data.v1

Provisional semantic identity:

- exact requested target;
- exact provider keyword string.

This is intentionally Ranked-local. It must not reuse Keyword Overview or Related Keywords
Observation kinds/tables merely because the nested JSON family looks familiar.

Persist the materially useful RANK-04 field states and content: current search demand,
competition/CPC/bids/categories, signed trends, properties/core-keyword/clustering/language,
backlink averages, search intent, nested SERP testimony, clickstream request-disabled states,
and independent Bing state.

If multiple returned ranked rows state the same keyword, the reviews must decide whether
identical enrichment collapses to one semantic keyword-data Observation plus every item
occurrence, and whether conflicting same-identity enrichment rejects the whole Capture-stage
unit. RK-04 Related Keywords is a strong mechanical precedent but not automatic semantic
authority for Ranked Keywords.

### Candidate 4 — Ranked-local monthly search-volume testimony

Candidate kind:

    dataforseo.google.ranked_keywords.monthly_search_volume.v1

Provisional semantic identity:

- exact requested target;
- exact provider keyword;
- provider-stated year;
- provider-stated month.

Persist exact nonnegative search volume and enough item occurrence testimony to show which
returned row(s) carried the point. Provider row order/index is occurrence testimony only.
Monthly `(year, month)` is the Data Period; it never inherits a Capture time or provider update
clock. Current search volume is independent from the newest monthly point.

For duplicate keyword occurrences, review whether equal overlapping monthly values collapse,
conflicting overlaps reject the unit, and non-overlapping windows union — the RK-04 pattern —
or whether Ranked-specific occurrence semantics require a different rule.

## Result context and completeness boundary

Persist exactly one typed result-context row for an admitted/admitted-empty Capture + Recipe.
It should preserve at minimum:

- exact verified Attempt target, location/language, ordered five item types,
  `ignore_synonyms=false`, `include_clickstream_data=false`, `limit=100`, `offset=0`,
  `load_rank_absolute=true`, `historical_serp_mode=all`, and exact `order_by`;
- provider result target/location/language/`se_type` Field states and values;
- independent `total_count` and `items_count`;
- exact returned-item count as a labeled rebuildable count only if useful for complete-set
  proof.

Do not persist a fabricated `complete`, `truncated`, `first_page`, `coverage_percent`, or
`corpus_exhausted` fact. The fixture proves 100 returned rows while `total_count=248`; later API
work must disclose request/prefix context honestly, not turn one request shape into a corpus
claim.

Task echo, cost, durations, task UUID/path, and provider version/status remain typed parser IR
and raw Evidence unless review identifies a concrete persistence need. Attempt parameters are
request authority. Well-typed provider echo/result disagreement must not silently overwrite
them.

## Field states, exact strings, and nested structure

RANK-05 must preserve RANK-04's distinctions rather than flatten them:

- ABSENT / JSON_NULL / STATED / NOT_REQUESTED / recipe-defined INAPPLICABLE where required;
- exact duplicate/order-preserving arrays such as categories, foreign intent, highlighted,
  and SERP item types;
- exact URL/domain/main-domain/website-name/relative-URL/text strings;
- null-only unsupported Ranked SERP children remain a parser-version drift trigger if later
  populated; RANK-05 must not invent their Organic schemas;
- `rank_info.main_domain_rank` remains distinct from
  `avg_backlinks_info.main_domain_rank`;
- Ranked-element keyword difficulty remains distinct from keyword-properties difficulty;
- duplicated Ranked-element versus keyword `serp_info` paths remain independently persisted
  where they carry material testimony; equality in the fixture is not reconciliation.

Identity-bearing/persisted strings must fail deterministically before JCS/PostgreSQL if empty
where identity forbids emptiness or if they contain content the accepted canonical-I-JSON
boundary cannot persist. No psycopg/JCS crash may become accidental classification behavior.

## Time and movement semantics

Time remains explicitly multi-axis:

- Capture/acquisition time = Evidence provenance only;
- monthly `(year, month)` = Data Period only;
- Ranked-element `last_updated_time` and `previous_updated_time` = structure-local provider
  clocks;
- nested keyword `serp_info` current/previous clocks = separate provider paths;
- keyword-info, intent, and backlinks clocks remain their own axes;
- provider duration strings are not timestamps;
- `pre_snippet` remains arbitrary text even when date-looking.

`rank_changes`, element `is_lost`, and aggregate `is_new/is_up/is_down/is_lost` are opaque
provider comparison testimony. They are **not Observatory Capture-to-Capture deltas** and no
Recipe rule may infer one from another or from the previous clock/rank.

The synthetic lost-row branch accepted by RANK-04 must remain representable if otherwise
semantically admissible. One real all-mode Capture containing only `is_lost=false` does not
prove that future lost-row shape or meaning is invariant.

## Outcome and atomicity questions

Attempt-stage classification remains:

    authorized_unresolved

Provisional Capture-stage taxonomy is the accepted provider set:

- `no_response`
- `response_partial`
- `transport_complete_non_admissible`
- `provider_error`
- `provider_envelope_rejected`
- `reconciliation_failed`
- `observation_admitted`
- `observation_admitted_empty`

Repository Outcome is Recipe-owned and must never be copied directly from parser-local
`ParseClassification` text.

The reviews must decide whole-unit behavior for a successful parser IR containing a returned
item with `keyword_data` or `ranked_serp_element` ABSENT/JSON null. Candidate policy is
fail-closed whole-unit `provider_envelope_rejected` when the missing structure prevents a
required semantic identity; do not silently admit corpus metrics while dropping malformed
returned rows unless authority explicitly accepts partial semantic admission.

Likewise, same-identity conflicting detail should fail the whole Capture-stage semantic unit,
not use first/last wins or `ON CONFLICT DO NOTHING`.

## Verified production Evidence boundary

Production Derivation should reuse the mature provider authority chain:

1. require concrete `EvidenceStore`;
2. verify-on-read each committed Ranked Keywords Capture;
3. require exact Ranked adapter on Capture;
4. obtain the exact Attempt ID cited by that Capture;
5. verify-on-read that exact committed Attempt and adapter;
6. require Mapping parameters and revalidate them through existing public
   `validate_ranked_keywords_http_parameters`;
7. verify complete body bytes through `EvidenceStore.read_capture_body`;
8. pass only validator-returned closed parameters + verified body to
   `parse_ranked_keywords`;
9. plan one exact Recipe semantic unit;
10. atomically write/compare the complete intended Outcome/context/envelope/detail/occurrence
    set.

`DocumentError`, damaged citation/Attempt/body, adapter mismatch, or residual parser failure
under `/attempt` is Evidence integrity failure, not provider testimony. Body parser failure is
`provider_envelope_rejected`; parser `PROVIDER_ERROR` becomes repository `provider_error`.

An unrelated valid Ranked Attempt in the same EvidenceStore must never influence the Capture
that cites another Attempt.

## PostgreSQL / Recipe direction — deliberately not frozen yet

Reuse generic `provider_recipes`, `outcomes`, `observation_envelopes`, and
`derivation_diagnostics`. Add Ranked-specific typed relations only after semantic identities
are reconciled.

Likely relation families include:

- target corpus-metric semantic parent with separate rank-group and absolute-detail shapes;
- ranked-result semantic parent plus returned-item occurrence testimony;
- Ranked-local keyword-data semantic parent and stated enrichment child structures;
- monthly semantic parent plus returned-item monthly occurrences;
- one result-context relation.

The reviews must minimize unnecessary table count while still preserving nested Field states,
exact arrays, independent clocks, and kind-bound foreign keys. A wide typed row is acceptable
when semantically honest; table splitting is not a virtue by itself.

Migration should likely introduce `PRE_RANK05_SCHEMA_STATEMENTS` equal to the exact schema at
RANK-05 start, then append only Ranked relations. The Writer review must trace which existing
migration-baseline tests would need a minimal retarget. Current Related Keywords tests still
compare `SCHEMA_STATEMENTS` directly against the RK-04 delta and are a known likely affected
precedent; do not widen other tests speculatively.

## Required pre-implementation code-first questions

The designated Writer must inspect authority/code/schema/tests/fixture and return a read-only
review that answers at least:

1. Which ranked-result identity candidate (A, B, or a third exact alternative) is faithful,
   and what synthetic duplicate case disproves the rejected candidate(s)?
2. Should `metrics` + `metrics_absolute` be one corpus-metrics Observation per family with two
   sibling typed structures, two Observation kinds, or one kind with an explicit locus axis?
3. Does Ranked keyword-data identity require requested target as an axis, or would that encode
   request context as false semantic identity? Explain against RK-04/D12 rather than visual
   JSON similarity.
4. How should duplicate same-keyword enrichment and monthly periods reconcile across multiple
   returned rows?
5. Which returned-item structures are required for Recipe admission versus permitted Field
   states, especially `keyword_data` and `ranked_serp_element`?
6. Does well-typed result/echo target/locale disagreement remain provider testimony, or is any
   exact Recipe reconciliation justified?
7. What exact Ranked-element / SERP-item content belongs on semantic detail versus occurrence
   detail under the chosen identity?
8. How are `is_lost`, rank-change members, previous rank, and previous clocks preserved without
   inventing longitudinal Observatory change?
9. Which exact aggregate and item clickstream states need PostgreSQL CHECKs under the frozen
   request-disabled flag?
10. What is the minimum faithful relation set and exact migration-layer impact?
11. Which current schema-sensitive tests genuinely require a baseline retarget?
12. What golden and synthetic tests are needed to prove exact-content idempotency,
   duplicate/reorder behavior, complete-set equality, and two-database rebuild equivalence?

The Writer must also report Product questions, if any. No Product question should be invented
for a code/authority answer that can be resolved read-only.

## Independent adversarial review requirement

After the designated Writer's review, [GROK] must independently review the same clean ticket
HEAD without reading the Writer report. The Steward then reconciles both reports into one final
semantic/persistence contract. Only after that reconciliation may [CHAZ] separately authorize
implementation from an exact clean accepted-ticket HEAD.

## Provisional changed-path ceiling

No path is implementation-authorized yet. The expected maximum implementation surface is:

- `src/observatory/dataforseo_google_ranked_keywords.py` — Recipe/kind constants and only
  bounded IR additions genuinely required by accepted persistence;
- new `src/observatory/google_ranked_keywords_derive.py` — Ranked provider Derivation;
- `src/observatory/migrate.py` — additive pre-RANK-05 layering + Ranked typed relations;
- `tests/test_dataforseo_google_ranked_keywords.py` — only if a reviewed IR addition needs
  parser proof;
- new `tests/test_dataforseo_google_ranked_keywords_derive.py` — derivation/PostgreSQL tests;
- `tests/test_dataforseo_google_related_keywords_derive.py` — only the minimal migration-
  baseline retarget if required to preserve the existing RK-04 delta assertion;
- this RANK-05 ticket — review/authorization/implementation bookkeeping.

The code-first reviews must verify this ceiling is sufficient. Do not edit `capture_event.py`,
`provider_recipe.py`, `derive.py`, API/selection modules, fixtures, or another provider surface
unless the Steward explicitly reconciles a proven need before implementation.

## Verification direction

Writer implementation verification, if later authorized, should follow current project
cadence:

- bounded Ranked parser/derive tests;
- any specifically affected migration-baseline test module;
- `uv run ruff check .`;
- targeted mypy over changed Ranked source/tests;
- configured repository mypy compared message-for-message to the exact start baseline.

Ordinary tests perform zero provider/DNS/public-network activity and require no credentials or
protected Evidence root. Use small synthetic bodies for most adversarial persistence tests and
limit full-fixture PostgreSQL derives to the golden/rebuild proofs that genuinely need them.

The designated Writer does not run the final full repository pytest suite unless the accepted
ticket explicitly changes current workflow. [CHAZ] supplies final full-suite integration
validation before Steward closure.

## Explicit out of scope

- any new DataForSEO request, pricing/account call, credentials, spend, or Evidence mutation;
- Recipe selection or read/history API;
- offset pagination / second-page acquisition;
- clickstream-enabled acquisition;
- exact-page target adapter or another historical mode;
- canonical Page/domain/brand/keyword/topic identity;
- URL normalization, apex/`www` collapse, or redirect resolution;
- cross-surface Keyword Overview / Related Keywords / Organic semantic unification;
- Capture-to-Capture rank delta calculation;
- competitor gaps, content opportunities, priority, scoring, recommendation, or Strategy;
- generic Labs parser/derive framework;
- recurring acquisition/F12;
- fixing unrelated inherited mypy or warning debt.

## One eventual implementation must prove

One verified Ranked Keywords Capture can be deterministically re-derived under one exact
content-addressed Recipe into typed, provenance-bound **target corpus aggregate, returned rank,
Ranked-local keyword enrichment, and monthly Data-Period testimony**, while preserving the
100-of-248 prefix boundary, exact provider occurrence/order, independent rank systems,
movement/loss testimony, URLs/hosts, field states, and structure-local clocks — without
inventing completeness, canonical pages, cross-surface equivalence, longitudinal change, or
Strategy meaning.
