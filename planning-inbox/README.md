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

1. `observatory-working-notes.md`
2. `repo-first-research-triage.md`
3. `CLAUDE_START_HERE.md` only if model-specific historical context is needed

Root authority files take priority over this folder.

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `observatory-working-notes.md` | working note | Preserves current planning ideas, doctrine phrases, DataForSEO inheritance notes, Strategy/IMI boundary notes, capture runner ideas, and research topics | Not authority; useful planning substrate |
| `repo-first-research-triage.md` | working note / research triage | Identifies which Observatory research questions are already partly answered by local repos before deep research | Not final roadmap; use to focus later research |
| `knowledgebase-reconciliation.md` | planning | Reconciles project knowledge docs against the live repo and classifies Claude/GPT candidate ideas into now, next, research, later, defer, forbidden, or killed buckets | M0.1 artifact; not implementation approval |
| `audit-response-2026-07-07.md` | planning / audit response backlog | Tracks Claude's repo audit findings, assigns each to a milestone/file, and prevents partial audit cherry-picking | M1 closure/M2 planning input; not implementation approval |
| `CLAUDE_START_HERE.md` | historical / model-specific context | Prior Claude-specific onboarding note | Model-specific; do not treat as active root authority now that `LLM_START_HERE.md` exists |
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
Reviewer: GPT-5.5 Thinking via Go8
Result: Created as part of M0 repair
Open issues: Decide later whether CLAUDE_START_HERE.md should move to archive once model-neutral onboarding is stable
```
