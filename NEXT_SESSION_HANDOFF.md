# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff
Purpose: preserve current state after M7 closure and M8 activation
Last updated: 2026-07-10

---

## Current State

The Observatory is in hammer matrix and acceptance-gate planning.

Closed milestones:

- M0 - LLM-first repo navigation and roadmap preservation
- M0.1 - Knowledgebase-to-repo reconciliation and candidate decision pass
- M1 - Roadmap Content Draft and Milestone Sequencing
- M2 - Folder Structure and Folder README Indexes
- M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
- M4 - Boundary Reconciliation and Doctrine Hardening
- M5 - Research Gate Plan
- M6 - Research Gate Execution
- M7 - Core Contract Planning

Active milestone:

```text
M8 - Hammer Matrix and Acceptance Gates
```

M1 created the detailed roadmap sequence through Observatory v1, M2 created the approved folders/indexes, M3 preserved the approved planning-inbox source docs, M4 hardened boundary law, M5 planned the research gates, M6 executed all 13 research gates plus the deep-research backlog, and M7 drafted/indexed all 13 planned non-schema contracts. The repo is still not ready for schema, provider pulls, provider purchases, API, MCP, dashboard, capture runners, or customer-data work.

The next milestone after M8 is:

```text
M9 - First Evidence Slice Definition
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
11. `contracts/README.md`
12. `planning-inbox/m7-contract-draft-set-review.md`
13. `planning-inbox/owner-ruling-tracker.md`
14. `research/rg13-hammer-matrix-inputs.md`

For planning notes, read `planning-inbox/README.md` first.

---

## Tool Discipline

When using `ob-dev`:

- Do not retry the exact same failed tool call more than once.
- Do not repeat a mutation call when SHA or diff evidence shows no meaningful change.
- If a mutation returns no diff, stop mutating and inspect with read, status, or diff tools.
- If a safety block occurs, do not hammer the same call. Try one safe read/status/diff check, then report the blocker.
- For edits, use this sequence: read -> one mutation -> diff -> diff_check -> stage exact paths -> commit.

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
- M5 closed research gate planning
- M6 closed research gate execution
- M7 closed core contract planning
- M8 active hammer matrix and acceptance-gate planning
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

Proceed with active M8:

```text
M8 - Hammer Matrix and Acceptance Gates
```

Status 2026-07-10: M7 is closed by `decisions/2026-07-10-m7-closure.md`. All thirteen planned M7 contracts are drafted and indexed in `contracts/README.md`. The M7 draft-set review lives at `planning-inbox/m7-contract-draft-set-review.md`. M8 is active for hammer matrix and acceptance-gate planning only.

Immediate next moves:

```text
1. Create/earn hammers/ with README/index if M8 work proceeds.
2. Draft the M8 hammer matrix from the M7 contract set and RG13.
3. Map each hammer to contract source, failure mode, owner-ruling dependency, and milestone gate.
4. Keep unresolved owner rulings fail-closed.
5. Do not start M9 first-slice selection until M8 hammer expectations are clear enough.
```

Use `contracts/README.md` as the index to the completed M7 contract draft set and `research/rg13-hammer-matrix-inputs.md` as the primary M8 research input. Do not make provider purchases, paid pulls, schema, migrations, API/MCP implementation, dashboard work, capture runner work, customer-data handling, or strategy/recommendation storage.

---

## Open Questions

Open questions to carry forward:

- OR-A1: persisted Disagreement Ledger vs compute-on-read only.
- OR-A2: RG6 sentiment/tone provider-attributed-only vs mechanically derived sentiment.
- OR-A3: `ai_visibility_sample_summary` read-time output only vs storable under materialization test.
- OR-A4: citation handles global vs artifact-local; report-safe references separate or derived.
- OR-B1 through OR-B3: hammer acceptance criteria, hard gates by milestone, and freshness/report-use blockers.
- Which M8 hammers are hard gates for M9, M10, M11, M12, M13, M14, M15, M16, M17, and M18.

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
- M9 first-slice selection before M8 gates exist

The project now has rails. Stay on them. No schema goblin jazz.
