---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

Optional side path. Not automatic in the Observatory main chain.

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/prototype/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Do not edit authority, accepted specs, or tickets except to leave a pointer the Steward
   or a draft already allows.
3. Fold validated decisions into durable artifacts only via Steward reconciliation or an
   explicit draft update under `docs-temp/specs/` / ticket draft — never silent authority edit.

## Pick a branch

Identify which question is being answered:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Single shareable
  HTML file with free-play controls and tabbed guided walkthroughs.
- **"What should this look like?"** → [UI.md](UI.md). Several radically different UI
  variations on one route, switchable via URL param and a floating bar.

If the question is ambiguous and the user is unreachable, pick the branch that matches the
surrounding code (backend → logic; page → UI) and state the assumption at the top.

## Rules for both branches

1. **Throwaway and marked as such.** Place near the code it prototypes; name so a casual
   reader sees it is not production.
2. **Trivial to run.** One project command or a double-click HTML file.
3. **No persistence by default.** In-memory state. If the question needs storage, use a
   clearly named scratch DB or local file marked wipe-me.
4. **Skip polish.** No tests, no extra abstractions, only enough error handling to run.
5. **Surface the state** after every action or variant switch.
6. **Capture the verdict.** Record the question and answer in the session and optionally
   in `docs-temp/` or a throwaway branch. Point a draft spec or ticket at that
   verdict when the Steward wants it retained. Keep main free of unvalidated prototype code.

## Completion

The design question has a concrete answer. Validated decisions re-enter the main chain
through Steward recon, `to-spec`, or `to-tickets` — not by promoting prototype code as
product by default.
