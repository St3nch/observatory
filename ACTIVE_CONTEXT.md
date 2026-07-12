# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
first evidence slice definition
```

This is still not schema, provider, API/MCP, dashboard, customer workflow, or implementation authorization.

---

## Active Milestone

```text
M9 - First Evidence Slice Definition
```

M0, M0.1, M1, M2, M3, M4, M5, M6, M7, and M8 are complete and committed.

---

## Current Task

Execute M9 as bounded first evidence slice definition work.

Current M9 work is allowed to:

- compare first-slice candidates;
- choose the smallest useful evidence slice;
- name applicable hammers from H1-H22;
- name non-applicable or deferred hammers and why;
- name M10 schema-planning gates;
- name M12 implementation-execution gates;
- reject candidates that require provider spend, customer private data, marketplace ambiguity, dashboard work, API/MCP implementation, or strategy/recommendation storage too early.

M8 is closed by `decisions/2026-07-10-m8-closure.md`. The hammer matrix lives at `hammers/hammer-matrix-v0-1.md`, the gate policy lives at `hammers/acceptance-gate-policy-v0-1.md`, and the M8 review lives at `planning-inbox/m8-hammer-planning-review.md`. M9 now selects the first evidence slice before schema, provider admission, or implementation can begin.

M9 does not authorize provider purchases, paid pulls, provider admission, schema work, migrations, API/MCP implementation, dashboard work, customer-data handling, capture runner work, automated recurring capture, or strategy/recommendation storage.

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

Active:

- M9 - First Evidence Slice Definition

Next after M9:

```text
M10 - Schema Planning Only
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
