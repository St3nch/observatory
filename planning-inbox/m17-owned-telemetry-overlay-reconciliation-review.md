# M17 Owned Telemetry Overlay Reconciliation Review

Status: planning review
Authority: none beyond cited accepted contracts
Milestone: M17
Date: 2026-07-12

---

## Purpose

Reconcile the accepted overlay, scope-rights-retention, claim-safety, typed-read, SearchClarity, and no-persistence boundaries before any M17 proof implementation.

## Accepted law carried forward

- Overlay is a read-time lens, not evidence admission.
- Customer and owner-internal first-party telemetry remain outside canonical Observatory storage.
- Overlay rows receive no observation ID, evidence ID, citation handle, capture ID, raw payload ID, or panel-run identity.
- Overlay values may support temporary alignment only.
- Durable interpretation, recommendations, reports, and accepted conclusions belong to the owning consumer.
- Missing scope, freshness, no-storage assertion, discard requirement, or allowed-use metadata fails closed.
- Screenshots, CSV/PDF exports, broad files, credentials, and direct provider access are not admitted overlay inputs.

## Reconciled M17 posture

### Internal telemetry

Owner-internal telemetry follows the same overlay law as customer first-party telemetry. Ownership does not convert private telemetry into Observatory evidence.

### First proof input class

The first proof should use synthetic scalar/time-series values embedded directly in committed fixtures. It should not parse files or accept arbitrary payload shapes.

### Discard proof

For the bounded in-memory proof, discard means:

- request-local overlay objects only;
- no module-level cache or mutable registry;
- no file, database, environment, network, subprocess, or logging writes;
- no overlay value in returned evidence units or persistent result metadata;
- no mutation of Observatory fixtures;
- no surviving reference after the function returns except the returned consumer-safe alignment summary.

This is bounded code-path proof, not operating-system memory erasure proof.

### Retained manifest

No overlay-derived manifest survives the read call. The response may state discard status and bounded alignment counts, but it must not return or retain a separate field inventory, value manifest, hash, customer identifier, file path, external overlay reference beyond the request-local response, or reversible fingerprint.

### Intervention timelines

Synthetic intervention events may be admitted as ephemeral alignment markers only. They cannot become Observatory history and cannot support causal claims.

### Screenshots and files

Remain blocked. M17 does not create file intake, parsing, upload, OCR, screenshot, CSV, PDF, or export support.

## Remaining owner gates

The concrete proposals are in `planning-inbox/m17-owner-ruling-proposals.md`.

After those rulings and the full proof contract are accepted, one exact synthetic fixture-backed implementation task may be separately authorized.

## Non-authorizations

No real private telemetry, customer identity, external files, overlay persistence, canonical ingestion, reports, provider calls, Postgres, schema, migrations, production API/MCP, or production integration is authorized.
