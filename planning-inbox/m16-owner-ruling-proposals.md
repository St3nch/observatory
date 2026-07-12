# M16 Owner-Ruling Proposals

Status: planning / owner-decision proposal
Authority: none until accepted in `decisions/`
Milestone: M16
Date: 2026-07-12

---

## Purpose

Present the minimum rulings required before the M16 provider cross-check proof contract can be accepted or any bounded proof implementation can be authorized.

---

## OR-A1 — Persistent Disagreement Ledger

Proposed ruling:

```text
M16 disagreement output is compute-on-read only.
```

No persistent Disagreement Ledger, comparison table, derived summary cache, materialized disagreement record, or durable provider-comparison score is admitted.

A later persistence proposal would require the V6 materialization test, explicit owner ruling, schema authority, retention/rights review, and proof that persistence provides value that deterministic recomputation cannot.

## M16-R1 — Comparability threshold

Proposed ruling:

```text
Strong comparison requires alignment of subject, metric family, scope, surface, and material context dimensions.
```

Missing or materially mismatched dimensions downgrade to `partially_comparable`, `unresolved_incomparability`, or a blocked disposition.

Same-looking labels are insufficient.

## M16-R2 — Proprietary metric posture

Proposed ruling:

```text
Cross-provider proprietary scores are incomparable by default when definitions or scales are unknown.
```

This applies to difficulty, authority-like, visibility, confidence, opportunity, and other provider-model scores.

M16 may preserve values side by side as attributed testimony, but may not calculate differences as though the scales were equivalent.

## M16-R3 — Time-distance behavior

Proposed ruling:

```text
Each provider side retains its own captured_at, provider-reported time, freshness, and volatility state.
```

A deterministic warning is required when capture or provider-data times differ. Material separation must downgrade or block current-state comparison rather than being hidden.

No universal fixed time threshold is invented by M16; fixture rules may use declared synthetic bands to prove behavior only.

## M16-R4 — Truth, winner, average, consensus, and composite prohibition

Proposed ruling:

```text
M16 produces no truth value, winner provider, average, consensus, blended metric, trust score, or composite score.
```

No “closest to the average” or majority-vote adjudication is allowed.

## M16-R5 — Ground-truth adjudication

Proposed ruling:

```text
External verified evidence may be introduced later as another explicitly admitted evidence source, not as an automatic truth-provider override.
```

M16 does not implement adjudication. Any future ground-truth workflow requires separate methodology, source admission, and owner ruling.

## M16-R6 — Provider profile notes

Proposed ruling:

```text
Provider personality/profile notes are allowed only as cited, versioned, caveated methodology metadata.
```

They may explain coverage, update cadence, index/source differences, or known method boundaries. They may not rank provider quality, predict accuracy, or recommend purchases.

## M16-R7 — Cross-scope aggregation

Proposed ruling:

```text
Cross-scope provider comparisons remain blocked.
```

The first proof uses two isolated synthetic scopes and must reject any attempt to combine them.

## M16-R8 — Bounded proof eligibility

After contract and hostile-path acceptance, M16 may propose one local fixture-backed proof using committed synthetic observations and sanitized provider testimony.

The proof must remain:

- local-only;
- in-memory;
- deterministic;
- no network or provider calls;
- no credentials or purchases;
- no customer data or overlays;
- no report generation;
- no database or persistence;
- no production API/MCP or integration.

Implementation requires separate exact owner authorization.

---

## Recommended owner decision bundle

```text
ACCEPT OR-A1 compute-on-read disagreement only; no persistent ledger
ACCEPT M16 comparability threshold and fail-closed mismatch behavior
ACCEPT proprietary metrics incomparable by default when definitions/scales are unknown
ACCEPT per-provider time/freshness preservation and non-synchronous warnings
ACCEPT no truth, winner, average, consensus, blended metric, trust score, or composite
ACCEPT no ground-truth adjudication in M16
ACCEPT provider profile notes only as cited caveated methodology metadata
ACCEPT cross-scope comparisons blocked
ACCEPT bounded M16 proof eligibility, not implementation
```

Do not combine proof implementation authorization with this ruling bundle.

---

## Still deferred

- live cross-provider calls;
- Ahrefs/Semrush acquisition or admission;
- recurring cross-provider capture;
- persistent Disagreement Ledger;
- production comparison API/MCP;
- customer-facing provider-comparison wording;
- ground-truth adjudication;
- provider-selection recommendations;
- Postgres, schema, migrations, and production integrations.
