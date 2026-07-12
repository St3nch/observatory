# Decision — Accept M17 Owned Telemetry Overlay Proof Contract and Rulings

Status: accepted
Date: 2026-07-12
Milestone: M17 — Owned Telemetry Overlay Proof

---

## Decision

Accept `contracts/owned-telemetry-overlay-proof-v0-1.md` as the binding M17 proof contract within its declared scope.

Accept the prepared M17 ruling bundle:

1. Synthetic internal telemetry follows the same no-storage overlay law as synthetic customer first-party telemetry.
2. M17 uses synthetic in-memory fixtures only; no real customer analytics, owner-private telemetry, account identifiers, exports, URLs, screenshots, files, credentials, or connector data are admitted.
3. Bounded discard proof requires no file/database/network/subprocess/secret/external-repository access, no mutable cache, unchanged fixtures, no overlay values in proof records or logs, deterministic response construction, and explicit non-persistence/discard status. This does not prove production memory erasure or infrastructure logging behavior.
4. No overlay-derived manifest survives the read call. No values, hashes, field inventory, external reference, derived private summary, or reversible fingerprint may be retained.
5. Synthetic intervention timelines may support temporal before/after alignment only. They cannot establish causality, recommendations, tasks, report prose, or accepted conclusions.
6. Screenshots, CSV/PDF exports, URLs, files, external references, parsers, upload paths, connectors, and screenshot/file readers remain blocked.
7. Overlay inputs receive no Observatory observation, evidence, capture, raw-payload, citation, or scope identity.
8. Output is limited to bounded synthetic alignment facts, freshness/incomparability warnings, coverage context, explicit discard status, and consumer-promotion requirements.
9. M17 is eligible for one exact local deterministic synthetic fixture-backed proof, but implementation remains separately gated.

OR-F2 is ruled for M17 scope: internal first-party telemetry does not receive a storage exception.

OR-F3 is ruled for M17 scope: consumer-supplied freshness may support bounded alignment warnings only and does not authorize customer-facing conclusions.

---

## Explicit non-authorizations

This decision does not authorize:

- real customer first-party analytics;
- real owner/internal telemetry;
- customer identities or account records;
- screenshots, files, URLs, exports, connectors, or external references;
- overlay persistence, caching, durable logs, manifests, hashes, or canonical ingestion;
- evidence-ID or scope-ID promotion of overlay inputs;
- customer report generation or delivery;
- provider calls or recurring capture;
- Postgres, schema, or migrations;
- production API/MCP or consumer integration;
- recommendations, tasks, strategy storage, or automatic conclusion promotion;
- M17 proof implementation beyond a later exact authorization.

---

## Next gate

A separate owner authorization is required before implementing the exact task in:

`planning-inbox/m17-owned-telemetry-overlay-fixture-proof-task-proposal.md`
