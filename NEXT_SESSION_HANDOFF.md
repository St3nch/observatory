# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve current state after M14 closure and M15 planning activation
Last updated: 2026-07-12

---

## Current State

The Observatory is in M15 SearchClarity proof-workflow planning.

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
- M11 - Implementation Foundation
- M12 - First Evidence Slice Build
- M13 - Provider Admission and Controlled Pull Plan
- M14 - Typed Read API / MCP Contract and Prototype

Active milestone:

```text
M15 - SearchClarity Proof Workflow
```

M14 closed on an accepted typed-read contract plus one local fixture-backed in-memory prototype. The owner ran the full suite: 141 tests passed. M15 is active for planning only. No customer records, customer-private storage, report generation, production SearchClarity integration, overlays, Postgres, schema, migrations, provider execution, recurring capture, production API/MCP, or strategy/recommendation storage is authorized.

Current milestone-transition authority:

```text
decisions/2026-07-12-m14-closure-and-m15-activation.md
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
19. `planning-inbox/m11-implementation-foundation-spec.md`
20. `planning-inbox/m11-foundation-readiness-review.md`
21. `decisions/2026-07-10-m11-foundation-closure.md`
22. `planning-inbox/m12-local-test-evidence-2026-07-10.md`
23. `planning-inbox/m12-first-slice-closure-readiness-review.md`
24. `decisions/2026-07-10-m12-first-slice-closure.md`
25. `research/rg1-dataforseo-rights-retention-cost.md`
26. `research/rg10-capturepackage-v0-1-inputs.md`
27. `research/rg11-raw-archive-provider-drift.md`
28. `planning-inbox/owner-ruling-tracker.md`

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
- M11 closed implementation foundation
- M12 closed first evidence slice build
- M13 active provider admission and controlled pull planning
- M14 typed read API / MCP contract and prototype
- M15 SearchClarity proof workflow
- M16 Provider Cross-Check proof
- M17 owned telemetry overlay proof
- M18 recurring watch panel planning
- M19 hardening / backup / recovery / operations
- M20 Observatory v1 acceptance

---

## Immediate Next Steps

Proceed with active M13:

```text
M13 - Provider Admission and Controlled Pull Plan
```

Status 2026-07-10: M12 is closed by `decisions/2026-07-10-m12-first-slice-closure.md`. The accepted local C2 first evidence slice is proven for the bounded fixture implementation. M13 is active for provider admission and controlled pull planning only.

Immediate next moves:

```text
1. Draft the provider admission plan.
2. Confirm rights, retention, and cost gates from existing research/contracts.
3. Define a controlled pull recipe as a proposal only.
4. Define cost ceiling and stop conditions.
5. Define raw payload handling, no-customer-data, no-recurring-capture, and no-API/MCP/dashboard/report posture.
```

Do not make provider purchases, perform paid pulls, execute provider tasks, build API/MCP tools, create dashboard work, handle customer data, scrape marketplaces, create recurring capture, or store strategy/recommendations.

---

## Open Questions

Open questions to carry forward:

- OR-A1: persisted Disagreement Ledger vs compute-on-read only.
- OR-A2: RG6 sentiment/tone provider-attributed-only vs mechanically derived sentiment.
- OR-A3: `ai_visibility_sample_summary` read-time output only vs storable under materialization test.
- OR-A4: citation handles global vs artifact-local; report-safe references separate or derived.
- OR-B1 through OR-B3 remain open with M8 fail-closed defaults.
- M13 provider admission planning must stay document-only and must not broaden into provider execution, paid pulls, customer data, marketplace scraping, dashboard, API/MCP, recurring capture, or strategy storage implementation.

---

## Do Not Start Yet

Do not start:

- provider calls
- DataForSEO pulls
- Ahrefs/Semrush work
- provider admission execution
- marketplace scraping
- browser-extension capture
- API/MCP exposure
- dashboard/operator console work
- customer data handling
- customer-facing reports
- strategy/recommendation storage
- recurring capture
- broad implementation beyond C2
- M13 provider admission before M12 proves the first slice

The project now has rails. Stay on them. No schema goblin jazz.
