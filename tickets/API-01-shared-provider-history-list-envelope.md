# API-01 — Shared provider-history list envelope

**Status:** provisional — GROK review reconciled; implementation authorization pending  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** explicit CHAZ implementation authorization and an exact clean start commit  
**Approved by:** [CHAZ] for ticket-review correction publication only  
**Pre-implementation review:** completed read-only against `fa8cc3cc7bfc0042a192479af8a6decaa054ecda`  
**Implementation start:** not authorized

## Purpose

Make the existing Keyword Overview, Google Organic, and Search Mentions history routes
truthfully disclose the cardinality and truncation of their outer admitted-Capture lists.

This is one shared consumer-contract correction after the three surface reviews accepted
under D14. It adds outer list metadata and a typed OpenAPI boundary without changing any
surface's fact body, candidate membership, Derivation Recipe, Observation identity,
admitted-empty semantics, or provider acquisition behavior.

API-01 is not implementation authority. CHAZ must separately authorize implementation, and
the implementation prompt must name this reconciled ticket's exact clean start commit and
retain all changed-path, testing, zero-provider, and no-push boundaries.

## Pre-implementation review reconciliation

GROK completed the mandatory code-first review of the provisional ticket read-only against
`fa8cc3cc7bfc0042a192479af8a6decaa054ecda`. The review found no false premise, authority
contradiction, unresolved Product question, or need to redesign the accepted D14 boundary.

The review confirmed that all three readers already load and verify the full matching candidate
series before sorting and limiting. It also confirmed the surface-specific membership,
admitted-empty, Recipe, ordering, and count-grain claims in this ticket.

This reconciliation accepts five corrections: semantic rather than byte-for-byte Capture
equivalence; complete omission of all envelope keys on HTTP 409; explicit outer-versus-inner
count-grain tests; uncoerced nested Capture mappings under the typed outer model; and
substantive OpenAPI-description assertions. A small shared-helper unit test is permitted only
as additional evidence and never as a substitute for the three independent route suites.

## Authority and accepted direction

- VISION — every consumer, including the future strategy LLM, uses only the versioned API;
  API reads disclose truncation, omissions, freshness, and known blind spots.
- D2 and D3 — API-only consumers; strategy and recommendations remain outside Observatory.
- D8 — verified Evidence remains authoritative and reads fail closed.
- D11 — provider/surface identity, provenance, Recipe, and time axes remain explicit.
- D14 — accepted shared history, Outcomes, and holdings separation after Keyword Overview,
  Google Organic, and Search Mentions consumer reviews.
- PF-08 — Keyword Overview recipe-aware history and verify-before-limit precedent.
- PF-13 — Google Organic history, admitted-empty context, and whole-Capture projection.
- PF-14 — matching damage outside the returned limit must fail closed.
- AI-06 — Search Mentions history, result-context truncation testimony, and occurrence
  integrity.
- The 2026-08-24 D14 shared history-envelope question-resolution lock.

The future shared resource sequence remains:

1. outer admitted-history list envelope;
2. separate Measurement Outcomes;
3. separate holdings/inventory.

API-01 implements only item 1.

## Existing routes

Apply the same outer envelope behavior to exactly:

- `GET /v1/providers/dataforseo/google/keyword-overview/history`
- `GET /v1/providers/dataforseo/google/organic/history`
- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/history`

Each route retains its existing query contract:

- required `requested_keyword`;
- optional `derivation_version_id`;
- `limit`: default 20, minimum 1, maximum 100;
- `order`: `asc` or `desc`, default `asc`.

No new route, version, outer cursor, offset, or pagination token is authorized.

## Exact outer response boundary

The change is additive on the existing `/v1` routes.

Retain the current top-level fields:

- `provider`
- `adapter_contract`
- `requested_keyword`
- `derivation_version_id`
- `recipe_resolution`
- `observation_kinds`
- `captures`

Add exactly these top-level list fields:

- `total_matching`
- `returned_count`
- `limit`
- `order`
- `has_more`

Do not add a universal `scope` object. The existing provider, adapter, requested subject,
resolved Recipe, and Observation-kind fields disclose the list scope. Their OpenAPI
descriptions must state that the list grain is admitted, subject-bound Capture history under
one resolved Recipe.

The three routes keep different Capture-group/fact-body mappings. API-01 must not introduce a
universal fact body or force their nested keys into one schema.
The typed outer boundary must preserve each nested Capture mapping semantically. Response
validation must not strip, coerce, normalize, or reject surface-specific nested keys or values.
Closure of the 12 outer keys does not close or universalize the nested Capture mappings.

## Field semantics

### `total_matching`

`total_matching` is the number of unique matching admitted Capture documents for:

- the exact route/provider/adapter;
- the requested keyword;
- the resolved or explicitly pinned Recipe;
- the surface's accepted history-membership predicate.

It is computed after every matching candidate passes:

- verify-on-read Attempt and Capture Evidence checks;
- exact provider/adapter/parent/request agreement;
- the surface's complete PostgreSQL consistency checks.

It is computed before sort/limit projection.

Do not count:

- Observation envelopes;
- typed fact rows;
- monthly points;
- ranked items;
- source occurrences;
- provider `total_count`, `items_count`, result counts, or inner pages;
- SQL join multiplicity;
- Attempt-stage activity outside admitted history.

A matching integrity disagreement returns the existing HTTP 409
`evidence_integrity_failure` response. No history envelope or partial count is returned.

### `returned_count`

`returned_count` equals the number of whole Capture documents in `captures`.

It must equal `len(captures)` and must never describe nested facts.

### `limit`

`limit` echoes the validated applied outer history limit supplied to the route.

The accepted maximum remains 100. Do not remove or increase the cap in API-01.

### `order`

`order` echoes the validated `asc` or `desc` query value.

All three readers retain their accepted deterministic ordering:

`(request_started_at, capture_id)`

Ascending uses that order. Descending reverses the complete order before limiting.

### `has_more`

`has_more` is true exactly when:

`total_matching > returned_count`

It discloses an omitted outer-history tail. It is not an authorization or capability to fetch
another page.

API-01 adds no outer offset/cursor. A caller may raise `limit` only to 100. If more than 100
matching admitted Captures exist, the remaining tail is known but unavailable until a later,
separately authorized outer-pagination ticket.

Do not:

- return an unbounded list;
- follow Search Mentions' inner `search_after_token`;
- reinterpret a provider offset/token as Observatory history continuation;
- add a second exchange or provider activity.

## Empty and failure semantics

A successful empty history response returns:

- `captures: []`
- `total_matching: 0`
- `returned_count: 0`
- the applied `limit`
- the requested `order`
- `has_more: false`

It means only:

> No matching admitted history exists under this route, requested keyword, and resolved
> Recipe.

It does not mean:

- never measured;
- measurement failed;
- provider returned zero;
- not ranking;
- not mentioned;
- no Outcome exists;
- no Attempt exists.

Keep existing error semantics:

- invalid query: FastAPI 422;
- unselected Recipe: 503 with the accepted stable signal;
- wrong/unavailable pin: 404;
- integrity disagreement: 409 with no history payload.

API-01 does not implement Outcomes or holdings.

## Surface-specific behavior that must remain unchanged

### Keyword Overview

- Candidate membership remains anchored by accepted Keyword Overview coverage/provenance.
- Do not manufacture `observation_admitted_empty` history.
- A multi-keyword Capture is still one Capture document when it matches the requested
  keyword.
- Capture-wide Outcome/envelope/detail checks remain distinct from one keyword's projected
  facts.

### Google Organic

- Valid subject-bearing `observation_admitted_empty` documents remain history members.
- Placement identity, result context, AIO/PAA occurrence checks, and Evidence-only prose
  remain unchanged.
- Non-null `related_result` remains the existing stop-before-derive trigger, not API-01
  scope.

### Search Mentions

- Valid subject-bearing `observation_admitted_empty` documents remain history members.
- Inner `total_count`, `items_count`, result offset, and opaque token remain
  surface-specific result context.
- `observation_count` remains Observation-envelope cardinality; it is not outer
  `returned_count` or provider `items_count`.
- Question/answer/source text, identities, occurrence arrays, and Google-null drift behavior
  remain unchanged.

## Verify-before-limit and transaction boundary

For each route:

1. resolve the Recipe exactly as today;
2. select the complete matching candidate set exactly as today;
3. verify every candidate's Evidence and surface-local PostgreSQL consistency exactly as
   today;
4. compute `total_matching` from the verified unique Capture set;
5. sort the complete verified set;
6. select at most `limit` whole Capture groups;
7. project the selected Capture groups;
8. compute and return the remaining envelope fields.

Do not weaken matching-damage-outside-limit behavior.

Keep the existing read-only connection/transaction discipline. API-01 does not authorize new
isolation claims, locks, concurrency control, or F7 work.

## Typed OpenAPI boundary

Each route must expose a typed response model sufficient for OpenAPI to describe:

- the existing scope/provenance fields;
- the five new list fields;
- `captures` as an array of surface-specific mapping objects.
- nested Capture mappings as pass-through values rather than one closed shared schema.

The metadata fields must have concise descriptions that distinguish:

- outer admitted Capture count from nested Observation/provider counts;
- `has_more` disclosure from pagination capability;
- empty admitted history from failed or never measured;
- deterministic outer ordering from provider item order.

API-01 does not require full typed models for each nested Capture fact body. That remains
surface-local later work. Do not claim the generic nested mappings are fully described merely
because the outer envelope is typed.

The typed response boundary must preserve the readers' nested mapping values without
normalization, key stripping, scalar coercion, or response-validation rejection. Tests must
exercise that pass-through boundary with representative surface-specific nested fields.

## Shared implementation boundary

A small shared module may own only:

- `HISTORY_LIMIT_DEFAULT`;
- `HISTORY_LIMIT_MAX`;
- shared outer response typing;
- exact outer metadata construction and invariant checks;
- deterministic `returned_count` / `has_more` math.

Proposed path:

- `src/observatory/provider_history.py`

The three readers retain surface-local ownership of:

- candidate SQL and membership;
- Evidence/request validation;
- Capture-wide PostgreSQL checks;
- admitted-empty behavior;
- sorting inputs;
- Capture-group projection;
- nested fact bodies.

Do not build a generic provider-history loader or abstract surface candidate tuples.

Remove the current architectural dependency in which `api.py` imports shared history limit
constants from `keyword_overview_read.py`; import them from the bounded shared module instead.

## Proposed changed-path allowlist

Production:

- `src/observatory/provider_history.py` — new, bounded shared metadata/types only
- `src/observatory/keyword_overview_read.py`
- `src/observatory/google_organic_read.py`
- `src/observatory/search_mentions_read.py`
- `src/observatory/api.py`

Tests:

- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`
- `tests/test_provider_history.py` — optional shared-helper invariant tests only; never a
  substitute for independent route tests

Ticket:

- `tickets/API-01-shared-provider-history-list-envelope.md`

No other path is authorized. If implementation reveals a necessary path outside this
allowlist, GROK must stop and return it to the Steward rather than expanding scope.

## Acceptance criteria

### Shared response shape

- [ ] All three routes retain the seven existing top-level keys and add exactly the five
      approved metadata keys.
- [ ] Existing Capture-group/fact-body mappings remain semantically equivalent for the same
      database/Evidence state; typed outer serialization does not change field presence,
      nesting, scalar values, arrays, or surface-specific meaning.
- [ ] Nested Capture mappings pass through without stripping, normalization, or coercion.
- [ ] Exact-key tests are updated intentionally; no unrelated response field changes.
- [ ] `returned_count == len(captures)`.
- [ ] `has_more == (total_matching > returned_count)`.
- [ ] `limit` and `order` echo the validated query.

### Counting and limiting

- [ ] Zero matching admitted Captures returns 0/0/false with `captures: []`.
- [ ] One match with default limit returns 1/1/false.
- [ ] More matches than `limit=1` returns the full verified total, one whole Capture, and
      `has_more=true`.
- [ ] A requested limit above the verified total returns all matches and
      `has_more=false`.
- [ ] Ascending and descending order retain the current request-started-at/capture-ID
      behavior before limit.
- [ ] A Search Mentions Capture with 113 Observation envelopes and provider
      `total_count=3055` still increments `total_matching` and `returned_count` by one.
- [ ] Organic fixtures deliberately separate outer Capture count from `se_results_count`
      and prove that provider corpus testimony does not control the outer envelope.
- [ ] Keyword Overview fixtures deliberately separate outer Capture count from
      `observation_count`, typed fact counts, and SQL join multiplicity.
- [ ] Organic/Search Mentions admitted-empty Capture documents each count as one history
      document.
- [ ] Keyword Overview does not count or manufacture a zero-envelope admitted-empty
      document.
- [ ] Keyword Overview multi-keyword join behavior counts unique matching Capture documents,
      not facts or join multiplicity.
- [ ] Recipe pinning counts only the matching series under the resolved pinned Recipe.

### Fail-closed behavior

- [ ] Damage or consistency disagreement in a matching candidate inside the returned limit
      remains 409.
- [ ] The same damage outside `limit=1` remains 409.
- [ ] A 409 response exposes none of `captures`, `total_matching`, `returned_count`,
      `limit`, `order`, or `has_more`, and exposes no partial count. The accepted body
      remains `{"detail":"evidence_integrity_failure"}`.
- [ ] Unselected Recipe, wrong pin, invalid query, and unknown/empty admitted history retain
      their exact accepted status meanings.
- [ ] No GET mutates Evidence, PostgreSQL, Recipe selection, or acquisition state.

### OpenAPI

- [ ] OpenAPI for each of the three routes exposes the same required outer metadata field
      names and scalar types.
- [ ] Descriptions state the admitted Capture-document grain and deterministic order.
- [ ] Descriptions state that `has_more` does not provide pagination.
- [ ] Descriptions state that empty history does not distinguish failed from never measured.
- [ ] Surface Capture bodies remain mappings and are not falsely documented as one universal
      schema.
- [ ] OpenAPI tests assert the substantive admitted-Capture, truncation, empty-history, and
      no-pagination meanings rather than checking property names and scalar types alone.
- [ ] Representative nested surface mappings retain their keys and scalar types through the
      response model.

### Architecture

- [ ] Shared history constants no longer belong to Keyword Overview.
- [ ] Shared code does not know surface table names, candidate tuples, identities, or fact
      bodies.
- [ ] Each surface retains its existing complete verification before metadata calculation.
- [ ] No schema, migration, Recipe, Derivation, provider, or Evidence write path changes.

## Required independent test vectors

Do not satisfy the ticket with one shared helper unit test alone. Each route must independently
prove its response and integrity boundary.

At minimum, tests must cover:

1. zero, one, and over-limit matching Capture counts for each route;
2. `limit=1` with at least one omitted healthy matching Capture;
3. deterministic ascending/descending order and Capture-ID tie-break;
4. matching damage outside the returned limit still producing 409;
5. Organic and Search Mentions admitted-empty counting;
6. Keyword Overview no manufactured admitted-empty history;
7. Search Mentions 113-envelope / provider-3055 Capture counting as one outer document;
8. Organic provider `se_results_count` remaining distinct from outer Capture count;
9. Keyword Overview Outcome/fact/join counts remaining distinct from outer Capture count;
10. pinned Recipe isolation;
11. exact additive key sets;
12. OpenAPI required fields, types, and substantive descriptions for all three routes;
13. representative nested Capture mappings passing through without stripping or coercion;
14. a tripwire proving no Search Mentions continuation, provider transport, Derivation, or
    mutation occurs during history GET.

Synthetic fixtures prove constructed branches, not that those branches occurred in live
provider Evidence. Report that distinction.

## Honest limits

API-01 does not prove or provide:

- retrieval of an outer tail beyond the requested limit;
- outer cursor stability or pagination under concurrent inserts;
- a complete measurement-activity ledger;
- failure-aware subject discovery;
- holdings/inventory;
- full typing of nested surface fact bodies;
- coordinated PostgreSQL-corruption detection beyond existing read checks;
- new transaction-isolation or concurrency guarantees;
- provider-corpus completeness;
- recurring acquisition;
- F12 or F13 remediation.

A response with `has_more=true` may expose a tail that cannot yet be retrieved when more than
100 admitted Capture documents match. This is deliberate Product direction for API-01, not a
completeness claim.

## Forbidden scope

API-01 must not add or modify:

- database schema or migrations;
- Derivation Recipes or Recipe selection semantics;
- parsers, paid probes, transport, credentials, or provider calls;
- Observation kinds, identities, values, or occurrence relations;
- inner provider paging, token following, or another exchange;
- Outcomes or holdings resources;
- failure coverage rows;
- direct Evidence/database access;
- strategy, panels, cadence, scoring, recommendations, or conclusions;
- outer offset/cursor pagination;
- unbounded list responses;
- F7, F12, F13, or AI-12 work;
- unrelated refactors.

## Completed pre-implementation review

GROK completed the required read-only code-first review against
`fa8cc3cc7bfc0042a192479af8a6decaa054ecda`. It returned
`REQUIRES TICKET CORRECTION`, not a Product or architecture redesign.

The review found no false premise in candidate membership, verify-before-limit sequencing,
transaction posture, admitted-empty behavior, Recipe scope, or the proposed helper boundary.

GPT accepted the optional `tests/test_provider_history.py` allowlist decision and reconciled
all five required corrections into this ticket.

The ticket remains provisional and implementation remains blocked until explicit, separate
CHAZ authorization names the exact clean start commit.

## Implementation report requirements

If a final reconciled ticket is later authorized, the implementation report must include:

- exact parent/child commits and changed paths;
- targeted and full verification evidence;
- exact response/OpenAPI changes for all three routes;
- proof that matching damage outside limit still fails closed;
- strongest and weakest parts;
- possible false greens;
- remaining caller-controlled influence;
- architecture drift or coupling;
- parser/provider traps exposed;
- closure blockers and deferred work;
- what later Outcomes/holdings surfaces should reuse;
- what should deliberately remain surface-local;
- usefulness and inference limits for the future strategy LLM;
- clean tree, no push, and confirmation of zero provider/network/credential activity.

## Verification commands for later implementation

Targeted:

    uv run pytest -q \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

If `tests/test_provider_history.py` is created, include it in the targeted invocation.

Full:

    uv run pytest -q
    uv run ruff check .
    uv run mypy

The five-minute full suite runs once on the final implementation/remediation commit through
the accepted exact-HEAD operator workflow. A connector timeout is not test evidence.
