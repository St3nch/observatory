# AI-15 — LLM Mentions Historical strict parser and AI-14 Conformance fixture

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** explicit [CHAZ] implementation authorization at the exact final ticket commit  
**Product direction:** [CHAZ] continues the Historical slice after AI-14 accepted one-shot live Evidence  
**Draft base:** `9d6941859b649c232e46eb68a8b489fb4acb2875`  
**Pre-implementation review:** GROK `RECONCILE` at `c5c08e26ff12e12a5543fffe5c8499196ef3845d`; accepted corrections are incorporated below.  
**Start commit:** `fb6ef9d75fc9e4f3aa765a38b0f569b7c7a06212`  
**Implementation start commit:** `fb6ef9d75fc9e4f3aa765a38b0f569b7c7a06212`  

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

GROK completed the mandatory read-only review and returned `RECONCILE`. GPT independently
verified and incorporated the accepted corrections. This final accepted ticket is still not
implementation authority until [CHAZ] separately authorizes implementation from its exact
clean committed HEAD. No second ticket review is required.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Derivation, Observation, Provenance, Data Period, and
  strategy boundaries.
- D11 — provider interpretation, reconciliation, time-axis separation, and Observation
  identity restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, parser, and Recipe
  remain distinct; one Capture proves existence, not invariance.
- D14 consumer resources remain outside this parser boundary. As in AI-10, parser
  `ParseClassification` values are parser-only and must not be treated as repository
  Measurement Outcomes.
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

The following technical decisions are locked for this final ticket:

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
   `ParseClassification.PROVIDER_ERROR` without parsing Historical item testimony. The
   provider echo is still structurally parsed and retained when well-typed; `result_count`
   remains required and nonnegative on the provider-error branch; successful-result fields
   such as `items_count` and monthly points are `None`/uninterpreted and the result array is
   not read. Missing or malformed echo/result-count structure still fails parsing.
   Inconsistent top-level/task success is a parser failure.
6. The verified Attempt parameter object is closed to exactly `contract`, `date_from`,
   `date_to`, `language_code`, `location_code`, `platform`, and `target`; its one target is
   closed to exactly `keyword`, `match_type`, `search_filter`, and `search_scope`. Root,
   task, task data, echoed target, result, item, and metrics objects are likewise closed for
   this v1 strict parser. Unknown members fail deterministically. This does not assert the
   provider can never add fields; later accepted interpretation changes remain versioned work.
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

The one-time fixture promotion command is frozen to the verified inspector, not a `/tmp`
copy:

```bash
test ! -e tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25" \
  --capture-id 218d5cf475bb0b3b8861b0dc83b8c763b36252ee4065f72900e17a937763b18b \
  > tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json
wc -c tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json
sha256sum tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json
```

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

Provider-error IR retains the typed request, typed provider echo, envelope/task testimony,
and nonnegative `result_count`, but has no interpreted Historical `items_count` or monthly
points. The provider-error branch does not read the result array. Parser classification here
is not a repository Outcome.

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
- close verified Attempt parameters to exactly `contract`, `date_from`, `date_to`,
  `language_code`, `location_code`, `platform`, and `target`, with the target closed to
  `keyword`, `match_type`, `search_filter`, and `search_scope`;
- preserve provider duration strings as strings, never timestamps;
- require and type the verified Attempt parameter object for this exact adapter contract;
- preserve well-typed provider echo even when it disagrees with Attempt context;
- never synthesize an omitted/null Historical row or metric.

## Status and topology rules

- `tasks_count` must equal the task-array length and exactly one task is required.
- `tasks_error` must equal the number of non-success tasks in that one-task envelope.
- A consistent non-success provider status returns `PROVIDER_ERROR` parser IR and does not
  interpret a Historical result as admitted testimony. The provider echo is still parsed and
  retained when structurally valid, and `result_count` is still required as a nonnegative
  JSON integer. Malformed echo/result-count structure fails. `items_count` and monthly points
  remain uninterpreted/`None`, and the result array is not read.
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
- existing provider Conformance fixtures remain byte-identical, including at minimum:
  Target Metrics AI-09
  `7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`,
  Search Mentions AI-03
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`,
  Keyword Overview PF-03
  `d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c`,
  and Google Organic PF-10
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`.

## Required synthetic adversarial proofs

At minimum mutate decoded copies or dedicated synthetic JSON; never edit the frozen fixture:

### Decode and numeric strictness

- UTF-8 BOM, invalid UTF-8, trailing junk, invalid JSON, duplicate object members,
  `NaN`/`Infinity`;
- Decimal integer/fraction/exponent/high-precision cost forms without float round-trip;
- mutation helpers must decode provider decimals as `Decimal` and re-encode `Decimal`
  lexically without routing fixture cost through binary float, following the accepted
  AI-10 test-helper pattern;
- bool/string/decimal forms where counts, year/month, mentions, or volume require integers;
- negative counts and negative metrics.

### Envelope/status/count topology

- wrong `tasks_count`; two tasks; wrong `tasks_error` on success and failure;
- top-level success with task failure and the inverse;
- consistent provider error with valid echo returns parser `PROVIDER_ERROR`, preserves echo
  and nonnegative `result_count`, and leaves `items_count`/monthly points unparsed;
- negative, boolean, float, or otherwise malformed `result_count` fails on the provider-error
  branch as well as on success;
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
- shuffled order parses without sorting; exact point tuples remain unchanged and only
  zero-based `provider_array_index` follows the new array order;
- dropped in-window month still parses, the remaining exact tuples are retained, and the
  verified request context still records the full frozen `date_from`/`date_to` window;
- added valid out-of-window month still parses as an additional typed point, the verified
  request context remains unchanged, and indexes follow the expanded provider array;
- unexpected member at every closed object layer fails.

### Request/echo isolation

- well-typed echoed keyword/platform/dates disagreement remains visible and does not replace
  Attempt request context;
- missing/wrong-typed echo fields fail structural parsing;
- missing/wrong adapter Attempt parameters and any extra unknown Attempt parameter key fail
  before successful parse;
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

## Completed GROK provisional-ticket review

GROK reviewed the provisional ticket read-only against current authority, the AI-13/AI-14
Evidence boundary, the real parser precedents, and actual code/tests at exact HEAD
`c5c08e26ff12e12a5543fffe5c8499196ef3845d`.

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

GROK returned `RECONCILE`. GPT independently verified the material findings and accepts the
four corrections now incorporated into this final ticket: close the Attempt parameter keys;
make provider-error IR/echo/result-count behavior explicit and Target-Metrics-like without
parsing Historical items; freeze fixture promotion to the verified inspector; and strengthen
the false-green/isolation tests, including Decimal-safe mutation encoding. GROK also
confirmed the D11 boundary that extra/missing periods remain parser-visible testimony for
later Recipe reconciliation. No Product question remains, and no second ticket review is
required.

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

AI-15 is final and accepted after this reconciliation commit. Implementation remains blocked
until [CHAZ] explicitly authorizes GROK from that exact clean start commit.

## Implementation report

**Parent:** `fb6ef9d75fc9e4f3aa765a38b0f569b7c7a06212`  
**Child:** this implementation commit  
**Status:** `review`  
**AI-15 only:** yes. Nothing pushed. No amend.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

Branch `main`, working tree clean after this commit. Started from the authorized HEAD.

### Changed-path allowlist

- `src/observatory/dataforseo_ai_optimization_llm_mentions_historical.py` (new)
- `tests/test_dataforseo_ai_optimization_llm_mentions_historical.py` (new)
- `tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json` (new)
- this ticket (Start commit, Status, Implementation report)

### Fixture promotion

Copied once through the frozen inspector (not `/tmp`):

```bash
uv run python -m observatory.dataforseo_ai_optimization_llm_mentions_historical_paid_probe inspect \
  --evidence-root "$HOME/.local/share/observatory/ai14-historical-generative-engine-optimization-2026-08-25" \
  --capture-id 218d5cf475bb0b3b8861b0dc83b8c763b36252ee4065f72900e17a937763b18b \
  > tests/fixtures/dataforseo_ai_optimization_llm_mentions_historical_ai14.json
```

Result: **5246** bytes, SHA-256
`4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`,
no BOM, no trailing newline. Pretty-printed provider JSON retained byte-for-byte.
Ordinary tests read only the committed fixture path.

### Public interface

`parse_historical(body: bytes, parameters: Mapping[str, object]) -> HistoricalIR`

Attempt parameters are closed request authority. Echo is independently typed. Well-typed
echo disagreement does not replace Attempt context and does not fail parse. Parser
`ParseClassification.ADMITTED` / `PROVIDER_ERROR` is parser-only.

### Command evidence

```
uv run pytest -q tests/test_dataforseo_ai_optimization_llm_mentions_historical.py
```

exit 0, **49 passed**.

```
uv run ruff check .
```

exit 0, all checks passed.

```
uv run mypy src
```

exit 0, no issues in 36 source files.

### Strongest / weakest

Strongest: golden fixture SHA/length plus exact twelve-point IR; Decimal-safe mutation
encoder; extra/missing/shuffle assertions that keep Attempt `date_from`/`date_to`
unchanged; provider-error IR retains echo/`result_count` and leaves items unparsed;
closed Attempt parameter keys including rejection of TM `internal_list_limit`.

Weakest: synthetic `_encode` compact-JSON mutations are not pretty-printed like the
fixture; they prove semantics, not provider whitespace. Top-level success with task
failure follows Target Metrics (`PROVIDER_ERROR`) rather than treating both
inconsistency directions as hard parse failures.

### Possible false greens

- Compact `_encode` could hide pretty-print-only fixture bugs; golden tests use raw
  fixture bytes.
- Hash-isolation of other fixtures proves those files are unchanged, not that their
  parsers still run.
- `Decimal("0.1010") == Decimal("0.101")` is numeric equality, not lexical identity.

### Remaining caller-controlled influence

The public function takes caller-supplied `parameters`. Closed-key validation rejects
unknown keys and wrong contract before body success. Body bytes are caller-supplied
test/derive input; they are not live Evidence.

### Architecture drift / coupling

Historical parser is a new module. It imports `HISTORICAL_ADAPTER_CONTRACT` and
`ParseClassification` only. It does not import TM/SM/Organic parse functions or the
paid-probe module. JSON/int/Decimal helpers are deliberately duplicated.

### Parser / provider traps

Pretty-printed `0.101` must not go through binary float. Month is unpadded JSON
integer. Result has no `total_count`/`offset`. Extra/out-of-window months parse.
Duplicates fail. No Provider Update Time and no `YYYY-MM` construction.

### Deferred work

Recipe, Observation identity, completeness vs requested window, derive, schema, API,
Outcomes/Holdings, F12/F13, other platforms. No recapture.

### Reuse vs remain duplicated

Reuse later: closed-object + Decimal decode pattern, Attempt-vs-echo split,
parser-only `ParseClassification`. Remain duplicated: Historical field table, monthly
point IR (`mentions` + `ai_search_volume`, not SM `search_volume`), window strings
on request context.

### Confirmation

Zero provider, DNS, credential, account, pricing, restic, rclone, or public-network
calls other than reading the already protected local Evidence Store through the
read-only inspector. Zero Evidence mutation. Zero PostgreSQL mutation. No Recipe,
schema, API, or other-parser edits. No amend. No push.

## Remediation report

**Parent:** `eea893d97c93feeadd49581aace59a7588e0daef`  
**Child:** this remediation commit  
**Status:** `review`

Two Steward findings only:

1. Mixed root/task success now fails with `HistoricalParseError("inconsistent_status")`
   in both directions. Only both-non-20000 returns parser `PROVIDER_ERROR`.
   `tasks_error` is still reconciled from task status before that check.
2. Consistent provider-error tests now plant success-path-invalid `result` content
   (unknown member, `items=null`, `items_count` mismatch). Parse still returns
   `PROVIDER_ERROR` with echo and `result_count` retained and `items`/`items_count`
   `None`.

Targeted suite: **51 passed**. `uv run ruff check .` passed. `uv run mypy src` passed
(36 files).

Changed paths: parser module, parser tests, this ticket. Fixture bytes/SHA-256
unchanged (`5246` /
`4419daf0b7076625129ab18c6bf3c83905b998c3b3332f2ba6d42c8879b50781`).

No provider, DNS, credential, Evidence, or PostgreSQL activity. No fixture recopy.
No amend of `eea893d`. No push.
