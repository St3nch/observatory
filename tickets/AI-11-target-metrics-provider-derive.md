# AI-11 — Target Metrics provider Derivation and typed persistence

**Status:** accepted  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; mandatory GROK technical review reconciled  
**Approved by:** [CHAZ] for final ticket publication / [GPT] Steward reconciliation  
**Technical-review base:** cd276059b98553cf74d24013e55e468763a9b762  
**Implementation start:** the accepted-ticket commit supplied by the Steward in the implementation prompt  

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
