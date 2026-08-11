---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
disable-model-invocation: true
---

# Observatory implementation workflow

This section supersedes the short upstream instructions below for Observatory.

Implement only a Project Steward-approved ticket.

1. Read `VISION.md`, `VOCABULARY.md`, both decision registers, `AGENTS.md`, the ticket,
   and any relevant ADR.
2. Record the starting commit and verify the working tree contains no unexplained changes.
3. Restate the ticket boundary, acceptance behavior, approved seams, and explicitly
   deferred work. Stop only for a contradiction that materially changes the implementation.
4. Use `tdd` in small vertical slices. The approved ticket pre-authorizes its stated seams.
5. Run the narrow relevant test after each slice. Run Ruff and mypy regularly.
6. Never make live provider calls from ordinary tests. Use real PostgreSQL when the claim
   depends on PostgreSQL behavior.
7. Do not edit product authority merely to make code fit. Propose vocabulary, decision, or
   architecture changes to the Project Steward.
8. Run the complete test, lint, and typecheck commands at the end.
9. Invoke `code-review` against the recorded starting commit. Resolve valid findings and
   rerun affected checks.
10. Commit the bounded ticket only after checks and review pass. Do not push or broaden the
    ticket unless the Project Steward directs it.

Report the commit, acceptance evidence, and exact unproven limits.

## Superseded upstream summary

Do not follow this generic summary where it conflicts with the workflow above:

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Commit your work to the current branch.
