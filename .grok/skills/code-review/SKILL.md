---
name: code-review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along two axes — Standards (does the code follow this repo's documented coding standards?) and Spec (does the code match what the originating issue/spec asked for?). Runs both reviews in parallel sub-agents and reports them side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
---

# Code Review

Two-axis review of the diff between `HEAD` and a fixed point:

- **Standards** — does the code conform to this repo's documented coding standards?
- **Spec** — does the code faithfully implement the originating ticket / parent spec?

Both axes run as **parallel sub-agents**, then this skill aggregates findings.

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/code-review/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Read `VISION.md`, `VOCABULARY.md`, the decision registers, `AGENTS.md`, and the ticket.
3. Do not run setup, create `docs/agents/`, or invent an issue-tracker convention.
4. Require an active VedaOps lease only if applying fixes; pure review is read-only.

## Process

### 1. Pin the fixed point

Use the ticket's recorded start commit. If none, use merge-base with `main` and state that
choice; ask only when neither is safe.

Capture: `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.
Confirm the fixed point resolves and the diff is non-empty before spawning sub-agents.

### 2. Identify the spec source

In order:

1. The Observatory ticket and its acceptance criteria.
2. Parent path under `docs/specs/` when the ticket names one.
3. A path the user passed as an argument.
4. If nothing is found, report Spec axis unproven; do not create a spec.

### 3. Identify the standards sources

Repo docs such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`, plus the **smell baseline**
below. Repo standards override the baseline. Baseline smells are always judgement calls.
Skip anything tooling already enforces.

- **Mysterious Name** — name does not reveal role → rename or redesign.
- **Duplicated Code** — same logic shape in multiple hunks → extract shared shape.
- **Feature Envy** — method reaches into another object's data more than its own → move it.
- **Data Clumps** — same fields travel together → bundle into one type.
- **Primitive Obsession** — primitive standing in for a domain concept → small type.
- **Repeated Switches** — same cascade on the same type → polymorphism or shared map.
- **Shotgun Surgery** — one logical change scatters across many files → gather together.
- **Divergent Change** — one module edited for unrelated reasons → split by reason.
- **Speculative Generality** — abstraction the ticket does not need → delete until needed.
- **Message Chains** — long `a.b().c().d()` → hide behind one method.
- **Middle Man** — mostly delegates → call the real target.
- **Refused Bequest** — ignores most of what it inherits → composition instead.

### 4. Spawn both sub-agents in parallel

**Standards** — full diff command, commit list, standards sources + smell baseline pasted
in full. Brief: report documented-standard breaches (cite file+rule) and baseline smells
(name + hunk). Under 400 words. Distinguish hard violations from judgement calls.

**Spec** — diff command, commit list, ticket/spec contents. Brief: (a) missing or partial
requirements; (b) scope creep; (c) wrong implementation of a stated requirement. Quote the
ticket/spec line for each finding. Under 400 words.

If the spec source is missing, skip Spec sub-agent and note it.

### 5. Aggregate

Present `## Standards` and `## Spec` separately. Do not merge or rerank across axes.
End with one-line totals per axis and the worst issue within each axis.

## Why two axes

Standards-pass + Spec-fail and Spec-pass + Standards-fail are both possible. Separation
stops one axis from masking the other.
