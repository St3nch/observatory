# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-07

---

## Current Phase

The Observatory is in:

```text
research gate planning
```

This is still not implementation authorization.

---

## Active Milestone

```text
M5 - Research Gate Plan
```

M0, M0.1, M1, M2, M3, and M4 are complete and committed.

---

## Current Task

Execute M5 as bounded research-gate planning work.

Current M5 work is allowed to:

- define research gate questions;
- define output docs and required sources for each gate;
- define completion rules;
- define M6 execution order;
- preserve M4 boundary constraints in every gate.

M5 is about planning research, not executing it. It is not provider work, paid pulls, schema work, migrations, API/MCP implementation, dashboard work, customer-data handling, or strategy/recommendation storage.

---

## Immediate Non-Goals

Do not start:

- schema design
- migrations
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
- research execution
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

Active:

- M5 - Research Gate Plan

Next after M5:

```text
M6 - Research Gate Execution
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred: contracts/ until M7, hammers/ until M8
```
