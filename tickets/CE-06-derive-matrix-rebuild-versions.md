# CE-06 — Derive completion: matrix, rebuild, multi-version, damaged refuse

**Status:** done
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-05 — Derive admitted_results into real PostgreSQL
**Approved by:** Project Steward
**Start commit:** d26d5a002199449dd221bd770940ddf0d31fa8e6

## What to build

End-to-end behaviour this ticket makes work: derive **all ten** fixture scenarios so every
verified Attempt has its Attempt-stage `authorized_unresolved` Outcome and every Capture
has its authorized Capture-stage Outcome (with Observations only where admitted); rebuild an empty PostgreSQL database from
verified Evidence with **logical** equivalence; append a new derivation version without
rewriting prior derivation rows; refuse derived data that depends on damaged Evidence while
preserving derivation from independently verified Evidence; and ignore uncommitted material.

## Authority

- `docs/specs/capture-event-v2.md` — §Fixture response-construction algorithm (classification and Observation count per scenario)
- `docs/specs/capture-event-v2.md` — §Rebuildable PostgreSQL / entrypoints
- `docs/specs/capture-event-v2.md` — §Canonicalization and verify-on-read (fail closed; never silent repair)
- `docs/specs/capture-event-v2.md` — §Commit visibility (uncommitted is not Evidence)
- `VISION.md` — §What v1 must prove items 3 and 5
- `decisions/decisions.md` — D8 (rebuildable PostgreSQL; verify-on-read)

## Scope

- Full ten-scenario Attempt-stage and Capture-stage Outcomes, classifications, and Observation counts
- Empty-PostgreSQL rebuild from verified Evidence with logical equivalence (defined below)
- New derivation version appends without mutating prior derivation-version rows
- Refuse Capture-stage Outcomes and Observations that depend on a Capture or cited body that fails verify-on-read
- Preserve the Attempt-stage Outcome when its parent Attempt remains independently verified
- No derived rows from uncommitted material, which is not Evidence

## Out of scope

- HTTP API
- status/scrub CLIs (CE-08)
- Projection tables
- Off-host restore proof (F6)
- Inventing physical DB dump equivalence

## Rebuild equivalence (mandatory definition)

Empty-PostgreSQL rebuild equivalence is **logical data equivalence**, not physical or
byte-for-byte database equivalence.

The rebuilt database must contain the same authorized:

- derivation-version identity;
- Attempt-stage and Capture-stage Outcomes;
- Observation natural identities;
- classifications;
- provenance;
- Observation values and counts.

Comparison must use stable natural keys or an equivalently deterministic normalized row
representation. Database row order, insertion order, physical storage, sequence state,
and raw table-dump bytes are **not** equivalence requirements unless committed authority
expressly makes them normative (it does not).

## Acceptance criteria

- [x] For every verified Attempt across all ten scenarios, derive produces an Attempt-stage `authorized_unresolved` Outcome with `capture_id` null, and the corresponding verified Capture produces the scenario-authorized Capture-stage Outcome.
- [x] Observations are produced only for admitted cases and have the normative count for each scenario.
- [x] After derive into a populated DB, an empty PostgreSQL instance re-derived from the same verified Evidence is logically equivalent per the definition above.
- [x] A new derivation version appends its Outcomes/Observations without rewriting or deleting prior derivation-version rows.
- [x] A Capture or cited body that fails verify-on-read produces no Capture-stage Outcome or Observations from that damaged Capture, while an independently verified parent Attempt still produces its Attempt-stage `authorized_unresolved` Outcome; material lacking `COMMITTED` visibility is not used as Evidence.
- [x] CE-05 admitted_results behavior remains true under the expanded matrix.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: **real PostgreSQL** + real Evidence FS
- Forbidden claims: mock PG ≠ proof; not off-host disaster recovery

## Required automated tests

- All ten scenarios with both the Attempt-stage `authorized_unresolved` Outcome (`capture_id` null) and the authorized Capture-stage Outcome
- All ten classification and Observation-count cases, including no Observations outside admitted cases
- Logical empty-PG rebuild equivalence (stable natural-key comparison), including every Attempt-stage Outcome
- Multi-version append without rewrite
- Damaged Attempt → no Outcome or Observation rows from that Attempt
- Damaged Capture or cited body → no Capture-stage Outcome or Observations from that Capture, while an independently verified parent Attempt still derives its Attempt-stage Outcome
- Uncommitted material → no derived rows
- Real PostgreSQL substrate

## Forbidden claims

- API integrity HTTP complete (CE-07)
- Scrub report product complete (CE-08)
- Off-host backup/restore

## One implementation commit must prove

Full fixture derive/rebuild/multi-version/refuse-damaged surface—without needing CE-07/CE-08 for those claims.

## Later tickets

Later tickets are **not** required to make this ticket’s acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: supplied in the implementer handoff report (a commit cannot
  embed its own final hash).
- Acceptance evidence:
  - `uv run pytest -q` — 431 passed
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Ten Attempt-stage + Capture-stage Outcomes:
    `test_all_ten_attempt_and_capture_stage_outcomes`
  - Observation counts / only admitted_results:
    `test_observation_counts_only_admitted_results`
  - AR identity/values/provenance:
    `test_admitted_results_identity_values_and_provenance`
  - admitted_empty zero Observations:
    `test_admitted_empty_success_has_zero_observations`
  - Depth 1 and 16 AR:
    `test_admitted_results_depth_boundaries`
  - Classification from Capture, not scenario name:
    `test_classification_follows_capture_not_scenario_name`
  - Logical rebuild, two real DBs:
    `test_logical_rebuild_equivalence_two_real_databases`
  - Multi-version append + prior xmin:
    `test_new_version_appends_without_mutating_prior`
  - Damaged Attempt isolation:
    `test_damaged_attempt_refuses_only_that_chain`
  - Damaged Capture / body, Attempt preserved:
    `test_damaged_capture_preserves_valid_attempt_and_other_chain`,
    `test_damaged_response_body_preserves_attempt_stage`
  - Uncommitted ignored: `test_uncommitted_material_is_ignored`
  - CE-05 media-type / atomicity / idempotency / CLI /
    conflict-registration remain in
    `tests/test_derive_admitted_results.py`
- Unproven limits:
  - Durable matrix uses depth 2 plus AR depths 1 and 16, not 160
    Evidence commits.
  - Header eligibility is exact-list equality.
  - No physical dump, crash/fsync, concurrency, or off-host claims.
  - Damage cases are representative, not the CE-08 scrub product.
  - `0 < result_count < depth` is treated as `observation_admitted`
    with that many Observations (admission success); fixture
    construction never produces that body.
- Review findings remaining:
  - Steward answer: CE-06 completes the already-authorized fixture-v1
    derivation meaning; it does not redefine that meaning. A later semantic
    behavior change must use a new `derivation_version_id`. Reusing a label
    under changed code would violate authority. With fixture-v1's deliberately
    minimal registration metadata, no additional code-level comparison can
    detect such a change when `adapter_contract` still matches.
  - `interrupt=` remains a test seam on `derive`.
  - CE-05 planted H_plain-on-AR now also writes Capture-stage
    `transport_complete_non_admissible` (still zero Observations).

## Closure

<!-- Project Steward only -->

- Closed at commit: `85c60c84addab26bc66f3150675d177c49b26e93`
- Evidence accepted: yes
- Steward verification:
  - Exact comparison: `d26d5a002199449dd221bd770940ddf0d31fa8e6` through
    `85c60c84addab26bc66f3150675d177c49b26e93`
  - `uv run pytest -q` — 431 passed on real PostgreSQL 18
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Full matrix, two-database logical rebuild, multi-version append,
    dependency-bounded damage refusal, and uncommitted-ignore proofs accepted
