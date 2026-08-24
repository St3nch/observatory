# AI-10 — Target Metrics strict parser and AI-09 conformance fixture

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** AI-09 — Target Metrics Live one-shot Evidence activation (`done`)  
**Approved by:** Project Steward  
**Start commit:** `be6dd0b99272aadf5582da624709f2f79e5977f5`  

## Purpose

Build the zero-network interpretation boundary for the exact closed adapter
`dataforseo-ai-optimization-llm-mentions-target-metrics-live-paid-probe-v1`.
Copy the verified AI-09 response bytes through the existing read-only inspector into one
frozen deterministic Conformance fixture, then parse those bytes into a strict typed
in-memory Target Metrics representation with bounded adversarial proofs.

AI-10 does not create a Derivation Recipe, Outcome, Observation identity, PostgreSQL schema
or rows, derive command, recipe-selection rule, history/read API, recurring acquisition,
strategy output, or another provider exchange. Those boundaries remain AI-11 and later.

## Authority and accepted foundation

- VISION and VOCABULARY Evidence, Derivation, Observation, Provenance, and strategy
  boundaries.
- D11 — provider interpretation and Observation identity restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, parser, and Recipe
  remain distinct.
- D13 and `docs/dataforseo-surface-roadmap.md` — useful coverage does not bypass bounded
  activation or create strategy inside Observatory.
- `docs/specs/capture-event-v2.md` provider-interpretation and verified-body rules.
- AI-07 selected Target Metrics Live / Google as the next bounded AI Optimization contract.
- AI-08 closed the Evidence-only one-shot adapter.
- AI-09 closed the one authorized live exchange, byte-exact inspection, encrypted off-host
  snapshot, fresh-restore proof, payload assessment, and challenged technical review.
- AI-04's accepted Search Mentions parser is the closest structural precedent, including
  strict JSON decoding, one-task envelope checks, Decimal cost parsing, typed provider echo,
  parser isolation, and its later `tasks_error` remediation.

The official endpoint reference was rechecked on 2026-08-24:

<https://docs.dataforseo.com/v3/ai_optimization-llm_mentions-target_metrics-live/>

It claims the grouping row shape `key`, `mentions`, and `ai_search_volume` for
`location`, `language`, `platform`, `sources_domain`,
`search_results_domain`, `brand_entities_title`, and
`brand_entities_category`. Only the exact AI-09 Google states described below are real
Evidence. Claimed but unobserved branches remain synthetic parser proofs and are not
provider testimony.

AI-10 authorizes no provider, DNS, credential, account, paid-host, pricing, or other public
network access.

## Exact fixture provenance

Read the response only through the existing verified local inspector:

- Evidence root:
  `/home/chaz/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24`;
- Attempt:
  `1edeabd8d8a4dd0f396a02692c35718837885ec6f175a49ee4cb2556083fdcd5`;
- Capture:
  `347d8eebf6c706370f59dbdc7057ca95c03010bcb01b5edb8eade05bc0e1295e`;
- exact response bytes: `1775`;
- exact response SHA-256:
  `7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`.

The committed fixture must be byte-identical to inspector stdout. Tests must prove its byte
length and SHA-256 independently and must never depend on the operator Evidence root after
the copy is established. The Conformance fixture is deterministic test material, not
Evidence authority.

Required fixture path:

`tests/fixtures/dataforseo_ai_optimization_target_metrics_ai09.json`

## Verified real testimony

The exact body proves one HTTP-complete, provider-successful Google result:

- envelope version `0.1.20260806`;
- root/task statuses `20000` / `Ok.`, one task, no task error, one result;
- root and task cost `0.101`; duration strings `0.8758 sec.` and `0.8400 sec.`;
- task ID `08240309-1463-0651-0000-7982d3d5ec07`;
- path exactly `v3/ai_optimization/llm_mentions/target_metrics/live`;
- task data echoes exact adapter inputs: limit `10`, `en`, `2840`, `google`, and
  one included `generative engine optimization` keyword with `word_match` and
  `search_scope=["answer"]`;
- result keys exactly `total_count`, `offset`, `items_count`,
  `aggregated_metrics`, and `items`;
- `total_count=0`, `offset=0`, `items_count=0`, and real `items=[]`;
- documented `items=null` versus real `items=[]` is material field-state drift;
- `aggregated_metrics` has exactly eight known keys;
- singleton location `2840`, language `en`, platform `google`, and `total` each
  independently state `3061` mentions and `2336840` AI search volume;
- `sources_domain` has ten ordered rows with exact keys, mentions, and AI search volumes;
- `search_results_domain`, `brand_entities_title`, and
  `brand_entities_category` are present empty arrays;
- the source-domain mention sum `4415` and volume sum `3187610` exceed the total, proving
  overlapping histograms rather than a partition;
- no duplicate keys, zero aggregate values, decimal metrics, or unknown fields were observed.

One body proves existence, not invariance. It does not prove list truncation, completeness,
stable sort or tie-breaks, grouping equality, unique future keys, nonempty optional-list
states, `items=null`, omitted fields, alternate platform testimony, multi-group results,
or semantic/persistence identity.

## Parser boundary

Implement a dedicated Target Metrics parser module. Do not extend the paid adapter, Search
Mentions parser, Keyword Overview parser, Google Organic parser, fixture classifier, or
provider Derivation into this interpretation boundary. Reuse small accepted value types only
when that does not create a shared provider-parser framework.

Required production module:

`src/observatory/dataforseo_ai_optimization_target_metrics.py`

Required public parser shape:

`parse_target_metrics(body: bytes, parameters: Mapping[str, object]) -> TargetMetricsIR`

The parser accepts verified complete response-body bytes plus verified Attempt parameters.
It accepts no HTTP status, response headers, transport state, Capture classification,
Evidence path, credentials, client, URL, or network seam.

The parser must:

- strict-decode UTF-8;
- reject a UTF-8 BOM, invalid UTF-8, duplicate JSON object member names, trailing
  non-whitespace material, and non-finite JSON constants;
- parse structural and aggregate integers as real integers, rejecting booleans, floats,
  strings, and negatives;
- parse known decimal-capable cost fields with `Decimal` or an equivalent non-binary
  representation, never through binary float;
- preserve duration strings as durations, never timestamps;
- classify root/task JSON provider status independently from transport;
- require the adapter's exactly-one-task envelope, reconcile `tasks_count`, and require
  `tasks_error` to equal the number of non-success task statuses in that one-task
  envelope;
- require nonnegative `result_count` on every parsed provider-status branch;
- validate the successful one-result topology and declared counts;
- preserve task ID, path, status/message, durations, costs, and result count;
- use verified Attempt parameters as request authority;
- parse `task.data` as a closed typed provider-echo object, retain it independently, and
  never use it to fill or override verified Attempt context;
- make echo disagreement visible in the IR without turning echo into authority or declaring
  a repository Outcome;
- parse all known response objects as closed; unknown member names fail deterministically;
- return deterministic parser failure/classification for malformed JSON, known-field,
  status, count, numeric, or structural drift.

AI-10 creates parser classifications only. It does not create or emit the repository's
versioned Outcomes.

## Typed IR requirements

The complete in-memory representation must retain enough exact testimony for AI-11 to design
a Recipe without rereading ad hoc JSON.

Envelope/task/result IR retains:

- root version/status/message/duration/exact cost/task counts;
- task ID/path/status/message/duration/exact cost/result count;
- typed task-data echo, separate verified Attempt request context, and any disagreement;
- result `total_count`, `offset`, `items_count`, and exact `items` field state;
- all eight known aggregate structures independently.

Request context retains the exact requested keyword target, `match_type`,
`search_filter`, `search_scope`, platform, location, language, and
`internal_list_limit`. No response echo or grouping key replaces it.

Each aggregate row retains:

- its native key type: location integer; every other grouping key string;
- nonnegative integer `mentions`;
- nonnegative integer provider-specific `ai_search_volume`;
- zero-based `provider_array_index` as lexical array-order testimony only.

The required `total` retains independent nonnegative integer `mentions` and
`ai_search_volume`.

The parser must not rename `ai_search_volume` into Keyword Overview search volume, claim
that it shares Search Mentions item grain, calculate shares/concentration, normalize
domains, or declare natural Observation identities.

## Closed objects, field states, and unsupported meaning

- Root, task, task data, target, result, aggregate container, every aggregate row, and total
  are closed objects.
- `location`, `language`, `platform`, `sources_domain`, and `total` are required
  known aggregate members. Group arrays may be empty; `total` must be a stated object.
- `search_results_domain`, `brand_entities_title`, and
  `brand_entities_category` each preserve absent, JSON null, stated-empty array, and
  stated-nonempty array distinctly.
- A nonempty optional-list row uses the claimed closed
  `key`/`mentions`/`ai_search_volume` shape. It is synthetic contract coverage, not
  evidence that Google returned such rows. AI-10 does not decide whether AI-11 admits it.
- `items` preserves absent, JSON null, and stated-empty array distinctly. A nonempty array
  or any other value fails because this Target Metrics contract defines no item-row shape.
- Successful Target Metrics requires `total_count=0`, `offset=0`, and
  `items_count=0`; it does not borrow Search Mentions pagination or admitted-empty
  semantics.
- Missing a required total, wrong native key type, wrong metric type, or malformed known
  state fails deterministically.
- No parser branch synthesizes absent fields, coerces null to empty, or silently skips a
  known malformed row.

## Reconciliation, duplication, ordering, and completeness restraint

- The four overall location/language/platform/total values are preserved independently.
  Value disagreement is valid typed testimony and must not fail parsing.
- Grouping keys are retained independently from verified Attempt context. A syntactically
  valid but different location/language/platform key remains visible for AI-11
  reconciliation; AI-10 does not silently rewrite or classify it.
- Duplicate keys within any one aggregate array fail, even when metrics agree. A duplicate
  source domain is not an occurrence.
- `provider_array_index` is array position only. It is not rank, identity, a tie-break, or
  proof of provider ordering semantics.
- Reordering rows preserves each exact key/metric tuple and recomputes only lexical array
  position; it does not invent rank or sort.
- Source-domain metrics may overlap and must never be summed into, reconciled against, or
  required to partition `total`.
- Preserve the requested `internal_list_limit` and actual list cardinalities. Count equal
  to limit means only count-equals-limit; it must not become `truncated=true`.
- Counts below, equal to, or otherwise different from the requested limit remain explicit
  testimony. AI-10 makes no corpus-completeness claim and creates no comparable-series rule.
- A required stated zero total remains parseable testimony. It is not an absent result or an
  `observation_admitted_empty` decision.

## Required fixture proofs

The exact AI-09 fixture must prove:

- exact bytes and SHA-256;
- exact root/task/result topology and values;
- exact task-data echo and separate verified Attempt parameters;
- exact result counts and real `items=[]` state;
- exact eight-key aggregate topology;
- singleton location/language/platform and independent total values;
- exact ten source-domain rows in provider order, including all keys and metric pairs;
- zero-based lexical provider indexes without rank semantics;
- exact present-empty states for the three optional lists;
- overlapping source-domain sums greater than total without parser rejection;
- costs retain exact decimal value and durations remain non-time strings.

## Required bounded adversarial proofs

At minimum test:

- duplicate JSON member, invalid UTF-8, BOM, trailing bytes, and `NaN`/infinity;
- missing required fields and unknown additive fields at every object layer, including task
  data, target, aggregate container, each row family, and total;
- root/task success disagreement, provider error, wrong `tasks_count`,
  wrong `tasks_error` on success and error branches, negative/bool/float
  `result_count`, two tasks, and two results;
- Decimal integer/fraction/exponent/high-precision cost forms without binary-float
  round-trip;
- negative/bool/float/string structural counts and aggregate metrics;
- nonzero successful `total_count`, `offset`, or `items_count`;
- `items=[]`, `items=null`, and absent `items` remain distinct accepted states;
  nonempty and wrong-typed `items` fail;
- optional aggregate lists independently exercise absent, null, empty, nonempty claimed
  rows, and wrong types;
- nonempty optional rows remain typed even for this Google parser branch and are not silently
  admitted to persistence;
- total missing/null/wrong-shaped; group arrays missing/null/wrong-shaped where required;
- integer location key versus string/boolean/float; string keys versus non-string values;
- duplicate grouping keys with equal and unequal metrics;
- grouping value disagreement with total parses and remains visible;
- syntactically valid grouping-key disagreement with Attempt parses and remains visible;
- source-domain reorder preserves key/metric attachment and only changes lexical index;
- source count below and equal to `internal_list_limit` both parse without a truncation
  claim;
- overlapping domain sums greater than total remain valid;
- zero mentions and zero AI search volume, including required zero total, parse as stated
  values;
- existing Search Mentions, Keyword Overview, Google Organic, acquisition identities, and
  frozen fixtures remain unchanged.

Synthetic mutations prove parser behavior, not that those variants occurred in AI-09.

## Acceptance criteria

- The byte-identical AI-09 Conformance fixture is committed at the recorded length and
  digest.
- A dedicated strict parser emits complete typed IR for the real aggregate result, including
  one total, ten source domains, grouping arrays, exact field states, and request/echo
  separation.
- Known provider drift and null/empty/absent distinctions are preserved rather than
  corrected.
- All known objects are closed and malformed known fields fail deterministically.
- Group values are not forced to equal total; domain metrics are not treated as a partition.
- Duplicate histogram keys fail; no occurrence semantics are introduced.
- List-limit equality is not called truncation or completeness.
- Array position is lexical testimony only and no semantic identity is declared.
- The parser creates no PostgreSQL rows, Recipe, Outcome, Observation, projection, score, or
  strategy conclusion.
- Ordinary tests perform zero provider, DNS, credential, paid-host, or other public-network
  activity.
- `uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics.py` passes.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are clean on the exact
  implementation commit.
- Implementation is one commit from the exact Steward handoff HEAD, is not amended, is not
  pushed, and stops at `review` for independent Steward inspection.

## Changed-path allowlist

Only these paths may change:

- `src/observatory/dataforseo_ai_optimization_target_metrics.py` — new;
- `tests/test_dataforseo_ai_optimization_target_metrics.py` — new;
- `tests/fixtures/dataforseo_ai_optimization_target_metrics_ai09.json` — new byte-exact
  fixture;
- this ticket — Start commit, Status, and Implementation report only.

Do not modify any existing `src/`, test, fixture, migration, authority, dependency, or lock
file. If a required change falls outside this allowlist, stop and report it.

## Required skills and implementation report

Load and report these exact project-local skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

The implementation report must include:

- exact parent and child commits and final clean status;
- exact changed paths;
- fixture copy method, byte length, digest, and zero-network confirmation;
- parser public interface and main IR types;
- acceptance-to-test mapping;
- targeted/full pytest, Ruff, and mypy commands and exact results;
- strongest proof and weakest assumption;
- possible false greens and remaining caller-controlled influence;
- architecture drift, coupling, parser/provider traps, and deliberately duplicated seams;
- anything that should block closure;
- anything deferred to AI-11 or later;
- no amend, no push, no provider/API-host/credential/spend use.

## Explicit non-goals

- another provider exchange, Evidence root, inspector mutation, or Evidence rewrite;
- ChatGPT, another platform, another target, another list limit, Multi-Target, Historical,
  Timeseries, top-list, Lite, catalog, account, or User Data request;
- Derivation Recipe, Outcome classification, Observation identity, PostgreSQL migration or
  persistence, derive dispatch, selection, API, or history;
- domain normalization, cross-surface joins, shares, concentration, ranking, scoring,
  recommendations, reporting, or strategy;
- recurring capture, scheduler, routine F6 automation, F7 locking, or F12 orchestration;
- refactoring existing provider parsers into a generic framework.

## Next boundary

After accepted implementation, independent review, remediation if needed, exact-HEAD test
evidence, and explicit [CHAZ] closure authorization:

1. AI-11 — Target Metrics Derivation Recipe, semantic identities, typed PostgreSQL
   persistence, and rebuild proof;
2. AI-12 — Target Metrics recipe selection and read/history API.

AI-10 authorizes neither boundary.

## Implementation report

**Parent:** `be6dd0b99272aadf5582da624709f2f79e5977f5`  
**Child:** this implementation commit  
**Status:** `review`  
**AI-10 only:** yes. Nothing pushed. Nothing amended.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_ai_optimization_target_metrics.py` (new parser/IR)
- `tests/test_dataforseo_ai_optimization_target_metrics.py` (new)
- `tests/fixtures/dataforseo_ai_optimization_target_metrics_ai09.json` (inspector stdout copy)
- this ticket (Start commit, Status, Implementation report)

### Fixture provenance

Copied through the existing local read-only inspector, with stdout redirected
to the required fixture path:

```text
uv run python -m observatory.dataforseo_ai_optimization_target_metrics_paid_probe inspect
  --evidence-root /home/chaz/.local/share/observatory/ai09-target-metrics-generative-engine-optimization-2026-08-24
  --capture-id 347d8eebf6c706370f59dbdc7057ca95c03010bcb01b5edb8eade05bc0e1295e
```

Independent `hashlib.sha256` and `sha256sum` both measured length `1775` and
SHA-256 `7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`.
No pretty-print, no regeneration, no BOM, no trailing newline. Inspector CLI
does not load credentials and reads only the local Evidence Store. Ordinary
tests never open that operator root after the copy. Zero provider, DNS,
credential, paid-host, or other public-network activity.

### Parser interface

`parse_target_metrics(body: bytes, parameters: Mapping[str, object]) -> TargetMetricsIR`

No HTTP status, headers, transport state, Capture classification, Evidence
path, credentials, client, URL, or network seam. Provider success/error is
JSON `status_code`. Request context is verified Attempt parameters. `task.data`
is typed echo and never overrides Attempt context.

Principal IR types: `RequestContext`, `ProviderEcho` / `EchoTarget`,
`LocationRow`, `GroupingRow`, `TotalMetrics`, `AggregatedMetrics`,
`TargetMetricsIR`. Optional lists and `items` use reused `Field` states.
Parser classification reuses `ParseClassification` (`observation_admitted` /
`provider_error`) as in AI-04; this is not a repository Outcome.

### Acceptance-to-test mapping

| Acceptance | Test |
|---|---|
| Fixture length/digest, independent of Evidence root | `test_frozen_fixture_independent_sha256_and_length` |
| Signature has no HTTP/transport input | `test_parser_signature_has_no_http_or_transport_input` |
| Golden IR, request/echo split, eight aggregates, ten source-domain rows, present-empty optionals, overlap, lexical indexes, durations | `test_golden_parse_preserves_request_echo_and_aggregates` |
| Echo ≠ Attempt authority | `test_echo_disagreement_does_not_replace_attempt_context` |
| Grouping-key disagreement with Attempt remains visible | `test_grouping_key_disagreement_with_attempt_remains_visible` |
| Group values need not equal total | `test_grouping_value_disagreement_with_total_parses` |
| Domain metrics are not a partition | `test_overlapping_domain_sums_greater_than_total_remain_valid` |
| Reorder preserves key/metric tuples; index is lexical, not rank | `test_source_domain_reorder_preserves_key_metrics_and_reindexes` |
| Count below/equal/above limit is not truncation | `test_source_count_below_and_equal_to_limit_is_not_truncation` |
| Zero totals/metrics remain stated; not admitted-empty | `test_zero_totals_and_zero_metrics_are_stated_values` |
| Decimal cost, not spelling or binary float | `test_cost_decimal_value_ignores_numeral_spelling`, `test_integer_json_cost_is_decimal`, `test_high_precision_cost_does_not_use_binary_float` |
| BOM/UTF-8/dup/trailing/NaN/Infinity | `test_duplicate_json_member_invalid_utf8_bom_trailing_and_nonfinite` |
| Unknown fields at every closed object layer | `test_unknown_fields_fail_at_every_closed_object_layer` |
| Missing required fields, including language/platform/row members | `test_missing_known_fields_fail` |
| Root/task disagreement, provider error | `test_provider_error_and_inconsistent_status` |
| `tasks_error` on success and error branches | `test_wrong_tasks_error_fails_on_success_and_provider_error` |
| Nonnegative `result_count` on every branch | `test_negative_result_count_fails_including_provider_error` |
| Two tasks, two results, wrong `tasks_count` | `test_task_and_result_count_errors` |
| Nonzero successful `total_count`/`offset`/`items_count` | `test_nonzero_successful_result_counts_fail` |
| `items=[]` / `null` / absent distinct; nonempty/wrong-type fail | `test_items_empty_and_null_are_distinct_accepted_states`, `test_absent_items_is_distinct_from_null_and_empty`, `test_nonempty_and_wrong_typed_items_fail` |
| Optional lists absent/null/empty/nonempty/wrong-type | `test_optional_aggregate_lists_preserve_absent_null_empty_nonempty_and_wrong_type` |
| Nonempty optional rows typed, not persisted | `test_nonempty_optional_rows_are_typed_ir_not_persistence` |
| Required total/group arrays null/wrong-shaped; empty required arrays parse | `test_required_total_and_group_arrays_reject_null_and_wrong_shape` |
| Location integer key vs string/bool/float | `test_location_key_must_be_integer` |
| String grouping keys vs non-strings | `test_string_grouping_keys_reject_non_strings` |
| Structural counts reject bool/float/string/negative | `test_structural_counts_reject_bool_float_string_negative` |
| Aggregate metrics reject negative/bool/float/string | `test_aggregate_metrics_reject_negative_bool_float_string` |
| Duplicate histogram keys fail, including equal metrics and optional lists | `test_duplicate_grouping_keys_fail_even_when_metrics_agree` |
| Existing parsers, fixtures, and adapter identity unchanged | `test_existing_fixtures_and_parsers_unchanged` |

### Verification

On this implementation tree, before the commit:

```text
uv run pytest -q tests/test_dataforseo_ai_optimization_target_metrics.py
51 passed in 0.23s

uv run pytest -q
1164 passed, 1 skipped, 1 warning in 292.98s

uv run ruff check .
All checks passed!

uv run mypy
Success: no issues found in 60 source files
```

The warning is the existing Starlette `httpx` TestClient deprecation from
`fastapi/testclient.py`, not this ticket.

### Strongest proof

Independent fixture digest plus golden literals for the ten source-domain
rows, overlap sums, and distinct field states. Adversarial tests would go red
if the parser treated limit-equality as truncation, forced group=total,
accepted duplicate histogram keys as occurrences, or collapsed zero totals
into admitted-empty.

### Weakest assumption

One Google AI-09 body proves existence of the eight-key aggregate topology,
not invariance. Nonempty optional-list rows and `items=null` are synthetic
parser proofs, not provider testimony. Parser classification reuses
`ParseClassification.ADMITTED` (`observation_admitted`); AI-11 must not treat
that string as a repository Outcome or as Search Mentions admitted-empty.

### Possible false greens

- Isolation tests hash other fixtures and re-parse them; they do not prove
  absence of conceptual coupling via reused `Field` / `ParseClassification`.
- `not hasattr(..., "rank")` / `"truncated" not in dataclass fields` prove
  absence of those attributes, not that a caller cannot invent rank later.
- Network guard patches `socket.create_connection` only, matching AI-04.
- Source-text guards (`psycopg`, `provider_recipe`,
  `observation_admitted_empty`) are string checks on this module.

### Remaining caller-controlled influence

Attempt `parameters` are caller-supplied. The parser type-checks them and
requires the Target Metrics adapter contract, but it does not re-close
adapter-level constants such as `internal_list_limit=10`. Echo disagreement
is retained, not used as authority. AI-11 owns Recipe, reconciliation,
admission, and persistence.

### Architecture drift / coupling

Small accepted value-type reuse: `Field` and `ParseClassification` from
`dataforseo_keyword_overview`, plus `TARGET_METRICS_ADAPTER_CONTRACT` from
`capture_event`. No shared parser framework, no recipe, no derive, no
PostgreSQL, no API. Named aggregate fields rather than a dimension/EAV map.

### Parser/provider traps exposed

- Documented `items=null` versus real `items=[]`.
- Overlapping source-domain histograms versus a partition of `total`.
- Count-equals-`internal_list_limit` versus truncation/completeness.
- Integer location keys versus string grouping keys.
- Independent location/language/platform/total values that happen to agree
  in this body.
- Duplicate grouping keys are collisions, not occurrences.
- `provider_array_index` is array position, not rank.

### Deliberately duplicated seams

Strict JSON decode (UTF-8, BOM, duplicate members, trailing data, non-finite
numbers), closed-object rejection, Decimal cost parsing, one-task envelope,
and `tasks_error` reconciliation are copied into this module rather than
extracted from Search Mentions / Keyword Overview.

### Code-review residuals

- **Standards:** no hard violations. Judgement: location vs string-grouping
  row loops left unextracted so a generic keyed-row helper cannot become an
  EAV/dimension framework. `items` is `Field[tuple[object, ...]]` because
  this contract defines no item-row type.
- **Spec:** no wrong-implementation findings. Partial-proof gaps called out
  in review (missing `language`/`platform`/row members, echo target golden
  fields, above-limit cardinality) were closed before this commit.

Nothing here should block closure of AI-10. AI-11 remains the next boundary.

### Deferred to AI-11 or later

Derivation Recipe, semantic identities, typed PostgreSQL persistence, rebuild
proof, recipe selection, read/history API, whether nonempty optional rows are
admitted, whether grouping-key disagreement is a reconciliation failure, and
the repository Outcome for a stated zero total.

### Confirmations

No amend, no push, no provider/API-host/DNS/network call, no credentials, no
spend, no Evidence mutation, no Recipe/Outcome/Observation/PostgreSQL/
derivation/selection/API/history/projection/scoring/strategy work.

## Steward review and closure — 2026-08-24

[CHAZ] explicitly authorized closure after the implementation report, strategic addendum,
direct technical follow-up, independent Steward review, and exact-HEAD operator verification.
The Steward accepts AI-10 as `done`.

Accepted commits:

- final reviewed ticket / implementation parent:
  `be6dd0b99272aadf5582da624709f2f79e5977f5`;
- implementation:
  `60fa11dc10f53c536c6b73e8dcef9bf426be15e2`.

The exact parent/child comparison changed only the four allowed paths. The Steward read the
complete production parser and test file, verified the committed fixture independently as
`1775` bytes without a trailing newline and SHA-256
`7b6974704f73cff9687986a83ab14ba8ec942ccdbfde359ec7e8fde6bea8eee2`,
and found no wrong implementation or required remediation.

[CHAZ] returned exact-HEAD operator evidence on the implementation commit:

- targeted Target Metrics parser suite: `51 passed`;
- full suite: `1164 passed, 1 skipped, 1 warning`;
- Ruff: passed;
- mypy: passed;
- final tree: clean on the same commit.

The warning is the known Starlette/`httpx` TestClient deprecation. No provider call,
credential use, spend, Evidence mutation, PostgreSQL mutation, amend, or push occurred in
AI-10.

The challenged implementation review and direct follow-up established these mandatory
AI-11 guards:

1. Repository Outcome is created only by the accepted Recipe after verified transport,
   parse, reconciliation, and admission. Never assign it from
   `TargetMetricsIR.outcome.value`.
2. Do not copy Search Mentions' zero-envelope →
   `observation_admitted_empty` rule. Target Metrics success is aggregate testimony; a
   required stated total, including zeros, is not an empty page.
3. Production derivation must verify the Capture and its exact cited Attempt, require the
   Target Metrics adapter contract, revalidate the committed closed parameters, and pass
   only those parameters and the verified body to the parser. Never construct provenance
   context from provider echo, operator flags, an API query, an arbitrary Mapping, or
   another Attempt.
4. Never admit Observations from `ParseClassification.PROVIDER_ERROR`. Error-path
   `result_count` remains unreconciled provider testimony, not valid result topology; a
   later materially different error shape requires new bounded Evidence/Recipe review.
5. Grouping-key disagreement with the verified Attempt remains parser-visible but receives
   one explicit fail-closed, diagnostic, or admission rule in AI-11. Parser visibility is
   not semantic identity.
6. Nonempty optional grouping families, grouping/total disagreement, field-state
   persistence, Observation kinds/identities, and whether location/language/platform are
   facts or context remain AI-11 decisions. The parser does not settle them.

Accepted explicit limits remain: the one Google body proves existence rather than
invariance; it proves no truncation, completeness, stable order, partition, cross-platform
behavior, time series, provider Data Period, provider update clock, cross-surface identity,
or billing formula. Claimed nonempty optional rows and `items=null` remain synthetic parser
coverage, not live Google testimony.

This closure changes documentation and workflow authority only. No behavior-affecting change
followed the exact-HEAD test evidence, so the full suite was not repeated.

