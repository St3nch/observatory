# PF-05 — DataForSEO Keyword Overview strict parser and PF-03 conformance fixture

**Status:** review
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** parser/conformance
**Blocked by:** none; PF-04 closed
**Approved by:** Project Steward
**Start commit:** `fc654cdf20102ade832c48b6be61415ac811baa6`

## What to build

Build a zero-network, provider-specific parser for the exact paid adapter contract
`dataforseo-labs-google-keyword-overview-live-paid-probe-v1`. Promote the verified PF-03
response bytes into a frozen deterministic test fixture and prove a typed in-memory
interpretation plus fail-closed adversarial cases.

This ticket writes no provider-derived PostgreSQL rows and exposes no provider API.

PF-05 parses and validates the **full first-surface typed intermediate representation**,
including the field families later persisted by PF-07. PF-07 must reuse this parser/typed
IR rather than adding a second provider parser. PF-05 also authors the first production
Keyword Overview **core recipe** for PF-06, whose emitted kinds are coverage and core
metrics only. Adding the PF-07 Observation kinds is a semantic expansion and therefore
uses a new extended recipe digest in PF-07; the PF-06 recipe is never mutated in place.

## Authority

- D11
- D12
- `docs/specs/capture-event-v2.md` — §Provider Derivation after F11
- PF-03 exact paid Evidence and read-only inspector
- PF-04 provider recipe/Observation foundation

PF-03 is the accepted Provider contract probe for this exact live adapter. PF-05 continues
from its verified Evidence plus the claimed provider contract and bounded synthetic
adversarial cases. It does not restart Keyword Overview reconnaissance and does not claim
contracts for request-disabled SERP/clickstream enrichment, Standard/asynchronous workflows,
or other DataForSEO endpoints.

## PF-03 fixture acquisition

Read the exact response bytes only through the existing verified read-only paid-probe
inspection path. Record exact byte length and SHA-256 in the deterministic test vector, then
copy those exact bytes into the test corpus. Tests must not depend on the operator Evidence
root after the copy is established.

No capture command, provider network, DNS, credentials, or paid host is permitted.

## Parser contract

Implement a narrowly named DataForSEO Keyword Overview parser; do not grow the fixture
`_classify_capture` / `_admit_ok_results` code into provider parsing.

The parser must:

- strict-decode UTF-8;
- reject duplicate JSON object member names;
- reject `NaN`, `Infinity`, `-Infinity`, and equivalent non-finite constants;
- parse JSON structural integers as integers and decimal lexical forms without binary-float
  normalization; known decimal-capable provider fields accept integer or decimal lexical
  input and normalize exactly to `Decimal` or equivalent exact decimal values;
- validate the DataForSEO v3 envelope and the adapter's exact one-task/one-result contract;
- distinguish `tasks[0].result[0].items` from `result_count` and `items_count`;
- distinguish response/task execution-duration strings from Provider Update Time;
- preserve exact provider-returned keyword text;
- reconcile items against exact requested keywords from the verified Attempt parameters,
  never against array indexes or provider `task.data` echoes;
- parse provider timestamps under a provider-specific rule, not Observatory's frozen
  timestamp serializer;
- classify each known object as closed or extension-permitted per the first recipe;
- return stable diagnostics for tolerated additive fields on extension-permitted objects.

## Reconciliation rules

- Exact requested keyword is request authority and eventual Observatory subject.
- Exact returned keyword is provider testimony.
- The recipe-defined provider normalization is used only for matching.
- Result item order is irrelevant.
- A documented omitted requested keyword is represented in the typed parse result as provider
  no-data/coverage absence, not drift.
- Duplicate returned items, unrequested returned items, or an ambiguous many-request-to-one-
  provider-key normalization fail reconciliation.

The PF-03 real response does not prove every documented normalization edge; tests must add
synthetic collision vectors without claiming those collisions occurred in PF-03.

## Acceptance criteria

- [ ] Exact PF-03 response bytes are frozen with recorded byte length and SHA-256 after
      verify-on-read inspection.
- [ ] The parser walks `tasks[] -> result[] -> items[]` correctly and is independent of item
      order.
- [ ] Every PF-03 requested keyword is reconciled to the correct returned item or an explicit
      no-data omission state without using request/result position.
- [ ] Decimal-capable values retain exact decimal meaning for integer-looking and decimal
      lexical forms.
- [ ] PF-03 provider update timestamps are parsed independently for the structures that state
      them; execution durations are not timestamps.
- [ ] Present values, legitimate zero, JSON null, permitted absence, and request-disabled
      data are distinguishable in the typed parse result where the recipe requires it.
- [ ] Provider quirks in the frozen response are preserved verbatim rather than corrected.
- [ ] Duplicate JSON keys, non-finite numbers, known-field type drift, bad timestamp/period,
      impossible counts, duplicate/unrequested items, and ambiguous reconciliation fail
      deterministically.
- [ ] A permitted unknown additive field produces a stable diagnostic and does not alter
      known typed values.
- [ ] Full ordinary test/lint/typecheck suite remains zero-network.

## Required adversarial tests

- reorder the real `items` array
- duplicate a returned keyword item
- remove one requested keyword item
- add an unrequested item
- normalization collision between two synthetic requested keywords
- mismatch `items_count` / `result_count`
- duplicate JSON member name
- `NaN` / infinity
- integer lexical form versus decimal lexical form for one decimal-capable field
- malformed Provider Update Time
- invalid historical `(year, month)`
- provider task status error inside HTTP-complete testimony
- known nullable field as value/null/absent
- disabled SERP/clickstream field state from Attempt parameters
- unknown additive field on extension-permitted object
- unknown field on a closed object

- `tasks` length other than exactly one and `result` length other than exactly one
- `items` missing, JSON null, and an empty list in the all-omitted/no-data case
- top-level success with task-level failure, and the inverse inconsistent status shape
- integer-looking `1300` versus decimal-looking `1300.0` on a decimal-capable field
- a decimal with enough precision to prove there is no binary-float round trip
- invalid UTF-8, UTF-8 BOM, and trailing non-whitespace data after the JSON document
- Provider Update Time missing versus explicitly JSON null where the recipe permits either
- duplicate historical `(year, month)` points inside one returned keyword item
- negative monthly search volume
- invalid month `0` / `13` and recipe-invalid year bounds

## Out of scope

- PostgreSQL provider Outcomes/Observations
- API routes or recipe selection
- Other DataForSEO endpoints/sandbox parsing
- Live contract tests
- Additional paid calls
- Cross-provider abstractions

## One implementation commit must prove

The exact real PF-03 body and bounded mutants deterministically parse into a strict typed
Keyword Overview interpretation without provider network or PostgreSQL side effects.

## Implementation report

**Parent:** `fc654cdf20102ade832c48b6be61415ac811baa6`  
**Child:** recorded in this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

**Changed paths:**
- `src/observatory/dataforseo_keyword_overview.py` (new; parser, typed IR, core recipe)
- `tests/test_dataforseo_keyword_overview.py` (new)
- `tests/fixtures/dataforseo_keyword_overview_pf03.json` (exact PF-03 body)
- `tests/fixtures/dataforseo_keyword_overview_core_recipe.jcs` (published core recipe JCS)
- this ticket (Status + Start commit + Implementation report)

No `derive.py`, `migrate.py`, API, or Evidence/Capture changes. No PF-06 persistence.

### Fixture establishment

Inspected `/home/chaz/.local/share/vedaops/observatory/pf03-paid-20260816T213724Z` through `inspect_paid_probe_body`. Attempt `c0da493c3a44f1f60bc21d7afaab290e852dadafa8157386b79bd58ebec07462`, Capture `b4fc36a7799b497d0d183a88449bf0a770ce741ec1f0d8eaade2d75c930154d5`. Copied exact body bytes (26270, `d91fdc7ab8acf429f0ff9c00bd7cdb725be1ba9585481af35d14f7c4e79a6d1c`). Ordinary tests hash the frozen file only.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Frozen PF-03 length/SHA-256 | `test_frozen_fixture_independent_sha256_and_length` |
| Walk items independent of order; all requested reconciled | `test_pf03_parses_all_requested_keywords_independent_of_item_order` |
| Quirks, decimals, clocks, monthly counts, request-disabled | `test_pf03_preserves_quirks_decimals_times_and_monthly_counts` |
| Duplicate / unrequested / omitted | `test_duplicate_unrequested_and_omitted_reconciliation` |
| Normalization collision | `test_synthetic_normalization_collision_fails` |
| Count/shape, tasks/result length | `test_count_and_shape_failures` |
| Items missing/null/empty | `test_items_missing_null_and_empty_no_data` |
| Task error / inconsistent status | `test_status_combinations` |
| Impossible calendar/time timestamps fail closed | `test_timestamp_and_period_failures` |
| Missing/null required envelope status/counts | `test_required_envelope_status_and_counts_fail_when_missing_or_null` |
| Duplicate member, NaN/Inf, UTF-8, BOM, trailing | `test_duplicate_member_nonfinite_utf8_bom_and_trailing` |
| Integer/decimal lexical + high precision | `test_decimal_lexical_forms_and_high_precision` |
| Timestamp/period/zero-month/duplicate/negative | `test_timestamp_and_period_failures` |
| Null/absent timestamp; extension vs closed unknown | `test_null_absent_timestamp_and_unknown_fields` |
| Known-field type drift | `test_known_field_type_drift_fails` |
| Unknown enum; populated disabled enrichment | `test_unknown_enum_and_populated_disabled_enrichment` |
| Core recipe digest/kinds | `test_core_recipe_published_digest_and_kinds` |

### Required vs optional envelope fields

Required by the claimed v3 live-envelope / one-task contract (missing or JSON null fails closed):

- root `status_code`, `tasks`, `tasks_count`, `tasks_error`
- task `status_code`
- on success: `result`, `result_count`, `items`, `items_count`

Intentionally optional (not admission-critical; absence is not treated as success):

- `version`, `status_message`, `time`, `cost`, task `id`/`path`/`data`/`time`/`cost`

`authorized_unresolved` is attempt-stage and is not representable in the PF-04 `admission.capture_outcomes` list. That schema was not expanded.

### Production core recipe

1662-byte JCS, SHA-256 `319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908`. Capture outcomes now include `observation_admitted_empty`. Emits only `coverage.v1` and `metrics.v1`. PF-07 kinds are absent.

### Checks

- `uv run pytest -q` — 740 passed, 1 skipped
- `uv run ruff check .` — clean
- `uv run mypy` — clean
- Ordinary tests remain zero-network; autouse socket guard in PF-05 tests

### Review

Code-review against `fc654cdf20102ade832c48b6be61415ac811baa6`.

**Spec:** reviewer claimed `YEAR_MIN=2000` rejects PF-03 year 2018; that is incorrect (2018 ≥ 2000). Valid findings fixed: omitted `returned_keyword` is absence not JSON null; omitted request-disabled states follow Attempt flags; type-drift test added; PF-07 family values asserted; year bounds named in recipe `data_period.rule`; ordinary tests no longer open the operator Evidence root; `foreign_intent` string is wrong-type; parser classification renamed off Outcome.

**Standards:** 0 remaining hard after those fixes. Residual judgement: one module owns parser+IR+recipe (ticket cut).

### Unproven limits

- Claimed-contract enums/year window are recipe semantics, not proven by PF-03 completeness.
- SERP/clickstream populated contracts are not observed; represented as request-disabled.
- Normalization is casefold+whitespace only; PF-03 did not exhibit a real collision.
- No PostgreSQL provider writes.

### Implementer judgement

Weakest area: year/enum closures and keyword normalization are claimed-contract choices informed by one Capture. PF-03 is existence proof, not invariance (D12). The parser is ready for PF-06 persistence of coverage/metrics only.

## Closure

<!-- Project Steward only -->
