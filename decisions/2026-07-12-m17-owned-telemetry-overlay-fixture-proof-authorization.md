# Decision — M17 Owned Telemetry Overlay Fixture Proof Authorization

Status: accepted
Date: 2026-07-12
Milestone: M17 — Owned Telemetry Overlay Proof

## Decision

Authorize exactly the bounded implementation task in:

```text
planning-inbox/m17-owned-telemetry-overlay-fixture-proof-task-proposal.md
```

The implementation may prove only synthetic, request-local, deterministic, in-memory overlay alignment and discard behavior.

## Authorized scope

- `src/observatory_overlay_proof/`
- the six named M17 overlay test files
- bounded result-register and local-test evidence files
- status/index updates required to record this exact authorization

## Non-authorizations

This decision does not authorize:

- real customer or owner-private telemetry;
- customer identity, accounts, URLs, files, screenshots, CSV/PDF exports, connectors, or credentials;
- overlay persistence, caching, durable logging, manifests, hashes, fingerprints, or canonical ingestion;
- Observatory evidence identity for overlay inputs;
- provider calls, capture, recapture, spend, reports, recommendations, causality, or tasks;
- Postgres, schema, migrations, production API/MCP, or production integration.

## Proof ceiling

A successful implementation proves only the committed synthetic local code path. It does not prove secure memory wiping, production infrastructure logging behavior, real private-data handling, consumer authentication, deployment, or integration.

## Separate test gate

No proof pass is claimed until the owner runs the full repository suite and the actual result is recorded separately.
