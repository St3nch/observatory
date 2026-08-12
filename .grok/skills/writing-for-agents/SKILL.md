---
name: writing-for-agents
description: Writing documents for agents. Use when creating or editing skills, or modifying AGENTS.md or CLAUDE.md.
---

# Writing for Agents

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/writing-for-agents/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. When authoring Observatory skills: keep `SKILL.md` concise, imperative, under 500 lines;
   put shared skill mechanics in sibling files behind pointers; add no auxiliary README,
   changelog, or setup docs inside skill folders.
3. Do not create `CONTEXT.md`, `CONTEXT-MAP.md`, `docs/agents/`, or `.scratch/`.
4. Do not embed product-feature architecture (specific tickets, stashed work, provider
   designs) into reusable workflow skills — only process, paths, and Steward gates.
5. `skills-lock.json` holds installer upstream provenance only. Do not invent schema fields.
   Git history records local adaptations. Warn: a future skills update must not blindly
   overwrite adapted project-local skills.

When the document is a skill, also read [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md) for
frontmatter, invocation choice, and router skills.

## Context pointers

A **context pointer** is a reference held in the agent's context that names some
out-of-context material and encodes the condition for reaching it. A skill's description
is one; a line in `AGENTS.md` naming a doc is the same object. The pointer's _wording_,
not its target, decides when the agent reaches the material.

- **Front-load the leading word** — the pointer is where it does its triggering work.
- **One trigger per branch.** Collapse synonym renames of a single branch.
- **Cut identity the body already carries.**

## The two loads

- **Context load** — always-loaded material on the agent's window.
- **Cognitive load** — the human index of which documents exist and when to use them.

Material reached only through a pointer escapes context load at the price of the pointer's
line; material with no pointer rides entirely on cognitive load.

## Information hierarchy

Documents mix **steps** (ordered actions) and **reference** (consulted on demand):

1. **In-file step** — primary: what the agent does, in order.
2. **In-file reference** — consulted on demand.
3. **Disclosed reference** — separate file behind a pointer.

**Progressive disclosure** pushes material down the ladder so the top stays legible.
**Co-location** keeps a concept's definition, rules, and caveats under one heading.
**Sprawl** is excess length; cure it by disclosing and splitting.

## Steps and completion criteria

Every step ends on a **completion criterion**:

- **Clarity** — agent can tell done from not-done. Sharpen vague bounds first; hide later
  steps across a real context boundary only when premature completion is observed.
- **Demand** — how much it requires. Exhaustive, checkable criteria drive legwork.

## When to split

- **By sequence** — when post-completion steps tempt the agent to rush the current one.
- **By invocation** — skill-specific: see [`SKILL-MECHANICS.md`](SKILL-MECHANICS.md).

## Leading words

A **leading word** is a compact pretrained concept the agent thinks with (_tracer bullets_,
_fog of war_). Repeat as a token. Prefer existing words over coined ones.

Prompt the **positive** target behaviour. A prohibition earns its place only as a hard
guardrail you cannot phrase positively — then pair it with the positive target.

## Pruning

- One **single source of truth** per meaning.
- The **environment** is a source of truth; restating it is a cache — keep only expensive lookups.
- Every line must stay **relevant**.
- Delete **no-ops** (instructions the model already obeys by default) as whole sentences.
