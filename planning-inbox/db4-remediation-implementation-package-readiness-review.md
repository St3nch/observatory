# DB-4 Remediation Implementation Package Readiness Review

Status: owner-ready planning review; not implementation or execution authority
Date: 2026-07-14
Milestone: DB-4 remediation

## Package reviewed

```text
planning-inbox/db4-remediation-exact-implementation-manifest-v0-1.md
planning-inbox/db4-proof-security-and-operations-package-v0-1.md
planning-inbox/db4-one-restart-implementation-and-validation-plan-v0-1.md
```

Foundation:

```text
planning-inbox/db4-audit-remediation-program-v0-1.md
planning-inbox/db4-db3-implementation-traceability-matrix.md
planning-inbox/db4-migration-history-redesign-options.md
planning-inbox/db4-behavioral-hammer-remapping.md
```

## Readiness verdict

```text
ready for exact owner implementation-package decision
not authorized for implementation yet
not authorized for PostgreSQL execution
```

## What the package fixes

The package directly addresses the independent audit findings by requiring:

- replacement of the thin migration set with the full DB-3 relation responsibilities;
- one-session/one-transaction migration plus immutable history;
- advisory locking, safe search path, fixed timeouts, deterministic ownership, and broad fingerprints;
- behavioral rather than catalog-count hammers;
- role/RLS proof under fixed non-superuser role switching;
- broken candidates through the real migration admission path;
- real project concurrency identities rather than a control-table primary key;
- immutable durable result records for pass, fail, blocked, cleanup, and supersession;
- marker identity and authority-file binding;
- full-envelope redaction and secret scanning;
- network/connector reachability and authentication verification;
- exact role lifecycle and cleanup;
- data-driven SHA-bound profiles to reduce owner restart burden;
- one validated implementation restart before campaign execution.

## Scope judgment

The package remains within DB-4.

It does not authorize:

- governed database creation;
- DB-5;
- persisted synthetic or real evidence;
- providers, paid pulls, ingestion, or capture;
- customer/private data;
- recurring work;
- production;
- product API/MCP/dashboard work;
- strategy, recommendation, conclusion, or report persistence.

## Required implementation commits

The later implementation decision should require at least two independently validated commits:

```text
ob-dev implementation commit
Observatory migration/profile/proof package commit
```

The implementation decision must bind the exact path manifests. The later PostgreSQL execution decision must bind the exact resulting commits and profile hashes.

## Required pre-implementation checks

Before editing implementation paths:

- owner accepts exact package paths and permissions;
- `ob-dev` working tree disposition is resolved, including any existing diagnostic detector edit;
- Observatory working tree is clean except the protected untracked audit prompt;
- current authority sync passes;
- no disposable DB-4 database exists;
- no bounded test roles remain;
- no PostgreSQL execution capability is treated as active authority.

## Required pre-restart checks

Before asking the owner to restart:

- complete `ob-dev` tests and Ruff pass;
- complete Observatory tests and authority sync pass;
- profile and proof schemas validate;
- both repositories have exact commits and clean trees;
- final MCP tool inventory is documented;
- network/authentication posture is verified or execution remains blocked;
- exact owner runbook is written;
- no secret exists in Git or proof output.

## Required pre-execution checks

Before creating a disposable database:

- separate exact execution authority exists;
- `ob-dev` has been restarted once on the accepted commit;
- connector actions match the accepted tool inventory;
- PostgreSQL server identity matches;
- password and elevated capability are temporary and owner-supervised;
- authority path and SHA are verified;
- evidence root is configured outside Git;
- campaign and profile manifests are exact and SHA-bound;
- preflight inventory shows no target database or leftover campaign roles.

## Open items that do not block the implementation-package decision

- exact final SQL bytes do not exist yet; implementation authority is required to create them;
- final profile SHA values cannot exist until files are implemented;
- final tool count cannot be frozen until implementation review confirms whether existing tools are retained unchanged;
- restore inclusion in the DB-4 execution campaign remains a later exact execution-package decision;
- the exact tunnel/authentication facts must be verified before mutation, not guessed in planning.

## Stop conditions

Stop implementation on any:

- path outside the accepted manifest;
- omitted DB-3 responsibility;
- schema object without a traceability row;
- weakened fixed-root/no-arbitrary-SQL boundary;
- migration/history split transaction;
- mutable result/history record;
- tool-per-hammer expansion that recreates restart churn;
- test or authority-sync failure;
- secret exposure;
- governed database, DB-5, provider, customer/private data, production, or recurring work.

## Recommended owner ruling

Accept the exact remediation implementation planning package and authorize bounded implementation in two repositories, but keep all PostgreSQL mutation and execution separately gated until the completed implementation commits, profiles, proof schemas, tool inventory, and security posture are reviewed.
