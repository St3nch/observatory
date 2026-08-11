# Observatory Agent Instructions

## Authority

Read in this order:

1. VISION.md
2. decisions/decisions.md
3. decisions/deferred.md
4. Relevant ticket
5. Relevant ADR, when one exists

CONTEXT.md is a glossary only. Files under docs-temp/ are ignored working notes and are
never project authority.

## Roles

- The human product owner owns product purpose, priorities, major trade-offs, final
  decisions, and release approval.
- The Project Steward owns sequencing, architectural coherence, authority maintenance,
  ticket quality, integration, acceptance evidence, and drift control.
- Coding and review agents implement or inspect bounded assignments under the current
  authority and ticket. They do not replace the Project Steward or silently redefine
  project direction.
- Agent findings are inputs. A finding changes the project only after the Project Steward
  reconciles it with existing authority and records any resulting decision.
- No agent may broaden its assignment merely because it discovers adjacent work; report
  the finding and keep the current ticket bounded.

## Hard boundaries

- Observatory is a standalone observation-data service.
- Every consumer uses the versioned API; never create direct database or file access for a
  project, LLM, agent, or script.
- Keep strategy, recommendations, conclusions, scoring, reporting narratives, customer
  overlays, and campaign workflow outside Observatory.
- Preserve exact evidence and immutable attempt/outcome history; make query projections
  rebuildable and versioned.
- Never collapse missing, refused, failed, partial, malformed, or inapplicable states.
- Never make provider calls from ordinary automated tests.
- Never claim fixture or mock success proves real PostgreSQL, crash, concurrency, or
  recovery behavior.
- Do not weaken durability to improve development convenience.

## Work method

- Work from one ticket with observable acceptance criteria.
- Ordinary tests are the default.
- Add a hammer candidate only when the invariant, consequence, and required proof substrate
  can be named.
- Create an ADR only when the choice is hard to reverse, surprising without context, and
  the result of a real trade-off.
- Do not generate planning, audit, closure, or status document trees.
- When a decision changes, update the existing authority instead of adding a competing file.
- Do not implement deferred work before its recorded trigger fires.

## Commands

These are the intended repository commands once the Python project scaffold exists:

    uv run pytest -q
    uv run ruff check .
    uv run mypy
    uv run python -m observatory.migrate
    uv run python -m observatory.derive

## Completion

A ticket is complete only when:

- its acceptance behavior is observable;
- relevant ordinary tests pass on the correct substrate;
- data and API boundary rules remain intact;
- the exact unproven limits are stated;
- authority docs changed only if the ticket made a real decision.
