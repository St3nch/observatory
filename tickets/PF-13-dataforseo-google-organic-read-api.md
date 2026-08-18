# PF-13 — DataForSEO Google Organic read/history API and recipe selection integration

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-12 closed  
**Approved by:** Project Steward  
**Start commit:** to be recorded by the implementer

## Purpose

Expose the accepted PF-12 Google Organic testimony through the versioned, read-only,
Evidence-backed Observatory API.

PF-13 integrates the existing adapter-aware provider recipe selector with the Google
Organic adapter, extends the existing Attempt audit resource to dispatch this provider
surface, and adds one surface-explicit Google Organic history resource. It does not change
Derivation, persist new testimony, create a generic Observation API, or authorize another
provider exchange.

## Authority and precedent

- D2 — every consumer uses the versioned API
- D11 — Attempt audit resource retained; adapter-aware provider recipe selection; first
  provider histories remain explicit to provider/surface semantics
- D12 — the accepted recipe and frozen fixture remain the interpretation boundary
- PF-08 — accepted Keyword Overview selection, Attempt, history, integrity, and read-only
  precedent
- PF-12 — accepted Google Organic Outcomes, result context, six typed kinds, and occurrence
  relations

F8 production auth/non-loopback, F9 HTTP writes, and F10 cross-provider projections remain
deferred.

Implementation begins from clean `main` at the ticket's recorded Start commit.

## Fixed substrate

Exact adapter:

`dataforseo-serp-google-organic-live-advanced-paid-probe-v1`

Accepted recipe:

`338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`

PF-13 reads the accepted PF-12 relations:

- `google_organic_result_context`
- `google_organic_serp_features`
- `google_organic_ranked_results`
- `google_organic_aio_presence`
- `google_organic_aio_sources`
- `google_organic_aio_source_occurrences`
- `google_organic_related_questions`
- `google_organic_related_question_occurrences`
- `google_organic_related_queries`
- generic `outcomes`, `observation_envelopes`, `provider_recipes`, and
  `provider_recipe_selections`

Recipe bytes, fixture bytes, identities, parser semantics, Derivation behavior, tables, and
the 237 normal-Observation count are unchanged.

## Recipe selection integration

Reuse the accepted `provider_recipe_selections` schema and
`provider_recipe_selection` service. PF-13 adds no second selection table and no HTTP
selection write.

The existing operator command can select the accepted Organic recipe for the exact Organic
adapter. Derivation and API reads must never select a recipe automatically.

For the Organic Attempt and history resources:

- an explicit `derivation_version_id` pin resolves that exact registered recipe for the
  Organic adapter;
- without a pin, resolve the current recipe selected for the exact Organic adapter;
- no selection returns the existing stable
  `503 provider_recipe_not_selected` response;
- malformed, unknown, or wrong-adapter pins return 404;
- Organic selection remains independent of Keyword Overview and every other adapter;
- changing an adapter's selection never deletes or mutates prior recipe rows.

Only one production Organic recipe exists today. Do not invent a second production recipe
or mutate recipe bytes merely to demonstrate versioning. Existing generic selector tests
already prove coexistence; PF-13 must prove the accepted Organic recipe can be selected,
explicitly pinned, and isolated from the Keyword Overview selection.

## Existing Attempt audit resource

`GET /v1/attempts/{attempt_id}` remains the Evidence-backed audit/provenance resource.

Extend provider dispatch so a verified Attempt for the exact Organic adapter receives the
accepted provider representation already used for Keyword Overview:

- `attempt_id`
- provider
- exact adapter contract
- selected or pinned `derivation_version_id`
- `recipe_resolution` as `selected` or `pinned`
- Attempt-stage Outcome
- Capture-stage Outcome, or null when unresolved

Dispatch only the exact paid Organic adapter
`dataforseo-serp-google-organic-live-advanced-paid-probe-v1`. Do not route every
non-fixture adapter through provider recipe selection; in particular, the nearby Organic
sandbox adapter remains outside this resource. A bounded generalization of the shared
provider Attempt view/loader is allowed so Keyword Overview and paid Organic share Outcome
lookup and Evidence verification. Do not duplicate that provenance logic, and do not put
Organic family SQL in `keyword_overview_read.py`.

Outcome lookup uses the full recipe/Attempt/Capture provenance. Before returning success,
verify every cited Capture and its parent Attempt through the Evidence Store.

Required compatibility:

- fixture Attempt JSON remains logically unchanged, including its observation fields;
- Keyword Overview provider Attempt behavior remains unchanged;
- Organic Attempts never receive fixture `panel_id`/`score` fields;
- a valid selected/pinned recipe with no Outcome for this Attempt returns 404 rather than
  triggering Derivation;
- missing/damaged Evidence with leftover derived rows returns 409
  `evidence_integrity_failure`.

Do not replace the Attempt resource with history and do not add provider observations to
the Attempt response.

## Google Organic history resource

Add:

`GET /v1/providers/dataforseo/google/organic/history`

Query contract:

- required exact `requested_keyword`;
- optional exact `derivation_version_id` pin;
- `limit` default 20, minimum 1, maximum 100;
- `order=asc|desc`, default `asc`.

The limit applies to complete Capture groups, never to individual Observation rows or
occurrences. For a valid selected/pinned recipe with no matching admitted result context,
return HTTP 200 with `captures: []`.

Candidate Captures are anchored by the exact PF-12 result-context grain and joined to their
Capture Outcome through the full
`(derivation_version_id, attempt_id, capture_id)` provenance. A foreign-Attempt Outcome
for the same Capture/recipe must neither duplicate nor supply classification/count.

Candidate membership is
`google_organic_result_context JOIN outcomes` on that full tuple only. Do not join
`observation_envelopes` to decide membership: an admitted-empty Capture has context and
zero envelopes, while an admitted frozen Capture has 237 envelopes. Membership also
requires `outcomes.classification IN ('observation_admitted',
'observation_admitted_empty')`; existence of a context row alone does not establish
admission.

Verify every matching candidate's Attempt, Capture, and cited body through
`EvidenceStore.read_attempt()` / `read_capture()` before returning normal history.
Follow PF-08's accepted fail-closed behavior: verification occurs before history
sort/limit, so damaged matching Evidence yields 409 even if that Capture would fall outside
the returned limit.

History order is deterministic by verified `request_started_at`, with `capture_id` as
tie-breaker. `asc` and `desc` reverse the complete key. A Capture group is never
partially returned.

Only `observation_admitted` and `observation_admitted_empty` context belongs in normal
history. Non-admitted Capture Outcomes remain visible through the Attempt audit resource,
not as normal Observation history.

## Top-level response

Return:

- provider `dataforseo`
- exact Organic `adapter_contract`
- exact requested keyword
- resolved `derivation_version_id`
- `recipe_resolution`
- exact recipe `observation_kinds`
- `captures`

Do not return a universal metric, score, rank, recommendation, strategy conclusion, or
cross-provider identity.

## Capture group

Every returned Capture group includes:

- `attempt_id`, `capture_id`, provider, adapter, and recipe identity;
- verified Attempt `authorized_at`;
- verified Capture `request_started_at` and `transport_ended_at`;
- exact request context:
  `location_code`, `language_code`, `depth`, `device`, `os`,
  `group_organic_results`, and `load_async_ai_overview`;
- Capture Outcome classification and observation count;
- one typed `result_context`;
- the six surface-specific families below.

Assemble all seven request-context fields from the verified Attempt parameters.
`location_code` and `language_code` must agree with the persisted result context; their
presence there is not authority to widen PF-12 with the other five fields. A missing or
wrong-typed required Organic Attempt parameter, or disagreement between Attempt and context,
returns 409 `evidence_integrity_failure`.

The result context exposes:

- exact requested keyword;
- provider-returned keyword as `{state, value}`;
- `se_domain` as `{state, value}`;
- provider result/retrieval time as
  `provider_result_time: {state, value}`;
- `se_results_count` and `pages_count` as `{state, value}`;
- required `items_count`;
- exact provider-order `item_types`.

`provider_result_time` is not Capture time and is not Provider Update Time.
`se_results_count` is provider testimony, not Observatory completeness.

Cost, check URL, task UUID, raw response bodies, and omitted PF-11 families are not exposed.

## Typed families

Every row includes its exact `observation_kind` and
`within_capture_identity`.

### `serp_features`

Return every feature placement with exact:

- item type
- page
- position
- `rank_group`
- `rank_absolute`

### `ranked_results`

Return every organic placement with exact:

- URL
- provider domain
- title
- description as `{state, value}`
- website name as `{state, value}`
- page
- position
- `rank_group`
- `rank_absolute`

The frozen Capture returns all 97 placements even though only 87 exact URLs are unique.
Never deduplicate, normalize, group, or identify these rows by URL.

### `ai_overview_presence`

Return the one presence object or null, including
`asynchronous_ai_overview` and its placement axes.

### `ai_overview_sources`

Return the semantic source rows with exact locus, URL, and provider domain/title/source
field states. Nest each source's complete `occurrences` array containing:

- locus
- `element_index` as integer or null
- `reference_index`

The frozen Capture exposes 15 semantic sources with 18 total occurrences: seven top-level
and eleven element-level. Top-level and element loci remain distinct; no stronger citation
claim is invented.

### `related_questions`

Return exact visible title plus every subordinate occurrence containing parent PAA page,
position, `rank_group`, `rank_absolute`, and block-local `question_index`.

Title remains semantic identity. Occurrence order does not become identity.

The frozen Capture's four questions and four occurrences are not sufficient proof of this
attachment. A synthetic second PAA block must reach history as four title-identified
questions with eight total nested occurrences, preserving each parent placement and
block-local `question_index` without collapsing by title or index.

### `related_queries`

Return the nine exact-string semantic query rows from the frozen Capture. Do not recreate
repeated per-page chip multiplicity.

## Deterministic presentation order

Array order is presentation only and never a new identity or universal Google rank.

Use stable order based on stored semantic testimony with
`within_capture_identity` as the final tie-breaker:

- feature and ranked placements: page, position, `rank_absolute`, `rank_group`;
- AIO sources: locus, exact URL;
- AIO occurrences: locus, `element_index NULLS FIRST`, `reference_index`;
- related questions: exact title;
- PAA occurrences: page, position, `rank_absolute`, `rank_group`,
  `question_index`;
- related queries: exact query text.

Do not label this array ordering as one universal SERP position.

## Integrity and read-only behavior

API success remains backed by verified Evidence. Missing, unlinked, or damaged Attempt,
Capture, or response-body Evidence for a matching selected/pinned history candidate returns
HTTP 409 with `evidence_integrity_failure` and no normal payload.

All API PostgreSQL connections retain
`default_transaction_read_only=on`. GET requests must not:

- select or derive a recipe;
- mutate selection, Outcomes, envelopes, context, details, or occurrences;
- mutate Evidence;
- repair missing rows;
- invoke provider or DNS access.

## Acceptance criteria

- [ ] Fixture and Keyword Overview Attempt/history responses remain logically unchanged.
- [ ] Organic Attempt dispatch returns selected and explicitly pinned provider Outcome
      representations with exact adapter isolation.
- [ ] Missing Organic selection is 503; malformed/unknown/wrong-adapter pin is 404; a
      selected recipe with no Attempt rows is 404.
- [ ] Organic selection does not alter Keyword Overview selection or any prior derived row.
- [ ] Frozen PF-10 history returns one complete 237-Observation Capture group with exact
      per-family counts, 97/87 URL testimony, AIO 15/18/7/11 testimony, four questions, and
      nine queries.
- [ ] Every field state and occurrence location survives serialization without invented
      values or identity.
- [ ] Provider result time, Capture time, and placement/rank axes remain distinct.
- [ ] A valid admitted-empty Capture returns a complete Capture group with context, zero
      observation count, empty arrays, and null AIO presence despite having no
      `observation_envelopes`.
- [ ] A planted context row whose full-tuple Outcome is non-admitted does not enter normal
      history.
- [ ] Two Capture-anchored testimonies for the same requested keyword remain distinct and
      sort deterministically; `limit=1` returns one complete Capture group.
- [ ] A foreign-Attempt Outcome for the same Capture/recipe does not duplicate or supply
      history provenance.
- [ ] Damaged matching Evidence returns 409 with no normal history payload.
- [ ] API reads do not mutate PostgreSQL or Evidence.
- [ ] Two databases rebuilt from the same Evidence/recipe/selection return logically equal
      Organic history JSON.
- [ ] No cost, check URL, task UUID, universal score/rank, raw body, or deferred detail is
      exposed.
- [ ] Ordinary tests perform zero provider/DNS activity.
- [ ] API remains loopback/no-auth and read-only; F8/F9/F10 remain unclaimed.

## Required tests

- Existing fixture Attempt and Keyword Overview Attempt/history regression
- Organic adapter current selection, explicit pin, missing selection, and wrong-adapter pin
- Organic provider Attempt selected/pinned representation and 404-without-derived-row behavior
- Frozen PF-10 history exact response shape and every per-family/occurrence count
- Duplicate exact URLs remain 97 placement rows / 87 unique strings
- Field-state serialization including JSON null/absence/stated values where represented
- Independent acquisition time and provider-result-time serialization
- Frozen request context assembled from the verified Attempt; missing/wrong-typed required
  Attempt parameter and Attempt/context disagreement return 409
- Admitted-empty Capture response with an explicit assertion that its envelope set is empty
- Planted non-admitted full-tuple Outcome plus matching context remains outside history
- Synthetic second Capture revising content at the same placement identity; asc/desc and
  whole-Capture limit behavior
- Synthetic second PAA block through the API: four title-identified questions, eight nested
  occurrences, preserved parent placement axes, and block-local `question_index`
- Foreign-Attempt Outcome provenance adversary
- Attempt/Capture/body Evidence damage 409
- PostgreSQL/Evidence read-only before/after proof across selection, Outcomes, envelopes,
  all nine PF-12 tables, and Evidence Store operations
- Two-database API JSON equivalence
- Route/OpenAPI and invalid query-bound behavior
- Autouse public-network socket guard
- One completed-implementation full suite, Ruff, and mypy run

During TDD, use the smallest API/Organic targeted set and one session-scoped PostgreSQL
fixture. Run the full suite only once after implementation is complete.

## Out of scope

- any Derivation, recipe, parser, identity, or PF-12 schema change
- automatic recipe selection or HTTP selection writes
- a second production Organic recipe
- generic non-fixture Attempt dispatch or Organic family reads in
  `keyword_overview_read.py`
- generic `/observations`, universal SERP rank, URL/Page normalization, or cross-provider
  projection
- AIO prose/markdown, sentence citations, PAA expanded answers, sitelinks,
  `related_result`, organic publication time, top-stories/video details
- cost, check URL, task UUID, raw Evidence body exposure
- provider calls, recurring acquisition, another adapter/device/locale/search engine
- F6 automation, F7 concurrency, F8 production auth, F9 HTTP writes, F10 projections, or
  F12 orchestration
- unrelated API, selector, or read-model refactoring

## One implementation commit must prove

The accepted Google Organic recipe's Capture-anchored testimony is consumable through a
surface-explicit, recipe-aware, Evidence-backed, read-only API without collapsing placement,
occurrence, field-state, or time semantics and without changing fixture or Keyword Overview
behavior.

## Implementer report required

The implementation commit must update this ticket to `review`, record its exact parent,
changed paths, acceptance-to-test map, command timings/results, and state explicitly:

- what is strong and weak in the resulting response contract;
- what generalized cleanly from PF-08 and what did not;
- whether shared provider Attempt logic should remain shared, duplicated, or later extracted;
- the weakest provenance join, ordering, field-state, occurrence-attachment, integrity, or
  read-only assumption;
- any false-green test risk, missing adversary, scalability concern, or under-proved case;
- improvements that would help a real consumer but do not belong in PF-13;
- anything learned that should affect the next Observatory ticket;
- confirmation that PF-12 recipe/fixture/identities/counts and both Keyword Overview recipes
  remain unchanged;
- confirmation of no provider/network call, Evidence mutation, new surface, or push.

Do not broaden implementation to fix adjacent findings. Report them for Steward
reconciliation.
