# M16 Provider Cross-Check Reconciliation Review

Status: planning complete; ready for owner ruling and contract acceptance
Milestone: M16
Date: 2026-07-12

---

## Reviewed authority

- `02-boundaries.md`
- `contracts/provider-testimony.md`
- `contracts/provider-cross-check.md`
- `contracts/freshness-staleness-volatility.md`
- `contracts/claim-safety.md`
- `contracts/typed-read-api-mcp-v0-1.md`
- `contracts/searchclarity-proof-workflow-v0-1.md`
- `research/rg9-provider-cross-check-disagreement-model.md`
- `hammers/hammer-matrix-v0-1.md`
- M13 sanitized provider evidence and disarmed execution posture
- M14 and M15 bounded proof outputs

---

## Reconciled conclusions

1. Provider disagreement is first-class evidence, not a defect to smooth away.
2. Provider identity, endpoint/surface, metric definition posture, evidence reference, capture time, provider time, freshness, rights, retention, and status stay attached to each side.
3. Same-looking proprietary metrics are incomparable by default when definitions/scales are unknown.
4. Comparability requires explicit aligned dimensions; missing context fails closed.
5. Time distance and freshness differences remain visible per side.
6. No truth, winner, average, consensus, blended metric, trust score, or composite score is allowed.
7. Presence/absence disagreement is sample- and context-bound.
8. Provider error, drift-blocked, rights-blocked, retention-expired, withdrawn, invalidated, or unadmitted testimony cannot silently participate as normal evidence.
9. Provider profile notes may explain methodology only when cited, versioned, and caveated; they cannot rank providers.
10. Disagreement output remains compute-on-read. A persistent ledger is not justified or authorized.
11. Consumer meaning, provider choice, purchases, recommendations, reports, and strategy promote out.
12. The first proof can be synthetic, local, deterministic, in-memory, and no-side-effect without any new provider activity.

---

## Outputs prepared

- `contracts/provider-cross-check-proof-v0-1.md`
- `planning-inbox/m16-owner-ruling-proposals.md`
- `planning-inbox/m16-provider-cross-check-hostile-path-plan.md`
- `planning-inbox/m16-provider-cross-check-fixture-proof-task-proposal.md`

---

## Gates remaining

1. Owner accepts or amends OR-A1 and M16-R1 through M16-R8.
2. Owner accepts the M16 proof contract and hostile-path plan.
3. Owner separately authorizes the exact fixture-backed implementation task.
4. Owner-local full-suite execution is required before proof closure.

---

## Non-authorizations preserved

No provider calls, purchases, credentials, recurring capture, persistence, truth/winner/average/consensus/composite logic, customer data, reports, overlays, Postgres, schema, migrations, production API/MCP, or production integration is authorized by this review.
