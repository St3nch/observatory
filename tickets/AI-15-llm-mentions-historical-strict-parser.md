# AI-15 — LLM Mentions Historical strict parser and AI-14 Conformance fixture

**Status:** provisional  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** mandatory read-only GROK review of this provisional ticket and final Steward reconciliation  
**Product direction:** [CHAZ] continues the Historical slice after AI-14 accepted one-shot live Evidence  
**Draft base:** `9d6941859b649c232e46eb68a8b489fb4acb2875`  
**Implementation start commit:** not yet authorized  

## Purpose

Build the zero-network interpretation boundary for the exact closed adapter
`dataforseo-ai-optimization-llm-mentions-historical-live-paid-probe-v1`.
Promote the already accepted AI-14 response bytes into one frozen deterministic
Conformance fixture, then parse those bytes into a strict typed in-memory Historical
representation with bounded synthetic adversarial proofs.

AI-15 does **not** create a Derivation Recipe, repository Outcome, Observation identity,
PostgreSQL schema or rows, derive command, recipe selection, history API, Outcomes/Holdings,
recurring acquisition, F12/F13 work, strategy state, or another provider exchange. Those
remain separate later boundaries.

This provisional ticket is not implementation authority. GROK must review it read-only,
GPT must reconcile that review, and [CHAZ] must later authorize implementation from the
exact final clean commit.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Derivation, Observation, Provenance, Data Period, and
  strategy boundaries.
- D11 — provider interpretation, reconciliation, time-axis separation, and Observation
  identity restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, parser, and Recipe
  remain distinct; one Capture proves existence, not invariance.
- D14 — parser classifications are not repository Measurement Outcomes and this ticket does
  not add consumer resources.
- `docs/specs/capture-event-v2.md` provider interpretation and verified-body rules.
- AI-13 closed the one-shot Historical Live Evidence-only adapter.
- AI-14 closed the single authorized live exchange, exact inspection, bounded encrypted F6
  protection, fresh restore/equality proof, receipt round-trip, payload assessment, and
  independent GROK review.
- AI-10 Target Metrics is the closest structural parser precedent. AI-04 Search Mentions
  supplies useful strict JSON/monthly-period precedent. Keyword Overview and Google Organic
  remain surface-local contrasts, not shared Historical semantics.

AI-15 authorizes no provider, DNS, account, credential, restic, rclone, pricing, or other
public-network activity.

## Question-resolution lock

GROK completed the required code-first question phase against clean synchronized
`9d6941859b649c232e46eb68a8b489fb4acb2875`. GPT independently checked the actual parser
precedents and D11/D12 boundaries. No Product question remains.

The following technical decisions are locked for this provisional ticket:

1. Verified Attempt parameters are request authority. Provider task echo is separately
   typed and preserved. A well-typed echo disagreement does **not** override Attempt context
   and does not itself fail parsing.
2. Successful Historical `items` is the actual testimony array. Omitted `items`, JSON null,
   object/scalar, or other wrong type fails parsing. `items=[]` with `items_count=0` parses
   as an empty parser IR only; this ticket assigns no admitted-empty or Observation meaning.
3. `items_count` must equal `len(items)` on the successful branch.
4. Exactly one task is required. `tasks_count` and `tasks_error` are reconciled as in the
   accepted Target Metrics parser. On provider success, exactly one result object is required
   and `result_count` must equal one. A successful empty result is malformed parser input,
   not a provider-error classification.
5. Consistent provider non-success status yields parser classification
   `ParseClassification.PROVIDER_ERROR` without parsing Historical item testimony.
   Inconsistent top-level/task success is a parser failure.
6. Root, task, task data, target, result, item, and metrics objects are closed for this v1
   strict parser. Unknown members fail deterministically. This does not assert the provider
   can never add fields; later accepted interpretation changes remain versioned work.
7. `year`, `month`, `mentions`, `ai_search_volume`, and structural counts are JSON integers;
   booleans, decimal numbers, and strings are rejected. Metrics are nonnegative; stated zero
   parses as zero testimony. Negative metrics fail.
8. Calendar bounds are `year=1..9999` and `month=1..12`. The provider's current 2025-08 data
   floor is claimed-contract context, not a parser year bound.
9. Duplicate `(year, month)` rows fail. Historical v1 defines one typed monthly point per
   returned period and no duplicate-period occurrence semantics.
10. Provider array order is retained only as zero-based `provider_array_index`. Newest-first
    was observed in AI-14 but is not a parser invariant; parser tests must accept shuffled
    order without sorting.
11. **Returned-period reconciliation is deliberately not encoded here.** Extra periods
    outside the verified requested window and missing periods inside that window remain
    parseable typed provider testimony. D11 puts unrequested-item and completeness meaning in
    later Recipe reconciliation/admission. AI-15 must not turn the observed twelve-month
    completeness into a parser invariant.
12. Capture/acquisition time is not parser data time. Historical Data Period remains provider
    `year` + `month` integers. Provider Update Time is unstated and no synthetic date,
    `YYYY-MM`, event time, or Capture-time inheritance is created.
13. No shared Mentions parser/kernel/framework is introduced. Small accepted value types such
    as `ParseClassification` may be reused without generalizing parser architecture.

## Exact fixture provenance

The fixture is copied once from the already protected AI-14 Evidence through the existing
read-only Historical inspector. No provider request is permitted.

- Evidence root:
  `/home/chaz/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25`;
- Attempt:
  `4d0981e2df7476935c4603c2569ea732cd523dee763263c483352ed4563c864c`;
- Capture:
  `218d5cf475bb0b3b8861b0dc83b8c763b36252ee4065f72900e17a937763b18b`;
- exact response bytes: `5246`;
- exact response SHA-256:
  `4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`.

Required fixture path:

`tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json`

The committed fixture must be byte-identical to verified inspector stdout. The real body is
pretty-printed UTF-8 JSON with no BOM and no trailing newline; that formatting is retained
exactly because fixture identity is byte identity. Tests independently prove exact length and
SHA-256. After the one-time local copy, ordinary tests must not depend on the operator
Evidence root or `/tmp` body file.

The fixture is deterministic Conformance material, not authoritative Evidence.

## Verified AI-14 testimony

The exact protected body establishes one HTTP-complete provider-success response:

- envelope version `0.1.20260806`;
- root/task `status_code=20000`, `status_message="Ok."`;
- root time `0.8682 sec.`, task time `0.7831 sec.`;
- root/task cost lexical value `0.101`;
- one task, `tasks_error=0`, task
  `08251832-1463-0662-0000-194ae8326094`, one result;
- provider path array
  `["v3", "ai_optimization", "llm_mentions", "historical", "live"]`;
- task data echoes `api=ai_optimization`, `function=historical`, exact dates
  `2025-08-01..2026-07-31`, `en`, `2840`, `google`, and the one included
  `generative engine optimization` target with `word_match` and
  `search_scope=["answer"]`;
- result has exactly `items_count` and `items`;
- `items_count=12`, and `items` is a nonempty 12-row array;
- every item has exactly `year`, `month`, `metrics`;
- every `metrics` object has exactly `mentions`, `ai_search_volume`;
- returned periods are 2026-07 down through 2025-08 with no duplicates, missing months,
  extras, null metrics, or zero metrics in this one Capture.

One body proves those states exist. It does not prove newest-first ordering, exact-window
completeness, missing/extra-period behavior, empty/null result branches, zero behavior,
future field stability, current-month partiality, alternate platforms, or billing formula.

## Required production module and public interface

Required new production module:

`src/observatory/dataforseo_ai_optimization_llm_mentions_historical.py`

Required public parser shape:

`parse_historical(body: bytes, parameters: Mapping[str, object]) -> HistoricalIR`

The parser accepts only verified complete response-body bytes plus verified Attempt
parameters. It accepts no HTTP status/header, transport state, Capture classification,
Evidence path, credential, client, URL, network, restic, or rclone seam.

Do not edit the paid-probe implementation to host parser logic.

## Typed IR requirements

The IR must retain enough exact testimony for a later Recipe ticket to reason without
rereading ad hoc JSON.

Request context retains:

- adapter contract;
- exact `date_from` and `date_to` strings;
- requested keyword;
- `match_type`, `search_filter`, `search_scope`;
- platform, location code, language code.

Provider echo retains independently:

- `api`, `function`;
- echoed `date_from`, `date_to`;
- echoed language, location, platform;
- exact echoed target tuple.

Envelope/task IR retains:

- parser classification `ADMITTED | PROVIDER_ERROR` as parser-only terminology;
- version, root status/message/duration/exact Decimal cost;
- `tasks_count`, `tasks_error`;
- task ID, task status/message/duration/exact Decimal cost;
- task path as tuple of strings;
- `result_count`.

Successful result IR retains:

- `items_count`;
- immutable tuple of Historical monthly points.

Each Historical monthly point retains:

- `year: int`;
- `month: int`;
- `mentions: int`;
- `ai_search_volume: int`;
- `provider_array_index: int` as lexical position only.

Do not add Capture timestamps, Provider Update Time, normalized month strings, computed
calendar dates, billing interpretation, trend scores, shares, aggregates, completeness flags,
or Observation identities.

## Strict JSON and field rules

The parser must:

- reject UTF-8 BOM, invalid UTF-8, duplicate JSON object members, trailing non-whitespace
  bytes, invalid JSON, and non-finite constants;
- use `Decimal` for decimal-capable provider cost fields and never binary float;
- reject booleans anywhere an integer is required;
- require all successful known fields and exact container types;
- parse known objects closed and fail on unknown keys;
- preserve provider duration strings as strings, never timestamps;
- require and type the verified Attempt parameter object for this exact adapter contract;
- preserve well-typed provider echo even when it disagrees with Attempt context;
- never synthesize an omitted/null Historical row or metric.

## Status and topology rules

- `tasks_count` must equal the task-array length and exactly one task is required.
- `tasks_error` must equal the number of non-success tasks in that one-task envelope.
- A consistent non-success provider status returns `PROVIDER_ERROR` parser IR and does not
  interpret a Historical result as admitted testimony.
- Top-level/task success disagreement fails deterministically.
- On the successful branch, `result_count` must equal the result-array length and both must
  equal one.
- The successful result object is closed to exactly `items_count` and `items`.
- `items_count` is a nonnegative integer equal to the parsed item-array length.
- Successful `items=[]` with `items_count=0` is parseable empty testimony only. No parser
  branch calls it Observation-admitted-empty or coverage.
- Successful omitted/null/wrong-typed `items` fails.

## Period, metric, order, and reconciliation restraint

- Each row is a closed `year`/`month`/`metrics` object.
- Each metrics object is closed `mentions`/`ai_search_volume`.
- `year` uses calendar bound `1..9999`; `month` uses `1..12`.
- `mentions` and `ai_search_volume` are nonnegative JSON integers; zero remains stated zero.
- Duplicate `(year, month)` fails even if metrics match.
- Returned row order is preserved and only `provider_array_index` changes when a synthetic
  test shuffles rows. Do not sort or require newest-first.
- Do not require the successful set to contain exactly twelve points.
- Do not reject a syntactically valid extra/out-of-window period or a missing in-window
  period in the parser. Preserve it for later Recipe reconciliation against `date_from` and
  `date_to`.
- Do not sum monthly metrics or compare them with Target Metrics totals.

## Required golden fixture proofs

At minimum prove from the exact AI-14 fixture:

- exact fixture length `5246` and SHA-256
  `4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`;
- no BOM and no trailing newline are retained exactly;
- exact root/task/result topology, statuses, messages, duration strings, Decimal costs,
  task ID/path, and counts;
- exact verified Attempt request context and separately typed provider echo;
- `items_count=12` and exact twelve returned points in provider order;
- every point's exact `(year, month, mentions, ai_search_volume)` values;
- zero-based provider indexes;
- parser outcome `ADMITTED` is explicitly parser-only, not a repository Outcome;
- ordinary test code contains no operator Evidence-root dependency after fixture promotion.

## Required synthetic adversarial proofs

At minimum mutate decoded copies or dedicated synthetic JSON; never edit the frozen fixture:

### Decode and numeric strictness

- UTF-8 BOM, invalid UTF-8, trailing junk, invalid JSON, duplicate object members,
  `NaN`/`Infinity`;
- Decimal integer/fraction/exponent/high-precision cost forms without float round-trip;
- bool/string/decimal forms where counts, year/month, mentions, or volume require integers;
- negative counts and negative metrics.

### Envelope/status/count topology

- wrong `tasks_count`; two tasks; wrong `tasks_error` on success and failure;
- top-level success with task failure and the inverse;
- consistent provider error returns parser `PROVIDER_ERROR` without item admission;
- wrong `result_count`; empty/two-result successful topology;
- unknown keys at root, task, data, target, result, item, and metrics layers.

### Historical result states

- omitted `items`; `items=null`; `items={}` fail;
- `items=[]` with `items_count=0` parses as empty parser IR;
- `items_count` mismatch fails;
- missing `metrics`, missing `mentions`, missing `ai_search_volume`, wrong metrics type;
- zero mentions and zero AI search volume parse distinctly;
- duplicate period fails;
- month `0`, `13`, negative month, year `0`, year `10000` fail;
- shuffled order parses without sorting and recomputes only provider indexes;
- dropped in-window month still parses;
- added valid out-of-window month still parses;
- unexpected member at every closed object layer fails.

### Request/echo isolation

- well-typed echoed keyword/platform/dates disagreement remains visible and does not replace
  Attempt request context;
- missing/wrong-typed echo fields fail structural parsing;
- missing/wrong adapter Attempt parameters fail before successful parse;
- parser signature remains only body + parameters;
- no credentials, sockets, provider hosts, DNS, restic, or rclone are used.

## Changed-path allowlist for later implementation

When and only when the final ticket is accepted and [CHAZ] authorizes implementation, GROK
may modify exactly:

- `src/observatory/dataforseo_ai_optimization_llm_mentions_historical.py`;
- `tests/test_dataforseo_ai_optimization_llm_mentions_historical.py`;
- `tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json`;
- this ticket only for Start commit, status, and implementation report.

Do not modify AI-13/AI-14, capture transport, other provider parsers, migrations, derive
code, APIs, decisions, roadmap, or unrelated tests in AI-15.

## Mandatory GROK provisional-ticket review

Before this ticket can become implementation authority, GROK reviews this exact provisional
ticket read-only against current authority, the AI-13/AI-14 Evidence boundary, the real
parser precedents, and actual code/tests.

Challenge especially:

- whether any parser rule above accidentally defines Recipe reconciliation/admission;
- whether echo disagreement, period extras/missing periods, empty items, provider errors,
  and duplicate periods are placed at the correct layer;
- whether closed unknown-field policy is justified for the parser boundary;
- whether the IR retains enough provider testimony for a later Recipe without over-modeling;
- whether the fixture provenance/copy proof can remain exact and zero-network;
- whether any requested helper/generalization widens the scope;
- missing adversarial tests or false greens;
- changed-path allowlist and test isolation.

Return `READY`, `RECONCILE`, or `NOT_READY`. Do not edit files, copy the fixture, call the
provider, access credentials, mutate Evidence/PostgreSQL, commit, amend, or push.

## Implementation verification after later authorization

GROK implementation should run bounded targeted Historical parser tests plus:

- `uv run ruff check .`;
- `uv run mypy src`.

Do not run the full suite during ordinary implementation. After independent review and any
remediation settle, GPT will issue the exact-HEAD full validation block if required by the
current workflow.

## Hard boundaries

- Parser + one frozen fixture only.
- No provider/network/credential/account/restic/rclone activity.
- No recapture or alternate Historical request.
- No Derivation Recipe, repository Outcome, Observation, schema, PostgreSQL, derive command,
  selection, API, Outcomes/Holdings, strategy, F12, F13, or another surface.
- No generic Mentions parser/capability framework.
- Only GROK writes `src/` and `tests/`.
- No amend or push without [CHAZ] authorization.

## Stop point

AI-15 remains provisional until GROK's ticket review is reconciled and the final ticket is
committed. Even then implementation remains blocked until [CHAZ] explicitly authorizes GROK
from that exact clean start commit.
