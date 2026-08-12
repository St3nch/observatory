# CE-05 — Derive admitted_results into real PostgreSQL

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-04 — Full fixture-panel-v1 matrix and all transport branches
**Approved by:** Project Steward
**Start commit:**

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

- [ ] Starting from verified admitted_results Evidence and empty or freshly migrated PostgreSQL, derive produces the Attempt-stage Outcome (`authorized_unresolved`, `capture_id` null for that stage row) and the Capture-stage Outcome (`observation_admitted`) under a registered derivation version.
- [ ] Exactly `depth` Observations are written with correct natural identities, provider/fixture axes, labels/scores, and provenance citing verified `attempt_id` and `capture_id`.
- [ ] Derive uses verify-on-read; unverifiable Evidence for this path does not produce normal Observation rows.
- [ ] Re-running the same derivation version does not duplicate or mutate existing Outcome/Observation rows for this slice (idempotency).
- [ ] The Capture-stage Outcome and its Observations for this Capture are written atomically (no partial Observation set without the corresponding Capture-stage Outcome for a successful completion of the derive unit).
- [ ] `python -m observatory.derive` performs this derivation.

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

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
