# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
implementation foundation
```

This is implementation foundation only. It is still not provider, API/MCP, dashboard, customer workflow, customer-data, provider-spend, or broad implementation authorization.

---

## Active Milestone

```text
M11 - Implementation Foundation
```

M0, M0.1, M1, M2, M3, M4, M5, M6, M7, M8, M9, and M10 are complete and committed.

---

## Current Task

Execute M11 as bounded implementation foundation work for the accepted C2 first slice only.

Current M11 work is allowed to:

- plan implementation foundation for the Controlled Public Manual Observation Package only;
- define repo/skeleton needs if still required;
- define test harness strategy;
- define migration-folder expectations without running migrations;
- define fixture/sample design expectations;
- define initial hammer-test scaffold expectations;
- define local configuration patterns without secrets.

M10 is closed by `decisions/2026-07-10-m10-schema-planning-closure.md`. The accepted schema planning target is the Controlled Public Manual Observation Package. M11 now prepares the implementation foundation before the first slice build can begin.

M11 does not authorize provider purchases, paid pulls, provider admission, provider calls, API/MCP exposure, dashboard work, customer-data handling, capture runner work, automated recurring capture, broad implementation, or strategy/recommendation storage.

---

## Immediate Non-Goals

Do not start:

- running migrations
- broad Postgres implementation
- DataForSEO pulls
- Ahrefs work
- Semrush work
- provider purchases
- MCP implementation
- API implementation
- dashboard or operator console work
- customer data handling
- strategy storage
- recommendation storage
- provider admission
- capture runner implementation
- automated recurring capture

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

Active:

- M11 - Implementation Foundation

Next after M11:

```text
M12 - First Evidence Slice Build
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
