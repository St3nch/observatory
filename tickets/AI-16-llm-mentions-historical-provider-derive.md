# AI-16 — LLM Mentions Historical provider Derivation and typed persistence

**Status:** accepted  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** explicit [CHAZ] implementation authorization from the exact final accepted ticket commit  
**Product direction:** [CHAZ] selected admission of syntactically valid extra/out-of-window returned months as normal monthly Observations; requested-window completeness remains separate context  
**Draft base:** `826c7c3e82eeac94a56fb81c669aee4a23a802cb`  
**Pre-implementation review:** GROK `RECONCILE`, completed read-only at `1b3471bfec16f82fde335f6cc26a82a8ca45441b`  
**Implementation start commit:** not yet authorized  

## Purpose

Add the first content-addressed Derivation Recipe and rebuildable typed PostgreSQL
persistence for the closed Historical adapter:

`dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`.

AI-16 consumes verified Historical Attempt/Capture Evidence through the closed AI-15 parser,
registers one immutable Recipe, creates repository Outcomes, generic Observation envelopes,
typed monthly Historical fact rows, one Capture-level result-context row, and non-Observation
rows for requested calendar periods the provider did not return.

This ticket does **not** add Recipe selection, an admitted-history API, Measurement Outcomes,
Holdings, recurring acquisition, provider calls, F12/F13 work, strategy/scoring, or a generic
Mentions schema/writer. Those remain separate boundaries.

GROK reviewed the provisional ticket read-only and returned `RECONCILE`. GPT independently
verified the material findings and incorporated the technical locks below. No Product
question remains and no second major ticket review is required. This final accepted ticket
is still not implementation authority until [CHAZ] separately authorizes GROK from the
exact clean reconciliation commit.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Derivation, Observation, Provenance, Data Period, and
  strategy boundaries.
- D11 — provider Derivation is Recipe-addressed, typed, semantic rather than positional,
  content-consistent on rebuild, and explicit about provider time/Data Period.
- D12 — claimed contract, bounded real Evidence, parser, Recipe, and consumer API remain
  distinct; one Capture proves existence, not invariance.
- D14 — repository Measurement Outcomes and Holdings remain sibling consumer resources,
  not automatic consequences of adding typed provider persistence.
- PF-15 migration hygiene and the accepted additive `PRE_*_SCHEMA_STATEMENTS` layering.
- AI-11 Target Metrics supplies the closest production Evidence/provenance, Recipe
  registration, complete-set persistence, and migration-spine precedent.
- AI-05 Search Mentions supplies the accepted provider-stated year/month Data Period and
  successful zero-envelope `observation_admitted_empty` precedent.
- AI-13 established the Historical consumer question and one-month candidate grain.
- AI-14 supplied the one accepted Historical live Capture and protected Conformance bytes.
- AI-15 closed the strict Historical parser and deliberately left returned-window
  reconciliation to this Recipe boundary.

D11's text about duplicate/unrequested returned items occurs in the first Keyword Overview
requested-subject reconciliation rule. AI-16 does not universalize that subject rule into a
requirement that an otherwise valid Historical month outside the requested date window fail
the whole Capture.

AI-16 authorizes no provider, DNS, credential, account, pricing, restic, rclone, or other
public-network activity.

## Question-resolution and Product lock

GROK completed the required code-first review against clean pushed
`826c7c3e82eeac94a56fb81c669aee4a23a802cb`. GPT independently verified the material D11,
AI-05, AI-11, AI-12, migration, and Historical-validator premises.

[CHAZ] resolved the only Product fork:

> A syntactically valid Historical month returned outside Attempt `date_from`/`date_to` is
> admitted as a normal monthly Observation. The requested window remains Capture context.
> Requested periods not returned by the provider are persisted separately as non-Observation
> **unreturned requested periods**. They are never synthesized as zero Observations.

This means AI-16 does not silently drop extra testimony and does not fail an otherwise valid
Capture merely because the provider returned an extra period.

## Observation and fact grain

Add exactly one Historical Observation kind:

`dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1`

One Observation is one provider-returned calendar-month fact for the exact requested subject.

Observation identity axes are exactly:

- `requested_keyword: string` — exact verified Attempt keyword;
- `year: integer`;
- `month: integer`.

Typed monthly fact content is exactly:

- `mentions: integer`;
- `ai_search_volume: integer`.

Do **not** persist `provider_array_index`. Provider order/newest-first is lexical parser
testimony only and is not Observation identity, rank, Data Period, or fact content.

Do not create a series-level Observation, generic Mentions fact body, occurrence relation,
coverage Observation for an unreturned month, aggregate total, trend, share, or score.

The adapter-v1 request tuple — platform, location, language, match/filter/scope, and requested
date window — is Capture result context, not additional monthly Observation identity axes.

## Data Period and time

Historical Data Period is provider-stated `year` + `month` only, with the AI-15 bounds
`year=1..9999`, `month=1..12`.

- Capture/acquisition time remains provenance only.
- Provider Update Time is unstated.
- No `YYYY-MM` string, synthetic date, event time, current-month assumption, or Capture-time
  inheritance is created.
- Newest-first order observed in AI-14 is not a Recipe invariant.
- The provider's documented/claimed 2025-08 floor is not a Recipe year bound.

## Returned-window and completeness semantics

The verified Attempt is request authority. Provider task echo remains parser/Evidence
testimony and is not persisted by this Recipe.

For a successful parsed Historical result:

1. Compute the requested calendar-month set from the inclusive `(year, month)` range covered
   by Attempt `date_from` through `date_to`. Production parameters first pass the existing
   closed `validate_historical_http_parameters`; never use `datetime.now()` or provider echo.
2. Admit **every** well-typed returned monthly point as one monthly Observation, including a
   point outside the requested window.
3. Compute `unreturned_requested_periods = requested_periods - returned_in_window_periods`.
4. Persist each unreturned requested period as non-Observation completeness context.
5. Never invent a zero metric or coverage Observation for an unreturned period.
6. An extra returned period neither removes nor satisfies a different requested period.
7. `items_count` is provider returned cardinality; `observation_count` is generic envelope
   cardinality. Under Recipe v1 they are equal because every parsed returned point is
   admitted and duplicate periods already fail in AI-15. This equality is not a claim about
   requested-window completeness.

AI-14 has twelve returned in-window months and therefore produces twelve envelopes, one
context row, zero unreturned-requested-period rows, and `observation_count=12`. Twelve is
golden Evidence cardinality, **not** a hardcoded provider invariant.

### Empty successful result

`items=[]` with `items_count=0` is a successful empty Historical result and derives:

- repository classification `observation_admitted_empty`;
- zero Observation envelopes/monthly fact rows;
- one result-context row;
- one unreturned-requested-period row for every period in the verified requested window.

This is the Search Mentions subject-bearing admitted-empty pattern, not Target Metrics' stated
zero-total pattern. A stated returned month with metrics `0`/`0` remains an ordinary
`observation_admitted` monthly fact and is distinct from an unreturned requested month.

## Parser / Recipe classification boundary

AI-15 parser behavior remains frozen.

- duplicate `(year, month)` → parser failure; never reaches Recipe;
- malformed/unknown closed provider structure → parser failure;
- mixed root/task success → parser failure;
- consistent provider non-success → parser `PROVIDER_ERROR` with result items uninterpreted;
- well-typed echo disagreement → retained by parser, does not replace Attempt context;
- shuffled order → parses; order is not semantic identity;
- extra/missing requested periods → parse successfully for Recipe interpretation;
- successful empty items → empty parser IR only; Recipe supplies repository meaning.

Repository classification is created by the Recipe after verified transport, parsing,
reconciliation, and admission. Never copy `HistoricalIR.outcome.value` directly into the
repository Outcome.

## Recipe contract

AI-16 must define and register one closed Historical Recipe using the existing
`provider_recipe.py` schema and content-addressing machinery.

Add stable Historical constants to the existing parser module without changing parser
admission behavior:

- `PROVIDER = "dataforseo"`;
- `PARSER_CONTRACT = "dataforseo-ai-optimization-llm-mentions-historical-live-parser-v1"`;
- `MONTHLY_KIND = "dataforseo.google.ai_optimization.llm_mentions_historical.monthly.v1"`.

Recipe v1 must lock:

- exact Historical adapter contract;
- the Historical parser contract above;
- provider `dataforseo`;
- one monthly Observation kind and the exact identity axes above;
- numeric normalization `exact_integer`;
- provider-stated year/month Data Period with no Capture inheritance;
- Provider Update Time `structure_unstated` with no Capture/sibling inheritance;
- closed-object/fail-closed extension policy consistent with AI-15's parser boundary;
- standard provider field-state vocabulary required by the Recipe schema, without inventing
  nullable Historical metric states;
- a Historical-local reconciliation rule whose semantics are exactly the requested-window,
  extras-admitted, unreturned-period behavior in this ticket;
- closed Capture classification list including `observation_admitted_empty`.

Canonical Recipe JCS bytes and SHA-256 derivation_version_id must be independently proven.
Do not call `select_provider_recipe`; selection is later API work.

## Capture-stage Outcome taxonomy

Use the accepted provider taxonomy for this Recipe:

- `no_response`;
- `response_partial`;
- `transport_complete_non_admissible`;
- `provider_error`;
- `provider_envelope_rejected`;
- `reconciliation_failed`;
- `observation_admitted`;
- `observation_admitted_empty`.

Attempt-stage classification remains `authorized_unresolved`.

`reconciliation_failed` stays in the Recipe's closed taxonomy but must not be abused for an
extra returned month, missing requested month, or well-typed echo disagreement. If v1 has no
ordinary successful path that emits it, do not manufacture one merely to exercise the label.

## Production Evidence and provenance chain

The production derive entrypoint must follow the hardened AI-11 chain:

1. require `type(store) is EvidenceStore`;
2. verify-on-read Capture and require the exact Historical adapter;
3. read only the Capture-cited `attempt_id`;
4. verify-on-read that Attempt and require the same Historical adapter;
5. require Mapping parameters and pass them through
   `validate_historical_http_parameters`;
6. read complete response bytes only through `EvidenceStore.read_capture_body`;
7. pass the validator-closed Attempt parameters plus verified body to `parse_historical`;
8. plan and write one atomic Capture/Recipe unit.

Evidence integrity failures, missing/foreign citation, wrong adapter, non-Mapping parameters,
or validator failure increment integrity failures and emit no Capture-stage Historical rows.

The Capture-cited Attempt exclusively controls persisted keyword/request context. A valid
foreign Historical Attempt in the same store must never leak into the Capture's Outcome,
context, or facts.

AI-16 reads committed test Evidence built from the frozen Conformance fixture/synthetic
bytes. Ordinary tests do not read the operator AI-14 Evidence root.

## Typed persistence and migration

Reuse the existing generic:

- `provider_recipes`;
- `derivation_versions`;
- `outcomes`;
- `observation_envelopes`;
- `derivation_diagnostics`.

Add exactly three Historical-local relations (exact names locked):

### `llm_mentions_historical_monthly`

One row per monthly Observation envelope. Include:

- `capture_id`;
- `derivation_version_id`;
- `within_capture_identity`;
- `observation_kind`;
- `requested_keyword`;
- `year`;
- `month`;
- `mentions`;
- `ai_search_volume`.

Require full envelope FK/candidate-key binding, exact-kind CHECK, nonempty keyword, year/month
bounds, BIGINT 0..9007199254740991 metric bounds, and Recipe-scoped uniqueness preventing two
typed rows for the same Capture/Recipe calendar period. No JSONB and no provider-array index.

### `llm_mentions_historical_result_context`

One row per `observation_admitted` or `observation_admitted_empty` Capture/Recipe. Include:

- `capture_id`, `derivation_version_id`, `attempt_id`;
- exact Attempt `requested_keyword`, `match_type`, `search_filter`, `search_scope`;
- exact Attempt `platform`, `location_code`, `language_code`;
- exact Attempt `date_from`, `date_to` strings;
- provider `items_count`.

Primary identity is `(capture_id, derivation_version_id)`. Require FK to the full Outcome
identity `(derivation_version_id, attempt_id, capture_id)`. Context is not an Observation and
does not increment `observation_count`.

### `llm_mentions_historical_unreturned_requested_periods`

One row per requested `(year, month)` absent from the returned in-window set. Include:

- `capture_id`;
- `derivation_version_id`;
- `year`;
- `month`.

Require FK to the matching Historical result context, year/month bounds, and uniqueness per
Capture/Recipe period. These rows are completeness context, not Observations and not zero
metrics.

Do not add a separate extra-period table. Extra returned months are ordinary monthly facts;
the later API can compare their Data Period with the explicit request window.

### Migration layering

Define:

`PRE_AI16_SCHEMA_STATEMENTS = current SCHEMA_STATEMENTS`

then:

`SCHEMA_STATEMENTS = PRE_AI16_SCHEMA_STATEMENTS + Historical statements`.

Preserve `PRE_PF12_SCHEMA_STATEMENTS`, `PRE_AI05_SCHEMA_STATEMENTS`, and
`PRE_AI11_SCHEMA_STATEMENTS` unchanged. The Target Metrics derive migration test may be
edited only to measure its three-table layer against `PRE_AI16_SCHEMA_STATEMENTS`, analogous
to AI-11's prior Search Mentions baseline adjustment.

Migration must remain additive, idempotent, and logically equivalent on fresh versus upgraded
databases while preserving fixture, Keyword Overview, Organic, Search Mentions, and Target
Metrics rows.

## Atomic complete-set behavior

One Historical Capture/Recipe unit consists of:

- exactly one intended Capture Outcome;
- one context row for admitted/admitted-empty results;
- all intended Observation envelopes;
- all intended typed monthly rows;
- all intended unreturned-requested-period rows;
- all intended diagnostics (v1 happy path is empty).

Same Recipe + same verified Evidence must be exact-content consistent:

- exact rerun succeeds;
- a missing planned rebuildable row may be restored only if the final complete set becomes
  exact;
- conflicting content fails;
- planted extra monthly/context/unreturned-period/diagnostic rows fail;
- wrong `observation_count` fails;
- foreign-Attempt Outcome/context fails;
- no `ON CONFLICT DO NOTHING` or last-write-wins may hide semantic disagreement.

Complete-set comparison is scoped by Capture + Recipe and ignores a different Recipe's rows.
A second Historical Recipe must coexist independently for the same verified Capture.

## Required golden proofs

Use the committed AI-14 fixture only. Prove:

- fixture remains exactly `5246` bytes with SHA-256
  `4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`;
- neighboring accepted provider fixtures remain byte-identical;
- exact canonical Recipe bytes, byte length, digest, and independent SHA-256 recomputation;
- Recipe ID equals `recipe_derivation_version_id()` independently;
- exact twelve AI-14 monthly `(year, month, mentions, ai_search_volume)` facts;
- exactly twelve monthly envelopes/typed rows, one context row, zero unreturned-requested
  periods, and `observation_count=12`;
- context preserves exact Attempt keyword/window/platform/location/language/filter/scope;
- provider echo and task/cost metadata are not persisted;
- no provider array index is persisted;
- year/month remain integer Data Period fields with no synthetic date/time;
- observation count is computed from planned envelopes, never hardcoded to twelve.

## Required adversarial proofs

At minimum prove on real PostgreSQL with zero network:

- Recipe content-ID determinism and conflicting Recipe-byte refusal;
- exact rerun and missing-row repair;
- planted extra row/diagnostic, content conflict, and wrong observation_count fail;
- foreign Attempt/Capture provenance cannot cross-link;
- an extra valid out-of-window month is admitted as a normal monthly Observation and increases
  `items_count`/`observation_count` without changing the requested window;
- a dropped requested in-window month leaves all returned facts intact and creates exactly one
  matching unreturned-requested-period row;
- successful empty items derives `observation_admitted_empty`, one context, zero envelopes,
  and the complete requested-period set as unreturned rows;
- stated zero metrics persist as stated zero and are distinct from unreturned periods;
- provider error creates `provider_error` with no context/facts/unreturned rows even when the
  result body contains success-path-invalid content;
- parser rejection, partial/no-response, and complete non-admissible transport have exact
  closed behavior;
- echo disagreement never replaces Attempt request context;
- shuffle changes no monthly identity/content set and creates no ordering column;
- empty identity text or persisted I-JSON overflow rejects the whole admitted unit as
  `provider_envelope_rejected` with no partial context/facts;
- PostgreSQL independently rejects wrong kind, orphan detail, invalid year/month,
  negative/overflow metrics, duplicate Capture/Recipe period, and context without Outcome;
- second Historical Recipe coexistence;
- populated-current-schema upgrade preserves all prior surface rows;
- fresh/upgraded bounded-catalog parity;
- two databases rebuilt from identical Evidence/Recipe are logically equivalent across every
  new Historical column;
- Historical derive skips other adapters and other provider derives do not consume Historical
  Evidence;
- parser behavior and frozen fixture bytes remain unchanged;
- no provider/DNS/credential/restic/rclone/operator-Evidence-root activity occurs.

A socket guard is only a bounded regression guard; do not describe it as a universal proof of
all possible network absence.

## Parser vs Recipe vs later API boundary

AI-15 parser:

`verified body + Attempt parameters -> HistoricalIR`

AI-16:

`verified Evidence + immutable Recipe -> repository Outcome + envelopes + typed monthly facts + result context + unreturned requested periods`

Later ticket only:

`Recipe selection/pinning + admitted-history API`

The later API must be able to assemble one admitted Capture document from Outcome + context +
monthly envelopes/facts + unreturned requested periods. One history item is one admitted
Capture. AI-16 adds no consumer route.

## Changed-path allowlist for later implementation

When and only when this ticket is final and [CHAZ] separately authorizes implementation,
GROK may modify exactly:

- `src/observatory/dataforseo_ai_optimization_llm_mentions_historical.py` — constants/Recipe
  contract publication only; no parser-admission change;
- `src/observatory/llm_mentions_historical_derive.py` — new;
- `src/observatory/migrate.py`;
- `tests/test_dataforseo_ai_optimization_llm_mentions_historical_derive.py` — new;
- `tests/test_dataforseo_ai_optimization_target_metrics_derive.py` — PRE_AI16 migration
  baseline adjustment only;
- this ticket for Start commit, status, and implementation report.

No other path is authorized. If implementation appears to require `capture_event.py`, AI-15
parser tests, API/selection modules, AGENTS.md, other derive modules/tests, roadmap, decisions,
or another path, stop and ask the Steward.

AGENTS.md entrypoint publication is a Steward-owned closure follow-up after accepted
implementation, not GROK scope:

`uv run python -m observatory.llm_mentions_historical_derive`

## Mandatory GROK provisional-ticket review

Before AI-16 can become implementation authority, GROK must review this exact provisional
ticket read-only against current authority and the actual code/schema/tests.

Challenge especially:

- monthly Observation identity and whether any request-context field was wrongly made identity
  or wrongly omitted;
- the Product-locked extra-period admission semantics and unreturned-period calculation;
- successful empty-series meaning;
- Recipe document tokens/closed taxonomy and whether `reconciliation_failed` is overbuilt;
- I-JSON and PostgreSQL constraints;
- AI-11 provenance-chain fidelity;
- complete-set writer scope, repair behavior, and second-Recipe coexistence;
- schema FK/uniqueness design and PRE_AI16 migration layering;
- whether three Historical relations are sufficient for the later admitted-history API;
- changed-path allowlist and whether the Target Metrics baseline edit is truly necessary;
- false greens, missing adversarial proofs, or accidental parser/API/F12/F13 widening;
- whether any shared-writer extraction should remain deferred rather than entering AI-16.

Do not edit files, run provider/network/credential activity, mutate Evidence/PostgreSQL,
implement, commit, amend, or push.

Return `READY`, `RECONCILE`, or `NOT_READY` and separate genuine Product questions from
technical corrections. No second major code-first review is required unless this ticket
introduces a new unresolved premise.

## Implementation verification after later authorization

GROK implementation should run the targeted Historical derive suite plus bounded migration
tests required by the implementation, then:

- `uv run ruff check .`;
- `uv run mypy src`.

Do not run the full suite during ordinary implementation. After implementation review and any
remediation settle, the Steward will issue the exact-HEAD full validation gate; [CHAZ] may run
that operator block over SSH when the governed runner is unavailable or unreliable.

## Hard boundaries

- Historical Recipe + Derivation + typed persistence only.
- No provider/network/credential/account/restic/rclone activity.
- No recapture or alternate Historical request.
- No Recipe selection/pinning or API route.
- No Measurement Outcomes or Holdings endpoint work.
- No parser admission change.
- No F12 recurring acquisition or F13 transport hardening.
- No strategy, scoring, recommendations, panel/cadence state, projections, or cross-surface
  metric normalization.
- No generic Mentions table, generic provider writer, or cross-surface schema redesign.
- Only GROK writes `src/` and `tests/`.
- No amend or push without [CHAZ] authorization.

## Stop point

## Final Steward reconciliation lock

This section is normative and supersedes any earlier less-specific wording in this ticket.
GROK's read-only review returned `RECONCILE`; GPT independently verified the material
findings. No Product question remains.

### Exact Recipe identity

`recipe()` lives in `src/observatory/llm_mentions_historical_derive.py`. The parser module may
add only `PROVIDER`, `PARSER_CONTRACT`, and `MONTHLY_KIND`; it must not import
`provider_recipe` or own Recipe construction.

The Recipe uses the existing schema/identity constants and these exact values. JCS object
member order is canonical, but every array order below is identity and is locked exactly:

- `adapter_contract = HISTORICAL_ADAPTER_CONTRACT`
- `provider = "dataforseo"`
- `parser_contract = PARSER_CONTRACT`
- `admission.rule = "recipe_closed_classifications"`
- `admission.capture_outcomes = [`
  `"no_response"`, `"observation_admitted"`, `"observation_admitted_empty"`,
  `"provider_envelope_rejected"`, `"provider_error"`, `"reconciliation_failed"`,
  `"response_partial"`, `"transport_complete_non_admissible"` `]`
- `data_period = {"inheritance": "never_from_capture", "rule":
  "provider_stated_year_month_1_9999"}`
- `provider_update_time = {"inheritance": "never_from_capture_or_sibling", "rule":
  "structure_unstated"}`
- `numeric.normalization = "exact_integer"`
- `reconciliation.rule = "attempt_window_admit_all_returned_periods"`
- `field_state.states = [` `"absent"`, `"inapplicable"`, `"json_null"`,
  `"not_requested"`, `"stated"` `]`
- `extension_policy.closed_objects = [` `"/"`, `"/items"`, `"/metrics"`, `"/result"`,
  `"/tasks"`, `"/tasks/data"` `]`
- `extension_policy.extension_permitted_objects = []`
- `unknown_closed_field = "fail_closed"`
- `unknown_extension_field = "fail_closed"`
- `observation_identity.kinds` contains exactly one `MONTHLY_KIND` entry whose axes are
  `requested_keyword: string`, `year: integer`, `month: integer`
- `observation_kinds = [MONTHLY_KIND]`

No additional Recipe member or alternate token is permitted in v1. The five field-state
tokens satisfy the shared Recipe schema; they do not authorize nullable metric-state columns.

### Exact requested-window algorithm

Recipe token `attempt_window_admit_all_returned_periods` means exactly:

1. Attempt `date_from` and `date_to` must each be exact lexical `YYYY-MM-DD` and valid
   calendar dates.
2. Take the `(year, month)` containing each endpoint and enumerate calendar months
   inclusively from the start endpoint month through the end endpoint month.
3. Start date after end date is invalid.
4. Never derive the window from day counts, `datetime.now()`, Capture time, or provider echo.
5. Lexically malformed, impossible, or inverted dates at a planning/test seam produce
   `provider_envelope_rejected`. Production first uses the already-frozen Historical
   validator, so this defense does not widen request policy.
6. Every parsed returned month is admitted, including extras. Unreturned requested periods
   are exactly `requested_periods - returned_in_window_periods`. An extra returned month does
   not satisfy another requested period.

### Schema and migration precision

`llm_mentions_historical_monthly` must have exact additional uniqueness:

`UNIQUE (capture_id, derivation_version_id, year, month)`

Do not include `requested_keyword` in that constraint. Keyword remains typed content and an
Observation-identity axis; including it in SQL uniqueness would permit two keywords for the
same Capture/Recipe period.

`llm_mentions_historical_result_context.location_code` and `.items_count` are BIGINT with
the accepted I-JSON bounds `0..9007199254740991`. `date_from` and `date_to` remain exact TEXT
Attempt testimony, not DATE/TIMESTAMPTZ normalization.

For the long `llm_mentions_historical_unreturned_requested_periods` relation, use these short
explicit constraint names to avoid PostgreSQL identifier truncation/collision:

- `hist_unret_pk`
- `hist_unret_context_fk`
- `hist_unret_year_ck`
- `hist_unret_month_ck`

The migration-layer arithmetic is exact:

- `PRE_AI16_SCHEMA_STATEMENTS - PRE_AI11_SCHEMA_STATEMENTS` is the existing three-table
  Target Metrics layer and must remain length 3 with the existing Target Metrics assertions.
- `SCHEMA_STATEMENTS - PRE_AI16_SCHEMA_STATEMENTS` is the new Historical layer.

Do not naively replace the current Target Metrics test's `SCHEMA_STATEMENTS - PRE_AI11` with
`SCHEMA_STATEMENTS - PRE_AI16`; that would measure Historical rather than Target Metrics.
No Search Mentions or Organic migration-test allowlist expansion is authorized.

### Complete-set and adversarial precision

Complete-set comparison for unreturned periods is exact set equality over `(year, month)`
tuples, not row-count equality. A count-preserving swapped/wrong period must fail.

Required proofs additionally include:

- one mixed mutation with an extra out-of-window returned month and one dropped in-window
  month: the extra is admitted and exactly the dropped requested period remains unreturned;
- provider_error, no_response, response_partial, parser rejection, and complete
  non-admissible transport write zero unreturned-period rows;
- production empty/changed keyword is a Historical validator integrity failure with no
  Capture-stage rows; a separate bounded plan-seam empty-identity defense may classify
  `provider_envelope_rejected`;
- parsed metric I-JSON overflow rejects the entire admitted planning unit as
  `provider_envelope_rejected` with no partial rows;
- two-database equivalence covers every column of all three new Historical relations;
- the existing closed AI-15 parser suite is rerun, without edits, because the parser module
  is allowlisted for constants:
  `uv run pytest -q tests/test_dataforseo_ai_optimization_llm_mentions_historical.py`.

The targeted Historical derive suite, bounded migration tests, `uv run ruff check .`, and
`uv run mypy src` remain required. The full suite remains deferred to the Steward exact-HEAD
validation gate after implementation review/remediation.

## Final stop point

AI-16 is final and accepted after the Steward reconciliation commit containing this section.
Implementation remains blocked until [CHAZ] separately authorizes GROK from that exact clean
final-ticket commit. No provider, Evidence mutation, PostgreSQL mutation, source/test edit,
implementation, amend, or push is authorized merely by accepting this ticket.
