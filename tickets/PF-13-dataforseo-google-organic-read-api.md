# PF-13 — DataForSEO Google Organic read/history API and recipe selection integration

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-12 closed  
**Approved by:** Project Steward  
**Start commit:** `7f1218de71ebb726af6cb632147427db80f5c20f`

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

## Implementation report

**Parent:** `7f1218de71ebb726af6cb632147427db80f5c20f`  
**Child:** supplied in the implementer handoff (a commit cannot embed its own final hash).  
**Status:** `review`

### Loaded skills

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### A. Start gate

- branch: `main`
- exact HEAD: `7f1218de71ebb726af6cb632147427db80f5c20f`
- working tree: clean
- PF-13: `ready` at start; set `in-progress` then `review`

### B. Changed paths

- `src/observatory/api.py` (exact paid-adapter Attempt dispatch; Organic history route)
- `src/observatory/keyword_overview_read.py` (shared provider Attempt loader uses the verified Attempt adapter)
- `src/observatory/google_organic_read.py` (new Organic history assembly)
- `tests/test_api_google_organic.py` (new)
- this ticket (Start commit, Status, Implementation report)

No recipe, fixture, parser, identity, Derivation, schema, or Keyword Overview recipe bytes.

### C. Recipe selection

Reused `provider_recipe_selections` and `provider_recipe_selection`. No second table. No HTTP write. Current selection and explicit pin both resolve
`338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`
for `dataforseo-serp-google-organic-live-advanced-paid-probe-v1`. Missing selection is `503 provider_recipe_not_selected`. Malformed, unknown, and wrong-adapter pins are 404. Changing Keyword Overview current selection does not change the Organic pointer.

### D. Attempt dispatch

`GET /v1/attempts/{attempt_id}` dispatches only:

- Keyword Overview paid adapter
- Organic paid adapter

The Organic sandbox adapter stays on the fixture path and returns 404 without entering recipe selection. Shared `load_provider_attempt` now resolves and verifies against the Attempt's own adapter. Organic Attempt JSON is the provider representation only: identities, `recipe_resolution`, Attempt/Capture Outcomes. No Organic families, no fixture `panel_id`/`score`.

### E. History

`GET /v1/providers/dataforseo/google/organic/history`

Candidate membership is `google_organic_result_context JOIN outcomes` on
`(derivation_version_id, attempt_id, capture_id)` with
`classification IN ('observation_admitted', 'observation_admitted_empty')`.
No `observation_envelopes` join. Evidence `read_attempt` / `read_capture` runs for every matching candidate before sort/limit. Order is `(request_started_at, capture_id)`, reversed as a whole for `desc`. Limit is whole Capture groups.

Request context is assembled from the seven verified Attempt parameters. `location_code` and `language_code` must agree with persisted result context. Missing/wrong-typed required parameters or disagreement raise `409 evidence_integrity_failure`.

### F. Acceptance map

| Criterion / required test | Proving test |
|---|---|
| Fixture and Keyword Overview Attempt/history remain isolated | `test_fixture_and_ko_remain_isolated_from_organic_selection`; existing `tests/test_api_attempts.py` and `tests/test_api_keyword_overview.py` in the full suite |
| Organic Attempt selected/pinned; sandbox not provider-dispatched | `test_organic_attempt_selected_pinned_and_http_errors`; sandbox 404 in isolation test |
| Missing selection 503; malformed/unknown/wrong-adapter pin 404; selected recipe with no Attempt rows 404 | `test_organic_attempt_selected_pinned_and_http_errors` |
| Organic selection does not alter Keyword Overview | isolation test |
| Frozen PF-10 one 237-Observation Capture; exact keys; 97/87; exact `item_types`; every family `observation_kind`/`within_capture_identity`; persisted-to-API field mapping | `test_frozen_history_shape_counts_times_and_request_context` via `_persisted_projection` |
| AIO 15 exact `(locus, URL)` parents; 18 exact occurrence tuples; nested under the correct source; 7/11 locus split; domain/title/source `{state, value}` | same |
| Exact PAA titles and one nested occurrence each; exact related-query strings | same |
| Field states, distinct clocks, frozen request context | same |
| Admitted-empty complete group; envelope set empty; planted non-admitted context excluded | `test_admitted_empty_and_non_admitted_context_stay_distinct` |
| Second Capture revision; asc/desc; whole-Capture `limit=1`; equal `request_started_at` / `capture_id` tie-break | `test_second_capture_paa_block_order_limit_and_tie_break` |
| Synthetic second PAA: four titles; two occurrences each; parent-block axes; title-bound `question_index` | same |
| Foreign-Attempt Outcome adversary | `test_foreign_attempt_outcome_does_not_supply_history` |
| Attempt/context disagreement, missing/wrong-typed Attempt parameter, in-window and outside-limit Evidence damage 409 | `test_request_context_integrity_and_damage_409` |
| Read-only PostgreSQL/Evidence | `test_api_reads_do_not_mutate_organic_state` |
| Two-database JSON equality with real 237-count data | `test_two_databases_return_equal_organic_history` |
| Route/OpenAPI and invalid query bounds | frozen-shape test (`/api/v1/openapi.json`, 422s) |
| Autouse public-network socket guard | module `_no_public_network` |

### G. Validation

One completed-implementation full-suite run, then a type-comment-only remediations of the Attempt-parameter mutator so `mypy` accepts the test double. Pytest was not re-run after that comment-only change.

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-18T22:19:35.870Z | 2026-08-18T22:21:49.402Z | 133.532 s (pytest 133.12 s) | 0 |
| `uv run ruff check .` | 2026-08-18T22:21:49.403Z | 2026-08-18T22:21:49.434Z | 0.031 s | 0 |
| `uv run mypy` (after test type-ignore) | 2026-08-18T22:22:54.063Z | 2026-08-18T22:22:54.328Z | 0.265 s | 0 |

`896 passed, 1 skipped, 1 warning` (upstream Starlette/`httpx` deprecation). Prior accepted PF-12 count was 887. Versions: pytest 8.4.2, ruff 0.16.2, mypy 1.20.2, 48 source files. No leftover `observatory-ce05-*` container.

### H. Review

Code-review against `7f1218de71ebb726af6cb632147427db80f5c20f`.

**Standards:** 0 hard. Residual judgement: JSON/field helpers are copied from Keyword Overview rather than extracted; `HISTORY_LIMIT_*` and Attempt views still live under the Keyword Overview module name; history candidates are a positional tuple.

**Spec:** 0 missing/partial/wrong on the named contract. Residual: missing/wrong-typed Attempt parameters cannot be committed through Organic validation, so that 409 path is proved by a post-verify `read_attempt` mutator.

### I. Candid assessment

**Strong.** The response keeps placement, occurrence, field-state, and time axes distinct. Membership does not use envelopes, so admitted-empty appears and a planted non-admitted context does not. Dispatch is an exact two-adapter allowlist, not “anything non-fixture.” Verify-all-before-limit matches accepted PF-08 fail-closed behavior, including damage outside the returned window.

**Weak.** There is still only one production Organic recipe, so selected vs pinned is the same digest with different `recipe_resolution`. Request-parameter 409 for missing/wrong types is a defensive check that ordinary committed Organic Attempts cannot reach. The Attempt audit resource remains one URL with two JSON shapes.

**What generalized from PF-08.** Adapter-aware resolve/pin/503/404, discriminated provider Attempt JSON, Capture-group history query contract, verify-before-limit, foreign-Attempt Outcome adversary, xmin/ops read-only proof, two-database JSON equality.

**What did not.** Candidate membership (context+Outcome+admission, not coverage+envelope). Request context is seven Organic Attempt parameters plus Attempt/context agreement, not KO enrichment flags. Occurrences nest under semantic AIO/PAA identity. Result context is not an Observation kind. There is no CORE/EXTENDED kind split.

**Shared Attempt loader.** Keep it shared. Outcome lookup and Capture verify are the same for both paid adapters. Do not put Organic family SQL in `keyword_overview_read.py`. A later rename/extract of the Attempt view into a neutral module would be naming hygiene, not a PF-13 need.

**Weakest assumption.** History 409s if any admission-matching candidate fails Evidence or request-context checks, including Captures a `limit` window would omit. That is tested and fail-closed. Selection remains a mutable pointer with no prior-pointer history.

**False-green / scale.** Two-database equality asserts a non-empty 237-count payload so two empty `captures: []` cannot pass. Module-scoped frozen setup is reused for the happy-path shape test; mutation tests rebuild. Verify-all-before-limit will not scale to large keyword histories; that is accepted fail-closed behavior, not a cursor.

**Not in PF-13.** Consumer-facing field docs; a second Organic recipe; HTTP selection writes; generic `/observations`; AIO prose/PAA answers; cost/check URL/task UUID.

**Next ticket.** The next provider history should copy Organic’s context-JOIN-Outcome membership and occurrence nesting, not Keyword Overview’s coverage-envelope join. Keep Attempt dispatch as an explicit adapter allowlist.

### J. Confirmations

- Organic recipe `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde` and PF-10 fixture bytes/hash unchanged
- Keyword Overview CORE `319af798…` and EXTENDED `cade41cb…` unchanged
- no provider/DNS/credentials/paid-gate use
- no Evidence mutation in product paths
- no recipe/parser/identity/Derivation/schema change
- no generic Observation API, no new acquisition surface
- no `scripts/verify-all`
- no push

### K. Commit

- parent SHA: `7f1218de71ebb726af6cb632147427db80f5c20f`
- child SHA: recorded in this implementation commit

### L. Steward remediation

Steward review of `e0ebcfda0b77e6185ed944d85fbb6025d2dfc154` found 0 authority/spec blockers and 0 demonstrated product-code defects, but one IMPORTANT acceptance-proof gap: family counts were stronger than exact serialization and occurrence attachment.

**Changes.** Test-only. `_persisted_projection` reads accepted PF-12 rows and maps them independently to the history JSON shape. It does not call `google_organic_read` helpers.

**Added assertions.**

- exact keys for top-level history, Capture group, result context, every typed family, and nested AIO/PAA occurrences
- every semantic family row’s `observation_kind` and 64-hex `within_capture_identity`
- complete persisted-to-API equality for features, ranked rows, AIO presence, AIO sources, PAA questions, and related queries
- exact provider-order `item_types` `["ai_overview", "organic", "people_also_ask", "top_stories", "video", "related_searches"]`
- ranked URL/domain/title, description/website_name field states, and placement axes via full-list equality
- AIO 15 exact `(locus, URL)` parents, 18 exact `(parent locus, parent URL, occurrence locus, element_index, reference_index)` tuples, attachment under the matching source, and 7 null / 11 element `element_index` values
- AIO domain/title/source `{state, value}` objects
- frozen PAA four exact titles, each with one nested occurrence
- exact nine related-query strings from the PF-11 first-seen list
- synthetic second PAA: four title parents; each title has two occurrences; first block `rank_absolute=3`/`rank_group=1` and second `112`/`2`; `question_index` bound to first-seen title order 0..3

**Product defect exposed?** No. Stronger proof matched the existing assembler.

**Remaining unproved serialization assumption.** `_persisted_projection` uses the ticket’s presentation `ORDER BY` to compare arrays. That proves content and attachment, and that API order matches the specified order. It does not independently re-derive identities from recipe bytes. Feature/ranked placement values are proved by full persisted-row equality rather than a second handwritten fixture table.

### M. Remediation validation

Targeted: `uv run pytest -q tests/test_api_google_organic.py` — 9 passed, 1 warning.

One completed-remediation full-suite run. First mypy pass failed on `expected["result_context"]["item_types"]` because `_persisted_projection` was typed `dict[str, object]`; the helper return type was widened to `dict[str, Any]`. Pytest was not re-run after that type-only change.

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-18T22:42:40.728Z | 2026-08-18T22:44:55.084Z | 134.356 s (pytest 133.88 s) | 0 |
| `uv run ruff check .` | 2026-08-18T22:44:55.085Z | 2026-08-18T22:44:55.119Z | 0.034 s | 0 |
| `uv run mypy` (after return-type fix) | 2026-08-18T22:45:09.195Z | 2026-08-18T22:45:09.485Z | 0.290 s | 0 |

`896 passed, 1 skipped, 1 warning`. 48 source files. No leftover `observatory-ce05-*` container. No product-code change. No push.
