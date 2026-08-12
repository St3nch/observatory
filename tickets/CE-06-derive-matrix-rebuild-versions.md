# CE-06 — Derive completion: matrix, rebuild, multi-version, damaged refuse

**Status:** ready-for-agent
**Parent spec:** docs/specs/capture-event-v2.md
**Kind:** tracer bullet
**Blocked by:** CE-05 — Derive admitted_results into real PostgreSQL
**Approved by:** Project Steward
**Start commit:**

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

- [ ] For every verified Attempt across all ten scenarios, derive produces an Attempt-stage `authorized_unresolved` Outcome with `capture_id` null, and the corresponding verified Capture produces the scenario-authorized Capture-stage Outcome.
- [ ] Observations are produced only for admitted cases and have the normative count for each scenario.
- [ ] After derive into a populated DB, an empty PostgreSQL instance re-derived from the same verified Evidence is logically equivalent per the definition above.
- [ ] A new derivation version appends its Outcomes/Observations without rewriting or deleting prior derivation-version rows.
- [ ] A Capture or cited body that fails verify-on-read produces no Capture-stage Outcome or Observations from that damaged Capture, while an independently verified parent Attempt still produces its Attempt-stage `authorized_unresolved` Outcome; material lacking `COMMITTED` visibility is not used as Evidence.
- [ ] CE-05 admitted_results behavior remains true under the expanded matrix.

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

- End commit:
- Acceptance evidence:
- Unproven limits:
- Review findings remaining:

## Closure

<!-- Project Steward only -->

- Closed at commit:
- Evidence accepted: yes/no
