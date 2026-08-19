# AUTH-01 — Post-PF-15 authority alignment

**Status:** done  
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

Completed as a Steward-only authority reconciliation.

- `AGENTS.md` now lists the three repository verification commands and every current
  executable module discovered through the implemented `__main__` seams. The command list
  expressly grants no provider, credential, spend, Evidence, or deferred-work authority.
- `VISION.md` now forbids direct automation or scraping of consumer LLM/AI-search
  interfaces, while preserving the ability to activate documented provider services or
  official APIs under all existing gates. A provider product named “scraper” is not
  confused with Observatory operating its own consumer-interface scraper.
- `docs/specs/capture-event-v2.md` now points to the accepted shared, Keyword Overview, and
  Google Organic rebuildable relations and the three provider read resources. `/v1` is the
  sole canonical resource namespace; `/api/v1/docs` and `/api/v1/openapi.json` are
  documentation locations only.
- The spec now records the existing Organic recipe behavior for AIO arrays: top-level
  arrays are required and null fails closed, while missing and null element-level
  `references` both emit no element-locus occurrence and make no absence claim. Raw
  Evidence retains the distinction; changing the rule requires a new recipe identity.

Verification:

- clean `main` at start commit
  `e828b82bc35a21f2c2f8a9e2271cb72b7b618f75`;
- current implementation inspected directly for entrypoint seams, route mounts, table
  names, and AIO parsing behavior;
- changed paths limited to `AGENTS.md`, `VISION.md`,
  `docs/specs/capture-event-v2.md`, and this ticket;
- no `src/` or `tests/` change, so pytest/ruff/mypy were not rerun;
- no provider, DNS, credential, paid-gate, Evidence, PostgreSQL, or network activity;
- no next acquisition surface selected or implemented;
- no push.
