# AUTH-01 — Post-PF-15 authority alignment

**Status:** ready  
**Owner:** [GPT] Project Steward  
**Blocked by:** none; PF-15 closed  
**Approved by:** Project Steward  
**Start commit:** `e828b82bc35a21f2c2f8a9e2271cb72b7b618f75`

## Purpose

Reconcile the bounded authority drift identified by the milestone audit and the Product
Owner's post-PF-15 acquisition boundary before selecting another provider surface.

## In scope

- Correct the stale implemented-entrypoint statement in `AGENTS.md` and enumerate the
  current module entrypoints without documenting their full CLI option surfaces.
- Add a compact provider-schema and read-route pointer to
  `docs/specs/capture-event-v2.md` so later sessions do not have to reconstruct the
  accepted Keyword Overview and Google Organic physical/API surface from closed tickets.
- Record `/v1` as the canonical versioned resource namespace. Record
  `/api/v1/docs` and `/api/v1/openapi.json` as development documentation locations, not a
  second or compatibility-mounted resource namespace.
- Record the accepted Google Organic recipe's asymmetric AIO source-array semantics:
  top-level `references` and `items` are required arrays and null fails closed;
  element-level `references` missing or JSON null both emit no element occurrence rows and
  make no absence claim. Any change requires a new recipe identity.
- Record the Product Owner's prohibition on Observatory directly scraping consumer LLM
  interfaces. AI answer/citation testimony may be acquired only through separately
  activated documented provider services or official APIs under accepted terms, retention,
  privacy, redistribution, Evidence, and spend gates.

## Files

- `AGENTS.md`
- `VISION.md`
- `docs/specs/capture-event-v2.md`
- this ticket

## Out of scope

- `src/` or `tests/` changes;
- route remounting or compatibility aliases;
- provider research, credentials, calls, spend, or Evidence creation;
- selection or implementation of the next acquisition surface;
- reopening PF-11 through PF-15 or changing accepted recipe bytes.

## Acceptance

- Authority describes current implemented entrypoints and provider read surface without
  claiming PostgreSQL is Evidence.
- The URL-prefix statement matches current behavior and names one canonical resource
  namespace.
- The AIO null/absence statement matches the accepted parser and does not mutate its recipe.
- Direct consumer-LLM scraping is forbidden without accidentally forbidding documented
  provider services whose product name includes “scraper.”
- Diff is limited to the four named files; no tests are required for documentation-only
  reconciliation; working tree is clean after the Steward commit.

## Steward report

Pending.
