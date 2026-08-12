---
name: tdd
description: Test-driven development. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/tdd/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Read `VOCABULARY.md`, relevant decisions, the approved ticket, and any applicable ADR.
3. The approved ticket pre-agrees its public seams. Do not re-confirm them with Chaz.
   Escalate only a newly discovered seam that changes the contract.
4. Ordinary TDD is not hammer testing. Never call a live provider from an ordinary
   automated test. Use real PostgreSQL when behavior depends on transactions, constraints,
   locking, migrations, SQL, or recovery.
5. Treat TypeScript examples in [tests.md](tests.md) and [mocking.md](mocking.md) as
   language-neutral illustrations; implement in this repo's Python/pytest style.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. A good test
reads like a specification and survives refactors. See [tests.md](tests.md) and
[mocking.md](mocking.md).

## Seams

A **seam** is the public boundary you test at. Tests live at seams, never against internals.

Work only at ticket-approved seams. When interface depth or seam placement is itself in
question, consult project-local `codebase-design` for vocabulary (module, interface, depth,
seam, adapter, leverage, locality) — as reference, not a separate session to run.

## Anti-patterns

- **Implementation-coupled** — mocks internals, private methods, or side-channel DB checks.
- **Tautological** — expected value recomputed the same way as the code.
- **Horizontal slicing** — all tests then all implementation. Prefer **vertical slices**:
  one test → one implementation → repeat (**tracer bullets**).

## Rules of the loop

- **Red before green.** Failing test first; only enough code to pass.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to `code-review`, not red → green.
