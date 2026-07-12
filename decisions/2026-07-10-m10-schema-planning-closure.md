# Decision: M10 Schema Planning Closure

Status: accepted decision
Authority: owner milestone closure / roadmap transition
Date: 2026-07-10
Milestone: M10 — Schema Planning Only
Closure basis: `planning-inbox/m10-logical-schema-plan-c2.md` and `planning-inbox/m10-schema-plan-review.md`

---

## Decision

M10 is closed.

M11 — Implementation Foundation is now active.

M10 accepts the logical schema planning target for the accepted first evidence slice:

```text
C2 — Controlled Public Manual Observation Package
```

This decision accepts logical schema responsibility planning only.

It does not accept physical DDL, migrations, implementation, provider integration, API/MCP tooling, dashboard work, customer-data handling, or strategy/recommendation storage.

---

## Accepted Logical Planning Target

M10 accepts the logical responsibility model described in:

```text
planning-inbox/m10-logical-schema-plan-c2.md
```

The logical model is bounded to these responsibility groups:

- scope context;
- observation package / envelope;
- observed artifact reference;
- raw support manifest if raw support is included;
- candidate observation;
- admitted observation;
- evidence identity;
- freshness / claim-use warning;
- audit event expectations;
- rejection reasons.

These are logical responsibilities for later planning and implementation foundation.

They are not tables, DDL, migrations, ORM models, or executable implementation.

---

## Required Defaults Recorded at Closure

### 1. Query / panel context

Default:

```text
Query/panel context is deferred from the base C2 schema plan.
```

A minimal measurement-context placeholder may be revisited later only if needed, and only if it does not become:

- a keyword strategy list;
- a priority list;
- a recurring capture plan;
- a provider execution plan;
- a recommendation store.

H14 query panel immutability remains deferred for the base C2 slice unless a later owner-approved planning step explicitly adds a minimal context placeholder.

### 2. Raw support posture

Default:

```text
Raw support is optional but first-class when included.
```

The schema plan must support raw-support manifests and hash verification when raw support is allowed.

Raw payload retention remains rights/retention-gated.

Raw support may be:

- retained with pointer/hash only when permitted;
- manifest-only when retention requires it;
- blocked entirely when rights/retention fail closed.

M10 does not approve raw payload retention by default.

### 3. Evidence identity posture

Default:

```text
M10 plans internal evidence identity only.
```

M10 may plan internal `evidence_id` and internal citation-handle concepts for admitted observations.

M10 does not plan or approve:

- report-safe customer references;
- customer-facing citation handles;
- external citation exposure;
- evidence IDs that encode customer identity;
- raw IDs/provider IDs as evidence IDs.

OR-A4 remains open for future report-safe citation behavior.

### 4. Audit event posture

Default:

```text
M10 plans minimum audit event concepts for consequential transitions only.
```

Minimum M10 audit event concepts:

```text
package_rejected
package_validated
observation_admitted
observation_superseded
observation_withdrawn
raw_support_purged
```

M10 does not create a full operations ledger.

M19 owns full hardening, backup, restore, recovery, and operations proof.

---

## Hammer Coverage Accepted for Planning

M10 accepts planning coverage for:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  Observation envelope validation
H9  Freshness / point-in-time claim-use warning
H12 Raw archive integrity if raw support is included
H15 Evidence ID / citation integrity
H18 Hostile weird input, planning only
H19 Append-only observations
H21 Audit-first enforcement, planning only
H22 Rollback/recovery expectations, planning only
```

No hammer has passed.

Executable hammer proof remains future work.

---

## Deferred / Excluded Schema Families

M10 explicitly excludes schema planning for:

```text
customer identity tables
customer order tables
SearchClarity report tables
strategy tables
recommendation tables
provider truth/winner tables
provider average score-as-truth tables
provider task execution tables
DataForSEO pull execution tables
API/MCP access tables
dashboard state tables
scheduler/recurring capture tables
private analytics tables
marketplace capture tables
cross-scope aggregate tables
```

Any future inclusion of those families requires the owning later milestone and, where applicable, explicit owner ruling.

---

## M11 Activation Boundary

M11 may begin implementation-foundation planning only.

M11 may plan:

- repository implementation foundation expectations;
- local project skeleton needs if still required;
- test harness strategy;
- migration folder expectations without running migrations;
- fixture/sample design expectations;
- first hammer test scaffold expectations;
- config pattern without secrets.

M11 must not perform real implementation unless the milestone explicitly permits the specific foundation task and preserves all boundaries.

M11 must not run migrations, connect providers, build dashboards, create API/MCP tools, handle customer data, or store strategy/recommendations.

---

## Non-Authorization Boundary

This decision does not authorize:

```text
physical DDL
running migrations
implementation beyond future M11 foundation boundaries
provider purchases
paid provider pulls
provider admission
DataForSEO calls
API/MCP implementation
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
accepting any hammer as passed
manual capture as production capture
scraping
crawling
browser-extension capture
customer-facing reports
```

---

## Source Inputs

This decision closes M10 using:

- `decisions/2026-07-10-m9-first-slice-closure.md`
- `planning-inbox/m10-logical-schema-plan-c2.md`
- `planning-inbox/m10-schema-plan-review.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- M7 contract draft set indexed in `contracts/README.md`

---

## Closure Result

```text
M10 closed.
M11 active.
```

M11 is active for implementation foundation only, under the roadmap boundaries.
