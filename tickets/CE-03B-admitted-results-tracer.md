# CE-03B — admitted_results tracer: Attempt, transport, Capture, CLI

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-03 — Evidence Store foundation: format, durable install, commit and read
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: using the CE-03 store, durably commit an
Attempt before any transport, run in-process **admitted_results** transport, durably commit
the Capture, and expose the deterministic fixture Capture CLI — such that published AR
identity digests match on disk when frozen published vector inputs are used, and transport
cannot begin before the Attempt is committed and verified.

This ticket covers only the **`response_complete`** transport branch as exercised by
**`scenario=admitted_results`**. It does not complete all three transport states.

CE-03 supplies the store. This ticket supplies the vertical path through it.

## Authority

- `docs/specs/capture-event-v2.md` — §Normative construction order
- `docs/specs/capture-event-v2.md` — §Durability profile `local-posix-fsync-v1` D8 (no
  transport before durable Attempt), and D4's rule for which bundle holds which body
- `docs/specs/capture-event-v2.md` — §Closed schemas (Attempt, Capture, request, body)
- `docs/specs/capture-event-v2.md` — §Conformance vectors Set AR
- `docs/specs/capture-event-v2.md` — fixture-panel-v1 request constants; the
  `admitted_results` path of §Fixture response-construction algorithm
- `docs/specs/capture-event-v2.md` — fixture journal skip only when the full in-process
  result is retained before Capture construction
- `decisions/decisions.md` — D8 (Attempt before transport)
- `VISION.md` — §What v1 must prove items 1–2, narrowed to admitted_results

## Scope

- Attempt construction per §Normative construction order steps 1–6, committed to the CE-03
  store
- D8 enforced structurally: the transport call is unreachable from any path that has not
  first obtained a verified committed Attempt
- In-process `admitted_results` fixture transport, zero choices, per the fixture algorithm
- Capture construction and commit for the `response_complete` branch
- Deterministic fixture Capture CLI at `uv run python -m observatory.capture`; prints
  `attempt_id` and `capture_id`
- Fixture journal skip only under the authorized full in-process retention rule — no
  journal product for future providers

## Out of scope

- The other nine fixture scenarios
- `response_partial` and `no_response` branches, and RP/NR vectors
- Store mechanism, durability protocol, verify-on-read implementation — all CE-03
- Derive, PostgreSQL, HTTP API, status/scrub CLIs
- Multi-process locking (F7), off-host backup (F6), paid providers (F3)

## Acceptance criteria

- [ ] Using frozen published AR vector inputs, the on-disk Attempt and Capture identities match published `attempt_id` `46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f` and `capture_id` `604663f0e7842f1e076189652667357083d4c4a5e56a44d67ea4596ef624ad44`.
- [ ] The Attempt bundle contains `request.body`; the Capture bundle contains `response.body`; neither contains the other's, per §Durability profile D4.
- [ ] Automated proof that fixture transport cannot begin until the Attempt is committed and verified. An ordering assertion inside one happy-path function is not proof — show why the transport call is unreachable otherwise.
- [ ] `admitted_results` transport is deterministic and in-process, and produces exactly the published AR response body bytes and digest.
- [ ] Capture CLI completes the admitted_results Attempt→Capture path and prints `attempt_id` and `capture_id`; it does not write PostgreSQL and does not derive.
- [ ] The journal is not written for this path, and the authorized full in-process retention condition holds.
- [ ] Verify-on-read of the committed AR events succeeds; bit-flip of those events fails closed.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- Substrate: real local POSIX temporary Evidence roots
- Forbidden claims: this proves one scenario and one transport branch — not the matrix, not
  all transport states, not power-loss or hardware guarantees

## Required automated tests

- Published AR `attempt_id` and `capture_id` on disk from frozen vector inputs
- Attempt-before-transport, proven structurally rather than by call-order assertion
- Body placement: `request.body` in the Attempt bundle, `response.body` in the Capture
  bundle
- `admitted_results` response body bytes and digest match the published vector
- Capture CLI happy path, printing both identities
- Journal absent for this path
- Verify-on-read success and tamper failure on the AR events

## Forbidden claims

- Full ten-scenario matrix complete
- All three transport states complete
- PostgreSQL, API, scrub product complete
- Off-host recovery or multi-process writer safety

## One implementation commit must prove

The first durable vertical Evidence path for admitted_results / response_complete,
including CLI — without needing later tickets for that claim to be true.

## Later tickets

Later tickets are **not** required to make this ticket's acceptance criteria truthful.

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
