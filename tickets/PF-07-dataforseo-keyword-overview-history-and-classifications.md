# PF-07 — Keyword Overview history, properties, backlinks, and intent

**Status:** review
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** provider derivation expansion
**Blocked by:** none; PF-06 closed
**Approved by:** Project Steward
**Start commit:** `ff55577fc039f8bc852f6ad06dba3d8d4fce504c`

## What to build

Complete the first Keyword Overview recipe's useful typed provider testimony beyond PF-06:
historical monthly search volume, provider-computed search-volume trends, keyword properties,
average backlink summary, and search intent. Preserve each structure's independent provider
time semantics and the exact provider quirks already present in Evidence.

PF-07 is a **new extended Keyword Overview recipe**, not an in-place mutation of PF-06's
core recipe. Its canonical recipe document references the same PF-05 parser/reconciliation
contract, includes the PF-06 coverage/core-metrics kinds plus the additional PF-07 kinds,
and therefore has a new `derivation_version_id` digest. PF-07 re-derives the complete
extended Observation set under that new version. PF-06 rows and Outcome counts remain
immutable historical derivation results under the core recipe.

## Authority

- D11
- §Provider Derivation after F11
- PF-05 strict parser
- PF-06 provider derive spine

## Observation kinds

### `dataforseo.google.keyword_overview.monthly_search_volume.v1`

One Observation per exact requested keyword and provider `(year, month)` point.

- identity: exact requested keyword + year + month + kind, within Capture/recipe
- value: exact integer monthly search volume, including legitimate zero
- Data Period: exact year/month
- Capture/acquisition time remains separate provenance
- Provider Update Time is included only if the recipe explicitly establishes which provider
  timestamp governs the series; do not infer it from a sibling structure by convenience

Different Captures may legitimately disagree about the same historical month. Capture ID
keeps those testimonies distinct; no overwrite/current projection is created here.

### `dataforseo.google.keyword_overview.search_volume_trend.v1`

Typed provider-computed relative trend fields (`monthly`, `quarterly`, `yearly` or the exact
recipe-authorized equivalents). Preserve provider semantics; do not convert them into a
universal trend score.

### `dataforseo.google.keyword_overview.properties.v1`

Typed provider properties/classifications including the admitted fields present in the
recipe such as core keyword, keyword difficulty, detected language, language flag, and any
other explicitly accepted first-recipe property. Provider quirks are stored as testimony;
request language does not overwrite detected language.

### `dataforseo.google.keyword_overview.avg_backlinks.v1`

Typed average backlink summary with decimal-capable values stored exactly and its own
`last_updated_time` interpreted only as this kind's Provider Update Time.

### `dataforseo.google.keyword_overview.search_intent.v1`

Typed main/foreign intent testimony with its own Provider Update Time. Provider intent is an
Observation value, never an Observatory Outcome. Nullable/array forms follow the recipe's
field-state rules rather than being coerced to one shape.

For the PF-07 extended recipe, `outcomes.observation_count` is the total number of normal
provider Observation envelopes emitted by the complete extended recipe for that Capture;
it does not update the PF-06 core-recipe Outcome row.

## Acceptance criteria

- [ ] PF-03 monthly history produces deterministic point identities based on exact requested
      keyword + year/month, never array index.
- [ ] Point counts follow the actual frozen provider fixture rather than a hard-coded 12-month
      assumption.
- [ ] Legitimate monthly zero remains a stated numeric zero.
- [ ] Re-deriving a later synthetic Capture that revises one historical month creates distinct
      Capture-anchored testimony without rewriting the earlier row.
- [ ] Search-volume trend values remain provider-computed testimony with no strategy score.
- [ ] Keyword properties preserve exact provider quirks, nulls, and classifications.
- [ ] Average backlink decimal values are exact and use only the backlink structure's Provider
      Update Time.
- [ ] Search intent uses only the intent structure's Provider Update Time and preserves
      nullable/multi-valued intent semantics.
- [ ] No sibling provider timestamp is silently inherited by another Observation kind.
- [ ] Same-recipe exact-content idempotency, damage refusal, and two-database logical rebuild
      equivalence extend across all new kinds.
- [ ] PF-06 coverage/core metrics and all fixture regressions remain true.

- [ ] The extended recipe digest differs from PF-06's core recipe digest, re-emits the
      coverage/core kinds plus all PF-07 kinds under the new version, and leaves every
      PF-06 row unchanged.

## Required tests

- Real frozen PF-03 expected row counts/natural identities for every new kind
- Historical-period boundaries/identity and zero point
- Synthetic revised historical point in a later Capture
- Distinct provider timestamps across metrics/backlinks/intent
- Null versus stated array/string fields for properties/intent
- Integer-looking and decimal-looking backlink values normalize identically in type semantics
- Same-recipe conflict mismatch refusal across one new detail kind
- Full empty-DB rebuild equivalence on real PostgreSQL

## Out of scope

- SERP enrichment normalization (disabled in PF-03)
- Clickstream normalization (disabled in PF-03)
- Other DataForSEO endpoints or YouTube surfaces
- Cross-provider joins or projections
- Consumer/API history endpoint (PF-08)
- Additional paid calls

## One implementation commit must prove

The first provider recipe preserves the PF-03 historical and independently timed provider
structures as deterministic typed Observations without collapsing time, nulls, decimals, or
provider classifications.

## Implementation report

**Parent:** `ff55577fc039f8bc852f6ad06dba3d8d4fce504c`  
**Child:** recorded in this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

**Changed paths:**
- `src/observatory/dataforseo_keyword_overview.py` (EXTENDED recipe; CORE builder extracted without byte change)
- `src/observatory/keyword_overview_derive.py` (recipe-aware spine; `derive_keyword_overview_extended`)
- `src/observatory/migrate.py` (five additive typed detail relations)
- `tests/test_dataforseo_keyword_overview.py` (extended recipe publication)
- `tests/test_keyword_overview_extended_derive.py` (new)
- `tests/fixtures/dataforseo_keyword_overview_extended_recipe.jcs` (frozen 2554-byte JCS)
- this ticket (Status + Start commit + Implementation report)

### Extended recipe

- Digest: `cade41cb916bc5595f62ac8ea4ef73d6c688974a1ee5caad0c9d8f95f51664c7`
- Bytes: 2554
- Frozen: `tests/fixtures/dataforseo_keyword_overview_extended_recipe.jcs`
- CORE digest/bytes unchanged: `319af798…` / 1662
- Seven kinds; monthly identity axes are `requested_keyword` + `year` + `month`

Provider Update Time:
- monthly history: omitted from the typed relation. Monthly points are closed `{year,month,search_volume}` with no provider timestamp. `keyword_info.last_updated_time` is a sibling-structure clock and is not inherited.
- search-volume trend: omitted. Closed `{monthly,quarterly,yearly}` has no timestamp.
- properties: omitted. Ticket forbids manufacturing a clock.
- avg_backlinks: only `avg_backlinks_info.last_updated_time`
- search_intent: only `search_intent_info.last_updated_time`

### PF-03 extended counts

coverage 5, metrics 5, monthly 441, trend 5, properties 5, avg_backlinks 5, search_intent 5, total `observation_count` 471.

Monthly per keyword: ai search optimization 85, generative engine optimization 78, keyword research 93, local seo 93, seo api 92.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Monthly keyword+year/month identity, not index | `test_monthly_identity_is_semantic_not_positional` |
| Actual fixture point counts, not 12-month | `test_extended_derive_pf03_counts_and_zero_point` |
| Stated monthly zero | `test_extended_derive_pf03_counts_and_zero_point` |
| Later Capture revises one month without overwrite | `test_historical_revision_creates_second_capture_row` |
| Trend remains provider testimony | `test_trend_properties_backlinks_intent_and_independent_clocks` |
| Properties quirks / core_keyword JSON null | `test_trend_properties_backlinks_intent_and_independent_clocks` |
| Backlink NUMERIC + own PUT | `test_trend_properties_backlinks_intent_and_independent_clocks`, `test_backlink_integer_and_decimal_lexical_forms` |
| Intent array/null + own PUT | `test_trend_properties_backlinks_intent_and_independent_clocks` |
| No sibling clock inheritance | `test_trend_properties_backlinks_intent_and_independent_clocks` |
| Idempotency / damage / two-DB rebuild | `test_exact_content_idempotent_and_monthly_conflict`, `test_extended_failure_and_damage_paths`, `test_two_databases_are_logically_equivalent` |
| PF-06 + fixture regression | `test_core_rows_remain_unchanged_after_extended_derive`, `test_fixture_derive_still_skips_provider_rows`, existing PF-06 file |
| Extended digest / seven kinds / CORE unchanged | `test_extended_recipe_published_digest_and_kinds`, `test_extended_recipe_is_not_the_core_recipe` |
| Wrong-kind + state/value contradictions | `test_wrong_kind_and_state_value_contradictions` |

### Checks

- `uv run pytest -q` — 771 passed, 1 skipped
- `uv run ruff check .` — clean
- `uv run mypy` — clean

### Review

Code-review against start commit. Residual judgement: closed-row writer remains a fork of PF-04 `write_derived_row`; PF-07 reuses that one writer for all seven detail families.

### Unproven limits

- F7 locking and PostgreSQL crash/fsync are not claimed.
- Operator Evidence proof is conditional on the local PF-03 root.
- Monthly/trend/properties omit PUT columns rather than storing explicit unstated tokens.

### Implementer judgement

Weakest remaining assumption: monthly history and search-volume trend have no recipe-authorized governing Provider Update Time, so those relations omit PUT columns entirely. Parent-structure JSON null/absence is cascaded onto child field states rather than suppressing the Observation row (except monthly points, which exist only when the series is stated).

## Closure

<!-- Project Steward only -->
