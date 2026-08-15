# PF-01 — HTTP event v2 and mixed-store verification

**Status:** ready
**Parent spec:** docs/specs/capture-event-v2.md, “Provider HTTP event version 2”
**Authority:** D8, D9
**Kind:** provider-foundation implementation
**Blocked by:** none
**Approved by:** Project Steward
**Start commit:** implementer records the exact assigned clean HEAD

## Why this ticket exists

The accepted fixture event-v1 schemas are deliberately closed and cannot admit HTTP
testimony. D9 authorizes a second event version on the existing Evidence Store format and
bundle layouts, before any real provider transport exists.

This ticket builds and verifies that durable schema seam. It also prevents valid provider
Evidence in a mixed store from being called corrupt, fixture-classified, or written under
the fixture derivation label.

## What to build

- Add closed construction and validation for:
  - `observatory.request-fingerprint` version 2;
  - `observatory.attempt-event` version 2;
  - `observatory.capture-event` version 2;
  - the exact
    `dataforseo-serp-google-organic-live-advanced-sandbox-v1` adapter contract.
- Dispatch all three document families by `schema` and `version` while leaving event
  version 1 exact.
- Commit and verify version-2 Attempt/Capture bundles through the existing format-2
  Evidence Store, paths, body pool, D1–D7/D4a protocol, and full D5 read.
- Make scrub verify valid candidates under either event version.
- Make fixture derivation explicitly select `fixture-panel-v1` before writing any
  derivation-version, Outcome, or Observation row. Valid provider HTTP events are skipped
  with zero rows and are not integrity failures.
- Keep existing fixture API behavior correct when the same Evidence root also contains
  valid version-2 provider Evidence.

No HTTP client, credential loading, or provider call belongs in this ticket.

## Acceptance criteria

- [ ] The published HTTP-v2 request body, fingerprint preimage, Attempt, and Capture
      reproduce the exact byte lengths and IDs in the parent spec.
- [ ] Version-1 conformance bytes and published IDs remain unchanged.
- [ ] A validator reads only `schema`/`version` to choose a branch, then re-validates the
      selected closed schema and all cross-field rules; unknown versions/contracts and
      version-confused keys fail closed.
- [ ] Attempt version 2 forbids `prior_attempt_id` and every unknown key.
- [ ] The sandbox policy structurally requires the exact sandbox host, HTTPS target, one
      task, and depth 10.
- [ ] Request-header rules reject credential-class headers and any header set/order other
      than the exact committed application set.
- [ ] Response-header validation enforces `http-headers-v1`, the closed denylist,
      lowercasing, preserved retained order/duplicates, unique sorted omission markers,
      positive counts, and no retained/omitted overlap.
- [ ] Complete, partial, and no-response Capture branches enforce status, HTTP version,
      body/completeness, timestamps, and the closed phase/code failure table exactly.
- [ ] HTTP `url`, `final_url`, redirect-chain, free-text failure, provider task/cost/result
      envelope fields, secrets, Outcome fields, and Observation fields are rejected.
- [ ] Version-2 Attempt and Capture commit to the unchanged `attempts/v1` and
      `captures/v1` layouts and pass the existing full D5 aggregate read, including parent
      Attempt and both body copies.
- [ ] A mixed store with valid v1 and v2 events scrubs cleanly; tampered committed v2
      manifest/body material fails as an integrity failure; an unknown committed event
      version is reported as failure, not ignored.
- [ ] Deriving a mixed store writes exactly the fixture rows it wrote before and no row of
      any kind for the provider adapter; the valid provider events do not increment
      integrity failures.
- [ ] Existing fixture `GET /v1/attempts/{attempt_id}` responses remain unchanged with v2
      Evidence present; a provider Attempt with no derived rows remains 404 rather than a
      fabricated unresolved envelope.
- [ ] No test or production path performs HTTP transport.
- [ ] `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy` pass.

## Required automated tests

- Independent recomputation of every published HTTP-v2 vector byte count and digest.
- Event-v1 published-ID regression.
- Unknown schema/version and cross-version key rejection.
- Adapter parameter, policy, request-header, response-header, omission, response-branch,
  and failure-enum boundary tables.
- Format-2 version-2 commit/read and manifest/body tamper.
- Mixed-store scrub.
- Real-PostgreSQL mixed-store derive skip with exact row accounting.
- Fixture API read plus provider no-row 404 from one mixed Evidence root.

Tests must use test-side literals/formulas as their oracle rather than production builders
alone.

## Scope constraints

- One implementation commit; do not amend or push.
- Implementer may change only:
  - `src/observatory/capture_event.py`
  - `src/observatory/evidence_store.py`, only if version dispatch cannot remain inside the
    document validators
  - `src/observatory/derive.py`
  - existing tests directly needed by the acceptance criteria
  - one new focused `tests/test_http_event_v2.py` if useful
  - this ticket's Status and Implementation report
- Do not change `capture.py` or add HTTP transport.
- Do not edit `AGENTS.md`, `VISION.md`, `VOCABULARY.md`, `decisions/`, `docs/`, or another
  ticket.
- Do not add a dependency.

## Out of scope

- PF-02 transport or an operator sandbox smoke
- Credentials or settings
- Paid/production host
- Standard, task_post/task_get, polling, retry linkage, or a source-Capture field
- Provider Outcome, Derivation, Observation, or API envelope
- Capability catalog, pricing catalog, spend budget, project context, or strategy
- Redirect following
- Concurrency, crash/power-loss, or off-host recovery claims

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy`
- PostgreSQL substrate: exercised real PostgreSQL 18 for mixed-store derive tests
- Review compares the exact recorded Start commit through the one implementation commit.

## Implementation report

<!-- Implementer fills; may set Status: review; never Status: done. -->

## Closure

<!-- Project Steward fills only after independent review. -->

