# PF-15 — PostgreSQL migration catalog and widening hygiene

**Status:** ready  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-14 closed  
**Approved by:** Project Steward  
**Start commit:** dc9534b44c0f15353cf194b436866d7f0270a6c1

## Purpose

Harden Observatory's rebuildable PostgreSQL migration path so additive constraints are
detected on their actual target relations rather than by database-wide names, and so the
three legacy I-JSON integer columns are widened only when their real catalog type requires
it.

This ticket reconciles the migration findings from the independent milestone audit at
59559a1e. It is migration hygiene over the accepted schema, not a schema redesign,
migration-framework project, new provider surface, or change to Evidence authority.

## Authority and accepted precedent

- D4 — long-lived data requires migrations, upgrades, verified restores, and fresh
  re-derivation.
- D8 — PostgreSQL is disposable and rebuildable; Evidence remains authoritative.
- D11 — provider provenance constraints and exact identities remain enforced.
- PF-04/PF-08 — provider recipes, envelope identity, and adapter-aware selection introduced
  additive constraints over earlier schemas.
- PF-12 — Organic result context introduced the Outcome provenance foreign key and proved an
  additive populated PF-08 upgrade.
- PF-14 — read-path integrity is closed; PF-15 does not change API behavior.

Real PostgreSQL remains required for migration proof. No migration success may depend on a
constraint name found on an unrelated table or schema.

## Confirmed defect: global constraint-name checks

Four additive migration blocks currently query pg_constraint by conname alone:

- outcomes_identity on outcomes;
- provider_recipes_adapter_version on provider_recipes;
- observation_envelopes_kind_identity on observation_envelopes;
- google_organic_result_context_outcome on google_organic_result_context.

PostgreSQL constraint names are not database-global identities. An unrelated CHECK or other
constraint with the same conname can make the current IF NOT EXISTS branch skip the required
target constraint.

For every additive block:

- resolve and test the exact target relation, not only conname;
- retain the accepted constraint name and definition;
- do not confuse a same-named constraint on another table or schema with the target;
- repeated migration over the correct target constraint remains idempotent;
- catalog assertions in tests must also be target-relation-scoped rather than capable of
  passing on an unrelated constraint.

The smallest accepted implementation may use conrelid against the exact regclass resolved by
the same schema/search-path rules as the unqualified CREATE/ALTER statements. Do not invent
a second schema namespace or qualify only half of the migration.

## Required collision adversary

On real PostgreSQL, construct a legacy/additive path in which unrelated relations carry
same-named decoy constraints for all four names while the real target relations lack their
required additive constraints.

Applying the current schema must:

- ignore the decoys;
- install each required constraint on its exact target table;
- retain each decoy untouched;
- produce the accepted constraint type and definition on the target;
- enforce the target uniqueness/foreign-key behavior;
- succeed again on a second application without duplicates or mutation.

The test must prove target table OID/name plus constraint name/type/definition. A global
SELECT WHERE conname = ... is not sufficient proof.

If one integrated legacy fixture becomes unreasonably broad because of dependency order,
bounded per-constraint setup is allowed, but the report must explain why the combined
apply_schema path is still covered. Do not drop production constraints merely to make a
false-green test convenient.

## I-JSON widening reconciliation

The audit claimed that the INTEGER-to-BIGINT path lacked a genuine INTEGER-start test. That
claim is obsolete at the PF-15 Start commit.

tests/test_derive_admitted_results.py already contains
test_apply_schema_upgrades_integer_columns_and_preserves_rows. It creates real INTEGER
columns for:

- outcomes.observation_count;
- observations.result_index;
- observations.score;

then proves real catalog types become BIGINT, planted rows survive, and a second
apply_schema call preserves those rows. Fresh BIGINT types and I-JSON bounds also already
have dedicated tests.

PF-15 must preserve and build on those proofs rather than create a duplicate weaker test.

## Type-aware widening

WIDEN_IJSON_COLUMNS_SQL currently executes three unconditional ALTER COLUMN TYPE BIGINT
statements on every migration, including already-current schemas. Replace that behavior
with a bounded catalog-aware migration for each exact table/column:

- INTEGER is widened to BIGINT;
- BIGINT is accepted without executing ALTER COLUMN TYPE;
- a missing column or any unexpected type fails closed rather than being silently accepted
  or opportunistically coerced;
- existing rows and the accepted I-JSON bound CHECK behavior survive conversion;
- a second migration over BIGINT columns is a true widening no-op;
- fresh schema creation remains BIGINT from the start.

Do not claim a quantified lock-duration or concurrency guarantee. F7 multi-process
concurrency remains deferred. The accepted claim is narrower: an already-current BIGINT
schema does not issue the unnecessary type ALTER.

Implementation may retain WIDEN_IJSON_COLUMNS_SQL as the public test/import seam if useful.
Do not create a generic migration DSL for three columns.

## Fresh-versus-upgraded parity boundary

Add one catalog projection helper/test that compares a fresh current schema with the
supported legacy/additive path for the migration-owned invariants in this ticket.

Required parity is bounded to:

- the four named additive constraints above, including exact target relation, constraint
  type, and normalized pg_get_constraintdef output;
- the three I-JSON columns' final BIGINT catalog types;
- preservation of representative populated rows and existing provider recipe selection /
  envelope / Outcome / Organic context provenance needed by the legacy fixture.

Do not assert that every CHECK, primary key, foreign key, index, default, or column in every
historical hand-built test table is identical to a fresh schema. CREATE TABLE IF NOT EXISTS
does not constitute a general historical-schema reconciliation system, and PF-15 does not
authorize one.

If the existing supported upgrade fixtures represent more than one materially different
legacy boundary, the technical review must identify which path provides the decisive parity
proof and which existing tests remain separate regression coverage.

## Wrong-target and wrong-type behavior

The pre-implementation review must determine whether a correctly named but structurally
wrong constraint already present on the target table is possible under supported history.

Minimum PF-15 requirement:

- same name on the wrong relation must never satisfy the migration;
- correct accepted target constraint remains idempotent;
- unexpected I-JSON column type must fail closed.

Do not automatically drop, rename, or replace an existing target constraint unless the
technical review demonstrates a supported legacy state and the Steward amends the ticket.
Destructive catalog repair is not implicitly authorized.

## Implementation constraints

- GROK is the sole writer of src/ and tests/.
- Steward owns this ticket and any authority reconciliation.
- Preserve every accepted table, column, constraint name, and constraint definition.
- Preserve populated rows and current Derivation/API behavior.
- No schema-version ledger, Alembic adoption, migration file split, or generalized framework.
- No provider recipe, parser, identity, Derivation, Evidence, API, selection, or read-model
  change.
- No provider, DNS, credential, paid-gate, or network use.
- No new acquisition surface.
- Keep one bounded implementation commit; do not push without [CHAZ] authorization.

## Required tests

At minimum, real-PostgreSQL tests must prove:

- all four same-named decoy constraints on unrelated relations do not suppress installation
  on the target relations;
- exact target conrelid/name/type/definition match the accepted fresh schema;
- target uniqueness and Organic context-to-Outcome foreign-key behavior remain enforced;
- decoys survive untouched;
- a second apply is idempotent;
- existing genuine INTEGER columns widen to BIGINT with planted rows preserved;
- fresh BIGINT columns remain BIGINT;
- already-BIGINT widening takes the no-ALTER branch;
- one unexpected target-column type fails closed and does not report migration success;
- the bounded fresh-versus-upgraded catalog projection is equal and non-empty;
- accepted populated PF-08-to-PF-12 upgrade, fixture rows, recipe selection, Outcomes,
  envelopes, and Organic derive remain green;
- no provider/public-network path is invoked.

Avoid tests that pass merely because any row with the desired conname exists somewhere in
pg_constraint. Avoid comparing two empty catalog projections.

## Validation

Use focused real-PostgreSQL tests during TDD. Run the repository acceptance commands once
after the final implementation state:

- uv run pytest -q
- uv run ruff check .
- uv run mypy

Record UTC start/end, elapsed time, exit code, counts, exact HEAD, tree state before/after,
and remaining observatory-ce05-* containers. The full suite runs locally, not through the
synchronous MCP gateway.

## Out of scope

- full historical-schema diff/repair or destructive constraint replacement;
- schema-version ledger, Alembic, migration framework, down-migrations, or rollback engine;
- renaming current tables/columns/constraints;
- indexes or query-performance work unrelated to avoiding repeated type ALTER;
- database concurrency or lock-duration hammer claims;
- Evidence Store migration, backup automation, restore inventory, or F6/F7 work;
- AGENTS.md/spec/API-prefix authority refresh;
- element-level AIO null/absence semantics;
- API/read/Derivation changes;
- another acquisition surface or provider call.

## One implementation commit must prove

A same-named constraint elsewhere in PostgreSQL cannot suppress Observatory's required
additive target constraint, and current BIGINT schemas avoid unnecessary type ALTER while
the supported real INTEGER upgrade remains preserving and fail-closed.

## Mandatory pre-implementation technical review

Before editing any file, GROK must perform a deep read-only technical review against this
ticket and the exact Start commit.

The review must inspect:

- all SCHEMA_STATEMENTS and their dependency order;
- all four additive DO blocks and every foreign key depending on their target constraints;
- WIDEN_IJSON_COLUMNS_SQL and apply_schema transaction behavior;
- the real existing INTEGER conversion/bounds tests;
- PF-08 and PF-12 populated upgrade fixtures;
- every pg_constraint assertion in the current tests;
- PostgreSQL namespace, conrelid, regclass, contype, and backing-index behavior relevant to
  the proposed decoy test;
- whether an integrated four-decoy fixture is feasible without destructive setup;
- the smallest reliable proof that BIGINT takes no type-ALTER branch;
- the precise bounded fresh/upgrade parity projection.

GROK must identify false-green risks, dependency traps, lock/test flakiness, unsupported
legacy states, and any premise that would require destructive repair.

Stop and report exactly one final verdict:

- PROCEED UNCHANGED;
- AMEND TICKET;
- AUTHORITY DECISION REQUIRED.

No implementation, edit, commit, full suite, Docker mutation beyond ordinary read-only
inspection, or provider/network call occurs during the review. Implementation begins only
after Steward reconciliation.

## Implementer report required

The implementation commit must update PF-15 to review and record exact parent/child, changed
paths, acceptance-to-test map, and command evidence. It must report candidly:

- the exact catalog predicates used and why they identify the target relation;
- how decoy constraints were planted without invalidating the proof;
- which supported legacy path was compared with fresh schema;
- how the no-ALTER BIGINT branch is proved;
- behavior for missing/unexpected column types;
- dependencies and ordering among the four additive constraints;
- strongest and weakest tests and remaining false-green risk;
- migration lock/scaling implications without overclaiming concurrency;
- anything that should change the later authority refresh or next acquisition surface;
- confirmation of no provider/API/recipe/Derivation/Evidence/new-surface change;
- confirmation of no push.

Do not broaden implementation to repair adjacent migration history. Report it for Steward
reconciliation.

