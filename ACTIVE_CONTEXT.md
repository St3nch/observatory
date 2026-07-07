# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-07

---

## Current Phase

The Observatory is in:

```text
knowledge-doc preservation / pre-boundary-reconciliation planning
```

This is still not implementation authorization.

---

## Active Milestone

```text
M3 - Knowledge Doc Preservation and Planning-Inbox Expansion
```

M0, M0.1, M1, and M2 are complete and committed.

---

## Current Task

Execute M3 as bounded knowledge-doc preservation work.

Current M3 work is allowed to:

- add the classified Claude/project knowledge docs to `planning-inbox/`;
- label them as planning, research agenda, or advisory context;
- update `planning-inbox/README.md`;
- preserve the docs without promoting them into authority.

M3 is about making important source material repo-visible. It is not implementation, boundary rewriting, research execution, or schema work.

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

Active:

- M3 - Knowledge Doc Preservation and Planning-Inbox Expansion

Next after M3:

```text
M4 - Boundary Reconciliation and Doctrine Hardening
```

M2 folder ruling completed:

```text
Created: decisions/, archive/, research/
Deferred: contracts/ until M7, hammers/ until M8
```
