# Decision 2026-07-07 — Audits Folder Earned

Status: accepted
Date: 2026-07-07
Owner ruling: The owner created `audits/` to preserve audit reports as durable project evidence, acknowledged it was "rogue" (un-governed), and directed the steward to fix its governance during the M7 audit-fix pass.
Related milestone: M7 — Core Contract Planning
Related files:

- `audits/README.md`
- `REPO_MAP.md`
- `planning-inbox/m7-audit-response-2026-07-07.md`
- `decisions/2026-07-07-m2-folder-subset.md`

---

## Decision

```text
audits/ is an earned, governed folder as of 2026-07-07.
It preserves audit reports as planning input / advisory context only.
Audit reports are never authority, doctrine, or implementation approval.
Findings must be routed through an audit-response tracker in planning-inbox/.
```

---

## Context

The M2 folder-subset decision created only `decisions/`, `archive/`, and `research/`, deferring `contracts/` (M7) and `hammers/` (M8). `audits/` was not in that set because the need had not yet materialized.

By M7, two substantial audit reports existed and the earlier M1-era audit had already been lost to external upload history — demonstrating real friction. The owner created the folder and placed the M6/M7-readiness audit in it. The full repo audit of 2026-07-07 flagged the folder as un-indexed and un-README'd (ISS-01/ISS-02); the owner then ruled to govern it rather than remove it.

---

## Options Considered

| Option | Summary | Result | Reason |
|---|---|---|---|
| A | Keep audit reports in planning-inbox/ | Rejected | Audits are a distinct artifact class with a distinct trust posture; mixing them with working notes blurs both |
| B | Remove audits/ and rely on chat/export history | Rejected | Already failed once: the M1-era audit source is unrecoverable in-repo |
| C | Govern audits/ with README, REPO_MAP row, and workflow convention | Accepted | Matches earned-folder doctrine; friction demonstrated the need |

---

## Scope

This decision applies to:

- audits/ folder existence and governance
- audit report preservation and trust labeling
- the audit → audit-response-tracker routing convention

This decision does not apply to:

- promoting any audit finding into doctrine
- schema, implementation, provider, API/MCP, dashboard, or customer-data work
- contracts/ or hammers/ folder gates (unchanged: M7 / M8)

---

## Authority Impact

```text
scope change
```

Adds one folder to the earned set defined by the M2 folder-subset decision. Owner approval given directly in the 2026-07-07 M7 audit-fix session.

---

## Follow-up Work

| Follow-up | Target milestone | Target file(s) | Status |
|---|---|---|---|
| Create audits/README.md | M7 | `audits/README.md` | done |
| Add audits/ to repo map | M7 | `REPO_MAP.md` | done |
| Route both 2026-07-07 audit findings | M7 | `planning-inbox/m7-audit-response-2026-07-07.md` | done |
| Recover M1-era audit export if it exists | opportunistic | `audits/` | open |

---

## Anti-Drift Notes

- This does not make audit reports authority.
- This does not authorize implementation, provider work, or schema.
- This does not permit auditors to self-promote findings without the tracker/owner path.

---

## Supersession

```text
Superseded by:
Date:
Reason:
```
