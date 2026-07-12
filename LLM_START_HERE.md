# LLM Start Here — The Observatory

Status: authority
Authority: root onboarding
Purpose: first read path for every LLM or human steward before recommendations, edits, or implementation

---

## Purpose

This is the model-neutral first file for The Observatory.

Every new LLM session must read this file before making recommendations or editing the repo. Do not rely on chat history, stale handoffs, or prior connector claims when the live repo disagrees. Read the repo, then answer. Wild concept, apparently.

---

## What The Observatory Is

The Observatory is a standalone evidence-only SEO / GEO / SERP / visibility observation project.

Core rule:

```text
The Observatory stores what was observed.
The connected LLM interprets what it means at read time.
Accepted conclusions promote out to the owning consumer.
```

The Observatory is the telescope. The connected LLM is the astronomer.

The database must never become the astronomer.

The project exists to preserve historical, provenance-complete observations such as:

- SERP results
- keyword demand observations
- ranking observations
- AI answer-surface mentions and citations
- public page or listing snapshots
- provider responses
- capture metadata
- rights, retention, freshness, and source labels

---

## What The Observatory Is Not

The Observatory is not:

- a generic SEO tool
- a dashboard project
- a strategy engine
- a recommendation store
- a customer database
- a SearchClarity customer database
- a Neon Ronin subsystem
- a Kaizen replacement
- a random Postgres experiment
- a place for scores-as-truth
- a place for customer first-party analytics
- a direct SQL playground for LLMs or agents

Strategy is compute-on-read by the connected LLM. Strategy is not stored in Observatory tables.

---

## Required Read Order

Read these files in order before making recommendations or edits:

1. `README.md`
2. `LLM_START_HERE.md`
3. `ACTIVE_CONTEXT.md`
4. `ROADMAP.md`
5. `ROADMAP_RULES.md`
6. `REPO_MAP.md`
7. `00-project-overview.md`
8. `01-harvest-register.md`
9. `02-boundaries.md`
10. `NEXT_SESSION_HANDOFF.md`

If a referenced file is missing, stop and report the missing file. Do not improvise around dangling authority.

---

## Current Hard Boundaries

Unless the owner explicitly changes project law:

- Store observations, not conclusions.
- Store provider testimony, not fake truth.
- Preserve provider disagreement.
- No recommendation store.
- No strategy table.
- No score-as-truth table.
- No customer database.
- No customer first-party data in Observatory.
- Customer first-party data may only be supplied as read-time overlays unless a future explicit owner ruling changes this.
- Owned internal first-party telemetry requires explicit internal-scope boundary handling before any storage.
- LLMs and agents receive no direct SQL access and no direct credentials.
- Future LLM access must go through typed API / MCP read tools.
- Rights and retention fail closed.
- Hammer tests are a hard gate for implementation.
- Killed ancestor concepts stay killed.
- No VEDA Brain resurrection under a new name.

---

## Current Boundary Rule

`ACTIVE_CONTEXT.md` is the single authority for the current phase. Do not hard-code a milestone from this file.

For the active M14 planning boundary, do not start:

- production API or MCP implementation/deployment
- direct SQL or credential access for LLMs or agents
- Postgres creation, physical schema, or migrations
- live provider ingestion or any additional paid provider request
- recurring capture
- dashboard or operator console work
- customer-data handling or customer first-party analytics storage
- customer-facing reports
- strategy or recommendation storage

If another root file disagrees with `ACTIVE_CONTEXT.md`, stop and reconcile the authority drift before proceeding.

---

## Roadmap Required-Reading Rule

Every roadmap milestone must list required reading before implementation.

Required reading may name exact files or folders.

If a milestone lists a folder as required reading, that folder must contain a `README.md` summarizing what each important document in that folder is for.

No implementation work begins until required reading has been completed and reported.

---

## Access Direction

Future LLM-facing access is typed API / MCP only:

```text
LLM
  -> MCP tools
  -> Observatory API
  -> validation / authorization / rights / provenance layer
  -> PostgreSQL
```

MCP tools are not database clients.

The API owns database access.

The LLM receives evidence packs, comparison outputs, freshness warnings, blind-spot warnings, and stable evidence IDs — not raw mystery rows.

---

## Final Rule

```text
The Observatory makes the astronomer dangerous.
It never becomes the astronomer.
```
