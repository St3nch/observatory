# AUD-01 — Fixture milestone audit cleanup

**Status:** review
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** milestone audit remediation
**Blocked by:** none
**Approved by:** Project Steward
**Start commit:** fc94b80849ed1e068a08f8e7a659fcf8b73bb32d

## Why this ticket exists

The accepted fixture-v1 milestone audit found two bounded claim-precision defects:

1. the real-PostgreSQL test proves PostgreSQL, but does not itself require the exercised
   server to be major version 18; and
2. three SQL columns are `INTEGER` while their CHECK constraints name I-JSON safe-integer
   bounds outside the `INTEGER` range, making the upper/lower bounds unreachable.

Neither finding invalidates the accepted milestone. This ticket closes them without
reopening CE-02 through CE-08. The same audit raised a D8 wording question about the pure
fixture conformance calculator; the parent authority now clarifies that pure byte
calculation is not transport or Evidence creation, while every service path that adopts
the result as testimony remains gated.

## What to build

- Make the permanent real-PostgreSQL test assert that the **exercised connection** is
  PostgreSQL major version 18. This must also apply when
  `OBSERVATORY_TEST_DATABASE_URL` selects an existing server: a different major fails
  rather than silently supporting a “tested on PostgreSQL 18” claim.
- Make these existing columns `BIGINT`, retaining meaningful I-JSON safe-integer bounds:
  - `outcomes.observation_count`
  - `observations.result_index`
  - `observations.score`
- Make schema application idempotently upgrade an existing Observatory schema whose three
  columns still use `INTEGER`. Preserve existing rows; do not drop or recreate the
  tables.

Use PostgreSQL's numeric server-version setting for the major-version assertion rather
than depending on presentation text.

## Acceptance criteria

- [ ] The permanent suite fails closed unless its exercised PostgreSQL server is major
      version 18.
- [ ] A newly created schema declares all three named columns as `BIGINT`.
- [ ] Their existing domain rules remain true and database-enforced:
  - `observation_count` accepts 0 through 9007199254740991;
  - `result_index` accepts 1 through 9007199254740991;
  - `score` accepts -9007199254740991 through 9007199254740991.
- [ ] Real-PostgreSQL tests demonstrate that representative safe boundary values are
      accepted and values just outside the stated bounds are rejected by PostgreSQL.
- [ ] Starting from the prior `INTEGER` column shape with existing rows, schema
      application upgrades the three columns to `BIGINT` without losing or changing
      those rows.
- [ ] Applying the schema again is successful and does not change existing row values.
- [ ] Existing fixture-v1 derivation, rebuild, API, and Evidence behavior remains green.
- [ ] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

## Required automated tests

- Exercised server major version equals 18.
- Fresh-schema types for all three columns.
- PostgreSQL acceptance at the stated safe boundaries and rejection immediately outside
  them.
- Upgrade from the prior `INTEGER` schema with row preservation.
- Repeated schema application.

## Scope constraints

- One implementation commit; do not amend or push.
- Implementer may change only:
  - `src/observatory/migrate.py`
  - `tests/test_derive_admitted_results.py`
  - this ticket's implementation-report section
- Do not change capture, Evidence Store, fixture algorithm, derive behavior, API routes, or
  derivation-version semantics.
- Do not add a general migration framework or a schema-version table.
- Do not reopen or edit completed CE tickets.

## Out of scope

- The cosmetic `/api/v1` docs/OpenAPI prefix residue
- Provider transports or DataForSEO
- Same-label derivation meaning changes
- PostgreSQL crash, fsync, concurrency, or off-host recovery claims
- Any claim that PostgreSQL is authoritative Evidence

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- Substrate: real PostgreSQL 18
- Review must compare this ticket's exact Start commit through the implementation commit.

## Implementation report

<!-- Implementer fills; may set Status: review; never Status: done. -->

- End commit: supplied in the implementer handoff report (a commit cannot
  embed its own final hash).
- Start commit: `fc94b80849ed1e068a08f8e7a659fcf8b73bb32d`
- Acceptance evidence:
  - `uv run pytest -q` — 471 passed on real PostgreSQL 18
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Exercised major version 18:
    `test_real_postgres_is_postgresql` reads `SHOW server_version_num` on the
    same `postgres_dsn` connection the suite uses (including when
    `OBSERVATORY_TEST_DATABASE_URL` selects the server) and requires
    `int(server_version_num) // 10000 == 18`. It does not parse
    `server_version` text or the Docker image name.
  - Fresh-schema types: `test_fresh_schema_ijson_columns_are_bigint`
  - I-JSON bounds accepted and adjacent values rejected by PostgreSQL CHECK:
    `test_ijson_column_bounds_accepted_and_adjacent_rejected`
  - INTEGER → BIGINT upgrade with row preservation and repeated apply:
    `test_apply_schema_upgrades_integer_columns_and_preserves_rows`
- Unproven limits:
  - The major-18 assertion lives in this module because `tests/conftest.py`
    is outside the ticket's permitted paths. A pytest invocation that
    excludes `test_real_postgres_is_postgresql` can still run other tests
    against a non-18 server.
  - `ALTER COLUMN … TYPE BIGINT` is a lossless widen, not crash/fsync/
    concurrency proof. PostgreSQL remains disposable, not Evidence.
  - Upgrade proof reconstructs the prior INTEGER CREATE TABLE shape in the
    test; it is not a restore of a production dump.
- Remaining review findings:
  - Standards: 0 hard / judgement-only duplication of the prior INTEGER
    CREATE TABLE (intentional so the prior shape cannot track the live
    schema). Duplicate major-18 test removed after review.
  - Spec: 0 findings.


## Closure

<!-- Project Steward only -->
