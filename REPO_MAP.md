# Repo Map — The Observatory

Status: authority
Authority: repository navigation
Purpose: explain what goes where and prevent random-folder archaeology

---

## Purpose

This file explains the intended layout of The Observatory repo.

Fresh LLMs must use this file before creating files or proposing folder structure changes.

Do not create random folders from vibes. That is how repos turn into haunted filing cabinets.

---

## Root Files

| File | Purpose | Authority label |
|---|---|---|
| `README.md` | Public entrypoint and LLM-first read path pointer | authority |
| `LLM_START_HERE.md` | Model-neutral first read file for LLMs | authority |
| `ACTIVE_CONTEXT.md` | Current phase, active milestone, current non-goals | authority |
| `ROADMAP.md` | Roadmap operating document and milestone memory | authority |
| `ROADMAP_RULES.md` | Rules for roadmap edits, required reading, and gates | authority |
| `REPO_MAP.md` | Repository layout and placement rules | authority |
| `FOLDER_README_TEMPLATE.md` | Template for folder README files | contract |
| `NEXT_SESSION_HANDOFF.md` | Current handoff for fresh sessions | authority |
| `00-project-overview.md` | Project identity, goal, telescope rule, relationships | authority |
| `01-harvest-register.md` | Inherited concepts and keep/adapt/kill/defer dispositions | authority |
| `02-boundaries.md` | Boundary law and anti-drift rules | authority |
| `.gitignore` | Git ignore rules | maintenance |
| `.gitattributes` | Git text normalization rules to reduce cross-tool line-ending noise | maintenance |

---

## Current Folders

| Folder | Purpose | Current status |
|---|---|---|
| `planning-inbox/` | Working notes, triage, historical/model-specific context, unpromoted planning material | active working area |
| `decisions/` | Accepted owner/project decisions and decision templates | active authority-support folder |
| `archive/` | Superseded, historical, or model-specific material retained for context | active archive folder |
| `research/` | Research gate specs and source-grounded research outputs | active; M6 research corpus complete (RG1–RG13 + deep-research backlog); feeds M7 contracts |
| `audits/` | Audit reports preserved as planning input / advisory context, never authority | active; earned by owner ruling 2026-07-07 (`decisions/2026-07-07-audits-folder.md`) |
| `contracts/` | Non-schema evidence-behavior contracts and contract template | active as of M7; earned per M2 decision's deferred-until-M7 ruling |
| `hammers/` | Hammer-test matrix and hostile-path acceptance-gate planning | active as of M8; earned per M2 decision's deferred-until-M8 ruling |

`planning-inbox/` is not authority. It stores useful material before promotion, pruning, or rejection.

---

## Planned Folder Layout

These folders are not automatically approved for creation. Create them only when the roadmap says the folder is earned.

| Planned folder | Intended purpose | Gate |
|---|---|---|
| `providers/` | Provider admission notes and provider-specific plans | provider planning milestone |
| `capture/` | CapturePackage, capture recipe, raw archive planning | capture planning milestone |
| `schemas/` | Schema design docs only, not migrations | schema planning milestone |

Do not create implementation folders, migrations, app scaffolds, dashboards, or MCP code until the roadmap explicitly opens that gate.

---

## Authority Labels

Use these labels in document headers when practical.

| Label | Meaning |
|---|---|
| authority | Current project law or required operating context |
| contract | A binding format, interface, template, or procedure once accepted |
| research | Source-grounded investigation; informs decisions but is not itself law |
| planning | Proposed structure, sequence, or design not yet binding |
| working note | Useful scratch/planning material; not authority |
| draft | Incomplete or not yet accepted |
| deferred | Owned future concern; no implementation or schema yet |
| killed | Explicitly rejected; must not re-enter under a new name |
| superseded | Replaced by newer authority but preserved for history |

When in doubt, label a new planning document `working note` or `draft`, not `authority`. Authority is earned, not assumed.

---

## What Goes Where

### Root

Root is for current operating documents that a fresh LLM must understand quickly.

Allowed at root:

- onboarding
- active context
- roadmap and roadmap rules
- repo map
- project overview
- harvest/boundary authority docs
- handoff
- templates used repo-wide

Not allowed at root without approval:

- random research dumps
- provider notes
- schema sketches
- implementation scratch files
- model-specific instructions when model-neutral alternatives exist

### `planning-inbox/`

Use for:

- working notes
- rough planning material
- Claude/GPT review notes
- unpromoted ideas
- deep research prompts
- historical/model-specific context

Do not use for:

- final authority
- hidden decisions
- schema implementation
- provider credentials
- customer data
- raw provider payloads

---

## Folder README Requirement

Any folder listed as required reading in a roadmap milestone must contain a `README.md`.

That README must summarize what each important document in the folder is for.

Use `FOLDER_README_TEMPLATE.md`.

If a folder has no README, do not list the folder as required reading. List exact files instead.

---

## Notes for LLMs

Before creating a file, answer:

1. Does this belong at root or in an existing folder?
2. Is this authority, contract, research, planning, or working note?
3. Is there an existing file that should be updated instead?
4. Does the roadmap currently allow this work?
5. Would this accidentally promote strategy/recommendation/customer data into Observatory?

If the answer smells like raccoon architecture, stop.
