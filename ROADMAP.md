# The Observatory — Roadmap

Status: draft 1  
Date: 2026-07-07  
Purpose: milestone control document for planning, research, implementation, tests, and completion of The Observatory.

---

## 1. Roadmap Role

This roadmap is the project memory spine.

It does not only list work. It controls how work begins:

```text
read required docs
summarize required context
check gates
confirm non-goals
then work
```

If an LLM cannot name the active milestone, required reading, boundaries, gates, and non-goals, it is not ready to act.

Roadmap rules live in `ROADMAP_RULES.md`.

Repo navigation lives in `REPO_MAP.md`.

---

## 2. Active Milestone

Current active milestone:

```text
M0 — LLM-First Repo Navigation and Roadmap Preservation
```

No schema, provider, MCP, dashboard, or implementation work is active yet.

---

## 3. Milestone Status Labels

| Status | Meaning |
|---|---|
| planned | Not started. |
| active | Current work. |
| blocked | Cannot proceed until named blocker is resolved. |
| review | Work produced; needs owner/steward review. |
| accepted | Milestone output accepted. |
| closed | Accepted and closure note recorded. |
| deferred | Owned future work; no action now. |
| killed | Explicitly not happening. |

---

## 4. Milestone Template

Every milestone must use this structure:

```text
# Milestone N — Name

Status:
Owner:
Last updated:
Current state:

## Goal

## Why this milestone exists

## Required reading before work

## Required context summary

## Inputs

## Outputs

## Explicit non-goals

## Gates before implementation

## Acceptance criteria

## Closure note

## Links to follow-up work
```

---

# Milestone 0 — LLM-First Repo Navigation and Roadmap Preservation

Status: active  
Owner: Project owner  
Last updated: 2026-07-07  
Current state: root onboarding/control files being created

## Goal

Make the repo self-explaining for humans and LLMs before deeper planning or implementation begins.

## Why this milestone exists

Planning docs get forgotten over time. Future LLMs need a durable repo map, roadmap rules, active context, and required-reading system so they do not rebuild from memory fog.

## Required reading before work

```text
README.md
00-project-overview.md
01-harvest-register.md
02-boundaries.md
ROADMAP_RULES.md
REPO_MAP.md
ACTIVE_CONTEXT.md
```

## Required context summary

The LLM must understand:

- the Observatory stores observations, not strategy;
- roadmap memory beats LLM memory;
- required reading must be explicit per milestone;
- folders listed as required reading must have README summaries;
- this milestone is about navigation/control, not database design.

## Inputs

- Existing project overview and boundary docs.
- Owner requirement for LLM-first onboarding files.
- Owner requirement for milestone required reading.
- Owner requirement for folder READMEs when folders are listed.

## Outputs

```text
LLM_START_HERE.md
REPO_MAP.md
ROADMAP_RULES.md
ROADMAP.md
ACTIVE_CONTEXT.md
NEXT_SESSION_HANDOFF.md
FOLDER_README_TEMPLATE.md
README.md update
```

## Explicit non-goals

This milestone must not create or approve:

- schema;
- migrations;
- provider pulls;
- paid capture;
- MCP implementation;
- dashboard work;
- customer data handling;
- strategy/recommendation storage;
- cross-scope aggregation.

## Gates before implementation

No implementation is in scope.

Before later implementation milestones can begin, they must have:

- required reading listed;
- boundary summary;
- non-goals;
- gates;
- acceptance criteria.

## Acceptance criteria

- Root onboarding files exist.
- `README.md` points to the LLM-first read path.
- `ROADMAP_RULES.md` defines edit/preservation rules.
- `REPO_MAP.md` explains what goes where.
- `ROADMAP.md` identifies active milestone and required format.
- Folder README rule/template exists.
- A fresh LLM can read root docs and know not to start schema work.

## Closure note

Open.

## Links to follow-up work

- M1 — Roadmap Content Draft and Milestone Sequencing.
- M2 — Folder Structure and Folder README Indexes.
- M3 — Research Gate Planning.

---

# Milestone 1 — Roadmap Content Draft and Milestone Sequencing

Status: planned

## Goal

Draft the real project milestone sequence from planning and research through completed Observatory v1.

## Required reading before work

```text
ROADMAP.md
ROADMAP_RULES.md
REPO_MAP.md
ACTIVE_CONTEXT.md
00-project-overview.md
01-harvest-register.md
02-boundaries.md
strategy-layer-dangerous-design.md
planning-inbox/deep-research-danger-agenda.md
planning-inbox/repo-first-research-triage.md
```

If any listed doc is missing from the repo, stop and resolve placement before continuing.

## Explicit non-goals

Do not start schema or implementation. This milestone sequences work; it does not execute it.

## Acceptance criteria

- Milestones are listed in order.
- Each milestone has required reading.
- Research gates appear before schema gates.
- Hammer-test milestone appears before real implementation.
- MCP/typed read-tool contract appears before MCP implementation.
- Customer/private-data boundary is preserved.

---

# Milestone 2 — Folder Structure and Folder README Indexes

Status: planned

## Goal

Create the minimum folder structure needed by the roadmap, with README files that explain each folder.

## Required reading before work

```text
REPO_MAP.md
ROADMAP_RULES.md
FOLDER_README_TEMPLATE.md
ROADMAP.md
```

## Explicit non-goals

Do not create empty sprawl. Create folders only when they are needed by roadmap milestones or current docs.

## Acceptance criteria

- Every folder used as required reading has a README.
- Every folder README includes purpose, what belongs, what does not belong, file index, reading order, related milestones, and LLM notes.

---

# Milestone 3 — Research Gate Planning

Status: planned

## Goal

Turn the existing danger agenda and repo-first triage into ordered research gates that block or enable later contracts/schema.

## Required reading before work

```text
planning-inbox/deep-research-danger-agenda.md
planning-inbox/repo-first-research-triage.md
strategy-layer-dangerous-design.md
01-harvest-register.md
02-boundaries.md
```

## Explicit non-goals

Do not execute DataForSEO pulls. Do not buy Ahrefs/Semrush. Do not create schema.

## Acceptance criteria

- Research topics are tied to blockers.
- DataForSEO rights/retention is first-class.
- Provider comparison is captured as a research lane.
- Marketplace evidence ceiling is captured.
- GEO/AI citation methodology is captured.

---

## Deferred / Maybe Later

These are not active:

- dashboard/operator console;
- persistent Strategy/IMI storage;
- cross-scope aggregate seismograph;
- embeddings/vector store;
- automated recurring capture;
- customer-facing report automation.

They may be revisited only through roadmap edit rules and owner ruling where required.

---

## Final Rule

```text
Do not start the database until the roadmap has taught the next LLM what the database is allowed to be.
```
