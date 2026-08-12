# CE-04 — Full fixture-panel-v1 matrix and all transport branches

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-03 — First durable Capture Event: admitted_results
**Approved by:** Project Steward
**Start commit:**

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

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
