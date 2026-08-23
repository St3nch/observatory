# AI-06 — Search Mentions recipe selection and read API

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Parent spec:** `docs/specs/capture-event-v2.md`  
**Blocked by:** AI-05 — Search Mentions provider Derivation and typed persistence (`done`)  
**Approved by:** Project Steward  
**Technical-review base:** `c73d4ec60daf1331de63e47113807473000eff03`  
**Start commit:** `a0df3ab9b218b3c823dcf569c209d1d173069501`

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

**Parent:** `a0df3ab9b218b3c823dcf569c209d1d173069501`  
**Child:** this implementation commit  
**Status:** `review`  
**AI-06 only:** yes. Nothing pushed.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/api.py` (Search Mentions Attempt allowlist + history route)
- `src/observatory/search_mentions_read.py` (new surface-local history assembly)
- `tests/test_api_search_mentions.py` (new)
- this ticket (Start commit, Status, Implementation report)

No Recipe, parser, identity, Derivation, fixture, Evidence, schema, migration, README, spec, decision, or vocabulary change. `load_provider_attempt` was not relocated. No shared provider-read framework.

### Route / query / response

- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/history`
- query: required `requested_keyword`; optional `derivation_version_id`; `limit` default 20, min 1, max 100; `order` `asc`|`desc` default `asc`
- OpenAPI path and closed parameter set proven
- Capture groups expose `search_mention_items`, `monthly_search_volume`, `structured_sources` plus request, result_context, and provenance envelope
- `observation_kinds` in Recipe order: item, monthly, source

### Membership / provenance / verify-before-limit

Candidates are `search_mentions_result_context JOIN outcomes` on the full
`(derivation_version_id, attempt_id, capture_id)` tuple, filtered to
`observation_admitted` / `observation_admitted_empty`, resolved Recipe, and exact
keyword. Every matching candidate verifies Attempt and Capture Evidence, provider
and adapter on both, Capture parent, Attempt/context agreement, then Capture-wide
PostgreSQL checks, then sort/limit. Check 7 is classification-gated: admitted-empty
requires `observation_count == 0` and zero envelopes/typed rows/occurrences;
admitted requires `observation_count > 0`, envelope cardinality equal to that
count, typed-key union equal to the envelope set, and every typed parent at least
one matching occurrence. Context and occurrences are excluded from envelope
cardinality. Attempt audit still may display a stale classification/count.

### Frozen family / occurrence counts

Independent persisted-to-API projection of the AI-03 Capture:

- 5 items / 5 item occurrences
- 60 monthly parents / 60 monthly occurrences
- 48 source parents / 48 source occurrences
- 113 envelopes
- context `items_count=5`, `total_count=3055`, `result_offset=0`, exact stated token
- three current-volume vs newest-monthly disagreements:
  `search engine optimized` 135000 vs 110000,
  `seos` 110000 vs 60500,
  `engine optimization service` 110000 vs 49500

### Selected / pinned / errors

- no selection: HTTP 503 `provider_recipe_not_selected`
- malformed / unknown / wrong-adapter pin: HTTP 404 `not found` on Attempt and history
- selected/pinned production Recipe with no matching keyword: HTTP 200 `captures: []`
- selected Recipe with no derived Outcomes: Attempt HTTP 404
- integrity disagreement: HTTP 409 `evidence_integrity_failure`

### Acceptance-to-test map

| Criterion | Test |
|---|---|
| Exact route and closed query / OpenAPI | `test_frozen_history_shape_counts_token_and_volume_disagreements` |
| Selected/pinned Attempt audit; 503/404; no family fields | `test_search_mentions_attempt_selected_pinned_and_http_errors` |
| Frozen complete group + independent projection + token + 5-of-3055 | `test_frozen_history_shape_counts_token_and_volume_disagreements` |
| Three volume/newest-monthly disagreements | `test_frozen_history_shape_counts_token_and_volume_disagreements` |
| Duplicate item/source collapse; same URL under another question stays separate | `test_duplicate_identities_collapse_and_cross_question_urls_stay_separate` |
| Admitted-empty + planted non-admitted excluded | `test_admitted_empty_and_non_admitted_context_stay_distinct` |
| Classification/emptiness swap 409 both directions; valid admitted and admitted-empty 200 | `test_swapped_outcome_classification_is_409` |
| Classification disagreement outside `limit=1` still 409; Attempt audit stale | `test_classification_disagreement_outside_limit_is_409` |
| Asc/desc, capture-id tie-break, whole-group limit | `test_second_capture_order_limit_and_tie_break` |
| Foreign-Attempt Outcome cannot supply membership/count | `test_foreign_attempt_outcome_does_not_supply_history` |
| Missing/wrong Attempt parameters and Attempt/context disagreement 409 | `test_request_context_integrity_and_damage_409` |
| Damaged/cross-linked/wrong-adapter Evidence 409 inside and outside `limit=1` | `test_request_context_integrity_and_damage_409`, `test_history_consistency_damage_outside_limit_is_409` |
| Missing/extra typed keys, extra envelopes, wrong Outcome count, zero-occurrence parents 409 | `test_history_missing_and_extra_typed_rows_are_409`, `test_history_extra_envelope_wrong_count_and_zero_occurrences_are_409` |
| Token performs zero continuation/transport/capture/derive | `test_token_presence_performs_zero_continuation_or_transport` |
| Isolation from KO/Organic/fixture; second Recipe does not inflate selected history | `test_fixture_ko_and_organic_remain_isolated_from_search_mentions_selection` |
| xmin/content + Evidence ops read-only | `test_api_reads_do_not_mutate_search_mentions_state` |
| Two independently derived non-empty databases | `test_two_databases_return_equal_search_mentions_history` |
| Fixture/KO/Organic/Attempt regressions | existing suites plus isolation test |
| Zero public network/DNS/provider/credential | autouse socket/getaddrinfo/credential guards in `tests/test_api_search_mentions.py` |

### Independent projection and two-database proof

`_persisted_projection` maps the seven AI-05 relations plus envelope count to the
API shape without calling `load_search_mentions_history`. Frozen history JSON
equals that projection. Two PostgreSQL databases independently derived from one
Evidence Store return equal non-empty history (`observation_count=113`).

### Read-only / zero-network evidence

GET uses `default_transaction_read_only=on`. xmin snapshots cover recipes,
selections, Outcomes, envelopes, and all seven Search Mentions relations.
Evidence `recorded_ops` is unchanged. Ordinary tests patch
`socket.create_connection`, `socket.getaddrinfo`, and DataForSEO credential
loaders; the token test also tripwires derive, paid capture, HTTP exchange, and
fixture capture.

### Query cost / scaling

Verify-all-before-limit is O(all matching Captures): two Evidence reads per
candidate, then Capture-wide envelope/typed/occurrence SQL for the full matching
set, then sort/limit. Returned groups issue six family/occurrence queries each.
There is no API cursor. This accepted cost was not weakened.

### Strongest / weakest seams

Strongest: Organic-style context⋈Outcome membership; verify-all-before-limit;
independent projection; two-database equality; Capture-wide envelope/typed/
occurrence fail-closed.

Weakest: extra typed rows without an extra envelope are schema-blocked by the
envelope FK, so extra typed is proven as extra envelope keys vs typed after
`observation_count` is bumped to match; Attempt missing/wrong-typed parameters
are proven by mutating the verified Attempt view, not by rewriting committed
Attempt bytes; occurrence nesting order is presentation SQL, not identity.

### Unproven limits

Coordinated internally consistent rewrites/deletions; deletion of the only
context anchor; loss of one occurrence while another remains; value corruption
that preserves keys/counts; PostgreSQL equality to raw bodies without
re-Derivation; completeness beyond 5-of-3055; concurrent writers; production
auth/non-loopback exposure; routine acquisition; prior Recipe-pointer history;
Provider Update Time semantics for item clocks.

### False premises

None that changed implementation. Source ranks in mutated duplicate-identity
bodies must remain contiguous from 1 or the parser rejects the Capture.

### Command evidence

Final implementation bytes, then:

```
uv run pytest -q
```

UTC `2026-08-23T21:18:07Z` → `2026-08-23T21:22:51Z`, exit 0, **1043 passed**,
**1 skipped**, 1 Starlette TestClient deprecation warning, 283.29s.

```
uv run ruff check .
```

UTC `2026-08-23T21:22:56Z`, exit 0, all checks passed.

```
uv run mypy
```

UTC `2026-08-23T21:22:56Z` → `2026-08-23T21:22:57Z`, exit 0, no issues in 56
source files.

No leftover `observatory-ce05-*` test containers. No behavior-affecting change
after this suite.

### Review findings remaining

Standards: no hard violations. Judgement only — local helper names
`_items`/`_monthly`/`_sources` vs presentation keys; candidate tuple vs named
type; Organic-copied `_json_value` breadth. Ticket forbids extracting a shared
read framework, so Organic duplication was left local.

Spec gaps found and fixed in this commit: history-route pin 404s;
`request_offset` disagreement; extra typed-key 409 isolated from extra-envelope
count mismatch. No residual spec defects.

### Clean tree / no push / no scope drift

One implementation commit on `main` whose parent is
`a0df3ab9b218b3c823dcf569c209d1d173069501`. Working tree clean after that
commit. Nothing pushed. No provider, DNS, credential, sandbox, paid, or public
network call. No continuation follow. No schema or migration. No authority edit
outside this ticket's implementer fields.

### Classification-gated check 7 remediation

Steward ruled check 7 classification-gated. Parent of this remediation:
`74283f8703880c0b530a666173eb648b6d22f968`. Status remains `review`.

Changed paths: `src/observatory/search_mentions_read.py`,
`tests/test_api_search_mentions.py`, this Implementation report.

Mechanism: `_assert_history_candidates_consistent` now receives
`(capture_id, classification, observation_count)` for every matching candidate
before sort/limit. `observation_admitted_empty` fail-closes unless count is 0 and
envelope/typed sets are empty, then leftover occurrence rows fail closed.
`observation_admitted` fail-closes unless count > 0, envelope cardinality equals
count, typed keys equal envelopes, and every typed parent has a matching
occurrence. Unexpected classification fail-closes.

Planted swaps (classification only):

- frozen admitted Capture relabeled `observation_admitted_empty` with count 113
  and 113 envelopes → history HTTP 409 `evidence_integrity_failure`
- derived admitted-empty Capture relabeled `observation_admitted` with count 0
  and zero envelopes → history HTTP 409 `evidence_integrity_failure`
- same swap on a later Capture with `limit=1` (earlier sibling healthy) → 409
- valid admitted and admitted-empty GETs remain 200

Adjacent finding (not implemented): Organic and Keyword Overview GET still
accept a swapped classification when count/envelopes agree. Attempt audit still
returns 200 with the planted stale classification/count.

No schema, migration, Evidence, Recipe, Derivation, API shape, route, query,
Organic, KO, unknown-query, framework, provider, or network change.

Remediation suite after final behavior-affecting bytes:

```
uv run pytest -q
```

UTC `2026-08-23T21:49:28Z` → `2026-08-23T21:54:21Z`, exit 0, **1045 passed**,
**1 skipped**, 1 Starlette TestClient deprecation warning, 292.59s.

```
uv run ruff check .
```

UTC `2026-08-23T21:54:25Z`, exit 0.

```
uv run mypy
```

UTC `2026-08-23T21:54:25Z` → `2026-08-23T21:54:26Z`, exit 0, 56 source files.

No leftover `observatory-ce05-*` containers. Ticket report fill after this
suite is documentation only.

## Closure

<!-- Project Steward only. -->

- Closed at commit:
- Evidence accepted: yes/no

