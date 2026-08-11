---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

# Grill with Docs

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/grill-with-docs/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Read `VISION.md`, `VOCABULARY.md`, `decisions/decisions.md`, `decisions/deferred.md`,
   and any relevant accepted ticket or `docs/specs/` file before questioning.
3. Invoke project-local `grilling` and `domain-modeling` only.
4. Require an active VedaOps lease before any filesystem write, including `docs-temp/`.

## Process

1. Run a grilling session against existing authority and prior work. Question Chaz; do not
   invent product facts.
2. Use `domain-modeling` to challenge terms, scenarios, and ADR candidacy. Propose precise
   language; do not write `VOCABULARY.md`, decisions, ADRs, or `VISION.md`.
3. End with a **proposal package** (conversation summary and, under lease, optional
   `docs-temp/grilling/<slug>-proposals.md`) listing:
   - proposed vocabulary entries (term, definition, avoided synonyms)
   - proposed decision entries (decision, why, cost, rejected alternative)
   - proposed deferrals (why not now, trigger, cost of forgetting)
   - ADR candidates only when hard to reverse, surprising, and a real trade-off
   - open questions still for Chaz
4. Stop for **Steward reconciliation**. Skill output is working input, not authority.

## Completion

Shared understanding reached and proposal package delivered. Authority changes happen only
when the Project Steward explicitly reconciles them. Next main-chain step after
reconciliation: `to-spec` when an implementation contract is needed.
