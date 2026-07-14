# Active Context - The Observatory

Status: authority
Authority: current operating context
Purpose: tell fresh sessions what phase the repo is in and what work is currently allowed
Last updated: 2026-07-14

---

## Current Phase

The Observatory has accepted and closed DB-3 and entered bounded DB-4 package preparation:

```text
DB-1 is trusted and complete.
DB-2 is trusted, accepted, and complete.
DB-3 is trusted, accepted, and complete.
DB-4 is active for exact implementation-package preparation only.
DB-5 is inactive.
```

Current transition authority:

```text
decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md
```

Observatory v1 remains accepted at the bounded proof-system ceiling by
`decisions/2026-07-12-observatory-v1-acceptance.md`.

---

## Active Milestone

```text
DB-4 — Database Hammer Harness and Migration Specification
```

DB-4 authority is preparation only. It may produce an exact, reviewable
implementation-package proposal derived from accepted DB-3. It grants no
implementation, PostgreSQL, database, migration, tooling, restart, hammer-execution,
backup, restore, or persistence authority.

---

## Accepted DB-3 checkpoint

The owner accepted the exact DB-3 planning package:

```text
planning-inbox/db3-accepted-input-traceability-matrix.md
sha256 db2ae41552aa4fc2c88b450f86f8070fb8e3cc023fb93fc7e7a39ab625aadc98

planning-inbox/db3-fresh-postgres-design-specification-v0-1.md
sha256 9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e

planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md
sha256 d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec
```

DB-3 is now the last trusted completed database milestone. The accepted planning
artifacts are immutable specifications; they are not executable implementation
artifacts.

The exact accepted DB-2 freeze remains immutable:

```text
path: planning-inbox/db2-physical-data-contract-freeze-specification.md
version: 0.2.1
sha256: 7c24d38ea8e7634dea8cf52cd7b85b49eda18b8ecde5a00c74b6303809c17891
```

The five retired DB-3/DB-4 artifacts remain permanently absent and prohibited from
restoration, salvage, reuse, copying, paraphrased reconstruction, or memory-based
reconstruction.

---

## Current Task

Prepare one exact DB-4 implementation package for owner review:

1. derive only from accepted DB-1, DB-2, and DB-3 authority;
2. propose the exact `ob_dev` source/test edit manifest and 28-tool registry;
3. propose exact non-executable migration-specification, rollback, disposable-harness,
   hammer-profile, proof, credential, restart, and validation inventories;
4. preserve protected database names, capability gates, optimistic SHA controls,
   redaction, and fail-closed behavior;
5. stop for a separate owner decision before creating any implementation artifact.

---

## Immediate Non-Goals

Do not start:

- PostgreSQL startup, shutdown, restart, or control
- database creation, reset, drop, or connection
- role or credential creation
- secrets or credential setup
- SQL or DDL
- executable migration or rollback files
- migration validation or execution
- disposable database lifecycle
- real PostgreSQL hammers
- database-control-plane source implementation or tool registration
- `ob_dev` restart or connector refresh
- backup or restore execution
- synthetic or real persistence
- provider calls or paid pulls
- recurring capture
- production API/MCP exposure
- dashboard or operator console work
- customer or private data handling
- raw capture or storage
- customer-facing reports
- strategy, recommendation, conclusion, or report-state storage
- DB-5 planning or activation

The package must become exact before implementation can become a question.

---

## Current Boundary Posture

The Observatory stores observations, not conclusions.

The connected LLM interprets at read time.

Accepted conclusions promote out to the owning consumer.

Customer records and customer first-party analytics stay outside Observatory durable
storage. LLMs and agents receive shaped evidence through typed boundaries, not direct
SQL access or database credentials.

Provider disagreement is first-class evidence. Proprietary provider scores are
provider-attributed testimony, not facts about the web.

Rights and retention fail closed. Hammer tests are hard gates, and real database
claims require a separately authorized real substrate.

Killed ancestor concepts remain killed.

---

## Current Completion State

Trusted and closed:

```text
M0, M0.1, M1 through M20
DB-1 — Post-v1 Audit Reconciliation and Ruling Closure
DB-2 — Physical Data-Contract Freeze
DB-3 — Postgres Operational Boundary and Physical Schema Specification
```

Active for exact implementation-package preparation only:

```text
DB-4 — Database Hammer Harness and Migration Specification
```

Inactive:

```text
DB-5
```

Planned and inactive:

```text
DB-5 through DB-10
```

No milestone implies the next milestone.

---

## Tool Posture

- Use only the custom `ob-dev` MCP for local repository inspection, bounded mutation,
  Git, and fixed validation profiles.
- Generic shell, PowerShell, Python, SQL, and arbitrary Git execution remain disabled.
- `chatgpt_mcp` is a read-only Git reference; local staging and commits are limited to
  `ob_dev` and `observatory`.
- Do not implement or register PostgreSQL tools during DB-4 package preparation.
- Tool availability never creates roadmap authority.
