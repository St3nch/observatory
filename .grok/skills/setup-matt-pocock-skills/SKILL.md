---
name: setup-matt-pocock-skills
description: Configure this repo for the engineering skills — set up its issue tracker, triage label vocabulary, and domain doc layout. Run once before first use of the other engineering skills.
disable-model-invocation: true
---

# Setup Matt Pocock's Skills

## Observatory mode

Observatory's setup is already decided. For this repository, do **not** execute the generic
scaffolding process below.

### Preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/setup-matt-pocock-skills/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. This skill must not write in Observatory mode.

### Validate only

Confirm each approved project skill exists under `.grok/skills/<name>/SKILL.md`:

- `setup-matt-pocock-skills`
- `implement`
- `tdd`
- `code-review`
- `diagnosing-bugs`
- `research`
- `domain-modeling`
- `codebase-design`
- `handoff`
- `wait-what`
- `grilling`
- `grill-with-docs`
- `to-spec`
- `to-tickets`
- `wayfinder`
- `prototype`
- `writing-for-agents`

Also validate:

- `AGENTS.md` routes authority through `VISION.md`, `VOCABULARY.md`, the decision
  registers, the relevant ticket under `tickets/`, applicable ADRs under `docs/adr/`,
  and accepted specs under `docs/specs/` when named.
- Artifact conventions: drafts in `docs-temp/`; tickets in `tickets/`; no issue tracker.
- No parallel `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/`, triage configuration, or
  `.scratch/` local issue system was created.
- `skills-lock.json` remains installer provenance only (no invented schema). Adapted
  skills must not be blindly overwritten by a future skills update — git history is the
  adaptation record.

Report discrepancies to the Project Steward. Do not ask setup questions or write files.
The remaining upstream process is reference material for other repositories, not steps.

---

## Upstream process (do not run here)

Scaffold the per-repo configuration that the engineering skills assume elsewhere:

- **Issue tracker** — GitHub by default; local markdown also supported upstream
- **Triage labels** — five canonical triage roles
- **Domain docs** — `CONTEXT.md` and ADRs

In other repositories this skill explores, confirms, and writes `docs/agents/*`. For
Observatory, stop after validation. Seed templates in this folder
(`issue-tracker-*.md`, `domain.md`, `triage-labels.md`) are upstream reference only.
