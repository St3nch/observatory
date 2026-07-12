# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff
Purpose: preserve current state after M10 closure and M11 activation
Last updated: 2026-07-10

---

## Current State

The Observatory is in implementation foundation.

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
- M8 - Hammer Matrix and Acceptance Gates
- M9 - First Evidence Slice Definition
- M10 - Schema Planning Only

Active milestone:

```text
M11 - Implementation Foundation
```

M1 created the roadmap, M2 created approved folders/indexes, M3 preserved planning source docs, M4 hardened boundary law, M5 planned research gates, M6 executed all 13 research gates, M7 drafted/indexed all 13 planned non-schema contracts, M8 drafted/indexed the hammer matrix and acceptance-gate policy, M9 accepted C2 as the first evidence slice, and M10 accepted logical schema planning for C2. The repo is still not ready for migrations, provider pulls, provider purchases, API, MCP, dashboard, capture runners, or customer-data work.

The next milestone after M11 is:

```text
M12 - First Evidence Slice Build
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
12. `hammers/README.md`
13. `hammers/hammer-matrix-v0-1.md`
14. `hammers/acceptance-gate-policy-v0-1.md`
15. `decisions/2026-07-10-m9-first-slice-closure.md`
16. `planning-inbox/m10-logical-schema-plan-c2.md`
17. `planning-inbox/m10-schema-plan-review.md`
18. `decisions/2026-07-10-m10-schema-planning-closure.md`
19. `planning-inbox/owner-ruling-tracker.md`

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
- M8 closed hammer matrix and acceptance-gate planning
- M9 closed first evidence slice definition
- M10 closed schema planning only
- M11 active implementation foundation
- M12 first slice build after gates
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

Proceed with active M11:

```text
M11 - Implementation Foundation
```

Status 2026-07-10: M10 is closed by `decisions/2026-07-10-m10-schema-planning-closure.md`. The accepted logical planning target is the Controlled Public Manual Observation Package. M11 is active for implementation foundation only.

Immediate next moves:

```text
1. Specify M11 foundation deliverables concretely.
2. Define repo/skeleton expectations for the accepted C2 first slice only.
3. Define test-harness and initial hammer-test scaffold expectations.
4. Define fixture/sample design expectations.
5. Define migration-folder expectations without running migrations.
```

Do not run migrations, make provider purchases, perform paid pulls, build API/MCP tools, create dashboard work, handle customer data, broaden implementation beyond the accepted first slice, or store strategy/recommendations.

---

## Open Questions

Open questions to carry forward:

- OR-A1: persisted Disagreement Ledger vs compute-on-read only.
- OR-A2: RG6 sentiment/tone provider-attributed-only vs mechanically derived sentiment.
- OR-A3: `ai_visibility_sample_summary` read-time output only vs storable under materialization test.
- OR-A4: citation handles global vs artifact-local; report-safe references separate or derived.
- OR-B1 through OR-B3 remain open with M8 fail-closed defaults.
- M11 foundation work must stay constrained to the accepted C2 first slice and must not broaden into provider, customer, dashboard, API/MCP, or strategy storage implementation.

---

## Do Not Start Yet

Do not start:

- running migrations
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
- M12 first-slice build before M11 foundation expectations are clear

The project now has rails. Stay on them. No schema goblin jazz.
