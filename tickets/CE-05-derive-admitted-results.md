# CE-05 — Derive admitted_results into real PostgreSQL

**Status:** done
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-04 — Full fixture-panel-v1 matrix and all transport branches
**Approved by:** Project Steward
**Start commit:** 08f0b36923926cdecfe17da47e23dad8fa966687

## What to build

End-to-end behaviour this ticket makes work: from verified **admitted_results** Evidence,
register a derivation version, write Attempt-stage and Capture-stage Outcomes and the
depth-governed Observations into **real PostgreSQL**, expose `python -m observatory.derive`,
and prove atomicity and same-version idempotency for that slice.

This ticket is independently usable and reviewable without CE-06. It does not claim full
ten-scenario derive completion.

## Authority

- `docs/specs/capture-event-v2.md` — §Rebuildable PostgreSQL / entrypoints / API (`derivation_versions`, `outcomes`, `observations`; derive CLI)
- `docs/specs/capture-event-v2.md` — Observation natural identity; Attempt-stage Outcome rule; admission for successful complete response
- `docs/specs/capture-event-v2.md` — scenario row for `admitted_results` classification and Observation count
- `decisions/decisions.md` — D8 (disposable PostgreSQL; Observations only from verified complete admissible Captures; Outcome derived)
- `VISION.md` — §What v1 must prove item 3 (narrowed to admitted_results for this ticket)
- `VOCABULARY.md` — Outcome, Observation, Derivation, Provenance

## Scope

- Minimum authorized derivation substrate: `derivation_versions`, `outcomes`, `observations`
- Derive from verified Evidence only (verify-on-read before use)
- Attempt-stage `authorized_unresolved` and Capture-stage `observation_admitted` for admitted_results
- Observations with natural identity `(capture_id, derivation_version_id, within_capture_result_id)` and required provenance
- Derive entrypoint
- Atomic write of that Capture’s Outcome together with its Observations
- Same-version re-derive idempotency for this slice

## Out of scope

- The other nine scenario classifications (CE-06)
- Empty-database rebuild of the full matrix (CE-06)
- New derivation-version append without rewrite of prior versions (CE-06)
- Systematic refuse of all damage classes beyond what is needed for admitted_results verify-on-read (CE-06 expands)
- HTTP API, status/scrub CLIs
- Projection tables; optional “current views”; prescribed SQL uniqueness dialect (state observable uniqueness/idempotency only)

## Acceptance criteria

- [x] Starting from verified admitted_results Evidence and empty or freshly migrated PostgreSQL, derive produces the Attempt-stage Outcome (`authorized_unresolved`, `capture_id` null for that stage row) and the Capture-stage Outcome (`observation_admitted`) under a registered derivation version.
- [x] Exactly `depth` Observations are written with correct natural identities, provider/fixture axes, labels/scores, and provenance citing verified `attempt_id` and `capture_id`.
- [x] Derive uses verify-on-read; unverifiable Evidence for this path does not produce normal Observation rows.
- [x] Re-running the same derivation version does not duplicate or mutate existing Outcome/Observation rows for this slice (idempotency).
- [x] The Capture-stage Outcome and its Observations for this Capture are written atomically (no partial Observation set without the corresponding Capture-stage Outcome for a successful completion of the derive unit).
- [x] `python -m observatory.derive` performs this derivation.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: **real PostgreSQL** (e.g. compose Postgres) + real Evidence FS
- Forbidden claims: mock/in-memory DB success ≠ PostgreSQL proof

## Required automated tests

- Admission for admitted_results (Observation count = depth)
- Attempt-stage and Capture-stage Outcomes present
- Natural identity and provenance fields
- Same-version idempotency
- Atomicity of Capture-stage Outcome + Observations
- Derive CLI path
- Real PostgreSQL substrate

## Forbidden claims

- Full ten-scenario derive complete
- Multi-version append complete
- Full empty-matrix rebuild complete
- API or scrub complete

## One implementation commit must prove

Working derive spine for admitted_results on real PostgreSQL—truthful without CE-06.

## Later tickets

Later tickets are **not** required to make this ticket’s acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: supplied in the implementer handoff report (a commit cannot
  embed its own final hash).
- Acceptance evidence:
  - `uv run pytest -q` — 418 passed
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Real PostgreSQL 18.6 via ephemeral `postgres:18-alpine` container
    (or `OBSERVATORY_TEST_DATABASE_URL`); per-test `CREATE DATABASE` /
    `DROP DATABASE … WITH (FORCE)`. Tests fail closed, never skip.
  - Schema: `test_migrate_creates_authorized_tables`,
    `test_migrate_cli_on_real_postgres`
  - Version registration: `test_derive_registers_derivation_version`
  - Attempt-stage `authorized_unresolved` / `capture_id IS NULL`:
    `test_published_ar_attempt_stage_outcome`
  - Capture-stage `observation_admitted` + exact `depth` Observations:
    `test_published_ar_capture_stage_and_observations`,
    `test_depth_governs_observation_count`
  - Natural identity / axes / provenance: same two tests, independent
    published AR literals (not production body helpers)
  - Verify-on-read refuse: `test_tampered_capture_yields_no_observations`
  - Uncommitted residue ignored: `test_uncommitted_capture_residue_is_not_derived`,
    `test_list_committed_ids_ignores_uncommitted_residue`
  - Same-version idempotency (full row content + `xmin`):
    `test_same_version_rerun_does_not_duplicate_or_mutate`
  - Capture-unit atomicity / rollback:
    `test_capture_unit_rollback_leaves_no_partial_rows`
  - CLI: `test_derive_cli_on_real_postgres`
  - Media-type admission (AR attempt + H_plain Capture):
    `test_admitted_results_plain_media_type_is_not_admitted`
  - Conflicting derivation-version registration:
    `test_conflicting_adapter_contract_fails_before_derived_rows`
  - CE-02–CE-04 remain green in the same suite run
- Unproven limits:
  - Only `admitted_results` receives a Capture-stage Outcome.
    Other scenarios get Attempt-stage `authorized_unresolved` only.
  - `object.__setattr__` / monkeypatch of derive internals not defended.
  - No multi-version append, empty-DB full-matrix rebuild, concurrency,
    crash/fsync of PostgreSQL, or off-host recovery.
  - Docker leftover if the pytest process is killed before fixture teardown.
  - Derivation-version identity is an operator-supplied string, not a
    content-addressed recipe document.
- Review findings remaining:
  - `interrupt=` on `derive_admitted_results` is a test seam for
    atomicity injection, not public product API.
  - Steward decision: fixture v1 keeps the operator-supplied semantic label;
    same-label registration metadata must agree, and changed derivation
    behavior requires a new label.
  - Spec review: Capture-stage now also requires `transport_state =
    response_complete`, `completeness=complete`, and admitted count ==
    `depth`. Other silent-continue paths (failed admission, non-AR) still
    produce no Capture-stage row rather than a CE-06 classification.

## Closure

<!-- Project Steward only -->

- Closed at commit: `4d9471671400e58eb0533b409d30fa78478c50bb`
- Evidence accepted: yes
- Steward verification:
  - Exact comparison: `08f0b36923926cdecfe17da47e23dad8fa966687` through
    `4d9471671400e58eb0533b409d30fa78478c50bb`
  - `uv run pytest -q` — 418 passed on real PostgreSQL 18
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Disposable review regressions exposed and remediation closed media-type
    admission and conflicting derivation-version registration
