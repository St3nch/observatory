# Observatory

Observatory is a standalone, long-lived API service for acquiring, preserving, and serving
clean historical SEO/GEO observation data to many projects.

It preserves Evidence on a filesystem Evidence Store (Attempt and Capture events plus
content-addressed bodies), derives Outcomes and Observations into rebuildable PostgreSQL,
and serves them through an API. It does not perform SEO/GEO strategy.

## Current status

Authority documents describe the capture-event Evidence boundary (D8). The Python service
scaffold exposes process liveness only. Evidence Store, derive, observation schema, and
provider adapters are not yet implemented. First implementation remains fixture-only
(`fixture-panel-v1`).

## Read first

Authority hierarchy for agents and humans:

1. `VISION.md` — product doctrine, lifecycle, survival, v1 proof
2. `VOCABULARY.md` — canonical terms
3. `decisions/decisions.md` — settled decisions (see D8; D5 superseded for storage boundary)
4. `decisions/deferred.md` — deferred work with triggers
5. `AGENTS.md` — agent hard boundaries and commands
6. `docs/adr/0001-capture-event-evidence-boundary.md` — why the Evidence boundary is fixed
7. `docs/specs/capture-event-v2.md` — normative capture/evidence contract

When a ticket exists, read it after the decision registers and before coding.

## Repository shape

    VISION.md
    VOCABULARY.md
    decisions/decisions.md
    decisions/deferred.md
    AGENTS.md
    docs/adr/                  ADRs when the ADR bar is met
    docs/specs/                Normative implementation contracts
    src/observatory/           Service package (scaffold)
    tests/

Directories are created only when they have content. Planning belongs in tickets, not a
planning-document tree. Files under `docs-temp/` are never project authority.

## Canonical lifecycle

```text
prepared request
  → committed Attempt
  → transport
  → committed Capture when possible
  → derived Outcome / classification
  → Derivation / admission
  → Observation
  → API
```

PostgreSQL holds rebuildable Outcomes and Observations. It is not authoritative Evidence.

## Build sequence

1. Capture-event authority in-repo (this documentation stage).
2. Implement Evidence Store primitives, Attempt/Capture commit, verify-on-read, and
   fixture-only transport seam (no real provider network).
3. Implement derive from committed Evidence into rebuildable PostgreSQL Outcomes and
   Observations citing `capture_id` and `attempt_id`.
4. Read API with Outcome and Observation visibility; integrity fail-closed on verify.
5. Scrub and status; state unproven limits (off-host, multi-process, paid providers).
6. Add a real provider only after the fixture path is sound and Steward authorizes it.

## Intended commands

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.capture
    uv run python -m observatory.derive
    uv run python -m observatory.evidence status
    uv run python -m observatory.evidence scrub

Migration, capture, derivation, and evidence commands remain placeholders until
implemented.
