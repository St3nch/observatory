# The Observatory — Active Context

Status: active  
Last updated: 2026-07-07  
Purpose: short current-state file for humans and LLMs before starting work.

---

## Current Phase

The project is in **early planning / doctrine / roadmap shaping**.

Current work target:

```text
Build the LLM-first repo navigation and roadmap preservation system.
```

This is not schema work yet.

---

## Active Work Item

Create and connect root onboarding/control files:

```text
LLM_START_HERE.md
REPO_MAP.md
ROADMAP_RULES.md
ROADMAP.md
ACTIVE_CONTEXT.md
NEXT_SESSION_HANDOFF.md
```

Also establish folder README rules so future milestone required-reading paths do not become vague.

---

## Immediate Non-Goals

Do not start:

- PostgreSQL schema design;
- migrations;
- DataForSEO pulls;
- Ahrefs/Semrush integration;
- MCP implementation;
- dashboard work;
- customer data handling;
- strategy/recommendation storage;
- cross-scope aggregation.

These are later milestones or deferred candidates.

---

## Current Hard Boundaries

- Observatory stores observations, not conclusions.
- Strategy is compute-on-read unless a future owner ruling creates a governed boundary.
- Customer first-party data is not stored here.
- Typed API/MCP read tools are the only future access door.
- Hammer tests are a hard gate before real schema/API/tool behavior.
- Provider data is testimony, not truth.
- Roadmap required reading must be explicit.

---

## Current Open Questions

- Final root file set: keep both `LLM_START_HERE.md` and any model-specific start files, or consolidate model-specific files into this general LLM entrypoint?
- Exact first roadmap milestone names and order.
- Which existing Claude-created docs should move from project knowledge into the GitHub repo, if not already present.
- Whether to add `GLOSSARY.md`, `DOC_STATUS.md`, and `FORBIDDEN_PATTERNS.md` in this initial root-control pass.

---

## Recommended Next Action

1. Finish root control files.
2. Update `README.md` to point to the new onboarding path.
3. Draft `ROADMAP.md` as a roadmap operating document first, not a schema plan.
4. Add folder README template/rule before listing any folder as required milestone reading.

---

## Notes For The Next LLM

You are not here to build the Observatory database yet.

You are here to make sure the repo cannot forget itself.

If you are about to create schema, provider calls, or implementation code, stop and check the roadmap gates.
