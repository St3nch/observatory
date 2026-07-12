# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-12

---

## Current Phase

The Observatory is in:

```text
M15 SearchClarity proof-workflow planning
```

M14 is closed after acceptance of the typed-read contract, direct review of the named Hermes lineage inputs, implementation of one bounded fixture-backed in-memory prototype, and owner-local proof that all 141 tests pass. M15 is active for planning only: SearchClarity consumer-boundary reconciliation, evidence-pack-to-report-support requirements, report-safe reference boundaries, no-storage overlay decision points, claim-safety propagation, and hostile-path acceptance criteria. No customer records, customer-private storage, report generation, production integration, Postgres, schema, migration, provider execution, or production API/MCP is authorized.

---

## Active Milestone

```text
M15 - SearchClarity Proof Workflow
```

M0, M0.1, and M1 through M14 are complete and committed.

---

## Current Task

Begin M15 with repo-first consumer-boundary and contract reconciliation before any proof implementation.

Current M15 work is allowed to:

- reconcile the accepted SearchClarity consumer placeholder with the accepted typed-read and consumer-promotion contracts;
- define the evidence-pack-to-report-support workflow without generating customer reports;
- define claim-safety, caveat propagation, report-safe reference, and public-observation scope requirements;
- define customer/private first-party overlay requirements as no-storage read-time inputs only, if needed;
- define how interpretations, recommendations, reports, and accepted conclusions promote out to SearchClarity;
- define hostile-path tests and an exact bounded proof-task proposal;
- route deeper research and owner rulings required before customer-facing proof.

M15 does not authorize customer records in Observatory, customer-private analytics storage, report delivery records, customer-facing report generation, SearchClarity production integration, overlay implementation, Postgres, schema, migrations, provider calls, recurring capture, production API/MCP deployment, strategy storage, recommendation storage, or automatic conclusion promotion.

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

Active:

- M15 - SearchClarity Proof Workflow

Next after M15:

```text
Follow the accepted roadmap sequence; no later milestone is activated by this context file.
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
