# Contracts

Status: contract-folder index
Authority: folder index; individual contracts become binding only when marked accepted
Purpose: hold non-schema contracts that define Observatory evidence behavior before any database design, provider admission, API/MCP implementation, or consumer integration

---

## Purpose

`contracts/` holds M7's core deliverables: non-schema contracts drafted from the M6 research outputs.

A contract here defines behavior, vocabularies, required fields, validation rules, fail-closed defaults, and boundaries. It does not define physical schema, migrations, endpoints, code, or tests.

Folder earned at M7 per `decisions/2026-07-07-m2-folder-subset.md` (deferred-until-M7 ruling) and activated during the 2026-07-07 M7 audit-fix pass.

---

## What Belongs Here

- non-schema evidence-behavior contracts (scope/rights/retention, evidence ID/citation, freshness, claim safety, query panel, CapturePackage, raw archive/drift, provider testimony/cross-check, consumer/promotion/overlay, typed read-tool skeleton)
- the contract template
- contract-status changes recorded in each contract's own header

## What Does Not Belong Here

- physical schema or migrations
- API/MCP implementation specs beyond contract-level requirements
- provider admission decisions (those are M13 + `decisions/`)
- customer private data, credentials, raw provider payloads
- strategy/recommendation content of any kind
- research (that lives in `research/`; contracts cite it)

---

## Contract Rules

1. Every contract cites its source RG doc(s) and stays aligned with `02-boundaries.md`. On conflict, boundaries win.
2. Every contract carries a status: `draft` → `ready for review` → `accepted` (owner) → possibly `superseded`. Only `accepted` binds.
3. Every contract preserves its owner-ruling candidates and deeper-research blockers explicitly — no silent assumptions.
4. Field lists in contracts are contract-level requirements, not schema. M10 plans schema from accepted contracts; contracts must not pre-draw tables.
5. Anything that would persist interpretive output must pass the V6 materialization test and an explicit owner ruling before a contract permits it.

---

## Reading Order

1. `contract-template.md` — the required shape
2. Contracts in drafting order once they exist (spine first: scope/rights/retention, then evidence ID/citation)

---

## File Index

| File | Status | Purpose | Notes |
|---|---|---|---|
| `contract-template.md` | template | Required structure for all Observatory contracts | Created during M7 audit-fix pass |

Planned M7 contracts (not yet drafted; sequencing per the 2026-07-07 audits):

```text
1. scope-rights-retention        (RG2)
2. evidence-id-citation          (RG3)
3. freshness-staleness-volatility (RG5)
4. claim-safety                  (RG8 + RG6; absorbs negative-evidence/absence rules; includes predictive_claim class)
5. query-panel                   (RG4)
6. capturepackage-v0-1           (RG10)
7. raw-archive-provider-drift    (RG11; merged raw pointer + drift)
8. provider-testimony            (RG1 + RG9 + V7; skeleton until M13 bindings)
9. provider-cross-check          (RG9; Disagreement Ledger persistence is an open-question section, not presumed)
10. consumer-promotion           (RG12)
11. overlay                      (RG12/DR10; covers customer first-party overlays AND NC3 intervention-timeline ephemeral inputs)
12. searchclarity-consumer-placeholder (RG12; placeholder only until DR9)
13. typed-read-tool-skeleton     (RG3/RG5/RG8/RG12; skeleton only — M14 owns the real contract; includes NC5 coverage/blind-spot output fields)
```

---

## Related Roadmap Milestones

- M7 — drafts these contracts
- M8 — hammers are defined against them
- M10 — schema planning consumes accepted contracts
- M13/M14/M15 — provider, read-tool, and consumer milestones bind them

---

## Notes for LLMs

Draft contracts are not law. Accepted contracts are law within their scope, subordinate to `02-boundaries.md`.

Do not invent contracts not listed in the roadmap/this index without owner approval.

If a contract draft would store meaning, strategy, recommendations, customer data, or truth-scores, stop — it is failing.

---

## Last Review Notes

```text
Last reviewed: 2026-07-07
Reviewer: Claude (Observatory Project Steward role)
Result: Folder + template created during M7 audit-fix pass; no contracts drafted yet
Open issues: Draft spine contracts (scope/rights/retention, evidence ID/citation) next
```
