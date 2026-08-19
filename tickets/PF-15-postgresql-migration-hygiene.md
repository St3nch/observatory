# PF-15 — PostgreSQL migration catalog and widening hygiene

**Status:** done  
**Owner:** [GROK] implementation / [GPT] Steward review  
**Blocked by:** none; PF-14 closed  
**Approved by:** Project Steward  
**Start commit:** `239623b29b82c57db779775ae696fcea0d1a747e`

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

## Implementation report

**Parent:** `239623b29b82c57db779775ae696fcea0d1a747e`  
**Child:** supplied in the implementer handoff (a commit cannot embed its own final hash).  
**Status:** `review`

### Loaded skills

- `/home/chaz/projects/vedaops/observatory/.grok/skills/implement/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/codebase-design/SKILL.md`
- `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`

### A. Start gate

- branch: `main`
- exact HEAD: `239623b29b82c57db779775ae696fcea0d1a747e`
- working tree: dirty only with this ticket's authorized files at validation time
- PF-15: `ready` at assignment; set `in-progress` then `review`
- local `main` was one commit ahead of `origin/main` at start

### B. Changed paths

- `src/observatory/migrate.py`
- `tests/test_derive_admitted_results.py`
- `tests/test_provider_recipe_selection.py`
- this ticket

No API, provider, recipe, parser, Derivation, Evidence, selection, or new-surface change.

### C. Behavior

Additive existence probes now require both the accepted `conname` and
`conrelid = '<table>'::regclass` for:

- `outcomes_identity` on `outcomes`
- `provider_recipes_adapter_version` on `provider_recipes`
- `observation_envelopes_kind_identity` on `observation_envelopes`
- `google_organic_result_context_outcome` on `google_organic_result_context`

Unqualified `regclass` follows the same search_path resolution as the existing
CREATE/ALTER statements. Constraint names and definitions are unchanged.

I-JSON widening is a bounded helper over the three exact targets. Catalog type
`int4` executes `ALTER COLUMN ... TYPE BIGINT`. Catalog type `int8` returns
`skip` and does not issue the type ALTER. A missing column or any other type
raises `SchemaError` before `apply_schema` commits. Transaction/commit shape is
unchanged: statements run, then widen, then one commit.

`WIDEN_IJSON_COLUMNS_SQL` remains the generated public import seam used by the
populated PF-08 fixture. `apply_schema` no longer executes those strings
unconditionally.

### D. Acceptance map

| Criterion | Proving test |
|---|---|
| Same-named CHECK decoys do not suppress target constraints | `test_same_named_decoys_do_not_suppress_target_constraints` |
| Target relation + name + type + normalized definition | same; `_additive_constraint_projection` |
| Target uniqueness is `outcomes_identity` | `test_same_named_decoys_do_not_suppress_target_constraints` (`diag.constraint_name`) |
| Organic context FK is `google_organic_result_context_outcome` after valid recipe/version | same (`diag.constraint_name`; isolated savepoint) |
| Seeded fixture survives both isolated violations | same (`_populated_provenance_projection` after second apply) |
| Decoys survive untouched | same; `_decoy_constraint_projection` |
| Second `apply_schema` is idempotent | same (`second == first` after both savepoints) |
| Genuine INTEGER start widens and preserves planted rows | `test_apply_schema_upgrades_integer_columns_and_preserves_rows` |
| Fresh schema starts BIGINT | `test_fresh_schema_ijson_columns_are_bigint` |
| I-JSON bounds and adjacent rejection | `test_ijson_column_bounds_accepted_and_adjacent_rejected` |
| Already-BIGINT takes no type ALTER (`skip`,`skip`,`skip`) | `test_already_bigint_schema_skips_type_alter` |
| Unexpected type fails closed; no success commit | `test_unexpected_ijson_column_type_fails_closed` |
| Missing column fails closed | `test_missing_ijson_column_fails_closed` |
| Fresh vs decoy/incomplete-target catalog + pre-upgrade row survival | `test_fresh_and_decoy_upgrade_share_bounded_catalog` |
| Global `conname` probes tightened | `test_migrate_creates_authorized_tables`; `test_additive_selection_schema_works_on_populated_pf07_tables` |
| Populated PF-08→PF-12 upgrade remains green | `test_populated_pf08_schema_then_organic_derive` |
| Recipe selection / envelopes / Outcomes / Organic derive | existing PF-04/PF-08/PF-12 tests remain green |

### E. Validation

First implementation suite (HEAD `239623b`, dirty product + tests + ticket):

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-19T00:21:20Z | 2026-08-19T00:23:53Z | 153 s (pytest 152.64 s) | 0 |
| `uv run ruff check .` | 2026-08-19T00:24:04Z | 2026-08-19T00:24:04Z | 0 s (second resolution) | 0 |
| `uv run mypy` | 2026-08-19T00:24:04Z | 2026-08-19T00:24:04Z | 0 s (second resolution) | 0 |

Remediation suite (HEAD `c7676ee0a95fbebc35cec355a2ffc383a4dedcf2`; dirty
`tests/test_derive_admitted_results.py` and this ticket only):

| Command | UTC start | UTC end | Elapsed | Exit |
|---|---|---|---|---|
| `uv run pytest -q` | 2026-08-19T00:35:19Z | 2026-08-19T00:37:49Z | 150 s (pytest 149.66 s) | 0 |
| `uv run ruff check .` | 2026-08-19T00:37:49Z | 2026-08-19T00:37:49Z | 0 s (second resolution) | 0 |
| `uv run mypy` | 2026-08-19T00:37:49Z | 2026-08-19T00:37:50Z | 1 s | 0 |

`911 passed, 1 skipped, 1 warning`. 48 source files. No leftover
`observatory-ce05-*` container. After the remediation pytest run, only this
report / status change was added. No `src/` or `tests/` bytes changed after
that pytest. No `src/` change in the remediation.

### F. Review

Code-review against `239623b29b82c57db779775ae696fcea0d1a747e`.
Standards and Spec axes ran as parallel read-only sub-agents on the first
implementation tree, then again on the test-only remediation.

**Standards:** 0 hard. Residual judgement unchanged: private
`_widen_ijson_columns` no-ALTER seam; `"skip"`/`"alter"` strings; repeated
DO-block shape; dual widen import seam; `current_schema()` + `relname` versus
unqualified `regclass`. Remediation added a shared populated-row projection
helper in tests only.

**Spec:** first implementation left two false-green proofs (whole-connection
rollback after `UniqueViolation`; post-migration Outcome-only seed). Remediation
closes both. Remaining residuals: decoy test still uses UNIQUE/FK substrings
for definition while parity holds full normalized defs; insert uniqueness is
still outcomes + Organic FK, not the other two UNIQUEs; INTEGER conversion
still does not re-insert adjacent I-JSON bounds.

### G. Candid assessment

**Catalog predicates.**
`WHERE conrelid = '<table>'::regclass AND conname = '<accepted>'`.
`regclass` identifies the search_path relation the CREATE/ALTER statements
already use. `conname` alone is not a database-global identity.

**Decoy planting.** Four unrelated tables
(`decoy_outcomes_identity`, `decoy_recipes_adapter_version`,
`decoy_envelopes_kind_identity`, `decoy_organic_context_outcome`) each carry a
same-named `CHECK (true)`. UNIQUE decoys were not used: their backing index
names are schema-unique and can collide, proving the wrong thing. Targets were
created incomplete (no additive constraints), not as a fresh current schema
with production constraints dropped. `apply_schema` then installed the four
target constraints.

**Parity path.** Fresh current schema (`postgres_second_dsn` +
`apply_migrations`) versus the decoy/incomplete-target upgrade. Catalog
projection remains target relation, `conname`, `contype`, normalized
`pg_get_constraintdef`, plus the three I-JSON BIGINT types. Populated
projection now includes derivation version, Attempt-stage and Capture-stage
Outcomes, provider recipe, observation envelope, and Organic result context.
Those rows are seeded and committed on the incomplete targets *before*
`apply_schema`; the same projection is compared after upgrade and against an
equivalent fresh seed. INTEGER-start and populated PF-08→PF-12 remain
separate regression boundaries.

**No-ALTER proof.** `_widen_ijson_columns` returns `("skip", "skip", "skip")`
when all three catalog types are `int8`. A recording execute wrapper was
abandoned after mypy rejected an untyped Connection stand-in; the
action-returning helper is the ticket-authorized alternative. A second
row-preserving `apply_schema` is not treated as no-ALTER proof.

**Missing / unexpected types.** Missing column and non-`int4`/`int8` types
raise `SchemaError` and do not reach `commit()`. Unexpected `text` remains
`text`. Representative coverage is `outcomes.observation_count`; the helper
uses one loop for all three targets.

**Dependencies.** `outcomes_identity` is the UNIQUE that Organic context
references. `provider_recipes_adapter_version` is the UNIQUE that selections
reference. `observation_envelopes_kind_identity` is the UNIQUE that typed
observation tables reference. The integrated fixture did not expose a
dependency problem; `CREATE TABLE IF NOT EXISTS` leaves incomplete targets in
place and the DO blocks add the missing constraints in `SCHEMA_STATEMENTS`
order.

**Strong.** Honest CHECK decoy adversary on one `apply_schema` path. Catalog
assertions are relation-scoped. Genuine INTEGER conversion test kept, not
replaced. Fail-closed widening. Pre-upgrade populated rows survive additive
constraints and match a fresh seed. Isolated savepoints assert exact
constraint names.

**Weak.** INTEGER conversion proves planted-row survival and BIGINT types, not
a post-ALTER adjacent-bound insert; I-JSON bound CHECKs remain proven on the
fresh schema. No-ALTER is proved at the helper seam, not by intercepting
`apply_schema`'s internal execute list. Incomplete targets are hand-built
subsets, not historical dumps. `test_provider_recipe.py` still has a
`derivation_diagnostics_identity` catalog check that was not an identified
PF-15 assertion.

**False-green risks closed in remediation.** Whole-connection rollback after
the duplicate Outcome insert no longer erases the recipe/version fixture.
Organic FK proof now requires `diag.constraint_name ==
google_organic_result_context_outcome` with a capture_id that lacks only the
composite Outcome. Parity no longer seeds only after migration or compares
Outcomes alone.

**False-green risks remaining.** A correctly named wrong-definition constraint
already on the target still satisfies `IF NOT EXISTS` and is skipped. That is
an unsupported state: PF-15 does not drop, replace, or silently repair it.
Global `conname` probes outside the identified tests can still false-green.

**Lock / scaling.** Skipping `ALTER COLUMN ... TYPE BIGINT` on already-`int8`
columns avoids repeating that catalog rewrite on current schemas. No lock
duration, concurrency, or multi-process claim. INTEGER conversion still issues
the type ALTER. F7 remains deferred.

**Unsupported states.** Wrong-definition-on-correct-target; unexpected column
types other than the fail-closed refusal; schema-qualified vs unqualified
split; historical tables beyond the three I-JSON columns and four additive
constraints.

**Later authority / next surface.** Additive migrations must key
`(conrelid, conname)`. Do not treat PostgreSQL constraint names as global.
UNIQUE decoys are the wrong collision adversary. Do not add a migration DSL or
destructive catalog surgery from this ticket.

**Ticket premises.** All held. Integrated four-decoy path was feasible. The
audit claim that INTEGER-start proof was missing remains obsolete.

### H. Confirmations

- no API / provider / recipe / parser / Derivation / Evidence / selection /
  new-surface change
- no provider / DNS / credentials / paid-gate use
- no push

### I. Commit

- parent SHA: `239623b29b82c57db779775ae696fcea0d1a747e`
- child SHA: recorded in this amended implementation commit
- previous child `c7676ee0a95fbebc35cec355a2ffc383a4dedcf2` is replaced by amend
  and was never pushed

### J. Remediation

Steward accepted production `migrate.py` and required two test-only proofs.

Finding 1: seed now runs on the incomplete targets and `apply_schema` commits
those rows before adversarial inserts. Each violation uses
`connection.transaction()`. Duplicate Outcome asserts `outcomes_identity`.
Organic insert keeps derivation version `aa…`, recipe, and Attempt `ab…`
valid and uses capture_id `ff…` so only the composite Outcome is missing;
the exception must be `google_organic_result_context_outcome`. The second
`apply_schema` still runs after both savepoints.

Finding 2: `_populated_provenance_projection` captures version, both
Outcome stages, recipe, envelope, and Organic context. That projection is
taken before upgrade, committed, compared after `apply_migrations`, and
compared to an equivalent fresh seed. Catalog comparison is unchanged.

The pre-upgrade seed accepted the four additive constraints. No production
defect. No `src/` change.

## Steward closure — 2026-08-18

**Accepted by:** Project Steward  
**Accepted implementation:** `8d49005834cdf55c16abc8915b17935c9527d850`  
**Accepted parent:** `239623b29b82c57db779775ae696fcea0d1a747e`

PF-15 is accepted and closed after GROK's mandatory pre-implementation
technical review, ticket reconciliation, one amended bounded implementation
commit, independent Steward code review, and independent operator verification.

The four additive PostgreSQL constraint probes now bind both the accepted
constraint name and the intended target relation. Same-named constraints on
unrelated tables therefore cannot suppress installation on `outcomes`,
`provider_recipes`, `observation_envelopes`, or
`google_organic_result_context`. The integrated decoy path proves the exact
installed `outcomes_identity` uniqueness constraint and
`google_organic_result_context_outcome` foreign key through isolated
savepoints, preserving the seeded fixture across both adversarial inserts and
a second idempotent `apply_schema` call.

The bounded I-JSON migration path now inspects exactly
`outcomes.observation_count`, `observations.result_index`, and
`observations.score`: `int4` widens to `BIGINT`, `int8` is skipped, and a
missing or unexpected type fails closed with `SchemaError` before the success
commit. Existing INTEGER rows survive widening; fresh and already-BIGINT
schemas retain the accepted I-JSON boundary behavior.

Fresh-versus-upgrade parity covers the four relation-scoped constraints, their
types and normalized definitions, the three BIGINT catalog types, and a
non-empty provenance projection. Derivation version, Attempt-stage and
Capture-stage Outcomes, provider recipe, observation envelope, and Organic
result context are planted before upgrade, survive unchanged, and equal the
same rows on a fresh current schema.

Independent Steward review found no authority, spec, correctness, security, or
scope blocker after the two test-proof remediations. The remediation changed no
production bytes. Independent static verification at the accepted child:

- `uv run ruff check .`: clean;
- `uv run mypy`: clean, 48 source files.

Independent operator verification at the accepted child:

- exact HEAD `8d49005834cdf55c16abc8915b17935c9527d850`;
- clean working tree before and after;
- `uv run pytest -q`: 911 passed, 1 skipped, 1 upstream Starlette/httpx
  deprecation warning, exit 0;
- 147.97 seconds wall time;
- no remaining `observatory-ce05-*` container.

Accepted limits remain explicit. PF-15 does not repair a correctly named but
wrong-definition constraint already present on the correct target, invent a
migration framework, make schema-qualified policy changes, or claim lock-time
or concurrent-migration guarantees. The already-BIGINT no-ALTER proof remains
at the bounded helper seam; unsupported historical shapes continue to fail
closed or require Steward reconciliation rather than destructive catalog
surgery.

No API, provider, recipe, parser, identity, Derivation, Evidence, selection,
credential, paid-gate, network, or new-surface change occurred. Nothing was
pushed during closure.
