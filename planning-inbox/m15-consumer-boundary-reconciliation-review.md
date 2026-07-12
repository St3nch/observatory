# M15 Consumer-Boundary Reconciliation Review

Status: complete planning review; owner rulings pending
Authority: planning record only; not implementation or customer-facing authority
Milestone: M15
Date: 2026-07-12

---

## Reviewed authority

The M15 package was reconciled against:

- `contracts/searchclarity-consumer-placeholder.md`;
- `contracts/consumer-promotion.md`;
- `contracts/claim-safety.md`;
- `contracts/overlay.md`;
- `contracts/typed-read-api-mcp-v0-1.md`;
- `planning-inbox/owner-ruling-tracker.md`;
- DR4, DR5, DR9, DR10, and DR14 in `research/deep-research-backlog.md`;
- current M15 authority in `ACTIVE_CONTEXT.md` and `ROADMAP.md`.

## Confirmed doctrine

The reviewed contracts agree that:

```text
Observatory owns observations and evidence support.
SearchClarity owns customers, private inputs, interpretations, recommendations, reports, consent, review, acceptance, delivery, and revisions.
```

No accepted contract authorizes customer records, report prose, recommendations, private analytics, real overlays, file/screenshot intake, report delivery state, or production SearchClarity integration inside Observatory.

## Reconciled M15 design

The full proposed contract:

```text
contracts/searchclarity-proof-workflow-v0-1.md
```

settles the planning shape for:

- customer-clean internal report-support requests;
- closed claim-intent vocabulary;
- deterministic report-support dispositions;
- mandatory caveat propagation;
- separation of internal evidence handles from report-safe references;
- SearchClarity-owned human review and promotion;
- automatic evidence-side blocker conditions;
- provider disagreement without winner/average/composite logic;
- sampled-only AI/GEO support;
- marketplace fail-closed behavior;
- overlay and file/screenshot deferral;
- single-scope behavior;
- local synthetic proof boundaries.

## Open owner rulings

Concrete proposals now exist for:

- OR-E1 report-safe reference separation;
- OR-E2 marketplace report-support admission posture;
- OR-E3 AI/GEO sampled-only posture and deferred repeated-sampling thresholds;
- OR-E4 provider disagreement presentation;
- OR-E5 automatic report-support blockers;
- OR-F1 real overlay deferral to M17;
- consent-record ownership;
- mandatory SearchClarity human review;
- bounded M15 proof eligibility.

Source:

```text
planning-inbox/m15-owner-ruling-proposals.md
```

## Research disposition

### DR9

Customer-facing report-language validation remains required before SearchClarity launch or final report templates. The first M15 proof deliberately does not generate customer-facing prose.

### DR10

Real customer first-party overlays remain deferred to M17 under the proposed OR-F1 ruling. M15 may prove only blocked-path and no-leak behavior.

### DR4 / DR5

The M15 contract refuses to invent AI/GEO repeated-sampling thresholds. A single run supports only a sampled point-in-time observation.

### DR14

The first proof uses synthetic artifact-local report-safe references distinct from internal handles. Production format and resolution remain later work.

## Hostile-path disposition

The M15 hostile-path plan distinguishes high-consequence hammers from ordinary acceptance tests.

Primary high-consequence boundaries:

- customer identity laundering;
- private-data smuggling;
- report/recommendation laundering;
- caveat detachment;
- reference enumeration and cross-scope access;
- claim-status bypass;
- overlay smuggling;
- cross-customer aggregation;
- no-side-effect consumer behavior.

## Proof-task readiness

An exact bounded task proposal exists at:

```text
planning-inbox/m15-searchclarity-fixture-proof-task-proposal.md
```

It is not implementation authority.

Entry gates:

- owner accepts the full M15 contract;
- owner rules OR-E1 through OR-E5 and OR-F1;
- owner accepts consent and human-review boundaries;
- owner accepts the hostile-path plan;
- owner separately authorizes the exact task.

## Final review conclusion

M15 planning is coherent and ready for owner decision.

No customer-facing or production work is authorized by this review.
