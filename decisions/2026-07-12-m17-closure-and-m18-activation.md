# Decision — Close M17 and Activate M18 Planning

Status: accepted decision
Date: 2026-07-12
Milestone transition: M17 -> M18

## Decision

Close M17 — Owned Telemetry Overlay Proof.

Activate M18 — Recurring Watch Panel Planning — for planning only.

## Accepted M17 evidence

- accepted M17 overlay proof contract and rulings;
- exact synthetic fixture-backed proof authorization;
- implementation commit `7cdcdc7cbaeff7c68c30653f91231d7fe3fe7964`;
- corrective test commit `04ef29c980d9c655acc739693b944fa5b6a6faeb`;
- owner-local result: 184 tests passed;
- proof classification: bounded synthetic fixture/in-memory enforcement proof.

M17 proved request-local synthetic alignment, explicit discard/no-storage status, no overlay value return, no evidence promotion, no cross-scope access, and fail-closed handling for private identity, files, screenshots, exports, causality, recommendations, and canonical ingestion.

## M17 limits preserved

M17 did not prove or authorize real private telemetry, secure memory wiping, production infrastructure logging, file/connector intake, authentication, persistence, database enforcement, production API/MCP behavior, integration, or deployment.

## M18 authority

M18 may plan:

- watch panel design;
- cadence policy;
- budget policy;
- stop conditions;
- stale and coverage warnings;
- approval/rejection criteria for recurring capture.

M18 does not authorize:

- scheduler implementation;
- recurring capture execution;
- autonomous spend;
- provider calls;
- broad crawling or scraping;
- credentials;
- Postgres, schema, or migrations;
- production API/MCP;
- production integrations;
- customer data, reports, strategy, or recommendations.

Recurring capture execution remains outside v1 unless the owner explicitly changes the roadmap.
