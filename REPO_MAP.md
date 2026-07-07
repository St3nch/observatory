# The Observatory — Repo Map

Status: draft 1  
Date: 2026-07-07  
Purpose: tell humans and LLMs what goes where in this repo.

---

## 1. Map Rule

The repo must explain itself.

A fresh LLM should be able to land in the root, read the root onboarding files, and know:

- what the project is;
- what files to read first;
- where each kind of work belongs;
- which docs are authority vs planning vs working notes;
- what must not be created here.

No repo archaeology. No guessing. No vibes-based raccoon architecture.

---

## 2. Root Files

| File | Purpose | Status |
|---|---|---|
| `README.md` | Human-facing overview and quick start. | active root overview |
| `LLM_START_HERE.md` | First file every LLM should read before work. | required |
| `REPO_MAP.md` | This file; map of where project knowledge belongs. | required |
| `ROADMAP.md` | Milestone control document. | required |
| `ROADMAP_RULES.md` | Rules for preserving/editing/executing the roadmap. | required |
| `ACTIVE_CONTEXT.md` | Current active milestone, blockers, and next action. | required |
| `NEXT_SESSION_HANDOFF.md` | Session-to-session continuation note. | required |
| `00-project-overview.md` | Identity, purpose, telescope rule, relationships. | authority draft |
| `01-harvest-register.md` | Decision-shaped inheritance register. | authority draft |
| `02-boundaries.md` | Boundary law: in/out, rights, scope, anti-drift. | authority draft |

---

## 3. Current Root Reading Order

For a fresh LLM:

```text
README.md
LLM_START_HERE.md
ACTIVE_CONTEXT.md
ROADMAP.md
ROADMAP_RULES.md
REPO_MAP.md
00-project-overview.md
01-harvest-register.md
02-boundaries.md
NEXT_SESSION_HANDOFF.md
```

Then read the milestone-specific required reading from `ROADMAP.md`.

---

## 4. Folder Rules

Every major folder must contain a `README.md` before it is used as milestone required reading.

Folder README format:

```text
# Folder Name

## Purpose

## What belongs here

## What does not belong here

## Reading order

## File index

| File | Status | Authority | Summary |
|---|---|---|---|

## Related roadmap milestones

## Notes for LLMs
```

If a folder lacks a README, a milestone may link individual files inside it, but may not list the folder as required reading.

---

## 5. Planned Folder Layout

```text
C:\dev\observatory\

  README.md
  LLM_START_HERE.md
  REPO_MAP.md
  ROADMAP.md
  ROADMAP_RULES.md
  ACTIVE_CONTEXT.md
  NEXT_SESSION_HANDOFF.md
  00-project-overview.md
  01-harvest-register.md
  02-boundaries.md

  docs\
    README.md
    boundaries\
      README.md
    architecture\
      README.md
    operations\
      README.md

  research\
    README.md
    dataforseo\
      README.md
    geo-ai-citation\
      README.md
    serp-weakness\
      README.md
    provider-comparison\
      README.md
    marketplace-evidence\
      README.md

  contracts\
    README.md
    capture-package\
      README.md
    evidence-id\
      README.md
    mcp-tools\
      README.md
    query-panels\
      README.md
    rights-retention\
      README.md

  schema\
    README.md

  testing\
    README.md
    hammer\
      README.md

  proofs\
    README.md

  planning-inbox\
    README.md

  decisions\
    README.md

  archive\
    README.md
```

This layout is planned, not fully built. Create folders only when needed by the active roadmap milestone.

---

## 6. What Goes Where

### Root

Project identity, onboarding, roadmap, active context, and boundary authority.

Do not dump working notes in root.

### `planning-inbox/`

Early notes, triage, rough ideas, and non-authoritative exploration.

Everything here must be treated as working material unless promoted elsewhere.

### `docs/`

Stable explanatory docs that are not contracts, research outputs, tests, or roadmap control files.

### `research/`

Research outputs that answer blockers or support milestone decisions.

Research docs must identify which milestone/blocker they inform.

### `contracts/`

Precise shapes and rules for future system behavior: capture packages, evidence IDs, MCP tool responses, query panels, rights/retention vocabularies.

Contracts are stronger than working notes, but do not authorize implementation unless the roadmap gate says so.

### `schema/`

Schema designs, migrations, family maps, and forbidden schema patterns.

Schema work starts only after research and contract gates are satisfied.

### `testing/`

Test doctrine, hammer matrix, hostile-path cases, acceptance test plans.

Hammer tests are a hard gate, not decoration.

### `proofs/`

Small end-to-end proofs: sample evidence packs, report-section proofs, provider disagreement proofs, first evidence slice proof.

### `decisions/`

Earned decision records for changes to project law. Do not create decision ceremony until friction earns it.

### `archive/`

Superseded material preserved for history. Archived docs must not be treated as current authority.

---

## 7. Authority Labels

Use these labels in docs and folder indexes:

| Label | Meaning |
|---|---|
| authority | Current project law or boundary. |
| contract | Precise rule/shape for later implementation. |
| research | Research output; informs decisions. |
| planning | Directional but not implementation approval. |
| working note | Rough/non-authoritative; must not be treated as law. |
| draft | Current but not accepted as final. |
| deferred | Owned future concern; no tables/code yet. |
| killed | Explicitly forbidden from re-entering under a new name. |
| superseded | Replaced by newer doc; historical only. |

---

## 8. LLM Notes

Before creating or moving files, check this map.

If the right location is unclear, stop and propose placement. Do not create random folders because the names feel cool.

If a doc could change boundary law, roadmap scope, or implementation gates, it needs owner approval before being treated as accepted.

---

## Final Rule

```text
The repo map is the anti-amnesia layer.
```
