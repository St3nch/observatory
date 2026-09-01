# PF-18 — Google Organic MVP testimony completion

**Status:** implementation authorized  
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

<!-- Designated Writer fills only after final Steward acceptance and implementation authority. -->

## Closure

<!-- Project Steward fills after implementation, independent review, and final validation. -->
