# API-02 — Provider Measurement Outcomes

**Status:** provisional — mandatory [GROK] ticket review pending  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** read-only pre-implementation ticket review and Steward reconciliation  
**Question-resolution pass:** completed against `5fa8bc17835e45795deda380276dab7b3b078004`  
**Start commit:** not assigned

## Purpose

Add sibling, subject-filtered Measurement Outcomes resources for Keyword Overview,
Google Organic, and Search Mentions.

These resources answer a different consumer question from `/history`:

> What verified measurement activity does Observatory hold for this requested subject,
> and what Attempt- and Capture-stage classifications were derived under this Recipe?

They include unresolved Attempts and every closed provider Capture classification. They
never present failure material as an Observation and never include provider fact bodies.

API-02 is not implementation authority. After [GROK]'s mandatory read-only ticket review,
[GPT] must reconcile and commit the final ticket. [CHAZ] must separately authorize
implementation against that exact clean start commit.

## Question-resolution and decision lock

[GROK] completed the required code-first question pass against clean
`5fa8bc17835e45795deda380276dab7b3b078004`. [GPT] independently checked the material
schema, lifecycle, API, tests, and D14 claims. No Product question remains.

D9 and D14 already settle Keyword Overview's multi-keyword grain:

- one HTTP exchange is one Attempt and at most one Capture;
- Measurement Outcomes expose Attempt- and Capture-stage classifications;
- one multi-keyword exchange must not be exploded into apparently independent
  per-keyword measurements.

One list item is therefore one verified Attempt with an optional verified Capture and
Capture-stage Outcome. Keyword Overview filtering uses exact membership in the verified
Attempt keyword list. The same Attempt may match queries for different member keywords,
but appears once in any one response.

D14 rejects overloading Outcome with provider-specific subject arrays. API-02 adds no
subject column to `outcomes`, changes no Outcome identity, and adds no generic
`requested_subjects` field. Each surface exposes its own typed `request` mapping from
verified Attempt Evidence. Keyword Overview's `request.keywords` is exact request
testimony that discloses Capture-wide scope; it is not an Outcome field, coverage claim,
or item multiplication.

## Authority and current substrate

This ticket is bounded by D2, D3, D8/D9, D11/D12, D14, API-01, and PF-14.

API-01 is complete. Holdings remain the next separate D14 resource. Target Metrics Recipe
selection/read work remains AI-12.

The unchanged `outcomes` table stores only `attempt_id`, nullable `capture_id`,
`derivation_version_id`, `classification`, and `observation_count`. It has no
provider, subject, stage, or time fields. Subject identity and lifecycle testimony for
non-admitted activity must therefore come from verified Evidence.

Provider derivations write one Attempt-stage `authorized_unresolved` row for every
derived Attempt, including Attempts that later have a Capture, plus an optional
Capture-stage row. Raw rows are not consumer documents.

## Exact routes and query contract

Add exactly:

- `GET /v1/providers/dataforseo/google/keyword-overview/outcomes`
- `GET /v1/providers/dataforseo/google/organic/outcomes`
- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/outcomes`

Each route accepts:

- required `requested_keyword`;
- optional `derivation_version_id`;
- `limit`: default 20, minimum 1, maximum 100;
- `order`: `asc` or `desc`, default `asc`.

No all-subject route, cursor, offset, continuation, unbounded response, or new API version
is authorized.

## List grain and outer response

`total_matching` is the number of unique matching Attempt documents under the exact
route/provider/adapter, requested keyword, and resolved Recipe. It is not the number of
raw Outcome rows.

A successful exchange normally has an Attempt-stage row and a Capture-stage row. Pair
them into one item. The Attempt-stage name `authorized_unresolved` is lifecycle
vocabulary: when a verified Capture exists it must not be described as current unresolved
status. When no Capture exists, it must not be interpreted as definitely unsent.

Every route returns a typed object with exactly:

- `provider`;
- `adapter_contract`;
- `requested_keyword`;
- `derivation_version_id`;
- `recipe_resolution`;
- `observation_kinds`;
- `total_matching`;
- `returned_count`;
- `limit`;
- `order`;
- `has_more`;
- `outcomes`.

`returned_count == len(outcomes)`.

`has_more == (total_matching > returned_count)`.

`has_more` discloses an omitted tail only. It provides no pagination capability and no
way to retrieve a tail beyond the maximum limit of 100.

Do not count or manufacture items from Observation envelopes, typed facts, provider
result/corpus counts, SQL join multiplicity, individual keywords, fixture/sandbox/Target
Metrics adapters, or a Capture without its verified parent Attempt.

## Exact shared item boundary

Every item has exactly:

- `attempt_id`;
- nullable `capture_id`;
- `provider`;
- `adapter_contract`;
- `derivation_version_id`;
- `authorized_at`;
- nullable `request_started_at`;
- nullable `transport_ended_at`;
- nullable `transport_state`;
- surface-specific typed `request`;
- `attempt_outcome`;
- nullable `capture_outcome`.

`attempt_outcome` and non-null `capture_outcome` each have exactly:

- `classification`;
- `observation_count`.

With no Capture, `capture_id`, all Capture time/state fields, and
`capture_outcome` are null. With a Capture, all are non-null and agree with the same
verified Capture.

Do not add Observation facts, response bodies, headers, diagnostics, provider task
objects, billing testimony, recommendations, or a synthesized combined status.

## Surface-local request testimony

The typed `request` object comes only from the verified Attempt.

Keyword Overview:

- `keywords` — exact ordered 1..5 keyword list;
- `location_code`;
- `language_code`;
- `include_serp_info`;
- `include_clickstream_data`.

Google Organic:

- `keyword`;
- `location_code`;
- `language_code`;
- `depth`;
- `device`;
- `os`;
- `group_organic_results`;
- `load_async_ai_overview`.

Search Mentions:

- `keyword`;
- `match_type`;
- `search_filter`;
- `search_scope`;
- `platform`;
- `location_code`;
- `language_code`;
- `limit`;
- `offset`.

The top-level `requested_keyword` echoes the filter. Keyword Overview requires exact
membership in `request.keywords`; the other routes require equality with
`request.keyword`.

These mappings preserve request scope, not provider response facts. Do not generalize
them into one universal subject model.

## Closed classification semantics

The only accepted Attempt-stage classification is:

- `authorized_unresolved`.

The closed Capture-stage set is:

- `no_response`;
- `response_partial`;
- `transport_complete_non_admissible`;
- `provider_envelope_rejected`;
- `provider_error`;
- `reconciliation_failed`;
- `observation_admitted`;
- `observation_admitted_empty`.

Unexpected classifications, duplicate stage rows, a non-null Capture ID at Attempt stage,
a null Capture ID at Capture stage, or disagreement with verified lifecycle Evidence fail
closed with HTTP 409.

`observation_admitted_empty` is valid Outcomes activity for all three derivations even
though Keyword Overview cannot expose it as a subject-bound history document. Outcomes
must not reuse admitted-history membership.

## Evidence discovery and verification

At current pre-F12 volume, use D14's accepted bridge: a bounded read-only scan of committed
Evidence.

For each request:

1. Resolve the selected or explicitly pinned Recipe for the route's exact adapter.
2. Enumerate committed Attempt and Capture identities through the existing Evidence Store.
3. Verify identity, committed marker, manifest bytes, referenced bodies, body sizes,
   parentage, and closed schema before using a document.
4. Build provider/adapter lifecycle relationships from verified Evidence.
5. Apply surface-local keyword membership to verified Attempt parameters.
6. Require the exact PostgreSQL Attempt-stage Outcome under the resolved Recipe for every
   matching Attempt.
7. If Evidence has a Capture, require its exact Capture-stage Outcome. If it has none,
   require no Capture-stage row for that item.
8. Verify all matching items and rebuildable state before ordering, counting, or limiting.

Evidence defines membership and subject identity. PostgreSQL does not nominate candidates.
Missing required state, extra/foreign stage state for a matching Attempt, wrong parent,
wrong adapter/provider/Recipe, or Evidence disagreement is HTTP 409 with no partial
Outcomes envelope.

The pre-implementation review must explicitly assess whether the current Evidence Store
interface can implement this adapter-scoped lifecycle scan without silently skipping
unreadable or unrelated committed events, and what availability behavior unrelated damage
would create. If the boundary is false, [GROK] must request the smallest ticket correction
rather than broaden implementation.

## Observation-count integrity

API-02 hardens counts served by the new ledger while leaving
`GET /v1/attempts/{attempt_id}` unchanged.

For every matching item:

- Attempt-stage `observation_count` is zero.
- Capture-stage count equals `observation_envelopes` cardinality for the exact Capture
  and resolved Recipe.
- Non-admitted and `observation_admitted_empty` classifications require zero envelopes
  and count zero.
- `observation_admitted` requires exact stored-count/envelope-cardinality equality.

Any disagreement is HTTP 409, including in a matching item outside the returned limit.

Do not import history's full typed-row equality or subordinate-occurrence checks. Those
remain the admitted fact-document/history boundary under PF-14 and D14.

The existing Attempt audit may still return a stale count; that accepted PF-14 limit is not
remediated here.

## Ordering, limiting, transaction, and errors

The deterministic order is `(authorized_at, attempt_id)`. Ascending uses that tuple;
descending reverses the complete verified order before limiting. Do not use Capture request
time because unresolved Attempts have none.

Use a read-only PostgreSQL transaction. Complete matching Evidence and PostgreSQL
verification before `total_matching` or slicing.

A successful empty response has `outcomes: []`, zero totals, the applied limit, echoed
order, and `has_more: false`. It means no verified matching Attempt with complete
matching rebuildable Outcome state is held under this route, subject, and Recipe. It does
not mean the subject is unimportant, the provider reported absence, nothing exists under
another surface/Recipe, or Observatory intends a cadence.

Keep stable meanings:

- invalid query: FastAPI 422;
- unselected Recipe: HTTP 503;
- unavailable/wrong pin: HTTP 404;
- integrity disagreement: HTTP 409
  `{"detail":"evidence_integrity_failure"}`;
- successful empty scoped list: HTTP 200.

A 409 exposes no Outcomes envelope or partial count.

## Typed OpenAPI contract

All three routes require typed response and surface-specific request models. OpenAPI must
state:

- one item is one Attempt/exchange, not one stage row or requested keyword;
- `authorized_unresolved` is not definitely unsent or a combined current status;
- `capture_outcome=null` means no verified Capture is held;
- classifications are derived, Recipe-addressed Outcome testimony;
- `observation_count` counts Observation envelopes, not provider results/corpus;
- request mappings are verified, surface-local Attempt testimony;
- `has_more` does not provide pagination;
- items contain no Observation facts;
- empty-scope and failure/absence inference limits.

A generic untyped request mapping or universal provider request schema is insufficient.

## Shared and surface-local implementation boundary

A small `src/observatory/provider_outcomes.py` may own only limit constants, shared
classification/Outcome-view typing, common item fields, and outer metadata/invariant math.

Each surface reader retains adapter/Recipe inputs, verified subject membership, exact
request mapping, lifecycle validation, PostgreSQL queries/count verification, and item
projection.

Reuse API-01 envelope mathematics and limits where practical, but do not call this history,
reuse `HistoryListEnvelope`, build a generic provider loader, create a universal
request/subject model, or use PostgreSQL-first candidate selection.

## Proposed changed-path allowlist

Production:

- `src/observatory/provider_outcomes.py` — new bounded shared types/math;
- `src/observatory/keyword_overview_read.py`;
- `src/observatory/google_organic_read.py`;
- `src/observatory/search_mentions_read.py`;
- `src/observatory/api.py`.

Tests:

- `tests/test_api_keyword_overview.py`;
- `tests/test_api_google_organic.py`;
- `tests/test_api_search_mentions.py`;
- optional `tests/test_provider_outcomes.py` for shared invariants only.

Ticket:

- `tickets/API-02-provider-measurement-outcomes.md`.

No migration, schema, Evidence Store, Recipe, parser, derive, provider-gate, or history path
is authorized. A necessary path outside this list must return to [GPT] before
implementation.

## Acceptance criteria

### Response, grain, and classifications

- [ ] All routes expose the exact typed outer and item boundaries.
- [ ] One matching Attempt produces one item regardless of keyword count or Capture.
- [ ] A Keyword Overview multi-keyword Attempt appears once for each member query and never
      duplicates within a response; a non-member does not match.
- [ ] Attempt and optional Capture Outcome rows are paired without a combined status.
- [ ] Unresolved, every closed non-admitted classification, admitted, and admitted-empty
      activity are representable without failure material becoming an Observation.
- [ ] Unexpected, missing, duplicate, or lifecycle-inconsistent stage state returns 409.
- [ ] No item contains Observation fact bodies.

### Counts and order

- [ ] Zero, one, and over-limit Attempt counts are proven for each route.
- [ ] `total_matching` counts Attempts, not rows, keywords, envelopes, provider items, or
      joins.
- [ ] `returned_count == len(outcomes)` and
      `has_more == (total_matching > returned_count)`.
- [ ] Ascending/descending `(authorized_at, attempt_id)` ordering is proven before limit.
- [ ] Matching damage outside `limit=1` still returns 409 without a partial envelope.

### Integrity and request contracts

- [ ] Subject identity comes from verified Attempt Evidence.
- [ ] Matching Attempt/Capture Evidence is verified before use.
- [ ] Missing PostgreSQL stage state returns 409 rather than empty/partial success.
- [ ] Wrong parent, adapter, provider, Recipe, stage, or Capture relationship returns 409.
- [ ] Capture count equals exact Observation-envelope cardinality; non-admitted and
      admitted-empty counts are zero.
- [ ] A stale count accepted by the old Attempt audit is rejected by Outcomes while that
      existing route remains unchanged.
- [ ] Each route exposes its exact verified surface-local request key set.
- [ ] Malformed or drifted required Attempt parameters fail closed.
- [ ] No GET mutates Evidence, PostgreSQL, Recipe selection, or acquisition state.
- [ ] Search Mentions continuation is never read or followed.

### OpenAPI and architecture

- [ ] OpenAPI tests assert grain, stages, counts, completeness, null-Capture, and inference
      semantics—not only field names.
- [ ] Request models remain surface-specific and typed.
- [ ] Shared code knows no provider table names or request shapes.
- [ ] No schema, migration, history membership, parser, Recipe, derive, or provider
      behavior changes.

## Required independent test vectors

At minimum:

1. unresolved Attempt for each surface;
2. representative non-admitted Capture for each surface;
3. admitted and admitted-empty Capture activity;
4. Keyword Overview five-keyword membership and single-item grain;
5. non-member subject exclusion;
6. zero/one/over-limit counts for every route;
7. authorized-time/Attempt-ID ascending and descending order;
8. matching damage outside the returned limit;
9. missing and duplicate/wrong-stage PostgreSQL rows;
10. wrong Capture parent/provider/adapter/Recipe;
11. stale `observation_count` versus envelope cardinality;
12. exact request keys and malformed parameters per surface;
13. exact response keys and substantive OpenAPI descriptions;
14. tripwires proving no transport, continuation, Derivation, Evidence write, or
    PostgreSQL mutation.

Synthetic tests prove constructed branches, not that those branches occurred in live
provider Evidence.

## Honest limits

API-02 does not provide or prove:

- cursor/offset pagination or retrieval beyond 100;
- a scalable recurring-acquisition subject index;
- holdings or observed-subject discovery;
- all-provider/cross-surface activity;
- fact-body integrity beyond envelope cardinality;
- repair or re-Derivation of missing state;
- coordinated corruption detection preserving all checked identities/counts;
- a synthesized current/final status;
- provider-corpus completeness;
- whether unresolved activity was sent;
- strategy, importance, panels, cadence, or recommendations.

The Evidence scan is an explicit low-volume bridge. A scalable rebuildable
measurement-subject index remains required before F12-scale acquisition.

## Forbidden scope

Do not add or modify:

- database schema, migration, or `outcomes` identity/columns;
- Evidence layouts, bodies, manifests, Store behavior, or write paths;
- parsers, Recipes, Recipe selection, or derivation;
- Observation kinds, facts, identities, or occurrence relations;
- existing history contracts or the existing Attempt audit;
- holdings or AI-12 Target Metrics read work;
- transport, credentials, spend, continuation, or another exchange;
- Google Organic `related_result` handling;
- outer pagination or direct Evidence/PostgreSQL consumer access;
- F7, F12, F13, strategy, scoring, recommendations, panels, or cadence;
- unrelated refactors.

Missing enforcement of D14's non-null Organic `related_result` stop-before-derive rule
is separate authority/code drift. API-02 must not claim to repair it. It remains a gate
before affected future derivation/live/F12 work.

## Mandatory pre-implementation ticket review

[GROK] must review this provisional ticket read-only against its exact committed parent and
return:

- false premises or authority conflicts;
- whether one-Attempt pairing hides any stage disagreement;
- whether the current Evidence Store supports the stated lifecycle scan, including
  unrelated-damage availability behavior;
- missing checks or checks exceeding D14/PF-14;
- request-shape, classification, or count-grain errors;
- likely false greens;
- helper coupling or changed-path problems;
- OpenAPI/consumer-readiness gaps;
- READY or REQUIRES TICKET CORRECTION.

No implementation, tests, mutation, provider call, credentials, or Evidence activity is
authorized during review.

## Implementation report requirements

If later authorized, [GROK]'s report must include exact commits/paths; targeted verification;
all route/OpenAPI changes; verify-before-limit and count proof; strongest/weakest aspects;
false greens; caller influence; coupling; provider traps; blockers/deferred work; later
reuse versus surface-local behavior; Evidence versus claimed contract versus synthetic
proof; useful/not-useful strategy implications; data-model implications and unsafe
inferences; clean tree; no push; and zero provider/network/credential activity.

## Verification commands for later implementation

Targeted:

    uv run pytest -q \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

Include `tests/test_provider_outcomes.py` if created. During implementation also run:

    uv run ruff check .
    uv run mypy

The full suite is reserved for the final exact-HEAD operator block after review/remediation.

## Implementation report

Not started. Implementation is unauthorized.
