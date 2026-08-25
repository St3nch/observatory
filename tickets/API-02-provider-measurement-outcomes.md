# API-02 — Provider Measurement Outcomes

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none — [CHAZ] authorized closure after exact-HEAD verification  
**Question-resolution pass:** completed against `5fa8bc17835e45795deda380276dab7b3b078004`  
**Pre-implementation review:** completed against `00e7c754b804df88e3c33c42512668678bd3430f`  
**Start commit:** `6c59da885d97f423be4453ae5bae67f350bc7933`

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

## Pre-implementation review reconciliation

[GROK] returned `REQUIRES TICKET CORRECTION` after the mandatory read-only review of
`00e7c754b804df88e3c33c42512668678bd3430f`. [GPT] independently verified and accepts
the store-wide Evidence availability correction, positive admitted-count invariant,
one-Capture lifecycle check, explicit Attempt parameter paths, closed OpenAPI enums, and
missing test vectors.

The review proposed treating a subject-matching Evidence set with no Attempt-stage rows
under the resolved Recipe as empty 200 while treating a proper subset of missing rows as
409. That proposal is not accepted. D14 makes Outcomes the all-classification activity
resource and requires Evidence/rebuildable disagreement to fail closed. Every provider
derivation writes an Attempt-stage row for every verified adapter Attempt under that
Recipe. Therefore, once verified Evidence proves a subject-matching Attempt, a missing
resolved-Recipe Attempt-stage row is incomplete rebuildable state and returns 409 whether
one, some, or all such rows are missing.

This deliberately differs from admitted-only history. It prevents a selected-but-not-built
or wholly deleted Outcome projection from masquerading as no measurement activity. A
successful empty Outcomes list is reserved for no verified subject-matching Attempt
Evidence in the route's adapter scope.

No Product question or architecture redesign remains.

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

Keyword Overview subjects come from `parameters.keywords`; Organic from
`parameters.keyword`; Search Mentions subject/filter fields from
`parameters.target[0]`. Membership is exact string equality or membership and must not
use `normalize_keyword`. Do not emit the closed `parameters.contract` field because
the item already discloses `adapter_contract`.

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
a null Capture ID at Capture stage, two verified Captures citing one Attempt, or any other
disagreement with verified lifecycle Evidence fail closed with HTTP 409. The reader must
not select one Capture and hide the other.

`observation_admitted_empty` is valid Outcomes activity for all three derivations even
though Keyword Overview cannot expose it as a subject-bound history document. Outcomes
must not reuse admitted-history membership.

## Evidence discovery and verification

At current pre-F12 volume, use D14's accepted bridge: a bounded read-only scan of committed
Evidence.

The walk is store-wide verify-first, then adapter-filtered. Adapter, parent, and subject
cannot be trusted until a committed bundle has verified. Any duplicate committed identity
or `IntegrityError` while enumerating or verifying an Attempt or Capture returns HTTP
409 with no envelope, even when the damaged event would have belonged to fixture, sandbox,
Target Metrics, another adapter, or another provider after a successful read. Do not copy
Derivation's skip-on-`IntegrityError` behavior. Successfully verified foreign events may
be excluded after their provider/adapter is known.

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
8. Require at most one verified Capture for each verified Attempt.
9. Verify all matching items and rebuildable state before ordering, counting, or limiting.

Let S be the verified Attempt Evidence matching the exact route adapter and subject filter.
If S is empty, return an empty 200. If S is non-empty, every member must have its exact
Attempt-stage Outcome under the resolved Recipe; any missing row, including all rows
missing, is HTTP 409. Every member with a verified Capture must likewise have its exact
Capture-stage row. This route does not use the history convention in which an underived
Recipe can simply have no admitted candidates.

Evidence defines membership and subject identity. PostgreSQL does not nominate candidates.
Missing required state, extra/foreign stage state for a matching Attempt, wrong parent,
wrong adapter/provider/Recipe, two Captures for one Attempt, duplicate committed identity,
or any Evidence disagreement is HTTP 409 with no partial Outcomes envelope.

This store-wide availability coupling is deliberate for the pre-F12 bridge. History may
remain available when unrelated damaged Evidence is outside its PostgreSQL-nominated
candidate set; Outcomes may not, because an unreadable event cannot safely be classified
as foreign.

## Observation-count integrity

API-02 hardens counts served by the new ledger while leaving
`GET /v1/attempts/{attempt_id}` unchanged.

For every matching item:

- Attempt-stage `observation_count` is zero.
- Capture-stage count equals `observation_envelopes` cardinality for the exact Capture
  and resolved Recipe.
- Non-admitted and `observation_admitted_empty` classifications require zero envelopes
  and count zero.
- `observation_admitted` requires `observation_count >= 1` and exact
  stored-count/envelope-cardinality equality.

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
order, and `has_more: false`. It means no verified subject-matching Attempt Evidence is
held under this route's exact provider/adapter scope. A matching Attempt with missing
resolved-Recipe Outcome state is 409, not empty. Empty does not mean the subject is unimportant, the provider reported
absence, nothing exists under
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
- the Attempt-stage singleton and eight Capture-stage classifications are closed enums;
- `observation_admitted` requires a positive envelope count;
- unrelated unreadable committed Evidence in the same root makes the route fail 409;
- `has_more` does not provide pagination;
- items contain no Observation facts;
- empty-scope and failure/absence inference limits.

A generic untyped request mapping or universal provider request schema is insufficient.

## Shared and surface-local implementation boundary

`src/observatory/provider_outcomes.py` may own surface-neutral integrity machinery that
must remain identical across all three routes:

- limit constants, shared classification/Outcome-view typing, common item fields, and
  outer metadata/invariant math;
- the store-wide verify-first Evidence walk and Attempt/Capture lifecycle index;
- validated Recipe-material loading and Recipe identity/metadata agreement checks;
- resolved-Recipe Outcome-stage queries and strict Attempt/Capture pairing;
- Observation-envelope provenance/cardinality checks;
- common item projection from already verified Evidence, Recipe, and stage state.

This shared machinery must receive the route's exact expected provider and adapter where
needed. It must not know Keyword Overview, Google Organic, or Search Mentions fact-table
names, request shapes, subject fields, membership rules, provider continuation, or
surface-specific admitted-history behavior.

Each surface reader retains its exact provider/adapter/Recipe inputs, verified subject
membership, exact request mapping, surface-specific parameter validation, deterministic
ordering, limiting, and outer-response assembly.

Reuse API-01 envelope mathematics and limits where practical, but do not call this history,
reuse `HistoryListEnvelope`, build a generic subject/provider loader, create a universal
request/subject model, or use PostgreSQL-first candidate selection.

## Post-implementation Steward review reconciliation

[GROK] completed the required strictly read-only post-implementation question pass against
clean `1b4477632dae2979ea2bce2c67df9e3812787d58`. [GPT] independently inspected the
committed ticket, parent/child diff, production code, tests, Evidence Store, Recipe
selection/validation, and PostgreSQL schema through LinuxVedaOpsMCP. No Product question
remains. API-02 is not closure-ready until the following bounded remediation is committed
and independently reviewed.

The implementation correctly centralized the store-wide Evidence walk and stage pairing,
but this exceeded the earlier narrow shared-module sentence. The corrected boundary above
accepts that surface-neutral centralization because triplicating verify-or-409 and pairing
would increase cross-surface drift risk. It does not authorize a generic subject loader or
move any request shape, membership rule, provider fact table, or continuation behavior
out of its surface reader.

### Required Recipe identity remediation

For the resolved Recipe used by each route, the reader must verify before any successful
empty or non-empty response:

- resolved provider equals the route's exact provider;
- resolved adapter equals the route's exact adapter;
- `recipe_canonical_bytes` decode as UTF-8 JSON and validate as the closed Recipe
  document;
- validated Recipe bytes are exact canonical JCS;
- SHA-256 of those exact bytes equals `derivation_version_id`;
- Recipe-document provider/adapter, `provider_recipes` provider/adapter columns,
  resolved provider/adapter, and route provider/adapter all agree.

Decode, schema, canonicalization, digest, or metadata disagreement is integrity failure:
HTTP 409 `{"detail":"evidence_integrity_failure"}`, with no Outcomes envelope. A
wrong-provider Recipe registered for the route adapter must not produce an incorrectly
labelled empty 200. Do not modify Recipe registration, selection, schema, or Derivation.

### Required Observation-envelope provenance remediation

Cardinality alone is insufficient. For every matching Capture and resolved Recipe, load
the exact `observation_envelopes` rows used for the count and require every row to agree
with:

- the verified Evidence `attempt_id`;
- the route/Recipe provider;
- the route/Recipe adapter;
- an `observation_kind` declared by the validated Recipe.

Continue to require exact row cardinality equality, positive cardinality for
`observation_admitted`, and zero rows/count for every non-admitted or admitted-empty
classification. Do not import history's typed fact-row equality, subordinate-occurrence
checks, or provider-specific table knowledge.

### Required remediation proofs

Add independent Outcomes HTTP tests proving at least:

1. identical `authorized_at` values are tie-broken by `attempt_id` in ascending and
   descending order before limiting;
2. damaged committed foreign-adapter Attempt Evidence returns 409, complementing the
   existing foreign-Capture proof;
3. unexpected/wrong-stage or extra Capture-stage PostgreSQL state returns 409;
4. wrong Capture/Recipe relationship returns 409;
5. malformed or drifted committed Attempt Evidence for every surface returns 409 before
   its request testimony can be served;
6. wrong-provider Recipe metadata for the correct adapter returns 409 even when the
   subject-matching Evidence set is empty;
7. invalid UTF-8/JSON, non-canonical, digest-disagreeing, or document/column-disagreeing
   Recipe bytes return 409 rather than 200 or 500;
8. cardinality-preserving `observation_envelopes` drift in `attempt_id`, provider,
   adapter, or observation kind returns 409;
9. every new 409 response exposes no Outcomes envelope or partial count.

Tests may consolidate equivalent plants where one exact vector proves multiple listed
invariants, but must not claim that a schema/helper inference is an independent HTTP proof.
No full suite is authorized during remediation; use the existing targeted API-02 command,
Ruff, and mypy.

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
- [ ] Two verified Captures for one Attempt return 409 rather than selecting one.
- [ ] The Attempt singleton and eight Capture classifications are closed enums.
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
- [ ] `observation_admitted` with zero count and zero envelopes returns 409.
- [ ] If verified subject-matching Attempt Evidence exists but one, some, or all
      resolved-Recipe Attempt rows are missing, the route returns 409.
- [ ] A damaged committed Attempt or Capture for another adapter in the same root returns
      409 rather than being skipped.
- [ ] Each route exposes its exact verified surface-local request key set and parameter
      paths.
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
9. damaged foreign-adapter committed Attempt and Capture in the same root;
10. zero, partial, and wholly missing resolved-Recipe Attempt-stage rows for nonempty S;
11. Evidence Capture present without Capture-stage row, which must not render unresolved;
12. two verified Captures citing one Attempt;
13. missing and duplicate/wrong-stage PostgreSQL rows;
14. wrong Capture parent/provider/adapter/Recipe;
15. stale `observation_count` versus envelope cardinality;
16. planted `observation_admitted` with zero count and zero envelopes;
17. exact request keys, parameter paths, and malformed parameters per surface;
18. exact closed classification enums and substantive OpenAPI descriptions;
19. tripwires proving no transport, continuation, Derivation, Evidence write, or
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
- isolation from unrelated damaged committed Evidence during the store-wide walk;
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

## Completed pre-implementation ticket review

[GROK] reviewed the provisional ticket read-only against
`00e7c754b804df88e3c33c42512668678bd3430f` and returned
`REQUIRES TICKET CORRECTION`.

The review confirmed the route set, one-Attempt grain, surface request fields,
classification set, changed-path allowlist, ordering, HTTP mappings, and no-schema
boundary. This reconciliation incorporates the six bounded proof/contract corrections
listed above and rejects the proposed all-missing-rows empty response for the D14
fail-closed reason recorded above.

The ticket is now ready for separate [CHAZ] implementation authorization against the final
clean ticket commit. No implementation, tests, provider call, credentials, or Evidence
activity occurred during ticket review or reconciliation.

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

**Parent / start commit:** `6c59da885d97f423be4453ae5bae67f350bc7933`  
**This commit** is the API-02 implementation child. Status `review`, never `done`.

### Changed paths

Production:

- `src/observatory/provider_outcomes.py` (new)
- `src/observatory/keyword_overview_read.py`
- `src/observatory/google_organic_read.py`
- `src/observatory/search_mentions_read.py`
- `src/observatory/api.py`

Tests:

- `tests/test_provider_outcomes.py` (new, helper invariants only)
- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`

Ticket: this file.

### Routes and OpenAPI

Added:

- `GET /v1/providers/dataforseo/google/keyword-overview/outcomes`
- `GET /v1/providers/dataforseo/google/organic/outcomes`
- `GET /v1/providers/dataforseo/google/ai-optimization/search-mentions/outcomes`

Typed envelopes `KeywordOverviewOutcomesEnvelope`, `GoogleOrganicOutcomesEnvelope`, and `SearchMentionsOutcomesEnvelope` with closed Attempt/Capture classification enums and surface-specific `request` models. History routes and `GET /v1/attempts/{attempt_id}` are unchanged.

### Integrity proofs

Store-wide verify-or-409: damaged foreign-adapter Capture in the same root 409s Outcomes while admitted history of the route adapter can still 200.

Nonempty S with one, some, or all missing Recipe Attempt-stage rows is 409, including selected-but-not-derived Evidence.

Evidence Capture without Capture-stage Outcome is 409 (does not render unresolved).

Two verified Captures for one Attempt is 409.

`observation_admitted` requires count ≥ 1 and envelope cardinality equality; non-admitted and admitted-empty require count 0 and zero envelopes. Attempt audit may still 200 a stale count.

Verify-before-limit: matching damage outside `limit=1` is 409 with no envelope keys.

Keyword Overview five-keyword Attempt is one item; member queries hit it once; non-members empty 200.

### Verification

Targeted:

    uv run pytest -q \
      tests/test_provider_outcomes.py \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

Result: **63 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy           # Success: no issues found in 66 source files

Full suite was **not** run (reserved for CHAZ exact-HEAD operator block).

### Strongest

Store-wide verify-first then adapter filter; Capture presence from Evidence; nonempty-S missing Attempt-stage is 409; envelope-cardinality hardening that the Attempt audit still lacks.

### Weakest

The three loaders repeat the resolve/filter/sort/envelope shell. Shared `provider_outcomes.py` owns the Evidence walk and pairing so skip-on-`IntegrityError` cannot appear in one surface only. That is slightly broader than the ticket's "math/types only" sentence, but it has no surface tables or request shapes.

### Possible false greens

Helper math tests do not replace route 409s. Synthetic no_response → reclassified admitted-empty/zero-admitted plants prove Recipe branches, not live PF-03/PF-10/AI-03 (those are admitted non-empty). Closed Attempt schema already enforces KO 1..5 keywords; the reader also fail-closes if that ever drifted.

### Caller-controlled influence

Query `requested_keyword`, optional Recipe pin, `limit` 1–100, `order`. Mutable Recipe selection. No cursor.

### Architecture

`HISTORY_LIMIT_*` reused. Shared module does not know KO/Organic/SM table names. Readers own subject membership and request mapping. History membership SQL is unused.

### Parser/provider traps

None new. SM `request.limit`/`offset` are Attempt fields, not Outcomes pagination. Token is not read. KO classification remains Capture-wide.

### Closure blockers

None from this implementation. Full suite not yet run.

### Deferred

Holdings/index, outer pagination past 100, Attempt-audit count hardening, AI-12, F12/F13, `related_result` stop-before-derive.

### Reuse later

Store-wide verify-or-409 walk, pair grain, envelope math, 409-no-partial-payload, Recipe pin/select HTTP map.

### Remain surface-local

Subject extraction, request mapping, admitted-empty eligibility as classification (not history membership).

### Evidence vs contract vs synthetic

Evidence is Attempt/Capture bytes. Recipe is the classification contract. Ordinary tests prove synthetic unresolved/transport/empty/zero-count plants.

### Strategy-LLM

Useful: for keyword X on surface S under Recipe R, derived measurement events including unresolved and failures. Unsafe: `authorized_unresolved` as unsent/current status; `observation_count` as ranks/mentions; five KO keywords as five measurements; empty Outcomes as provider-zero.

### Data-model

No `outcomes` column or subject index. Failure subjects remain Evidence-derived. Do not invent coverage.

### Hygiene

One implementation commit, no amend, no push. Zero provider calls, credentials, spend, retained Evidence access, or continuation. Working tree left clean after the commit.

## Remediation report

**Remediation start commit:** `9634f95c648328b2d62afbb0aebbb2d496e1db67`  
**This commit** is the API-02 remediation child. Status `review`, never `done`.

### Changed paths

Production:

- `src/observatory/provider_outcomes.py`
- `src/observatory/keyword_overview_read.py`
- `src/observatory/google_organic_read.py`
- `src/observatory/search_mentions_read.py`

Tests:

- `tests/test_api_keyword_overview.py`
- `tests/test_api_google_organic.py`
- `tests/test_api_search_mentions.py`

Ticket: this file.

`src/observatory/api.py` unchanged: existing `IntegrityError` → HTTP 409 mapping already covers the new raises. `tests/test_provider_outcomes.py` unchanged (helper math only).

### Recipe identity

`load_validated_outcomes_recipe` runs after Recipe selection and before any empty or non-empty Outcomes 200. It requires:

- resolved provider/adapter equal the route expected pair;
- `provider_recipes` columns including `recipe_canonical_bytes`;
- UTF-8 JSON decode;
- public `validate_recipe`;
- `canonical_json(validated)` exact-equals stored bytes;
- `content_digest(stored_bytes)` equals `derivation_version_id`;
- document, PostgreSQL columns, resolved metadata, and route expectations agree.

Decode, JSON, Recipe-document, JCS, digest, and metadata disagreement become `IntegrityError` → HTTP 409 `{"detail":"evidence_integrity_failure"}`. No Outcomes envelope is returned. `provider_recipe.py` was not modified.

### Envelope provenance and cardinality

`assert_capture_envelopes` loads `observation_envelopes` rows for the exact Capture and Recipe. `len(rows)` is cardinality. Every row must match verified Attempt `attempt_id`, validated Recipe provider/adapter, and a declared `observation_kind`.

Still required:

- `observation_admitted`: count ≥ 1 and count == `len(rows)`;
- every non-admitted classification: count == 0 and no rows;
- `observation_admitted_empty`: count == 0 and no rows.

Typed fact tables and subordinate occurrence tables are not read.

### Shared vs surface-local

Shared in `provider_outcomes.py`: store-wide verify-first walk, validated Recipe loading, stage queries and pairing, envelope provenance/cardinality, common item projection. Helpers take exact expected provider/adapter.

Surface-local: subject membership, request mapping, route constants, ordering/limiting, outer-response assembly. No generic subject/provider loader. Shared code still knows no KO/Organic/Search Mentions fact-table names, request shapes, or continuation.

### New HTTP vectors

1. Equal `authorized_at` tie-broken by `attempt_id` in asc and desc-before-limit on all three routes.
2. Damaged committed foreign-adapter Attempt Evidence → 409 (KO fixture Attempt, complements existing foreign-Capture).
3. Extra Capture-stage Outcome row → 409.
4. One-row Capture-stage `capture_id` disagrees with Evidence Capture (no_response plant, FK-safe) → 409.
5. Xor-damaged committed Attempt Evidence on each surface → 409.
6. Wrong-provider Recipe column for the correct adapter with empty subject scope on all three routes → 409, not empty 200.
7. Invalid JSON, invalid UTF-8, non-canonical JCS, CORE bytes under EXTENDED id (digest), and document/column provider disagreement → 409, not 500.
8. Cardinality-preserving envelope `attempt_id` / provider / adapter drift, plus extra undeclared `observation_kind` with matching bumped count → 409. In-place undeclared-kind UPDATE is blocked by typed-table FKs; the extra-row plant is the HTTP proof.
9. Every new 409 asserts no `outcomes`, `total_matching`, `returned_count`, or `has_more` keys.

### Verification

Targeted:

    uv run pytest -q \
      tests/test_provider_outcomes.py \
      tests/test_api_keyword_overview.py \
      tests/test_api_google_organic.py \
      tests/test_api_search_mentions.py

Result: **69 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy           # Success: no issues found in 66 source files

Full suite was **not** run. No push, provider call, credentials, spend, continuation, or live Evidence activity.

### Strongest

Recipe identity runs before empty 200, so a drifted selected Recipe cannot masquerade as no activity. Envelope provenance is row-level, so count-only agreement no longer hides attempt/provider/adapter/kind drift.

### Weakest

The three loaders still copy resolve/filter/sort/envelope assembly. Ticket forbids a generic subject loader. Envelope kind drift uses an extra undeclared-kind row plus bumped count because child typed-table FKs reject `UPDATE observation_kind`.

### Possible false greens

Helper envelope math in `tests/test_provider_outcomes.py` does not prove these 409s. Synthetic Recipe-byte and envelope UPDATE plants prove constructed branches, not live provider Recipe or envelope corruption. Tie-break tests use unresolved Attempts; they do not prove Capture-time ordering (forbidden). Extra undeclared-kind INSERT is not an in-place kind UPDATE.

### Caller-controlled influence

Unchanged: `requested_keyword`, optional Recipe pin, `limit` 1–100, `order`. Mutable Recipe selection. No cursor.

### Architecture

No schema, Recipe write path, Derivation, history, Attempt-audit, parser, provider, or continuation change. Shared Recipe/envelope checks use public `validate_recipe`, `canonical_json`, and `content_digest`.

### Parser/provider traps

None new. Search Mentions still does not read `search_after_token`. `request.limit`/`offset` remain Attempt fields.

### Closure blockers

Full suite not run. Steward independent review of this remediation commit is still required. Ticket remains `review`.

### Deferred

Unchanged: holdings/index, pagination past 100, Attempt-audit count hardening, AI-12, F12/F13, Organic `related_result` stop-before-derive.

### Reuse later

Validated Recipe loading and envelope provenance/cardinality belong in later Outcomes-like readers. Do not reuse for history membership.

### Remain surface-local

Subject membership, request mapping, ordering/limiting, outer assembly.

### Evidence vs contract vs synthetic

Evidence remains Attempt/Capture bytes. Recipe bytes are the classification contract, now verified as JCS identity before any Outcomes 200. Envelope rows are rebuildable PostgreSQL, not Evidence. Tests are synthetic plants.

### Strategy-LLM

Useful: do not treat empty Outcomes as “no measurement” unless Recipe identity also verified. Unsafe: `observation_count` as provider result/corpus counts; envelope kind extra-row plants as live provider shape.

### Data-model

No `outcomes` or envelope schema change. Do not infer a subject index from the store-wide walk.

### Hygiene

One remediation commit, no amend, no push. Zero provider calls, credentials, spend, continuation, or live Evidence mutation outside isolated tests. Working tree left clean after the commit.

## Steward closure

[GPT] independently reviewed the committed implementation and remediation through
LinuxVedaOpsMCP, including the exact ticket, parent/child diffs, production code, tests,
Evidence Store behavior, Recipe validation/selection, PostgreSQL schema, API boundary,
and Grok's candid implementation assessments. Grok's reports and question passes were
treated as coworker input, not independent verification.

[CHAZ] authorized closure after running the final operator block against exact clean
implementation HEAD `2296dfe06d89a508b473192f815f803ed67c6b5c`.

Accepted exact-HEAD evidence:

- targeted API-02 suite:

      uv run pytest -q \
        tests/test_provider_outcomes.py \
        tests/test_api_keyword_overview.py \
        tests/test_api_google_organic.py \
        tests/test_api_search_mentions.py

  Result: **69 passed**, 1 warning in 167.40 seconds.
- full suite, run once after review/remediation settled:
  **1222 passed, 1 skipped, 1 warning** in 357.28 seconds;
- `uv run ruff check .`: all checks passed;
- `uv run mypy`: success, no issues in 66 source files;
- initial and final HEAD checks: exact
  `2296dfe06d89a508b473192f815f803ed67c6b5c`;
- initial and final working-tree checks: clean.

The warning is the known Starlette/`httpx` TestClient deprecation and is accepted as
non-blocking.

Closure accepts the documented API-02 limits. In particular, Outcomes remains a
subject-filtered, all-classification activity resource—not holdings, history, current
status, cadence, strategy, or provider-corpus completeness. The store-wide Evidence walk
remains the accepted low-volume bridge; holdings/index, pagination past 100, Attempt-audit
count hardening, AI-12, F12/F13, and Organic `related_result` stop-before-derive remain
separate work.

This closure changes only the API-02 ticket. The suites, Ruff, and mypy are not repeated
after this ticket-only commit. Agents do not push; [CHAZ] owns any push.
