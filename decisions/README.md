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
| `2026-07-10-m9-first-slice-closure.md` | accepted decision | Records M9 first-slice selection, M9 closure, and M10 activation | C2 Controlled Public Manual Observation Package accepted; M10 schema planning is active |
| `2026-07-10-m10-schema-planning-closure.md` | accepted decision | Records M10 logical schema planning closure and M11 activation | C2 logical responsibility planning accepted; M11 implementation foundation is active |
| `2026-07-10-m11-foundation-closure.md` | accepted decision | Records M11 implementation foundation closure and M12 activation | C2 foundation expectations accepted; M12 first evidence slice build is active |
| `2026-07-10-m12-first-slice-closure.md` | accepted decision | Records M12 first evidence slice closure and M13 activation | Bounded local C2 proof accepted; M13 provider admission planning is active |
| `2026-07-11-m13-dataforseo-controlled-probe-approval.md` | accepted decision | Authorizes the bounded fixture-only DataForSEO probe safety cage and preserves separate funding/execution gates | Fixture-only implementation accepted; live execution remains separately controlled |
| `2026-07-12-m13-dataforseo-exploratory-campaign.md` | accepted decision | Reserves the available $50 balance for staged DataForSEO provider validation and defines per-pull review gates | Campaign catalog/testing authorized; each live request still requires preflight and explicit owner confirmation |
| `2026-07-12-m13-closure-and-m14-activation.md` | accepted decision | Closes M13 after the reviewed C00 probe and activates M14 planning | One paid probe accepted, raw payload purged with proof, no further provider or implementation authority granted |
| `2026-07-12-m14-contract-and-read-boundary-rulings.md` | accepted decision | Accepts contract set v0.1 and M14 read-boundary rulings | No production API/MCP, persistence, provider execution, or customer-data authority |
| `2026-07-12-m14-typed-read-contract-acceptance-and-prototype-authorization.md` | accepted decision | Accepts the full M14 typed-read contract and authorizes one exact fixture-backed prototype | Local, in-memory proof only; no network, database, provider, customer, overlay, or report work |
| `2026-07-12-m14-closure-and-m15-activation.md` | accepted decision | Closes M14 after bounded proof and activates M15 planning | SearchClarity consumer-boundary planning only; no customer records, reports, overlays, production integration, or persistence |
| `2026-07-12-m15-searchclarity-contract-and-consumer-boundary-rulings.md` | accepted decision | Accepts the M15 SearchClarity proof-workflow contract and consumer-boundary rulings | Proof implementation remains separately gated; no customer data, overlays, report generation, production integration, provider execution, or persistence |
| `2026-07-12-m15-searchclarity-fixture-proof-authorization.md` | accepted decision | Authorizes one exact synthetic fixture-backed M15 proof task | Local, in-memory proof only; no real customers, reports, overlays, integration, provider execution, or persistence |
| `2026-07-12-m15-closure-and-m16-activation.md` | accepted decision | Closes M15 after bounded proof and activates M16 planning | Provider disagreement planning only; no new provider work, truth scores, winner logic, recurring capture, persistence, or production integration |
| `2026-07-12-m16-provider-cross-check-contract-and-rulings.md` | accepted decision | Accepts the M16 provider cross-check proof contract and rulings | Proof implementation remains separately gated; no provider execution, purchases, recurring capture, persistence, truth/winner/composite logic, customer data, reports, or production integration |
| `2026-07-12-m16-provider-cross-check-fixture-proof-authorization.md` | accepted decision | Authorizes one exact synthetic fixture-backed M16 provider cross-check proof task | Local, deterministic, in-memory proof only; no provider execution, purchases, recurring capture, persistence, customer data, reports, database, or production integration |
| `2026-07-12-m16-closure-and-m17-activation.md` | accepted decision | Closes M16 after bounded proof and activates M17 planning | Overlay planning only; no real private analytics, files, persistence, canonical ingestion, provider execution, database, or production integration |
| `2026-07-12-m17-owned-telemetry-overlay-contract-and-rulings.md` | accepted decision | Accepts the M17 owned telemetry overlay proof contract and rulings | Proof implementation remains separately gated; no real private telemetry, files, persistence, manifests, canonical ingestion, database, reports, or production integration |
| `2026-07-12-m17-owned-telemetry-overlay-fixture-proof-authorization.md` | accepted decision | Authorizes one exact synthetic fixture-backed M17 overlay proof task | Local, deterministic, in-memory code-path discard proof only; no real private telemetry, files, persistence, database, reports, or production integration |
| `2026-07-12-m17-closure-and-m18-activation.md` | accepted decision | Closes M17 after bounded overlay discard proof and activates M18 planning | Recurring watch-panel planning only; no scheduler, recurring execution, autonomous spend, provider calls, crawling, database, or production integration |
| `2026-07-12-m18-watch-panel-policy-and-m19-activation.md` | accepted decision | Accepts the bounded M18 watch-panel policy, rejects recurring execution for v1, closes M18, and activates M19 planning | Hardening/backup/recovery planning only; no scheduler, recurring provider work, live database, deployment, credentials, or production integration |
| `2026-07-12-m19-hardening-backup-recovery-rulings.md` | accepted decision | Accepts repository-only protection, manual encrypted backups, mandatory disposable restore proof, redacted secret checks, and no destructive cleanup | Bounded archive/restore proof implementation remains separately gated; no cloud upload, credential transfer, live database backup, scheduling, or deletion |
| `2026-07-12-m19-bounded-backup-restore-proof-authorization.md` | accepted decision | Authorizes one exact owner-local repository bundle and disposable restore proof | Encryption remains blocked without a separately approved tool/key path; no cloud upload, credentials, database backup, scheduling, or cleanup |
| `2026-07-12-m19-closure-and-m20-activation.md` | accepted decision | Closes M19 after bounded repository recovery proof and activates M20 acceptance planning | Acceptance review only; encryption/off-machine recovery remains unproven and no production deployment or implementation widening is authorized |
| `2026-07-12-observatory-v1-acceptance.md` | accepted decision | Accepts Observatory v1 at the bounded proof-system ceiling and closes M20 | Known limits remain binding; no production, post-v1 implementation, provider expansion, recurrence, live database, customer data, reports, or production API/MCP authority |
| `2026-07-12-post-v1-audit-acceptance-and-db-roadmap-activation.md` | accepted decision | Accepts the post-v1 audit as advisory input, preserves v1 acceptance, and activates DB-1 reconciliation/database-roadmap planning | No Postgres creation, DDL, migration files/execution, real ingestion, provider calls, customer data, or production authority |
| `2026-07-12-db1-contract-corrections-and-database-boundary-rulings.md` | accepted decision | Accepts typed-read and SearchClarity v0.1.1 corrections plus OR-B1/B2/C2/C4 | Authorizes DB-1 hammer-policy and data-contract planning only; no Postgres, DDL, migrations, persistence, capture, ingestion, or production authority |
| `2026-07-13-db1-closure-and-db2-activation.md` | accepted decision | Accepts hammer policy v0.2, result-register v0.1, and the DB-2 logical freeze; closes DB-1 and activates DB-2 | Logical-contract work only; no Postgres, roles, DDL, migrations, real hammers, persistence, ingestion, or DB-3 authority |

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
Result: M12 first-slice closure decision added and indexed; roadmap state moved from M12 to M13
Open issues: none
```
