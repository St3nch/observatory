# PF-04 — Provider Derivation recipe and Observation foundation

**Status:** ready
**Parent spec:** `docs/specs/capture-event-v2.md`
**Kind:** foundation
**Blocked by:** PF-03 closed; D11/F11 resolution
**Approved by:** Project Steward
**Start commit:** <!-- implementer fills -->

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

### Derivation diagnostics

Diagnostics are rebuildable and are not Observations. They identify at least the provider
recipe, Attempt/Capture as applicable, a stable diagnostic code, and a stable provider-body
path (JSON Pointer or an equivalently unambiguous recipe-defined path). The first supported
use is tolerated unknown fields on extension-permitted provider objects.

## Acceptance criteria

- [ ] Empty PostgreSQL migration creates the provider recipe, canonical Observation envelope,
      and Derivation diagnostic substrate without changing existing fixture table meaning.
- [ ] A fixed published provider recipe document has a test-computed JCS SHA-256 that equals
      its `derivation_version_id`; registration stores/recovers the exact canonical bytes.
- [ ] Re-registering identical recipe bytes/adapter metadata is idempotent.
- [ ] Same digest with conflicting canonical bytes or adapter metadata fails closed before
      any provider-derived write.
- [ ] Fixture `derivation_version_id` labels continue to register and derive exactly as before.
- [ ] Existing fixture Outcomes/Observations, logical rebuild equivalence, and API Attempt
      envelopes are unchanged.
- [ ] Foundation code has a tested exact-content comparison path suitable for later provider
      same-recipe writes; it does not authorize changing fixture-v1 conflict behavior here.
- [ ] Real PostgreSQL is used for migration/registration tests.

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

<!-- implementer fills; may set Status: review; never Status: done -->

## Closure

<!-- Project Steward only -->
