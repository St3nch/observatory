# PF-12 — DataForSEO Google Organic provider Derivation and persistence

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-11 closed  
**Approved by:** Project Steward  
**Start commit:** `bea97ae4a8b06cc8fa8ae7a2437404981ca45382`

## Purpose

Derive the first DataForSEO Google Organic Outcomes and typed Observations from verified
Evidence into real PostgreSQL under the exact PF-11 recipe.

This ticket is the Google Organic analogue of PF-06/PF-07: it adds the provider-specific
Derivation and persistence boundary only. A later ticket will add adapter-aware recipe
selection and a surface-specific Google Organic read/history API, following the separation
already established by PF-08.

No provider exchange, acquisition widening, read API, recipe-selection mutation, or
cross-provider projection is authorized here.

## Authority and fixed identities

- D11 and D12
- the Provider Derivation section following resolved F11
- PF-04 provider recipe/envelope substrate
- PF-06/PF-07 provider write and exact-content idempotency precedent
- PF-10 accepted Google Organic Evidence contract
- PF-11 strict parser, typed IR, frozen Conformance fixture, and corrected semantic identity

Implementation begins from clean `main` at the ticket's recorded Start commit.

The accepted Google Organic recipe must remain byte-for-byte unchanged:

- adapter:
  `dataforseo-serp-google-organic-live-advanced-paid-probe-v1`
- recipe length: `2487` bytes
- derivation version:
  `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`

The PF-10 response fixture must remain byte-for-byte unchanged:

- length: `135722` bytes
- SHA-256:
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`

PF-12 may extend PF-11 typed IR only where necessary to retain non-identity occurrence
placement for persistence. It must not change the recipe axes, recipe bytes, parser
admission semantics, or the frozen response bytes.

## Dispatch and provenance boundary

Add a provider-specific Google Organic derive module/entrypoint following the bounded
Keyword Overview provider pattern. Do not make fixture `observatory.derive` reinterpret
provider Captures and do not dispatch by guessing from response JSON.

Derivation starts only from committed, verify-on-read Attempt/Capture/body Evidence whose
adapter is the exact Google Organic adapter above. Every normal Observation envelope cites
the verified `attempt_id`, `capture_id`, provider, adapter, and exact recipe identity.

Attempt-stage classification is `authorized_unresolved`. Capture-stage classifications are
the same closed provider taxonomy already accepted for the recipe:

- `no_response`
- `response_partial`
- `transport_complete_non_admissible`
- `provider_error`
- `provider_envelope_rejected`
- `reconciliation_failed`
- `observation_admitted`
- `observation_admitted_empty`

Provider errors, strict-parser failures, reconciliation failures, incomplete transport, or
damaged Evidence emit zero normal provider Observations for that Capture. Attempt-stage
Outcome may survive independently when the Attempt verifies.

## Observation kinds and typed detail

Persist all six PF-11 kinds under generic `observation_envelopes` plus kind-bound typed
relations. Each typed relation must carry the exact `observation_kind` and be structurally
bound to a matching envelope candidate key, as accepted in PF-06/PF-07.

### `dataforseo.google.organic.serp_feature_presence.v1`

Emit one Observation per admitted top-level item placement.

Identity axes are exactly:

- requested keyword
- provider item type
- page
- position
- `rank_group`
- `rank_absolute`

Persist those axes as typed placement testimony. Neither response-array index nor URL is
identity.

### `dataforseo.google.organic.ranked_result.v1`

Emit one Observation per admitted organic placement.

Identity axes are exactly requested keyword, page, position, `rank_group`, and
`rank_absolute`. Persist exact URL, provider domain, title, optional description state,
optional website-name state, and all placement axes.

Exact URL is content, not identity. The frozen PF-10 Capture has 97 organic placements but
only 87 unique exact URLs. All 97 placement Observations must survive; no URL-based
deduplication or normalization is permitted.

### `dataforseo.google.organic.ai_overview_presence.v1`

Emit the admitted AIO presence Observation identified by requested keyword. Persist
`asynchronous_ai_overview` and the provider placement axes. Do not interpret the flag as
an Observatory success/completeness state.

### `dataforseo.google.organic.ai_overview_source.v1`

Emit one semantic Observation per exact
`(requested_keyword, locus, exact_url)`, with `locus` remaining
`top_level` or `element`. Persist exact URL and the field-state/value pairs for provider
domain, title, and source.

PF-11's `element_index` and `reference_index` are occurrence testimony, never
Observation identity. Persist every admitted occurrence in a subordinate typed occurrence
relation.

Each occurrence carries `locus` and is structurally bound to its parent AIO-source detail
through the parent key including Capture, recipe, semantic identity, exact kind, and locus.
PostgreSQL enforces:

- `locus='top_level'` implies `element_index IS NULL` and nonnegative
  `reference_index`;
- `locus='element'` implies nonnegative `element_index` and
  `reference_index`;
- occurrence uniqueness uses `UNIQUE NULLS NOT DISTINCT` on
  `(capture_id, derivation_version_id, within_capture_identity, element_index,
  reference_index)`;
- ordinary `UNIQUE` is not acceptable because PostgreSQL would admit duplicate
  top-level `(NULL, reference_index)` keys;
- no integer sentinel and no split Observation kind.

All occurrences sharing one semantic identity must agree exactly on semantic detail
(including every domain/title/source field state/value). Disagreement rejects the entire
Capture-stage Derivation unit as `provider_envelope_rejected`: write its zero-Observation
Capture Outcome, but no normal Observation envelopes, typed details, result context, or
occurrence rows. Do not choose first/last testimony, drop only the conflicting group, emit
the other kinds, or misclassify the conflict as Attempt reconciliation failure.

The frozen fixture must produce 15 semantic AIO-source envelopes from 18 occurrence rows:
seven top-level and eleven element-level occurrences. Reordering returned reference arrays
may change occurrence indexes but must not change the semantic Observation identity set.

### `dataforseo.google.organic.related_question.v1`

Emit one semantic Observation per exact `(requested_keyword, title)`.
`question_index` is block-local occurrence/order testimony and is never identity.

PF-12 must extend `RelatedQuestion` with the parent PAA block's exact `page`,
`position`, `rank_group`, and `rank_absolute`, copied from the parent
`people_also_ask` top-level item. These fields are occurrence testimony and do not change
the recipe bytes or identity axes. Persist every occurrence in a subordinate typed relation
keyed by the semantic question plus those four non-NULL parent-placement fields and a
nonnegative block-local `question_index`.

A synthetic second PAA block with the same four titles must yield four semantic question
envelopes and eight occurrence rows. A restarted `question_index` must neither collide nor
create a new semantic Observation.

### `dataforseo.google.organic.related_query.v1`

Emit one Observation per exact deduplicated returned query string under the PF-11 identity
`(requested_keyword, query)`. Preserve the parser's exact-string, first-seen semantic
deduplication; do not normalize queries or recreate repeated per-page chips as new facts.

## Result context and time semantics

Persist exactly one typed result-context row per
`(capture_id, derivation_version_id)`, without turning it into an extra Observation kind:

- exact required requested keyword plus provider-returned keyword field state/value;
- required Attempt `location_code` and `language_code` as stated request context;
- `se_domain` field state/value;
- result `datetime` field state/value;
- `se_results_count` and `pages_count` field state/value;
- `items_count` as a nonnegative `BIGINT NOT NULL`;
- exact provider-order `item_types` as `TEXT[] NOT NULL`.

Name and treat result `datetime` as provider SERP result/retrieval time. It is distinct
from Observatory Capture/acquisition time and is not Provider Update Time. Never inherit a
missing provider result time from Capture time or another structure.

Every optional state/value pair must be constrained so `stated` requires a non-NULL value
and non-stated states require SQL NULL. Retain legitimate zero, `FALSE`, and empty values.
PostgreSQL types must preserve exact testimony without binary-float round trip.

Provider cost, task UUID, and check URL remain in raw Evidence only. PF-12 does not persist
them in PostgreSQL, turn them into Observations, or expose new API fields.

## Frozen-Capture cardinality

For the accepted PF-10 Capture, the recipe emits exactly 237 normal Observation envelopes:

| Kind | Envelopes |
|---|---:|
| SERP feature placement/presence | 111 |
| Organic ranked result | 97 |
| AI Overview presence | 1 |
| Semantic AI Overview source | 15 |
| Semantic related question | 4 |
| Related query | 9 |
| **Total / Outcome observation_count** | **237** |

The 18 AIO-source occurrences and four PAA occurrences are subordinate testimony and do not
increase `outcomes.observation_count`.

## Write semantics

- Register and use the exact accepted provider recipe; never write these rows under the
  fixture semantic label or a Keyword Overview recipe.
- One Capture's Outcome, typed result context, diagnostics, envelopes, typed details, and
  subordinate occurrence rows are atomic.
- Same recipe + same verified Evidence compares the complete intended Capture/recipe row
  set. PF-06/PF-07 per-identity closed-row comparison is necessary but not sufficient:
  after planned rows are inserted or exactly compared, and before commit, compare the
  intended and stored identity sets and counts for the one Capture Outcome, generic
  envelopes, every PF-12 typed detail relation, both occurrence relations, the one result
  context, and diagnostics.
- A previously missing rebuildable planned row may be restored by the Derivation, but the
  post-write stored set must exactly equal the intended set. Any extra row, conflicting
  content, wrong Outcome count, or post-write missing row aborts the transaction.
- `outcomes.observation_count` must equal both the planned envelope count and the actual
  stored envelope count for the Capture/recipe unit.
- Do not treat the existing PF-06/PF-07 writer as proof of complete-set equality. Do not use
  `ON CONFLICT DO NOTHING` or last-write-wins as semantic equality.
- Diagnostics preserve PF-11 bounded unknown-extension paths.
- Two fresh PostgreSQL databases rebuilt from the same verified Evidence/recipe must be
  logically equivalent across all PF-12 relations.
- Schema changes are additive and must apply safely over the accepted PF-08 schema.

## Acceptance criteria

- [ ] Exact adapter/recipe dispatch from verified Evidence produces the closed
      Attempt/Capture Outcomes and no fixture-provider confusion.
- [ ] The frozen PF-10 response derives exactly 237 normal envelopes and the six exact
      per-kind counts above on real PostgreSQL.
- [ ] Every typed detail is kind-bound to its matching envelope in PostgreSQL.
- [ ] Feature and organic identities use provider placement axes, never array position or
      URL.
- [ ] All 97 organic placements persist despite ten duplicate exact URLs.
- [ ] AIO sources persist as 15 semantic Observations plus all 18 occurrences; nullable
      `element_index` is testimony, not a sentinel or identity axis.
- [ ] Same-identity AIO semantic-content disagreement produces
      `provider_envelope_rejected` for the whole Capture-stage unit and zero normal rows.
- [ ] PAA title identity survives reorder and a second block; parent block placement plus
      local index preserves all occurrences without identity collision.
- [ ] Related queries remain nine exact semantic facts for the frozen Capture.
- [ ] Provider result time is independently named/stored and never inherited from Capture
      time or mislabeled Provider Update Time.
- [ ] Field-state/value constraints, exact values, diagnostics, and provenance are enforced
      in PostgreSQL rather than only by Python planning.
- [ ] Provider/task/parser/reconciliation/transport failures produce their closed Outcomes
      and zero normal Observations.
- [ ] Damaged Attempt/Capture/body Evidence produces no Capture-stage provider rows; a
      separately verified Attempt-stage Outcome remains valid.
- [ ] Exact-content rerun is idempotent; planted content conflicts and extra
      envelope/detail/context/occurrence/diagnostic rows are refused by complete-set
      comparison, while missing rebuildable planned rows are restored to the exact set.
- [ ] Two real PostgreSQL databases rebuilt from the same Evidence/recipe are logically
      equivalent.
- [ ] Existing fixture, Keyword Overview derivation/selection/API, and PF-11 parser behavior
      remain green.
- [ ] Ordinary tests perform zero provider/DNS activity.

## Required tests

- Real-PostgreSQL derivation of a committed synthetic PF-10-shaped Attempt/Capture using the
  exact frozen response bytes
- Exact 237 Outcome count and per-kind envelope/detail counts
- 97 placement rows versus 87 unique URLs, including duplicate-URL distinct identities
- AIO 15 semantic rows / 18 occurrence rows / 7 top-level / 11 element, including
  field-state agreement and planted whole-unit disagreement refusal
- Duplicate top-level AIO occurrence rejection proving NULL-safe uniqueness
- PAA reorder and duplicated second-block proof: four semantic rows / eight occurrence rows
- Wrong-kind typed-detail, wrong-parent-locus, and invalid occurrence-shape PostgreSQL
  rejection
- Result-context field-state constraints and independent provider-result/Capture times
- Provider error, strict-envelope rejection, reconciliation failure, transport states, and
  Evidence damage
- Exact-content idempotency plus planted content conflicts and extra
  envelope/detail/context/occurrence/diagnostic rows
- Additive migration over an accepted populated PF-08 schema
- Two-database logical equivalence across every new table
- One full existing regression-suite run at the completed implementation commit

During TDD, prefer the bounded loop below and use one session-scoped PostgreSQL fixture:

    uv run pytest -q tests/test_dataforseo_google_organic.py tests/test_dataforseo_google_organic_derive.py
Run the full suite, Ruff, and mypy once after the implementation is complete and before its
single commit.

A valid admitted zero-item SERP maps to `observation_admitted_empty`. Do not change PF-11
string admission or invent a new empty-title rule without provider evidence.

## Out of scope

- Google Organic recipe selection or current-pointer mutation
- Google Organic Attempt/read/history API; cut that as the next ticket after PF-12
- generic `/observations` or cross-provider query contracts
- provider HTTP calls, new paid probes, recurring acquisition, or F12 orchestration
- another SERP adapter, device, locale, search engine, or acquisition surface
- AIO prose/markdown, sentence citations, PAA expanded answers, sitelinks,
  `related_result`, organic publication timestamp, top-stories/video detail
- URL normalization, Page identity, universal rank, scoring, strategy, or projection
- refactoring the shared parser kernel, `Field` type, or unrelated architecture
- F6 automation, F7 concurrency, F8 production auth, F9 HTTP writes, or F10 projections

## One implementation commit must prove

One verified Google Organic Capture can be re-derived into the exact accepted recipe's
237 semantic, typed, provenance-bound Observations while all AIO/PAA occurrence testimony
and duplicate organic URL placements survive without becoming identity.

## Implementer report required

The implementation commit must update this ticket to `review`, record its exact parent,
changed paths, acceptance-to-test map, commands/results, and state explicitly:

- whether the ticket or existing architecture was awkward;
- what generalized cleanly from PF-06/PF-07 and what did not;
- the weakest identity, aggregation, schema, transaction, or test assumption;
- any under-proved adversarial case or fixture surprise;
- why any changed PF-11 IR field is occurrence testimony rather than recipe identity;
- confirmation that recipe/fixture bytes and both accepted Keyword Overview recipe IDs are
  unchanged;
- confirmation of no provider/network call, no API/selection work, no other surface, and no
  push.

Do not broaden the implementation to fix adjacent findings. Report them for Steward
reconciliation.

## Implementation report

**Parent:** `bea97ae4a8b06cc8fa8ae7a2437404981ca45382`  
**Child:** supplied in the implementer handoff (a commit cannot embed its own final hash).  
**Status:** `review`

### Loaded skills

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### Changed paths

- `src/observatory/dataforseo_google_organic.py` (`RelatedQuestion` parent placement)
- `src/observatory/google_organic_derive.py` (new derive module/entrypoint)
- `src/observatory/migrate.py` (nine additive Organic tables)
- `tests/test_dataforseo_google_organic.py` (PAA parent-placement IR)
- `tests/test_dataforseo_google_organic_derive.py` (new)
- this ticket (Start commit, Status, Implementation report)

No recipe/fixture bytes, no KO recipes, no selection/API, no other surface.

### Frozen identities

- Organic recipe: 2487 bytes,
  `338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`
- PF-10 fixture: 135722 bytes,
  `7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`
- KO CORE: `319af798f3e0b3e5fe4579539442c4ca5d384b683e1f4bce0f7a1b3e26cd5908`
- KO EXTENDED unchanged:
  `cade41cb916bc5595f62ac8ea4ef73d6c688974a1ee5caad0c9d8f95f51664c7`

`RelatedQuestion` now carries parent `page`, `position`, `rank_group`, and
`rank_absolute` as occurrence testimony. Recipe identity axes are still
`(requested_keyword, title)`.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Adapter/recipe dispatch; fixture skip | `test_fixture_derive_skips_organic_and_organic_skips_fixture`, `test_provider_rows_cannot_use_fixture_label` |
| 237 envelopes and per-kind counts | `test_plan_frozen_fixture_has_exact_semantic_counts`, `test_derive_pf10_fixture_into_real_postgres` |
| Kind-bound details / wrong kind / wrong locus / shape | `test_wrong_kind_and_occurrence_shape_are_rejected` |
| 97 placements / 87 URLs | `test_derive_pf10_fixture_into_real_postgres`, `test_duplicate_urls_keep_distinct_placement_identities` |
| AIO 15/18/7/11 | `test_plan_frozen_fixture_has_exact_semantic_counts`, `test_derive_pf10_fixture_into_real_postgres` |
| NULL-safe top-level uniqueness | `test_top_level_aio_occurrence_uniqueness_is_null_safe` |
| Whole-unit AIO disagreement → `provider_envelope_rejected` | `test_plan_aio_disagreement_rejects_whole_unit`, `test_aio_disagreement_writes_rejected_outcome_and_zero_rows` |
| PAA parent IR + second block 4/8 | PF-11 PAA tests; `test_paa_second_block_keeps_four_questions_and_eight_occurrences` |
| Result context, no cost/check_url, independent result time | plan/derive happy-path tests |
| Result-context field-state CHECKs | `test_result_context_field_state_constraints` |
| Result-context FK to Capture Outcome | `test_result_context_requires_matching_outcome` |
| Transport / parse / recon / damage / non-admissible | `test_transport_parse_reconciliation_and_damage_paths` |
| Empty SERP → `observation_admitted_empty` | `test_plan_zero_item_serp_is_admitted_empty`, `test_zero_item_serp_writes_admitted_empty_outcome` |
| Exact-content, extra rows, missing restore | `test_exact_content_extra_rows_and_missing_restore` |
| Extra foreign-Attempt Outcome refused | `test_foreign_attempt_outcome_is_complete_set_mismatch` |
| Additive PF-08 populated migration | `test_populated_pf08_schema_then_organic_derive` |
| Two-database equivalence | `test_two_databases_are_logically_equivalent` |
| Recipe/fixture/KO freeze | `test_accepted_recipe_and_ko_identities_remain_unchanged` |

### Checks

Targeted loop
`uv run pytest -q tests/test_dataforseo_google_organic.py tests/test_dataforseo_google_organic_derive.py`
— 42 passed in 17.53 s after remediations.

Final local validation after Steward remediations, parent still `bea97ae4…`:

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-18T21:12:06.989Z | 2026-08-18T21:14:34.215Z | 147.227 s (pytest 146.81 s) | 0 |
| `uv run ruff check .` | 2026-08-18T21:14:34.215Z | 2026-08-18T21:14:34.247Z | 0.032 s | 0 |
| `uv run mypy` | 2026-08-18T21:14:34.247Z | 2026-08-18T21:14:34.756Z | 0.509 s | 0 |

`887 passed, 1 skipped, 1 warning`. Prior accepted count at the first PF-12 commit was 884.
Versions: pytest 8.4.2, ruff 0.16.2, mypy 1.20.2.
No leftover `observatory-ce05-*` container.
Ordinary tests remain zero-network; autouse socket guard in PF-12 tests.
No paid-gate env, no provider call, no push.

### Review

Code-review against `bea97ae4a8b06cc8fa8ae7a2437404981ca45382`.

**Standards:** 0 hard. Residual: derive walk/writer is copied from KO rather
than extracted; kind strings are duplicated in `migrate.py` as KO already does.

**Spec:** remediations are present. Residual test limits: extra typed-detail and
extra context rows are not planted (context extras are blocked by the
`(capture_id, derivation_version_id)` primary key; extra details require a
matching envelope first). PAA reorder is proved at parse, not re-derived
into PostgreSQL.

### Unproven limits

- AIO field-state disagreement is synthetic only; the frozen fixture agrees.
- A second real PAA block is synthetic.
- Right-rail rank sequences remain unobserved.
- Complete-set compare does not include `locus` in the AIO occurrence tuple
  because uniqueness is `(identity, element_index, reference_index)` as specified.
- Empty SERP still writes one result-context row with `items_count=0`.
- Two-database snapshot remains a selected-column compare, not every column.

### Steward remediations

Steward review of `e542b0237f4a7ac3bcc98353427cacf7e3c4dfbc` required four
bounded fixes; the design, identities, 237-count, and AIO rejection class
were accepted.

1. `_assert_complete_set` now loads every Capture/recipe Outcome including
   `attempt_id` and requires the stored set to be exactly the one planned
   `(attempt_id, classification, observation_count)` row. A planted
   foreign-Attempt Outcome is refused and does not mutate accepted rows.
   Test: `test_foreign_attempt_outcome_is_complete_set_mismatch`.
2. `google_organic_result_context` now FKs
   `(derivation_version_id, attempt_id, capture_id)` to `outcomes`. Additive
   `CREATE TABLE` plus `ALTER TABLE` for existing databases. An additive
   `outcomes_identity` unique is applied first so older `outcomes` tables
   (the PF-04 integer-schema upgrade path) can host the FK. Test:
   `test_result_context_requires_matching_outcome`.
3. `test_populated_pf08_schema_then_organic_derive` now applies
   `PRE_PF12_SCHEMA_STATEMENTS` only (asserted to contain PF-08/KO tables
   and no `google_organic_` names), plants representative KO selection /
   Outcome / envelope / coverage rows, then `apply_schema()`. Existing rows
   stay; nine Organic tables become present and writable.
4. Result-context `stated`/NULL and non-stated/value CHECKs are proved on
   `result_datetime`. `transport_complete_non_admissible` is planted with a
   response-complete empty body.

### Engineering assessment

**Ticket awkwardness.** Complete-set comparison had to be bolted onto the KO
per-row writer instead of replacing it. That is two equality stories in one
transaction. Extra context cannot exist at the required grain because of the
PK, so the ticket's "extra context row" plant is structurally empty.

**What generalized.** Adapter-filtered Evidence walk, classify-then-plan,
envelope + kind-bound detail FKs, state/value CHECKs, attempt-stage survival
on Capture damage, and additive `CREATE TABLE IF NOT EXISTS`.

**What did not.** Keyword Overview has no occurrence layer and no Capture-level
context table. Monthly points are first-class identities; AIO indexes are not.
The KO writer cannot see extra rows. Organic identity is placement-shaped, not
one-row-per-keyword.

**Weakest assumption.** Complete-set compare trusts that all Organic rows for
one Capture/recipe are only the ones this writer created. A second Organic
recipe digest in the same Capture would be a later ticket; this compare is
keyed by the PF-11 digest.

**Fragile edges.** (1) `connection.rollback()` in constraint tests can wipe
uncommitted derive work if the caller forgets `commit()`. (2) AIO disagreement
is detected only after a successful parse, so a title mutation that also
breaks parse never reaches the disagreement class. (3) Occurrence uniqueness
omits `locus` as specified; locus is enforced by parent FK instead.

**Do not refactor yet.** Do not extract a shared provider-derive kernel. Do
not split AIO kinds. Do not persist cost/check_url.

**PF-13 trigger.** History/API will need the occurrence tables and the
Capture-level context row. Selection must not be this module. If history wants
cost, that is a new context column, not a silent add here.

## Steward closure — 2026-08-18

**Accepted by:** Project Steward  
**Accepted implementation:** `d8caf4dd52678e7805e394b608bc95d98f3ab712`  
**Accepted parent:** `bea97ae4a8b06cc8fa8ae7a2437404981ca45382`

PF-12 is accepted and closed after independent Steward review of the original implementation
and amended remediation commit. The implementation remains one bounded commit from the
accepted parent and changes only the parser IR, Google Organic provider Derivation,
additive PostgreSQL schema, dedicated tests, and this ticket.

The accepted Derivation registers and uses the unchanged 2487-byte Google Organic recipe
`338fc2080d31a35b1f7cc5d7a71c971d25d72517ca3b846959ccb501b666acde`.
The frozen 135722-byte PF-10 fixture remains unchanged with SHA-256
`7143871e3e1e88b1eb462dd5c06300e7db0fd7c68a55e075d33107d7cbd9955f`.
Both accepted Keyword Overview recipe identities remain unchanged.

One verified PF-10-shaped Capture derives exactly 237 normal Observation envelopes:
111 SERP feature placements, 97 organic ranked results, one AIO presence, 15 semantic AIO
sources, four semantic related questions, and nine related queries. All 97 organic
placements survive despite only 87 unique exact URLs; URL remains content rather than
placement identity.

AIO source indexes remain subordinate occurrence testimony. The accepted schema stores
15 semantic source details and all 18 occurrences, including seven top-level occurrences
with nullable `element_index` and eleven element occurrences. PostgreSQL
`UNIQUE NULLS NOT DISTINCT`, locus-shape checks, and the parent detail/locus foreign key
prevent duplicate NULL-index occurrences, sentinels, wrong-locus rows, and orphaned source
testimony. Same-identity domain/title/source disagreement rejects the whole Capture-stage
unit as `provider_envelope_rejected` with zero normal rows.

`RelatedQuestion` now carries its parent PAA page, position, `rank_group`, and
`rank_absolute` solely as occurrence testimony. Semantic identity remains exact requested
keyword plus title. A synthetic repeated PAA block proves four semantic question envelopes
and eight placement/index occurrences without using block-local order as Observation
identity.

The Capture-scoped result context preserves requested/returned keyword testimony,
Attempt location/language, SERP domain, provider result/retrieval time, provider counts, and
provider-order item types. Provider result time remains distinct from both Capture time and
Provider Update Time. State/value consistency is enforced in PostgreSQL, and the context's
exact recipe/Attempt/Capture provenance is structurally bound to its Capture Outcome.
Provider cost, task UUID, and check URL remain only in Evidence.

Capture writes are atomic across Outcome, diagnostics, context, envelopes, typed details,
and occurrence relations. Per-row content comparison is followed by exact complete-set
comparison. A foreign-Attempt Outcome, extra envelope, extra occurrence, extra diagnostic,
content conflict, wrong Outcome count, or post-write set mismatch is refused. Missing
rebuildable planned rows may be restored, after which the stored set must exactly equal the
plan. The additive migration is proved over representative populated pre-PF-12
Keyword Overview recipe, selection, Outcome, envelope, and typed-detail state.

Closed provider failure classifications produce zero normal rows. Tests cover no response,
partial response, complete non-admissible transport, provider error, strict-envelope
rejection, reconciliation failure, Evidence damage, and valid admitted-empty SERP behavior.
Fixture Derivation and existing Keyword Overview derivation, selection, and API behavior
remain unchanged.

Independent Steward verification at the accepted amended implementation commit:

- operator-independent `uv run pytest -q`: 887 passed, 1 skipped, 1 upstream
  Starlette/httpx deprecation warning, exit 0, 117.70 seconds wall time;
- clean working tree before and after that run;
- no leftover `observatory-ce05-*` Docker container;
- independent Steward `uv run ruff check .`: clean;
- independent Steward `uv run mypy`: clean, 46 source files.

Accepted limits remain explicit: AIO disagreement and a second PAA block are synthetic;
right-rail rank behavior remains unobserved; the two-database proof is logical rather than a
byte-for-byte dump of every column; the provider-derive walk/writer remains intentionally
unextracted; and the third-tier occurrence layer is new but bounded by relational
constraints. Google Organic recipe selection and read/history API work remain a separate
later ticket.

No provider or DNS call, credentials, paid-gate environment, Evidence mutation, API or
selection work, another acquisition surface, `scripts/verify-all`, or push occurred.
