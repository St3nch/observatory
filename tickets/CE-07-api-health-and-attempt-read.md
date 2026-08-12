# CE-07 — Read API: health and attempt envelope

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-06 — Derive completion: matrix, rebuild, multi-version, damaged refuse
**Approved by:** Project Steward
**Start commit:**

## What to build

End-to-end behaviour this ticket makes work: authorized read HTTP surface for the fixture
vertical slice—`GET /v1/health` process liveness, `GET /v1/attempts/{attempt_id}` returning
Outcomes and Observations with provenance, loopback and no-auth operation, and HTTP 409
when verify-on-read fails with a response body containing the stable signal
`evidence_integrity_failure`; the same verified Evidence also rebuilds logically
equivalent API-visible Attempt data in a separate empty PostgreSQL instance.

## Authority

- `docs/specs/capture-event-v2.md` — §Rebuildable PostgreSQL / entrypoints / API (`GET /v1/health`, `GET /v1/attempts/{attempt_id}`, loopback, no auth, 409 `evidence_integrity_failure` on failed verify-on-read)
- `VISION.md` — §What v1 must prove items 4–5
- `decisions/decisions.md` — D2 (consumers use versioned API for data access)
- `decisions/deferred.md` — F8 (production auth/bind deferred); F9 (HTTP write API deferred)

## Scope

- `GET /v1/health`
- `GET /v1/attempts/{attempt_id}`
- Loopback / no-auth posture for fixture/dev
- Verify-on-read on read of cited Evidence; HTTP 409 with body containing `evidence_integrity_failure`
- API-visible logical rebuild equivalence for the same verified Evidence and authorized derivation-version identity

## Out of scope

- Freezing a health JSON schema, media type, or required field list
- Any claim about preserving, removing, replacing, or supporting `/healthz`
- `/api/v1` dual mounting or compatibility routing
- Degraded dependency-health behavior
- Optional derivation-version query parameter (not fixed in committed API text)
- HTTP capture/write API
- Collection/list endpoints beyond the attempt resource
- status/scrub CLIs (CE-08)

## Acceptance criteria

- [ ] `GET /v1/health` returns **HTTP 200** when the process is live and expresses process-liveness semantics only (no dependency-health claims).
- [ ] `GET /v1/attempts/{attempt_id}` returns Outcomes and Observations for derived fixture Evidence, distinguishing fixture-v1 classifications and including provenance citing verified `attempt_id` and `capture_id` as applicable.
- [ ] When verify-on-read fails for Evidence that would back the response, the handler returns **HTTP 409** and the response body **contains** the stable signal `evidence_integrity_failure`; it does not return a normal success payload of stale derived rows for that damaged aggregate.
- [ ] Deriving the same verified Evidence with the same authorized derivation-version identity into an originally populated PostgreSQL instance and a separate empty PostgreSQL instance yields logically equivalent domain content from `GET /v1/attempts/{attempt_id}`: Outcomes, Observations, classifications, provenance, identities, values, and counts match after normalizing implementation-dependent ordering. Byte-identical HTTP responses are not required.
- [ ] Fixture/dev operation is consistent with loopback and no-authentication requirements (no production auth model claimed).

## Verification

- Commands: `uv run pytest -q`; `uv run ruff check .`; `uv run mypy` as applicable
- Substrate: application tests; real Evidence FS + **real PostgreSQL** for integrity failure cases that depend on derived rows citing Evidence
- Forbidden claims: production auth complete; problem+json or other invented public error schema beyond the stable signal string

## Required automated tests

- `GET /v1/health` → 200, process-liveness only
- Attempt envelope for multiple classifications (Outcomes + Observations as applicable)
- Provenance fields on admitted Observations
- Integrity: plant damaged Evidence after derive → 409 and body contains `evidence_integrity_failure`
- Real-Evidence, real-PostgreSQL API integration: populated and empty-DB rebuilds yield logically equivalent Attempt resources after normalization of non-normative ordering
- No auth requirement for these routes in fixture/dev tests

## Forbidden claims

- Health payload field contract beyond process-liveness
- `/healthz` disposition
- Scrub/status product complete
- HTTP write API

## One implementation commit must prove

Authorized read API vertical, API-visible logical rebuild equivalence, and integrity 409 signal—without needing CE-08 for those claims.

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
