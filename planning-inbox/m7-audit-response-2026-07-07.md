# M7 Audit Response — 2026-07-07 Claude Audits

Status: planning / audit response tracker
Authority: none
Purpose: route every finding from the two 2026-07-07 Claude audits so nothing is cherry-picked or lost
Sources: `audits/m7-audit-report-2026-07-07.md` (M6/M7-readiness audit) and `audits/full-repo-audit-2026-07-07.md` (full repo audit)
Created: 2026-07-07
Disambiguation: this file responds to the two audits above. The older `planning-inbox/audit-response-2026-07-07.md` responds to the separate M1-era audit (`observatory-repo-audit-2026-07-07.md`, external upload, not in repo). Same date, different audits.

---

## Routing rule (inherited from the M1-era audit-response pattern)

Every finding gets exactly one outcome:

```text
apply now | assign to milestone | defer with reason | reject with reason | needs owner ruling
```

Findings are revisited when their assigned milestone activates.

---

## Finding backlog

Owner approved the audit-fix pass on 2026-07-07 ("fix all the issues with the two previous audits"), authorizing the cleanup class below. Contract drafting itself remains separate M7 work.

| ID | Finding (source) | Action | Status | Notes |
|---|---|---|---|---|
| ISS-01 | audits/ has no README (full audit) | apply now | done 2026-07-07 | `audits/README.md` created; audit workflow convention included |
| ISS-02 | audits/ absent from REPO_MAP (full audit) | apply now | done 2026-07-07 | Row added; contracts/ also moved from planned to current |
| ISS-03 | research/README stale reading order + review notes (both audits) | apply now | done 2026-07-07 | Reading order now points at the M6 corpus |
| ISS-04 | REPO_MAP research row stale status text (both audits) | apply now | done 2026-07-07 | |
| ISS-05 | audit-response-2026-07-07.md status column frozen ~M2 (full audit) | apply now | done 2026-07-07 | AUD-013..022 statuses refreshed with dated pass note |
| ISS-06 | CLAUDE_START_HERE.md: no in-file header, stale read order, archive move never happened (full audit) | apply now | done 2026-07-07 (one manual step remains) | Supersession header added; archived copy at `archive/CLAUDE_START_HERE.md`; both folder indexes updated. Steward tools cannot delete files, so a tombstone remains at `planning-inbox/CLAUDE_START_HERE.md` — owner deletes it manually |
| ISS-07 | decisions/README stale open issue (full audit) | apply now | done 2026-07-07 | |
| ISS-08 | M2 folder-subset decision follow-up rows stale (full audit) | apply now | done 2026-07-07 | REPO_MAP + M3 rows closed; contracts/ row closed at M7 activation |
| ISS-09 | Two same-date audits + dangling source reference in old audit-response (full audit) | apply now | done 2026-07-07 | Disambiguation headers added both sides; missing-ancestor note in audits/README |
| ISS-10 | 00/01 headers say draft while REPO_MAP says authority (both audits) | apply now | done 2026-07-07 | Headers promoted to authority |
| ISS-11 | RG13 missing hammer categories: append-only, concurrency, audit-first, migration rollback (both audits) | apply now | done 2026-07-07 | H19–H22 added as dated M7 addendum in RG13; minimum M8 suite updated |
| ISS-12 | No owner-ruling tracker; ~40 candidates scattered (both audits) | apply now | done 2026-07-07 | `planning-inbox/owner-ruling-tracker.md` created, groups A–G |
| ISS-13 | NC3/NC5 have no owning gate/contract (both audits) | assign to M7 contracts + needs owner ruling (OR-A5) | routed | Audit recommendation recorded in contracts/README planned list: NC3 → overlay contract; NC5 → typed read-tool skeleton; ROADMAP M7 contract list annotated |
| ISS-14 | Closure convention never refreshes trackers/review notes — root cause of staleness class (full audit) | apply now | done 2026-07-07 | Step added to ROADMAP_RULES closure convention |
| ISS-15 | ROADMAP closed-milestone stubs duplicated in Planned section (both audits) | defer with reason | deferred | Collapse after M7 closes; low risk meanwhile |
| ISS-16 | M5 planned-topics (12) → executed gates (13) mapping gap (both audits) | apply now | done 2026-07-07 | Mapping addendum added to `research/m5-research-gate-plan.md` |
| ISS-17 | RG6 drift vectors: "mechanically derived" sentiment; sample-summary stored-vs-read ambiguity (both audits) | assign to M7 claim-safety/AI contract + needs owner ruling (OR-A2/OR-A3) | routed | Tighten in contract language; RG left unedited as historical research |
| ISS-18 | Disagreement Ledger presumes persistence (both audits) | assign to M7 Cross-Check contract + needs owner ruling (OR-A1) | routed | Ledger is an open-question section, not a standalone contract; ROADMAP M7 contract list annotated |
| ISS-19 | Backlog missing DR16 (consumer authn/authz) and DR17 (provider secrets) (both audits) | apply now | done 2026-07-07 | Added to `research/deep-research-backlog.md` |
| ISS-20 | Prior audit slightly overstated NC5 as "folded into nothing" (full audit self-correction) | reject as issue / record correction | recorded | Accurate version: NC5 has read-tool mentions in RG4/RG5 but no owning gate/contract |
| ISS-21 | Git tracked/push state unverifiable with available tools; AUD-002 unknown (full audit) | assign to owner (manual) | open | Owner: run `git status`; push before cross-tool handoff |
| ISS-22 | RG8 lacks explicit predictive_claim class (both audits) | assign to M7 claim-safety contract | routed | Recorded in contracts/README planned list |
| SEQ-01 | Contract packaging: merge absence-rules into claim-safety; merge raw-pointer + drift; typed read-tool as skeleton only; owned-telemetry + SearchClarity as placeholders (M6/M7 audit) | apply now (recorded as plan) | done 2026-07-07 | Encoded in contracts/README planned list and ROADMAP M7 annotations; owner may override via OR-A6 |

---

## Remaining open items after this pass

```text
ISS-13 / ISS-17 / ISS-18 / ISS-22 — land inside their M7 contracts (rulings OR-A1..A5 pending)
ISS-15 — collapse ROADMAP stubs after M7 closure
ISS-21 — manual git verification/push (owner)
Owner-ruling groups A–G — see planning-inbox/owner-ruling-tracker.md
```

---

## Notes for LLMs

Do not re-fix items marked done. Do not treat routed contract items as done until their contract is drafted and the linked ruling is resolved.
