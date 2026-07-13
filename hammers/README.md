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
9. `hammer` is reserved for high-consequence hostile-path proof. Ordinary correctness checks use ordinary labels.
10. Every future result should state proof class, execution surface, and proof strength; fixture/in-memory passes must not be restated as database, transaction, API/MCP, or production enforcement proof.

---

## Reading Order

1. `README.md` — this folder index
2. `hammer-matrix-v0-2.md` — current DB-1 database-phase hammer and proof-class mapping candidate
3. `acceptance-gate-policy-v0-2.md` — current DB-1 database milestone gate-policy candidate
4. `per-hammer-result-register-v0-1.md` — current DB-1 immutable proof-record contract candidate
5. `hammer-matrix-v0-1.md` — preserved M8 historical planning baseline
6. `acceptance-gate-policy-v0-1.md` — preserved M8 historical gate-policy baseline
7. `../planning-inbox/m8-hammer-planning-review.md` — historical M8 review and closure-readiness note

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `README.md` | index | Explains hammer folder scope, rules, and reading order | Updated for DB-1 policy candidates |
| `hammer-matrix-v0-2.md` | accepted policy | Carries H1-H22 into DB-2 through DB-10 with accepted proof classes and real-substrate gates | Accepted by the DB-1 closure decision; does not claim execution |
| `acceptance-gate-policy-v0-2.md` | accepted policy | Defines database-phase closure gates, required proof classes, blocked outcomes, and authority controls | Accepted by the DB-1 closure decision |
| `per-hammer-result-register-v0-1.md` | accepted contract | Defines immutable per-execution proof metadata and validation rules | Repository proof metadata only; not Observatory evidence |
| `hammer-matrix-v0-1.md` | historical draft | First M8 hostile-path hammer matrix and milestone-gate mapping | Preserved as the v0.1 planning baseline |
| `acceptance-gate-policy-v0-1.md` | historical draft | M8 acceptance levels, milestone defaults, and first-slice filter | Preserved as the v0.1 planning baseline |
| `../planning-inbox/m8-hammer-planning-review.md` | historical planning review | Reviews M8 readiness and closure posture without claiming hammer execution | Advisory note; not authority |

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
Last reviewed: 2026-07-13
Reviewer: ChatGPT / Observatory Steward
Result: Hammer matrix v0.2, acceptance-gate policy v0.2, and per-hammer result-register contract v0.1 accepted at DB-1 closure; v0.1 preserved as historical baseline
Open issues: No database hammer has executed; DB-2 consumes policy as logical design constraints only
```
