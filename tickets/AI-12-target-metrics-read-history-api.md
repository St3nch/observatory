# AI-12 — Target Metrics Recipe selection and admitted-history API

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none  
**Authorized by:** [CHAZ] implementation authorization at the named start commit  
**Closure authorized by:** [CHAZ] after exact-HEAD operator verification  
**Pre-implementation review:** GROK RECONCILE, completed read-only at f7e243c8c180eedd2cce277c2e39db4b80a8128f  
**Review base:** f7e243c8c180eedd2cce277c2e39db4b80a8128f  
**Start commit:** `2297aa2c464a8b851e01c70b6ed75cebb21e204a`  

## Purpose

Complete the first consumer-readable Target Metrics fact slice for the exact adapter:

    dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1

AI-12 selects or pins the accepted Recipe and adds one subject-filtered admitted-history
route. One returned item is one admitted Capture with a fully typed Target Metrics request,
provenance, total, distinct source-domain facts, and result context inside the API-01 outer
list envelope.

This does not copy the D14 three-resource split merely because the first three surfaces expose
history, Measurement Outcomes, and Holdings. Target Metrics Outcomes and Holdings remain
possible later siblings, not prerequisites or AI-12 scope.

GROK reviewed the provisional ticket read-only at the exact review base and returned
RECONCILE. GPT independently verified and incorporated the accepted technical corrections
below. This final ticket is not implementation authority until CHAZ separately authorizes
implementation at its exact committed HEAD. No second GROK ticket review is required.

## Authority

- VISION and VOCABULARY
- D2, D3, D8, and D11 through D14
- F5, F6, F12, and F13 deferrals
- Capture Event v2 and Provider Derivation after F11
- AI-07 through AI-10 adapter, Evidence, and strict-parser authority
- AI-11 Recipe, two kinds, three typed relations, and complete-set persistence
- API-01 history envelope and verify-before-limit behavior
- API-02 separation of Measurement Outcomes
- API-03 separation of Evidence-backed Holdings

AI-11 names Target Metrics Recipe selection and read/history API as the next boundary. D14
does not broaden that into an automatic three-resource ticket.

## Question-resolution lock

GROK completed the required code-first consumer review read-only at the review base. GPT
independently checked its material findings through LinuxVedaOpsMCP.

No Product question remains. The smallest honest boundary is Recipe selection/pinning plus
admitted history. Failure-versus-never-measured remains a future Outcomes concern.
Subject/scope discovery remains a future Holdings concern.

Settled semantics:

- the exact verified Attempt keyword is the subject;
- exact closed Attempt parameters are request testimony;
- one history item is one admitted Capture;
- valid zero metrics remain observation_admitted;
- Recipe v1 never emits observation_admitted_empty;
- structural total_count, result offset, and items_count zeros are not corpus emptiness;
- internal_list_limit and returned source count prove neither truncation nor completeness;
- location, language, and platform groupings are context, not Observation families;
- exact source-domain strings are identities;
- provider_array_index is lexical testimony, not rank;
- Provider Update Time and Data Period remain unstated;
- no universal fact body or shared Target Metrics/Search Mentions model is justified.

Recipe v1 Observation grain is one total plus one source-domain Observation per distinct
exact domain identity. AI-10 rejects duplicate grouping keys before Derivation; AI-11's
same-key grouping loop is defense in depth and emits no collapsed-duplicate admitted
document. Therefore every Recipe v1 admitted Capture must satisfy:

    observation_count == 1 + len(source_domains)
    sources_domain_count == len(source_domains)

The two counts still describe different grains: generic Observation-envelope cardinality and
raw parsed provider-array cardinality. Equality is a Recipe v1 invariant, not evidence of
completeness, truncation, rank, share, or partition. Any inequality is PostgreSQL integrity
damage and returns HTTP 409 with no envelope. Duplicate provider keys remain parser rejection,
not a successful-history or distinct history-409 scenario.

## Existing substrate

The review base contains:

- accepted adapter constant and parameter validator;
- strict parser and frozen AI-09 fixture;
- canonical Recipe digest
  b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104;
- total kind dataforseo.google.ai_optimization.target_metrics.total.v1;
- source-domain kind
  dataforseo.google.ai_optimization.target_metrics.source_domain.v1;
- target_metrics_totals, target_metrics_source_domains, and
  target_metrics_result_context;
- generic Recipe registration, selection, and pinning;
- API-01 list helpers and limits;
- generic provider Attempt audit reader.

It has no repository proof of Target Metrics selection, read module, route, typed API/OpenAPI,
route tests, or Target Metrics membership in the provider-Attempt routing set. This ticket
makes no claim about external operator-database state. Generic selection must be proven only
in isolated PostgreSQL; implementation must not inspect or select operator state
automatically.

## Boundary

AI-12 may add:

- src/observatory/target_metrics_read.py;
- a dedicated Target Metrics history envelope and fully typed closed nested models;
- one admitted-history route;
- isolated selection, pinning, history, OpenAPI, and integrity tests;
- Target Metrics membership in the existing provider Attempt-audit routing set and bounded
  proof of existing generic behavior.

It may reuse resolve_provider_recipe, API-01 constants/helpers, read-only PostgreSQL
discipline, verified Attempt/Capture reads, and existing HTTP error mappings.

It must not add:

- Target Metrics Outcomes or Holdings;
- a scope filter beyond requested_keyword;
- outer cursor/offset/token or retrieval beyond 100;
- provider activity, credentials, spend, retries, continuation, or new/live Evidence;
- schema, migration, parser, Recipe, derivation, identity, classification, or persistence
  changes;
- automatic Recipe selection;
- a generic history/writer framework or shared Search Mentions request model;
- normalization, Brand/Page identity, cross-surface joins, rank, share, completeness,
  truncation, strategy, scoring, cadence, monitoring, or desired coverage;
- direct consumer Evidence/PostgreSQL access;
- F12, F13, or unrelated Attempt-audit count hardening.

## Route and query

Add exactly:

    GET /v1/providers/dataforseo/google/ai-optimization/target-metrics/history

Query:

- requested_keyword: required exact string with FastAPI min_length=1;
- derivation_version_id: optional exact Recipe pin;
- limit: default 20, minimum 1, maximum 100;
- order: asc or desc, default asc.

Do not trim, case-fold, normalize, or replace the subject with task.data echo. Add no scope
filter, cursor, offset, continuation, provider token, or undeclared query parameter.

## Recipe resolution

Resolve the exact adapter through resolve_provider_recipe.

- no selection/no pin: HTTP 503 provider_recipe_not_selected;
- selected Recipe: recipe_resolution selected;
- accepted pin: recipe_resolution pinned;
- malformed, unknown, or wrong-adapter pin: accepted HTTP 404 behavior;
- Recipe or relational integrity disagreement: HTTP 409 evidence_integrity_failure with no
  history-envelope keys.

After resolution, load provider_recipes.recipe_canonical_bytes. Require UTF-8 JSON, the
closed Recipe schema, exact JCS, digest agreement with derivation_version_id, and agreement
among route, resolved state, columns, and document on provider dataforseo and the exact Target
Metrics adapter.

This route serves only Recipe v1 identity
b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104. Require exactly the two
v1 Observation kinds in Recipe order and exactly these Capture classifications:

- no_response;
- observation_admitted;
- provider_envelope_rejected;
- provider_error;
- reconciliation_failed;
- response_partial;
- transport_complete_non_admissible.

observation_admitted_empty is forbidden. Any other resolved Recipe identity, whether selected
or pinned, returns HTTP 404 with no history envelope. Tampered, non-canonical, or
digest-disagreeing stored bytes for the v1 identity return HTTP 409. A same-shaped or
caller-supplied document is not authority.

Selection is operational state, not Evidence or Derivation. Tests may select only in isolated
temporary PostgreSQL.

## Exact outer response

Successful responses have exactly:

- provider
- adapter_contract
- requested_keyword
- derivation_version_id
- recipe_resolution
- observation_kinds
- captures
- total_matching
- returned_count
- limit
- order
- has_more

Use API-01 semantics. total_matching counts unique verified matching admitted Captures before
sort/limit. returned_count equals len(captures). has_more is true exactly when total_matching
is greater than returned_count. Never use envelope, typed-row, raw-source, mention,
provider-count, or SQL-join cardinality as the outer grain.

Order by (request_started_at, capture_id). Descending reverses the complete order before
limiting. has_more discloses an unavailable tail; it is not pagination.

## Membership and request authority

A history member is one unique Capture for the resolved Recipe where:

- context has the exact requested_keyword;
- Capture Outcome is exactly observation_admitted;
- Outcome/Attempt/Capture/Recipe provenance agrees;
- exactly one total exists;
- generic envelopes, typed facts, and context form a complete set;
- verified Attempt/Capture Evidence agrees with provider, adapter, parent, subject, scope, and
  PostgreSQL provenance.

Load context rows for the exact keyword and v1 Recipe before filtering on classification. If
a matching context row has a missing or non-observation_admitted Capture Outcome, return HTTP
409. Context exists only for admitted Recipe v1 Captures; silently omitting corrupt context as
empty history is forbidden.

Exclude Attempt-stage activity, honestly rejected/failing Captures without context,
observation_admitted_empty, unverified rows, other Recipes, echo-only matches, and
per-Observation items.

A zero-metric total is admitted. A Capture with zero domains still has its required total and
is not admitted-empty.

Each Capture exposes exact verified Attempt request testimony:

- keyword
- match_type
- search_filter
- search_scope as exact ordered array
- platform
- location_code
- language_code
- internal_list_limit

Frozen constants remain scope testimony. Run the accepted Target Metrics parameter validator
over verified Attempt parameters and require equality with persisted context. task.data and
task.path remain non-authoritative.

## Fully typed Capture

Each captures item is closed with exactly:

- attempt_id
- capture_id
- provider
- adapter_contract
- derivation_version_id
- authorized_at
- request_started_at
- transport_ended_at
- request
- capture_outcome
- result_context
- total
- source_domains

The three repeated provenance keys must exactly equal the outer envelope and verified
Recipe/Evidence. They keep each Capture document self-describing like the sibling history
resources without creating a universal fact body.

capture_outcome contains classification fixed to observation_admitted and observation_count.
The count must equal complete envelope cardinality and:

    1 + len(source_domains)
    1 + sources_domain_count

AI-10 uniqueness makes the typed source-domain list and raw parsed source array equal in
cardinality for every admitted Recipe v1 Capture.

total is exactly one closed object with:

- observation_kind
- within_capture_identity
- requested_keyword
- mentions
- ai_search_volume

The kind is fixed to the accepted total kind. Subject matches route, Attempt, context, and
identity. Zero metrics remain stated facts.

source_domains contains one closed object per distinct exact domain:

- observation_kind
- within_capture_identity
- requested_keyword
- domain
- mentions
- ai_search_volume
- provider_array_index

Preserve exact raw strings. Do not normalize, parse as hostname, collapse www, resolve a
Brand, or join another surface. Order by (provider_array_index, within_capture_identity).
The index is the exact unique lexical array position for that admitted Recipe v1 identity,
never rank, importance, share, or cross-Capture identity.

result_context is a closed object with exactly:

- total_count;
- result_offset;
- items_count;
- items_state;
- location;
- language;
- platform;
- sources_domain_count;
- search_results_domain;
- brand_entities_title;
- brand_entities_category.

location is exactly
{key: integer, mentions: integer, ai_search_volume: integer,
provider_array_index: integer, row_count: 1}. language and platform have the same exact keys
with string key and row_count fixed to 1.

search_results_domain, brand_entities_title, and brand_entities_category are each exactly
{state, count}. state is the closed enum absent | json_null | stated. count is null for absent
or json_null and zero for stated under admitted Recipe v1, because nonempty optional families
fail closed. items_state uses the same closed enum.

Groupings are request-constrained context, not Observation families. Their metrics may
disagree with total. Structural zeros and absent/JSON-null/stated-empty items do not mean an
empty aggregate.

sources_domain_count is raw provider-array length and must equal len(source_domains) for every
admitted Recipe v1 Capture. Any inequality returns HTTP 409; it is never a collapsed-duplicate
or truncation state. Reaching internal_list_limit changes nothing. Capture timestamps cannot
substitute for unstated provider time axes.

## Verify before limit

Within one read-only PostgreSQL boundary:

1. resolve and validate Recipe;
2. select the complete unique matching set;
3. verify every matching Attempt and Capture;
4. validate exact request and parentage;
5. verify complete Outcome/envelope/total/domain/context consistency;
6. compute total_matching;
7. sort the complete set;
8. limit whole Captures;
9. project typed Captures;
10. compute returned_count and has_more.

Any matching damage, including outside limit=1, returns exact 409 with no partial envelope.

Checks include:

- one admitted Capture Outcome;
- observation_count equals generic envelope cardinality;
- envelopes equal one total plus all distinct domain identities;
- exactly one context and one total;
- no unknown kind or missing/extra/cross-Capture typed row;
- exact subject, request, provider, adapter, parent, Recipe, and provenance agreement;
- sources_domain_count exactly equals typed source-domain cardinality;
- valid integer, state, and singleton-context invariants.

Do not re-run parser/Derivation in reads or mutate Evidence/PostgreSQL.

## Empty and errors

Empty history returns captures [], total_matching 0, returned_count 0, applied limit, requested
order, and has_more false. It means only no matching admitted history under this subject and
Recipe. It does not mean failure, unresolved authorization, never measured, provider zero, or
absence from a provider corpus.

Outcomes are needed for activity/failure testimony. Holdings are needed for discovery.
Neither is added here.

## Provider Attempt audit

Add Target Metrics to the provider-Attempt routing set so:

    GET /v1/attempts/{attempt_id}

uses the existing generic provider reader for verified Target Metrics Attempts. Prove selected,
pinned, and fail-closed behavior. Do not redesign the resource, expose facts there, or perform
deferred count hardening.

## Typed OpenAPI

Use a dedicated TargetMetrics history envelope in target_metrics_read.py. Do not reuse
HistoryListEnvelope, whose captures are pass-through mappings, and do not change
provider_history.py. Every Target Metrics model must use strict field validation and
extra="forbid".

OpenAPI describes the exact closed outer and all nested models. Descriptions/tests distinguish:

- Capture, Observation, and raw source counts;
- distinct-domain and raw-array grains while stating their admitted v1 cardinalities are
  equal and any inequality is integrity failure;
- provider_array_index from rank;
- internal_list_limit from completeness/truncation;
- structural zeros from empty measurement;
- admitted zero from admitted-empty;
- grouping context from Observation families;
- empty history from failure/never measured;
- has_more from pagination;
- Capture timestamps from unstated provider time axes.

Assert exact properties, required fields, additionalProperties closure, constants/enums,
nullability, bounds, descriptions, and query contracts. Malformed projection must not be
silently stripped, coerced, or normalized.

## Expected changed paths

Production:

- src/observatory/target_metrics_read.py
- src/observatory/api.py

Do not change src/observatory/provider_history.py.

Tests:

- tests/test_api_target_metrics.py
- tests/test_api_attempts.py only for bounded Attempt routing proof
- tests/test_provider_recipe_selection.py only for Target Metrics selection proof

Ticket:

- tickets/AI-12-target-metrics-read-history-api.md

Stop before any other production, test, schema, migration, authority, or ticket path.

## Required proof

Use only isolated synthetic Evidence and PostgreSQL.

Recipe/routing proof:

- selected/pinned Recipe;
- stable unselected 503 and pin 404s;
- exact canonical Recipe validation;
- provider Attempt routing;
- no automatic live selection.

Successful-history proof:

- frozen AI-09 projection;
- admitted zero metrics and empty domain list;
- below/equal/above internal list limit with no truncation claim;
- equal Observation/source counts for empty, below-limit, at-limit, and above-limit source
  arrays without a truncation claim;
- Unicode/whitespace exact domain preservation;
- grouping disagreement remains context;
- absent, JSON-null, and stated-empty states;
- exact typed envelope, deterministic ordering/list arithmetic, and empty 200.

Fail-closed proof:

- matching Evidence damage outside limit;
- missing/mismatched Attempt/Capture;
- request/provider/adapter disagreement;
- altered/missing Recipe;
- missing, extra, duplicate, or cross-linked database rows;
- wrong classification/count, including matching context paired with a non-admitted Outcome;
- raw source count either below or above typed source-domain cardinality;
- unknown kind or malformed projection;
- exact 409 with no partial envelope.

OpenAPI proof:

- exact route/query and closed schemas;
- constants, required fields, and substantive semantic descriptions;
- no Target Metrics Outcomes or Holdings route.

Distinguish frozen Evidence, claimed contract, and synthetic mutations. Mocks cannot be the
only Evidence/PostgreSQL proof.

## Implementation verification

GROK runs on the VPS:

1. targeted AI-12/API/selection tests;
2. Ruff;
3. mypy.

Do not run the full suite during ordinary implementation and do not test through the ChatGPT
MCP connector. After independent review/remediation, GPT gives CHAZ one exact-HEAD VPS block
for targeted tests, the full suite once, Ruff, mypy, and initial/final HEAD/tree checks.

## GROK implementation report

GROK may move Status only to review, never done. Report:

- exact commits, changed paths, targeted verification, final HEAD/tree, no amend/no push;
- strongest/weakest aspects, false greens, caller influence, coupling, parser/provider traps,
  blockers, and deferred work;
- later reuse versus surface-local behavior;
- Evidence versus claimed contract versus synthetic proof;
- safe/unsafe strategy and data-model implications;
- zero provider calls, credentials, spend, retry, continuation, live Evidence, operator
  PostgreSQL mutation, automatic selection, or F12/F13 work.

Do not bury Product questions in the report.

## Closure gate

Close only after GROK ticket review, GPT reconciliation/final-ticket commit, CHAZ
implementation authorization at that commit, GROK implementation commit without push, GPT
exact-diff review, remediation, CHAZ exact-HEAD operator verification, CHAZ closure
authorization, and GPT ticket-only closure commit. Do not repeat the suite after closure.

## Deferred

- Target Metrics Outcomes and Holdings
- scope filters, direct event links, and outer pagination beyond 100
- rebuildable Evidence-derived subject index
- nonempty optional grouping families and other Target Metrics surfaces
- shared writer/reader extraction
- strategy, scoring, recommendations, importance, cadence, or desired coverage
- F12 and F13

## Implementation report

**Start commit:** `2297aa2c464a8b851e01c70b6ed75cebb21e204a`  
**This commit** is the AI-12 implementation child. Status `review`, never `done`.  
**AI-12 only:** yes. Nothing amended. Nothing pushed.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`

### Changed paths

Production:

- `src/observatory/target_metrics_read.py` (new)
- `src/observatory/api.py`

Tests:

- `tests/test_api_target_metrics.py` (new)
- `tests/test_api_attempts.py` (bounded Target Metrics Attempt routing only)
- `tests/test_provider_recipe_selection.py` (bounded Target Metrics selection only)

Ticket: this file.

No parser, Recipe, derivation, schema, migration, or `provider_history.py` changes.

### Route and contract

Added `GET /v1/providers/dataforseo/google/ai-optimization/target-metrics/history`.

Query: required `requested_keyword` with FastAPI `min_length=1`; optional Recipe pin; `limit` 1–100 default 20; `order` asc/desc.

Dedicated `TargetMetricsHistoryEnvelope` with `extra="forbid"` and `strict=True` on every nested model. 12-key outer envelope via `history_list_response`. Nested Capture has the accepted 13 keys including `provider`, `adapter_contract`, and Recipe v1 `derivation_version_id`.

Recipe resolution: `resolve_provider_recipe` then v1-only identity
`b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104`. Other resolved identities are HTTP 404. Tampered/non-canonical v1 bytes are HTTP 409. Unselected without pin is HTTP 503. Pin of v1 does not require selection.

Membership loads `target_metrics_result_context` for the exact keyword and v1 Recipe **before** classification filtering. Missing or non-`observation_admitted` Capture Outcome is HTTP 409. Admitted Capture documents are verified against Evidence, Attempt parameters, singleton grouping context, envelope/typed completeness, and

`observation_count == 1 + len(source_domains) == 1 + sources_domain_count`

before sort/limit. Matching damage outside `limit=1` is 409 with no envelope keys.

`GET /v1/attempts/{attempt_id}` now routes Target Metrics Attempts through the existing generic provider reader.

### Verification

Targeted:

```
uv run pytest -q \
  tests/test_api_target_metrics.py \
  tests/test_api_attempts.py \
  tests/test_provider_recipe_selection.py
```

Result: **29 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

```
uv run ruff check .   # All checks passed
uv run mypy src       # Success: no issues found in 34 source files
```

Full suite was **not** run.

### Strongest

Recipe v1 freeze plus LEFT JOIN context-before-classification. Empty history cannot hide a planted `provider_error` context row. Cardinality equality is an integrity check, not a truncation story. Nested models are closed and strict, so `HistoryListEnvelope` pass-through cannot strip TM fields.

### Weakest

Context-without-Outcome remains mostly schema-blocked by the result-context FK; the LEFT JOIN is still there, but the HTTP proof is non-admitted classification rather than a true missing-row plant. Extra-envelope 409 uses a synthetic INSERT. OpenAPI assertions search component schemas for required phrases.

### Possible false greens

Helper envelope math is inside the route tests, not a substitute. Frozen AI-09 projection is real derived fixture bytes. Variant bodies (zero metrics, empty/below/above source lists, Unicode domain, grouping disagreement, field states) are synthetic mutations, not additional live Evidence. XOR-damaged Capture JSON proves verify-before-limit, not a legal Capture write path.

### Caller-controlled influence

Query `requested_keyword`, optional v1 pin, `limit` 1–100, `order`. Mutable Recipe selection in isolated test PostgreSQL only. No cursor, scope filter, or automatic selection.

### Architecture

Shared `history_list_response` and `resolve_provider_recipe` only. Recipe identity validation is local to the TM reader (not `load_validated_outcomes_recipe`) so history does not import Outcomes machinery. No generic history loader. Request mapping uses `validate_target_metrics_http_parameters` on verified Attempt parameters.

### Parser/provider traps

Structural `total_count`/`items_count` zeros are required on admitted documents and 409 if planted otherwise. Source-domain overlap is visible (mention sum 4415 ≠ total 3061) without a partition field. `internal_list_limit=10` with 3, 10, or 11 domains has no truncation flag. `provider_array_index` is lexical. Grouping metrics may disagree with total. No `observation_admitted_empty`.

### Closure blockers

Full suite not run. Steward independent review of this commit is required.

### Deferred

Unchanged: TM Outcomes and Holdings; pagination past 100; subject index; nonempty optional families; ChatGPT/other platforms; shared writer/reader extraction; F12/F13; Attempt-audit count hardening.

### Later reuse

v1-only resolved-Recipe identity check; context-before-classification 409; closed strict nested history envelope; cardinality equality as integrity, not completeness.

### Remain Target Metrics-local

Candidate SQL, request tuple (`internal_list_limit`, not Search Mentions limit/offset), grouping-as-context, two-kind projection, v1 classification set without admitted-empty.

### Evidence vs claimed contract vs synthetic

Evidence: AI-09 fixture 1775-byte Google Capture, 11 envelopes, 10 unique domains. Claimed contract: official Target Metrics aggregate shape (not re-fetched here). Recipe is the interpretation contract. Tests add synthetic zero/empty/limit/state/disagreement bodies and PostgreSQL plants.

### Strategy-LLM

Useful: keyword-level AI mention and AI-search-volume history for this closed Google request; exact domain strings in the returned histogram; change of those attributed numbers across Captures. Unsafe: empty history as never-measured or failed; structural zeros as corpus emptiness; domain index as rank; domain metrics as shares; list-limit saturation as completeness; grouping context as independent location/language/platform families; Attempt-audit as a fact document.

### Data-model

No schema change. Do not invent coverage rows. Do not treat `sources_domain_count != len(source_domains)` as a successful collapsed-duplicate document. Later Outcomes/Holdings should reuse Evidence subject extraction, not PostgreSQL context, for non-admitted activity.

### Hygiene

One implementation commit, no amend, no push. Zero provider calls, credentials, spend, retry, continuation, live Evidence activity, operator PostgreSQL mutation, automatic Recipe selection, or F12/F13 work. Working tree left clean after the commit.

## Remediation report addendum

**Remediation start commit:** `bed50a5c9b6b040ac3aeab0cf928d9556cf1d216`  
**This commit** is the AI-12 bounded remediation child. Status `review`, never `done`.

### Changed paths

- `src/observatory/target_metrics_read.py`
- `tests/test_api_target_metrics.py`
- `tickets/AI-12-target-metrics-read-history-api.md`

No `api.py`, parser, Recipe, derivation, schema, migration, Outcomes, or Holdings changes.

### Production behavior

- Every selected `observation_envelopes.attempt_id` must equal the verified/context Attempt ID. A valid cross-linked 64-hex Attempt ID is HTTP 409.
- Singleton location/language/platform `provider_array_index` must be 0. Ordered source-domain indexes must be exactly dense `0..n-1`. Disagreement is integrity failure without rerunning parse or Derivation.
- Optional-family `count` is required and nullable, with no default. `observation_kinds` is validated as the exact ordered v1 pair. Frozen request constants, structural zeros, and singleton grouping constants are Literal/const in the typed models. Malformed projection raises `IntegrityError` rather than coercing.

### Verification

Targeted suite **37 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy src       # Success: no issues found in 34 source files

Full suite was **not** run.

### Strongest

Cross-linked envelope Attempt ID is now a first-class 409. Dense lexical indexes are checked from persisted typed rows, not re-parsed arrays. OpenAPI now requires optional-family `count`.

### Weakest

Missing-count and wrong-`observation_kinds` 409s use monkeypatches of projection helpers, because a legal derive cannot emit those payloads. Missing envelope is planted by deleting a typed source-domain row and its parent envelope together (typed-table FK).

### Possible false greens

OpenAPI `const` vs `enum` helper accepts either. Dense-index plant uses `9 -> 11` on the AI-09 ten-row set. Monkeypatched projection tests do not prove that Derivation would produce those documents.

### Caller-controlled influence

Unchanged: `requested_keyword`, optional v1 pin, `limit` 1–100, `order`.

### Architecture

No reader/API redesign. No shared writer. Frozen request Literals document the closed adapter; they do not replace Attempt parameter validation.

### Parser/provider traps

None new. Index density is lexical completeness of the admitted array, not rank or truncation.

### Closure blockers

Full suite not run. Steward review of this remediation commit is required.

### Deferred

Unchanged.

### Hygiene

One remediation commit, no amend, no push. Zero provider calls, credentials, spend, continuation, live Evidence mutation, or F12/F13. Working tree left clean after the commit.

## Final tests-only proof correction

**Parent:** `919cf37f7f549dc9932b3118c0aed18b2c76ef6b`  
**This commit** is the AI-12 tests/ticket-only child. Status `review`, never `done`.

### Changed paths

- `tests/test_api_target_metrics.py`
- `tickets/AI-12-target-metrics-read-history-api.md`

No production, `api.py`, schema, Recipe, Derivation, Outcomes, or Holdings changes.

### Proofs added

OpenAPI now walks anyOf/oneOf leaves and asserts:

- query contract: required `requested_keyword` minLength 1; optional pin; limit default 20 min 1 max 100; order default `asc` enum `asc`/`desc`;
- outer provenance constants, `recipe_resolution` enum, count minima, limit 1–100, order enum;
- Capture/Observation hex-64 identity pattern and string bounds;
- `capture_outcome` classification constant and `observation_count` 1..IJSON_MAX;
- `search_scope` item const `"answer"`;
- exact `items_state` and optional-family state enums;
- required nullable family `count` with integer 0..IJSON_MAX bounds on the integer branch;
- metric and variable `provider_array_index` bounds;
- total/source `observation_kind` constants plus structural-zero and singleton constants.

Parameterized PostgreSQL UPDATEs of `observation_envelopes.provider` and `adapter_contract` each return exact HTTP 409 with no history-envelope keys. The Evidence `read_capture` monkeypatch remains as a second, non-relational proof.

### Verification

Targeted suite **39 passed**, 1 warning (known Starlette/`httpx` TestClient deprecation).

    uv run ruff check .   # All checks passed
    uv run mypy src       # Success: no issues found in 34 source files

Full suite was **not** run.

### Candid notes

Strongest: envelope provider/adapter 409 is now a real PostgreSQL plant, not only a monkeypatch. OpenAPI enum/const/bounds checks inspect branch values.

Weakest: OpenAPI helpers still accept either `const` or single-value `enum` because FastAPI emits both. Outer `total_matching`/`returned_count` assert minimum 0 only; the models do not declare an IJSON maximum.

Possible false greens: the parameterized SQL plants every envelope row for the Capture; one disagreeing row is enough for 409. Query-parameter `required` absence is treated as optional.

No production change. No amend. No push. Zero provider/Evidence/F12/F13 activity.

## Closure

CHAZ explicitly authorized closure after the accepted implementation and both bounded
remediation reviews settled. GPT independently reviewed the exact parent/child comparisons
through LinuxVedaOpsMCP.

Accepted implementation lineage:

- start boundary: `2297aa2c464a8b851e01c70b6ed75cebb21e204a`;
- implementation: `bed50a5c9b6b040ac3aeab0cf928d9556cf1d216`;
- bounded remediation: `919cf37f7f549dc9932b3118c0aed18b2c76ef6b`;
- final tests-only proof correction and operator-verified HEAD:
  `dcf77b7ecd2b8c6c44f02cb5af9fab02869f491c`.

CHAZ's exact-HEAD VPS operator verification:

- initial exact-HEAD and clean-tree guards passed;
- targeted AI-12/API/selection suite: **39 passed**, 1 warning;
- full suite, run once: **1271 passed, 1 skipped**, 1 warning;
- Ruff: passed;
- mypy: passed with 34 source files;
- final HEAD: exact `dcf77b7ecd2b8c6c44f02cb5af9fab02869f491c`;
- final tree: clean.

The warning is the known Starlette/`httpx` TestClient deprecation and is accepted as
non-blocking. This closure changes only this ticket. Per the accepted workflow, tests are not
repeated after the ticket-only closure commit.

No provider calls, credentials, spend, continuation, live Evidence mutation, automatic Recipe
selection, F12, or F13 activity occurred. AI-12 is closed without adding Target Metrics
Outcomes or Holdings.
