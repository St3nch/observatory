---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

## Observatory preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/domain-modeling/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Observatory uses one glossary: `VOCABULARY.md`. Never create `CONTEXT.md` or
   `CONTEXT-MAP.md`. Ignore [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md) for this repository.
3. Read `VISION.md`, both decision registers, `AGENTS.md`, and the relevant ticket or spec
   before proposing model changes.
4. This skill normally **proposes** only; the Project Steward reconciles accepted
   changes into authority.
5. ADRs use [ADR-FORMAT.md](ADR-FORMAT.md) only when the Steward accepts a decision that
   meets the three-part bar. Create `docs/adr/` lazily.

## During the session

### Challenge against the glossary

When a term conflicts with `VOCABULARY.md`, quote the existing definition. Ask which
concept is intended only when ticket and authority do not resolve the ambiguity.

### Sharpen fuzzy language

Propose a precise canonical term when the user is vague or overloaded.

### Discuss concrete scenarios

Stress-test relationships with edge-case scenarios that force boundary precision.

### Cross-reference with code

When the user states how something works, check the code. Surface contradictions.

### Propose authority reconciliation

State proposed term, definition, avoided synonyms, affected existing definitions, and
affected API/schema/code names. The Steward decides whether and when to update
`VOCABULARY.md` and related authority. Working scenarios belong in `docs-temp/`.

### Offer ADRs sparingly

Offer an ADR only when all three hold:

1. **Hard to reverse**
2. **Surprising without context**
3. **Result of a real trade-off**

Otherwise skip the ADR.
