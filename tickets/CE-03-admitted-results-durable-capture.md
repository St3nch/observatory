# CE-03 — First durable Capture Event: admitted_results

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-02 — Canonical JCS, closed schemas, and content-ID vectors
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: create and open a format-2 Evidence Store,
durably commit an Attempt before fixture transport, run in-process **admitted_results**
transport only, durably commit the Capture, and expose the deterministic fixture Capture
CLI—such that published AR identity digests match on disk when frozen published vector
inputs are used, and transport cannot begin before Attempt commit visibility.

This ticket covers only the **`response_complete`** transport branch as exercised by
**`scenario=admitted_results`**. It does not complete all three transport states.

## Authority

- `docs/specs/capture-event-v2.md` — §FORMAT.json (exact bytes and digest)
- `docs/specs/capture-event-v2.md` — §Paths and bundles
- `docs/specs/capture-event-v2.md` — §Commit visibility (COMMITTED-last; no-overwrite; fsync file and parent directories; Evidence only after verified manifest + bodies + COMMITTED)
- `docs/specs/capture-event-v2.md` — §Normative construction order
- `docs/specs/capture-event-v2.md` — §Closed schemas (Attempt, Capture, request, body)
- `docs/specs/capture-event-v2.md` — §Conformance vectors Set AR
- `docs/specs/capture-event-v2.md` — fixture-panel-v1 request constants; admitted_results path of §Fixture response-construction algorithm
- `docs/specs/capture-event-v2.md` — fixture journal skip only when full in-process result retained before Capture construction
- `decisions/decisions.md` — D8 (Attempt before transport; FS Evidence; verify-on-read; no ordinary hardlinks; COMMITTED)
- `docs/adr/0001-capture-event-evidence-boundary.md` — Evidence Store boundary
- `VISION.md` — §What v1 must prove items 1–2 (narrowed to admitted_results for this ticket)

## Scope

- FORMAT-2 create/open; fail-closed validation of exact FORMAT bytes/digest
- Path and sharding rules for objects, attempts, captures
- Body pool install; body digest and byte-count verification; no ordinary hardlinks to the pool (independent copy or COW reflink only)
- Exact committed filesystem durability operations and ordering: no-overwrite install; required file fsync and parent-directory fsync; `COMMITTED` last with content `<event_id>\n`
- Attempt commit before transport; Capture commit for admitted_results / response_complete
- Verify-on-read of those events
- Deterministic fixture Capture CLI for this path; prints `attempt_id` and `capture_id`; does not derive
- Fixture journal skip only under the authorized full in-process retention rule—no journal product for future providers

## Out of scope

- The other nine fixture scenarios
- `response_partial` and `no_response` branches and RP/NR vectors
- Derive, PostgreSQL, HTTP API
- status/scrub CLIs
- Multi-process locking (F7), off-host backup (F6), paid providers (F3)
- Broader power-loss, hardware, or crash-recovery claims beyond the committed protocol under test

## Acceptance criteria

- [ ] A format-2 root can be created and opened; FORMAT exact JCS bytes (no trailing newline) and SHA-256 `67fb338d3237a22a29f50110c705e552cd9af29f830c1bfffa9ee1cafa876c7e` are enforced.
- [ ] Missing, malformed, noncanonical, unsupported, or conflicting FORMAT fails closed on open.
- [ ] Using frozen published AR vector inputs, on-disk Attempt and Capture identities match published `attempt_id` and `capture_id`; paths follow format-2 layout.
- [ ] Request/response bodies are content-addressed; digests and sizes verify; ordinary hardlinks into the object pool are not used.
- [ ] Durable install uses no-overwrite behavior; required fsync operations and directory fsync occur per committed protocol; `COMMITTED` is last; uncommitted directories are not admitted as Evidence.
- [ ] Automated proof: fixture transport for this path does not begin until Attempt commit is visible and verified.
- [ ] Capture CLI completes admitted_results Attempt→Capture and prints `attempt_id` and `capture_id`; it does not write PostgreSQL or derive.
- [ ] Verify-on-read of the committed AR events succeeds; bit-flip of those events fails closed.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: real local POSIX temporary Evidence roots; ordinary tests for pure logic already in CE-02
- Forbidden claims: tests prove the committed durability **protocol** under the supported profile—not arbitrary power-loss, multi-filesystem, or hardware guarantees

## Required automated tests

- FORMAT open / fail-closed
- Path layout for AR events
- Body digest/size verification
- No-overwrite / occupied-path conflict
- COMMITTED-last visibility; uncommitted not Evidence
- Attempt-before-transport ordering
- Published AR identity digests on disk (frozen published vector inputs)
- Verify-on-read success and negative tamper on AR events
- Capture CLI admitted_results path

## Forbidden claims

- Full ten-scenario matrix complete
- All three transport states complete
- PostgreSQL, API, scrub product complete
- Off-host recovery or multi-process writer safety

## One implementation commit must prove

The first durable vertical Evidence path for admitted_results / response_complete, including CLI and committed durability protocol—without needing later tickets for that claim to be true.

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
