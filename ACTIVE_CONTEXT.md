# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-12

---

## Current Phase

The Observatory is in:

```text
M20 Observatory v1 acceptance planning
```

M19 is closed after acceptance of repository-only protection and recovery rulings plus a bounded owner-local full-history Git bundle and disposable restore proof. Source and restored HEAD matched, Git integrity passed, prohibited ignored roots were absent, and 184 restored tests passed. Encryption/off-machine recovery remains unproven and explicitly blocked. M20 is active for acceptance review only; no production deployment or implementation widening is authorized.

---

## Active Milestone

```text
M20 - Observatory v1 Acceptance
```

M0, M0.1, and M1 through M19 are complete and committed.

---

## Current Task

Review Observatory v1 against accepted doctrine, contracts, hammer results, bounded evidence behavior, consumer usefulness, recovery proof, known limitations, and deferred capabilities.

Current M20 work is allowed to:

- reconcile doctrine and boundary conformance;
- review accepted proof and hammer evidence;
- assess bounded consumer usefulness;
- preserve known limitations and deferred capabilities;
- issue an explicit v1 accept/reject recommendation;
- propose post-v1 roadmap work only after acceptance.

M20 does not authorize production deployment, provider execution, recurring capture, live Postgres/schema/migrations, customer data, report generation, production API/MCP, credentials or secret transfer, cloud backup upload, automatic backup jobs, destructive cleanup, strategy storage, or recommendation storage.

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

Active:

- M20 - Observatory v1 Acceptance

Next after M20:

```text
No post-v1 milestone is activated until the owner accepts or rejects v1 and approves a new roadmap.
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred at M2: contracts/ until M7, hammers/ until M8
```

Folder state update 2026-07-10: `contracts/` exists and all planned M7 contracts are drafted/indexed. `hammers/` exists and M8 hammer planning outputs are drafted/indexed. `audits/` is governed by owner ruling (`decisions/2026-07-07-audits-folder.md`).
