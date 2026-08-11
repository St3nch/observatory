---
name: to-spec
description: Turn the current conversation into a spec and publish it to the project issue tracker — no interview, just synthesis of what you've already discussed.
disable-model-invocation: true
---

# To Spec

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/to-spec/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Read `VISION.md`, `VOCABULARY.md`, both decision registers, and any Steward-reconciled
   proposals already in authority.
3. Do not interview. Synthesize what is already settled.
4. Require an active VedaOps lease before any filesystem write.
5. Do not use an issue tracker, labels, `.scratch/`, or `docs/agents/`.

## Process

1. Explore the codebase only as needed. Use `VOCABULARY.md` terms. Respect ADRs.
2. Propose the test **seams** at the highest useful point; prefer existing seams. Confirm
   seams with the Steward or Chaz when not already fixed by authority.
3. Write the draft under `docs-temp/specs/<kebab-slug>.md` using the template below.
4. Stop for **Steward acceptance**. Do not write `docs/specs/` unless the Steward
   explicitly directs promotion of this accepted draft.
5. On explicit promote instruction only: under lease, write
   `docs/specs/<kebab-slug>.md` with status **normative**, and leave or remove the draft
   as the Steward directs. Create `docs/specs/` lazily.

## Spec template

```markdown
# <Title>

**Status:** draft | normative
**Authority:** links to VISION, VOCABULARY, decisions, ADRs that bind this spec

## Problem

What must be true that is not true today, in product terms.

## Authority

Which settled decisions and terms this spec implements. Quote IDs where they exist.

## Invariants

Non-negotiable rules this implementation must preserve.

## Behavior

Observable behavior the system must exhibit. Prefer explicit outcomes over layer chores.

## Seams

Public boundaries under test. Name modules by role, not file paths.

## Verification

Commands, substrates (ordinary tests, real PostgreSQL, …), and forbidden false proofs
(no live provider in ordinary tests; mocks do not prove durability).

## Out of scope

Explicit exclusions for this spec.

## Unproven limits

What this spec deliberately leaves unproved.
```

Do not include specific file paths or code snippets. Exception: a prototype snippet that
encodes a decision more precisely than prose (state machine, schema, type shape) may be
inlined and marked as prototype-derived.

## Completion

Draft exists at `docs-temp/specs/…`, or durable normative file exists only after explicit
Steward promote. Next: `to-tickets` against the accepted durable spec when ready.
