# Planning Inbox — The Observatory

Status: working note index
Authority: none
Purpose: index unpromoted planning material and prevent working notes from being mistaken for project law

---

## Purpose

`planning-inbox/` is a holding area for working material.

It exists so useful ideas, triage notes, Claude/GPT review material, and draft research directions do not get lost in chat history.

This folder is not authority.

Nothing in this folder authorizes implementation, provider spending, schema creation, MCP/API work, dashboard work, customer data handling, or strategy/recommendation storage.

---

## What Belongs Here

- working notes
- repo-first triage
- unpromoted planning drafts
- model-specific historical context
- future research prompts
- review notes
- dangerous ideas clearly labeled as dangerous

---

## What Does Not Belong Here

- credentials or secrets
- customer private data
- customer first-party analytics
- raw provider payloads
- accepted doctrine hidden as notes
- schema migrations
- implementation code
- final consumer deliverables

---

## Reading Order

For current planning context, read:

1. `m13-dataforseo-admission-and-probe-plan.md` — current M13 DataForSEO admission/probe planning draft; does not authorize credits or calls
2. `m12-first-slice-closure-readiness-review.md` — M12 closure-readiness review for the bounded C2 first evidence slice
3. `m12-local-test-evidence-2026-07-10.md` — M12 owner-local unittest execution evidence note
4. `m11-foundation-readiness-review.md` — M11 closure-readiness review for the implementation foundation spec
5. `m11-implementation-foundation-spec.md` — M11 implementation-foundation specification for the accepted C2 first slice
6. `m10-schema-plan-review.md` — M10 review and closure-readiness note for the C2 logical schema plan
7. `m10-logical-schema-plan-c2.md` — M10 logical schema planning draft for the accepted C2 first slice
8. `m9-first-slice-definition-proposal.md` — M9 proposed first-slice definition accepted by owner decision
9. `m9-first-slice-candidate-comparison.md` — M9 first-slice candidate comparison and recommendation
10. `m8-hammer-planning-review.md` — M8 closure-readiness and M9 entry review
11. `owner-ruling-tracker.md` — all open owner-ruling candidates, grouped by blocking milestone
12. `m7-audit-response-2026-07-07.md` — audit-finding routing and status
13. `observatory-working-notes.md`
14. `repo-first-research-triage.md`

Root authority files take priority over this folder.

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `observatory-working-notes.md` | working note | Preserves current planning ideas, doctrine phrases, DataForSEO inheritance notes, Strategy/IMI boundary notes, capture runner ideas, and research topics | Not authority; useful planning substrate |
| `repo-first-research-triage.md` | working note / research triage | Identifies which Observatory research questions are already partly answered by local repos before deep research | Not final roadmap; use to focus later research |
| `knowledgebase-reconciliation.md` | planning | Reconciles project knowledge docs against the live repo and classifies Claude/GPT candidate ideas into now, next, research, later, defer, forbidden, or killed buckets | M0.1 artifact; not implementation approval |
| `audit-response-2026-07-07.md` | planning / audit response backlog | Tracks the M1-era Claude repo audit findings, assigns each to a milestone/file, and prevents partial audit cherry-picking | Responds to the M1-era audit only; the 2026-07-07 M7/full-repo audits are tracked in `m7-audit-response-2026-07-07.md` |
| `m7-audit-response-2026-07-07.md` | planning / audit response backlog | Routes all findings from the two 2026-07-07 audits in `audits/` (ISS-01..22, SEQ-01) | Created in M7 audit-fix pass |
| `owner-ruling-tracker.md` | planning / ruling tracker | Consolidates every open owner-ruling candidate (groups A–G) with source refs and blocking milestones | Rulings bind only via `decisions/` records |
| `m8-hammer-planning-review.md` | planning review | Reviews M8 hammer planning readiness and closure posture | Advisory note; not authority |
| `m9-first-slice-candidate-comparison.md` | planning / candidate comparison | Compares M9 first-slice candidates against M8 gates and recommends the controlled public manual observation package | Advisory note; not authority |
| `m9-first-slice-definition-proposal.md` | planning / proposed first-slice definition | Defines the recommended controlled public manual observation package slice for owner review and later M10 planning | Advisory proposal; owner accepted C2 in `decisions/2026-07-10-m9-first-slice-closure.md` |
| `m10-logical-schema-plan-c2.md` | planning / logical schema plan | Drafts logical schema responsibilities for the accepted C2 Controlled Public Manual Observation Package | M10 planning only; not DDL, migration, implementation, or authority |
| `m10-schema-plan-review.md` | planning review | Reviews the C2 logical schema plan against M10 gates, hammers, anti-patterns, and closure-readiness defaults | Advisory note; not authority |
| `m11-implementation-foundation-spec.md` | planning / implementation-foundation specification | Specifies bounded M11 foundation expectations for the accepted C2 first slice | M11 planning only; not migrations, provider work, API/MCP, dashboard, customer data, or broad implementation |
| `m11-foundation-readiness-review.md` | planning review | Reviews M11 foundation readiness, closure defaults, and M12 handoff boundaries | Advisory note; not authority |
| `m12-local-test-evidence-2026-07-10.md` | execution evidence note | Records owner-local M12 unittest run output and reported push verification | Evidence note only; not M12 closure and not connector-executed proof |
| `m12-first-slice-closure-readiness-review.md` | planning review | Reviews M12 C2 first-slice implementation, hammer coverage, and closure caveats | Advisory note; not authority |
| `m13-dataforseo-admission-and-probe-plan.md` | planning draft | Drafts DataForSEO admission/probe controls, credit gate, endpoint ceiling, raw payload handling, and CLI requirements | M13 planning only; does not authorize credits, calls, provider admission, schema, or DB creation |
| `strategy-layer-dangerous-design.md` | planning artifact | Preserves dangerous Strategy Layer / IMI design candidates for later classification and reconciliation | M3 preservation artifact; authority none; do not activate dangerous ideas |
| `deep-research-danger-agenda.md` | research agenda | Preserves future deep-research questions and danger-map topics for later research gate planning | M3 preservation artifact; authority none; not research execution approval |
| `steward-context-dump.md` | advisory context | Preserves steward/context material for future reconciliation without promoting it into doctrine | M3 preservation artifact; authority none; advisory only |
| `m4-boundary-reconciliation.md` | planning / reconciliation note | Classifies M4 boundary deltas before any root boundary-law edit | Authority none; identifies safe clarifications and owner-ruling candidates |

---

## Related Roadmap Milestones

- M0 — creates this index and makes the repo LLM-first
- M0.1 — creates knowledgebase reconciliation
- M1 — creates the detailed roadmap and audit-response backlog
- M2 — may create additional folder README indexes if the roadmap earns new folders

---

## Notes for LLMs

Do not treat planning-inbox files as accepted doctrine unless a root authority file or owner ruling says so.

Use this folder to understand context and unresolved ideas.

Go8 refers to the bounded repo/MCP tooling used to inspect and edit the live local repository. It is tool context, not project doctrine.

When citing this folder in a plan, preserve labels like `working note`, `historical`, and `not authority`.

Do not implement directly from planning-inbox material. That is how the raccoon gets the keyboard.

---

## Last Review Notes

```text
Last reviewed: 2026-07-07
Reviewer: Claude (Observatory Project Steward role), M7 audit-fix pass
Result: Added m7-audit-response and owner-ruling-tracker; CLAUDE_START_HERE moved to archive/ (tombstone remains pending manual owner deletion); reading order updated
Open issues: Owner deletes planning-inbox/CLAUDE_START_HERE.md tombstone manually
```
