# Owner-Ruling Tracker

Status: planning / ruling tracker
Authority: none — this file tracks candidates; rulings bind only via `decisions/` records or explicit owner statements recorded there
Purpose: consolidate every open owner-ruling candidate scattered across research, boundaries, roadmap, and audits so contracts do not ship with silent assumptions
Created: 2026-07-07 (M7 audit-fix pass; consolidates candidates from RG1–RG13, boundaries, roadmap, and both 2026-07-07 audits)

---

## Rules

- Every ruling candidate gets one row. New candidates found in any doc get added here with a source reference.
- Status vocabulary: `open`, `ruled — see decision`, `delegated to contract decision`, `withdrawn`.
- Until ruled, the affected behavior fails closed.
- A ruling recorded only in chat is not a ruling. Route it to `decisions/` or record the owner's explicit statement here with date.

---

## Group A — Needed during M7 (contract-shape rulings)

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-A1 | Provider Cross-Check: is a *persisted* Disagreement Ledger permitted, or compute-on-read only? (V6 materialization test applies) | RG9; ROADMAP contract list; audits ISS-18 | open |
| OR-A2 | RG6 sentiment/tone: provider-attributed-only, or is any "mechanically derived" sentiment permitted? | RG6; audits ISS-17 | open |
| OR-A3 | `ai_visibility_sample_summary`: read-time output only, or storable under materialization test? | RG6; audits ISS-17 | open |
| OR-A4 | Citation handles: global vs artifact-local; report-safe references separate class or derived? | RG3; DR14 | open — delegable to contract decision |
| OR-A5 | NC3 (intervention timeline) and NC5 (coverage/blind-spot) disposition: contract sections vs DR items. Audit recommendation: NC3 → overlay contract; NC5 → typed read-tool skeleton | harvest register NC3/NC5; audits ISS-13 | ruled — see `decisions/2026-07-10-m7-closure.md`; NC3 routed to `contracts/overlay.md`, NC5 routed to `contracts/typed-read-tool-skeleton.md` |
| OR-A6 | Minimum M7 contract set required for M7 closure (which of the 13 planned contracts are mandatory vs optional) | ROADMAP M7; audits | ruled — see `decisions/2026-07-10-m7-closure.md`; all 13 planned M7 contracts drafted and indexed for closure |
| OR-A7 | audits/ folder earned and governed | owner statement 2026-07-07 | ruled — see `decisions/2026-07-07-audits-folder.md` |

## Group B — Needed before M8 hammers close

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-B1 | Hammer acceptance criteria + acceptable mock/stub level for pre-implementation hammers | RG13 | open — draft default recorded in `hammers/acceptance-gate-policy-v0-1.md`; mock/stub planning does not satisfy implementation acceptance unless later ruled |
| OR-B2 | Which hammers are hard gates for which milestone | RG13 | open — draft milestone mapping recorded in `hammers/hammer-matrix-v0-1.md` and `hammers/acceptance-gate-policy-v0-1.md`; not binding until accepted |
| OR-B3 | Does any freshness class automatically block customer-facing report use? | RG5 | open — draft fail-closed default recorded in `hammers/acceptance-gate-policy-v0-1.md`; M15 must revisit report-facing use |

## Group C — Needed before M13 provider/capture admission

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-C1 | Fund/use a DataForSEO account; release the reserved validation budget; approve recipe/endpoint list/ceilings/stop conditions | RG1; DR1; `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md`; `decisions/2026-07-12-m13-dataforseo-exploratory-campaign.md`; `decisions/2026-07-12-m13-closure-and-m14-activation.md` | ruled for the completed C00 request only — the authorized request was consumed and M13 closed; no additional live request is authorized; any future request requires a new decision and the post-M13 provider hardening gates |
| OR-C2 | Long-term raw payload retention posture per source family (durable vs manifest-only vs capture-and-purge vs no-storage) | RG1 F6; RG11; DR2; `decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md` | open — first-probe capture-and-purge posture proposed only; no general or durable retention ruling |
| OR-C3 | Use AI Optimization endpoint families for validation | RG1; RG6 | open |
| OR-C4 | Raw archive layout: filesystem-first, object-storage-first, or hybrid | RG11; DR13 | open |
| OR-C5 | Etsy: pursue API path and/or express written authorization, or keep all Etsy evidence consumer/report-side | RG7; DR6 | open |
| OR-C6 | Browser-extension capture instrument: admit per-marketplace, keep deferred, or kill | RG7; DR8; harvest Q2 | open |
| OR-C7 | Fiverr capture posture after full-terms review | RG7; DR7 | open |
| OR-C8 | Manual public observations as Observatory evidence (manual-capture family contract) | RG10; DR8; harvest Q2 | open |
| OR-C9 | market_watch panel execution before provider validation spend | RG4 | open |
| OR-C10 | Capture-and-purge exceptions for unclear rights (per-case) | RG2; RG10 | open |
| OR-C11 | Recurring capture of any kind (also gates M18) | RG4; RG5; boundaries deferred list | open |

## Group D — Needed before M14 API/MCP

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-D1 | Consumer authentication/authorization model | RG12; DR16; `planning-inbox/m14-owner-ruling-proposals.md` | open — concrete M14 proposal prepared; owner ruling required before prototype implementation |
| OR-D2 | Raw payload pointer exposure outside internal tools | RG3; `planning-inbox/m14-owner-ruling-proposals.md` | open — internal-only fail-closed proposal prepared; owner ruling required before contract acceptance |
| OR-D3 | Evidence withdrawal/deprecation/supersession behavior finalization | RG3; DR14; `planning-inbox/m14-owner-ruling-proposals.md` | open — status-aware read proposal prepared; owner ruling required before evidence-handle contract acceptance |
| OR-D4 | Update-window feeds as a read-tool dependency | RG5; `planning-inbox/m14-owner-ruling-proposals.md` | open — fail-closed unknown/caveated proposal prepared; owner ruling required before contract acceptance |
| OR-D5 | Ordinary-read event posture versus separate security/access logging | post-M13 audit; V9; `planning-inbox/m14-owner-ruling-proposals.md` | open — proposal keeps ordinary reads out of evidence events while allowing bounded security logs outside the evidence corpus |
| OR-D6 | Machine-readable implementation-test result register as repository proof metadata | post-M13 audit; `planning-inbox/m14-read-boundary-hostile-path-plan.md`; `planning-inbox/m14-owner-ruling-proposals.md` | open — proposal prepared; not an Observatory observation or database requirement |

## Group E — Needed before M15 SearchClarity proof

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-E1 | SearchClarity report-safe language + evidence-handle exposure to customers | RG8; DR9 | open |
| OR-E2 | Marketplace evidence permitted in customer reports | RG7; RG8 | open |
| OR-E3 | Report-safe AI visibility metrics + repeated-sampling thresholds | RG6; DR4 | open |
| OR-E4 | Provider disagreement shown in customer-facing reports | RG9 | open |
| OR-E5 | Any claim status automatically blocking a downstream report | RG8 | open |

## Group F — Needed before M17 overlay/internal telemetry proof

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-F1 | Customer first-party overlay acceptance rules into read tools | RG12; DR10 | open |
| OR-F2 | Internal first-party telemetry admission + internal-scope handling | RG2; RG12; DR11 | open |
| OR-F3 | Overlay freshness metadata used in customer-facing conclusions | RG5 | open |

## Group G — Deferred (do not resolve now)

| ID | Ruling needed | Source | Status |
|---|---|---|---|
| OR-G1 | Cross-scope aggregate analysis exception (seismograph etc.) | boundaries; M4 D3 | open — forbidden by default |
| OR-G2 | TacticCapture family + triage verdict storage location | M4 D2 | open — not admitted |
| OR-G3 | New scope_class beyond internal/customer_engagement/market_watch | RG2 | open |
| OR-G4 | Ahrefs/Semrush admission research activation | DR3; roadmap deferred list | open |
| OR-G5 | Persistent strategy records / V21-style future layer (doctrine change) | boundaries; harvest V21 | open — forbidden unless doctrine change |

---

## Notes for LLMs

If drafting a contract that touches an open ruling: mark the ruling ID in the contract's owner-ruling section and make the affected behavior fail closed.

Do not mark a row `ruled` without a decision record or an explicit dated owner statement.
