# Decisions

Status: authority index
Authority: decision-folder index; individual decision files define their own authority
Purpose: preserve owner rulings, roadmap choices, scope changes, and doctrine changes in a durable format

---

## Purpose

`decisions/` exists so owner rulings and accepted project choices do not remain buried in chat history, working notes, or audit reports.

This folder is for explicit decisions, not casual suggestions.

---

## What Belongs Here

- owner rulings
- roadmap scope decisions
- doctrine-change decisions
- folder-structure decisions
- provider-admission decisions when that milestone arrives
- milestone closure decisions if a decision record is useful

---

## What Does Not Belong Here

- raw brainstorming
- unaccepted suggestions
- customer private data
- credentials or secrets
- raw provider payloads
- schema migrations
- implementation code
- strategy/recommendation records

---

## Reading Order

1. `decision-record-template.md` — format for future decision records
2. decision files in chronological order once they exist

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `decision-record-template.md` | template | Reusable decision record shape | Use for future owner rulings and accepted choices |
| `2026-07-07-m2-folder-subset.md` | accepted decision | Records the M2 folder subset ruling | Create `decisions/`, `archive/`, `research/`; defer `contracts/`, `hammers` |
| `2026-07-07-audits-folder.md` | accepted decision | Records the owner ruling earning `audits/` as a governed folder | Audit reports are planning input, never authority |
| `2026-07-10-m7-closure.md` | accepted decision | Records M7 closure and M8 activation | M7 contract drafts are complete; M8 hammer planning is active |
| `2026-07-10-m8-closure.md` | accepted decision | Records M8 closure and M9 activation | Hammer matrix and gate policy are complete; M9 first-slice definition is active |

---

## Related Roadmap Milestones

- M2 — creates this folder and the decision record template
- M4 — may use decisions for boundary/doctrine changes
- M5+ — may use decisions for research gate acceptance and provider admission later

---

## Notes for LLMs

Do not invent decisions.

Do not infer owner approval from a discussion, suggestion, audit note, or planning draft.

If a decision is missing, say it is missing. If a decision is proposed, mark it proposed until the owner accepts it.

Decision records can change project authority only when they explicitly say so and align with `ROADMAP_RULES.md`.

---

## Last Review Notes

```text
Last reviewed: 2026-07-10
Reviewer: ChatGPT / Observatory Steward
Result: M8 closure decision added and indexed; roadmap state moved from M8 to M9
Open issues: none
```
