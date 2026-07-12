# M16 Provider Cross-Check Hostile-Path Plan

Status: planning / acceptance-gate proposal
Authority: none until accepted
Milestone: M16
Date: 2026-07-12

---

## Purpose

Define the high-consequence hostile paths that must fail closed before any M16 fixture proof can be accepted.

---

## High-consequence hammers

### H-M16-01 Missing provider attribution

Input: one side omits provider name/family or evidence reference.

Expected: affected side blocked; no comparison value emitted as normal testimony.

### H-M16-02 Winner laundering

Input asks for `winner_provider`, `best_provider`, or “which source is right.”

Expected: reject with closed error; no side selected.

### H-M16-03 Average/consensus laundering

Input asks for average, median, majority vote, consensus, blended rank, or “best estimate.”

Expected: reject; no derived truth value.

### H-M16-04 Proprietary metric equivalence

Input compares same-looking difficulty/authority/visibility scores with unknown definitions.

Expected: `unresolved_incomparability`; no arithmetic difference presented as scale-equivalent.

### H-M16-05 Time-distance erasure

Input contains materially separated capture or provider-data times but requests no warning.

Expected: mandatory non-synchronous warning; downgrade or block current-state comparison.

### H-M16-06 Freshness collapse

Input has one fresh side and one stale/unknown side.

Expected: each side retains its own state; no shared “fresh” result.

### H-M16-07 Rights/retention bypass

Input includes blocked/expired testimony.

Expected: blocked or partial disposition; blocked side not normalized into ordinary comparison.

### H-M16-08 Source-admission bypass

Input includes unadmitted provider/source family.

Expected: `blocked_source_not_admitted`.

### H-M16-09 Provider error parsed as testimony

Input includes error/throttle/malformed fixture as though it were a value.

Expected: blocked status; no normal provider side.

### H-M16-10 Presence/absence universalization

Input asks to convert sampled provider disagreement into universal presence/absence.

Expected: reject or return scoped caveat only.

### H-M16-11 Disagreement erasure

Input requests only a clean summary with caveats and differing values removed.

Expected: reject projection; disagreement and mandatory caveats remain attached.

### H-M16-12 Cross-scope aggregation

Input mixes evidence from two synthetic scopes.

Expected: external `not_found` or blocked-scope result; no existence leak.

### H-M16-13 Provider profile becomes trust ranking

Input converts methodology/profile notes into accuracy, quality, or trust score.

Expected: reject.

### H-M16-14 Recommendation laundering

Input asks which provider SearchClarity should buy/use or which metric should guide strategy.

Expected: reject or evidence-only response with consumer promotion required.

### H-M16-15 Persistence laundering

Input asks to save comparison, ledger entry, consensus, or derived score.

Expected: reject; no file/database/cache write.

### H-M16-16 No-side-effect boundary

Runtime/static checks prove cross-check reads do not call provider/network/subprocess code, write files, mutate fixtures, import DB drivers, or create reports/tasks/recommendations.

---

## Contract-acceptance tests

- exact request/response vocabulary;
- deterministic side ordering;
- deterministic caveat ordering;
- aligned/misaligned dimension output;
- per-side attribution/status/freshness preservation;
- closed comparison-disposition vocabulary;
- closed disagreement-type vocabulary;
- truth/winner/composite flags always false;
- whole-unit truncation if bounded output ceilings apply.

---

## Proof classification

A future passing implementation may claim only:

```text
proof_class: mixed_suite
execution_surface: synthetic_fixture_in_memory_local
proof_strength: bounded_enforcement_proof
```

It may not claim live-provider, production, database, recurring-capture, report-language, or external-methodology proof.
