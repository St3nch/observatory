# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-10

---

## Current Phase

The Observatory is in:

```text
first evidence slice build
```

This is first-slice build only. It is still not provider, API/MCP exposure, dashboard, customer workflow, customer-data, provider-spend, marketplace scraping, recurring capture, or broad implementation authorization.

---

## Active Milestone

```text
M12 - First Evidence Slice Build
```

M0, M0.1, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, and M11 are complete and committed.

---

## Current Task

Execute M12 as bounded first evidence slice build work for the accepted C2 slice only.

Current M12 work is allowed to:

- create C2-only build artifacts needed for the first evidence slice;
- create safe non-customer, non-provider, non-marketplace fixtures;
- implement or define fixture-based validation behavior for C2 only;
- create executable hammer tests for the accepted C2 hammer set;
- implement internal evidence identity behavior for C2 only;
- implement raw support manifest/hash behavior if included;
- implement minimum audit-event behavior for C2 consequential transitions;
- run local tests that do not call providers, access customer data, expose API/MCP, or require external services.

M11 is closed by `decisions/2026-07-10-m11-foundation-closure.md`. The accepted first-slice build target is the Controlled Public Manual Observation Package. M12 now builds and tests that slice only.

M12 does not authorize provider purchases, paid pulls, provider admission, provider calls, API/MCP exposure, dashboard work, customer-data handling, marketplace scraping, browser-extension capture, capture runner work, automated recurring capture, broad implementation beyond C2, or strategy/recommendation storage.

---

## Immediate Non-Goals

Do not start:

- provider calls
- DataForSEO pulls
- Ahrefs work
- Semrush work
- provider purchases
- provider admission
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

Active:

- M12 - First Evidence Slice Build

Next after M12:

```text
M13 - Provider Admission and Controlled Pull Plan
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
