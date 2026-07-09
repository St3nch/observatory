# Audits

Status: audit-folder index
Authority: folder index only; audit reports are planning input / advisory context, never authority
Purpose: preserve repo and milestone audit reports as durable project evidence instead of losing them to chat history

---

## Purpose

`audits/` preserves audit reports produced by stewards (LLM or human) reviewing the repo, a milestone, or a work product.

Audit reports are serious review input. They are not doctrine, not owner rulings, and not implementation approval. If any document cites an audit as authority for a capability, that citation is invalid by construction.

Folder created by owner ruling 2026-07-07 (see `decisions/2026-07-07-audits-folder.md`).

---

## What Belongs Here

- full repo audit reports
- milestone-readiness audit reports (pre-M7 contract audit, pre-M8 hammer audit, etc.)
- work-product audits (research set audits, contract audits, future schema/implementation audits)
- audit reports recovered from external sources (chat exports, uploads) when they still matter

## What Does Not Belong Here

- audit-response trackers (those live in `planning-inbox/` so routing/status stays with working material)
- accepted decisions (those live in `decisions/`)
- customer private data, credentials, raw provider payloads
- implementation code
- anything pretending audit findings are accepted doctrine

---

## Audit Workflow Convention

```text
1. Audit is performed and the report is preserved here.
2. Findings are routed through an audit-response tracker in planning-inbox/
   (apply now / assign to milestone / defer with reason / reject with reason / needs owner ruling).
3. Routed findings are revisited when their milestone activates.
4. Audits are never silently absorbed and never partially cherry-picked.
```

---

## Reading Order

Read the most recent audit first unless investigating history. Always read the matching audit-response tracker afterward — the tracker, not the audit, records what was actually accepted.

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `m7-audit-report-2026-07-07.md` | audit report / planning input | M6 research set + M7-readiness audit (Claude). Verdict: yes with caveats | Scope was M6/M7-readiness, not full repo. Findings routed via `planning-inbox/m7-audit-response-2026-07-07.md` |
| `full-repo-audit-2026-07-07.md` | audit report / planning input | Full repository consistency/authority/index audit post-M6 closure (Claude). Verdict: clean enough after small cleanup | Placed by owner. Findings ISS-01..22 routed via `planning-inbox/m7-audit-response-2026-07-07.md` |

Note on a missing ancestor: the original 2026-07-07 M1-era repo audit (`observatory-repo-audit-2026-07-07.md`, referenced as source by `planning-inbox/audit-response-2026-07-07.md`) exists only as external uploaded project knowledge and is not preserved in this repo. If its export is recovered, it belongs here.

---

## Related Roadmap Milestones

- M7 — first audits preserved here (M6 research audit, full repo audit)
- M8+ — future hammer/schema/implementation audits land here

---

## Notes for LLMs

Do not treat audit findings as accepted until the audit-response tracker or a decision record says so.

Do not re-litigate a routed finding without new evidence; check the tracker first.

Audits may be wrong. Later audits may correct earlier ones (see the NC5 correction in the full repo audit).

---

## Last Review Notes

```text
Last reviewed: 2026-07-07
Reviewer: Claude (Observatory Project Steward role)
Result: Folder governance created during M7 audit-fix pass; both 2026-07-07 audits indexed
Open issues: Recover original M1-era audit export if it still exists
```
