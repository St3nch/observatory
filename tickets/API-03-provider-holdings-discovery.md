# API-03 — Provider Holdings discovery

**Status:** provisional — mandatory [GROK] read-only ticket review required  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** final Steward reconciliation after the mandatory ticket review  
**Question-resolution pass:** completed against `ed5bf39923f3872ff9ecc96962d58a89847e0bee`  
**Product lock:** [CHAZ] approved subject-plus-exact-scope / Evidence-only / catalog-order Holdings  
**Start commit:** unset — implementation is not authorized

## Purpose

Add the third D14 consumer resource for Keyword Overview, Google Organic, and Search
Mentions: surface-explicit discovery lists describing the exact requested subjects and
request scopes for which Observatory holds verified Attempt Evidence.

Holdings answers a question that admitted history and subject-filtered Outcomes cannot:

> Under this provider surface, which exact requested subjects and request scopes does
> Observatory have verified measurement Evidence for?

It is an Evidence-backed inventory projection. It is not admitted Observation history,
Recipe-addressed Outcome activity, provider corpus coverage, a desired panel, monitoring
state, importance, cadence, recommendation, or strategy.

API-03 is not implementation authority. [GROK] must first perform the mandatory read-only
adversarial review of this provisional ticket. [GPT] must reconcile that review and commit
the final accepted ticket. [CHAZ] must then separately authorize implementation against
the named exact clean start commit.

## Question-resolution and Product lock

[GROK] completed a code-first Holdings question pass and a bounded technical reaction
against clean `ed5bf39923f3872ff9ecc96962d58a89847e0bee`. [GPT] independently verified
the material D14, schema, Evidence, API, reader, and API-02 claims.

[CHAZ] approved these three Product choices:

1. **Subject plus exact request scope.** One Holdings item is one distinct exact requested
   subject plus the complete surface-local request tuple under which it appeared.
2. **Evidence-only and Recipe-independent.** Membership, counts, and times come only from
   verified Attempt/Capture Evidence. Recipe selection and PostgreSQL state do not affect
   Holdings availability or membership.
3. **Catalog order.** Holdings uses deterministic exact subject/scope order, not recency,
   importance, or strategy ranking.

These choices stay inside Observatory's factual inventory purpose. A downstream strategy
consumer may reason from the testimony, but Observatory does not decide what is important,
sufficient, current, recommended, or worth measuring next.

No Product question remains.

## Authority and accepted boundary

- D2/D3: every consumer is API-only; strategy and recommendations remain outside
  Observatory.
- D8: Evidence is authoritative; reads verify and fail closed.
- D9: one provider exchange is one Attempt and at most one Capture. Keyword Overview's
  1..5 requested keywords do not become 1..5 exchanges.
- D11-D14: provider and surface scope, provenance, time, absence, completeness, and
  limitations remain explicit; Holdings is distinct from history and Outcomes.
- API-01: every bounded consumer list discloses complete cardinality metadata before its
  applied limit; `has_more` does not create pagination.
- API-02: the current low-volume bridge is a store-wide verify-first Evidence walk with
  no partial payload on integrity failure.
- F12 remains deferred. A scalable rebuildable measurement-subject index is required
  before F12-scale recurring acquisition, not in API-03.
- F13 is not fired by this read-only API ticket. No provider gate, live invocation,
  substantive acquisition modification, or affected-gate reuse is authorized.

## Exact routes and query contract

Add exactly:

- `GET /v1/providers/dataforseo/google/keyword-overview/holdings`
- `GET /v1/providers/dataforseo/google/organic/holdings`
- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/holdings`

Each route accepts only:

- `limit`: integer, default 20, minimum 1, maximum 100;
- `order`: `asc` or `desc`, default `asc`.

Do not accept `requested_keyword`, `derivation_version_id`, Recipe selection, prefix,
subject filter, scope filter, cursor, offset, continuation, or provider token.

Caller-controlled influence is limited to the bounded outer limit and exact catalog-order
direction.

## Exact outer response boundary

Each successful route returns a closed typed envelope with exactly eight keys:

- `provider`
- `adapter_contract`
- `total_matching`
- `returned_count`
- `limit`
- `order`
- `has_more`
- `holdings`

Extra keys are forbidden.

`provider` and `adapter_contract` disclose the route scope. There is deliberately no
top-level subject filter or Recipe scope.

`total_matching` is the number of unique Holdings groups after complete store-wide
Evidence verification, exact route-adapter filtering, surface-local request extraction,
and grouping, but before ordering/limiting. It counts subject-plus-exact-request groups,
not Attempts, Captures, Outcome rows, Observation envelopes, facts, provider result items,
provider corpus totals, or independent exchanges.

`returned_count == len(holdings)`.

`has_more == (total_matching > returned_count)`. It discloses an omitted catalog tail. It
is not pagination, a cursor, or authority to fetch another page. A tail beyond the maximum
limit of 100 remains known but unavailable.

Do not include `requested_keyword`, `derivation_version_id`, `recipe_resolution`,
`observation_kinds`, `outcomes`, or `captures` on the envelope.

## Exact item boundary

Every item is closed and has exactly nine keys, including its surface-specific `request`:

- `requested_keyword`
- `request`
- `attempt_count`
- `capture_count`
- `unresolved_count`
- `first_authorized_at`
- `last_authorized_at`
- `first_request_started_at`
- `last_request_started_at`

Extra keys are forbidden.

### Subject and scope

`requested_keyword` is the exact verified Attempt parameter string for the discoverable
member represented by this item. Do not case-fold, normalize, trim, translate, or substitute
a returned provider keyword.

`request` is the complete closed surface-local request testimony defined below. The
grouping identity is the exact pair `(requested_keyword, request)`. Equivalent
`request_fingerprint` values are not the Holdings identity and are not exposed.

### Counts

For the exact Holdings group:

- `attempt_count` is the number of unique verified Attempts and is at least 1;
- `capture_count` is the number of those Attempts having exactly one verified Capture;
- `unresolved_count` is the number of those Attempts having no Capture;
- `attempt_count == capture_count + unresolved_count`.

`unresolved_count` uses the canonical authorized/unresolved lifecycle meaning only. It does
not mean definitely unsent, currently queued, retryable, or current operational status.

Counts come only from verified Evidence. They are not Observation counts, admitted counts,
provider item/corpus/result counts, rankings, mentions, query volume, panels, or cadence.

### Time boundaries

- `first_authorized_at` / `last_authorized_at` are the minimum/maximum canonical
  `authorized_at` values among the group's verified Attempts.
- `first_request_started_at` / `last_request_started_at` are the minimum/maximum canonical
  `request_started_at` values among the group's verified Captures.
- Both request-time fields are null exactly when `capture_count == 0`; otherwise both are
  non-null.

These fields are Evidence testimony. `last_authorized_at` is not “last monitored,” a cadence,
a desired refresh time, or current status. API-03 adds no `transport_ended_at` field.

### Identifiers deliberately omitted

Do not expose full, sampled, first, or latest Attempt/Capture ID lists. Full lists would be
unbounded inside one bounded outer item; samples are not inventory; first/latest IDs invite
a false current-measurement interpretation. History and Outcomes retain event-level
testimony for a known subject.

Do not place provider, adapter, Recipe, Outcome, transport, Observation, or strategy fields
on an item.

## Surface-local request testimony and grouping

The API may define the three explicit typed request/item models together in the new shared
Holdings module, following the API-02 typing precedent. This does not create a universal
subject model. Extraction, parameter validation, member expansion, and grouping remain in
the three surface readers.

### Keyword Overview

`request` has exactly:

- `keywords` — exact ordered unique 1..5 `parameters.keywords`;
- `location_code`;
- `language_code`;
- `include_serp_info`;
- `include_clickstream_data`.

One verified Attempt with N keywords produces N Holdings memberships, one for each exact
member, while retaining the complete ordered keyword bundle in every member's `request`.
The grouping identity is:

`(requested_keyword, keywords, location_code, language_code, include_serp_info, include_clickstream_data)`

An Attempt for `["seo api"]` does not merge with an Attempt for
`["seo api", "local seo"]`. For one shared Attempt, each member item has the same factual
counts and time boundaries. OpenAPI must state that one exchange may appear in up to five
Holdings items and that this does not prove five measurements or five independent exchanges.

### Google Organic

`request` has exactly:

- `keyword`;
- `location_code`;
- `language_code`;
- `depth`;
- `device`;
- `os`;
- `group_organic_results`;
- `load_async_ai_overview`.

`requested_keyword == request.keyword`. The duplicate display is deliberate: the common
item field is the discoverable subject and the request remains exact surface testimony.

### Search Mentions

`request` has exactly:

- `keyword`;
- `match_type`;
- `search_filter`;
- `search_scope` — exact Attempt array order;
- `platform`;
- `location_code`;
- `language_code`;
- `limit`;
- `offset`.

`requested_keyword == request.keyword`. `request.limit` and `request.offset` are the closed
Attempt fields, not Holdings list pagination. Do not read or follow `search_after_token`.

## Deterministic catalog order

Build every group and complete all verification before sorting or limiting. Ascending uses
the complete exact group identity; descending reverses that same complete key before
slicing.

Use exact canonical stored types:

- strings by Python/Unicode code-point order, with no locale, case-fold, or keyword
  normalization;
- integers numerically;
- booleans `False < True`;
- arrays as nested tuples preserving exact order, never flattened or sorted copies.

The exact ascending keys are:

- Keyword Overview: `(requested_keyword, tuple(keywords), location_code, language_code,
  include_serp_info, include_clickstream_data)`;
- Google Organic: `(requested_keyword, keyword, location_code, language_code, depth,
  device, os, group_organic_results, load_async_ai_overview)`;
- Search Mentions: `(requested_keyword, keyword, match_type, search_filter,
  tuple(search_scope), platform, location_code, language_code, limit, offset)`.

Do not add `min_attempt_id` or another defensive sort tie-break. The grouping identity is
already unique and therefore a total item order. If duplicate group identities survive
grouping, fail closed rather than masking the defect with an event identifier.

Catalog order is not recency, provider item order, importance, or strategy rank.

## Evidence discovery and integrity

Reuse API-02's `load_verified_store_events` low-volume bridge. Do not copy the Evidence
walk or build a generic provider/subject loader.

The Holdings projection must additionally verify every committed Capture's relationship to
its verified parent Attempt across the complete store before adapter filtering:

- parent Attempt is committed;
- parent has at most one Capture;
- Capture provider equals parent Attempt provider;
- Capture adapter equals parent Attempt adapter.

The existing shared walk verifies committed identities, bundles, bodies, parent existence,
duplicate identities, and the one-Capture limit, but parent provider/adapter comparison is
currently performed later by API-02 projection. API-03 must not assume the walk already
performs that global relationship check. Add Holdings-local shared relationship validation
without changing history or Outcomes behavior in this ticket.

Only after complete store-wide verification may successfully verified foreign providers or
adapters be excluded. For the exact route adapter, extract and validate every Attempt's
closed surface parameters before grouping. A malformed route-adapter Attempt cannot be
skipped.

Verify the complete matching catalog before computing counts, time ranges, ordering, or
applying `limit`. Damage outside `limit=1` still returns 409 with no partial envelope.

Holdings does not inspect PostgreSQL, Recipe selection, provider Recipes, Outcomes,
Observation envelopes, typed fact tables, or result-context tables.

## Empty and error semantics

A successful empty response returns exactly:

- `holdings: []`;
- `total_matching: 0`;
- `returned_count: 0`;
- applied `limit`;
- echoed `order`;
- `has_more: false`;
- the route provider and adapter.

It means only:

> After a successful store-wide Evidence verification, no verified Attempt Evidence is
> held for this route's exact provider/adapter.

It does not mean provider-zero, unimportant, never worth measuring, no data under another
surface, no admitted facts, or no provider corpus results.

Empty 200 also remains valid when:

- the store contains only successfully verified foreign adapters;
- no Recipe is selected or registered;
- Outcome, envelope, fact, or result-context rows are missing or stale;
- PostgreSQL is unconfigured or unavailable.

HTTP behavior:

- invalid `limit`/`order`: FastAPI 422;
- no configured Evidence Store: existing service-configuration 503;
- verified empty catalog: 200;
- Evidence or lifecycle integrity disagreement: 409
  `{"detail":"evidence_integrity_failure"}`.

Do not accept a Recipe pin, call Recipe selection, or catch
`ProviderRecipeSelectionError`. PostgreSQL/Recipe-only damage is irrelevant to Holdings.

Every 409 returns no `holdings`, `total_matching`, `returned_count`, or `has_more` key.

## PostgreSQL independence

The three Holdings routes must not call `_require_dsn`, open a PostgreSQL connection, or
begin a transaction. They must return their Evidence-derived 200/409 result when
`Settings.database_url` is unset or PostgreSQL is unavailable.

This deliberate difference from history and Outcomes is part of the Evidence-only Product
lock. It does not grant consumers direct Evidence access.

## Honest limits

- Holdings has no subject or scope filter. It discovers only the first bounded catalog slice
  in exact catalog order, with an unavailable tail beyond 100.
- History and Outcomes still accept only `requested_keyword`, not the complete Holdings
  request scope. Following a Holdings subject into either route may return multiple scopes
  mixed in one bounded response. Outcomes exposes each Attempt's request testimony, but
  API-03 does not add exact-scope follow-up or guarantee that a particular scope is inside
  the returned Outcomes tail.
- Holdings exposes no event identifiers or direct jump link to one grouped series. This is
  the accepted bounded-inventory trade-off, not evidence that the group lacks events.
- Store-wide verify-first discovery couples every Holdings route to unrelated damaged
  committed Evidence until the later rebuildable subject index exists.
- Counts and first/last times summarize preserved Evidence only. They do not prove a
  monitoring program, regular cadence, freshness requirement, current status, or future
  acquisition intent.

## Typed OpenAPI and inference traps

All three routes require closed, surface-specific response models and substantive OpenAPI
descriptions. Assert descriptions, not merely model names or route existence.

The contract must state:

- Holdings is an Evidence-backed subject/scope catalog, not admitted history or Outcomes;
- one item is one exact subject-plus-request group, not one Attempt, Capture, Observation,
  provider item, or desired measurement;
- multiple Captures prove multiple historical measurements, not a monitoring program;
- `unresolved_count` is not definitely unsent or current status;
- empty is not provider-zero, failure, unimportance, or an unselected Recipe;
- counts and time ranges are Evidence inventory, not strategy, cadence, ranks, mentions,
  volume, or corpus size;
- the same subject under one request scope says nothing about other locations, languages,
  devices, depths, platforms, match types, scopes, offsets, limits, or enrichment flags;
- Keyword Overview's member expansion does not multiply exchanges;
- Search Mentions request `limit`/`offset` are not Holdings pagination and its provider token
  is not followed;
- the catalog is bounded and a tail beyond 100 is disclosed but unavailable.

Avoid contract names implying false semantics, including `current_*`, `latest_*`, `status`,
`classification`, `measurement_count`, `observation_count`, `admitted_count`, `coverage`,
`total_count`, `items_count`, `last_measured_at`, `monitoring`, `panel`, `score`, or Recipe
fields.

## Shared versus surface-local implementation boundary

New shared `provider_holdings.py` may own:

- explicit closed Holdings request/item/envelope Pydantic models;
- list limit/order constants and envelope math;
- common immutable grouping/count/time structures;
- Holdings-wide parent provider/adapter relationship verification over already verified
  store events;
- common closed-item/envelope assembly from surface-verified inputs.

It may reuse `load_verified_store_events` from API-02. It must not know provider fact-table
names, perform PostgreSQL work, select Recipes, extract surface subjects, follow provider
continuation, or become a generic provider loader.

The three readers retain:

- exact route provider/adapter filtering;
- closed Attempt parameter extraction;
- surface-local request mapping and validation;
- Keyword Overview member expansion;
- group-key construction and catalog sorting;
- surface-specific item/envelope assembly where typing requires it.

Do not refactor history or Outcomes loaders merely to remove repeated outer shells.

## Changed-path allowlist

Production:

- `src/observatory/provider_holdings.py` — new shared explicit typing, math, grouping support,
  and Holdings relationship validation;
- `src/observatory/keyword_overview_read.py`;
- `src/observatory/google_organic_read.py`;
- `src/observatory/search_mentions_read.py`;
- `src/observatory/api.py`.

Tests:

- `tests/test_provider_holdings.py` — new helper/model invariants only; never a substitute
  for route proofs;
- `tests/test_api_keyword_overview.py`;
- `tests/test_api_google_organic.py`;
- `tests/test_api_search_mentions.py`.

Ticket:

- `tickets/API-03-provider-holdings-discovery.md` — [GROK] may update only his assigned
  status/start/report fields during implementation and must leave status `review`, never
  `done`.

No other path is authorized. Stop and report before changing another file.

In particular, do not modify schema/migrations, `provider_outcomes.py`, Recipe selection or
registration, Derivation, parsers, provider transports, history/Outcomes behavior, Attempt
audit, Evidence format, authority docs, or the roadmap during implementation.

## Required adversarial HTTP proofs

Helper tests may supplement but never replace independent assertions on all three routes.
Consolidation is allowed only when the test still drives each route.

1. Empty store returns exact typed 200 envelope with zero totals and no Recipe/DSN
   requirement.
2. All-classification presence is discoverable from Evidence: admitted, non-admitted
   Capture, and Attempt-without-Capture subjects all appear without reading Outcomes.
3. Same exact subject and scope across multiple Attempts groups once with exact attempt,
   capture, unresolved counts and first/last time ranges.
4. Same subject with any different surface scope field produces separate Holdings items.
5. Keyword Overview 1..5 members produce 1..5 items sharing the full ordered bundle and
   factual shared inventory; they do not appear as 1..5 exchanges.
6. Different Keyword Overview sibling bundles do not merge for a shared member.
7. Exact nested-array catalog ordering for KO keywords and Search Mentions search scope;
   asc and desc reverse the complete group key before limiting.
8. `limit=1` exposes correct `total_matching`, `returned_count`, and `has_more`; an omitted
   tail beyond 100 remains unavailable.
9. Unselected/missing/drifted Recipe, missing Outcome rows, and unavailable PostgreSQL do
   not change an otherwise valid Holdings 200.
10. Damaged committed foreign-adapter Attempt and Capture Evidence returns 409 even when
    the route adapter's own Evidence is valid.
11. Duplicate committed Attempt or Capture identity returns 409.
12. Two verified Captures for one Attempt returns 409.
13. Capture parent missing, or Capture provider/adapter disagreeing with its verified parent,
    returns 409 before adapter filtering.
14. Every surface independently 409s malformed/drifted route-adapter Attempt parameters,
    including missing subject arrays/objects and scope fields.
15. Matching or foreign Evidence damage outside `limit=1` returns 409 with no partial keys.
16. Missing required Attempt/Capture timestamp testimony fails closed. Valid groups with no
    Capture use null request-time boundaries.
17. No response exposes Attempt/Capture ID lists, request fingerprint, Recipe/Outcome/fact
    fields, provider result counts, or strategy/cadence state.
18. Search Mentions never reads/follows `search_after_token`; request `limit`/`offset` remain
    typed Attempt testimony.
19. OpenAPI asserts the exact route, query, closed envelope/item/request schemas, KO
    non-explosion meaning, counts/times, empty semantics, catalog completeness, and strategy
    inference traps.
20. A Holdings GET does not mutate Evidence, PostgreSQL, Recipe selection, acquisition, or
    provider state.

For every new 409 proof, assert absence of `holdings`, `total_matching`, `returned_count`,
and `has_more`.

## Testing workflow

During implementation [GROK] runs only:

    uv run pytest -q \
      tests/test_provider_holdings.py \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

Then:

    uv run ruff check .
    uv run mypy

Do not run the full suite during implementation. After committed implementation and any
bounded remediation settle, [GPT] independently reviews through LinuxVedaOpsMCP and gives
[CHAZ] one exact-HEAD operator block. [CHAZ] runs the targeted suite, full suite once, Ruff,
mypy, and initial/final HEAD/tree checks.

No provider call, credentials, spend, live Evidence activity, continuation, or F12/F13 work
is part of testing.

## Explicit exclusions and deferred work

API-03 does not authorize:

- PostgreSQL schema or a measurement-subject index;
- F12 recurring/coordinated acquisition or intended subject sets;
- F13-triggering provider-gate reuse or live activity;
- AI-12 Target Metrics Recipe/read/history/Holdings work;
- outer pagination, cursor, offset, or limits above 100;
- a cross-provider, cross-surface, generic Holdings route or universal subject model;
- subject/prefix/scope filtering;
- Outcome/history scope-filter remediation;
- Attempt-audit count hardening;
- Recipe changes, selection, registration, or identity checks;
- Observation facts, provider response bodies, diagnostics, corpus counts, or tokens;
- Search Mentions continuation;
- Organic `related_result` resolution;
- strategy, recommendations, scoring, importance, desired panels, monitoring state, or
  cadence.

The future rebuildable subject index must derive from verified Evidence and must not become
new authority or invented coverage. Its exact schema remains a separate pre-F12 boundary.

## Mandatory pre-implementation ticket review

[GROK] must review this provisional ticket read-only against its exact clean commit before
any implementation authorization. The review must inspect current code, tests, schema,
Evidence Store, API-01/API-02, D14, and the three surface Attempt contracts.

Return:

- `APPROVE` or `REQUIRES TICKET CORRECTION`;
- false premises, missing proofs, overconstraints, and implementation traps;
- whether the exact nine-key item and eight-key envelope are truthful;
- grouping/order edge cases and KO non-explosion risks;
- whether PostgreSQL independence is completely enforced;
- whether shared-vs-surface ownership is implementable without a generic loader;
- any possible false green in the required HTTP vectors;
- any path genuinely required outside the allowlist;
- candid architecture, consumer-readiness, strategy-inference, and data-model consequences;
- exact HEAD/branch/tree and no-change confirmation.

Do not implement, edit the ticket, run tests, commit, push, or perform provider/Evidence
activity during that review.

## Implementation report requirements

If [CHAZ] later authorizes implementation, [GROK]'s committed report must include:

- exact start and implementation commits, branch, clean tree, changed paths, and no push;
- exact routes, envelope/item models, grouping keys, and OpenAPI behavior;
- Evidence walk and global parent/provider/adapter verification behavior;
- targeted tests, Ruff, and mypy results; full suite not run;
- strongest and weakest aspects;
- possible false greens;
- remaining caller-controlled influence;
- architecture drift or coupling;
- parser/provider traps;
- closure blockers and deferred work;
- what later index work should reuse and what stays surface-local;
- Evidence versus claimed contract versus synthetic proof;
- useful and unsafe strategy-layer implications;
- data-model implications and unsafe inferences;
- confirmation of zero provider calls, credentials, spend, continuation, live Evidence
  mutation, F12/F13 activity, amend, or push.

Status must remain `review`, never `done`. Only [GPT] closes the ticket after [CHAZ]
explicitly authorizes closure.
