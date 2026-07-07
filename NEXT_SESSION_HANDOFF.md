# The Observatory — Next Session Handoff

Status: active  
Last updated: 2026-07-07  
Purpose: short continuation note for the next human/LLM session.

---

## Current State

The repo is being converted into an LLM-first project workspace.

The immediate work is not database design. The immediate work is root navigation and roadmap preservation so future LLMs do not forget the planning docs or accidentally skip boundaries.

---

## Files Added In Current Pass

```text
ROADMAP_RULES.md
REPO_MAP.md
LLM_START_HERE.md
ACTIVE_CONTEXT.md
ROADMAP.md
FOLDER_README_TEMPLATE.md
NEXT_SESSION_HANDOFF.md
```

`README.md` still needs to be updated to point to the new root read path if that has not happened yet.

---

## Active Milestone

```text
M0 — LLM-First Repo Navigation and Roadmap Preservation
```

Goal: make the repo self-explaining before deeper roadmap content, research gates, schema, MCP, or provider work.

---

## Most Important Boundaries

- Observatory stores observations, not strategy.
- Connected LLM interprets at read time.
- Accepted conclusions promote out to Kaizen / Neon Ronin / SearchClarity / another owner-approved destination.
- Customer first-party data is not stored here.
- LLMs and agents do not get SQL or credentials.
- Typed API/MCP tools are the future access door.
- Hammer tests are a hard gate.
- Roadmap required reading is mandatory.
- Folders listed as required reading must have README summaries.

---

## Immediate Next Steps

1. Update `README.md` to point to `LLM_START_HERE.md`, `ROADMAP.md`, `ROADMAP_RULES.md`, `REPO_MAP.md`, and `ACTIVE_CONTEXT.md`.
2. Review whether Claude-created docs in project knowledge need to be added to the GitHub repo.
3. Draft or refine M1 roadmap content.
4. Create folder README files only when folders are actually used by roadmap required reading.
5. Do not start schema work yet.

---

## Open Questions

- Should `CLAUDE_START_HERE.md` remain model-specific, or should `LLM_START_HERE.md` fully replace it?
- Should `GLOSSARY.md`, `DOC_STATUS.md`, and `FORBIDDEN_PATTERNS.md` be added during M0 or postponed to M1/M2?
- Which uploaded project-knowledge docs are not yet in the GitHub repo?
- What exact milestone sequence should M1 produce?

---

## Warning To Next LLM

Do not turn the roadmap into implementation permission.

The roadmap is currently being built so implementation can happen safely later.

If you are about to create schema, write provider integration code, make API calls, build an MCP server, or design a dashboard, stop. You are probably ahead of the roadmap.
