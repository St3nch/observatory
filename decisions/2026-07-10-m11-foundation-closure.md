# Decision: M11 Implementation Foundation Closure

Status: accepted decision
Authority: owner milestone closure / roadmap transition
Date: 2026-07-10
Milestone: M11 — Implementation Foundation
Closure basis: `planning-inbox/m11-implementation-foundation-spec.md` and `planning-inbox/m11-foundation-readiness-review.md`

---

## Decision

M11 is closed.

M12 — First Evidence Slice Build is now active.

M11 accepts the implementation-foundation specification for the accepted first evidence slice:

```text
C2 — Controlled Public Manual Observation Package
```

This decision accepts foundation expectations only.

It does not accept executable implementation, migrations, provider calls, API/MCP exposure, dashboard work, customer-data handling, or strategy/recommendation storage.

---

## Accepted Foundation Planning Target

M11 accepts the foundation expectations described in:

```text
planning-inbox/m11-implementation-foundation-spec.md
planning-inbox/m11-foundation-readiness-review.md
```

The accepted M11 foundation target is:

```text
Implementation foundation for the C2 Controlled Public Manual Observation Package
```

The foundation workbench is expected to support later M12 build work for:

- C2 fixture/sample design;
- observation package envelope behavior;
- validation and rejection behavior;
- raw support manifest/hash behavior if raw support is included;
- candidate observation separation;
- admitted observation behavior;
- internal evidence identity;
- minimum audit-event behavior;
- executable hammer proof for the C2 first slice.

---

## Required Defaults Recorded at Closure

### 1. Folder creation posture

Default:

```text
Actual implementation folder/file creation is deferred to M12 by default.
```

M11 specified the workbench.

M11 did not create implementation folders, fixture files, test files, migration files, or runnable code.

M12 may create concrete folders/files only inside its active build boundary.

### 2. Migration posture

Default:

```text
No migration folder or migration placeholder is required during M11 closure.
```

M11 does not authorize:

```text
runnable migrations
DDL
SQL CREATE TABLE statements
ORM migration classes
migration execution scripts
Postgres connection code
```

M12 may address migration/build mechanics only if bounded to the accepted first slice and consistent with roadmap authority.

### 3. Test harness posture

Default:

```text
M11 accepts test-harness strategy only, not executable test implementation.
```

M12 inherits the planned hammer/test groups for:

```text
scope validation
rights validation
retention validation
envelope validation
strategy rejection
raw manifest integrity
evidence ID integrity
freshness warning
append-only behavior
audit expectation
hostile input
```

No hammer has passed.

Executable hammer proof belongs to M12 or later milestones as applicable.

### 4. Fixture posture

Default:

```text
M11 accepts safe fixture classes and names, but does not create fixture files.
```

M12 may create fixture files only if they remain:

- non-customer;
- non-provider;
- non-marketplace;
- no-secrets;
- controlled/public/manual-fixture only;
- bounded to C2.

### 5. Configuration posture

Default:

```text
M11 accepts a no-secrets local/test configuration pattern only.
```

Allowed future config concepts remain limited to:

```text
environment label
fixture root path
raw support fixture path
hash algorithm label
strict validation flag
```

Still forbidden:

```text
provider API keys
database passwords
OAuth tokens
customer account IDs
analytics credentials
paid-provider budget settings
```

---

## M12 Activation Boundary

M12 may now begin the first evidence slice build for the accepted C2 slice only.

M12 may work only on what is necessary for:

- controlled public/manual fixtures;
- C2 observation package/envelope behavior;
- scope, rights, and retention fail-closed behavior;
- raw support manifest/hash behavior when included;
- candidate-to-admitted observation separation;
- internal evidence identity;
- minimum audit-event concepts;
- executable hammers for the accepted C2 hammer set.

M12 remains forbidden from:

```text
provider calls
provider clients
DataForSEO pulls
Ahrefs/Semrush work
provider admission
customer data
marketplace scraping
browser-extension capture
API/MCP exposure
dashboard work
recurring capture
strategy/recommendation storage
report generation
manual capture as production capture
accepting hammers without execution evidence
```

---

## Required M12 Hammer Focus

M12 must preserve the C2 hammer set:

```text
H1  Scope isolation
H2  Rights fail-closed
H3  Retention enforcement
H5  No strategy/recommendation storage
H6  Observation envelope validation
H9  Freshness / point-in-time claim-use warning
H12 Raw archive integrity if raw support is included
H15 Evidence ID / citation integrity
H18 Hostile weird input
H19 Append-only observations
H21 Audit-first enforcement
H22 Rollback/recovery expectations
```

M12 may not claim a hammer has passed until the required executable proof exists.

---

## Non-Authorization Boundary

This decision does not authorize:

```text
provider purchases
paid provider pulls
provider admission
DataForSEO calls
Ahrefs/Semrush work
API/MCP exposure
dashboard work
customer data handling
capture runner implementation
automated recurring capture
strategy/recommendation storage
customer-facing reports
manual capture as production capture
scraping
crawling
browser-extension capture
broad implementation beyond C2
```

---

## Source Inputs

This decision closes M11 using:

- `decisions/2026-07-10-m10-schema-planning-closure.md`
- `planning-inbox/m11-implementation-foundation-spec.md`
- `planning-inbox/m11-foundation-readiness-review.md`
- `hammers/acceptance-gate-policy-v0-1.md`
- M10 logical schema plan and review by reference

---

## Closure Result

```text
M11 closed.
M12 active.
```

M12 is active for the first evidence slice build only, under the roadmap boundaries.
