---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

# Observatory research workflow

This section supersedes the generic storage instructions below for Observatory.

## Preflight

1. Report the absolute path of this loaded file:
   `/home/chaz/projects/vedaops/observatory/.grok/skills/research/SKILL.md`
   Prefer the resolved project-local path. Project-local skills override plugin copies.
2. Require an active VedaOps lease before any filesystem write, including `docs-temp/`.

Use a background agent when independent reading can proceed alongside useful work; direct
research is fine for a small question.

1. State the decision or implementation question the research must answer.
2. Prefer primary sources: official documentation, specifications, source code, research
   papers, and first-party APIs. Follow consequential claims to the owning source.
3. Separate sourced facts, inference, and recommendation.
4. Capture useful findings in one ignored file under `docs-temp/`, with links beside the
   claims they support. Reuse or replace the existing note instead of creating a note tree.
5. Treat the note as working input, never authority. The Project Steward records any
   accepted result in the existing decision register, ticket, vocabulary, or ADR.
6. Report uncertainty and any fact that still requires a real-environment check.

Do not put secrets, credentials, or unredacted provider payloads in a research note.

## Superseded upstream summary

Do not follow this generic summary where it conflicts with the workflow above:

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
