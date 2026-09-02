# PF-18 — Google Organic MVP testimony completion

**Status:** review — bounded integrity remediation required  
**Kind:** provider fidelity remediation  
**Triggered by:** MVP-01 Class 4 Google Organic finding  
**Blocked by:** none for the bounded PF-18 implementation  
**Approved by:** [CHAZ] for bounded implementation on 2026-09-01  
**Draft base:** `0465a5b6e3bb9c4e56aa613f5d61581620e46096`  
**Implementation start:** `404d3bebce3755c33989e10fe63559bd8ac89616`  
**Implementation Writer:** [CLAUDE]  

## Why this ticket exists

MVP-01 re-reviewed the exact protected PF-10 Google Organic provider body, SHA-256
`7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`, against the accepted
PF-11/PF-12 parser, Recipe, persistence, and read API. The six-kind v1 slice is faithful to
what it deliberately models, but the exact live body contains additional materially useful
SERP testimony that an API-only consumer cannot currently obtain:

- child Top Stories results with exact source/domain/title/URL/item-timestamp testimony;
- child Video results with exact source/title/URL/item-timestamp testimony;
- provider-stated item/result timestamps on returned organic ranked results; and
- sitelink relationships under an organic ranked result, including child title/URL/domain
  and nullable description testimony.

PF-11 intentionally left these structures raw to keep the first Google Organic Recipe bounded.
That was an accepted sequencing choice, not an implementation bug at PF-11 closure. The later
MVP fidelity gate now makes the missing consumer-visible relationships material: Observatory's
product doctrine prefers preserving historically irrecoverable query → ranked/feature result →
exact URL relationships and independent provider time testimony when the provider actually
returned them. Raw Evidence remains authority, but API-only consumers cannot use raw Evidence.

This ticket closes that one under-modeling gap. It is not authorization to type every PF-10
field or redesign Google Organic generally.

## Evidence and immutable baseline

Use only the existing exact PF-10 Conformance fixture, which MVP-01 independently proved
byte-identical to the verify-first restored protected Evidence body:

- fixture: `tests/fixtures/dataforseo_google_organic_pf10.json`;
- bytes: `135722`;
- SHA-256: `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`;
- Attempt: `acfdb7a06a5c2d1af4c00fc8518a08891d1a083bc13d59149916b707c5d7ed34`;
- Capture: `ff17d3d56e29281984c2171cf9dc065d47105a36116a4723dbe75e4c8a9c3c27`.

No provider request is needed or authorized. The accepted PF-11 Recipe bytes/digest and all
v1 historical rows remain immutable. A semantic expansion must use a new Recipe identity;
do not silently reinterpret the old Recipe or overwrite old derived rows.

## Consumer questions this remediation must make answerable

An ordinary API-only consumer, using the new accepted Recipe, must be able to answer from one
Google Organic Capture:

1. Which exact Top Stories child results did the provider return, and what source/domain,
   title, URL, and provider-stated item timestamp did each carry?
2. Which exact Video child results did the provider return, and what source, title, URL, and
   provider-stated item timestamp did each carry?
3. For each organic ranked placement, did the provider state an item/result timestamp and, if
   so, what exact timestamp did it state?
4. Which sitelink child relationships were returned under which exact organic placement, and
   what exact title/URL/domain/description state/value did each carry?

The answer must retain parent placement and child occurrence context without inventing a
canonical Page, Brand, entity, relevance score, or cross-surface identity.

## Required semantic boundaries

### Existing v1 semantics survive unchanged

The accepted PF-11/PF-12 Google Organic Recipe remains addressable and reproducible exactly as
before. Existing six-kind v1 observations, counts, identities, result context, API behavior,
and Recipe digest must not change merely to add the MVP-completion view.

The implementation must introduce a new content-addressed Recipe for the expanded semantics.
Whether the cleanest implementation uses a new parser-contract version, new Observation-kind
versions, additional kinds, or a combination is a technical design question for the required
code-first review. The final Steward ticket must freeze that choice before implementation.
It is not acceptable to change semantic meaning under unchanged normative Recipe bytes.

### Top Stories children

The exact PF-10 body contains one returned `top_stories` parent with a populated child `items`
array. Preserve the materially useful child testimony at minimum:

- exact source;
- exact domain;
- exact title;
- exact URL; and
- exact provider `timestamp` with explicit field state if the accepted child contract permits
  null/absence.

The parent SERP placement already carries page, position, rank_group, and rank_absolute. Child
array position/order may be preserved as occurrence testimony, but array index must not be the
sole semantic identity. The provider `timestamp` is structure-local item/result testimony;
Observatory does not certify it as an independent publication instant. It is not Capture time,
result retrieval time, Provider Update Time, or Data Period.

### Video children

The exact PF-10 body contains one returned `video` parent with a populated child `items` array.
Preserve at minimum exact source, title, URL, and provider `timestamp`, plus enough parent and
occurrence context to distinguish what the provider actually returned. Do not treat child
position as a universal Google rank or infer a canonical video/entity identity from the URL.

### Organic item/result timestamp

PF-10 contains organic placements with both stated and JSON-null provider `timestamp` values.
The expanded contract must preserve that distinction for each placement. PF-11's claimed-contract
discussion described this as result publication date/time, but PF-10 contains enough
retrieval-adjacent values that Observatory must not strengthen the provider field into a
certified independent publication instant. Name/document it as exact provider-stated organic
item/result timestamp testimony. It is not Provider Update Time, Capture time, result
`datetime`, or Data Period and must never inherit from a sibling clock, `pre_snippet`, relative
`date` text, or another row.

### Organic sitelinks

At least one PF-10 organic placement carries a populated child `links` array. Preserve the
relationship from the exact parent placement to every returned sitelink child, including exact
title, URL, domain, and description state/value admitted by the frozen body/claimed contract.
Child URL must not become a canonical Page ID. Preserve duplicate occurrences rather than
silently set-deduplicating them unless the final reviewed semantic identity explicitly proves a
safe separate occurrence model.

The parent ranked-result contract must preserve the `links` family state independently of child
rows so absent, JSON null, stated-empty array, and stated-populated array cannot collapse into
the same "no child row" representation.

## Deliberately not pulled into PF-18

The MVP finding does **not** require this ticket to expose:

- full AI Overview prose/markdown or sentence/token citation mapping;
- PAA expanded-answer content;
- images/CDN presentation data, xpath, rectangles, highlights, breadcrumbs, cache URLs,
  ratings, prices, AMP flags, `checks`, or decorative presentation fields merely because
  they exist;
- top-story image URLs or relative-date presentation strings; PF-18 preserves the provider
  `timestamp` itself and does not infer it from those presentation fields;
- unobserved populated `related_result`, rating, price, right-rail, or other hypothetical
  branches;
- URL normalization, redirect resolution, canonical Page/domain/site identity, cross-surface
  joins, scores, Strategy recommendations, or trend calculations;
- another provider request, pagination, PAA clicking, asynchronous follow-up, recurring
  acquisition, F9, F12, or F13 work.

If the Writer believes one excluded field is semantically inseparable from the four required
families, report that in pre-implementation review rather than silently broadening scope.

## Completeness and inference limits

- PF-10 is one exact depth-100 Google Organic Capture whose result reports `pages_count=10`
  and `items_count=111`. Neither depth nor these counts prove provider-corpus completeness.
- This ticket preserves every admitted child occurrence of the four required families in the
  exact returned body; it does not claim those families always exist or always have this shape.
- Top Stories/Video child order is returned occurrence testimony, not importance or rank unless
  a provider field explicitly states a rank.
- Organic item/result timestamps are provider-stated facts for individual results; missing or
  null time must not be filled from result `datetime`, Capture time, `pre_snippet`, relative
  date text, or another row, and Observatory does not certify them as independent publication
  instants.
- One observed sitelink shape proves existence only. Bounded synthetic mutations must prove
  duplicate/null/absence/drift behavior without another live call.
- Unknown/additive provider fields follow the new Recipe's explicit drift policy; known-field
  type/enum/time/relationship drift fails closed rather than being guessed.

## Provenance and persistence requirements

- Every new normal Observation must use the generic provider envelope and cite exact
  `attempt_id`, `capture_id`, new `derivation_version_id`, provider, adapter contract, kind,
  and collision-resistant within-Capture identity.
- Any subordinate occurrence/relation rows must be structurally bound to the correct typed
  parent(s), not merely share strings by convention.
- The new Capture-stage derive unit is atomic across Outcome, result context, envelopes,
  typed details, occurrences, and diagnostics.
- Same-Recipe rerun compares intended content and complete sets; missing rebuildable rows may
  be restored, while extra/conflicting rows fail closed. Do not use conflict-ignore or
  last-write-wins as semantic equality.
- Empty PostgreSQL rebuild from the same verified Evidence and new Recipe must be logically
  equivalent on real PostgreSQL 18.
- Damage to verified Attempt/Capture/body Evidence must prevent the new Capture-stage facts
  from being served as valid observations.

## API/read requirements

The new Recipe-selected/pinned Google Organic history document must expose the four required
families with their exact provenance and limits while retaining the existing v1 document's
correct distinctions. An API-only consumer must not need direct PostgreSQL or Evidence access.

Before applying the outer history limit, read-side integrity must still establish complete-set
agreement among the new Recipe's Outcome count, envelopes, typed detail rows, subordinate
occurrences, result context, and verified Evidence membership. Tampering or semantic
inconsistency fails closed under the existing integrity-error API convention.

The generated OpenAPI descriptions must teach at least:

- provider item/result timestamp versus Capture time, result retrieval time, Provider Update
  Time, Data Period, and Observatory-certified publication time;
- parent feature/organic placement versus child result occurrence;
- exact URL testimony versus canonical Page identity;
- returned child count/order versus provider/corpus completeness; and
- old pinned Recipe versus the newly selected expanded Recipe.

## Acceptance criteria for the eventual implementation

- [ ] Exact PF-10 fixture bytes/hash remain unchanged and ordinary tests use zero provider
      network activity.
- [ ] Accepted Google Organic v1 Recipe bytes/digest/rows/API remain unchanged and pinnable.
- [ ] A new immutable Recipe identity authorizes the expanded semantics; no semantic change is
      hidden under the old Recipe or parser contract.
- [ ] Every PF-10 Top Stories child required above is represented and API-visible with exact
      parent/occurrence context and no invented rank/Page identity.
- [ ] Every PF-10 Video child required above is represented and API-visible with exact
      parent/occurrence context and no invented rank/Page identity.
- [ ] Stated versus JSON-null/absent organic item/result timestamps survive parser → Recipe →
      PostgreSQL → API without clock inheritance or strengthened publication-time meaning.
- [ ] Every PF-10 sitelink relationship required above is represented and API-visible under its
      exact parent placement; duplicates/order are not silently destroyed.
- [ ] Existing 111 feature placements, 97 organic placements, AIO source relationships,
      PAA questions, related queries, rank axes, result context, and completeness limits remain
      correct under the expanded Recipe.
- [ ] Synthetic reorder/duplicate/null/absence/wrong-type/conflicting-content tests prove the
      chosen semantic identities and occurrence models without live acquisition.
- [ ] Complete-set persistence and read integrity detect missing/extra/conflicting new rows.
- [ ] Two fresh PostgreSQL 18 rebuilds from identical Evidence/new Recipe are logically
      equivalent.
- [ ] API/OpenAPI exposes the required facts, provenance, field states, time distinctions, and
      inference limits and returns the existing integrity failure response on damage.
- [ ] No provider call, credentials, spend, Evidence mutation, Strategy behavior, canonical
      Page identity, recurring acquisition, amend, rebase, reset, or push occurs.

## Required pre-implementation review — completed

The designated Writer must inspect the actual parser, Recipe bytes, migration schema,
Derivation, read models/routes, tests, and exact PF-10 fixture before writing code. Return:

1. any false premise in the four material-family findings;
2. the exact observed PF-10 child cardinalities/state patterns for Top Stories, Video,
   organic publication timestamps, and sitelinks, independently recomputed from the fixture;
3. the smallest Recipe/parser versioning design that leaves v1 reproducible;
4. proposed semantic identity axes and separate occurrence axes for each new relationship,
   with duplicate/reorder consequences;
5. whether publication-time lexical validation can safely reuse an existing Google Organic
   timestamp grammar or requires a separately named rule;
6. the exact existing tables/routes/tests that can be extended safely versus what should stay
   deliberately duplicated;
7. likely false greens and the smallest decisive adversarial tests;
8. any Product question that truly cannot be resolved from existing authority/Evidence; and
9. `READY_FOR_STEWARD_RECONCILIATION` or `NEEDS_RECONCILIATION`.

The review is read-only. It authorizes no implementation, provider/network call, credentials,
Evidence mutation, spend, branch push, or `main` push.

## Independent pre-implementation review — accepted 2026-09-01

The externally run read-only Grok review checked exact clean HEAD
`f6cd92f2a57432e6c576982acc6368bc230be12b`, reported no repository mutation, no tests, and no
provider/credential/Evidence access, inspected the exact PF-10 Conformance body, and returned
`READY_FOR_STEWARD_RECONCILIATION`.

The review independently reproduced the material-family premise and these exact PF-10 facts:

- one `top_stories` parent at page 1 / left / rank_group 1 / rank_absolute 6 with four child
  `top_stories_element` rows; all four state source, domain, title, URL, and timestamp;
- one `video` parent at page 1 / left / rank_group 1 / rank_absolute 7 with three child
  `video_element` rows; all three state source, title, URL, and timestamp and none carries a
  domain key;
- 97 organic placements split exactly 58 stated timestamp / 39 JSON-null timestamp / 0 absent
  timestamp; and
- all 97 organic placements carry a `links` key: one stated-populated array containing four
  `link_element` children, 96 JSON-null values, zero stated-empty arrays, and zero absent keys.
  The four observed sitelinks have stated title/URL/domain and JSON-null description.

The review also confirmed the current drop points: Top Stories and Video parents are reduced to
feature-placement testimony without walking their child arrays; `OrganicPlacement` does not
carry `timestamp`; and organic `links` is known raw JSON but never typed. No existing Recipe,
PostgreSQL relation, or read API can reconstruct those facts without returning to Evidence.

No tests were claimed or accepted from this review. Its role is adversarial contract review,
not implementation validation.

## Steward reconciliation — frozen implementation contract

The Project Steward accepts the Class 4 finding and only those review recommendations that
follow from repository authority, immutable Recipe/version rules, and the exact PF-10 body.
The following are frozen for PF-18 implementation.

### Versioning and coexistence

1. Parser-v1, Recipe-v1 bytes/digest, v1 rows, and pinned-v1 API behavior remain immutable.
   Recipe-v1 remains 2,487 bytes with digest
   `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`.
2. PF-18 introduces parser contract
   `dataforseo-serp-google-organic-live-advanced-paid-probe-parser-v2` and a new
   content-addressed expanded Recipe. Parser-v1 does not validate/type these child subtrees, so
   changing its admission behavior behind the old parser contract is not permitted.
3. The expanded Recipe's ordered Observation kinds are exactly:
   `dataforseo.google.organic.serp_feature_presence.v1`,
   `dataforseo.google.organic.ranked_result.v2`,
   `dataforseo.google.organic.ai_overview_presence.v1`,
   `dataforseo.google.organic.ai_overview_source.v1`,
   `dataforseo.google.organic.related_question.v1`,
   `dataforseo.google.organic.related_query.v1`,
   `dataforseo.google.organic.top_story_result.v1`,
   `dataforseo.google.organic.video_result.v1`, and
   `dataforseo.google.organic.organic_sitelink.v1`.
4. `dataforseo.google.organic.ranked_result.v2` replaces ranked-result v1 only inside the
   expanded Recipe. Its placement identity remains the accepted v1 placement identity; v2 adds
   exact organic timestamp state/value and parent `links` family state as content.
5. The three new child-kind names above are normative Recipe/API vocabulary, not Writer naming
   choices. The expanded Recipe digest is computed only from the final validated canonical JCS
   bytes and must be frozen by implementation tests before any derivation is accepted.
6. The same verified Capture must remain derivable under v1 and the expanded Recipe
   independently. Registering/deriving the expanded Recipe must **not** mutate
   `provider_recipe_selections`; changing the selected Recipe remains a separate explicit
   operator action. Pinned v1 remains reproducible after expanded derivation.

### Identity and occurrence

7. Top Stories child semantic identity is exact requested keyword + exact parent SERP placement
   `(page, position, rank_group, rank_absolute)` + exact child URL. Source, domain, title, and
   timestamp state/value are content. Child array index is subordinate occurrence/order
   testimony, never identity or rank.
8. Video child semantic identity uses the same parent scope + exact child URL. Exact composite
   provider source, title, and timestamp state/value are content. PF-10 has no video-child
   domain key; PF-18 must not derive one from URL.
9. Ranked-result v2 keeps the accepted ranked-result-v1 placement identity. Timestamp and
   `links` family state are content, never identity.
10. Organic sitelink semantic identity is exact requested keyword + exact parent organic
    placement `(page, position, rank_group, rank_absolute)` + exact child URL. Title, domain,
    and description state/value are content; child index is occurrence/order testimony.
11. Reorder leaves semantic identity sets unchanged while occurrence indexes follow provider
    order. Repeated agreeing semantic children produce one semantic envelope with multiple
    occurrences; conflicting content for one semantic identity rejects the whole expanded
    Capture-stage unit. The same URL under another parent placement or Observation kind is a
    distinct fact. No URL becomes canonical Page/Video/Site identity.
12. Every semantic Top Stories child, Video child, and sitelink must have at least one
    structurally bound occurrence row. Missing, extra, or orphan occurrences are integrity
    damage.

### State and time

13. Organic timestamp uses explicit `stated`, `json_null`, and `absent` state/value semantics.
    PF-10 observes 58/39/0; synthetic tests prove the absent branch without claiming it occurred
    live.
14. Organic `links` state is persisted on ranked-result v2 so absent, JSON null, stated-empty,
    and stated-populated remain distinct. PF-10 observes 0/96/0/1 respectively. Child-row count
    is never a substitute for this parent-family state.
15. The same strict UTC lexical grammar may be reused internally for result `datetime` and the
    three item-timestamp families, but each has a separately named semantic field/helper
    boundary. Shared syntax does not imply shared meaning.
16. Item timestamps are provider-stated structure-local item/result time testimony. Observatory
    does not certify them as independent publication instants. They are not Capture time,
    result retrieval time, Provider Update Time, or Data Period and never inherit from result
    `datetime`, Top Stories `date`, organic `pre_snippet`, another row, or Capture provenance.
    `date` and `pre_snippet` remain raw under PF-18.

### Persistence and read boundary

17. Do not ALTER `google_organic_ranked_results` into a second `ranked_result.v1` shape. Add a
    distinct typed relation for ranked-result v2. Existing v1 tables remain historical v1
    relations.
18. Add bounded typed relations for the three new child kinds plus structurally constrained
    occurrence relations. Sitelinks bind to the exact ranked-result-v2 parent; Top Stories and
    Video children bind to their exact parent SERP placement and matching semantic envelope.
19. The expanded derive unit remains atomic and complete-set checked across Outcome, result
    context, generic envelopes, reused/new typed details, subordinate occurrences, and
    diagnostics. `observation_count` counts semantic envelopes only, never occurrences.
20. For the exact PF-10 body, the expected expanded-Recipe semantic envelope count is **248**:
    the prior 237 with 97 ranked-result-v1 envelopes replaced one-for-one by 97 ranked-result-v2
    envelopes, plus 4 Top Stories children, 3 Video children, and 4 sitelinks. This is one
    frozen-Capture expectation, not a provider invariant.
21. Read-side integrity must know every expanded kind/table and occurrence family and validate
    all matching history candidates before the outer history limit. Damage hidden in an
    unreturned tail still produces the existing integrity-failure response.
22. Selected expanded history exposes ranked timestamp/links state plus Top Stories children,
    Video children, and sitelinks with exact parent/occurrence context. Pinned v1 remains the old
    document; API-only consumers require no direct Evidence or PostgreSQL access.
23. Expanded nested Capture/fact models must be typed strongly enough that generated OpenAPI
    attaches time/state/identity/completeness descriptions to the exact properties. Global
    keyword-presence assertions are not sufficient documentation proof.

### Drift and decisive proof

24. Parser-v2 strictly walks the newly admitted child structures and fails closed on known wrong
    types, invalid child type/time/URL shapes, and semantic duplicate disagreement. Non-null
    `related_result` remains outside PF-18 and is treated as known parser-version drift rather
    than guessed or partially typed.
25. Required synthetic proofs include child reorder; agreeing duplicate URL; conflicting
    duplicate content; same child URL under two parent placements; cross-kind URL overlap;
    timestamp null/absent/stated; no inheritance from result datetime/date/pre_snippet;
    midnight/timed forms; missing/extra/orphan occurrences; extra typed row not represented by
    envelopes; stated-empty versus JSON-null links; second Top Stories/Video parent; selected
    expanded versus pinned v1; hidden-tail damage before outer limit; and field-specific
    OpenAPI-description assertions.
26. A v1 immutability regression must prove Recipe-v1 bytes/digest, v1
    `observation_count=237`, v1 semantic/detail sets, and pinned-v1 API shape remain unchanged
    after expanded Recipe registration/derivation.
27. Two fresh PostgreSQL 18 databases rebuilt from identical verified Evidence under the
    expanded Recipe must be logically equivalent across every expanded relation.

### Product boundary

`NO_PRODUCT_QUESTION` remains after Steward reconciliation. Remaining choices are bounded
implementation mechanics under this contract. No provider request, credentials, spend,
Evidence mutation, Strategy logic, canonical Page/Site/Brand identity, recurring acquisition,
automatic Recipe-selection change, or push is authorized by PF-18.

**Steward pre-implementation verdict:** `READY_FOR_IMPLEMENTATION_AUTHORIZATION`.

## Implementation report

**Writer:** [CLAUDE]  
**Parent commit:** `a1db7449456a06afe1eee5dc8535ff92ce51e683`  
**Implementation commit:** one direct child of that parent; not pushed, not amended.

### Changed paths

Production:

- `src/observatory/dataforseo_google_organic.py` — parser-v2 and the expanded Recipe,
  added alongside an untouched parser-v1 and v1 Recipe.
- `src/observatory/migrate.py` — seven new Google-Organic-local relations plus one
  additive UNIQUE constraint on the reused v1 feature relation.
- `src/observatory/google_organic_derive.py` — expanded planning, atomic write, and
  complete-set gate.
- `src/observatory/google_organic_read.py` — expanded projections, expanded
  occurrence-integrity checks, and the typed expanded history models.
- `src/observatory/api.py` — the history route now returns
  `GoogleOrganicExpandedHistoryEnvelope | HistoryListEnvelope`.

Tests and fixtures:

- `tests/fixtures/dataforseo_google_organic_expanded_recipe.jcs` — new frozen Recipe bytes.
- `tests/test_dataforseo_google_organic_expanded.py` — new (42 tests).
- `tests/test_google_organic_expanded_derive.py` — new (21 tests).
- `tests/test_api_google_organic_expanded.py` — new (22 tests).
- `tests/test_dataforseo_google_ranked_keywords_derive.py` — retargeted the RANK-05
  migration-layering delta from `SCHEMA_STATEMENTS` to the new
  `PRE_PF18_SCHEMA_STATEMENTS`, following the same retarget the RK-04 test already
  carries. No RANK-05 behaviour assertion changed.
- `tests/test_api_google_organic.py` — retargeted `_assert_history_openapi` to resolve
  the route's new `anyOf` and select the `HistoryListEnvelope` branch, then assert the
  unchanged pinned-v1 envelope exactly as before.

Both retargets are consequences of PF-18 itself, not opportunistic cleanup. Nothing under
`README.md`, `docs/`, `AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, or any
other ticket was modified, and the PF-10 fixture is byte-identical.

### Parser contract

New: `dataforseo-serp-google-organic-live-advanced-paid-probe-parser-v2`.

`parse_google_organic` and `google_organic_recipe()` are unchanged. Parser-v2 is a
deliberate local duplicate of the v1 envelope walk (`parse_google_organic_v2`,
`_parse_top_item_v2`, `_require_unique_placements_v2`, `_expanded_error_ir`) so the two
frozen parser contracts cannot drift into each other; it reuses only the genuinely
identical leaf infrastructure — JSON decoding, type/URL requirements, field-state
helpers, and the unchanged AIO/PAA/related-search walkers.

Parser-v2 additionally walks `top_stories.items`, `video.items`, and organic `links`, and
fails closed on: wrong known type, wrong child element type, malformed child URL, invalid
item-timestamp lexical form or impossible calendar instant, missing required child
fields, `items` absent or JSON null on an admitted Top Stories/Video parent, a repeated
child URL under one parent whose testimony disagrees (`duplicate_child_disagreement`),
and populated `related_result` (`parser_version_drift`).

Shared UTC lexical grammar with separately named semantic boundaries:
`_require_utc_clock_lexical` is the one syntax rule; `_optional_result_datetime` (v1,
untouched), `_optional_organic_item_timestamp`, `_optional_top_story_item_timestamp`, and
`_optional_video_item_timestamp` are four separately named helpers with four distinct
error codes and four distinct persisted columns.

### Expanded Recipe identity

- bytes: **3405**
- SHA-256 / `derivation_version_id`:
  **`2704ff82a175be7bacfd601cf7f0e684ca1cc85f9e8cfc93f520b603bcb29d04`**
- frozen at `tests/fixtures/dataforseo_google_organic_expanded_recipe.jcs`, independently
  hashed in tests rather than trusted from the constant.

Exact ordered Observation kinds:

1. `dataforseo.google.organic.serp_feature_presence.v1`
2. `dataforseo.google.organic.ranked_result.v2`
3. `dataforseo.google.organic.ai_overview_presence.v1`
4. `dataforseo.google.organic.ai_overview_source.v1`
5. `dataforseo.google.organic.related_question.v1`
6. `dataforseo.google.organic.related_query.v1`
7. `dataforseo.google.organic.top_story_result.v1`
8. `dataforseo.google.organic.video_result.v1`
9. `dataforseo.google.organic.organic_sitelink.v1`

Ranked-result v2 carries the accepted ranked-result-v1 placement axes verbatim (asserted
against the v1 Recipe document, not restated by hand). The three child kinds share the
axis set `child_url + parent_page + parent_position + parent_rank_group +
parent_rank_absolute + requested_keyword`. No axis set contains a child index.

### Exact PF-10 expanded result

`observation_count` = **248** (`237 - 97 + 97 + 4 + 3 + 4`), per kind:

| kind | count |
|---|---|
| `serp_feature_presence.v1` | 111 |
| `ranked_result.v2` | 97 |
| `ai_overview_presence.v1` | 1 |
| `ai_overview_source.v1` | 15 |
| `related_question.v1` | 4 |
| `related_query.v1` | 9 |
| `top_story_result.v1` | 4 |
| `video_result.v1` | 3 |
| `organic_sitelink.v1` | 4 |

Occurrence rows (subordinate, never counted in `observation_count`): AIO source 18,
related question 4, Top Stories child 4, Video child 3, sitelink 4.

Field states for the exact frozen body:

- organic item timestamp: 58 stated / 39 JSON null / 0 absent;
- organic `links`: 0 absent / 96 JSON null / 0 stated-empty / 1 stated-populated with
  `links_count = 4`;
- Top Stories: one parent at page 1 / left / rank_group 1 / rank_absolute 6, four
  children, all stating source, domain, title, URL, and timestamp;
- Video: one parent at page 1 / left / rank_group 1 / rank_absolute 7, three children,
  all stating source, title, URL, and timestamp, none carrying a domain key and none
  given a derived one;
- sitelinks: four children under the rank_absolute 2 placement, all stating title, URL,
  and domain, all with JSON-null description;
- stated organic timestamps split 39 midnight / 19 non-midnight through one field
  semantics, and zero Derivation diagnostics.

248 is a frozen-Capture expectation, not a provider invariant, and the tests say so.

### Persistence

New relations, all Google-Organic-local:
`google_organic_ranked_results_v2`, `google_organic_top_story_results`,
`google_organic_top_story_result_occurrences`, `google_organic_video_results`,
`google_organic_video_result_occurrences`, `google_organic_sitelinks`,
`google_organic_sitelink_occurrences`.

`google_organic_ranked_results` is not altered and holds no v2 row. The five
semantically unchanged kinds and the result context reuse their existing relations,
discriminated by `derivation_version_id`, exactly as the Keyword Overview core/extended
Recipes already coexist.

Structural binding is expressed as database constraints, not string convention:

- sitelink → its exact ranked-result-v2 parent by
  `(capture_id, derivation_version_id, parent_within_capture_identity)`;
- Top Stories/Video child → its exact parent SERP placement by
  `(capture_id, derivation_version_id, parent_within_capture_identity, parent_item_type)`
  against `google_organic_serp_features`, with `parent_item_type` CHECK-pinned to
  `'top_stories'` / `'video'` respectively;
- every typed row → its generic envelope by the existing four-column envelope FK;
- every occurrence row → its semantic parent by
  `(capture_id, derivation_version_id, within_capture_identity, observation_kind)`;
- `links_state`/`links_count` consistency and every state/value pair are CHECK-enforced.

The one schema change to an existing relation is an additive
`google_organic_serp_features_parent UNIQUE (capture_id, derivation_version_id,
within_capture_identity, item_type)` applied through an idempotent `DO $$` block. It adds
no column, changes no v1 row, and is required for the child→parent FK above.

The expanded derive unit is atomic across Outcome, result context, envelopes, typed
details, occurrences, and diagnostics; the complete-set gate compares full intended and
stored sets and additionally proves every semantic child keeps at least one bound
occurrence. Missing rebuildable rows are restored; extra or conflicting rows raise
`DerivationError`. No `ON CONFLICT DO NOTHING`, no last-write-wins.

### v1 immutability proof

Proved on real PostgreSQL 18 after expanded registration and derivation
(`test_v1_recipe_bytes_rows_and_counts_are_unchanged_after_expansion`,
`test_expanded_and_v1_recipes_coexist_and_stay_independently_derivable`,
`test_pinned_v1_history_is_unchanged_while_expanded_is_selected`):

- Recipe-v1 bytes still 2,487 and digest still
  `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`, both in the module
  constant and in the stored `provider_recipes` bytes;
- v1 `observation_count` still 237 and v1 re-derivation still reports 237 after the
  expanded derivation;
- a full logical snapshot of every Google Organic relation plus `outcomes`,
  `observation_envelopes`, and `derivation_diagnostics` filtered to the v1
  `derivation_version_id` is byte-for-byte identical before and after;
- zero v2 rows exist under the v1 version and zero v1 rows under the expanded version;
- the pinned-v1 history document keeps its exact 17-key Capture shape, its six ordered
  kinds, `ranked_result.v1`, and ranked rows with no `organic_item_timestamp` and no
  `links` key.

Registering or deriving the expanded Recipe never writes `provider_recipe_selections`;
moving the selection is a separate explicit operator action, proved in both directions.

### Read/API

The history route resolves the Recipe and returns the expanded typed document for the
expanded Recipe and the unchanged `HistoryListEnvelope` document otherwise, so a v1
consumer sees no change. Generated OpenAPI advertises both through an `anyOf`, and the
expanded models are typed deeply enough that every time, state, identity, occurrence, and
completeness description lands on the exact nested property — asserted per property, not
by grepping the dump.

Read-side integrity knows every expanded kind, table, and occurrence family, and runs
over **all** matching candidate Captures before the outer limit; damage hidden in an
unreturned tail still returns the existing 409 `evidence_integrity_failure`.

### Validation actually run

Command environment: `OBSERVATORY_TEST_DATABASE_URL` pointed at a local
`postgres:18-alpine` container. No provider host was reachable; every test file installs
the public-network guard.

- `uv run pytest -q tests/test_dataforseo_google_organic.py
  tests/test_dataforseo_google_organic_derive.py
  tests/test_dataforseo_google_organic_expanded.py
  tests/test_google_organic_expanded_derive.py tests/test_api_google_organic.py
  tests/test_api_google_organic_expanded.py tests/test_api_keyword_overview.py
  tests/test_api_search_mentions.py tests/test_api_target_metrics.py
  tests/test_api_llm_mentions_historical.py` — **250 passed** (0 failed, 0 skipped).
- `uv run pytest -q tests/test_api.py tests/test_provider_recipe.py
  tests/test_provider_recipe_selection.py tests/test_provider_history.py
  tests/test_derive_matrix.py tests/test_fixture_matrix.py` — **313 passed**.
- `uv run pytest -q tests/test_dataforseo_google_ranked_keywords_derive.py` —
  **101 passed**.
- `uv run ruff check .` — **All checks passed!**
- `uv run mypy src/observatory` plus the three new test files and the retargeted RANK-05
  test file — **Success: no issues found in 50 source files**.

Not run: the full repository suite. Per the implementation prompt, final full-suite
closure is left to [CHAZ] after Steward review.

### Strongest and weakest parts

Strongest: the Recipe/parser version boundary and the exact PF-10 numbers. The expanded
Recipe is content-addressed from independently hashed frozen bytes, parser-v1 is
untouched, and v1 immutability is proved by a whole-relation logical snapshot rather than
by spot checks. The four family cardinalities, the 58/39/0 timestamp split, and the
0/96/0/1 links split were recomputed from the fixture before any code was written and
then re-proved at parser, plan, PostgreSQL, and API layers.

Weakest / candid limits:

- **Absent, stated-empty, and drifted branches are synthetic only.** PF-10 contains no
  absent organic timestamp, no stated-empty `links`, no second Top Stories or Video
  parent, no duplicate child URL, and no populated `related_result`. Every proof of those
  branches is a bounded mutation of the frozen body. They are claimed contract plus
  synthetic proof, never Evidence.
- **Duplicate disagreement is detected in parser-v2, not in derive.** That differs from
  the accepted AIO precedent, which detects it during grouping. Both land on
  `provider_envelope_rejected`, but the parser path discards the Derivation diagnostics
  that the AIO path preserves. This was a deliberate reading of frozen rule 24; a Steward
  who prefers the AIO shape should say so.
- **Fail-closed on a childless Top Stories/Video parent.** Under the expanded Recipe an
  admitted `top_stories` or `video` item whose `items` key is absent or JSON null rejects
  the whole Capture. That is strict; a real provider could plausibly return such a parent.
  Parser-v1 is unaffected, so the accepted v1 Recipe still admits that body. This is the
  most likely future false-negative in PF-18.
- **Extra occurrence rows are caught by derive, not by read.** A hand-inserted extra
  occurrence under a valid parent is rejected by the complete-set gate on the next
  same-Recipe run, and true orphans are impossible because of the FK, but the read path
  does not independently detect a spurious extra occurrence index. The same limit already
  exists for accepted v1 AIO and PAA occurrences, so PF-18 did not widen it — but it is
  not closed either.
- **`_expanded_capture_group` duplicates `_capture_group`.** That duplication is
  deliberate so the v1 document cannot change when the expanded document does, and it is
  the place a future reviewer should look first if the two documents ever need to diverge
  further.
- **Union response model.** The route's OpenAPI 200 schema is now an `anyOf`. That is the
  honest description of a route serving two Recipe documents, but it did change one
  inherited PF-13 assertion, and any future consumer generating a client from this spec
  must discriminate on `derivation_version_id`.

### Possible false greens

- `test_pf18_adds_exactly_seven_google_organic_local_relations` reads SQL text, so it
  proves wording, not runtime behaviour; the real proof is the PostgreSQL persistence and
  FK/CHECK tests beside it.
- The two-database logical-equivalence test compares stringified rows. That catches value
  and set differences but would not catch two databases sharing an identical wrong value.
- The OpenAPI assertions check that a specific sentence is attached to a specific
  property. They prove the documentation is placed correctly; they cannot prove a
  consumer reads it.

### Deliberately not done

`related_result`, AI Overview prose, PAA expanded answers, images, `date`, `pre_snippet`,
rectangles, xpath, badges, and every other presentation field remain raw. No URL
normalization, no canonical Page/Site/Video identity, no cross-surface join, no Strategy
logic, no recurring acquisition, and no automatic Recipe-selection change.

### Boundary statement

No provider request was made. No DataForSEO or other credentials were read or used. No
paid API was called. No Evidence was mutated: the PF-10 fixture is byte-identical at
135,722 bytes and SHA-256
`7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`, and no replacement
live Evidence was created. Nothing was pushed, amended, rebased, reset, or stashed. The
implementation is one commit whose parent is `a1db7449456a06afe1eee5dc8535ff92ce51e683`.

## Steward implementation review — 2026-09-01

The Project Steward reviewed implementation commit
`a4f83474bd3721617e80c87974a52bfa207d297a` against exact authorized parent
`a1db7449456a06afe1eee5dc8535ff92ce51e683`. The implementation is one direct child, the
working tree was clean, changed paths were bounded to PF-18 plus two directly consequential
test retargets, and the Writer's reported focused PostgreSQL/test/lint/typecheck evidence is
accepted as implementation handoff evidence pending the final [CHAZ] full-suite gate.

The parser/Recipe split, frozen expanded Recipe identity
`2704ff82a175be7bacfd601cf7f0e684ca1cc85f9e8cfc93f520b603bcb29d04`, exact PF-10
248-envelope cardinality, v1 coexistence, no automatic Recipe-selection mutation, explicit
item-time semantics, links-family preservation, and the three new child families match the
reconciled PF-18 design. No Product redesign is required.

The review found three bounded integrity defects that must be remediated before independent
Grok review or a final full-suite closure run.

### R1 — read-side extra-occurrence integrity is incomplete

PF-18 frozen rules 12, 19, 21, and 25 require missing, extra, and orphan subordinate child
occurrences to be integrity damage and require read-side complete-set agreement before the outer
history limit. The Derivation complete-set gate detects an extra occurrence on the next
same-Recipe derive, but `_assert_history_candidates_consistent()` only proves that each semantic
Top Stories/Video/sitelink parent has **at least one** occurrence. A hand-inserted additional
FK-valid `child_index` under an existing semantic parent therefore survives the read integrity
gate and is returned by `_child_occurrences()` as ordinary API testimony.

Remediation must make the expanded read path independently reject extra/spurious occurrence
rows, not merely rely on a future Derivation rerun. The check must run across every matching
candidate Capture before outer limiting. Add a decisive API tamper regression that inserts an
additional valid-parent occurrence index and requires HTTP 409 `evidence_integrity_failure`.
Do this for the child-occurrence contract generally (at minimum proving one family and shared
logic), while keeping accepted pinned-v1 behavior unchanged.

### R2 — duplicated child parent-placement axes are not structurally tied to the cited parent

The new Top Stories and Video tables FK
`(capture_id, derivation_version_id, parent_within_capture_identity, parent_item_type)` to the
SERP feature parent, and sitelinks FK the parent identity to ranked-result-v2. But each child row
also stores and serves `parent_page`, `parent_position`, `parent_rank_group`, and
`parent_rank_absolute`; those duplicated axes are not part of the parent FK and the read path
does not compare them with the cited parent row.

Consequently a positive but false child `parent_page`/rank value can be updated while the real
parent identity and FK remain valid; envelope/detail key checks still agree and the API can
serve contradictory parent-placement testimony as HTTP 200. That violates the frozen semantic
identity axes and the requirement that children be structurally bound to the **exact parent
placement**.

Remediation must structurally or deterministically prove agreement between every served child
parent axis and its cited parent placement. Prefer database-enforced composite parent binding
where it remains additive and local: a suitable UNIQUE parent key containing identity/type plus
page/position/rank axes and matching child FK columns; sitelinks analogously bind to the full
ranked-result-v2 parent placement. A read-side equality check may additionally defend existing
rows, but string/hash convention alone is not enough. Add PostgreSQL tamper tests showing a
mismatched duplicated parent axis cannot be committed or is rejected as integrity damage, plus
an API-level regression if the chosen design permits persisted legacy damage.

### R3 — new ordinary field-state domains are widened beyond PF-18 semantics

PF-18 item timestamps and parent `links` are ordinary provider fields whose applicable states
are exactly `absent`, `json_null`, or `stated`. The implementation uses the repository-wide
`_FIELD_STATE_CHECK` (`stated/json_null/absent/not_requested/inapplicable`) for the new
`organic_item_timestamp_state`, Top Stories/Video timestamp states, and `links_state`; the
expanded Pydantic `_FIELD_STATES` likewise admits all five tokens. Thus a tampered
`not_requested` or `inapplicable` item timestamp/links state with NULL value can satisfy the new
DB/API shape even though that state is impossible under the PF-18 field contract.

Remediation must close the applicable state domain for the new ordinary PF-18 fields to
`absent | json_null | stated` in persistence and read/API validation. At minimum this applies
to organic/Top-Stories/Video item timestamps and `links`; review the newly introduced sitelink
optional description state for the same ordinary-field rule rather than inheriting an
inapplicable/request-disabled domain accidentally. Do not mutate accepted v1 semantics merely
to make the checks uniform. Add DB/API tamper regressions proving `not_requested` and
`inapplicable` are refused rather than served.

### Review disposition

These findings are bounded integrity remediation, not a Recipe-identity or Product redesign.
The accepted expanded Recipe bytes/kinds/semantic axes do not need to change unless the Writer
finds that a required normative semantic change is unavoidable; if so, stop and return for
Steward reconciliation rather than silently changing the Recipe digest.

The Writer should produce one direct remediation child of
`a4f83474bd3721617e80c87974a52bfa207d297a`, update this ticket with exact focused validation,
and leave the tree clean. No provider request, credentials, spend, Evidence mutation,
automatic Recipe-selection change, amend, rebase, reset, or push is authorized.

**Steward implementation verdict:** `REMEDIATION_REQUIRED`.

## Closure

<!-- Project Steward fills after remediation, independent review, and final validation. -->
