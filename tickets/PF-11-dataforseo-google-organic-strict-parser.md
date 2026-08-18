# PF-11 — DataForSEO Google Organic strict parser and PF-10 conformance fixture

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Start commit:** unset  

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

[GROK] fills this section in the single implementation commit and sets Status to `review`.
Only the Project Steward may set Status to `done`.
