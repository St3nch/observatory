# PF-06 — Keyword Overview provider Derivation: Outcomes, coverage, and core metrics

**Status:** planned
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** provider derivation tracer
**Blocked by:** PF-05
**Approved by:** Project Steward
**Start commit:** <!-- implementer fills -->

## What to build

Derive the first DataForSEO Keyword Overview provider Outcomes and typed Observations from
verified Evidence into real PostgreSQL. This ticket proves the provider Derivation spine with
request/result reconciliation, provider coverage testimony, and core keyword metrics only.

Fixture derivation remains a separate accepted path and must not begin writing provider rows
under a fixture version.

## Authority

- D11
- §Provider Derivation after F11
- PF-04 provider recipe/envelope substrate
- PF-05 strict typed parser/conformance fixture

## Dispatch boundary

Do not turn the fixture classifier into a provider classifier. Add explicit adapter/recipe
dispatch or a provider-specific derive module invoked through a bounded derivation entrypoint.
Provider Derivation starts only from committed, verify-on-read Attempt/Capture/body Evidence.

## Provider Outcome taxonomy for this recipe

Attempt-stage:

- `authorized_unresolved`

Capture-stage closed classifications:

- `no_response`
- `response_partial`
- `transport_complete_non_admissible`
- `provider_error` — the provider envelope parsed but top/task provider status is not success
- `provider_envelope_rejected` — strict recipe parsing/schema semantics fail
- `reconciliation_failed` — parsed testimony cannot be unambiguously reconciled to Attempt
- `observation_admitted` — at least one recipe Observation is admitted
- `observation_admitted_empty` — reserved for a recipe-legitimate successful capture with zero
  Observations; the first coverage rule should make an all-omitted keyword response produce
  coverage Observations rather than this classification

Provider intent/competition/language classifications are Observation values, not Outcomes.

## Observation kinds in scope

### `dataforseo.google.keyword_overview.coverage.v1`

Emit exactly one coverage Observation for every exact requested keyword when the provider
envelope/reconciliation is admissible.

- subject: exact requested keyword from verified Attempt
- `covered=true` when exactly one returned provider item reconciles to it
- `covered=false` only for the recipe-recognized documented provider omission/no-data case
- preserve exact returned keyword when covered; it is null/unstated when omitted

### `dataforseo.google.keyword_overview.metrics.v1`

Emit one metrics Observation for every covered requested keyword. Include the first
`keyword_info`/item-level measurement family necessary to make the historical service useful,
including:

- exact requested keyword and exact returned keyword
- request context fixed by the adapter (location/language) and provider measurement context
  such as `search_partners` when present
- `search_volume`
- `competition`
- `competition_level`
- `cpc`
- low/high top-of-page bid
- provider categories/codes
- `keyword_info.last_updated_time` as Provider Update Time where the recipe states it governs

Nullable/optional fields use field-level state where required by D11. Decimal-capable values
use exact PostgreSQL `NUMERIC`-class storage without binary-float round trip.

Historical monthly points, trends, properties, backlink averages, and search intent are PF-07.

## Identity

Provider Observation natural identity includes `capture_id`, provider recipe
`derivation_version_id`, observation kind, and a deterministic within-Capture identity
derived from the exact requested keyword plus kind. Values, returned-array position, provider
task UUID, and provider-returned order are not identity.

The within-Capture identity should be a full 64-hex SHA-256 of a closed canonical identity
document or an equivalently collision-resistant recipe-defined canonical digest.

## Write semantics

- Attempt-stage provider Outcome may survive when the parent Attempt verifies but its Capture
  or body is damaged.
- Capture Outcome + diagnostics + envelope/detail rows for one Capture are atomic as one
  provider derive unit.
- Same recipe + same Evidence rerun compares intended content. Existing identical content is
  idempotent; any existing mismatch is `DerivationError` or equivalent fail-closed behavior.
- Do not use conflict-ignore as semantic equality.
- Empty PostgreSQL rebuild from the same verified Evidence/recipe is logically equivalent.

## Acceptance criteria

- [ ] Provider recipe registration is used; provider rows cannot be written under the fixture
      semantic label.
- [ ] Verified PF-03 Attempt receives `authorized_unresolved`; its Capture receives the
      recipe-authorized successful classification and correct Observation count.
- [ ] Returned item order does not affect identities or values.
- [ ] Coverage emits one row per exact requested keyword and preserves documented omission as
      bounded provider testimony.
- [ ] Core metrics are typed, exact, source-attributed, and cite verified Attempt/Capture and
      recipe identities.
- [ ] Provider Update Time is independent of Capture time; unstated provider time stays
      unstated.
- [ ] Provider task errors/schema drift/reconciliation failures produce their closed Outcomes
      and zero normal provider Observations for that Capture.
- [ ] Same-recipe rerun is exact-content idempotent; planted conflicting derived content fails.
- [ ] Damaged Capture/body produces no provider Capture-stage rows while a separately verified
      Attempt-stage Outcome remains.
- [ ] Two real PostgreSQL databases rebuilt from the same Evidence/recipe are logically
      equivalent for provider rows.
- [ ] Fixture derivation/API regression behavior remains unchanged.

## Tests that intentionally change

Provider-only/mixed-store tests that currently prove the **fixture** derive path writes zero
provider rows remain as fixture-path assertions. Add separate provider-derive tests proving
the new recipe writes provider rows. Do not make fixture `derive()` silently reinterpret paid
Captures under `fixture-panel-v1`.

## Out of scope

- Historical `monthly_searches`
- `search_volume_trend`
- keyword properties/difficulty/language
- average backlink summary
- search intent
- provider HTTP API exposure
- F7/F8/F10
- any live provider call

## One implementation commit must prove

One verified PF-03 Capture can be re-derived on real PostgreSQL into recipe-bound provider
Outcomes, coverage, and core metrics with exact-content idempotency and no fixture regression.

## Implementation report

<!-- implementer fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
