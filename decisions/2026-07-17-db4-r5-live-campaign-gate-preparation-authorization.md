# DB-4 R5 Live-Campaign Gate Preparation Authorization

Status: accepted
Date: 2026-07-17
Decision owner: project owner
Authorized operation classes: repository_static_edit, repository_validation, git_stage, git_commit

## Decision

Authorize Route C Batch R5 only: prepare the separately owner-gated DB-4 disposable PostgreSQL campaign from live repository truth.

R5 must:

- audit the frozen `ob-dev` implementation against every capability required by the live campaign;
- record each capability as compatible, incompatible, or blocked with exact evidence;
- draft the later owner execution decision and its acceptance checklist without accepting or executing it;
- keep all PostgreSQL execution prohibited;
- keep `ob-dev` frozen;
- stop if any required capability is missing rather than weakening the campaign.

## Accepted predecessor

R4 completed at commit `b4c02c87cbb27955245e89c2553491c1373a9435`.

## Exact R5 artifacts

- `planning-inbox/db4-r5-frozen-ob-dev-compatibility-review.md`
- `planning-inbox/db4-live-disposable-campaign-owner-decision-draft.md`
- `database/db4-remediation-conformance-manifest.json`
- current-state authority documents and validators/tests required to enforce this R5 state

## Boundaries

R5 does not authorize:

- PostgreSQL creation, reset, migration, rollback, profile execution, backup, restore, or deletion;
- any `ob-dev` source, test, configuration, connector, process, or deployment change;
- acceptance of the draft live-campaign decision;
- DB-4 closure or DB-5 activation;
- governed databases, providers, customer/private data, recurring work, or production work.

## Gate rule

The later live campaign may be accepted only when every required capability is proven compatible and every blocker is closed by a separately accepted decision. A draft decision is not authority.

## Stop condition

R5 completes when the compatibility review and owner-decision draft are committed, the authority spine is synchronized, static validation is green, and the live execution gate remains closed unless the owner separately accepts a blocker-free execution decision.
