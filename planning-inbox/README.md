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

1. `m13-probe-implementation-preparation-review.md` — current M13 implementation-preparation disposition, credits timing, and next owner gate
2. `m13-dataforseo-probe-implementation-task-proposal.md` — exact bounded no-network implementation task proposal
3. `m13-dataforseo-probe-hostile-path-test-plan.md` — forty-two hostile-path cases required before execution readiness
4. `m13-dataforseo-probe-preflight-record-template.md` — exact paid-request preflight evidence template
5. `m13-dataforseo-probe-post-pull-and-purge-template.md` — one-request review, field-summary, and raw-purge evidence template
6. `m13-dataforseo-official-verification-2026-07-11.md` — fresh official endpoint/field/minimum/terms verification; exact price may be checked after funding but before submission
7. `m13-controlled-probe-approval-readiness-review.md` — M13 owner-ruling and execution-readiness review; provider machine remains off
8. `m13-dataforseo-probe-cli-requirements.md` — bounded one-shot CLI requirements only; no implementation authority
9. `m13-dataforseo-probe-plan-review.md` — review of what is ready, unresolved, and required in a later owner decision
10. `m13-dataforseo-admission-and-probe-plan.md` — current M13 DataForSEO admission/probe planning draft; does not authorize credits or calls
11. `m12-first-slice-closure-readiness-review.md` — M12 closure-readiness review for the bounded C2 first evidence slice
12. `m12-local-test-evidence-2026-07-10.md` — M12 owner-local unittest execution evidence note
13. `m11-foundation-readiness-review.md` — M11 closure-readiness review for the implementation foundation spec
14. `m11-implementation-foundation-spec.md` — M11 implementation-foundation specification for the accepted C2 first slice
15. `m10-schema-plan-review.md` — M10 review and closure-readiness note for the C2 logical schema plan
16. `m10-logical-schema-plan-c2.md` — M10 logical schema planning draft for the accepted C2 first slice
17. `m9-first-slice-definition-proposal.md` — M9 proposed first-slice definition accepted by owner decision
18. `m9-first-slice-candidate-comparison.md` — M9 first-slice candidate comparison and recommendation
19. `m8-hammer-planning-review.md` — M8 closure-readiness and M9 entry review
20. `owner-ruling-tracker.md` — all open owner-ruling candidates, grouped by blocking milestone
21. `m7-audit-response-2026-07-07.md` — audit-finding routing and status
22. `observatory-working-notes.md`
23. `repo-first-research-triage.md`

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
| `m13-dataforseo-probe-plan-review.md` | planning review | Reviews what is ready, unresolved, and required in a later owner approval decision | Advisory only; endpoint/query/location/language/device remain proposals |
| `m13-dataforseo-probe-cli-requirements.md` | planning specification | Defines a bounded one-shot CLI safety contract, preflight, duplicate, cost, raw, audit, purge, and hammer requirements | Requirements only; no CLI implementation or provider call authority |
| `m13-dataforseo-official-verification-2026-07-11.md` | planning verification note | Verifies current official endpoint, request fields, minimum payment, terms, duplicate warning, and provider-side retention | Exact request price remains blocked pending official calculator/account proof; no credits or execution authority |
| `m13-controlled-probe-approval-readiness-review.md` | planning review | Reviews the complete M13 planning package for owner-ruling readiness and defines post-ruling sequence | Ready for owner review; not execution-ready and not M13 closure |
| `m13-dataforseo-probe-implementation-task-proposal.md` | proposed implementation task | Defines exact provider-specific no-network implementation scope, constants, commands, credential boundary, evidence lifecycle, and acceptance outputs | Planning only; no source implementation or provider-call authority |
| `m13-dataforseo-probe-hostile-path-test-plan.md` | planning test plan | Defines forty-two fixture/mock hostile paths covering authority, spend, duplicates, concurrency, secrets, raw integrity, scope creep, and purge | No test may call DataForSEO or use real credentials |
| `m13-dataforseo-probe-preflight-record-template.md` | template | Defines exact decision, pricing, recipe-hash, duplicate, credential, retention, and owner-confirmation evidence before submission | A completed template is evidence, not a substitute for accepted authority |
| `m13-dataforseo-probe-post-pull-and-purge-template.md` | template | Defines one-request result review, response classification, cost proof, shape summary, boundary review, and raw purge proof | Does not authorize a second request, persistence, or M13 closure |
| `m13-probe-implementation-preparation-review.md` | planning review | Reviews implementation-preparation completeness, credits timing, remaining authority gates, and recommended next batch | Credits not needed until no-network implementation and hostile-path proof pass |
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
