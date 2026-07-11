# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
hammer matrix and acceptance-gate planning
```

This is still not schema, provider, API/MCP, dashboard, customer workflow, or implementation authorization.

---

## Active Milestone

```text
M8 - Hammer Matrix and Acceptance Gates
```

M0, M0.1, M1, M2, M3, M4, M5, M6, and M7 are complete and committed.

---

## Current Task

Execute M8 as bounded hammer matrix and acceptance-gate planning work.

Current M8 work is allowed to:

- create earned `hammers/` folder/index if M8 work proceeds;
- define hammer categories from the M7 contract draft set;
- draft hostile-path tests and acceptance gates;
- map hammer tests to contract sections and owner-ruling blockers;
- preserve fail-closed behavior for unresolved rulings;
- identify which hammers gate M9 through later implementation/admission milestones.

M7 is closed by `decisions/2026-07-10-m7-closure.md`. All thirteen planned M7 contracts are drafted and indexed in `contracts/README.md`, and the M7 draft-set review lives at `planning-inbox/m7-contract-draft-set-review.md`. M8 now turns those contracts into testable hammers before schema, provider admission, or implementation can begin.

M8 does not authorize provider purchases, paid pulls, provider admission, schema work, migrations, API/MCP implementation, dashboard work, customer-data handling, capture runner work, automated recurring capture, or strategy/recommendation storage.

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

Active:

- M8 - Hammer Matrix and Acceptance Gates

Next after M8:

```text
M9 - First Evidence Slice Definition
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`). `hammers/` is now eligible to be created during M8 work.
