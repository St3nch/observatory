# CE-04 — Full fixture-panel-v1 matrix and all transport branches

**Status:** review
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-03B — admitted_results tracer: Attempt, transport, Capture, CLI
**Approved by:** Project Steward
**Start commit:** eb6695c665e3659d57d7f86b8d9529756312ee60

## What to build

End-to-end behaviour this ticket makes work: the deterministic fixture-panel-v1
response-construction algorithm for **all ten** scenarios and **every valid** parameter
combination; durable Capture for all three transport states with closed branch rules;
published RP and NR identity digests when frozen published vector inputs (including their
nonces) are used; and enforcement that each Attempt has at most one Capture.

## Authority

- `docs/specs/capture-event-v2.md` — §Fixture response-construction algorithm (helpers and per-scenario table)
- `docs/specs/capture-event-v2.md` — Capture branch rules (`response_complete`, `response_partial`, `no_response`)
- `docs/specs/capture-event-v2.md` — §Conformance vectors Sets RP and NR
- `docs/specs/capture-event-v2.md` — Invariant: ≤1 Capture per Attempt; construction order steps 7–8
- `decisions/decisions.md` — D8 (transport states; at most one Capture per Attempt)
- `VISION.md` — fixture-only path (matrix completeness for Evidence)

## Scope

- Parameter-general fixture transport for all ten scenarios
- All three transport states and closed null/branch rules
- RP/NR on-disk identity match for frozen published vector inputs (including nonces)
- At most one Capture per Attempt (write/admission enforcement)
- Capture CLI (or same service entrypoint) covers the full matrix

## Out of scope

- Derive, PostgreSQL Outcomes/Observations
- HTTP API
- status/scrub CLIs
- Journal product beyond authorized fixture skip
- Multi-Capture **scrub inventory** as a reporting taxonomy (enforcement is write-time here)
- Paid/network providers

## Acceptance criteria

- [ ] For every scenario in the closed ten-value enum and every valid `(panel_id, subject_key, depth)`, the fixture algorithm produces the mandated `transport_state`, headers (or no response), completeness, body state, and `transport_failure`, together with the authority-prescribed expected classification and Observation count; this ticket does not derive Outcomes or Observations.
- [ ] Automated verification exhaustively covers all ten scenarios at every valid depth `1..16` and uses parameter-general or property-based checks for schema-valid `panel_id` and `subject_key` values, including minimum- and maximum-length strings, permitted character classes, and the special `subject_key="other-subject"` branch. Generative tests prove the general construction rule; they do not claim to enumerate every possible valid string.
- [ ] `wrong_media_type` uses the deterministic admitted_empty body for the same parameters with `text/plain` content-type header.
- [ ] `response_partial` body is the first 32 UTF-8 bytes of JCS(`admitted_results_body(P,S,D)`).
- [ ] `extra_subject` and `too_many_results` commit Capture Evidence with correct transport completeness; they do not require Observations in this ticket.
- [ ] The published RP and NR identity digests match when the frozen published vector inputs, including their nonces, are used.
- [ ] A second Capture commit for the same Attempt is rejected; at most one Capture per Attempt holds.
- [ ] Branch null rules for `no_response` / partial / complete are enforced (closed Capture schema).
- [ ] Attempt remains committed before transport for every scenario path.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: real local POSIX temporary Evidence roots
- Forbidden claims: no derive/API completeness; no live provider

## Required automated tests

- All ten fixture-panel-v1 scenarios
- Every valid depth `1..16` across all ten scenarios
- Parameter-general or property-based coverage of schema-valid `panel_id` and `subject_key`, including minimum/maximum lengths, permitted character classes, and `other-subject`
- Transport-state branch tests (complete, partial, no_response)
- Published RP/NR identity digests with frozen published vector inputs (including nonces)
- At most one Capture per Attempt (negative second Capture)
- Attempt-before-transport retained for multi-scenario CLI paths

## Forbidden claims

- Full derive classification matrix complete
- API or scrub product complete
- Off-host or multi-process safety

## One implementation commit must prove

Complete fixture Evidence surface: all scenarios, all transport branches, ≤1 Capture—without needing later tickets for that claim.

## Later tickets

Later tickets are **not** required to make this ticket’s acceptance criteria truthful.

## Beyond authority

This ticket adds **no** behavior beyond committed authority.

## Implementation report

<!-- implement fills; may set Status: review; never Status: done -->

- End commit: supplied in the implementer handoff report (a commit cannot
  embed its own final hash).
- Acceptance evidence:
  - `uv run pytest -q` — 330 passed
  - `uv run ruff check .` — clean
  - `uv run mypy` — clean
  - Ten scenarios × depths 1..16 (algorithm):
    `test_algorithm_all_scenarios_all_depths`
  - Durable store path, all ten scenarios:
    `test_store_all_scenarios_durable`
  - Character classes / min / max / other-subject:
    `test_algorithm_panel_and_subject_tokens`,
    `test_algorithm_min_length_tokens`,
    `test_extra_subject_alt_key_and_other_subject_branch`,
    `test_store_extra_subject_other_subject_key`
  - Branch rules: `wrong_media_type` /
    `test_wrong_media_type_body_matches_admitted_empty`;
    partial / malformed in `test_algorithm_all_scenarios_all_depths`;
    `test_malformed_bytes_are_exactly_45_and_have_no_trailing_newline`
  - Published AR/RP/NR:
    `test_ar_entrypoint_still_matches_published_ids`,
    `test_published_rp_identities_and_partial_body`,
    `test_published_nr_identities_and_no_response_body`
  - ≤1 Capture: `test_second_capture_for_same_attempt_rejected`,
    `test_uncommitted_capture_residue_is_ignored_by_uniqueness`,
    `test_corrupt_committed_capture_during_uniqueness_is_integrity_failure`
  - D8 every scenario: `test_attempt_before_transport_every_scenario`
    plus existing CE-03B forgery/store-type tests
  - CLI: `test_cli_vector_rp`, `test_cli_scenario_covers_matrix`,
    existing `test_cli_prints_both_full_ids`
- Unproven limits:
  - Durable store path is all 10 scenarios at depth 2 (plus published vectors).
    Depths 1..16 are proven on the pure algorithm, not 160 full Evidence commits.
  - panel_id/subject_key coverage is representative tokens, not every string
    matching `[A-Za-z0-9._:-]{1,128}`.
  - Uniqueness scan is O(committed captures) with full D5 per bundle; one writer.
  - No derive, Observations, PostgreSQL, concurrent writers, or crash recovery.
- Review findings remaining:
  - `capture_admitted_results` and `--evidence-root` alone still produce published
    AR. `--vector AR|RP|NR` and `--scenario NAME` cover the matrix. Classification
    and Observation count are returned, not persisted.

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
