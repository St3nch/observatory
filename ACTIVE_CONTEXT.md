# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-14

---

## Current Phase

The Observatory has accepted the exact DB-4 planning package and entered bounded phased DB-4 implementation:

```text
DB-1 is trusted and complete.
DB-2 is trusted, accepted, and complete.
DB-3 is trusted, accepted, and complete.
DB-4 is active for exact phased implementation and disposable PostgreSQL proof.
DB-5 is inactive.
```

Current authority:

```text
decisions/2026-07-14-db4-package-acceptance-and-phased-implementation-authorization.md
```

Observatory v1 remains accepted at the bounded proof-system ceiling by `decisions/2026-07-12-observatory-v1-acceptance.md`.

---

## Active Milestone

```text
DB-4 — Database Hammer Harness and Migration Specification
```

DB-4 now authorizes only the exact phased implementation bound by the accepted package. It does not authorize governed or production database work.

---

## Accepted DB-4 checkpoint

The owner accepted commit `90e6cecec19a8ed3e4bd241b37ff575b55a826b1` and these exact immutable planning artifacts:

```text
planning-inbox/db4-dormant-postgres-gap-and-disposition-matrix.md
sha256 a65919ace9da12c16b7dcc3aa7b8262c1150f2acbc2dc521c91ca7c2ee055a2a

planning-inbox/db4-exact-ob-dev-implementation-package-specification.md
sha256 b44711fe80a1967ddf3d5413ce150fcc5d56ca7f61ddb5d8f42747c63d9ce14a

planning-inbox/db4-migration-harness-and-proof-package-specification.md
sha256 9aff671e31fe94dabe5acca6a6631b14f8197a7c85ad55115caced354c7dad2e

planning-inbox/db4-security-credentials-restart-and-owner-action-runbook.md
sha256 8c08648051a2b88c58d5999f861596c79e8a479f68f02e6061586111edb86b7f

planning-inbox/db4-owner-readiness-review.md
sha256 1a2cfd0ff9f30be9ca793fc386a218deb3710860cd83f36ae294a354fd431c92
```

DB-3 is now the last trusted completed database milestone. The accepted DB-3 artifacts and DB-2 freeze remain immutable foundations. The five retired DB-3/DB-4 artifacts remain permanently absent and prohibited from restoration or reuse.

---

## Current Task

Execute the accepted DB-4 package in its fixed phases:

1. implement the exact 17-path `ob_dev` package, version `0.5.0`, and exact 28-tool expansion to the expected 60-tool registry;
2. validate and commit `ob_dev` independently;
3. have the owner restart `ob_dev` and refresh the connector;
4. implement the exact 46-path Observatory migration/harness package;
5. validate and commit Observatory independently;
6. have the owner perform required PostgreSQL credential and service actions without exposing secrets;
7. execute only the exact disposable `observatory_test_` migration, rollback, hammer, backup/restore, and cleanup proof;
8. stop on any failed phase and preserve exact proof;
9. prepare a later DB-4 closure proposal only after all accepted proof gates pass.

---

## Authorized Work

Only work explicitly named by the accepted DB-4 package is authorized:

- exact package-defined `ob_dev` source and tests;
- exact 28 PostgreSQL tools and expected 60-tool registry;
- exact package-defined Observatory migration, rollback, fixture, profile, validator, and test paths;
- owner-controlled credentials, PostgreSQL service actions, `ob_dev` restart, and connector refresh;
- one protected, marked disposable PostgreSQL substrate using the `observatory_test_` prefix;
- exact-path and expected-SHA migration validation and execution;
- package-defined migration, role, concurrency, hammer, backup, restore, rollback, cleanup, and proof profiles;
- exact staged manifests and separate commits;
- manual owner pushes.

---

## Immediate Non-Goals and Prohibitions

Do not start or create:

- the governed database named `observatory`;
- governed or production roles, migrations, or persistence;
- production or production-like deployment;
- real evidence persistence;
- synthetic persistence outside the exact disposable fixtures;
- provider integration, provider calls, or paid pulls;
- ingestion, capture, or raw provider payload storage;
- customer records, customer first-party analytics, or private data;
- recurring capture or recurring work;
- autonomous spend;
- public API/MCP exposure;
- dashboard or operator-console work;
- strategy, recommendation, conclusion, score-as-truth, or report-state storage;
- any path, dependency, tool, database, profile, or capability outside the accepted package;
- DB-5 planning, activation, implementation, or execution.

---

## Stop Conditions

Stop immediately on any:

- changed path outside the exact manifest;
- unexpected tool or tool-count mismatch;
- authority, caller-identity, capability, or confirmation mismatch;
- protected-name attempt;
- disposable prefix or marker mismatch;
- migration path or SHA mismatch;
- credential or secret exposure;
- PostgreSQL version, binary, host, or port mismatch;
- test, Ruff, import, authority-sync, integrity, diff-check, hammer, rollback, restore, or cleanup failure;
- proof-class inconsistency.

Do not improvise beyond the accepted manifest.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions. The connected LLM interprets at read time. Accepted conclusions promote out to the owning consumer.

Customer records and customer first-party analytics stay outside Observatory durable storage. LLMs and agents receive shaped evidence through typed boundaries, not direct SQL access or database credentials.

Provider disagreement is first-class evidence. Proprietary provider scores are provider-attributed testimony, not facts about the web.

Rights and retention fail closed. Hammer tests are hard gates. Fixture proof is not real PostgreSQL proof.

---

## Current Completion State

Trusted and closed:

```text
M0, M0.1, M1 through M20
DB-1
DB-2
DB-3
```

Active:

```text
DB-4 — exact phased implementation and disposable PostgreSQL proof
```

Inactive:

```text
DB-5 through DB-10
```

No milestone implies the next milestone.

---

## Tool Posture

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation, Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- `chatgpt_mcp` is a read-only Git reference; local staging and commits are limited to `ob_dev` and `observatory`.
- The package-defined PostgreSQL tools may be implemented and registered only through the accepted DB-4 phases.
- Owner actions remain owner actions. Tool availability never widens authority.
