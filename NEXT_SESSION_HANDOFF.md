# Next Session Handoff - The Observatory

Status: authority
Authority: fresh-session handoff pointer; `ACTIVE_CONTEXT.md` owns current phase truth
Purpose: preserve the accepted Observatory v1 bounded proof-system state
Last updated: 2026-07-12

---

## Current State

The Observatory is accepted at the bounded v1 proof-system ceiling.

Closed milestones:

```text
M0, M0.1, and M1 through M20
```

Active milestone:

```text
none
```

The owner accepted Observatory v1 through `decisions/2026-07-12-observatory-v1-acceptance.md`. The accepted system is local, evidence-only, bounded, and not production-ready or feature-complete. The known-limit and deferred-capability register remains binding.

Current acceptance authority:

```text
decisions/2026-07-12-observatory-v1-acceptance.md
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

There is no active milestone.

Preserve the accepted-v1 state. Do not begin production or post-v1 implementation unless the owner explicitly approves a new roadmap.

Allowed next actions are limited to reviewing accepted evidence, correcting factual documentation defects, preserving proof artifacts, or drafting a new roadmap only when explicitly requested.

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
