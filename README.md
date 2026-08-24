# Observatory

Observatory is a standalone, long-lived API service for acquiring, preserving, and serving
clean historical SEO/GEO observation data to many projects.

It preserves Evidence on a filesystem Evidence Store (Attempt and Capture events plus
content-addressed bodies), derives Outcomes and Observations into rebuildable PostgreSQL,
and serves them through an API. It does not perform SEO/GEO strategy. Provider, Derivation,
schema, and API work is nevertheless reviewed for whether a future connected strategy LLM
can receive sufficient typed facts, relationships, provenance, completeness, and limitations
without direct storage access or misleading inference.

## Current status

Observatory now implements the capture-event Evidence boundary, format-2 filesystem Evidence
Store, verify-on-read and scrub tooling, rebuildable PostgreSQL derivation, provider
Derivation Recipes, and integrity-checked read APIs.

The implemented provider slices are:

- DataForSEO Google Keyword Overview: bounded capture, strict parser, typed derivation,
  Recipe selection, and history API;
- DataForSEO Google Organic: bounded capture, strict parser, typed derivation, Recipe
  selection, and history API;
- DataForSEO AI Optimization Search Mentions: bounded capture, strict parser, and typed
  PostgreSQL derivation, Recipe selection, and history API;
- DataForSEO AI Optimization Target Metrics: bounded capture, strict parser, and typed
  PostgreSQL derivation. Recipe selection and read/history API remain the next separate
  boundary.

The fixture path remains supported for conformance and regression proofs. Provider transport
is adapter-specific and gated; there is no generic paid runner or recurring acquisition
orchestrator.

## Read first

Authority hierarchy for agents and humans:

1. `VISION.md` — product doctrine, lifecycle, survival, v1 proof
2. `VOCABULARY.md` — canonical terms
3. `decisions/decisions.md` — settled decisions (including D8–D13)
4. `decisions/deferred.md` — deferred work with triggers
5. `AGENTS.md` — agent hard boundaries and commands
6. `docs/dataforseo-surface-roadmap.md` — provider direction, strategy-consumer review,
   and current retrofit sequence
7. `docs/adr/0001-capture-event-evidence-boundary.md` — why the Evidence boundary is fixed
8. `docs/specs/capture-event-v2.md` — normative capture/evidence contract

When a ticket exists, read it after the decision registers and before coding.

## Repository shape

    VISION.md
    VOCABULARY.md
    decisions/decisions.md
    decisions/deferred.md
    AGENTS.md
    docs/adr/                  ADRs when the ADR bar is met
    docs/specs/                Normative implementation contracts
    src/observatory/           Service implementation
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

## Implemented foundation

- Immutable Attempt and Capture Evidence with SHA-256 identities and content-addressed body
  objects.
- Closed event-v1 and event-v2 validation with mixed-store compatibility.
- Commit-before-send transport gates, bounded single-exchange HTTP, credential
  non-disclosure, and exact complete/partial/no-response testimony.
- Evidence inspection, status, scrub, tamper detection, and process-death hammer coverage.
- PostgreSQL schema migration and deterministic re-derivation from verified Evidence.
- Recipe-addressed provider Observations with typed detail, provenance, occurrence
  testimony, and complete-set checks.
- Read-only FastAPI service with health, Attempt, Keyword Overview history, and Google
  Organic history surfaces that fail closed on Evidence/PostgreSQL disagreement.

PostgreSQL remains rebuildable state, not authoritative Evidence. Multi-process writer
safety, routine acquisition orchestration, production API authentication/non-loopback
exposure, and Target Metrics read/history remain outside the implemented boundary.

## Commands

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.capture
    uv run python -m observatory.derive
    uv run python -m observatory.evidence status
    uv run python -m observatory.evidence scrub
    uv run python -m observatory.keyword_overview_derive
    uv run python -m observatory.google_organic_derive
    uv run python -m observatory.search_mentions_derive
    uv run python -m observatory.target_metrics_derive
    uv run python -m observatory.provider_recipe_selection
    uv run python -m observatory.serve

Use each module's `--help` for its required operator arguments. Listing a provider command
does not authorize credentials, transport, spend, or Evidence creation.
