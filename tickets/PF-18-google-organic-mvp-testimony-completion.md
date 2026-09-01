# PF-18 — Google Organic MVP testimony completion

**Status:** draft — designated Writer code-first review required  
**Kind:** provider fidelity remediation  
**Triggered by:** MVP-01 Class 4 Google Organic finding  
**Blocked by:** none for read-only review; implementation requires final Steward acceptance  
**Approved by:** Project Steward for pre-implementation review only  
**Draft base:** `0465a5b6e3bb9c4e56aa613f5d61581620e46096`  
**Implementation Writer:** [CHAZ] must designate [CLAUDE] or [GROK] before the review/implementation lane starts  

## Why this ticket exists

MVP-01 re-reviewed the exact protected PF-10 Google Organic provider body, SHA-256
`7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`, against the accepted
PF-11/PF-12 parser, Recipe, persistence, and read API. The six-kind v1 slice is faithful to
what it deliberately models, but the exact live body contains additional materially useful
SERP testimony that an API-only consumer cannot currently obtain:

- child Top Stories results with exact source/domain/title/URL/publication-time testimony;
- child Video results with exact source/title/URL/publication-time testimony;
- provider-stated publication timestamps on returned organic ranked results; and
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
   title, URL, and provider publication time did each carry?
2. Which exact Video child results did the provider return, and what source, title, URL, and
   provider publication time did each carry?
3. For each organic ranked placement, did the provider state a publication timestamp and, if
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
sole semantic identity. Provider publication time is not Capture time and is not Provider
Update Time.

### Video children

The exact PF-10 body contains one returned `video` parent with a populated child `items` array.
Preserve at minimum exact source, title, URL, and provider `timestamp`, plus enough parent and
occurrence context to distinguish what the provider actually returned. Do not treat child
position as a universal Google rank or infer a canonical video/entity identity from the URL.

### Organic publication time

PF-10 contains organic placements with both stated and JSON-null provider `timestamp` values.
The expanded contract must preserve that distinction for each placement. Name/document this as
provider result/publication-time testimony only. It is not a Provider Update Time, Capture time,
or Data Period and must never inherit from any sibling clock.

### Organic sitelinks

At least one PF-10 organic placement carries a populated child `links` array. Preserve the
relationship from the exact parent placement to every returned sitelink child, including exact
title, URL, domain, and description state/value admitted by the frozen body/claimed contract.
Child URL must not become a canonical Page ID. Preserve duplicate occurrences rather than
silently set-deduplicating them unless the final reviewed semantic identity explicitly proves a
safe separate occurrence model.

## Deliberately not pulled into PF-18

The MVP finding does **not** require this ticket to expose:

- full AI Overview prose/markdown or sentence/token citation mapping;
- PAA expanded-answer content;
- images/CDN presentation data, xpath, rectangles, highlights, breadcrumbs, cache URLs,
  ratings, prices, AMP flags, `checks`, or decorative presentation fields merely because
  they exist;
- top-story image URLs or relative-date presentation strings unless code-first review shows
  one is required to preserve the accepted publication-time meaning;
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
- Organic publication timestamps are provider-stated facts for individual results; missing or
  null time must not be filled from `datetime`, Capture time, `pre_snippet`, or another row.
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

- publication time versus Capture/result-retrieval/Provider Update Time;
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
- [ ] Stated versus JSON-null/absent organic publication timestamps survive parser → Recipe →
      PostgreSQL → API without clock inheritance.
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

## Required pre-implementation review

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

## Implementation report

<!-- Designated Writer fills only after final Steward acceptance and implementation authority. -->

## Closure

<!-- Project Steward fills after implementation, independent review, and final validation. -->
