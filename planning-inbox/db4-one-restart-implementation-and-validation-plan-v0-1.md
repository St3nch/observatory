# DB-4 One-Restart Implementation and Validation Plan v0.1

Status: planning candidate; no implementation or execution authority
Milestone: DB-4 remediation

## Goal

Complete the entire `ob-dev` implementation correction in one bounded batch, validate it fully while the current server remains available for repository work, then require one owner restart and one connector refresh before any PostgreSQL campaign.

## Why this plan exists

The previous DB-4 campaign forced repeated restarts because hammer behavior was encoded directly in Python and defects were discovered one fixture at a time during live execution.

The corrected approach separates:

```text
stable bounded MCP tools
from
SHA-bound data-driven profiles and candidates
```

Profile and fixture corrections should not change the MCP tool schema and therefore should not require a connector refresh.

## Tool-surface rule

The implementation batch must begin by freezing the intended public PostgreSQL tool surface.

Preferred outcome:

- retain the existing bounded tool names;
- correct annotations, capabilities, and contracts;
- make profile runners load exact repository profile files at invocation time;
- avoid adding one tool per hammer or fixture;
- document the final count only after implementation;
- treat count as inventory, not as a safety guarantee.

Any tool addition, removal, rename, or input/output schema change must be justified in the exact implementation decision before the owner restarts.

## Batch phases

### Phase A — contracts and failing tests

Implement tests first for:

- authority file verification;
- marker identity binding;
- atomic migration/history behavior;
- immutable history;
- advisory lock behavior;
- search path and timeout settings;
- schema fingerprint coverage;
- profile loading and SHA validation;
- result-register immutability and supersession;
- redaction of full result envelopes;
- fixed role switching;
- cleanup verification;
- tool registry stability.

No owner restart occurs.

### Phase B — stable runtime implementation

Implement all selected source changes in `ob-dev` as one branch/worktree batch.

No live PostgreSQL campaign is used to discover routine unit-level defects.

Use mocks and bounded subprocess contract tests only for development-time behavior. These tests do not become closure proof.

### Phase C — static and unit validation

Before restart, require:

```text
ruff pass
pytest pass
package import pass
registry count and contract tests pass
Git diff check pass
working tree exact-manifest review
README and version reconciliation pass
```

No restart occurs on a red suite.

### Phase D — Observatory package implementation

After `ob-dev` code is green but before restart:

- replace migration and rollback files;
- create profile manifests;
- create hostile candidates and manifests;
- create proof schemas and validators;
- update Observatory tests;
- run authority sync, unittest, pytest, Ruff where applicable, integrity scans, and Git diff checks.

No PostgreSQL execution occurs.

### Phase E — exact commit freeze

Create separate exact commits:

1. `ob-dev` implementation commit;
2. Observatory migration/profile/proof package commit;
3. optional authority/execution decision commit only after owner acceptance.

Record both commit hashes in the execution gate.

### Phase F — one owner restart

Owner performs one restart from the accepted environment and refreshes connector actions once.

Before the restart request, the steward must report:

- exact `ob-dev` commit;
- exact Observatory commit;
- clean-tree state excluding the protected untracked file;
- final tool inventory and any schema changes;
- all validation results;
- exact startup environment names without secrets;
- exact owner command/runbook.

### Phase G — post-restart read-only verification

After restart:

- confirm server version and commit identity if exposed;
- confirm tool inventory;
- confirm capability and authority posture;
- run read-only PostgreSQL readiness and server identity;
- verify no disposable database or test roles exist before campaign.

If any defect is found here, stop. Do not begin PostgreSQL mutation.

### Phase H — data-driven campaign

Run the exact campaign using profile files loaded at call time.

A profile or expected-outcome correction that does not alter Python contracts may be edited, validated, committed, and reloaded without restarting the MCP server.

A Python implementation defect stops the campaign and requires a new bounded implementation batch. It must not trigger rapid one-line restart churn.

## Owner restart ceiling

Target:

```text
one restart for the accepted implementation batch
```

Permitted exception:

A second restart may occur only after:

- a real implementation defect is proven;
- the campaign stops safely;
- the complete correction batch is prepared and validated;
- the owner is shown the cause and why profile/data correction cannot solve it.

No repeated restart-per-fixture workflow is permitted.

## Startup environment

The future runbook may require environment variables for:

```text
POSTGRES_BIN_DIR
OB_DEV_POSTGRES_CAPABILITY
OB_DEV_POSTGRES_AUTHORITY
OB_DEV_POSTGRES_AUTHORITY_SHA256
OB_DEV_POSTGRES_EVIDENCE_ROOT
POSTGRES_PASSWORD
```

Exact names may be revised by the implementation package, but:

- no secret value appears in documentation;
- authority and authority SHA must agree;
- evidence root must be outside Git or ignored;
- password remains temporary and owner-controlled.

## Restart command requirements

The owner command/script must:

1. stop only the intended `ob-dev` process if running;
2. validate required non-secret environment values;
3. prompt securely for the PostgreSQL password;
4. run fixed pre-start tests or verify the accepted commit;
5. start the server;
6. print no password or connection URI;
7. make cleanup of temporary environment straightforward.

The script must not change repositories, PostgreSQL configuration, roles, databases, or authority.

## Validation stop conditions

Do not ask the owner to restart when:

- either repository is dirty outside accepted exact paths;
- tests or Ruff fail;
- tool registry differs from the accepted manifest;
- profile schemas are invalid;
- authority sync fails;
- the execution decision is missing;
- remote access/authentication posture remains unresolved;
- PostgreSQL mutation is not yet authorized.

## Success condition

The plan succeeds when the owner performs one restart after a fully green implementation batch and the subsequent campaign can iterate on SHA-bound profile data without additional connector refreshes.
