# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
provider admission and controlled pull planning
```

This is provider-admission planning only. It is still not provider calls, provider purchases, paid pulls, API/MCP exposure, dashboard, customer workflow, customer-data, marketplace scraping, recurring capture, or broad implementation authorization.

---

## Active Milestone

```text
M13 - Provider Admission and Controlled Pull Plan
```

M0, M0.1, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, M11, and M12 are complete and committed.

---

## Current Task

Execute M13 as bounded provider admission and controlled pull planning only.

Current M13 work is allowed to:

- draft provider admission plan;
- confirm rights/retention/cost gate requirements from existing research and contracts;
- define controlled pull recipe;
- define cost ceiling;
- define stop conditions;
- define raw payload handling plan;
- define no-customer-data posture;
- define no-recurring-capture posture;
- define no-dashboard/report/API/MCP exposure posture.

M12 is closed by `decisions/2026-07-10-m12-first-slice-closure.md`. The bounded local C2 first evidence slice is accepted. M13 now plans provider admission and controlled pull gates only.

M13 does not authorize provider purchases, paid pulls, provider admission execution, provider calls, API/MCP exposure, dashboard work, customer-data handling, marketplace scraping, browser-extension capture, capture runner work, automated recurring capture, broad implementation, or strategy/recommendation storage.

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

Active:

- M13 - Provider Admission and Controlled Pull Plan

Next after M13:

```text
M14 - Typed Read API / MCP Contract and Prototype
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
