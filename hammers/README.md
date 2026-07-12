# Hammers

Status: hammer-folder index
Authority: folder index; individual hammer docs become binding only when marked accepted
Purpose: hold M8 hostile-path hammer matrices and acceptance-gate planning before implementation, schema, provider admission, API/MCP work, or consumer integration

---

## Purpose

`hammers/` holds M8 deliverables: hostile-path tests, acceptance gates, and milestone-gate mappings derived from the M7 contract draft set and RG13.

A hammer plan defines what Observatory must prove before later milestones may accept implementation, provider pulls, read tools, consumer workflows, or recurring capture.

A hammer plan does not implement tests, create schema, run migrations, call providers, expose APIs, create MCP tools, or handle customer data.

Folder earned during M8 after M7 closure by `decisions/2026-07-10-m7-closure.md` and the active M8 roadmap section.

---

## What Belongs Here

- hostile-path hammer matrices
- hammer acceptance-gate plans
- milestone-gate mappings
- planned test-result vocabularies
- mock/stub/real-surface acceptance notes
- links from hammers back to contracts, RG13, owner-ruling blockers, and later milestones

## What Does Not Belong Here

- test implementation code
- schema design
- migrations
- provider credentials
- provider responses or raw payloads
- customer private data
- report drafts
- strategy or recommendation content
- API/MCP implementation specs beyond hammer-level requirements

---

## Hammer Rules

1. Hammers test boundaries by trying to break them.
2. Happy-path validation is not enough.
3. A planned hammer is not a passed hammer.
4. `blocked_not_implemented` is not pass.
5. `blocked_owner_ruling_required` is not pass.
6. Any hammer touching an unresolved owner ruling must fail closed until the ruling is recorded.
7. Hammers must map to source contracts and later milestone gates.
8. No hammer document authorizes implementation, provider admission, provider spend, schema design, or customer data handling.

---

## Reading Order

1. `README.md` — this folder index
2. `hammer-matrix-v0-1.md` — first M8 hammer matrix draft
3. `acceptance-gate-policy-v0-1.md` — milestone gate policy and M9 entry filter

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `README.md` | index | Explains hammer folder scope, rules, and reading order | Created when M8 activated |
| `hammer-matrix-v0-1.md` | draft | First M8 hostile-path hammer matrix and milestone-gate mapping | Drafted from RG13 and M7 contract set |
| `acceptance-gate-policy-v0-1.md` | draft | Defines M8 acceptance levels, milestone gate defaults, owner-ruling defaults, and M9 first-slice entry filter | Drafted from hammer matrix, RG13, roadmap, and owner-ruling tracker |

---

## Related Roadmap Milestones

- M8 — drafts hammer matrix and acceptance gates
- M9 — chooses first evidence slice using hammer expectations
- M10 — consumes hammer expectations during schema planning
- M11/M12 — implementation foundation and first slice must satisfy relevant hammers
- M13 — provider admission must satisfy provider/cost/raw/capture hammers
- M14 — typed read API/MCP must satisfy read-tool/access hammers
- M15 — SearchClarity proof must satisfy consumer/report hammers
- M16 — provider cross-check proof must satisfy disagreement hammers
- M17 — overlay proof must satisfy overlay/no-storage hammers
- M18 — recurring watch panel planning must satisfy capture/cost/cadence hammers
- M19 — hardening/operations consumes audit, rollback, recovery, and retention hammers

---

## Notes for LLMs

Do not treat hammer docs as implementation tasks unless a later milestone explicitly activates implementation.

Do not soften hammers because they look harsh. They are supposed to be harsh.

If a boundary exists, the hammer matrix should try to break it.

If a hammer would require unresolved owner approval, mark it blocked/fail-closed rather than inventing permission.

---

## Last Review Notes

```text
Last reviewed: 2026-07-10
Reviewer: ChatGPT / Observatory Steward
Result: Hammers folder earned, first matrix drafted, and acceptance gate policy added for M8 planning
Open issues: Review M8 hammer matrix and gate policy; resolve or explicitly defer OR-B1 through OR-B3 before M8 closure
```
