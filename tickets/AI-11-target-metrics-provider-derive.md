# AI-11 — Target Metrics provider Derivation and typed persistence

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; mandatory GROK technical review reconciled  
**Approved by:** [CHAZ] for final ticket publication / [GPT] Steward reconciliation  
**Technical-review base:** cd276059b98553cf74d24013e55e468763a9b762  
**Implementation start:** `b8998eedb06e713ee2f0922316949658c22a33c1`  

## Purpose

Implement the first content-addressed Target Metrics Derivation Recipe, semantic Observation
identities, typed PostgreSQL persistence, and deterministic rebuild proof for the exact
closed adapter:

    dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1

This is the persistence half of the Target Metrics vertical slice. AI-12 remains a separate
recipe-selection and read/history API ticket. AI-11 authorizes no provider exchange, new
Evidence, recurring acquisition, API, strategy, scoring, reporting, second platform, or
cross-surface projection.

GROK performed the required read-only pre-implementation review at the technical-review
base, verified the frozen fixture independently, and returned RECONCILE. The Steward checked
the findings against AI-09, AI-10, D11, and current code and accepts the reconciled two-kind
model and rules below. This ticket, not the provisional draft, is implementation authority.

## Authority and accepted foundation

- VISION data doctrine and survival requirement
- VOCABULARY definitions of Evidence, Outcome, Observation, Derivation, Derivation Recipe,
  Provider Update Time, Data Period, and Conformance fixture
- D11 recipe-addressed typed provider Derivation
- D12 bounded claimed-contract plus real-Evidence interpretation
- D13 bounded measurement-family direction
- Capture Event v2, Provider Derivation after F11
- PF-04 provider Recipe, generic envelope, typed-detail, and writer substrate
- PF-12 typed-detail and complete-set precedent
- PF-14 provider read-integrity precedent
- PF-15 additive PostgreSQL migration hygiene
- AI-05 Search Mentions derivation precedent
- AI-08 closed Target Metrics acquisition gate
- AI-09 verified Evidence, scrub, off-host snapshot, restore proof, and accepted data review
- AI-10 strict parser, typed IR, frozen Conformance fixture, and mandatory AI-11 guards

AI-10 closed at Steward commit cd276059b98553cf74d24013e55e468763a9b762.

Fixed fixture identity:

- path: tests/fixtures/dataforseo_ai_optimization_target_metrics_ai09.json
- bytes: 1775
- SHA-256: 7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2
- no BOM and no trailing newline
- one required total aggregate
- one location row, one language row, and one platform row
- ten unique source-domain rows
- three present-empty optional grouping families
- present-empty items
- total_count, offset, and items_count all zero

One Google body proves existence, not invariance. It proves no stable order, tie-break,
partition, truncation, completeness, cross-platform behavior, independently queryable
location/language/platform slices, time series, provider Data Period, Provider Update Time,
cross-surface identity, or billing formula. Nonempty optional families, items JSON null,
above-limit source rows, grouping disagreement, and zero metrics remain synthetic parser
coverage rather than live Google testimony.

## Technical-review reconciliation

The final model has exactly two Observation kinds, three Target Metrics relations, and
eleven frozen-fixture envelopes:

- total and source-domain aggregates are provider-native facts;
- location, language, and platform groupings are typed result context, not Observation
  families;
- provider echo and task path remain typed IR and Evidence testimony, not admission
  authority;
- source-domain row count above internal_list_limit remains admissible testimony, not a
  truncation or completeness claim;
- exact singleton grouping cardinality and keys must reconcile to the verified Attempt;
- nonempty optional grouping families remain unsupported in Recipe v1 and fail closed;
- the Recipe never emits observation_admitted_empty;
- production derivation revalidates the exact Capture-cited Attempt before parsing;
- PRE_AI11_SCHEMA_STATEMENTS freezes the pre-AI-11 migration layer;
- parser success/failure behavior remains unchanged.

The provisional five-kind model is rejected. Under the closed Google/United States/English
request, the three grouping arrays are request-constrained restatements. One agreeing body
does not prove a useful independent location/language/platform fact grain. Persisting them
as first-class Observations would teach AI-12 and later strategy consumers a false query
surface. Their exact independently stated metrics remain recoverable in typed context.

The provisional echo/path and above-limit rejection rules are also rejected. The verified
Attempt is request authority. Echo/path disagreement remains inspectable in raw Evidence and
typed IR but neither overrides Attempt context nor rejects an otherwise reconciled result.
Returning more source-domain rows than the requested internal list limit remains exact
provider testimony; Observatory stores the row count and limit without inventing rank,
truncation, completeness, share, or partition semantics.

## Boundary

AI-11 may add:

- one content-addressed closed Target Metrics Derivation Recipe;
- Recipe, kind, provider, and parser-contract constants in the existing Target Metrics
  parser module;
- one dedicated Target Metrics derive module and local module entrypoint;
- three additive typed PostgreSQL relations and their constraints;
- one named pre-AI-11 schema statement layer;
- bounded migration-baseline adjustments to the existing Search Mentions derive test;
- zero-network real-PostgreSQL tests over the frozen fixture and synthetic mutations.

AI-11 must not add:

- provider transport, DNS, credentials, spend, another Evidence root, retry, continuation,
  or another request;
- Target Metrics parser admission changes;
- recipe selection or a current-pointer mutation;
- Attempt/read/history API behavior;
- strategy, shares, concentration, scoring, recommendations, or reporting;
- domain normalization, Page or Brand identity, cross-surface joins, or a universal metric;
- optional-family Observation kinds;
- a generic provider-derive framework or unrelated migration/parser refactor;
- Evidence mutation or PostgreSQL authority over raw bodies;
- F13 remediation of older gates.

## Verified production boundary

Production derive_target_metrics must require type(store) is EvidenceStore and use this
authority chain:

1. verify-on-read one committed Capture;
2. require the Target Metrics adapter contract on that Capture;
3. obtain the exact Attempt ID cited by the Capture;
4. verify-on-read that exact committed Attempt;
5. require the same Target Metrics adapter contract on the cited Attempt;
6. require committed parameters and run validate_target_metrics_http_parameters over them;
7. verify a complete Capture body through EvidenceStore.read_capture_body;
8. pass only the validator-returned closed parameters and verified body to
   parse_target_metrics.

Validator DocumentError, non-Mapping parameters, adapter mismatch on the cited Attempt,
missing citation, or Attempt/Capture/body integrity failure is an integrity failure and
produces no Capture-stage provider rows. Do not silently skip an invalid parameter document
without incrementing the summary's integrity-failure count.

A plan_target_metrics_capture function may remain a bounded test/planning seam. It is not
production authority. Production derivation must never construct request or provenance
context from:

- task.data echo;
- operator flags;
- API query parameters;
- an arbitrary Mapping;
- a test helper;
- another Target Metrics Attempt.

Tests must place two valid Target Metrics Attempts in one store, cite Attempt A from the
Capture, and prove Attempt B cannot influence persisted subject or context.

## Recipe contract

Add one closed canonical I-JSON Recipe through the accepted provider_recipe substrate.
Its derivation_version_id is SHA-256 of exact RFC 8785/JCS Recipe bytes. Publish final byte
length and digest and prove independent recomputation.

The Recipe fixes:

- provider: dataforseo;
- exact Target Metrics adapter contract;
- parser contract:
  dataforseo-ai-optimization-target-metrics-live-parser-v1;
- exact verified Attempt parameters as request authority;
- task.data and task.path as non-authoritative typed Evidence/IR testimony;
- closed objects and no extension-permitted objects in version 1;
- exact integer semantics with I-JSON-safe persistence;
- Decimal provider cost in parser IR/Evidence only;
- one-task/one-result structural rules already closed by AI-10;
- exact grouping reconciliation below;
- explicit field-state behavior;
- two exact Observation kinds and identities;
- no provider Data Period or Provider Update Time;
- the closed Capture Outcome taxonomy;
- exact-content and complete-set write behavior.

Any change to those semantics requires different Recipe bytes and identity. Do not change
AI-10 parser admission to implement Recipe policy.

## Outcome and failure behavior

Attempt-stage classification remains:

    authorized_unresolved

The Recipe's Capture-stage taxonomy is exactly:

- no_response
- response_partial
- transport_complete_non_admissible
- provider_error
- provider_envelope_rejected
- reconciliation_failed
- observation_admitted

The Recipe does not list or emit observation_admitted_empty.

Repository Outcome is created only by the Recipe after verified transport, parsing,
reconciliation, and admission. Never assign a repository classification from
TargetMetricsIR.outcome.value.

Classification rules:

- no_response, response_partial, and non-admissible complete transport use their existing
  transport classifications;
- TargetMetricsParseError produces provider_envelope_rejected;
- ParseClassification.PROVIDER_ERROR produces provider_error with no context, generic
  envelopes, typed facts, or normal diagnostics;
- exact singleton grouping-cardinality or grouping-key disagreement produces
  reconciliation_failed;
- empty semantic identity text, nonempty optional families, I-JSON overflow, or conflicting
  same-identity content produces provider_envelope_rejected;
- a structurally valid required total, including zero, produces observation_admitted after
  the other Recipe checks succeed.

Error-path result_count is unreconciled provider testimony, not valid topology. Never admit
Observations or context from a provider-error IR and do not inspect an error result for
hidden aggregates.

No normal Target Metrics rows survive a whole-unit semantic disagreement. Rejected or failed
units write only the appropriate Capture Outcome with observation_count zero. Result context
is written only for observation_admitted.

## Request/result reconciliation

After successful parsing, Recipe v1 requires:

- aggregated_metrics.location has exactly one row;
- that location key exactly equals the verified Attempt location_code;
- aggregated_metrics.language has exactly one row;
- that language key exactly equals the verified Attempt language_code;
- aggregated_metrics.platform has exactly one row;
- that platform key exactly equals the verified Attempt platform.

Missing, empty, extra, or disagreeing rows produce reconciliation_failed with zero context
and zero Observations. This rule remains Recipe/plan logic after parsing; do not move it into
AI-10 parser admission.

Location, language, platform, and total values need not agree. Persist all four independently
stated metric pairs. Disagreement remains valid testimony rather than a rejection invariant.

Echo target values, echo api/function, and task path do not override verified Attempt
parameters, do not become identity, are not persisted, and do not fail admission. They
remain available in verified Evidence and typed IR.

sources_domain rows remain admissible when their count is below, equal to, or above
internal_list_limit. Persist the exact request limit and returned row count. Do not derive or
store truncated, complete, rank, share, concentration, or partition flags. Domain metric
sums may exceed the total and remain valid.

For search_results_domain, brand_entities_title, and brand_entities_category:

- absent, JSON null, and stated-empty are admissible and distinct;
- stated-nonempty is provider_envelope_rejected in Recipe v1;
- no optional-family Observation kind or row relation is added.

For items, AI-10 parser already admits absent, JSON null, and stated-empty and rejects
nonempty. Preserve the three admissible states distinctly in result context.

## Observation families

The accepted model has exactly two semantic families.

### 1. Target Metrics total

Kind:

    dataforseo.google.ai_optimization.target_metrics.total.v1

Semantic identity axis:

- exact requested keyword from the verified Attempt.

The requested keyword must be a nonempty exact string after Attempt revalidation. Persist:

- exact requested keyword;
- exact nonnegative mentions;
- exact nonnegative ai_search_volume.

Zero is stated testimony. A zero total emits one normal total Observation and never
observation_admitted_empty.

Platform, location, language, match type, search filter, search scope, and list limit remain
closed request/result context rather than within-Capture identity axes.

### 2. Target Metrics source domain

Kind:

    dataforseo.google.ai_optimization.target_metrics.source_domain.v1

Semantic identity axes:

- exact requested keyword from the verified Attempt;
- exact raw provider domain key.

Both axes must be nonempty exact strings. Whitespace and Unicode remain exact testimony.
No hostname normalization, www collapse, brand/entity resolution, Page identity, or join to
Search Mentions source.v1.

Persist:

- exact requested keyword;
- exact raw provider domain key;
- exact nonnegative mentions;
- exact nonnegative ai_search_volume;
- provider_array_index as nonnegative lexical/order testimony.

provider_array_index is content, never semantic identity or rank. Reordering source-domain
rows must preserve the semantic identity set while changing the exact per-identity stored
index map. Comparing only range(count) is an inadequate reorder proof.

AI-10 rejects duplicate grouping keys. Duplicate domain keys are collisions, not occurrences.
Add no occurrence relation. Same semantic identity with conflicting intended content rejects
the whole Capture-stage unit.

## Frozen-Capture cardinality

The accepted AI-09 fixture emits:

| Kind | Semantic envelopes |
|---|---:|
| Target Metrics total | 1 |
| Source domain | 10 |
| **Total / Outcome observation_count** | **11** |

There is exactly one result-context row. Context and lexical array indexes do not add to
observation_count.

Tests must compute the count as one required total plus len(sources_domain), then independently
compare per-kind and stored envelope counts. Eleven is a frozen-Capture consequence, not a
provider invariant.

## Capture result context

Persist exactly one target_metrics_result_context row per admitted Capture and Recipe,
structurally bound to the exact Capture Outcome by derivation_version_id, attempt_id, and
capture_id.

Typed context includes:

- requested keyword, match_type, search_filter, and search_scope;
- verified Attempt platform, location_code, language_code, and internal_list_limit;
- result total_count, offset, and items_count;
- items_state as stated, json_null, or absent;
- location key, mentions, ai_search_volume, provider_array_index, and row count;
- language key, mentions, ai_search_volume, provider_array_index, and row count;
- platform key, mentions, ai_search_volume, provider_array_index, and row count;
- sources_domain_count;
- search_results_domain_state and nullable row count;
- brand_entities_title_state and nullable row count;
- brand_entities_category_state and nullable row count.

The three required grouping structures are NOT NULL context on admitted units. Singleton
cardinality is a Recipe rule, not a table-level constant that would prevent a second Recipe
from coexisting in these relations.

Optional-family row count is zero when state is stated-empty and SQL NULL when state is
absent or json_null. Enforce state/count consistency with the existing field-state helper
pattern. items is state-only because its successful structural count is separately fixed at
zero by the parser.

Provider root/task version, messages, durations, costs, task ID, path, and echo remain typed
parser IR and raw Evidence only. Do not duplicate them into PostgreSQL or add JSONB.

## Time and numeric rules

- Capture/acquisition time remains Evidence provenance.
- Target Metrics states no provider Data Period in the AI-09 body.
- Target Metrics states no Provider Update Time in the AI-09 body.
- Provider-unstated time remains unstated and never inherits Capture or sibling time.
- Provider duration strings are durations, not timestamps.
- Provider cost remains Decimal IR/Evidence testimony and is not persisted by AI-11.

Before persistence, every provider metric, numeric grouping key, structural count, and
provider_array_index must fit the accepted I-JSON integer range
0..9007199254740991. Overflow rejects the whole Capture-stage unit as
provider_envelope_rejected. PostgreSQL must independently reject planted negative or overflow
values.

Use BIGINT for these values. Use no NUMERIC because AI-11 persists no decimal provider value.

## Schema and provenance requirements

Use existing provider_recipes, outcomes, observation_envelopes, and
derivation_diagnostics. Add exactly:

- target_metrics_totals
- target_metrics_source_domains
- target_metrics_result_context

Both fact relations carry capture_id, derivation_version_id, within_capture_identity, and
exact observation_kind and are structurally bound to the matching generic envelope through
the accepted candidate key.

Require:

- kind CHECK constraints on each fact table;
- nonempty keyword and source-domain checks;
- BIGINT bounds on metrics and provider_array_index;
- a Recipe-scoped unique lexical index for source domains that does not make index semantic
  identity;
- context foreign key to the full matching Outcome identity;
- field-state/count consistency checks;
- no JSONB, EAV, generic dimension relation, or occurrence relation.

Define:

    PRE_AI11_SCHEMA_STATEMENTS = current SCHEMA_STATEMENTS
    SCHEMA_STATEMENTS = PRE_AI11_SCHEMA_STATEMENTS + Target Metrics statements

Preserve PRE_AI05_SCHEMA_STATEMENTS and PRE_PF12_SCHEMA_STATEMENTS unchanged. Adjust the
Search Mentions migration test so its seven-table layer is measured against
PRE_AI11_SCHEMA_STATEMENTS rather than absorbing Target Metrics DDL into the AI-05 layer.
Organic migration tests require no edit.

Migration must be additive over a representative populated current schema containing fixture,
Keyword Overview, Google Organic, and Search Mentions rows; preserve those rows; be
idempotent; and prove fresh/upgraded bounded-catalog parity. Same-named decoy constraints on
other relations must not suppress required Target Metrics constraints. Use relation-scoped
conrelid plus conname probes only if an existing relation is altered; this ticket should not
need such an alteration.

## Atomic and complete-set behavior

One Capture/Recipe unit includes:

- exactly one intended Capture Outcome;
- one result-context row when admitted;
- all generic envelopes;
- all total and source-domain typed rows;
- all intended diagnostics.

Same Recipe plus same verified Evidence is content-consistent:

- compare intended and stored natural-identity rows exactly;
- restore a missing rebuildable planned row only when the final stored set becomes exact;
- reject content disagreement;
- reject extra rows and planted diagnostics;
- reject foreign-Attempt or extra Outcomes;
- reject wrong observation_count;
- reject incomplete context, envelope, typed-detail, or diagnostic sets;
- require observation_count to equal both planned and stored envelope counts;
- never use ON CONFLICT DO NOTHING or last-write-wins as semantic equality.

Complete-set comparison is scoped by capture_id and derivation_version_id and includes
attempt_id on Outcomes. A second Target Metrics Recipe for the same Capture must coexist
under its own Outcome, context, envelopes, and facts. Each Recipe's comparison must ignore
the other Recipe's rows.

Two fresh PostgreSQL databases rebuilt from identical verified Evidence and Recipe must be
logically equivalent across every AI-11 column. Use a catalog-driven full-column projection,
not a selected thin subset. Independently prove exact frozen IR-to-row projection for every
explicit context and fact column.

Do not extract a shared provider writer in AI-11. This is the fourth surface-local provider
writer, so AI-05's extraction trigger has fired as a later Steward design question. Record
the repeated writer/complete-set cluster in the implementation report. A later bounded
ticket may consider extraction only if the fourth copy is clean and can avoid leaking
Search Mentions occurrence/emptiness rules or Target Metrics reconciliation rules into a
generic kernel.

## Required adversarial proofs

At minimum, implementation must prove on real PostgreSQL:

- canonical Recipe bytes, byte length, digest, and independent recomputation;
- frozen fixture remains exactly 1775 bytes with the accepted digest;
- exact frozen total and ten domain metric vectors;
- exact eleven envelopes, per-kind counts, and one result context;
- eleven is recomputed as one plus len(sources_domain);
- exact request, result, grouping, and field-state context projection;
- zero total and zero domain values remain stated and observation_admitted;
- no Search Mentions zero-envelope or observation_admitted_empty rewrite;
- grouping metric disagreement with total remains admitted and independently stored;
- source-domain overlap and sums above total remain admitted;
- source count below, equal to, and above limit remains admitted without any truncation,
  completeness, share, or rank field;
- exact singleton grouping-key match succeeds;
- empty, extra, or disagreeing location/language/platform rows produce
  reconciliation_failed after parsing;
- echo and task-path disagreement neither overrides Attempt context nor rejects admission;
- absent, json_null, and stated-empty optional states persist distinctly;
- stated-nonempty optional families reject the whole unit with no context or facts;
- absent, json_null, and stated-empty items states persist distinctly;
- provider error, including unusual result_count or result shape, emits no context or facts;
- parser rejection, partial/no-response, complete non-admissible transport, and Evidence
  damage produce exact closed behavior;
- two Attempts in one store prove the Capture-cited Attempt exclusively controls production
  derivation;
- validator failure, non-Mapping parameters, adapter mismatch, and cited-Evidence damage
  increment integrity failures and emit no Capture-stage rows;
- empty keyword/domain identity and I-JSON overflow reject the whole unit;
- source reorder preserves semantic identity while changing the exact per-identity lexical
  index map;
- wrong-kind detail, orphan detail, duplicate lexical index, invalid metric/index,
  inconsistent state/count, and context without matching Outcome are rejected by PostgreSQL;
- exact-content rerun, missing-row repair, planted extra rows, planted extra diagnostic,
  content conflict, wrong observation_count, and foreign-Attempt behavior;
- a second Target Metrics Recipe coexists for the same Capture;
- populated-current-schema upgrade preserves every previous surface;
- fresh versus upgraded bounded-catalog parity;
- two-database logical equivalence over every new column;
- existing fixture, Keyword Overview, Organic, Search Mentions, AI-10 parser behavior,
  Recipes, tables, and frozen fixture identities remain unchanged;
- ordinary tests perform no provider, DNS, credential, paid-gate, operator-Evidence-root, or
  other public-network activity.

Tests must not claim that a socket.create_connection guard proves all possible DNS/network
absence. It remains a bounded regression guard consistent with existing parser tests.

## Implementation path allowlist

The implementation assignment may change only:

- tickets/AI-11-target-metrics-provider-derive.md
- src/observatory/dataforseo_ai_optimization_target_metrics.py
- src/observatory/target_metrics_derive.py
- src/observatory/migrate.py
- tests/test_dataforseo_ai_optimization_target_metrics_derive.py
- tests/test_dataforseo_ai_optimization_search_mentions_derive.py

The Search Mentions test change is limited to preserving its migration-layer baseline after
PRE_AI11_SCHEMA_STATEMENTS is added. If any additional path is required, stop and ask the
Steward. Do not modify capture_event.py, AI-10 parser tests, Organic tests, selection, API,
or AGENTS.md.

AGENTS.md entrypoint publication is a Steward-owned closure follow-up after accepted
implementation:

    uv run python -m observatory.target_metrics_derive

## Implementer workflow

Implementation begins only from the exact clean accepted-ticket commit named by the Steward.

Before writing, GROK must load and report the absolute paths of:

- /home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md
- /home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md
- /home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md
- /home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md

GROK is the sole writer of src/ and tests/. Work test-first. Create one implementation
commit, do not amend, do not push, and leave the ticket at review with an implementation
report. Do not run or inspect the operator AI-09 Evidence root; ordinary work uses only the
committed fixture and synthetic mutations.

Targeted command:

    uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py

GROK may run bounded targeted tests during implementation. The final full suite, Ruff, and
mypy evidence must identify the exact implementation HEAD. Because the suite is long, [CHAZ]
normally runs the final exact-HEAD operator block over SSH once at the correct review point.

## Implementer report required

The implementation report must record:

- exact parent and child commits and final clean status;
- exact changed paths;
- final Recipe byte length and digest with independent recomputation;
- unchanged fixture byte length and digest;
- acceptance-to-test mapping;
- exact targeted/full pytest, Ruff, and mypy commands and results available at handoff;
- real-PostgreSQL and two-database proof boundaries;
- strongest proof and weakest assumption;
- possible false greens and remaining caller-controlled influence;
- architecture drift, coupling, parser/provider traps, and deliberately duplicated seams;
- any closure blocker or under-proved branch;
- the exact repeated writer/complete-set cluster and whether later extraction now appears
  safe or dangerous;
- what later surfaces should reuse and what must deliberately remain duplicated;
- confirmation of no provider/network/credential/spend/Evidence mutation, no AI-12/API/
  strategy/F13 work, no amend, and no push.

As coworker judgement for the future strategy layer, also report:

- what the persisted total and source-domain facts are genuinely useful for;
- what is not safely inferable from them;
- whether the actual schema helps or harms later trend, competitor, citation-gap, and
  cross-surface analysis;
- any data-model awkwardness discovered during implementation;
- clear separation of verified Evidence, provider claimed contract, synthetic proof,
  recommendation, and unproven inference.

Ask the Steward direct bounded questions when implementation context could materially improve
a decision. Do not broaden implementation to answer adjacent questions.

## Explicit non-goals

- another provider exchange, Evidence root, inspector mutation, or Evidence rewrite;
- ChatGPT, another platform, another target, another list-limit Capture, Multi-Target,
  Historical, Timeseries, top-list, Lite, catalog, account, or User Data request;
- AI-12 selection/read/history API;
- domain normalization, brand/entity consolidation, Page identity, shares, concentration,
  ranking, scoring, recommendations, reporting, or strategy;
- recurring capture, scheduler, routine F6 automation, F7 locking, or F12 orchestration;
- F13 remediation of older transport-capability gates;
- a shared provider-derive framework;
- refactoring existing provider parsers or writers.

## Next boundary

After accepted implementation, independent Steward review, remediation if required,
exact-HEAD test evidence, and explicit [CHAZ] closure authorization:

1. AI-12 — Target Metrics recipe selection and read/history API;
2. a separately bounded Steward design question on the now-fired fourth-writer extraction
   trigger.

AI-11 authorizes neither boundary.

## Implementation report

**Parent:** `b8998eedb06e713ee2f0922316949658c22a33c1`  
**Child:** this implementation commit  
**Status:** `review`  
**AI-11 only:** yes. Nothing pushed. Nothing amended.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_ai_optimization_target_metrics.py` (kind, provider, parser-contract constants only)
- `src/observatory/target_metrics_derive.py` (Recipe, derive module, local entrypoint)
- `src/observatory/migrate.py` (`PRE_AI11_SCHEMA_STATEMENTS` plus three Target Metrics relations)
- `tests/test_dataforseo_ai_optimization_target_metrics_derive.py` (new)
- `tests/test_dataforseo_ai_optimization_search_mentions_derive.py` (Mentions seven-table layer measured against `PRE_AI11_SCHEMA_STATEMENTS`)
- this ticket (Implementation start, Status, Implementation report)

Recipe document lives in the derive module, not the parser module. AI-10
`test_nonempty_optional_rows_are_typed_ir_not_persistence` forbids the substring
`provider_recipe` in the parser source. Putting Recipe registration there would
require editing an AI-10 test, which this ticket forbids. Kinds, provider, and
parser-contract constants remain in the parser module. Parser admission is
unchanged.

### Recipe and fixture identities

Target Metrics Recipe:

- byte length `1586`
- `derivation_version_id`
  `b6addc49c60eff18de7aaf5dc6c35ebffa93e242649d5e2ddd009822b12e5104`

Independent recomputation is
`hashlib.sha256(TARGET_METRICS_RECIPE_BYTES).hexdigest()` and
`recipe_derivation_version_id(target_metrics_recipe())`.

Frozen AI-09 fixture unchanged:

- path `tests/fixtures/dataforseo_ai_optimization_target_metrics_ai09.json`
- bytes `1775`
- SHA-256 `7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`
- no BOM, no trailing newline

Kinds:

- `dataforseo.google.ai_optimization.target_metrics.total.v1`
- `dataforseo.google.ai_optimization.target_metrics.source_domain.v1`

Relations:

- `target_metrics_totals`
- `target_metrics_source_domains`
- `target_metrics_result_context`

Frozen Capture cardinality: 1 total + 10 source domains = **11**; one result context.
`observation_count` is recomputed as `1 + len(sources_domain)`.

### Acceptance-to-test mapping

| Acceptance | Test |
|---|---|
| Recipe bytes/digest, fixture/KO/Organic/SM identities | `test_accepted_recipe_and_fixture_identities_remain_unchanged` |
| Frozen 11 = 1 + len(sources_domain), metric vectors, overlap, context | `test_plan_frozen_fixture_has_exact_semantic_counts`, `test_derive_ai09_fixture_into_real_postgres` |
| Never copy `parsed.outcome.value` | `test_plan_does_not_copy_parser_outcome_value` |
| Grouping value ≠ total admitted | `test_plan_grouping_disagreement_with_total_is_admitted` |
| Echo/path do not reject; Attempt remains authority | `test_plan_echo_and_path_disagreement_do_not_reject`, `test_adversarial_bodies_persist_on_postgres` |
| Source count below/equal/above limit, no truncation | `test_plan_source_count_below_equal_above_limit_is_admitted`, `test_adversarial_bodies_persist_on_postgres` |
| Empty/extra/wrong grouping keys | `test_plan_empty_extra_or_wrong_grouping_is_reconciliation_failed` |
| Nonempty optional families | `test_plan_nonempty_optional_family_rejects_whole_unit`, `test_adversarial_bodies_persist_on_postgres` |
| Concrete EvidenceStore type guard | `test_derive_rejects_non_concrete_store_before_schema_or_evidence` |
| Empty identity / I-JSON overflow | `test_plan_empty_identity_and_ijson_overflow_reject` |
| Zero total admitted, not admitted_empty | `test_plan_zero_total_remains_admitted`, `test_zero_total_writes_admitted_outcome` |
| Optional and items field states | `test_plan_optional_and_items_states_are_distinct`, `test_adversarial_bodies_persist_on_postgres` |
| Source reorder per-identity index map | `test_plan_source_reorder_preserves_identity_and_changes_index_map` |
| Zero domain values persist | `test_adversarial_bodies_persist_on_postgres` |
| Wrong-kind, orphan, lexical unique, I-JSON, empty identity, state/count | `test_constraints_reject_wrong_kind_orphan_index_and_state` |
| Context Outcome FK | `test_result_context_requires_matching_outcome` |
| Transport/parse/reconciliation/error/damage | `test_transport_parse_reconciliation_and_damage_paths` |
| Cited Attempt A, sibling Attempt B unused | `test_production_uses_cited_attempt_not_sibling` |
| Validator/non-Mapping/adapter mismatch integrity | `test_validator_non_mapping_and_adapter_mismatch_are_integrity_failures` |
| Exact-content, extra, missing restore, foreign Attempt | `test_exact_content_extra_rows_missing_restore_and_foreign_attempt` |
| Wrong observation_count, extra diagnostic | `test_wrong_outcome_count_and_extra_diagnostic_fail_closed` |
| Second Recipe coexistence | `test_second_recipe_coexists_for_the_same_capture` |
| Populated current-schema upgrade | `test_populated_current_schema_then_target_metrics_derive` |
| Fresh vs upgraded catalog | `test_fresh_and_upgraded_target_metrics_catalog_match` |
| Same-named decoy constraints | `test_same_named_decoy_does_not_suppress_target_constraints` |
| Two-database full-column equivalence | `test_two_databases_are_logically_equivalent` |
| Fixture derive skip | `test_fixture_derive_skips_target_metrics_and_target_metrics_skips_fixture` |

### Validation

Targeted at implementation child `b30b69f596800af36bcf85cc638bbf217bc21965`:

```
uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py
28 passed in 15.43s
```

Final exact-tree:

```
uv run pytest -q
1192 passed, 1 skipped, 1 warning in 309.52s
```

Warning: Starlette/`httpx` TestClient deprecation from
`.venv/lib/python3.12/site-packages/fastapi/testclient.py`, not this ticket.

```
uv run ruff check .
All checks passed!
```

```
uv run mypy
Success: no issues found in 62 source files
```

Leftover `observatory-ce05-*` containers: none checked as none were created.

### Real-PostgreSQL proofs

- Frozen IR-to-row projection of every explicit column on all three AI-11 relations.
- Catalog-driven two-database `SELECT` of every new column.
- Populated PRE_AI11 upgrade preserves fixture, Keyword Overview, Organic, and Search Mentions rows, then derives 11 Target Metrics envelopes.
- Complete-set: exact rerun, missing source-domain restore, planted extra envelope, content conflict, foreign-Attempt Outcome, corrupted `observation_count`, planted diagnostic.
- Second Recipe coexistence on the same Capture.
- Production two-Attempt store: persisted subject is Capture-cited Attempt A.
- Integrity failures for validator DocumentError, non-Mapping parameters, adapter mismatch, and damaged body: no Capture-stage rows.

### Candid technical assessment

**Strongest proof:** frozen 11 recomputed as `1 + len(sources_domain)` plus IR-to-row projection of grouping context metrics, field states, and source-domain lexical indexes; grouping-key mismatch parses as AI-10 `observation_admitted` IR and becomes `reconciliation_failed` with zero context; sibling Attempt B cannot become production authority.

**Weakest assumption:** complete-set typed-detail compare is still identity-set plus count, with content equality only in `_write_closed_row` (same PF-12/AI-05 shape). Two-database snapshot uses catalog column order rather than `SELECT *` system columns. Duplicate source-domain identity never occurs in the parser, so plan-level same-identity conflict is defense in depth. Validator/non-Mapping/adapter mismatch proofs monkeypatch `read_attempt` after a real commit because constructors cannot emit those documents.

**Possible false greens:**

- Isolation of AI-10 parser still hashes module source for `provider_recipe`; that is why Recipe is not in the parser module.
- `socket.create_connection` guard does not prove all DNS absence.
- Reorder proof compares per-identity index maps, not `range(n)` alone.
- Echo/path persist test mutates IR-visible echo while Attempt parameters stay closed; it does not prove a live provider would emit that pair.

**Remaining caller-controlled influence:**

- `plan_target_metrics_capture` still accepts a Mapping; it is the test/planning seam, not production. Production `derive_target_metrics` revalidates the Capture-cited Attempt through `validate_target_metrics_http_parameters`.
- `type(store) is EvidenceStore` still allows monkeypatching instance methods in-process.
- `_exchange`-style transport influence is out of this ticket.

**Architecture drift / coupling:**

- Fourth surface-local copy of `_write_closed_row` / `_assert_complete_set` / `_write_outcome`.
- Kind strings duplicated in parser constants and `migrate.py`, matching Organic/Mentions.
- Small reuse: `Field` / `ParseClassification`, `validate_target_metrics_http_parameters`, generic envelopes.
- No shared writer kernel. No JSONB/EAV/occurrence tables. No parser admission change.

**Parser/provider traps handled:**

- `ParseClassification.ADMITTED` is not the repository Outcome.
- Empty `items` is not Search Mentions admitted-empty.
- Grouping restatements are context, not Observation kinds.
- Source-domain overlap is not a partition.
- Limit equality/above is not truncation.
- `provider_array_index` is lexical content with Recipe-scoped UNIQUE, not identity.
- Error-path `result_count` is not topology.

**Deliberately duplicated:** writer/complete-set cluster; closed Recipe document construction; context dict rebuilt in tests from parser IR rather than from the planner.

**Fourth-writer extraction:** the AI-05 trigger has fired. Extraction still looks **dangerous**, not safe. This copy has no occurrence relations, no `observation_admitted_empty`, grouping-as-context columns, grouping-key reconciliation after parse, and production parameter revalidation that Search Mentions derive still lacks. A generic kernel would leak those differences or paper over them.

**Closure blockers:** none known. Residual: Recipe is in the derive module rather than the parser module, forced by the AI-10 source guard and the AI-10-test allowlist exclusion.

**Deferred:** AI-12 selection/read API; Steward design question on writer extraction; nonempty optional families; ChatGPT/other platforms; F13; AGENTS.md entrypoint listing.

**Later reuse:** production verify-and-revalidate chain; `PRE_*_SCHEMA_STATEMENTS` layering; two-kind envelope plus rich context; catalog-driven two-database projection; field-state/count CHECKs.

**Remain duplicated / provider-native:** Target Metrics `source_domain` vs Search Mentions structured source URL; TM `ai_search_volume` vs Keyword Overview / Search Mentions volumes; grouping restatements vs total.

### Coworker/strategy assessment

**Verified Evidence:** one Google Capture, 1775 bytes, digest above. Total 3061 mentions / 2336840 AI search volume. Ten unique source-domain rows whose mention sum 4415 and volume sum 3187610 exceed total. Location/language/platform each restated 3061 / 2336840. Optional families present-empty. `items=[]`.

**Provider claimed contract:** grouping row shape `key/mentions/ai_search_volume`; `internal_list_limit` 1..10; documented `items=null` vs real `items=[]`.

**Synthetic proof:** echo/path mismatch, grouping-key mismatch, value ≠ total, below/above limit, zeros, empty identity, I-JSON overflow, optional/items field states, nonempty optionals, provider error with strange `result_count`.

**Useful later (downstream):** keyword-level AI mention and AI-search-volume history for this closed Google/US/English/answer/word-match request; presence of a raw domain in the returned histogram; change of those facts across later Captures.

**Not safely inferable:** rank/sort/tie-break; share or partition of total; truncation or completeness; location/language/platform effects; ChatGPT behavior; Data Period or Provider Update Time; traffic or a universal visibility score; brand/entity/Page identity; equivalence to Search Mentions sources.

**Schema help/harm:** two fact tables plus a rich context row give AI-12 an honest grain. Storing grouping metrics as context keeps disagreement recoverable without teaching a false “metrics by location” Observation surface. `provider_array_index` UNIQUE lets later analysis test order stability without calling it rank. Awkwardness: 15 grouping context columns on one row is wide but matches singleton Recipe v1; a second multi-location Recipe would need different relations rather than stretching these CHECKs into array constants.

**Recommendation, not implemented:** keep location/language/platform as context until a probe shows they are not restatements of total.

### Bounded question for the Steward

Answered in the remediation addendum below. `TARGET_METRICS_RECIPE` remains in
`target_metrics_derive.py`.

### Confirmation

No provider, DNS, credential, paid-gate, operator-Evidence-root, or public-network call. No AI-12/API/selection/strategy/F13/shared-kernel work. No Evidence mutation. No amend. No push. Status is `review`.

## Remediation report

**Parent:** `b30b69f596800af36bcf85cc638bbf217bc21965`  
**Child:** this remediation commit  
**Status:** `review` (unchanged)  
**AI-11 only:** yes. Test and report remediation only. Nothing pushed. Nothing amended.

### Steward decision — Recipe seam

- `TARGET_METRICS_RECIPE` remains in `src/observatory/target_metrics_derive.py`.
- Do not relax AI-10’s parser-module `provider_recipe` source guard merely to
  colocate Recipe bytes with parser constants.
- Recipe is derivation policy; keeping the parser independent is the accepted
  durable seam unless a later concrete requirement proves otherwise.

### Changed paths

- `tests/test_dataforseo_ai_optimization_target_metrics_derive.py`
- this ticket (remediation addendum and targeted-evidence correction)

### Proofs added

- parameterized planner coverage of stated-nonempty
  `search_results_domain`, `brand_entities_title`, and
  `brand_entities_category`, each `provider_envelope_rejected` with zero
  envelopes, no context, and no typed facts;
- duck-typed store rejected with `TypeError` against a poisoned connection
  before schema work, Evidence reads, or connection use.

Production code is unchanged. Parser admission is unchanged.

### Targeted evidence correction

The implementation report’s “28+1 persist path in the combined 29-pass run”
wording is removed. That count mixed the AI-11 file with one Search Mentions
baseline test and is not an AI-11 targeted result.

Exact implementation-child targeted command:

```
uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py
28 passed in 15.43s
```

Exact remediation-tree targeted command:

```
uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics_derive.py
31 passed in 16.45s
```

```
uv run ruff check .
All checks passed!
```

```
uv run mypy
Success: no issues found in 62 source files
```

The full suite was not rerun in this remediation. [CHAZ] will run one final
exact-HEAD targeted/full/Ruff/mypy operator block after this commit.

### Confirmation

No production-code change. No provider/network/credential/Evidence/schema
change. No AI-12/API/strategy/F13/shared-kernel work. No amend. No push.
