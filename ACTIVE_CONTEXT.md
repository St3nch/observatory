# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-12

---

## Current Phase

The Observatory is in:

```text
M18 recurring watch panel planning
```

M17 is closed after acceptance of the owned telemetry overlay contract and rulings, one bounded synthetic fixture-backed implementation, one corrected false-positive safety test, and owner-local proof that all 184 tests pass. M18 is active for planning only: recurring watch-panel design, cadence policy, budget policy, stop conditions, stale/coverage warnings, and responsible approval-or-rejection criteria. No scheduler implementation, recurring capture execution, autonomous spend, provider calls, broad crawling/scraping, credentials, Postgres, schema, migrations, production API/MCP, customer data, reports, strategy, or production integration is authorized.

---

## Active Milestone

```text
M18 - Recurring Watch Panel Planning
```

M0, M0.1, and M1 through M17 are complete and committed.

---

## Current Task

Begin M18 with repo-first reconciliation of provider admission, cost, rights, recipe, freshness, query-panel, and hammer boundaries before any recurring-capture decision.

Current M18 work is allowed to:

- define watch-panel purpose and bounded subject membership;
- define cadence policy by volatility, freshness, and claim need;
- define budget ceilings, duplicate prevention, and approval gates;
- define stop conditions, failure budgets, and manual review points;
- define stale, incomplete, coverage, and non-synchronous warnings;
- define an explicit approve/reject recommendation for recurring capture planning.

M18 does not authorize scheduler implementation, recurring capture execution, provider calls, autonomous spend, credentials, broad crawling or scraping, customer data, customer reports, Postgres, schema, migrations, production API/MCP deployment, production integrations, strategy storage, recommendation storage, or automatic conclusion promotion.

---

## Immediate Non-Goals

Do not start:

- provider calls
- DataForSEO pulls
- Ahrefs work
- Semrush work
- provider purchases
- provider admission execution
- API/MCP exposure
- dashboard or operator console work
- customer data handling
- customer-facing reports
- marketplace scraping
- browser-extension capture
- strategy storage
- recommendation storage
- recurring capture
- broad implementation beyond C2

No schema goblin jazz. No provider confetti cannon. No dashboard side quest.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer, such as SearchClarity, Neon Ronin, or Kaizen.

Customer records stay outside Observatory.

Customer first-party analytics stay outside Observatory unless a future explicit owner ruling changes the law. Current expected handling is read-time overlay only.

LLMs and agents must not receive direct SQL access or database credentials. Future access is typed API / MCP read tools only.

Provider disagreement is first-class evidence. Proprietary provider scores are observations of provider model output, not facts about the web.

Hammer tests are a hard gate for implementation.

---

## Current Completion State

Closed:

- M0 - LLM-first repo navigation and roadmap preservation
- M0.1 - Knowledgebase-to-repo reconciliation and candidate decision pass
- M1 - Roadmap Content Draft and Milestone Sequencing
- M2 - Folder Structure and Folder README Indexes
- M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
- M4 - Boundary Reconciliation and Doctrine Hardening
- M5 - Research Gate Plan
- M6 - Research Gate Execution
- M7 - Core Contract Planning
- M8 - Hammer Matrix and Acceptance Gates
- M9 - First Evidence Slice Definition
- M10 - Schema Planning Only
- M11 - Implementation Foundation
- M12 - First Evidence Slice Build
- M13 - Provider Admission and Controlled Pull Plan
- M14 - Typed Read API / MCP Contract and Prototype
- M15 - SearchClarity Proof Workflow
- M16 - Provider Cross-Check Proof
- M17 - Owned Telemetry Overlay Proof

Active:

- M18 - Recurring Watch Panel Planning

Next after M18:

```text
Follow the accepted roadmap sequence; no later milestone is activated by this context file.
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
