# CE-02 — Canonical JCS, closed schemas, and content-ID vectors

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** necessary prefactor
**Blocked by:** None — can start immediately
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: pure, in-memory construction and validation of
identity-bearing Capture Event documents so that published content IDs and digests match
authority and invalid closed-schema inputs fail closed—without writing Evidence, running
transport, PostgreSQL, or HTTP.

## Authority

- `docs/specs/capture-event-v2.md` — §Scalar constraints (global)
- `docs/specs/capture-event-v2.md` — §Canonicalization and verify-on-read (JCS, hash algorithm, re-JCS equality)
- `docs/specs/capture-event-v2.md` — §Closed schemas (recursive unknown-key rule; `body_ref` through Capture/Attempt/request-fingerprint)
- `docs/specs/capture-event-v2.md` — §Conformance vectors (Sets AR, RP, NR; empty-body digest)
- `decisions/decisions.md` — D8 (full SHA-256 identities; JCS manifests)
- `VOCABULARY.md` — Attempt, Capture, request_fingerprint

## Scope

- RFC 8785 / JCS UTF-8 serialization (no trailing newline) for identity-bearing documents
- Recursive closed-schema validation (unknown properties forbidden at every nested object)
- Content digests and IDs: body SHA-256, `request_fingerprint`, `attempt_id`, `capture_id`
- Null-versus-omit rules as specified (including optional non-null `prior_attempt_id`)
- All published AR / RP / NR vector documents and digests as automated golden tests

## Out of scope

- Evidence Store filesystem, FORMAT.json on disk, paths, durability, COMMITTED
- Fixture transport, capture/derive/status/scrub CLIs
- PostgreSQL, HTTP API
- Provider network calls
- Deferred work (F3, F6–F10)

## Acceptance criteria

- [ ] Every published JCS document in §Conformance vectors (request bodies, fingerprint preimages, Attempt manifests, Capture manifests, response bodies as applicable) hashes to its published lowercase SHA-256 when encoded as UTF-8 with no trailing newline.
- [ ] For published AR / RP / NR inputs, computed `request_fingerprint`, `attempt_id`, and `capture_id` match the published identity digests.
- [ ] Documents with unknown properties at any depth are rejected.
- [ ] `attempt_nonce` must be exactly `[0-9a-f]{64}`; invalid length/charset rejected.
- [ ] Timestamps not matching the frozen syntax are rejected.
- [ ] Closed enums and exact constants (`schema`, `version`, `provider`, `adapter_contract`, fixture request constants) are enforced.
- [ ] `prior_attempt_id`, when absent, is omitted (not null); null is rejected when the field is present incorrectly.
- [ ] Re-JCS of a parsed valid document equals the original stored/canonical bytes for vector cases.
- [ ] No filesystem Evidence write is required for these tests to pass.

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: ordinary unit tests
- Forbidden claims: no durability, PostgreSQL, or live-provider proof; mocks of FS/PG not required and must not be claimed as substrate proof

## Required automated tests

- Schema-closure / unknown-property rejection
- JCS canonicalization
- Byte-count and SHA-256 vector tests (all published vectors)
- Request-fingerprint tests
- Attempt ID tests
- Capture ID tests
- Negative and boundary-input tests (nonce, timestamps, enums, omit/null)

## Forbidden claims

- Store durability, crash recovery, multi-process safety
- API or derive behavior
- Anything beyond pure identity/schema correctness

## One implementation commit must prove

Identity construction and closed-schema enforcement match committed vectors and rules without any later ticket.

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
