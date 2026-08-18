# PF-11 — DataForSEO Google Organic strict parser and PF-10 conformance fixture

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Start commit:** `aee38a5fa8dd5d752c96017e6ced4eb9d4128b94`  

## Purpose

Turn the accepted PF-10 Google Organic Live Advanced provider contract probe into a
zero-network, recipe-addressed parsing boundary for later Google Organic Derivation work.

PF-11 freezes the exact verified PF-10 response as a Conformance fixture, authors one closed
Google Organic Derivation Recipe, and implements a strict provider-specific parser that emits
a typed intermediate representation for the first intentionally admitted SERP testimony.

PF-11 does **not** write PostgreSQL Outcomes or Observations, add a history API, perform a
provider call, authorize another probe, or broaden recurring acquisition.

## Authority and exact Evidence

Authority begins at clean `main` commit
`11a8e46f0796cd8d9e0a91d3ff8d7c17d6aab360`.

PF-10 adapter:
`dataforseo-serp-google-organic-live-advanced-paid-probe-v1`.

Accepted live Evidence:

- keyword: `conspiracy theories`;
- Attempt: `acfdb7a06a5c2d1af4c00fc8518a08891d1a083bc13d59149916b707c5d7ed34`;
- Capture: `ff17d3d56e29281984c2171cf9dc065d47105a36116a4723dbe75e4c8a9c3c27`;
- exact response body length: `135722` bytes;
- exact response body SHA-256:
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`.

The source and fresh off-host restore were independently scrubbed clean and proved exact
Attempt/Capture inventory equality. Copying the exact verified response bytes into the
deterministic test corpus is authorized by this ticket; the copied fixture is not Evidence
authority.

## Verified claimed-contract semantics

The Steward rechecked the current DataForSEO Google Organic Live Advanced contract before
cutting PF-11. The recipe/parser must preserve these distinctions:

- `rank_group` is position among SERP elements of the same provider item `type`; it is not a
  universal Google rank.
- `rank_absolute` is position among SERP elements generally, but right-positioned elements
  may use a separately counted absolute sequence. `rank_absolute` alone is therefore not a
  universal SERP-item identity.
- `position` is provider SERP alignment (`left`/`right`) and is retained as placement
  testimony.
- `page` is the provider-reported SERP page.
- request `depth=100` is an acquisition/parsing-depth control, not a promise that
  `items_count==100` or exactly 100 organic placements are returned.
- `pages_count` is pages retrieved; `items_count` is returned top-level item count;
  `se_results_count` is provider-returned total-results testimony and is not Observatory
  completeness.
- `load_async_ai_overview=true` requests asynchronously loaded AI Overview when needed.
- a present AI Overview with `asynchronous_ai_overview=false` means the returned AIO was
  loaded from provider cache; the flag is retained as testimony.
- `group_organic_results=true` permits same-domain related organic material to appear under
  a parent `related_result`; `related_result:null` in PF-10 is only the observed null state.
- `people_also_ask_click_depth` was not requested. PF-10's four visible PAA questions are
  acquired testimony; empty/null expanded-answer shells do not prove that answers do not
  exist.
- result-level `datetime` is provider SERP-receipt/retrieval time in UTC, distinct from
  Observatory Capture time.
- organic item `timestamp`, where present, is provider testimony of result publication
  date/time; it is not Provider Update Time and is deliberately not typed in the first
  PF-11 IR.
- an AI Overview element's nested `references` are provider-described sources used to
  generate that element; top-level AI Overview references are the weaker provider claim
  that the pages may have been used to generate the overview. These loci must not be
  silently collapsed into one stronger citation claim.

## Closed first recipe testimony

PF-11's typed IR covers only the following first-slice facts:

1. SERP feature placement/presence for known top-level item types, retaining provider type,
   page, position, `rank_group`, and `rank_absolute`.
2. Organic ranked placement: exact URL, exact provider domain, title, optional description
   with explicit field state, optional website name, page, position, `rank_group`, and
   `rank_absolute`.
3. AI Overview presence including `asynchronous_ai_overview` state.
4. AI Overview source relationships, preserving whether the relationship came from the
   top-level AIO reference list or from a specific AIO element/reference locus; no
   sentence-span citation is invented.
5. People Also Ask related-question relationships from the visible question titles only.
6. Related-search query relationships, deduplicated semantically by exact returned query
   text within the Capture rather than multiplying repeated per-page chips into false new
   discoveries.

The verified Attempt's exact requested keyword is the Observatory subject. Provider-returned
keyword and SERP context remain separate testimony. Exact URLs are retained without
normalization and are never used alone as placement identity.

## Deliberately raw / not typed in PF-11

- full AI Overview prose/markdown;
- sentence-level or token-level AIO citation claims;
- PAA expanded-answer shells/content;
- organic `timestamp` / `pre_snippet` semantics;
- sitelinks and `related_result` structures;
- top stories and video-carousel detail rows;
- highlights, xpath, rectangles, provider CDN/image presentation fields;
- rating, price, AMP/cache and other absent/null optional families;
- provider cost/task id/check URL as Observations;
- URL normalization, Page IDs, cross-surface identity, scores, or strategy semantics.

Unknown additive fields in recipe-declared extension-permitted objects produce bounded
diagnostics rather than changing known facts. Missing/wrong-typed known required fields,
duplicate JSON keys, invalid closed enums, malformed required URLs/timestamps, task/envelope
failure, contradictory rank/cardinality invariants declared by the recipe, or ambiguous
subject reconciliation fail closed for provider Observation admission later; PF-11 exposes
those parser failures deterministically and writes no PostgreSQL rows.

## Acceptance criteria

- Exact PF-10 response bytes are copied to a deterministic fixture and independently checked
  in tests for length `135722` and SHA-256
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`.
- A closed RFC 8785/JCS Google Organic Derivation Recipe exists and its full lowercase
  SHA-256 is the provider `derivation_version_id`; changing semantic recipe bytes changes
  the identity.
- Parser accepts the verified fixture zero-network and reproduces the observed material
  cardinalities: one result; `pages_count=10`; `items_count=111`; 97 organic placements;
  one AIO; one PAA block with four visible questions; one top-stories block; one video block;
  ten related-search blocks; and nine unique related-search strings.
- Parser retains both rank axes plus page and position and never represents either rank as a
  universal Google position.
- Duplicate exact organic URLs at distinct placements remain distinct typed placements.
- AIO top-level and element-level reference relationships remain distinguishable.
- PAA null/empty expansion content is not admitted as an absence fact.
- Related-search repeated page chips do not become duplicate discovery facts.
- Provider-returned keyword/context is reconciled against, but never substituted for, the
  verified Attempt subject.
- Strict duplicate-key JSON rejection and exact decimal handling reuse the accepted D11/PF-05
  provider-parser discipline without binary-float identity behavior.
- Bounded adversarial tests cover at least: duplicate JSON member, unknown additive field,
  missing required known field, wrong rank type, unknown item type behavior under the recipe,
  duplicate placement ranks, reordered array/rank disagreement, malformed required URL,
  malformed result datetime, task error, result-count/cardinality disagreement, AIO source
  locus inconsistency, and null/absence variants.
- Existing fixture and Keyword Overview behavior/identities remain unchanged.
- Ordinary automated tests perform zero provider/DNS activity.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are clean.

## Explicit non-goals / deferred boundaries

PF-11 does not implement provider Outcome/Observation persistence, migrations, derive CLI
integration, Google Organic history/API resources, another SERP adapter, mobile or alternate
location/language probes, PAA-click acquisition, asynchronous workflows, recurring
acquisition, F6 automation, F7 concurrency, F9 write API, or F12 orchestration.

No provider exchange is authorized by this ticket.

## Implementation report

**Parent:** `aee38a5fa8dd5d752c96017e6ced4eb9d4128b94`  
**Child:** supplied in the implementer handoff (a commit cannot embed its own final hash).  
**Status:** `review`

### Loaded skills

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_google_organic.py` (new parser, typed IR, closed recipe)
- `tests/test_dataforseo_google_organic.py` (new)
- `tests/fixtures/dataforseo_google_organic_pf10.json` (exact PF-10 response bytes)
- `tests/fixtures/dataforseo_google_organic_recipe.jcs` (frozen JCS)
- this ticket (Status, Start commit, Implementation report)

No PostgreSQL persistence, migrate, derive CLI, API/history, other adapter, or
fixture-v1 / Keyword Overview identity change.

### Fixture provenance

Copied from the service-owned inspect path
`inspect_organic_paid_probe_body` against Evidence root
`$HOME/.local/share/observatory/pf10-google-organic-conspiracy-theories-2026-08-18`,
Capture `ff17d3d56e29281984c2171cf9dc065d47105a36116a4723dbe75e4c8a9c3c27`.
Inspect bytes equal the committed fixture (`cmp` / SHA-256 match). The fixture
is a Conformance copy, not Evidence authority.

- length `135722`
- SHA-256 `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`

### Production recipe

2487-byte JCS, SHA-256
`338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`.
Kinds: `serp_feature_presence.v1`, `ranked_result.v1`, `ai_overview_presence.v1`,
`ai_overview_source.v1`, `related_question.v1`, `related_query.v1`.
`closed_objects` is empty; unknown additive fields on extension-permitted objects
are diagnostics. Organic placement identity does not include URL.
`ai_overview_source.v1` identity is `(requested_keyword, locus, url)`.
`related_question.v1` identity is `(requested_keyword, title)`.
The first implementation commit used 2551-byte SHA-256
`9b8fa9cfad5acb1539684acfa27bdf88510a5355a61f7e82e14426d8db6d58d1` with
array-index AIO/PAA axes; that digest is superseded by the identity correction
below.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Frozen PF-10 length/SHA-256 | `test_frozen_fixture_independent_sha256_and_length` |
| Observed cardinalities; both rank axes; page/position; not a universal Google rank | `test_pf10_reproduces_observed_cardinalities_and_rank_axes` |
| Duplicate exact URLs remain distinct placements | `test_duplicate_exact_urls_remain_distinct_placements` |
| AIO top-level vs element loci remain distinct; prose not typed | `test_aio_top_level_and_element_loci_remain_distinct` |
| PAA titles only; expansion shells not absence facts | `test_paa_types_visible_questions_and_ignores_expansion_shells` |
| Related-search first-seen exact-string dedupe (80 → 9) | `test_related_search_strings_dedupe_by_exact_text_first_seen` |
| Requested keyword remains subject | `test_requested_keyword_remains_subject_when_returned_differs_only_by_form` |
| Duplicate member, BOM, NaN, unknown additive, missing required | `test_duplicate_member_unknown_field_and_missing_required` |
| Wrong rank type, unknown item type, duplicate ranks | `test_wrong_rank_type_unknown_item_type_and_duplicate_ranks` |
| Reorder keeps provider ranks; array index is not identity | `test_reordered_items_keep_provider_ranks_and_do_not_use_array_index` |
| Malformed URL / result datetime | `test_malformed_required_url_and_result_datetime` |
| Task error; items_count / result_count / task-length disagreement | `test_task_error_and_cardinality_disagreement` |
| AIO locus type errors; null required arrays fail; emptying one locus does not relabel the other | `test_aio_source_locus_inconsistency_fails_closed` |
| Null vs absent description/website_name; exact Decimal | `test_null_absence_and_decimal_variants` |
| Returned location/language not substituted for Attempt | `test_context_reconciliation_does_not_substitute_attempt_subject` |
| Recipe digest/kinds; semantic byte change changes identity | `test_google_organic_recipe_published_digest_and_kinds` |
| Keyword Overview core identity unchanged | `test_keyword_overview_identities_remain_unchanged` |
| 18 AIO occurrences → 15 semantic identities; no index axes | `test_pf10_aio_sources_map_to_fifteen_semantic_identities` |
| Locus distinguishes same URL; same-locus repeats collapse | `test_aio_source_identities_distinguish_locus_and_collapse_same_locus_url` |
| AIO reference reorder leaves identity set unchanged | `test_reordered_aio_reference_arrays_keep_semantic_identity_set` |
| Four PF-10 PAA titles; `question_index` absent from recipe identity | `test_pf10_paa_titles_have_four_semantic_identities` |
| PAA reorder and second block with repeated titles share identity | `test_paa_identity_survives_reorder_and_second_block_with_repeated_titles` |

### Checks

- `uv run pytest -q` — 862 passed, 1 skipped
- `uv run ruff check .` — clean
- `uv run mypy` — clean
- Ordinary tests remain zero-network; autouse socket guard in PF-11 tests

### Review

Code-review against `aee38a5fa8dd5d752c96017e6ced4eb9d4128b94`.

**Standards:** 0 hard. Residual judgement: rank/page/position travel together on
several IR types; JSON decode helpers are copied from PF-05 rather than extracted;
`_parse_aio_reference` still defends locus combinations the parser itself will not
construct.

**Spec:** valid finding fixed — JSON-null AIO `references`/`items` now fail closed
instead of admitting an empty locus. Locus tests now also prove that emptying one
locus does not relabel the other. Residual: `cost` and `check_url` are typed on
the parse IR (and AIO sources carry provider `domain`/`title`/`source`) but are
not Observation kinds. That matches PF-05 envelope testimony and the ticket's
"as Observations" wording; no PG rows are written.

### Unproven limits

- Right-positioned `rank_absolute` as a separately counted sequence is implemented
  (`(position, rank_absolute)` uniqueness) but unobserved in PF-10 (all 111 items
  are `left`; `rank_absolute` happens to equal array index + 1).
- IR `question_index` still restarts per PAA block; it is no longer an Observation
  identity axis. Persistence must aggregate occurrence locations under title.
- Related-search chips in this fixture are plain strings, not objects.
- PAA `expanded_element` shells are left raw and unvalidated.
- No PostgreSQL provider writes, derive CLI, or Observation emission.

### Engineering assessment

**Ticket awkwardness.** "Reordered array/rank disagreement" is ambiguous as a
fail-closed case: the same ticket says `rank_absolute` is not a universal item
index and right-positioned items may use a separate sequence. Implemented as
preservation (ranks stay on the item; uniqueness is per position sequence), not
as `rank_absolute == index+1`. "AIO source locus inconsistency" is also awkward
because locus is derived from tree position, not a provider field; payload
mutations can only destroy or empty a locus, not cross-label one. Location and
language are "context" in the ticket; they are reconciled when stated but are
not separate IR Fields.

**PF-05 substrate.** Decode / duplicate-member / Decimal / FieldState /
ParseClassification / recipe document shape generalized cleanly. Keyword
Overview identity (one row per requested keyword) did not. SERP identity is
placement-shaped. Reusing `Field` from `dataforseo_keyword_overview` is the
smallest reuse; it couples a second parser to the first surface's module.

**Protective vs harmful coupling.** Duplicating JSON decode and optional-field
helpers is protective: a shared parse kernel would become a third thing to
version. Importing `Field` is slightly harmful as a dependency direction, but
extracting a types module now would be speculative. One union `_ITEM_KEYS` for
all top-level item types is protective simplicity and harmful precision — a
`url` on `related_searches` would not diagnostic.

**IR bound.** The six kinds match the first slice. The IR is not forcing a
feature-type hierarchy or a citation graph. `SerpFeaturePlacement` for organic
items overlaps `OrganicPlacement` ranks; that is uniform item testimony, not a
reason to abstract a placement base class yet.

**Fragile edges.** (1) AIO source identity no longer includes `element_index`;
top-level IR rows still have `None` as occurrence testimony. Later persistence
must aggregate those locations under `(locus, url)`. (2) PAA identity is title,
not `question_index`; IR indexes remain block-local. (3) Rank uniqueness assumes
provider ranks are unique per `(position, rank_absolute)` and
`(type, position, rank_group)`; a future right-rail sequence is the untested
half. (4) URL is correctly excluded from organic identity; two different URLs
with identical ranks would fail closed as duplicate ranks, which is right, but
we have not seen that.

**Under-proved adversarial cases.** Right-position ranks; two PAA blocks;
related-search object items; AIO with only one of the two reference loci
missing-as-key vs empty-array vs populated; `item_types` disagreeing with
actually present types; sitelinks/`related_result` appearing under an organic
row (left raw, untested). Constructor `aio_source_locus` checks remain
unreachable from input.

**111-item pressure.** Parse is one linear walk of 135 KB; not a runtime
concern. The pressure is Observation cardinality at derive time: 111 feature
placements + 97 organic + 1 AIO presence + 15 semantic AIO source identities
(from 18 IR occurrences) + 4 questions + 9 queries ≈ 237 rows per Capture,
before sitelinks, AIO prose, or a second locale. That is the number that should
inform later write/API batching, not this parser.

**Do not refactor yet.** Do not extract a shared provider-JSON kernel. Do not
introduce a placement base type. Do not split AIO source kinds. Do not type PAA
expansions or AIO markdown. Do not change KO.

**Refactor triggers.** A third provider parser that would otherwise copy `Field`
and decode helpers. A right-rail Capture that falsifies the rank uniqueness
rule. Persistence needing a deterministic occurrence-location aggregate under
AIO `(locus, url)` or PAA title. Related-search items arriving as objects.

**Fixture surprise that changes opinion.** PAA `expanded_element` is not an
empty/null shell. Each of the four questions carries a list of structured
AIO-like objects (`type`, `items`, `references`, `asynchronous_ai_overview`)
with `items` itself null. Leaving that raw is still correct; treating PF-10 as
proof that expansions are "empty" would be wrong. Future PAA-click work should
assume nested AIO-shaped shells, not blank answers. Second surprise: result
`datetime` is stored as `2026-08-18 17:37:36 \u002B00:00` in the exact bytes;
JSON decode yields a literal `+`, so the PF-05 timestamp grammar still holds.
Third: `rank_absolute == index+1` in this Capture is an observation, not a
contract — do not bake it into the recipe. Fourth: 10 exact URL duplicates
across later pages are real provider testimony, not scrape errors; URL-as-
identity would have been silently wrong.

### Identity correction

**Baseline:** `b64c6ac4c4090bcca8f21f7b666990b9b08e5666`  
**Status:** `review`

Steward findings independently confirmed before editing:

- D11 rejects returned-array index / provider result order as Observation
  identity.
- `observation_identity()` requires every declared axis; `_axis_value(...,
  "integer", ...)` rejects `None`.
- Recipe `ai_overview_source.v1` declared integer `element_index` and
  `reference_index`. The seven admitted top-level PF-10 sources have
  `element_index=None`, so those rows cannot receive valid identities.
- The fixture has 18 AIO source occurrences (7 top-level, 11 element-level),
  15 unique semantic `(locus, exact URL)` pairs, and repeated element-level
  Wikipedia, Britannica, and YouTube URLs.
- Recipe `related_question.v1` used `question_index`. Reordering questions
  would change identity. A second PAA block restarts indexes at zero and can
  collide. The parser already accepts multiple PAA blocks.

Correction semantics:

- `ai_overview_source.v1` axes are `requested_keyword`, `locus`, `url`.
- `related_question.v1` axes are `requested_keyword`, `title`.
- IR still retains `element_index` (`None` for top-level), `reference_index`,
  and `question_index` as non-identity occurrence/ordering testimony.
- No integer sentinel. Kind not split. No persistence.

New recipe: 2487 bytes, SHA-256
`338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`.

Frozen PF-10 response fixture unchanged: length `135722`, SHA-256
`7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`.
KO CORE identity unchanged:
`319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908`.

Changed paths: `src/observatory/dataforseo_google_organic.py`,
`tests/fixtures/dataforseo_google_organic_recipe.jcs`,
`tests/test_dataforseo_google_organic.py`, this ticket.

Validation at this working tree, HEAD still `b64c6ac4…` before the correction
commit, tree dirty only on the four allowed paths. No
`OBSERVATORY_RUN_PAID_GATE_HAMMER` and no provider/network calls. No leftover
`observatory-ce05-*` container after the run.

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-18T19:51:33.729Z | 2026-08-18T19:53:39.603Z | 125.874 s (pytest 125.48 s) | 0 |
| `uv run ruff check .` | 2026-08-18T19:53:39.603Z | 2026-08-18T19:53:39.631Z | 0.028 s | 0 |
| `uv run mypy` | 2026-08-18T19:53:39.631Z | 2026-08-18T19:53:39.769Z | 0.137 s | 0 |

`867 passed, 1 skipped, 1 warning` (Starlette/`httpx` TestClient deprecation).
Prior accepted count at `b64c6ac4` was 862 passed, 1 skipped, 1 warning.
Tool versions: pytest 8.4.2, ruff 0.16.2, mypy 1.20.2, uv 0.12.1.
mypy elapsed is a warm cache; a prior cold run at `b64c6ac4` was 15.330 s.

Code-review against `b64c6ac4`. Standards: 0 hard. Spec: Steward identity
blockers closed; residual is later persistence aggregating occurrence
locations under the new semantic identities.
