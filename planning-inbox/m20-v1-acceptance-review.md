# M20 Observatory v1 Acceptance Review

Status: final acceptance proposal; owner decision required
Milestone: M20 - Observatory v1 Acceptance
Date: 2026-07-12

## Acceptance scope

This review evaluates the bounded Observatory v1 evidence system that actually exists in the repository. It does not evaluate a production service, deployed database, recurring capture system, customer reporting product, dashboard, or complete provider platform.

## Recommended verdict

```text
ACCEPT OBSERVATORY V1 AS A BOUNDED, LOCAL, EVIDENCE-ONLY PROOF SYSTEM.
DO NOT REPRESENT IT AS PRODUCTION-READY OR FEATURE-COMPLETE.
```

## Doctrine conformance

### Stores observations, not conclusions — PASS

The accepted contracts and implemented proof paths preserve observations, provenance, scope, rights, retention, freshness, provider attribution, and bounded read outputs. Strategy, recommendations, accepted conclusions, and customer workflow state remain outside Observatory.

### Connected LLM interprets at read time — PASS

Typed-read and consumer-proof boundaries expose shaped evidence and caveats without granting direct SQL, credentials, raw unrestricted paths, or strategy persistence.

### Customer/private-data boundary — PASS FOR BOUNDED V1

Customer records and customer first-party analytics are excluded from durable Observatory storage. Synthetic overlay proof demonstrated request-local alignment and discard behavior without evidence promotion, identity leakage, files, screenshots, or retained values.

### Provider testimony, not truth — PASS

The DataForSEO probe and provider cross-check proof preserve provider attribution, disagreement, comparability limits, and non-synchronous warnings. No winner, truth score, or composite truth layer was introduced.

### Rights and retention fail closed — PASS

Capture, raw support, purge, and provider execution paths block on missing rights, retention, authorization, price, account, credential, or shape evidence. The single live probe was reviewed and raw payload was purged with proof.

## Evidence behavior

### First evidence slice — PASS

The C2 Controlled Public Manual Observation Package has a bounded local validation spine with accepted contracts, hammers, and tests.

### Provider admission — PASS AT NARROW CEILING

One DataForSEO C00 probe was executed under explicit bounded authorization, cost ceiling, duplicate prevention, review, and purge. It does not authorize additional provider calls.

### Typed reads — PASS AS LOCAL PROTOTYPE

The typed-read proof demonstrates deterministic, closed, fixture/in-memory evidence shaping. It is not a production API or MCP deployment.

### SearchClarity usefulness — PASS AS PROOF

The SearchClarity proof workflow demonstrates safe evidence support, report-safe references, claim-safety boundaries, and outward promotion requirements without generating customer reports or storing customer data.

### Provider disagreement — PASS AS PROOF

The cross-check proof preserves provider-specific testimony and disagreement without collapsing providers into truth or strategy.

### Owned telemetry overlay — PASS AS SYNTHETIC CODE-PATH PROOF

The overlay proof demonstrates no-storage, no-cache, no-log, no-evidence-promotion, cross-scope isolation, and bounded alignment outputs. It does not prove secure memory wiping or production infrastructure behavior.

### Recovery — PASS AT REPOSITORY CEILING

A full-history Git bundle was created, independently hashed, verified, restored into a disposable root, checked with `git fsck --full`, and passed all 184 tests. Encryption and off-machine recovery remain unproven.

## Hammer and test posture

Final owner-local proof state:

```text
184 tests passed
restored full suite: 184 tests passed
Git diff checks: passed on accepted batches
Git bundle verify: passed
Git fsck --full: passed
```

The suite includes fail-closed paths for scope, rights, retention, private data, strategy contamination, provider execution, duplicate/cost controls, raw support, typed reads, consumer boundaries, disagreement, overlays, and side effects.

## Consumer usefulness

The bounded v1 is useful for:

- proving the observation-versus-interpretation architecture;
- validating safe evidence packages and typed-read shapes;
- proving SearchClarity evidence-support boundaries;
- proving provider disagreement handling;
- proving ephemeral overlay behavior;
- preserving accepted contracts, rulings, hammers, and evidence lineage;
- serving as a governed foundation for a future persistence and production roadmap.

It is not yet useful as a live production service, recurring monitoring platform, customer report engine, or complete provider-backed visibility database.

## Acceptance conditions

Acceptance must preserve all current non-authorizations. No deferred capability becomes active merely because v1 is accepted.

## Final recommendation

Accept v1 as a successfully governed and tested bounded proof system. Close M20 only after the owner explicitly accepts this exact ceiling and the known-limit register.
