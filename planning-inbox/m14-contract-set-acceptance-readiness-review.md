# M14 Contract-Set Acceptance Readiness Review

Status: owner-ruling proposal
Authority: none until accepted by owner decision
Milestone: M14 — Typed Read API / MCP Contract and Prototype
Date: 2026-07-12

---

## Question

Should the thirteen M7 contract artifacts be accepted as Observatory contract set v0.1, with their existing open-owner-ruling and deferred-milestone caveats preserved?

## Verified State

All thirteen planned M7 artifacts exist and remain marked `draft`, `draft skeleton`, or `draft placeholder`.

`contracts/README.md` states that only accepted contracts bind and that M10 schema planning consumes accepted contracts.

M8 through M13 nevertheless used these documents as the behavioral basis for hammers, first-slice planning, implementation validation, and provider-probe controls.

The documents were therefore operationally relied upon without a matching status transition.

## Proposed Ruling

Accept the following as **contract set v0.1** within their declared scope:

- `scope-rights-retention.md`
- `evidence-id-citation.md`
- `freshness-staleness-volatility.md`
- `claim-safety.md`
- `query-panel.md`
- `capturepackage-v0-1.md`
- `raw-archive-provider-drift.md`
- `provider-testimony.md`
- `provider-cross-check.md`
- `consumer-promotion.md`
- `overlay.md`
- `searchclarity-consumer-placeholder.md`
- `typed-read-tool-skeleton.md`

Acceptance would not resolve any open owner-ruling candidate already named inside the documents.

Acceptance would not authorize schema, migrations, provider calls, production API/MCP, customer data, reports, recurring capture, or strategy/recommendation storage.

The placeholder and skeleton artifacts would remain limited by their own labels and owning milestones:

- SearchClarity placeholder remains bounded to M15 planning.
- Typed read-tool skeleton becomes accepted M7 input, while M14 still owns the real typed-read contract.

## Recommendation

Accept the set as v0.1 because it has already survived M8–M13 use and because continued draft status creates more ambiguity than safety.

Do not edit all thirteen status headers until the owner explicitly approves this proposal.
