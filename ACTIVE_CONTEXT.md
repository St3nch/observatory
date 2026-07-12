# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
schema planning only
```

This is schema planning only. It is still not migrations, implementation, provider, API/MCP, dashboard, customer workflow, or customer-data authorization.

---

## Active Milestone

```text
M10 - Schema Planning Only
```

M0, M0.1, M1, M2, M3, M4, M5, M6, M7, M8, and M9 are complete and committed.

---

## Current Task

Execute M10 as bounded schema planning work for the accepted first evidence slice only.

Current M10 work is allowed to:

- plan logical schema for the Controlled Public Manual Observation Package only;
- define table responsibilities at planning level;
- map schema concepts to M7 contracts and M8 hammers;
- define migration expectations without running migrations;
- define anti-pattern checks for strategy/recommendation/customer-data leakage;
- define evidence/query examples needed for later M11/M12 planning.

M9 is closed by `decisions/2026-07-10-m9-first-slice-closure.md`. The accepted first slice is the Controlled Public Manual Observation Package. M10 now plans schema for that slice before implementation can begin.

M10 does not authorize provider purchases, paid pulls, provider admission, migrations, implementation, API/MCP implementation, dashboard work, customer-data handling, capture runner work, automated recurring capture, or strategy/recommendation storage.

---

## Immediate Non-Goals

Do not start:

- running migrations
- Postgres implementation
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

Active:

- M10 - Schema Planning Only

Next after M10:

```text
M11 - Implementation Foundation
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
