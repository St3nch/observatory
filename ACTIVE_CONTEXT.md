# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-12

---

## Current Phase

The Observatory is in:

```text
Observatory v1 accepted at the bounded proof-system ceiling
```

M20 is closed by `decisions/2026-07-12-observatory-v1-acceptance.md`. The accepted v1 is a bounded, local, evidence-only proof system. It is not production-ready or feature-complete. No production deployment, post-v1 implementation, provider expansion, recurring capture, live database work, customer data handling, report generation, production API/MCP, encrypted/off-machine recovery claim, or strategy storage is authorized.

---

## Active Milestone

```text
none
```

M0, M0.1, and M1 through M20 are complete and committed.

---

## Current Task

Preserve the accepted-v1 state and its known-limit/deferred-capability register.

Current work is limited to:

- reading and reviewing accepted v1 evidence;
- correcting factual documentation defects without widening authority;
- preserving proof artifacts and accepted limitations;
- proposing a new roadmap only when the owner explicitly requests one.

No post-v1 milestone, implementation package, production launch, or roadmap expansion is active.

---

## Immediate Non-Goals

Do not start:

- provider calls or new paid pulls
- recurring capture
- production API/MCP exposure
- dashboard or operator console work
- live Postgres/schema/migrations
- customer data handling
- customer-facing reports
- marketplace scraping
- browser-extension capture
- strategy or recommendation storage
- cloud backup upload
- automatic backup jobs
- destructive cleanup
- production deployment

No schema goblin jazz. No provider confetti cannon. No dashboard side quest.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer, such as SearchClarity, Neon Ronin, or Kaizen.

Customer records and customer first-party analytics stay outside Observatory durable storage.

LLMs and agents receive shaped evidence through typed boundaries, not direct SQL access or database credentials.

Provider disagreement is first-class evidence. Proprietary provider scores are provider-attributed testimony, not facts about the web.

Hammer tests are a hard gate for implementation.

Bounded repository recovery is proven. Encrypted/off-machine recovery is not yet proven.

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
- M19 - Hardening, Backup, Recovery, and Operations
- M20 - Observatory v1 Acceptance

Active:

```text
none
```

Post-v1 state:

```text
No post-v1 milestone is active. A new roadmap requires explicit owner approval.
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
