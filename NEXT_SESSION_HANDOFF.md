# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff
Purpose: preserve current state after M4 closure and M5 activation
Last updated: 2026-07-07

---

## Current State

The Observatory is in research gate planning.

Closed milestones:

- M0 - LLM-first repo navigation and roadmap preservation
- M0.1 - Knowledgebase-to-repo reconciliation and candidate decision pass
- M1 - Roadmap Content Draft and Milestone Sequencing
- M2 - Folder Structure and Folder README Indexes
- M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
- M4 - Boundary Reconciliation and Doctrine Hardening

Active milestone:

```text
M5 - Research Gate Plan
```

M1 created the detailed roadmap sequence through Observatory v1, M2 created the approved folders/indexes, M3 preserved the approved planning-inbox source docs, and M4 hardened boundary law. The repo is still not ready for schema, provider, API, MCP, dashboard, research execution, or customer-data work.

The next milestone after M5 is:

```text
M6 - Research Gate Execution
```

---

## Active Read Path

Fresh sessions must read:

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

For planning notes, read `planning-inbox/README.md` first.

---

## Tool Discipline

When using `ob-dev`:

- Do not retry the exact same failed tool call more than once.
- Do not repeat a mutation call when SHA or diff evidence shows no meaningful change.
- If a mutation returns no diff, stop mutating and inspect with read, status, or diff tools.
- If a safety block occurs, do not hammer the same call. Try one safe read/status/diff check, then report the blocker.
- For edits, use this sequence: read -> one mutation -> diff -> diff_check -> stage exact paths -> commit.

Future `ob-dev` hardening should make no-op mutation calls harder to spam by returning `changed: false` when before/after SHA is identical and by rejecting `find == replace` unless explicitly allowed.

---

## Boundaries to Preserve

- Observatory stores observations, not conclusions.
- Strategy is compute-on-read by the connected LLM, not stored in Observatory.
- Customer records are out.
- Customer first-party data is out.
- Customer overlays are read-time only unless a future explicit owner ruling changes the law.
- Provider disagreement is preserved as first-class evidence.
- Proprietary provider scores are observations of provider model output, not facts about the web.
- Rights and retention fail closed.
- LLMs and agents get no direct SQL access or credentials.
- Future access is through typed API / MCP tools only.
- Hammer tests are a hard gate.
- VEDA Brain and other killed ancestor concepts stay killed.
- Internal first-party telemetry requires explicit internal-scope handling before any storage.

---

## Roadmap State

`ROADMAP.md` now sequences:

- M0 / M0.1 closure
- M1 closed roadmap sequencing
- M2 closed folder structure and folder README indexes
- M3 closed knowledge doc preservation
- M4 closed boundary reconciliation and doctrine hardening
- M5 active research gate planning
- M6 planned research gate execution
- M7 contracts
- M8 hammer matrix
- M9 first evidence slice definition
- M10 schema planning only
- M11-M12 implementation foundation and first slice build after gates
- M13 provider admission and controlled pull plan
- M14 typed read API / MCP contract and prototype
- M15 SearchClarity proof workflow
- M16 Provider Cross-Check proof
- M17 owned telemetry overlay proof
- M18 recurring watch panel planning
- M19 hardening / backup / recovery / operations
- M20 Observatory v1 acceptance

---

## Immediate Next Steps

Proceed with active M5:

```text
M5 - Research Gate Plan
```

M5 should define the research gates, required sources, output docs, completion rules, and M6 execution order.

Do not start research execution, provider pulls, schema, migrations, API/MCP implementation, dashboard work, customer-data handling, or strategy/recommendation storage.

---

## Open Questions

Open questions to carry forward:

- What exact research gates should M5 define before M6 execution?
- Which research gate should run first in M6?
- Which research outputs need current web/source checks versus repo-only synthesis?
- Should Provider Cross-Check get its own standalone planning doc during M5, or wait for M7?
- How should the DataForSEO rights / retention / cost gate be scoped so no paid pull happens prematurely?

---

## Do Not Start Yet

Do not start:

- schema design
- migrations
- DataForSEO pulls
- Ahrefs/Semrush work
- provider admission
- capture runner implementation
- API implementation
- MCP implementation
- dashboard/operator console work
- customer data handling
- strategy/recommendation storage
- automated recurring capture

The project now has rails. Stay on them. No schema goblin jazz.
