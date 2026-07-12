# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-12

---

## Current Phase

The Observatory is in:

```text
M19 hardening, backup, recovery, and operations planning
```

M18 is closed after acceptance of a bounded recurring watch-panel policy and an explicit rejection of recurring capture execution for Observatory v1. M19 is active for planning only: backup posture, restore-proof design, audit-log expectations, secret-exposure checks, retention-cleanup proof, operational runbooks, and operational-risk documentation. No scheduler, recurring capture, provider execution, autonomous spend, credentials, Postgres, physical schema, migrations, production API/MCP, customer data, reports, deployment, or production integration is authorized.

---

## Active Milestone

```text
M19 - Hardening, Backup, Recovery, and Operations
```

M0, M0.1, and M1 through M18 are complete and committed.

---

## Current Task

Begin M19 with repo-first reconciliation of the existing evidence slice, raw archive/hash expectations, retention rules, hammer results, M18 no-execution posture, and current operational risks before any hardening implementation.

Current M19 work is allowed to:

- define backup scope, frequency, encryption, and retention posture;
- define a disposable restore-proof procedure;
- define audit-log and operation-evidence expectations;
- define secret-exposure inventory and checks;
- define retention-cleanup and purge-proof procedures;
- define bounded operational runbooks and risk registers;
- propose exact implementation or proof tasks only after separate owner gates.

M19 does not authorize production deployment, live database creation, Postgres schema or migrations, provider execution, recurring capture, credentials or secret transfer, customer data, report generation, production API/MCP, destructive cleanup, automatic backup jobs, or broad operational automation.

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
- M18 - Recurring Watch Panel Planning

Active:

- M19 - Hardening, Backup, Recovery, and Operations

Next after M19:

```text
Follow the accepted roadmap sequence; no later milestone is activated by this context file.
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
