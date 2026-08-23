# AI-06 — Search Mentions recipe selection and read API

**Status:** ready-for-agent  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Parent spec:** `docs/specs/capture-event-v2.md`  
**Blocked by:** AI-05 — Search Mentions provider Derivation and typed persistence (`done`)  
**Approved by:** Project Steward  
**Technical-review base:** `c73d4ec60daf1331de63e47113807473000eff03`  
**Start commit:**

## Purpose

Complete the first Search Mentions vertical slice by exposing its already-derived, typed,
source-attributed history through the read-only API under Recipe selection and Evidence-backed
integrity rules.

Exact adapter:

    dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1

Exact accepted Recipe:

    bd3dfbf87eba83df35dc7ae6eecd25c223a89ad72d910db346d8ebafb61933e0

AI-06 adds no acquisition, provider exchange, continuation, parser, Recipe, Derivation,
identity, schema, or migration behavior.

## Authority and accepted foundation

- VISION API-only boundary, provenance, distinct time axes, and explicit truncation limits
- VOCABULARY definitions of Attempt, Capture, Evidence, Outcome, Observation, Provenance,
  Derivation Recipe, Observation Kind, and Data Period
- D2, D3, D8, D11, and D12
- PF-08 Recipe selection and verify-before-limit
- PF-13 Organic context-plus-admission candidate membership
- PF-14 Capture-wide envelope/typed consistency and occurrence-parent checks
- AI-02 through AI-05 Search Mentions acquisition, Evidence, parser, Recipe, typed persistence,
  occurrence testimony, and result context

GROK completed the accepted pre-ticket read-only technical review at the named base. The
Steward reconciled its route, membership, integrity, naming, token, ordering, and test
findings into this ticket. No repeat design review is required before implementation.

## Fixed fixture and persistence facts

The accepted Conformance fixture remains byte-identical:

- `tests/fixtures/dataforseo_ai_optimization_search_mentions_ai03.json`
- 48,466 bytes
- SHA-256 `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`
- requested keyword `generative engine optimization`
- 5 item, 60 monthly, and 48 source occurrences
- 113 semantic Observation envelopes and one result-context row
- `total_count=3055`, `result_offset=0`, `items_count=5`
- one exact non-null opaque `search_after_token`

The existing seven Search Mentions relations are sufficient:

- `search_mentions_result_context`
- `search_mentions_items`
- `search_mentions_item_occurrences`
- `search_mentions_monthly_search_volume`
- `search_mentions_monthly_occurrences`
- `search_mentions_sources`
- `search_mentions_source_occurrences`

Result context and occurrence rows are not Observation envelopes and do not contribute to
Outcome `observation_count`.

## Exact API contract

### History route

Implement exactly:

    GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/history

Retaining `ai-optimization` prevents a future platform or Target Metrics surface from
silently colliding with this Google Search Mentions contract.

### Query parameters

- `requested_keyword` — required exact string
- `derivation_version_id` — optional lowercase 64-hex Recipe pin
- `limit` — default 20, minimum 1, maximum 100; whole Capture groups only
- `order` — `asc` or `desc`, default `asc`

Do not add a continuation token, time range, model, platform, location, language, or cursor
query. Invalid limit/order retains FastAPI 422 behavior. Empty or unknown keyword is an exact
match miss and returns a normal empty history.

### Recipe selection and errors

Use the existing provider Recipe-selection mechanism for the exact Search Mentions adapter.

- no selection and no pin → HTTP 503 `provider_recipe_not_selected`
- malformed, unknown, or wrong-adapter pin → HTTP 404 `not found`
- valid selected/pinned Recipe with no matching admitted history → HTTP 200 `captures: []`
- selected/pinned provider Attempt with no derived Outcomes → Attempt HTTP 404
- damaged Evidence or bounded projection disagreement → HTTP 409
  `evidence_integrity_failure`

Selected and pinned reads may resolve the same sole production Recipe. Do not invent a
second production Recipe merely to test pinning. Search Mentions selection must not move
Keyword Overview or Organic pointers or alter their rows/results.

### Provider Attempt audit

Add only the exact Search Mentions adapter to the existing provider Attempt dispatch
allowlist and reuse the accepted provider Attempt loader.

The resource remains audit/provenance only: provider, adapter, Attempt identity, Recipe
identity/resolution, Attempt Outcome, and optional Capture Outcome. It exposes no Search
Mentions families and no fixture `panel_id`, label, score, or fixture Observation shape.
Do not relocate the loader or accept an unknown provider adapter.

## History response

Top level contains exactly:

- `provider` = `dataforseo`
- `adapter_contract` = the exact Search Mentions adapter
- `requested_keyword` = exact query
- `derivation_version_id` = resolved Recipe
- `recipe_resolution` = `selected` or `pinned`
- `observation_kinds` in Recipe order:
  1. `dataforseo.google.ai_optimization.search_mentions.item.v1`
  2. `dataforseo.google.ai_optimization.search_mentions.monthly_search_volume.v1`
  3. `dataforseo.google.ai_optimization.search_mentions.source.v1`
- `captures` = complete Capture groups

Each Capture group contains:

- `attempt_id`, `capture_id`, `provider`, `adapter_contract`, `derivation_version_id`
- `authorized_at`, `request_started_at`, `transport_ended_at`
- `request`, `capture_outcome`, `result_context`
- `search_mention_items`, `monthly_search_volume`, `structured_sources`

The three family keys are fixed presentation names, not new Observation kinds.

### Verified request block

The `request` block comes from the verified Attempt and contains exactly:

- `match_type`
- `search_filter`
- `search_scope` as `["answer"]`
- `platform`
- `location_code`
- `language_code`
- `limit`
- `offset`

Persisted context must agree with the Attempt on requested keyword and every field above,
including `limit ↔ request_limit` and `offset ↔ request_offset`. Missing/wrong-typed
required Attempt parameters or disagreement returns 409. `adapter_contract` remains outside
the request block.

### Result context and opaque token

`result_context` contains exactly:

- `requested_keyword`
- `total_count`
- `result_offset`
- `items_count`
- `search_after_token` as `{state, value}`

`total_count` is provider population testimony, not Observatory completeness.
`items_count=5` with `total_count=3055` is explicit truncation. Never compare `items_count`
with Outcome `observation_count=113`.

The token is historical testimony only. Preserve exact stated text or explicit `json_null`.
Never decode, parse, normalize, accept, or follow it as a cursor, query, Attempt input,
authorization, or acquisition instruction. Its presence must never cause another exchange.

### Search Mention items

Each `search_mention_items` member contains:

- `observation_kind` and `within_capture_identity`
- `requested_keyword`, `platform`, `model_name`, `location_code`, `language_code`
- exact `question` and exact Markdown `answer`
- integer `ai_search_volume` and `is_web_search_based`
- exact lexical `first_response_at` and `last_response_at`
- `search_results`, `brand_entities`, and `fan_out_queries` as
  `{state: "json_null", value: null}`
- complete ordered `{"item_index": n}` occurrences

Item clocks are neither Capture times nor Provider Update Times. Current volume is not
derived from monthly testimony.

### Monthly search volume

Each `monthly_search_volume` member contains:

- `observation_kind` and `within_capture_identity`
- `requested_keyword`, `model_name`, `question`
- `data_period` as exact `{year, month}`
- integer `search_volume`
- complete ordered `{"item_index": n}` occurrences

Data Period is independent of Capture time and item clocks. Do not invent or expose monthly
array position.

### Structured sources

Each `structured_sources` member contains:

- `observation_kind` and `within_capture_identity`
- `requested_keyword`, `model_name`, `question`
- exact `url` including query/fragment
- exact `title`, `domain`, `source_name`, `snippet`
- `publication_date`, `thumbnail`, and `markdown` as `{state, value}`
- complete ordered `{"item_index": n, "rank": n}` occurrences

Semantic source identity is
`(requested_keyword, model_name, question, exact URL)`. Repeated appearances of that identity
produce one parent with multiple occurrences. The same URL under another model or question is
a different parent. Do not normalize URLs, collapse domains, extract Markdown links, create
Page identity, or treat rank as identity.

## Membership and provenance

Follow Organic, not Keyword Overview. Anchor candidates with:

    search_mentions_result_context JOIN outcomes

Join the full `(derivation_version_id, attempt_id, capture_id)` tuple and require
`observation_admitted` or `observation_admitted_empty`. Filter context by resolved Recipe
and exact requested keyword.

Do not anchor membership on envelopes, a typed family, or Keyword Overview coverage. Those
choices hide admitted-empty history or use the wrong grain. A foreign-Attempt Outcome for
the same Capture/Recipe cannot duplicate or supply classification/count.

Non-admitted Outcomes, unresolved Attempts, partial/no-response, provider errors,
provider-envelope rejection, and reconciliation failure remain outside normal history and
visible through Attempt audit when applicable.

## Verify all matching candidates before limit

For every matching admitted candidate:

1. verify full Attempt Evidence;
2. verify full Capture Evidence, parent, bodies, sizes, and commit marker;
3. require exact DataForSEO provider and Search Mentions adapter on both;
4. require Capture parent equals the candidate Attempt;
5. require Attempt/context agreement;
6. perform the PostgreSQL checks below;
7. only then sort and limit.

Sort by `(request_started_at, capture_id)` ascending. Descending reverses the complete order
before limiting. Never truncate a group. Matching damage outside `limit=1` still returns 409.

## Capture-wide PostgreSQL checks

For each exact `(capture_id, derivation_version_id)`:

1. load complete envelope keys `(within_capture_identity, observation_kind)`;
2. require envelope cardinality equals Capture Outcome `observation_count`;
3. load complete typed keys from exactly items, monthly-search-volume, and sources;
4. require the typed-key union equals the envelope set: no missing, extra, wrong-kind, or
   duplicate semantic row;
5. exclude context and occurrences from envelope cardinality;
6. require every item, monthly, and source parent has at least one matching occurrence at
   the same Capture, Recipe, kind, and identity;
7. accept admitted-empty only as zero envelopes/typed rows, one context, zero occurrences.

Existing constraints remain the boundary for orphaned/misattached occurrences. Do not
reparse Evidence bodies, rerun Derivation, repair rows, or add stored counts/digests on GET.
These checks do not extend to Attempt audit; it may still display stale `observation_count`.

## Deterministic presentation order

Ordering is presentation, not identity:

- items: `model_name`, `question`, `within_capture_identity`
- item occurrences: `item_index`
- monthly: `year`, `month`, `model_name`, `question`, `within_capture_identity`
- monthly occurrences: `item_index`
- sources: `model_name`, `question`, `url`, `within_capture_identity`
- source occurrences: `item_index`, `rank`

Do not order semantic parents by placement fields as if they were identity.

## Read-only and isolation requirements

Every GET uses the accepted read-only PostgreSQL connection and never selects a Recipe,
derives, repairs, captures, follows continuation, calls a provider, or mutates Evidence,
PostgreSQL, selections, or files.

Preserve fixture, Keyword Overview, and Organic behavior. Expose no raw bodies, credentials,
authorization policy, spend ceiling, provider cost/duration/messages, task UUID/path/data
echo, scoring, recommendation, or strategy.

Keep Search Mentions SQL, assembly, context agreement, and occurrence nesting surface-local.
Do not add a generic `/observations` endpoint, universal AI metric, generic history
assembler, cross-provider projection, or shared provider-read framework.

## Acceptance criteria

- [ ] Exact route appears in OpenAPI and accepts only the closed query contract.
- [ ] Search Mentions Attempts support selected/pinned audit reads with no fixture/family
      fields; missing selection is 503 and invalid/wrong pins or no rows are 404.
- [ ] Frozen admitted Capture returns an independently projected complete group: 5 items,
      60 monthly parents, 48 source parents, 113 envelopes, 5-of-3055 context, exact token,
      complete answers/clocks/null states, and every occurrence.
- [ ] Frozen response proves the three real current-volume/newest-monthly disagreements.
- [ ] Duplicate semantic item and source identities collapse only to one parent with multiple
      occurrences; same URL under a different model/question remains a separate parent.
- [ ] Valid admitted-empty returns context with zero envelopes and empty families.
- [ ] Planted non-admitted context is excluded while a healthy sibling remains.
- [ ] Two Captures prove asc/desc, equal-time capture-ID tie-break, and whole-group limit.
- [ ] Foreign-Attempt Outcome cannot duplicate or supply membership/count.
- [ ] Missing/wrong Attempt parameters or Attempt/context disagreement returns exact 409.
- [ ] Damaged/cross-linked/wrong-adapter Attempt, Capture, or body Evidence returns exact 409
      inside and outside `limit=1`.
- [ ] Missing/extra typed rows, extra envelopes, wrong Outcome count, and zero-occurrence
      item/monthly/source parents each return exact 409 before limit.
- [ ] Token presence performs zero continuation, transport, capture, or derive action.
- [ ] Search Mentions selection/pinning is isolated from Keyword Overview and Organic; a
      second Search Mentions Recipe does not inflate resolved history.
- [ ] Reads preserve xmin/content across Recipes, selections, Outcomes, envelopes, all seven
      Search Mentions relations, and preserve Evidence operation logs.
- [ ] Two independently derived non-empty PostgreSQL databases return equal history.
- [ ] Fixture, Keyword Overview, Organic, and provider Attempt regressions remain unchanged.
- [ ] Ordinary tests enforce zero public network, DNS, provider, or credential use.

The frozen proof must use an independent persisted-to-API projection, not only production
assembler counts.

## Verification

After final implementation bytes:

- `uv run pytest -q`
- `uv run ruff check .`
- `uv run mypy`

Use real PostgreSQL for selection/projection/isolation/read-only/two-database claims and real
local format-2 Evidence for verification/damage claims. Record commands, UTC timing, exit
codes, pass/skip/warning counts, exact commits/tree state, and leftover test containers.
Any behavior-affecting change after the full suite invalidates that suite until rerun.

## Honest limits

Do not claim detection of coordinated internally consistent rewrites/deletions; deletion of
the only context anchor; loss of one occurrence while another remains; value corruption that
preserves keys/counts; PostgreSQL equality to raw bodies without re-Derivation; completeness
beyond 5-of-3055; concurrent writers; production auth/non-loopback exposure; routine
acquisition; prior Recipe-pointer history; or Provider Update Time semantics for item clocks.

Verify-all-before-limit is O(all matching Captures). There is no API cursor. These accepted
limits do not permit weakening the fail-closed checks.

## Out of scope

- provider/DNS/credential/sandbox/paid/public-network calls
- continuation, polling, retry, second exchange, scheduling, orchestration
- Target Metrics, ChatGPT, another platform/surface/provider
- Recipe, parser, identity, Derivation, fixture, Evidence, or transport change
- schema, migration, index, stored completeness state, or projection table
- raw bodies/provider-envelope exposure
- URL/Page normalization, Markdown-link extraction, scoring, strategy, reporting
- F7 concurrency, F8 auth/exposure, F9 writes, F10 projections, F12 orchestration
- relocating the Attempt loader or extracting a shared read/derive framework
- README or spec edits by the implementer

After implementation acceptance, the Steward will refresh the capture-event spec's current
provider-schema/read-surface pointer.

## Implementation constraints

- GROK alone writes `src/` and `tests/`.
- Start from clean `main` at the exact Steward-assigned commit.
- One implementation commit; do not amend or push.
- Implementer may update only this ticket's Status, Start commit, and Implementation report
  alongside code/tests; never set `done`.
- Report adjacent findings without implementing them.

## Implementer report required

Record loaded project-local skills; exact parent/child; paths; acceptance-to-test map;
route/query/response; membership/provenance; verify-before-limit and count grain; frozen
family/occurrence counts; selected/pinned/errors; independent projection and two-database
proof; read-only/zero-network evidence; query cost/scaling; strongest/weakest seams; exact
unproven limits; false premises; command evidence; clean tree; no provider, continuation,
schema/migration, authority edit, push, or scope drift.

## Implementation report

<!-- Implementer fills; may set Status: review; never Status: done. -->

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only. -->

- Closed at commit:
- Evidence accepted: yes/no

