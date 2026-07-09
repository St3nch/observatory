# Decision 2026-07-07 — M2 Folder Subset

Status: accepted
Date: 2026-07-07
Owner ruling: Create only the M2 folders needed now or soon: `decisions/`, `archive/`, and `research/`. Defer `contracts/` until M7 and `hammers/` until M8.
Related milestone: M2 — Folder Structure and Folder README Indexes
Related files:

- `ROADMAP.md`
- `ACTIVE_CONTEXT.md`
- `NEXT_SESSION_HANDOFF.md`
- `planning-inbox/audit-response-2026-07-07.md`
- `REPO_MAP.md`

---

## Decision

```text
Create now:
- decisions/
- archive/
- research/

Defer:
- contracts/ until M7
- hammers/ until M8
```

---

## Context

Claude's 2026-07-07 repo audit found that M2's proposed folder set was directionally correct but slightly ahead of the project's own "earned folders only" doctrine.

The audit recommended creating `decisions/` and `archive/` now, optionally creating `research/`, and deferring `contracts/` and `hammers/` until the milestones that need them.

The owner approved proceeding with this audit-informed direction.

---

## Options Considered

| Option | Summary | Result | Reason |
|---|---|---|---|
| A | Create all proposed folders: `research/`, `contracts/`, `decisions/`, `hammers/`, `archive/` | Rejected for now | Too much ceremony in advance; `contracts/` and `hammers/` are not active until M7/M8 |
| B | Create only `decisions/` and `archive/` | Considered | Safe, but `research/` is the next major workstream and benefits from early README indexing |
| C | Create `decisions/`, `archive/`, and `research/`; defer `contracts/` and `hammers/` | Accepted | Balances readiness with earned-folder discipline |

---

## Scope

This decision applies to:

- M2 folder creation
- current repo map update
- folder README creation
- future required-reading folder hygiene

This decision does not apply to:

- schema design
- implementation
- provider calls
- MCP/API work
- dashboard work
- customer data handling
- strategy/recommendation storage

---

## Authority Impact

```text
scope change
```

This narrows M2 folder creation relative to the earlier candidate set in `ROADMAP.md` and preserves the deferred status of `contracts/` and `hammers/`.

---

## Follow-up Work

| Follow-up | Target milestone | Target file(s) | Status |
|---|---|---|---|
| Create folder READMEs for accepted M2 folders | M2 | `decisions/README.md`, `archive/README.md`, `research/README.md` | done |
| Update repo map to match actual folders | M2 | `REPO_MAP.md` | done in M2 |
| Add classified Claude docs | M3 | `planning-inbox/` | done in M3 |
| Create contracts folder when earned | M7 | `contracts/README.md` | done 2026-07-07 (M7 audit-fix pass; template included) |
| Create hammers folder when earned | M8 | `hammers/README.md` | deferred |

---

## Anti-Drift Notes

This decision does not authorize implementation.

This decision does not authorize schema work.

This decision does not authorize provider calls or provider purchases.

This decision does not authorize contracts or hammers work early.

This decision does not promote planning-inbox material into authority.

---

## Supersession

```text
Superseded by:
Date:
Reason:
```
