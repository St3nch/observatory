# The Observatory — Roadmap Rules

Status: draft 1  
Date: 2026-07-07  
Purpose: preserve roadmap memory, control roadmap edits, and force required reading before milestone work.

---

## 1. Roadmap Purpose

The roadmap is the project memory spine.

It is not only a task list. It exists so a future human or LLM can determine:

- what is active now;
- what has already been decided;
- what must be read before work begins;
- what is blocked;
- what is forbidden;
- what belongs to a later milestone;
- what must not be rebuilt from vague memory.

The roadmap must make it difficult for a fresh LLM to freestyle architecture from vibes.

---

## 2. Roadmap Preservation Rules

1. **Never delete milestone history silently.** Completed milestones stay visible or move to a completed section with closure notes.
2. **Never rewrite accepted history as if it always said the new thing.** If direction changes, add an amendment note.
3. **Every milestone must include required reading.** Required reading may be individual files or folders.
4. **Folders listed as required reading must have a `README.md`.** That README must summarize the folder and its important docs.
5. **No milestone starts from memory alone.** The LLM must read the milestone's required docs before planning or implementation.
6. **Every milestone must state explicit non-goals.** This prevents scope creep and accidental system birth.
7. **Every milestone must state gates before implementation.** If rights, retention, spend, schema, test, or boundary gates are unresolved, implementation stops.
8. **Every milestone must produce durable artifacts.** No progress by conversation mist.
9. **Research topics must stay tied to the milestone or blocker they resolve.** No random research swamp.
10. **Roadmap edits must be small, reviewable, and boring.** Boring means we did not accidentally build a doctrine casino.

---

## 3. Roadmap Edit Classes

### Class A — Maintenance Edit

Examples:

- typo fixes;
- path fixes;
- formatting cleanup;
- adding a missing link that does not change meaning.

Allowed without owner ruling.

### Class B — Clarification Edit

Examples:

- clarifying milestone scope;
- adding required reading;
- adding a blocker;
- adding acceptance criteria;
- adding an explicit non-goal that preserves existing doctrine.

Allowed, but the edit must include a short change note.

### Class C — Scope Change

Examples:

- adding a milestone;
- reordering milestones;
- changing a milestone's goal;
- moving implementation earlier/later;
- adding a new layer or system boundary;
- admitting a new provider or capture instrument.

Requires explicit owner approval.

### Class D — Doctrine Change

Examples:

- changing Observatory boundary law;
- reviving killed concepts;
- allowing customer first-party data storage in Observatory;
- allowing direct SQL or credentials to agents;
- weakening hammer-test requirements;
- permitting stored strategy/recommendation records.

Requires explicit owner ruling and must be recorded in `01-harvest-register.md` or `decisions/` once that folder is earned.

---

## 4. Required Milestone Format

Every milestone in `ROADMAP.md` must use this structure:

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

## 5. Required Reading Rules

Required reading may point to:

- specific files;
- folders;
- prior milestone outputs;
- research docs;
- contracts;
- registers;
- decision docs;
- external local repo paths.

If a folder is listed, that folder must contain `README.md` with:

- folder purpose;
- what belongs there;
- what does not belong there;
- file index;
- summary of each important file;
- authority/status of each important file;
- recommended reading order;
- related roadmap milestones;
- notes for LLMs.

A milestone must not say "read the folder" unless the folder tells the LLM what the folder means. No lazy treasure maps.

---

## 6. Required Reading Proof

Before doing milestone work, an LLM must summarize:

1. which required docs it read;
2. the boundaries that affect the milestone;
3. what the milestone is not allowed to change;
4. open blockers;
5. the proposed next action.

This summary belongs in the working response or the milestone work note. No silent reading theater.

---

## 7. Implementation Gate Rule

Implementation means any of the following:

- schema creation;
- migrations;
- production code;
- provider/API calls;
- paid capture;
- MCP/API tool implementation;
- data persistence behavior;
- customer-facing output behavior.

Implementation may not start until the milestone's gates are satisfied.

Planning docs may be created earlier, but must clearly label themselves as planning and must not imply approval.

---

## 8. Final Rule

```text
Roadmap memory beats LLM memory.
```

If the roadmap and the chat disagree, stop and reconcile before working.
