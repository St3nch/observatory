# Observatory

Observatory is a standalone, long-lived API service for acquiring, preserving, and serving
clean historical SEO/GEO observation data to many projects.

It stores observations and provenance. It does not perform SEO/GEO strategy.

## Current status

The clean rebuild is at the authority-and-scaffold stage. Product boundaries are settled;
the storage schema, API contract, and first provider adapter have not yet been implemented.

## Read first

1. VISION.md
2. decisions/decisions.md
3. decisions/deferred.md
4. CONTEXT.md
5. AGENTS.md

## Repository shape

    VISION.md                  Product north star and boundaries
    decisions/decisions.md     Settled decisions and rejected alternatives
    decisions/deferred.md      Deferred work with observable triggers
    CONTEXT.md                 Glossary only
    AGENTS.md                  Rules for coding agents
    docs/adr/                  Created only when the ADR bar is met

Directories are created only when they have content. Planning belongs in tickets, not a
planning-document tree.

## Build sequence

1. Lock the minimum storage and API decisions needed for one vertical slice.
2. Scaffold the Python service and PostgreSQL development environment.
3. Implement one fixture-only attempt → outcome → observation → API-read path.
4. Add cursor pagination, provenance disclosure, and deterministic re-derivation.
5. Prove backup, clean restore, verification, and equivalent API results.
6. Add a real provider only after the non-network path is sound.

## Intended commands

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.derive

The migration and derivation commands remain placeholders until their modules are implemented.
