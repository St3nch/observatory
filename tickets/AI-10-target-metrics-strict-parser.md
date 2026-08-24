# AI-10 — Target Metrics strict parser and AI-09 conformance fixture

**Status:** accepted  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** AI-09 — Target Metrics Live one-shot Evidence activation (`done`)  
**Approved by:** Project Steward  
**Start commit:** assigned in the Steward handoff  

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

[GROK fills this section in the single implementation commit.]

