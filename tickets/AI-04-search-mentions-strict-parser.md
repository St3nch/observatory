# AI-04 — Search Mentions strict parser and AI-03 conformance fixture

**Status:** review  
**Owner:** [GROK] technical review / [GPT] Steward reconciliation  
**Blocked by:** technical review and Steward reconciliation; not ready for implementation  
**Approved by:** Project Steward  
**Start commit:** `7a76bee9843006e0c1c76b16913e926d1cf73e36`  

## Purpose

Build the zero-network interpretation boundary for the exact closed adapter
`dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`.
Copy the verified AI-03 response bytes through the existing read-only inspector into one
frozen deterministic Conformance fixture, then parse those bytes into a strict typed
in-memory Search Mentions representation with bounded adversarial proofs.

AI-04 does not create a Derivation Recipe, Observation identity, PostgreSQL schema or rows,
derive command, selection rule, history/API route, continuation workflow, recurring
acquisition, or another AI Optimization surface. Those boundaries remain AI-05 and later.

## Authority and accepted foundation

- D11 — provider interpretation and Observation identity restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, and recipe remain
  distinct.
- D13 — useful coverage direction does not bypass bounded activation.
- `docs/specs/capture-event-v2.md` provider interpretation sections.
- AI-01 selected Search Mentions Live / Google as the first bounded AI Optimization
  contract.
- AI-02 closed the Evidence-only one-shot adapter.
- AI-03 closed the one authorized live exchange and its off-host restore proof.

AI-03 and the independent GROK payload audit both recommend
`PROCEED_WITH_AI04`. D12 rejects extra paid calls merely to increase sample count after
the material authorized branch is exercised. AI-04 authorizes no provider, DNS, credential,
account, paid-host, or other external network access.

## Exact fixture provenance

Read the response only through the existing verified local inspector:

- Evidence root:
  `/home/chaz/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20`;
- Attempt:
  `2a363a7bb07c27e55301d604afb1d06fda817760635943c68bcb4b567f9f7d03`;
- Capture:
  `bea666f9b982054df287da253fb49b0e0a9c1022b461c111a483b43d8606d4db`;
- exact response bytes: `48466`;
- exact response SHA-256:
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`.

The committed fixture must be byte-identical to inspector stdout. Tests must prove its byte
length and SHA-256 independently and must never depend on the operator Evidence root after
the copy is established. The Conformance fixture is test material, not Evidence authority.

Proposed fixture path:

`tests/fixtures/dataforseo_ai_optimization_search_mentions_ai03.json`

## Verified real testimony

The exact body proves one HTTP-complete, provider-successful, Google offset-zero result:

- root/task provider status `20000`; one task; one result;
- exact decimal cost lexical form `0.105` at root and task;
- result keys are exactly the observed `total_count`, `offset`,
  `search_after_token`, `items_count`, and `items`; no `current_offset`;
- `total_count=3055`, `offset=0`, `items_count=5`, and five returned items;
- non-null 628-character continuation token, retained but never followed;
- five provider questions: `enception`, `mathematical artificial intelligence`,
  `search engine optimized`, `seos`, and `engine optimization service`;
- those questions are answer-scope word-match hits, not replacements for the requested
  keyword `generative engine optimization`;
- current AI search volumes `368000`, `201000`, `135000`, `110000`, `110000`;
- five large Markdown answers, five independent first/last provider clock pairs, and five
  `is_web_search_based=true` values;
- 48 ranked structured sources distributed `7/14/13/4/10`;
- 60 monthly points, 12 per item, with per-item windows;
- current volume disagrees with the newest monthly value for three items;
- item fields `search_results`, `brand_entities`, and `fan_out_queries` are JSON null
  for all five Google items;
- source fields `publication_date`, `thumbnail`, and `markdown` are JSON null for all
  48 sources;
- all 48 exact source URLs are unique in this fixture, while repeated domains and answer
  Markdown links that do not equal structured source URLs are real testimony.

One body proves existence, not invariance. In particular it does not prove that URL
duplicates cannot occur, provider order is identity, current volume derives from monthly
points, result completeness follows transport completeness, or null-only fields can never
be stated.

## Parser boundary

Implement a dedicated Search Mentions parser module. Do not extend the fixture classifier,
Keyword Overview parser, Google Organic parser, or the paid acquisition adapter into this
interpretation boundary. Reuse small accepted value types only where that does not create a
shared provider-parser framework.

The parser must:

- strict-decode UTF-8;
- reject a UTF-8 BOM, invalid UTF-8, duplicate JSON object member names, trailing
  non-whitespace material, and non-finite JSON constants;
- parse structural integers as real integers, rejecting booleans and floats;
- preserve decimal-capable lexical testimony exactly with `Decimal` or an equivalent
  non-binary representation;
- distinguish HTTP transport success from root/task provider status;
- validate the exact one-task/one-result successful branch and all declared counts;
- preserve duration strings as durations, never as timestamps;
- parse provider response clocks under the observed
  `YYYY-MM-DD HH:MM:SS +00:00` grammar with real calendar validation;
- retain the continuation token as an opaque null-or-string field and never decode it;
- use the verified Attempt parameters as request authority;
- never substitute `task.data`, token internals, provider item order, or a returned
  question for the requested context;
- reconcile every item’s Google platform, location `2840`, and language `en` against the
  verified Attempt context;
- retain exact returned question and exact Markdown answer independently of the requested
  keyword;
- preserve exact URL, domain, source display name, title, snippet, query string, fragment,
  and provider rank;
- never extract or admit answer Markdown links as structured sources;
- preserve current AI search volume separately from every monthly point;
- preserve each monthly `(year, month, search_volume)` as provider-stated Data Period
  testimony, not Capture time;
- preserve JSON null, stated value, and permitted absence distinctly wherever the typed IR
  supports more than one state;
- produce stable diagnostics for tolerated unknown additive fields without changing known
  typed values;
- return deterministic parse failure/classification for known-field, status, count,
  context, or structural drift.

Proposed production module:

`src/observatory/dataforseo_ai_optimization_search_mentions.py`

## Typed IR requirements

The full in-memory representation must retain enough exact testimony for AI-05 to design a
Recipe without rereading ad hoc JSON.

Envelope/task/result retains root version/status/message/duration/exact cost/task counts;
task ID/path/status/message/duration/exact cost/result count; typed task-data testimony
without making the echo request authority; and result total count, offset, item count, and
exact opaque continuation state.

Request context retains requested keyword; `match_type`, `search_filter`,
`search_scope`; requested platform, location, language, limit, and offset; and provenance
sufficient for later reconciliation without creating Observation identity here.

Each item occurrence retains non-identity provider order testimony, platform, model,
location, language, exact question, exact answer, current volume, first/last provider
clocks, web-search boolean, explicit states for the three null-only item fields, monthly
points, and structured source occurrences.

Each source occurrence retains per-item provider rank, exact title/URL/domain/source
name/snippet, and explicit states for publication date, thumbnail, and source markdown.
There is no URL/domain deduplication and no Markdown-link synthesis.

AI-04 must not declare natural Observation identities. Item index, source array index, result
order, continuation-token contents, task echo, and answer-link position are forbidden as
semantic identity claims. Duplicate question strings and duplicate exact URLs must remain
representable as distinct parser occurrences for AI-05 to reconcile deliberately.

## Proposed field-state decision for review

The initial Steward proposal is:

- on this Google adapter, `search_results`, `brand_entities`, and
  `fan_out_queries` are required known keys whose only currently supported value is JSON
  null; a non-null value is unsupported Google contract drift and fails closed;
- source `publication_date`, `thumbnail`, and `markdown` are required known keys with
  null-or-stated-string typed states under the claimed optional source contract; JSON null
  is the only live state observed, strings are exercised synthetically, and any object,
  array, number, or boolean fails closed;
- missing required known keys remain failure rather than being silently converted to JSON
  null.

GROK must challenge this choice during technical review. AI-04 is not ready until the
Steward reconciles whether claimed-contract string support is justified without a second
live sample.

## Reconciliation and ordering rules

- The verified Attempt keyword remains requested query context; none of the five returned
  questions is rewritten or rejected for differing from it.
- `search_scope=["answer"]` means answer-scope matches are valid even when the question
  contains none of the requested words.
- Item order is preserved as occurrence testimony but does not create identity or a
  secondary sort rule.
- Equal `ai_search_volume` values do not authorize an invented tie-break.
- Source rank is scoped to one returned item. Rank is not Capture-wide and never equals
  source array index by definition.
- Proposed rank rule for review: rank must be a positive integer and unique within an item;
  reordering a source array preserves ranks; a positive rank gap is preserved with a stable
  diagnostic rather than automatically renumbered or rejected.
- Monthly identity is the explicit provider period, never array position. Reordering monthly
  arrays must not rewrite periods. Duplicate periods and invalid calendar months fail.
- Item and source duplicates are preserved; the parser does not deduplicate by question,
  URL, domain, title, source name, or array position.
- `total_count` describes the provider’s larger result population. A transport-complete
  five-item body with `total_count=3055` is explicitly truncated result testimony, not a
  complete corpus or an absence claim.

## Required fixture proofs

The exact AI-03 fixture must prove:

- exact bytes and SHA-256;
- exact root/task/result topology and one successful result;
- `offset` exists and `current_offset` does not;
- `items_count=5`, `len(items)=5`, `total_count=3055`;
- exact continuation token preserved without decoding;
- exact five questions in provider order and none substituted with the requested keyword;
- exact current volume vector and three real current/monthly disagreements;
- exact source counts `7/14/13/4/10`, all 48 exact URLs, and ranks attached to the correct
  item;
- exact 12 monthly points per item and per-item window variation;
- exact null states for the six null-only field families;
- Markdown answers preserved through parse, including non-ASCII;
- execution durations, provider clocks, Data Periods, Capture provenance, and cursor token
  time-like text remain distinct concepts.

## Required bounded adversarial proofs

At minimum test:

- duplicate JSON member, invalid UTF-8, BOM, trailing bytes, `NaN`/infinity;
- missing known fields at every layer and tolerated additive-field diagnostics where
  permitted;
- root/task success disagreement, provider error, task/result count errors, two tasks, two
  results, and HTTP-complete provider rejection classification;
- `items` missing, null, empty, wrong type;
- `items_count != len(items)`, `total_count < items_count`, negative/bool/float counts,
  and offset disagreement with the verified Attempt;
- `current_offset` added or substituted for `offset`;
- continuation null, stated string, missing, and wrong type; no token interpretation;
- item platform/location/language disagreement with Attempt context;
- returned questions without requested words remain valid;
- duplicate question occurrences remain distinct;
- source reorder, repeated ranks, zero/negative/bool/float rank, positive rank gap,
  duplicate exact URL within one item, and the same URL across items;
- URL query/fragment preservation and malformed required URL;
- Markdown with CDN, Google-search, and unrelated links never creates structured sources;
- monthly reorder, duplicate period, invalid month `0/13`, wrong/negative volume, empty
  list, and per-item windows that differ;
- current volume integer zero, wrong type, and disagreement with newest monthly point;
- timestamp lexical/calendar failures, non-UTC offsets, and last before first;
- `is_web_search_based=false` accepted and non-boolean rejected;
- non-null Google-only item fields fail under the reconciled field-state decision;
- source optional fields exercise null, supported stated form, missing, and wrong type;
- cost lexical forms `0.105`, `0.1050`, exponent form, and high precision prove no binary
  float round trip;
- existing Keyword Overview, Google Organic, acquisition identities, and frozen fixtures
  remain unchanged.

Synthetic mutations prove parser behavior, not that those variants occurred in AI-03.

## Acceptance criteria

- A byte-identical AI-03 Conformance fixture is committed at the recorded length and digest.
- A dedicated strict parser emits a complete typed IR for all five items, 48 sources, and
  60 monthly points with the request/result distinction intact.
- Known provider quirks and null states are preserved rather than corrected.
- All count, status, known-field, context, numeric, period, time, and structural failures
  are deterministic and zero-network.
- Additive-field handling is explicit and test-proved; known-field drift never hides as an
  extension.
- Provider order and array indexes are not semantic identities.
- Duplicate questions and URLs remain representable and are not silently collapsed.
- The exact continuation token is opaque testimony and no continuation request exists.
- The parser creates no PostgreSQL rows and no Recipe/Observation identity.
- Ordinary tests perform zero provider, DNS, credential, paid-host, or other public-network
  activity.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are clean.
- Implementation is one commit from the reconciled ready-ticket parent and stops for
  Steward review without push.

## Explicit non-goals

- another provider exchange or Evidence root;
- continuation/page-two support;
- ChatGPT or another platform;
- Target Metrics or another AI Optimization surface;
- Derivation Recipe or Observation identity;
- PostgreSQL migration, persistence, derive dispatch, selection, API, or history;
- recurring capture, scheduler, F6 automation, F7 concurrency, or F12 orchestration;
- Markdown citation extraction, URL normalization, domain/entity consolidation, scoring,
  strategy, or recommendations;
- refactoring existing provider parsers into a shared framework.

## GROK technical-review deliverable

Before implementation, independently review this ticket against current authority, code,
tests, the exact AI-03 Evidence, and the prior payload audit. Report:

1. every wrong, missing, ambiguous, or over-specified requirement;
2. whether the proposed null-or-string source-field treatment is justified;
3. whether Google-null item fields should fail on non-null;
4. whether positive source-rank gaps should parse with diagnostics or fail;
5. whether duplicate question/source occurrences remain representable without prematurely
   choosing AI-05 identity;
6. whether unknown additive fields can be diagnosed without a Recipe in AI-04;
7. the narrowest safe module/IR/test shape and dangerous coupling to avoid;
8. a corrected acceptance-to-test outline;
9. strong areas, weak areas, gaps, false-green risks, drift points, and anything another
   live pull would uniquely settle.

Return one verdict: `READY_AFTER_TICKET_RECONCILIATION` or
`BLOCKED_PENDING_NEW_EVIDENCE`. Do not implement, edit, commit, push, or call a provider.

## Next ticket boundary

After accepted implementation and Steward closure:

1. AI-05 — Derivation Recipe, semantic identities, typed PostgreSQL persistence, and
   rebuild proof;
2. AI-06 — read/history API.

Target Metrics remains a separate later surface. AI-04 does not authorize it.

