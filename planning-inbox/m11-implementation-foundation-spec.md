# M11 Implementation Foundation Spec — C2 Controlled Public Manual Observation Package

Status: planning / implementation-foundation specification
Authority: none — planning draft only; roadmap and decisions remain authority
Milestone: M11 — Implementation Foundation
Date: 2026-07-10
Source decision: `decisions/2026-07-10-m10-schema-planning-closure.md`
Accepted first slice: C2 — Controlled Public Manual Observation Package

---

## Purpose

This document specifies the M11 implementation foundation for the accepted C2 first evidence slice.

It defines what a later foundation implementation may prepare before M12 builds the first slice.

This is foundation specification only.

---

## Non-Authorization Boundary

This document does not authorize:

```text
running migrations
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
accepting any hammer as passed
manual capture as production capture
scraping
crawling
browser-extension capture
customer-facing reports
```

M11 may specify and, if later explicitly approved inside M11, create minimal foundation files for the accepted C2 slice only.

M11 must not build the first evidence slice itself; M12 owns that build.

---

## Foundation Target

M11 targets only:

```text
Implementation foundation for the C2 Controlled Public Manual Observation Package
```

The foundation must prepare the project for this later M12 path:

```text
controlled fixture/manual public artifact
  -> observation package envelope
  -> validation/rejection behavior
  -> raw support manifest if allowed
  -> candidate observation
  -> admitted observation
  -> evidence identity
  -> audit expectation
  -> hammer execution
```

M11 must not add provider, marketplace, customer, dashboard, API/MCP, or strategy surfaces.

---

## M11 Deliverable Groups

M11 foundation work should be split into these deliverable groups.

| Group | Purpose | M11 posture |
|---|---|---|
| Repository foundation | Decide whether an implementation folder/skeleton is needed | Planning now; create only if owner/steward approves within M11 |
| Test harness strategy | Define how future hammers will run | Planning required before M12 |
| Fixture/sample design | Define safe public/manual fixture inputs | Planning required before M12 |
| Migration-folder expectation | Define where migrations will live later | Planning only; no migration files that run |
| Configuration pattern | Define local config shape without secrets | Planning required; no secrets |
| Initial hammer scaffold expectation | Map M12 executable tests to C2 hammers | Planning required; scaffold only if explicitly approved |
| M12 handoff | Define what M12 must build and prove | Required before M11 closure |

---

## Repository Foundation Expectations

M11 should inspect whether the repository already has an implementation root.

If no implementation root exists, M11 may propose one, but must not create broad app architecture.

Allowed foundation shapes:

```text
src/ or app/ skeleton for C2-only domain logic
fixtures/ for controlled non-customer public/manual fixtures
tests/ for future hammer tests
migrations/ placeholder folder only if needed, with no runnable migrations
```

Disallowed foundation shapes:

```text
provider integration folders
DataForSEO clients
API servers
MCP tools
dashboard apps
customer models
strategy/recommendation modules
scheduler/capture-runner services
marketplace scrapers
browser extension code
```

M11 must prefer minimal names and comments that prevent future overreach.

---

## Test Harness Strategy

M11 should plan a test harness that can later prove the C2 hammer gates.

The test harness should support:

```text
pure fixture-based tests
no external network calls
no provider credentials
no database dependency unless M12 explicitly introduces one
no customer data
bounded malformed-input fixtures
clear pass/fail/blocked result vocabulary
```

M11 test strategy should prepare for these M12 test groups:

| Test group | Purpose | Hammer coverage |
|---|---|---|
| scope validation | reject missing/unknown/customer-like scope | H1/H4 |
| rights validation | reject missing/unclear/restricted rights | H2 |
| retention validation | reject missing/forbidden/no-storage raw retention | H3 |
| envelope validation | reject missing required package fields | H6 |
| strategy rejection | reject recommendation/strategy text as stored evidence | H5 |
| raw manifest integrity | reject missing pointer/hash or hash mismatch when raw support exists | H12 |
| evidence ID integrity | prevent evidence IDs before admission and ID confusion | H15 |
| freshness warning | require point-in-time claim-use posture | H9 |
| append-only behavior | prevent mutation/backdating of admitted observation | H19 |
| audit expectation | require audit event concepts for consequential transitions | H21 |
| hostile input | reject malformed/oversized/weird fixture input | H18 |

M11 must not claim these tests pass.

---

## Fixture / Sample Design Expectations

M11 should specify safe fixture classes for M12.

Allowed fixture classes:

```text
owner-controlled public test page fixture
static public HTML/text fixture created for Observatory tests
small public-page metadata fixture with no private/customer data
manifest-only raw support fixture
hash-mismatch raw support fixture
rights-missing fixture
retention-missing fixture
strategy-text rejection fixture
customer-like identity rejection fixture
```

Disallowed fixture classes:

```text
real customer page from a paid engagement
customer analytics exports
GSC/GA4/Search Console data
Etsy/Shopify/Fiverr private seller/account data
marketplace listing capture
SERP scrape
AI answer-surface capture
DataForSEO response
provider API response
screenshots of private dashboards
```

Fixture naming should make non-production status obvious.

Recommended naming posture:

```text
fixture_public_manual_observation_valid
fixture_missing_rights_rejected
fixture_raw_hash_mismatch_rejected
fixture_strategy_text_rejected
fixture_customer_identity_rejected
```

---

## Migration-Folder Expectations

M11 may plan where migrations belong later, but must not run migrations.

M11 may define:

```text
future migration folder name
future migration naming convention
future rollback expectation
future no-op placeholder note
```

M11 must not create:

```text
runnable migration files
DDL
SQL CREATE TABLE statements
ORM migration classes
Postgres connection code
migration execution scripts
```

If a placeholder folder is created later, it should include a README that says:

```text
No migrations are authorized until the roadmap explicitly opens migration work.
```

M12 owns first-slice build/migration execution only if later authorized.

---

## Local Configuration Pattern

M11 should define a local config pattern that avoids secrets and external services.

Allowed config concepts:

```text
environment label: local/test
fixture root path
raw support fixture path
hash algorithm label
strict validation mode flag
```

Forbidden config concepts:

```text
provider API keys
DataForSEO credentials
database passwords
customer account IDs
OAuth tokens
MCP credentials
analytics credentials
paid-provider budget settings
```

Configuration must default safe.

Safe default posture:

```text
network disabled
provider calls disabled
customer data disabled
strategy storage disabled
raw retention blocked unless fixture-retention explicitly permits manifest/hash posture
```

---

## Initial Hammer Scaffold Expectations

M11 may plan an initial hammer scaffold for M12.

Required M12 hammer labels for C2:

```text
H1_scope_isolation
H2_rights_fail_closed
H3_retention_enforcement
H5_no_strategy_recommendation_storage
H6_observation_envelope_validation
H9_freshness_claim_use_warning
H12_raw_archive_integrity_if_raw_support
H15_evidence_id_citation_integrity
H18_hostile_weird_input
H19_append_only_observations
H21_audit_first_enforcement
H22_rollback_recovery_expectations
```

Each scaffolded hammer should be able to remain:

```text
planned
blocked_not_implemented
fixture_executable_later
```

M11 must not mark any hammer:

```text
passed
accepted
complete
```

---

## C2 Foundation Modules / Responsibilities

M11 may define module responsibilities at a high level.

Allowed C2-only module concepts:

| Module concept | Responsibility | Boundary |
|---|---|---|
| scope validation | Validate safe internal fixture scope | No customer identity registry |
| observation envelope validation | Validate required package fields | No provider task execution |
| rights/retention validation | Fail closed before admission | No terms automation or legal advice |
| raw manifest validation | Verify pointer/hash concepts for fixtures | No production raw archive service |
| candidate observation validation | Keep candidate separate from evidence | No strategy/recommendation payloads |
| evidence identity assignment | Internal evidence identity only | No report-safe handles |
| audit event expectation | Record required future transition concepts | No full ops ledger |
| rejection handling | Preserve why invalid input is blocked | Rejected material is not evidence |

Forbidden module concepts:

```text
provider_client
seo_recommendation_engine
strategy_store
customer_repository
report_generator
api_server
mcp_tool_server
dashboard
scheduler
crawler
scraper
browser_extension
```

---

## M12 Handoff Expectations

M11 should leave M12 with enough clarity to build the first slice without guessing.

M12 handoff should include:

```text
foundation file/folder plan
fixture list
validation responsibility list
hammer-test groups
blocked/non-applicable hammer list
config no-secrets rule
migration boundary
raw support optional/first-class rule
internal evidence ID rule
audit event minimum set
```

M12 should not proceed until M11 explicitly records these.

---

## M11 Closure Criteria

M11 may close when:

- foundation deliverables are specified concretely;
- repo/skeleton expectations are clear;
- test-harness expectations are clear;
- fixture/sample expectations are clear;
- migration-folder expectations exist without running migrations;
- configuration pattern excludes secrets and providers;
- initial hammer scaffold expectations are named;
- M12 can build the first slice without guessing foundation intent;
- no migrations, provider calls, API/MCP, dashboard, customer data, or strategy storage are introduced.

---

## Recommended Next M11 Batch

Create a closure-readiness review that checks:

```text
Does this foundation spec satisfy M11 allowed work?
Does it avoid broad implementation?
Does it give M12 enough build guidance?
Are any folders safe to create now, or should creation wait for explicit M12 build authorization?
```

If safe, M11 can close by decision record and M12 can activate.

---

## Final Rule

```text
Prepare the workbench.
Do not build the telescope yet.
```
