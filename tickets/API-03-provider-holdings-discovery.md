# API-03 — Provider Holdings discovery

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** [GPT] Steward review of committed implementation  
**Question-resolution pass:** completed against `ed5bf39923f3872ff9ecc96962d58a89847e0bee`  
**Pre-implementation review:** completed read-only against `5cbef17f4daf042efc2798998df765f3a698e70e`  
**Product lock:** [CHAZ] approved subject-plus-exact-scope / Evidence-only / catalog-order Holdings  
**Start commit:** `762f50a33f640471e76665854a996ba99949bccb`

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

API-03 is not implementation authority. [GROK]'s mandatory read-only ticket review is
complete, and [GPT] has reconciled it into this final accepted boundary. [CHAZ] must
separately authorize implementation against the named exact clean start commit.

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

## Pre-implementation review reconciliation

[GROK] returned `REQUIRES TICKET CORRECTION` after the mandatory read-only review of
`5cbef17f4daf042efc2798998df765f3a698e70e`. [GPT] independently verified and accepts
three corrections:

1. `EvidenceStore.read_capture()` already loads the committed parent Attempt and validates
   full Capture/Attempt agreement, including provider and adapter, before returning. Because
   API-02's store-wide walk calls `read_capture()` for every committed Capture, no new
   Holdings-local relationship validator is required.
2. After exact route-adapter match, the verified Attempt provider must equal the route
   provider. A wrong-provider Attempt using the route adapter is integrity failure, not a
   foreign event to skip.
3. PostgreSQL-independence proofs must actually exercise both an unset DSN and an unreachable
   DSN, rather than merely omitting database calls in a normally configured test app.

[GPT] adds one consumer-safety correction from the review's query observation: because the
route accepts only `limit` and `order`, any other query key—including a Recipe pin—must be
HTTP 422. Silently ignoring `derivation_version_id`, `requested_keyword`, `offset`, or a
cursor could falsely imply that a caller-supplied scope was applied.

No Product direction, route, grain, schema, or changed-path expansion follows from these
corrections.

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

The query contract is closed. Any query key other than `limit` or `order` returns FastAPI
HTTP 422; it must not be silently ignored. In particular, a supplied Recipe pin must never
produce a 200 that could be mistaken for Recipe-scoped Holdings.

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

The reused walk already verifies, across every committed Capture before adapter filtering:

- committed identity, bundle, body, and parent existence;
- duplicate identity and at-most-one-Capture lifecycle;
- Capture/parent Attempt ID, request, request fingerprint, provider, and adapter agreement.

This occurs because `EvidenceStore.read_capture()` validates the Capture against its loaded
parent Attempt. Do not add a redundant Holdings-local relationship validator, copy the walk,
or modify `provider_outcomes.py`. The required HTTP parent/provider/adapter plants must prove
the existing store-wide failure path through each Holdings route.

Only after complete store-wide verification may successfully verified foreign adapters be
excluded. Filtering is adapter-first: when an Attempt adapter does not match the route
adapter, exclude it after verification. When the adapter does match, its provider must equal
the route provider; disagreement is HTTP 409, not a foreign event to skip. For the exact
route provider/adapter, extract and validate every Attempt's
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
- any unrecognized query key: FastAPI 422;
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
- common post-condition assertions over surface-grouped verified inputs;
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
  post-condition checks, and envelope assembly;
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

1. Empty store with `database_url=None` and no selected Recipe returns the exact typed 200
   envelope with zero totals.
2. The closed query contract rejects `requested_keyword`, `derivation_version_id`, offset,
   cursor, and any other undeclared query key with HTTP 422; none is silently ignored or
   mapped to Recipe 404/503 behavior.
3. Evidence lifecycle presence is discoverable without PostgreSQL classification: subjects
   represented by an Attempt without Capture, an admitted-fixture Capture, and a
   non-admitted-fixture Capture all appear while Outcome rows are absent or irrelevant.
4. Same exact subject and scope across multiple Attempts groups once with exact attempt,
   capture, unresolved counts and first/last time ranges.
5. Same subject with any different surface scope field produces separate Holdings items.
6. Keyword Overview 1..5 members produce 1..5 items sharing the full ordered bundle and
   factual shared inventory; they do not appear as 1..5 exchanges.
7. Different Keyword Overview sibling bundles do not merge for a shared member.
8. Exact nested-array catalog ordering for KO keywords and Search Mentions search scope;
   asc and desc reverse the complete group key before limiting.
9. `limit=1` over at least two items exposes correct `total_matching`, `returned_count`, and
   `has_more`; a separate catalog with more than 100 groups proves the disclosed but
   unavailable tail beyond the maximum limit.
10. An unselected/missing/drifted Recipe, missing Outcome rows, `database_url=None`, and an
    unreachable DSN do not change an otherwise valid Evidence-derived Holdings 200.
11. Damaged committed foreign-adapter Attempt and Capture Evidence returns 409 even when
    the route adapter's own Evidence is valid.
12. A verified Attempt whose adapter equals the route adapter but whose provider is not the
    route provider returns 409; it is not skipped as foreign Evidence.
13. Duplicate committed Attempt or Capture identity returns 409.
14. Two verified Captures for one Attempt returns 409.
15. Capture parent missing, or Capture provider/adapter disagreeing with its verified parent,
    returns 409 before adapter filtering.
16. Every surface independently 409s malformed/drifted route-adapter Attempt parameters,
    including missing keyword/target structures, nested arrays, flags, and scope fields.
17. Matching or foreign Evidence damage outside `limit=1` returns 409 with no partial keys.
18. Missing required Attempt/Capture timestamp testimony fails closed through verified
    Evidence read. Valid groups with no
    Capture use null request-time boundaries.
19. No response exposes Attempt/Capture ID lists, request fingerprint, Recipe/Outcome/fact
    fields, provider result counts, or strategy/cadence state.
20. Search Mentions never reads/follows `search_after_token`; request `limit`/`offset` remain
    typed Attempt testimony.
21. OpenAPI asserts the exact route, closed query, envelope/item/request schemas, KO
    non-explosion meaning, counts/times, empty semantics, catalog completeness, and strategy
    inference traps.
22. A Holdings GET does not mutate Evidence, PostgreSQL, Recipe selection, acquisition, or
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

## Pre-implementation ticket review

[GROK] completed the mandatory read-only adversarial review against exact clean commit
`5cbef17f4daf042efc2798998df765f3a698e70e` and returned
`REQUIRES TICKET CORRECTION`. The review found no Product or D14 contradiction and confirmed
that B/A/A, the eight-key envelope, nine-key item, grouping/count/time contract, PostgreSQL
independence, changed-path allowlist, and deferred boundaries are implementable.

The false walk-gap premise, missing route-adapter/wrong-provider 409, and incomplete DSN
proofs are reconciled above. [GPT]'s closed-query correction prevents silently ignored scope.
No implementation, edits, tests, commit, push, provider call, credentials, Evidence or
PostgreSQL mutation, continuation, or F12/F13/AI-12 activity occurred during the review.

This reconciled ticket is the final accepted work boundary. A new ticket review is required
only if the boundary changes substantively before [CHAZ] authorizes implementation.

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

## Implementation report

**Start commit:** `762f50a33f640471e76665854a996ba99949bccb`  
**This commit** is the API-03 implementation child. Status `review`, never `done`.

### Changed paths

Production:

- `src/observatory/provider_holdings.py` (new)
- `src/observatory/keyword_overview_read.py`
- `src/observatory/google_organic_read.py`
- `src/observatory/search_mentions_read.py`
- `src/observatory/api.py`

Tests:

- `tests/test_provider_holdings.py` (new, helper invariants only)
- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`

Ticket: this file.

### Routes and contracts

Added:

- `GET /v1/providers/dataforseo/google/keyword-overview/holdings`
- `GET /v1/providers/dataforseo/google/organic/holdings`
- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/holdings`

Eight-key envelope: `provider`, `adapter_contract`, `total_matching`, `returned_count`,
`limit`, `order`, `has_more`, `holdings`. Nine-key item including surface `request`.
Closed query: only `limit` and `order`; any other key is HTTP 422.

### Grouping, counts, order, KO expansion

Grouping identity is `(requested_keyword, exact request tuple)`. Duplicate group
identities fail closed. Catalog sort is that complete tuple; descending reverses it in
the three readers, then slices. No `min_attempt_id`.

Counts and first/last times come from verified Attempt/Capture Evidence.
`attempt_count == capture_count + unresolved_count`. Request times are null iff
`capture_count == 0`.

Keyword Overview: N keywords → N items sharing the full `keywords` bundle and the same
inventory counts/timestamps.

### Integrity and independence

Reuse `load_verified_store_events`. No copied walk. No Holdings-local parent validator.
`read_capture()` still fail-closes parent missing/disagreement before adapter filter.
After adapter match, wrong route provider is 409, not skip.

Routes do not call `_require_dsn`, Recipe selection, or PostgreSQL. Empty/valid 200 with
`database_url=None` and an unreachable DSN.

### Verification

Targeted:

    uv run pytest -q \
      tests/test_provider_holdings.py \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

Result: **81 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy           # Success: no issues found in 68 source files

Full suite was **not** run.

### Strongest

Evidence-only discovery that history/Outcomes cannot answer. Closed 422 query prevents a
silent Recipe pin. Store-wide verify-first plus adapter-then-provider 409 matches D14
fail-closed without touching Outcomes.

### Weakest

The three loaders still copy filter/group/sort/slice. Closed HTTP-v2 probes freeze most
scope fields, so some same-subject/different-scope and SM `search_scope` order proofs use
post-verify Attempt overrides rather than schema-valid committed bytes.

### Possible false greens

Helper math tests do not replace route 409s. Override stores prove extraction/provider
branches, not that those states exist in committed HTTP-v2 Evidence. XOR Capture plants
fail `read_capture` generally. 101-group tail is proven on KO and Organic.

### Caller-controlled influence

`limit` 1–100 and `order` only.

### Architecture

`HISTORY_LIMIT_*` reused for query bounds. Shared module has no fact-table names and does
no PostgreSQL/Recipe work. Readers own extraction, KO expansion, group keys, and sort.
`provider_outcomes.py` unchanged.

### Parser/provider traps

Exact strings; no normalization. SM `request.limit`/`offset` are Attempt fields.
`search_after_token` is not read. KO expansion is not N exchanges.

### Closure blockers

Full suite not run. Steward independent review of this commit is required.

### Deferred

Holdings index, pagination past 100, Outcomes/history scope filters, AI-12, F12/F13,
Organic `related_result`.

### Reuse later

Store-wide verify-or-409 walk, subject-plus-request grouping identity, 409-no-partial
payload, closed query, Evidence-only empty meaning.

### Remain surface-local

Subject paths, request field sets, KO member explosion, catalog field order.

### Evidence vs contract vs synthetic

Evidence is Attempt/Capture bytes. Holdings is a rebuildable projection. Tests include
synthetic unresolved/no_response plants and post-verify overrides.

### Strategy-LLM

Useful: surface S holds subject X at exact scope Y, including unresolved/failed presence.
Unsafe: empty as provider-zero or unselected Recipe; KO N items as N exchanges;
`last_authorized_at` as cadence; same subject as other-scope coverage; unresolved as unsent.

### Data-model

No `outcomes` subject column. No invented coverage rows. Do not treat
`request_fingerprint` as Holdings identity. Later index must derive from Evidence.

### Hygiene

One implementation commit, no amend, no push. Zero provider calls, credentials, spend,
continuation, live Evidence mutation, or F12/F13 activity. Working tree left clean after
the commit.

## Steward implementation review — remediation required

Reviewed implementation commit:
`f7b0863782c1139bcb341fbd7b2513c2fb01e53d`

Verdict: **REMEDIATION REQUIRED**.

The production data path is directionally correct and the Product boundary remains
locked. The three routes are Evidence-only, do not consult PostgreSQL or Recipe state,
verify the store before filtering, preserve surface-local scope identity, expand one
Keyword Overview Attempt by exact member keyword, sort the full catalog before limiting,
and expose no strategy, cadence, recommendation, score, or continuation state.

The remaining work is proof and typed-contract hardening. It does not authorize a reader
or API redesign, a schema or migration, a holdings index, Recipe work, provider activity,
history/Outcomes changes, or any deferred boundary.

### R1 — make count and time invariants visible in the typed contract

In `src/observatory/provider_holdings.py`, constrain and describe the existing
semantics rather than changing them:

- `attempt_count >= 1`;
- `capture_count >= 0`, `unresolved_count >= 0`,
  `total_matching >= 0`, and `returned_count >= 0`;
- applied `limit` remains 1–100;
- `attempt_count == capture_count + unresolved_count`;
- `first_authorized_at` and `last_authorized_at` are respectively the minimum and
  maximum verified Attempt authorization times in the exact group;
- `first_request_started_at` and `last_request_started_at` are respectively the
  minimum and maximum verified Capture request-start times in the exact group, and both
  are null exactly when `capture_count == 0`;
- `attempt_count` and `capture_count` describe Evidence Attempt/Capture cardinality,
  not provider fact, rank, mention, result, or observation counts.

These are schema-visible bounds and descriptions for already-enforced behavior. Do not
add inferred state or a new resource field.

### R2 — eliminate OpenAPI and query-contract false greens

For each Holdings route:

- assert the declared query-parameter names are exactly `{"limit", "order"}`, not a
  subset check that can pass when a parameter disappears;
- resolve that route's response-schema reference and inspect only its Holdings envelope,
  item, and surface request schemas; do not search the stringified whole OpenAPI document,
  where unrelated history or Outcomes prose can satisfy a Holdings assertion;
- prove the exact eight outer keys and exact nine item keys;
- prove the R1 numeric bounds and semantic descriptions, surface-specific request shape,
  Keyword Overview non-explosion wording, empty/limit/`has_more` meaning, unresolved
  meaning, Search Mentions request `limit`/`offset` and token warnings, and the
  prohibition on strategy/cadence/recommendation state against the relevant schema;
- prove invalid `order` and out-of-range `limit` fail with HTTP 422.

Tests may consolidate repeated schema traversal, but each route must be tied to its own
response schema.

### R3 — prove the named Evidence integrity failures specifically

The existing XOR-damaged Capture tests prove generic byte-integrity rejection, not the
ticket's Capture-to-parent agreement requirement. Add bounded HTTP proofs that:

- a damaged foreign-adapter Capture anywhere in the same Evidence root makes each
  Holdings surface fail HTTP 409 with no partial Holdings envelope;
- a schema/JCS/digest-valid committed Capture that disagrees with its cited parent
  Attempt is rejected specifically by the parent-agreement check, including the
  provider/adapter relationship required by the ticket;
- the test establishes the direct store-read failure cause before asserting the route's
  exact HTTP 409 and absence of Holdings envelope keys.

Use valid Evidence construction and the public Evidence Store behavior. Do not weaken
validation or add a Holdings-only substitute for Evidence verification. Consolidation is
allowed when one planted store-wide defect is exercised through all three routes.

### R4 — prove Search Mentions token non-use with token-bearing Evidence

Use a committed, valid Search Mentions Capture whose provider response actually contains
`search_after_token`. Through the Holdings route prove that the token is not returned or
followed, no continuation or provider transport occurs, no new Evidence is created, and
PostgreSQL remains irrelevant. An Attempt-only/no-response plant without a token does not
prove this requirement.

### R5 — complete surface-scope fail-closed proofs

Keep subject and request extraction surface-local. Add or consolidate HTTP 409 proofs for
malformed or missing scope fields that materially define grouping, including Organic
scope fields and Search Mentions `search_scope` as well as the subject field. Empty
keyword/target coverage alone is insufficient.

### Remediation boundary

Allowed paths:

- `src/observatory/provider_holdings.py`
- `tests/test_provider_holdings.py`
- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`
- `tickets/API-03-provider-holdings-discovery.md`

`src/observatory/api.py`, all three readers, provider Outcomes/history code, migrations,
Recipe code, provider code, and unrelated authority are outside this remediation. If a
direct production defect makes an outside path necessary, stop and report it rather than
expanding the patch.

Run the API-03 targeted suite plus Ruff and mypy. Do not run the full suite; reserve that
for CHAZ's exact-HEAD operator gate after Steward review settles. Commit one remediation
commit without amend or push, keep the ticket at `review`, and append an implementation
report addendum with the exact start/implementation commits, changed paths, verification,
and candid assessment required by this ticket.

## Remediation report addendum

**Remediation start commit:** `6dc18360147f11e870d307acef087d7248c967bc`  
**This commit** is the API-03 R1–R5 remediation child. Status `review`, never `done`.

### Changed paths

- `src/observatory/provider_holdings.py`
- `tests/test_provider_holdings.py`
- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`
- `tickets/API-03-provider-holdings-discovery.md`

No `api.py`, reader, Outcomes, history, schema, Recipe, or roadmap changes.

### R1–R5 behavior

R1: typed `ge`/`le` bounds, count equality validator, and min/max/null-when-zero time
descriptions on the existing Holdings models. No new fields.

R2: each route asserts query names `== {"limit", "order"}`, resolves its own 200 schema,
checks eight envelope keys, nine item keys, R1 minima, and surface request shape. Invalid
`order` and `limit` 0/101 are HTTP 422. Assertions use the route schema, not the whole
OpenAPI dump.

R3: XOR-damaged foreign-adapter Capture is store-read `IntegrityError` then 409 on all
three Holdings routes. A schema/JCS/digest-valid Capture retargeted onto a different
parent Attempt fails `read_capture` with `does not agree with its parent Attempt`, then
the same 409 with no envelope keys.

R4: committed Search Mentions Capture from the token-bearing AI-03 fixture. Holdings
response omits `search_after_token`; `recorded_ops` unchanged; no PostgreSQL.

R5: Organic missing `depth`/`device`/`os`/flags/location/language and Search Mentions
missing `search_scope` return HTTP 409.

### Verification

Targeted suite **92 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy           # Success: no issues found in 68 source files

Full suite was **not** run.

### Strongest

Parent-agreement is proven on the public `read_capture` path, not XOR. OpenAPI proofs
bind each Holdings route's own schema.

### Weakest

R5 still uses post-verify Attempt overrides because closed HTTP-v2 probes freeze those
fields. R3 parent plant writes a new Capture bundle on disk (commit_capture would
refuse); identity is still content-addressed and verified by `read_capture`.

### Possible false greens

OpenAPI substring checks can still pass if descriptions later move to a nested `$ref`
the helper does not follow. Override-store R5 plants are not committed drifted bytes.
Token proof checks the JSON key, not that Holdings parsed the body.

### Caller-controlled influence

Unchanged: `limit` and `order` only.

### Architecture

No reader/API redesign. Shared OpenAPI helpers remain triplicated in the three route
suites so each route binds its own schema.

### Parser/provider traps

None new. SM token remains result-context testimony, not a Holdings field.

### Closure blockers

Full suite not run. Steward review of this remediation commit is required.

### Deferred

Unchanged: holdings index, pagination past 100, Outcomes/history scope filters, AI-12,
F12/F13, Organic `related_result`.

### Reuse later

Typed count/time bounds, per-route OpenAPI binding, parent-agreement plant via
`validate_capture` plus content digest.

### Remain surface-local

Subject extraction and grouping keys stay in the three readers (untouched).

### Evidence vs contract vs synthetic

R3/R4 use committed Evidence plus one retargeted Capture bundle. R5 is a synthetic
post-verify parameter drop.

### Strategy-LLM

Unchanged: Holdings is inventory, not cadence, recommendation, or monitoring.

### Data-model

No schema change. Do not treat the retargeted Capture plant as a legal Capture write
path.

### Hygiene

One remediation commit, no amend, no push. Zero provider calls, credentials, spend,
continuation, live Evidence mutation, or F12/F13. Working tree left clean after the
commit.

## Steward remediation review — final proof correction required

Reviewed remediation commit:
`e1a3ae6297edee5a39841e2182472ef7a3c90726`

Verdict: **PRODUCTION ACCEPTED; FINAL TEST CORRECTION REQUIRED**.

R1 production typing and descriptions are correct. R3's store-wide foreign-Capture and
public parent-agreement paths, R4's token-bearing Evidence proof, and R5's surface-scope
fail-closed proofs satisfy their bounded remediation requirements. No reader, API,
Evidence Store, schema, Recipe, provider, or strategy-layer change is authorized.

One R2 false green remains. The three route helpers assert only that each schema's
`required` list equals the expected key set. A new optional envelope, item, or request
property could therefore enter the advertised OpenAPI contract while those “exact key”
assertions remain green.

For each Holdings route, update its existing OpenAPI proof to:

- assert `set(schema["properties"])` exactly equals the accepted envelope, item, and
  surface request key sets, in addition to exact `required`;
- assert the envelope, item, and request schemas are closed
  (`additionalProperties is false`);
- assert the applied-limit description distinguishes the Holdings limit from provider
  page size;
- assert both first and last request-start descriptions state their respective
  minimum/maximum meaning and null relationship to `capture_count`;
- assert the relevant Holdings schemas prohibit strategy, cadence, and recommendation
  state, not merely any one of those terms.

This is a tests-and-ticket-only correction. Allowed paths:

- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`
- `tickets/API-03-provider-holdings-discovery.md`

Do not modify production code. Run the same API-03 targeted suite, Ruff, and mypy; do not
run the full suite. Commit one child without amend or push, leave status `review`, and
append a concise report addendum. If the existing production OpenAPI does not satisfy
these assertions, stop and report rather than changing production under this boundary.
