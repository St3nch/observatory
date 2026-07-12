# Decision — Accept M14 Typed-Read Contract and Authorize Fixture-Only Prototype

Status: accepted
Date: 2026-07-12
Milestone: M14 — Typed Read API / MCP Contract and Prototype

## Decision

Accept `contracts/typed-read-api-mcp-v0-1.md` as the binding M14 typed-read behavioral contract v0.1.

Authorize implementation of exactly one bounded local fixture-backed prototype under `planning-inbox/m14-fixture-read-prototype-task-proposal.md`.

## Basis

The decision is supported by:

- accepted M7 contract set v0.1;
- accepted OR-D1 through OR-D6 and OR-A4 M14 rulings;
- completed post-M13 audit reconciliation;
- complete M14 requirements and hostile-path plans;
- direct bounded review of the exact Hermes source files recorded in `planning-inbox/m14-hermes-lineage-review-2026-07-12.md`;
- no blocking conflict between Hermes claim/evidence precedent and the M14 contract.

## Authorized Prototype Boundary

The prototype may be:

- local-only;
- fixture-backed;
- in-memory;
- deterministic;
- stdlib-first unless a dependency is explicitly justified;
- tested against C2 fixtures and sanitized C00 evidence artifacts;
- accompanied by repository test-proof metadata.

The prototype may implement only the request families and behaviors explicitly authorized by the accepted contract and exact task proposal.

## Not Authorized

This decision does not authorize:

- a network listener;
- real MCP registration;
- production API deployment;
- Postgres, schema, migrations, or persistence;
- provider calls or live ingestion;
- additional paid requests;
- customer/private data;
- overlays;
- reports or report-safe customer references;
- provider cross-check implementation;
- recurring capture;
- dashboards;
- strategy, recommendation, workflow-task, or conclusion storage;
- automatic promotion or canonicalization;
- direct SQL or credentials for LLMs/agents.

## Proof Boundary

Passing prototype tests may prove bounded contract behavior on fixtures only.

It must not be restated as proof of database, transaction, concurrency, network, production authorization, deployment, or customer-data enforcement.

High-consequence hostile-path results must use the accepted proof-class, execution-surface, and proof-strength labels.

## Stop Conditions

Stop implementation and return for owner review if:

- the exact task proposal cannot be followed without expanding scope;
- a database, network listener, MCP registration, provider transport, persistence, customer data, overlay, or report path appears necessary;
- required caveats can be detached from evidence;
- model-authored content can alter authority/review state;
- cross-scope reads or handle enumeration cannot be made fail-closed;
- any test claims a stronger proof surface than it actually exercises.
