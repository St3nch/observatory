# PF-04 — Provider Derivation recipe and Observation foundation

**Status:** review
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** foundation
**Blocked by:** PF-03 closed; D11/F11 resolution
**Approved by:** Project Steward
**Start commit:** `9e4dd055038675402c6ef16dd103ac3b60687505`

## What to build

Add the rebuildable substrate required by D11 before any provider body is normalized:
content-addressed provider Derivation Recipe registration, a canonical provider-capable
Observation envelope relation, and rebuildable Derivation diagnostics. Preserve every
fixture-v1 behavior and API response unchanged.

This ticket writes **no provider Outcomes or Observations from DataForSEO bodies**. It makes
the foundation on which later tickets can do that safely.

## Authority

- `decisions/decisions.md` — D11
- `decisions/deferred.md` — F11 resolved by D11
- `docs/specs/capture-event-v2.md` — §Provider Derivation after F11
- `VOCABULARY.md` — Derivation Recipe, Observation Kind, Provider Update Time, Data Period
- D8/D9/D10 remain unchanged for Evidence and transport

## Scope

- Provider recipe registration keyed by provider `derivation_version_id = sha256(JCS(recipe))`
- Exact canonical recipe bytes available in rebuildable PostgreSQL and compared on reuse
- Existing fixture `derivation_versions` semantics remain valid without recipe bytes
- Additive canonical Observation envelope relation for provider-capable Observations
- Additive rebuildable Derivation diagnostic relation for tolerated extensions/drift notices
- Provider-write helper behavior that can compare intended existing row content rather than
  silently treating a conflicting row as idempotent
- Real PostgreSQL migration/rebuild proof

## Required relational meaning

Physical SQL may use ordinary implementation names, but the provider substrate must expose
the following stable concepts.

### Provider recipe registration

For provider recipes, the registered version identity is exactly the lowercase 64-hex
SHA-256 of the exact canonical JCS recipe bytes. Registration associates that identity with
the exact adapter contract and exact canonical bytes. Re-registering the same digest with
different bytes or adapter metadata fails before derived writes.

Fixture versions remain grandfathered under the existing semantic-label rule and do not
require a recipe row.

PF-04 defines and tests the closed provider recipe-document schema and registration
mechanism only. Its published registration vector is a **test recipe instance**, not the
production Keyword Overview recipe. PF-05 authors the first Keyword Overview recipe
instance after the strict parser/conformance contract is proven. PF-04 must not freeze a
stub production recipe whose semantic fields would have to change in PF-05 or later.

### Canonical Observation envelope

The new additive envelope carries at least:

- `capture_id`
- `attempt_id`
- provider `derivation_version_id`
- `provider`
- `adapter_contract`
- recipe-declared `observation_kind`
- deterministic within-Capture Observation identity

The implementation may call the relation `observation_envelopes` or an equivalently clear
name. Do **not** widen the existing fixture `observations` table with provider nullable
columns. Do not migrate fixture rows into the new envelope in this ticket.

The within-Capture provider Observation identity must be capable of a full lowercase
64-hex digest derived from recipe-defined semantic identity bytes; it is not constrained to
`result:N`.

For PF-04, the within-Capture provider Observation identity is standardized as a full
lowercase 64-hex SHA-256 of a closed recipe-defined canonical semantic-identity document;
raw subject text and fixture-style `result:N` identifiers are not used for provider rows.

### Derivation diagnostics

Diagnostics are rebuildable and are not Observations. They identify at least the provider
recipe, Attempt/Capture as applicable, a stable diagnostic code, and a stable provider-body
path (JSON Pointer or an equivalently unambiguous recipe-defined path). The first supported
use is tolerated unknown fields on extension-permitted provider objects.

## Acceptance criteria

- [x] Empty PostgreSQL migration creates the provider recipe, canonical Observation envelope,
      and Derivation diagnostic substrate without changing existing fixture table meaning.
- [x] A fixed published provider recipe document has a test-computed JCS SHA-256 that equals
      its `derivation_version_id`; registration stores/recovers the exact canonical bytes.
- [x] Re-registering identical recipe bytes/adapter metadata is idempotent.
- [x] Same digest with conflicting canonical bytes or adapter metadata fails closed before
      any provider-derived write.
- [x] Fixture `derivation_version_id` labels continue to register and derive exactly as before.
- [x] Existing fixture Outcomes/Observations, logical rebuild equivalence, and API Attempt
      envelopes are unchanged.
- [x] Foundation code has a tested exact-content comparison path suitable for later provider
      same-recipe writes; it does not authorize changing fixture-v1 conflict behavior here.
- [x] Real PostgreSQL is used for migration/registration tests.

## Required tests

- Empty-schema migration and idempotent re-migration
- Fixture prior-schema upgrade regression remains green
- Provider recipe SHA/JCS registration
- Identical provider registration reuse
- Conflicting recipe bytes/adapter registration refusal
- Observation-envelope and diagnostic PK/identity constraints
- Full existing fixture derive/API regression suite remains green

## Out of scope

- Parsing the PF-03 provider response
- Provider Outcome classifications
- Provider detail/value tables
- Provider API selection or provider HTTP resources
- Migrating fixture rows into the canonical envelope
- F7 multi-process locking
- F8 authentication/non-loopback
- F10 projections
- Any provider network call

## One implementation commit must prove

Provider recipe identity and additive canonical Observation/diagnostic substrate exist on
real PostgreSQL while fixture-v1 derivation and API behavior remain logically unchanged.

## Implementation report

**Parent:** `9e4dd055038675402c6ef16dd103ac3b60687505`  
**Child:** recorded in this implementation commit.

**Loaded skills:**
- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

**Changed paths:**
- `src/observatory/migrate.py` (additive `provider_recipes`, `observation_envelopes`, `derivation_diagnostics`)
- `src/observatory/provider_recipe.py` (new; closed test recipe, registration, identity, writes)
- `tests/test_provider_recipe.py` (new)
- this ticket (Status + Start commit + Implementation report)

`src/observatory/derive.py` was not changed. Fixture `ON CONFLICT DO NOTHING` and fixture `observations` columns remain as accepted.

### Acceptance → proving tests

| Criterion | Test |
|---|---|
| Empty-schema migration + idempotent re-migration; fixture columns unchanged | `test_empty_schema_creates_provider_substrate_without_fixture_meaning` |
| Prior integer schema upgrade still preserves fixture rows and adds new tables | `test_prior_integer_schema_upgrade_still_preserves_fixture_rows` plus existing `test_apply_schema_upgrades_integer_columns_and_preserves_rows` |
| Published test recipe JCS/SHA-256 equals `derivation_version_id` | `test_published_test_recipe_jcs_sha256_equals_derivation_version_id` |
| Closed recipe schema rejects extra/missing/float/wrong schema | `test_recipe_schema_rejects_unknown_and_missing_members`, `test_recipe_schema_rejects_float_and_non_v1_identity` |
| Register stores/recovers exact bytes; identical reuse is idempotent | `test_register_test_recipe_stores_and_recovers_exact_canonical_bytes` |
| Conflicting bytes, adapter metadata, or fixture-occupied digest fail closed | `test_conflicting_recipe_bytes_or_adapter_metadata_fail_before_write` |
| Fixture versions still register without recipe bytes | `test_fixture_version_registers_without_recipe_bytes` |
| Envelope/diagnostic PK and `result:N` refusal | `test_envelope_and_diagnostic_identity_constraints` |
| Recipe-defined identity digest; extra axes fail | `test_observation_identity_is_sha256_of_canonical_semantic_document` |
| Identity kinds must match declared kinds exactly; axis types closed | `test_recipe_identity_kinds_must_match_declared_kinds` |
| Per-kind coverage vs monthly axes, types, undeclared kind | `test_multi_kind_recipe_identity_is_kind_specific` |
| Exact-content reuse and conflict; kind/adapter bound to registered recipe | `test_exact_content_comparison_reuses_identical_and_refuses_conflict` |
| Fixture derive/API regression | existing CE-05/CE-06/CE-07 suites remain green |

### Independently recomputed published test recipe

Literal hashed with `hashlib.sha256`, not the production constructor:

| Vector | Bytes | SHA-256 |
|---|---:|---|
| test recipe JCS | 1204 | `b234ea5315eaf7499a20dc0c612332576fd9af4a748b0ca380b2bae60897eb13` |
| sample identity document JCS | 141 | `884fef9385834e5923658eb07ba986e85b3d61cb27c88e068b3cd406f2218100` |

The published registration vector is `test-provider` / `test-provider-recipe-foundation-v1` with kind `test.provider.coverage.v1`. It is not the production Keyword Overview recipe.

### Checks

- `uv run pytest -q` — 724 passed, 1 skipped
- `uv run ruff check .` — clean
- `uv run mypy` — clean
- Ordinary tests remain zero-network

### Review

Code-review against `9e4dd055038675402c6ef16dd103ac3b60687505`.

**Standards:** 0 hard / 5 judgement. Worst: cloned document validators and a generic allowlisted row writer in one module. Left in place: importing `capture_event` private helpers would couple Evidence documents to rebuildable recipe documents; the ticket asked for a reusable exact-content path.

**Spec:** 2 partial findings, then addressed before the first PF-04 commit:
- Observation identity rules live in recipe bytes and participate in `derivation_version_id`.
- Envelope writes require a registered recipe and matching provider/adapter/`observation_kind`.

Steward review then required per-kind identity. Remediation:
- Closed `observation_identity` section, separate from `reconciliation`.
- Every declared `observation_kind` has exactly one identity-axis definition; undeclared kinds cannot have identity rules.
- `observation_identity()` selects the kind's axes, requires exactly those names, validates `string` / JSON `integer`, and hashes only the closed identity document.

Residual: no dedicated PF-04 API assertion beyond the existing CE-07 suite remaining green. Axis types other than string/integer are not in this schema. Per-kind identity axes are Steward-required recipe semantics; they are not yet a named VOCABULARY term.

### Unproven limits

- F7 multi-process registration/write locking is not claimed.
- PostgreSQL crash/fsync/commit behavior is not claimed.
- No provider body is parsed; no provider Outcomes/Observations are derived from DataForSEO.
- `write_derived_row` allowlists only the two foundation relations; later detail tables must be added explicitly.
- The test recipe must not be mutated into the PF-05/PF-06 production recipe.

### Implementer judgement

The published test recipe remains one coverage kind. The multi-kind recipe is a synthetic proof only and is not a production Keyword Overview recipe. PF-05/PF-07 must declare each kind's axes in `observation_identity` rather than a global list. The weakest later seam remains `write_derived_row`'s string-table allowlist.

## Closure

<!-- Project Steward only -->
