# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff
Purpose: preserve current state after M2 closure and M3 activation
Last updated: 2026-07-07

---

## Current State

The Observatory is in knowledge-doc preservation / pre-boundary-reconciliation planning.

Closed milestones:

- M0 - LLM-first repo navigation and roadmap preservation
- M0.1 - Knowledgebase-to-repo reconciliation and candidate decision pass
- M1 - Roadmap Content Draft and Milestone Sequencing
- M2 - Folder Structure and Folder README Indexes

Active milestone:

```text
M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
```

M1 created the detailed roadmap sequence through Observatory v1, and M2 created the approved folders/indexes. The repo is still not ready for schema, provider, API, MCP, dashboard, or customer-data work.

The next milestone after M3 is:

```text
M4 - Boundary Reconciliation and Doctrine Hardening
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
- M3 active knowledge doc preservation
- M4 boundary reconciliation
- M5/M6 research gate planning and execution
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

Proceed with active M3:

```text
M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
```

M3 should add these classified project knowledge docs to `planning-inbox/` with labels, without promoting them into authority:

- `strategy-layer-dangerous-design.md`
- `deep-research-danger-agenda.md`
- `steward-context-dump.md`

Then update `planning-inbox/README.md`.

---

## Open Questions

Open questions to carry forward:

- Should M3 immediately add `strategy-layer-dangerous-design.md`, `deep-research-danger-agenda.md`, and `steward-context-dump.md` to `planning-inbox/`?
- Should M4 boundary reconciliation happen before or after adding the Claude docs?
- Which M5 research gate should execute first once research begins?
- Should Provider Cross-Check get its own standalone planning doc before M5, or wait for M5/M7?

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
