# Decision: M9 First Evidence Slice Closure

Status: accepted decision
Authority: owner decision / milestone closure
Date: 2026-07-10
Milestone: M9 — First Evidence Slice Definition
Owner statement: "Accept C2 and close M9."

---

## Decision

M9 accepts C2 as the first evidence slice:

```text
Controlled Public Manual Observation Package
```

M9 is closed.

M10 — Schema Planning Only is now active.

---

## Accepted Slice

The accepted first evidence slice is a controlled public/manual observation package.

It is intended to prove the Observatory spine:

```text
observed public artifact
  -> provenance
  -> scope
  -> rights
  -> retention
  -> raw support where allowed
  -> observation identity
  -> evidence identity
  -> read-time interpretation boundary
```

The slice may use controlled fixture/manual-public observation inputs only.

It is not production capture approval.

---

## Slice Scope

The accepted slice may include planning for:

- controlled public/manual observation package envelope;
- scope context;
- source family;
- capture method label;
- operator intent limited to observation purpose;
- observed public artifact reference;
- captured-at timestamp expectation;
- rights class;
- retention class;
- raw support pointer/hash if raw support is included;
- candidate observation concept;
- admitted observation concept;
- evidence ID concept;
- claim-use/freshness warning concept;
- no-strategy/no-recommendation boundary.

Optional companion:

```text
Minimal query/panel context may be included only if needed for measurement context.
```

The query/panel context must remain a measurement context, not a keyword strategy list.

---

## Required M10 Schema-Planning Inputs

M10 must plan schema only for the accepted first slice.

M10 must account for these hammer expectations:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  CapturePackage validation / observation envelope validation
H9  Freshness / point-in-time claim-use warning
H12 Raw archive integrity if raw support is included
H15 Evidence ID / citation integrity
H19 Append-only observations
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

M10 must name which hammers are deferred or out of scope for the first slice.

---

## Required Future M12 Execution Gates

M12 must eventually execute applicable hammers for the built first slice.

Expected M12 hammer surfaces include:

```text
missing scope rejected
unknown scope class rejected
customer/private identity rejected
missing rights rejected
unclear rights rejected
missing retention rejected
no-storage retention blocks persistence
strategy/recommendation content rejected
missing required observation-envelope fields rejected
raw hash missing/mismatch rejected if raw support exists
evidence ID stable and not confused with raw/provider IDs
observation mutation rejected
supersession path creates new record, not in-place edit
audit-first behavior for consequential writes
hostile weird input bounded/rejected
```

M12 may not execute provider spend, customer workflow, marketplace scraping, read-tool API/MCP, or recurring capture hammers unless a later milestone explicitly activates those surfaces.

---

## Deferred / Rejected Candidate Families

The following are not selected for the first slice:

| Candidate family | Disposition | Reason |
|---|---|---|
| Real DataForSEO provider observation | deferred to M13 | Requires provider admission, spend controls, endpoint recipes, and owner approval |
| Marketplace observation | deferred | Marketplace evidence ceiling and capture posture remain unresolved |
| Customer first-party overlay | deferred to M17 | Customer/private data remains read-time overlay only |
| SearchClarity report-support workflow | deferred to M15 | Would pull consumer/report concerns too early |
| Provider disagreement proof | deferred to M16 | Needs base observation path first and OR-A1 fail-closed posture |
| Full typed read API/MCP proof | deferred to M14 | M9 cannot implement or expose read tools |
| Recurring watch panel | deferred to M18 | Requires provider/cost/cadence/duplicate controls |

---

## Non-Authorization Boundary

This decision does not authorize:

```text
schema design beyond M10 planning
migrations
implementation
provider purchases
paid provider pulls
provider admission
API/MCP implementation
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
accepting any hammer as passed
manual capture as a production capture method
scraping
crawling
browser-extension capture
customer-facing reports
```

M10 may plan schema.

M10 may not run migrations.

---

## Source Inputs

This decision closes M9 using:

- `planning-inbox/m9-first-slice-candidate-comparison.md`
- `planning-inbox/m9-first-slice-definition-proposal.md`
- `hammers/hammer-matrix-v0-1.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- M7 contract draft set indexed in `contracts/README.md`
- owner statement: "Accept C2 and close M9."

---

## Closure Result

```text
M9 closed.
M10 active.
```

M10 is active for schema planning only.
