# DB-4 R5 Repeat ob-dev Compatibility Review

Status: accepted review record
Date: 2026-07-17
Authority: `decisions/2026-07-17-db4-r5-repeat-compatibility-review-authorization.md`
Reviewed ob-dev commit: `879529c27cad666099cf4f697eb7cbb56dec2279`
Reviewed Observatory commit: `8ad08b28309b8981d19c3dd3d065c18e99422da5`
Refreshed server: `ob-dev` 0.5.0

## Verdict

```text
READY FOR OWNER EXECUTION DECISION
```

This is not execution authority. PostgreSQL remains prohibited until the owner separately accepts an exact live-campaign decision.

## Refreshed runtime evidence

```text
service: ob-dev
version: 0.5.0
tool_count: 63
generic_execution: false
postgres_tool_count: 31
postgres_capability_class: inspection_only
postgres_configured: false
postgres_mutation_enabled: false
```

## Blocker closure

| Blocker | Repeat-review result | Evidence |
|---|---|---|
| G1 marker verification | closed | profile and broken-candidate runners require marker verification; backup and restore paths verify markers; emitted result identity is bound to the verified marker |
| G2 authority enforcement | closed | live control, migration, profile, broken-candidate, backup/restore, and campaign-finalization paths require an accepted authority file with the exact operation class |
| G3 sixteen hostile fixtures | closed | the broken-candidate profile contains all sixteen SHA-bound fixtures and the executor has bounded native or semantic rejection logic for every check ID |
| G4 backup-role behavior | closed | the role profile directly executes same-scope and cross-scope checks under `observatory_test_backup`, recording active role, scope, and visible row counts |
| G5 campaign evidence and clean trees | closed | profile tools require one campaign ID; append-only campaign finalization exists; source-tree checks allow only prior campaign evidence beneath `database/hammer-results/` and reject unrelated dirtiness |

## Validation after restart

```text
ob-dev pytest: 104 passed
ob-dev Ruff: passed
Observatory pytest: 236 passed
Observatory authority sync: passed
Observatory origin/main: synchronized
ob-dev tree: clean
```

The Observatory tree remains non-clean only because of the protected unrelated file:

```text
audits/kaizen_to_slash_goal_prompt.md
```

That file was not touched. Its presence would correctly block a live campaign until resolved outside this review package.

## Gate boundary

The compatibility layer is ready for owner consideration. The existing owner-decision draft remains unaccepted and authorizes no operations. Before execution, the owner must accept an exact decision naming the campaign ID, clean commits, operation classes, bounded sequence, and stop conditions.

Campaign execution will still not close DB-4. Independent review and a separate closure decision remain mandatory.
