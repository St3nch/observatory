# AI-04 — Search Mentions strict parser and AI-03 conformance fixture

**Status:** review  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; GROK technical review reconciled  
**Approved by:** Project Steward  
**Review-ticket commit:** `7f4c57b82d16625193456f5a9e3527841a96b5ef`  
**Start commit:** `3c79a555ec0e97d3326407233022e4ccfe380f5f`  

## Purpose

Build the zero-network interpretation boundary for the exact closed adapter
`dataforseo-ai-optimization-llm-mentions-search-mentions-live-paid-probe-v1`.
Copy the verified AI-03 response bytes through the existing read-only inspector into one
frozen deterministic Conformance fixture, then parse those bytes into a strict typed
in-memory Search Mentions representation with bounded adversarial proofs.

AI-04 does not create a Derivation Recipe, Observation identity, PostgreSQL schema or rows,
derive command, selection rule, history/API route, continuation workflow, recurring
acquisition, or another AI Optimization surface. Those boundaries remain AI-05 and later.

## Authority and accepted foundation

- D11 — provider interpretation and Observation identity restraint.
- D12 — claimed contract, bounded real Evidence, Conformance fixture, and recipe remain
  distinct.
- D13 — useful coverage direction does not bypass bounded activation.
- `docs/specs/capture-event-v2.md` provider interpretation sections.
- AI-01 selected Search Mentions Live / Google as the first bounded AI Optimization
  contract.
- AI-02 closed the Evidence-only one-shot adapter.
- AI-03 closed the one authorized live exchange and its off-host restore proof.

AI-03 and the independent GROK payload audit both recommend
`PROCEED_WITH_AI04`. D12 rejects extra paid calls merely to increase sample count after
the material authorized branch is exercised. AI-04 authorizes no provider, DNS, credential,
account, paid-host, or other external network access.

## Exact fixture provenance

Read the response only through the existing verified local inspector:

- Evidence root:
  `/home/chaz/.local/share/observatory/ai03-search-mentions-generative-engine-optimization-2026-08-20`;
- Attempt:
  `2a363a7bb07c27e55301d604afb1d06fda817760635943c68bcb4b567f9f7d03`;
- Capture:
  `bea666f9b982054df287da253fb49b0e0a9c1022b461c111a483b43d8606d4db`;
- exact response bytes: `48466`;
- exact response SHA-256:
  `8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`.

The committed fixture must be byte-identical to inspector stdout. Tests must prove its byte
length and SHA-256 independently and must never depend on the operator Evidence root after
the copy is established. The Conformance fixture is test material, not Evidence authority.

Proposed fixture path:

`tests/fixtures/dataforseo_ai_optimization_search_mentions_ai03.json`

## Verified real testimony

The exact body proves one HTTP-complete, provider-successful, Google offset-zero result:

- root/task provider status `20000`; one task; one result;
- exact decimal cost lexical form `0.105` at root and task;
- result keys are exactly the observed `total_count`, `offset`,
  `search_after_token`, `items_count`, and `items`; no `current_offset`;
- `total_count=3055`, `offset=0`, `items_count=5`, and five returned items;
- non-null 628-character continuation token, retained but never followed;
- five provider questions: `enception`, `mathematical artificial intelligence`,
  `search engine optimized`, `seos`, and `engine optimization service`;
- those questions are answer-scope word-match hits, not replacements for the requested
  keyword `generative engine optimization`;
- current AI search volumes `368000`, `201000`, `135000`, `110000`, `110000`;
- five large Markdown answers, five independent first/last provider clock pairs, and five
  `is_web_search_based=true` values;
- 48 ranked structured sources distributed `7/14/13/4/10`;
- 60 monthly points, 12 per item, with per-item windows;
- current volume disagrees with the newest monthly value for three items;
- item fields `search_results`, `brand_entities`, and `fan_out_queries` are JSON null
  for all five Google items;
- source fields `publication_date`, `thumbnail`, and `markdown` are JSON null for all
  48 sources;
- all 48 exact source URLs are unique in this fixture, while repeated domains and answer
  Markdown links that do not equal structured source URLs are real testimony.

One body proves existence, not invariance. In particular it does not prove that URL
duplicates cannot occur, provider order is identity, current volume derives from monthly
points, result completeness follows transport completeness, or null-only fields can never
be stated.

## Parser boundary

Implement a dedicated Search Mentions parser module. Do not extend the fixture classifier,
Keyword Overview parser, Google Organic parser, or the paid acquisition adapter into this
interpretation boundary. Reuse small accepted value types only where that does not create a
shared provider-parser framework.

The parser must:

- strict-decode UTF-8;
- reject a UTF-8 BOM, invalid UTF-8, duplicate JSON object member names, trailing
  non-whitespace material, and non-finite JSON constants;
- parse structural integers as real integers, rejecting booleans and floats;
- parse known decimal-capable cost fields with `Decimal` or an equivalent non-binary
  representation, never through binary float; equal JSON numeric values compare equal and
  AI-04 does not retain original numeral spelling;
- consume only verified complete response-body bytes plus verified Attempt parameters; the
  parser accepts no HTTP status or transport-state input;
- classify root/task JSON provider status independently from transport and validate the exact
  one-task/one-result successful branch and all declared counts;
- preserve duration strings as durations, never as timestamps;
- parse provider response clocks under the observed
  `YYYY-MM-DD HH:MM:SS +00:00` grammar with real calendar validation;
- retain the continuation token as an opaque null-or-string field and never decode it;
- use the verified Attempt parameters as request authority;
- parse `task.data` as a closed provider-echo object, retain it in the IR, and never use it
  to fill or override verified Attempt context; echo disagreement remains visible and does
  not by itself rewrite or reject item context;
- never substitute token internals, provider item order, or a returned question for the
  requested context;
- reconcile every item’s Google platform, location `2840`, and language `en` against the
  verified Attempt context;
- retain exact returned question and exact Markdown answer independently of the requested
  keyword;
- preserve exact URL, domain, source display name, title, snippet, query string, fragment,
  and provider rank;
- never extract or admit answer Markdown links as structured sources;
- preserve current AI search volume separately from every monthly point;
- preserve each monthly `(year, month, search_volume)` as provider-stated Data Period
  testimony, not Capture time;
- preserve JSON null, stated value, and permitted absence distinctly wherever the typed IR
  supports more than one state;
- treat every known AI-04 response object as closed: an unknown member name fails
  deterministically; AI-04 emits no extension diagnostics and does not classify any object
  as extension-permitted;
- return deterministic parse failure/classification for known-field, status, count,
  context, or structural drift.

Proposed production module:

`src/observatory/dataforseo_ai_optimization_search_mentions.py`

## Typed IR requirements

The full in-memory representation must retain enough exact testimony for AI-05 to design a
Recipe without rereading ad hoc JSON.

Envelope/task/result retains root version/status/message/duration/exact cost/task counts;
task ID/path/status/message/duration/exact cost/result count; typed task-data testimony
without making the echo request authority; and result total count, offset, item count, and
exact opaque continuation state.

Request context retains requested keyword; `match_type`, `search_filter`,
`search_scope`; requested platform, location, language, limit, and offset; and provenance
sufficient for later reconciliation without creating Observation identity here.

Each item occurrence retains non-identity provider order testimony, platform, model,
location, language, exact question, exact answer, current volume, first/last provider
clocks, web-search boolean, explicit states for the three null-only item fields, monthly
points, and structured source occurrences.

Each source occurrence retains per-item provider rank, exact title/URL/domain/source
name/snippet, and explicit states for publication date, thumbnail, and source markdown.
There is no URL/domain deduplication and no Markdown-link synthesis.

AI-04 must not declare natural Observation identities. Item index, source array index, result
order, continuation-token contents, task echo, and answer-link position are forbidden as
semantic identity claims. Duplicate question strings and duplicate exact URLs must remain
representable as distinct parser occurrences for AI-05 to reconcile deliberately.

## Reconciled field-state decision

- On this Google adapter, `search_results`, `brand_entities`, and
  `fan_out_queries` are required known keys whose only supported value is JSON null. A
  non-null value is unsupported Google contract drift and fails closed; AI-04 does not
  import another platform’s shape.
- Source `publication_date`, `thumbnail`, and `markdown` are required known keys with
  null-or-stated-string typed states under the claimed optional source contract. JSON null
  is the only live state observed. Synthetic strings are preserved opaquely; publication
  date is not parsed as a clock. Objects, arrays, numbers, and booleans fail closed.
- Missing required known keys fail rather than silently becoming JSON null or absence.
- Every AI-04 object is closed. Extension-permitted policy and additive diagnostics belong
  to AI-05’s first normative Recipe.

## Reconciliation and ordering rules

- The verified Attempt keyword remains requested query context; none of the five returned
  questions is rewritten or rejected for differing from it.
- `search_scope=["answer"]` means answer-scope matches are valid even when the question
  contains none of the requested words.
- Item order is preserved as occurrence testimony but does not create identity or a
  secondary sort rule.
- Equal `ai_search_volume` values do not authorize an invented tie-break.
- Source rank is scoped to one returned item. Rank is not Capture-wide and never equals
  source array index by definition.
- Source rank must be a positive JSON integer, unique within an item, independent of array
  index, and contiguous from one through the item’s source count. Duplicate, zero, negative,
  boolean, float, and positive-gap ranks fail closed. Reordering a source array preserves
  each exact `(url, rank)` pair; the parser never renumbers ranks.
- Monthly identity is the explicit provider period, never array position. Reordering monthly
  arrays must not rewrite periods. Duplicate periods and invalid calendar months fail.
- Item and source duplicates are preserved; the parser does not deduplicate by question,
  URL, domain, title, source name, or array position.
- `total_count` describes the provider’s larger result population. A transport-complete
  five-item body with `total_count=3055` is explicitly truncated result testimony, not a
  complete corpus or an absence claim.

## Required fixture proofs

The exact AI-03 fixture must prove:

- exact bytes and SHA-256;
- exact root/task/result topology and one successful result;
- `offset` exists and `current_offset` does not;
- `items_count=5`, `len(items)=5`, `total_count=3055`;
- exact continuation token preserved without decoding;
- exact five questions in provider order and none substituted with the requested keyword;
- exact current volume vector and three real current/monthly disagreements;
- exact source counts `7/14/13/4/10`, all 48 exact URLs, and ranks attached to the correct
  item;
- exact 12 monthly points per item and per-item window variation;
- exact null states for the six null-only field families;
- Markdown answers preserved through parse, including non-ASCII;
- execution durations, provider clocks, Data Periods, Capture provenance, and cursor token
  time-like text remain distinct concepts.

## Required bounded adversarial proofs

At minimum test:

- duplicate JSON member, invalid UTF-8, BOM, trailing bytes, `NaN`/infinity;
- missing known fields and unknown additive fields at every layer; all fail closed;
- root/task success disagreement, provider error, task/result count errors, two tasks, and
  two results; provider status classification uses JSON only and accepts no HTTP argument;
- `items` missing, null, and wrong type fail; `items=[]` with `items_count=0` parses as
  a stated successful empty page whether `total_count` is zero or greater;
- `items_count != len(items)`, `total_count < items_count`, negative/bool/float counts,
  and offset disagreement with the verified Attempt;
- `current_offset` added or substituted for `offset`;
- required continuation key as JSON null or nonempty string; missing, empty string, and
  wrong type fail; no token interpretation;
- item platform/location/language disagreement with Attempt context;
- returned questions without requested words remain valid;
- duplicate question occurrences remain distinct;
- source reorder preserves exact `(url, rank)` pairs; repeated, zero, negative,
  boolean, float, and positive-gap ranks fail; duplicate exact URLs within one item and
  across items remain distinct occurrences;
- URL query/fragment preservation and malformed required URL;
- Markdown with CDN, Google-search, and unrelated links never creates structured sources;
- monthly reorder, duplicate period, invalid month `0/13`, wrong/negative volume, and
  per-item windows that differ; a required empty array is a stated empty series, while null
  or missing fails; fixture-specific tests alone require 12 points;
- current volume integer zero, wrong type, and disagreement with newest monthly point;
- timestamp lexical/calendar failures, non-UTC offsets, and last before first;
- `is_web_search_based=false` accepted and non-boolean rejected;
- non-null Google-only item fields fail under the reconciled field-state decision;
- source optional fields exercise null, supported stated form, missing, and wrong type;
- equivalent integer/decimal/exponent JSON number forms and high precision prove cost is
  parsed without a binary-float round trip; tests assert Decimal value, not original numeral
  spelling;
- existing Keyword Overview, Google Organic, acquisition identities, and frozen fixtures
  remain unchanged.

Synthetic mutations prove parser behavior, not that those variants occurred in AI-03.

## Acceptance criteria

- A byte-identical AI-03 Conformance fixture is committed at the recorded length and digest.
- A dedicated strict parser emits a complete typed IR for all five items, 48 sources, and
  60 monthly points with the request/result distinction intact.
- Known provider quirks and null states are preserved rather than corrected.
- All count, status, known-field, context, numeric, period, time, and structural failures
  are deterministic and zero-network.
- Every known object is closed; unknown additive fields and known-field drift fail
  deterministically. Extension policy is deferred to AI-05’s Recipe.
- Provider order and array indexes are not semantic identities.
- Duplicate questions and URLs remain representable and are not silently collapsed.
- The exact continuation token is opaque testimony and no continuation request exists.
- The parser creates no PostgreSQL rows and no Recipe/Observation identity.
- Ordinary tests perform zero provider, DNS, credential, paid-host, or other public-network
  activity.
- `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` are clean.
- Implementation is one commit from the exact ready-transition HEAD supplied in the
  Steward handoff and stops for Steward review without push.

## Explicit non-goals

- another provider exchange or Evidence root;
- continuation/page-two support;
- ChatGPT or another platform;
- Target Metrics or another AI Optimization surface;
- Derivation Recipe or Observation identity;
- PostgreSQL migration, persistence, derive dispatch, selection, API, or history;
- recurring capture, scheduler, F6 automation, F7 concurrency, or F12 orchestration;
- Markdown citation extraction, URL normalization, domain/entity consolidation, scoring,
  strategy, or recommendations;
- refactoring existing provider parsers into a shared framework.

## GROK technical-review reconciliation

GROK independently reverified the fixture identity and returned
`READY_AFTER_TICKET_RECONCILIATION`; no new live Evidence is required.

Accepted corrections:

- AI-04 has no Recipe and therefore no extension-permitted object policy or additive
  diagnostics. Every object is closed until AI-05 versions a different semantic rule.
- Source ranks are positive, per-item, unique, contiguous, reorder-stable field testimony;
  they are never inferred from array index or renumbered.
- Costs preserve exact decimal value without binary float, not the original JSON spelling.
- Empty items and empty monthly arrays have explicit stated-empty semantics; required null,
  missing, malformed, and count-disagreement cases fail.
- The parser consumes verified body bytes and Attempt parameters, not HTTP status or
  transport state. Provider errors are JSON classifications.
- `task.data` remains typed provider echo testimony, never request authority. Echo
  disagreement does not replace Attempt context.
- Google-null item fields and null-or-opaque-string source fields follow the reconciled
  rules above.
- Duplicate questions and URLs remain separate IR occurrences. No
  `within_capture_result_id`, URL deduplication, or persistence identity is introduced.
- Token opacity is proved by exact string retention and refusal of missing, empty, or
  wrong-typed forms, never by asserting decoded internals.
- Golden contiguous ranks cannot alone prove rank/index separation; the decisive test
  reorders sources and preserves exact `(url, rank)` pairs.
- Markdown-link mutations must leave the structured source collection unchanged.
- The implementation must reuse only small accepted IR/value types, not another parser’s
  parsing functions, recipe, or surface structures.

Carried limits are explicit: another offset-zero sample would only resample this branch;
continuation and other platforms are distinct contracts; optional and adversarial variants
remain synthetic until separately activated Evidence exists.

## Next ticket boundary

After accepted implementation and Steward closure:

1. AI-05 — Derivation Recipe, semantic identities, typed PostgreSQL persistence, and
   rebuild proof;
2. AI-06 — read/history API.

Target Metrics remains a separate later surface. AI-04 does not authorize it.

## Implementation report

**Parent:** `3c79a555ec0e97d3326407233022e4ccfe380f5f`
**Child:** this implementation commit
**Status:** `review`
**AI-04 only:** yes. Nothing pushed.

Loaded skills:

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_ai_optimization_search_mentions.py` (new parser/IR)
- `tests/test_dataforseo_ai_optimization_search_mentions.py` (new)
- `tests/fixtures/dataforseo_ai_optimization_search_mentions_ai03.json` (inspector stdout copy)
- this ticket (Start commit, Status, Implementation report)

### Fixture provenance

Copied from local inspector stdout for Capture
`bea666f9b982054df287da253fb49b0e0a9c1022b461c111a483b43d8606d4db`.
Length `48466`. SHA-256
`8b3cd0fb0c9fa23c102696bfe6b7212396c0f7c110e9ca8ca5b8ee5af182e80a`.
No pretty-print, no regeneration, no token decode.

### Parser interface

`parse_search_mentions(body: bytes, parameters: Mapping) -> SearchMentionsIR`

No HTTP status or transport-state argument. Provider success/error is JSON
`status_code`. Request context is Attempt parameters. `task.data` is typed echo.

### Acceptance-to-test mapping

| Acceptance | Test |
|---|---|
| Fixture length/digest | `test_frozen_fixture_independent_sha256_and_length` |
| Signature has no HTTP input | `test_parser_signature_has_no_http_or_transport_input` |
| Golden IR / request vs result | `test_golden_parse_preserves_request_result_distinction` |
| Answer-scope hits, not `question != keyword` only | `test_questions_are_answer_scope_hits_not_merely_unequal_to_keyword` |
| Rank independent of index | `test_source_reorder_preserves_url_rank_pairs` |
| Markdown ≠ sources | `test_markdown_links_do_not_become_sources` |
| Decimal cost, not spelling | `test_cost_decimal_value_ignores_numeral_spelling`, `test_high_precision_cost_does_not_use_binary_float` |
| Echo ≠ Attempt | `test_echo_disagreement_does_not_replace_attempt_context` |
| Duplicate question/URL occurrences | `test_duplicate_questions_and_urls_remain_distinct` |
| Empty page admitted | `test_empty_items_with_zero_count_is_admitted` |
| Empty monthly series | `test_empty_monthly_array_is_stated_empty_series` |
| Closed unknown keys / `current_offset` | `test_unknown_result_and_item_fields_fail_closed` (includes `/tasks/0/data` and `/tasks/0/data/target/0`) |
| BOM/UTF-8/dup/trailing/NaN | `test_duplicate_json_member_invalid_utf8_bom_trailing_and_nonfinite` |
| Missing keys | `test_missing_known_fields_fail` |
| JSON provider error | `test_provider_error_and_inconsistent_status` (synthetics now set `tasks_error=1`) |
| Declared `tasks_error` vs one task status | `test_wrong_tasks_error_fails_on_success_and_provider_error` |
| Nonnegative `result_count` on every declared branch | `test_negative_result_count_fails_including_provider_error` |
| Count/offset errors | `test_task_and_result_count_errors`, `test_items_null_wrong_type_and_count_mismatches` |
| Token null/empty/wrong type | `test_continuation_null_empty_and_wrong_type` |
| Item context | `test_item_context_mismatch_fails` |
| Ranks | `test_invalid_source_ranks_fail`, `test_duplicate_and_gap_ranks_fail` |
| URL http(s)+host, no spaces, exact preservation | `test_malformed_url_and_query_fragment_preservation` |
| Google-null fields | `test_google_null_item_fields_reject_non_null` |
| Source optionals opaque string | `test_source_optional_fields_null_string_missing_and_wrong_type` |
| Monthly periods | `test_monthly_reorder_duplicate_invalid_and_null` |
| Volume zero / type | `test_current_volume_zero_and_wrong_type` |
| Clocks | `test_timestamp_failures` |
| `is_web_search_based` | `test_web_search_boolean` |
| Isolation | `test_existing_fixtures_and_parsers_unchanged` |

### Steward remediation (findings 1–3)

Independent investigation confirmed all three findings. No material disagreement. Product code changed only for findings 1 and 2; finding 3 was a missing proof of already-closed echo objects.

#### Finding 1 — `tasks_error` not reconciled — **confirmed real**

Parser type-checked `tasks_error` and rejected negatives, then stored whatever nonnegative integer was declared. It never required that count to equal the number of non-success task statuses. With the adapter’s exactly-one-task envelope that means `0` iff task JSON status is `20000`, else `1`.

False-green path: golden fixture has `tasks_error=0` with status `20000`, so the success branch never mutated the count. Provider-error synthetics flipped root/task `status_code` to `40100` and left fixture `tasks_error=0`, then asserted `PROVIDER_ERROR`. Impossible envelopes were therefore admitted:

- task status `20000` with `tasks_error=1` or `2` → `ADMITTED`
- task status `40100` with `tasks_error=0` → `PROVIDER_ERROR`

`result_count` on the success branch failed negatives only because `-1 != len(result)` (`count_mismatch`). The provider-error branch returned `_error_ir` with `result_count=-1`. Booleans and floats were already rejected by `_require_int`.

Smallest fix: after reading the one task’s JSON status and `result_count`, require `result_count >= 0` on every declared branch, then `tasks_error == (0 if task_status == 20000 else 1)`. Success-branch equality of `result_count` with result length is unchanged and still runs only after both statuses are `20000`. Provider status remains JSON-only; no HTTP/transport argument.

#### Finding 2 — source URL validation too weak — **confirmed real**

`_require_url` accepted any `urlparse` scheme with nonempty netloc and did not reject spaces. `ftp://host.example/path`, `javascript://host`, and `https://example.com/path with space` were admitted. `not-a-url` already failed because it has empty scheme/netloc, so the existing malformed-URL test was green while the accepted Google Organic absolute HTTP(S) boundary was not enforced.

Smallest fix: require scheme exactly `http` or `https`, nonempty netloc, and no spaces; return the original URL text unchanged (query and fragment included). Do not import Organic’s helper.

#### Finding 3 — unknown field proofs missing at echo layers — **confirmed as a proof gap**

`_parse_echo` already `_reject_unknown` on `task.data` and each `task.data.target` object. Tests planted unknown keys at root, task, result, item, source, and monthly, but not at `/tasks/0/data` or `/tasks/0/data/target/0`. A later weakening of echo closedness would not have been caught. No extension-diagnostics policy was added; every AI-04 object remains closed.

### Remediation-to-test map

| Steward requirement | Test |
|---|---|
| Wrong `tasks_error` on success (`20000` + `tasks_error=1`) | `test_wrong_tasks_error_fails_on_success_and_provider_error` |
| Wrong `tasks_error` on provider-error (`40100` + `0` or `2`) | same |
| Provider-error synthetics internally consistent | `test_provider_error_and_inconsistent_status` now sets `tasks_error=1` |
| Negative `result_count` on success | `test_negative_result_count_fails_including_provider_error` |
| Negative `result_count` on provider-error | same |
| Boolean/float `result_count` still rejected, including error branch | same (`True`, `1.0`) |
| Non-HTTP source scheme | `test_malformed_url_and_query_fragment_preservation` (`ftp://host.example/path`) |
| Spaced/malformed URL | same (`https://example.com/path with space` and retained `not-a-url`) |
| Query/fragment preservation | same; also asserts parsed URL vector equals fixture URL vector |
| Unknown member in `/tasks/0/data` | `test_unknown_result_and_item_fields_fail_closed` (asserts pointer `/tasks/0/data/unexpected`) |
| Unknown member in `/tasks/0/data/target/0` | same (asserts pointer `/tasks/0/data/target/0/unexpected`) |

### Checks

Targeted: `uv run pytest -q tests/test_dataforseo_ai_optimization_search_mentions.py` — 38 passed in 0.14s after remediation (red-then-green on findings 1–2; finding 3 proofs were already closed in product code).

`uv run pytest -q`: 1005 passed, 1 skipped, 1 warning in 155.62s

`uv run ruff check .`: All checks passed

`uv run mypy`: Success: no issues found in 52 source files

Leftover `observatory-ce05-*` containers: none.

### Scope confirmations

- No acquisition/capture-event/existing parser/fixture/migration/derive/API/authority edits except this ticket.
- Fixture bytes unchanged.
- No Recipe, PostgreSQL, Observation identity, or `within_capture_result_id`.
- No provider/DNS/credential/paid-host/continuation/second-surface/push.

### Review vs parent `3c79a555`

Standards: no hard violations; parser duplicates KO decode/closed-object helpers rather than importing KO parse functions (ticket-required isolation). URL rule matches Organic’s accepted absolute HTTP(S) boundary by local duplication, not by importing `_require_http_url`.

Spec: golden path, closed-object failures including echo and echo-target, rank/index separation, echo vs Attempt, Decimal costs, empty-page admission, Google-null drift, `tasks_error` reconciliation on the one-task envelope, nonnegative `result_count` on admitted and provider-error branches, and http(s) source URLs are covered. Post-remediation two-axis review vs this parent: Standards 0 hard / 3 judgement (required helper duplication, KO `Field` import, IR `outcome` name — all pre-existing); Spec 3/3 findings implemented, 0 material misses. Echo unknown-key proofs now assert the JSON Pointers.

### Candid technical assessment

Strongest proof: the two-axis `tasks_error` adversarial (`20000`+`1` and `40100`+`0`) plus the provider-error `result_count=-1` case. Those were live false-greens, not coverage cosmetics. The ftp and spaced-URL failures are equally decisive against the old scheme+netloc check.

Weakest remaining assumption: `tasks_error` is interpreted only for the adapter’s exactly-one-task envelope as “0 if the one task JSON status is 20000 else 1”. Two-task bodies still fail earlier on `tasks_length`; this parser does not implement a general N-task error census. URL checking uses `urlparse` scheme/netloc plus a literal-space rejection and does not normalize, IDNA-map, strip credentials, or percent-decode; an encoded space (`%20`) remains admitted because it is not a literal space. That matches the Organic boundary this ticket was told to copy.

False-green risks that remain: (1) `_require_int`’s `isinstance(value, bool)` guard is still load-bearing because `bool` subclasses `int`; (2) echo-layer unknown-key proofs plant one extra member named `unexpected` and would not notice a newly introduced nested object that forgot `_reject_unknown`; (3) success-path `result_count=-1` previously failed for the wrong reason (`count_mismatch`); it now fails `invalid_number` before length equality, which is the intended invariant but means a regression that restored only length equality would still look green on that one case — the provider-error negative remains the load-bearing nonnegative proof.

Additional defect exposed during investigation: none beyond the three Steward findings. The earlier residual that `tasks_error < 0` cited `/tasks_count` was already stale in product code (`/tasks_error` was already used).

No fixture-byte change. No HTTP/transport inference. Status remains `review`. Nothing pushed.


