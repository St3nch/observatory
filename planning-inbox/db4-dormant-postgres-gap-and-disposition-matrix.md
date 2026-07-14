# DB-4 Dormant PostgreSQL Gap and Disposition Matrix

Status: planning specification; owner-approved artifact inventory; not implementation authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 — Database Hammer Harness and Migration Specification

## Purpose

Reconcile the live dormant PostgreSQL code in `C:\dev\ob-dev` against the exact
accepted DB-3 control-plane contract before any implementation is authorized.

This matrix is descriptive. It does not register a tool, execute SQL, start
PostgreSQL, create a database, handle credentials, create migrations, run hammers,
restart `ob-dev`, or authorize implementation.

## Accepted inputs

- `planning-inbox/db3-future-ob-dev-control-plane-contract-v0-1.md`
  - SHA-256 `d13e83b8fd74fd4c427a3ede92c70e24a252458b80c8abc6531cb5bd92ac2dec`
- `planning-inbox/db3-fresh-postgres-design-specification-v0-1.md`
  - SHA-256 `9b79f0551fac9bbea11bc6e5afbececf48e216e47f41c3554e5806903f666e5e`
- `decisions/2026-07-14-db3-acceptance-closure-and-db4-package-preparation.md`
- live `ob_dev` commit
  `46df253c40b9de03826aa562c744a1943fe52ccf`

## Baseline verification

Read-only verification on the live `ob_dev` worktree found:

- version 0.4.0;
- 32 registered tools;
- generic execution false;
- clean worktree;
- no remote or upstream;
- 57 pytest tests passing;
- Ruff passing;
- five PostgreSQL-related modules importing successfully;
- PostgreSQL wrappers present in `server.py` but not decorated or registered.

The dormant code is review material, not latent authority.

## Current dormant file inventory

| Path | SHA-256 | Current responsibility | DB-4 disposition |
|---|---|---|---|
| `src/ob_dev/settings.py` | `b27e200da867453adf681f2e3d545f56b766f7d06db8bfd3f7b15df9faa2f9ed` | Environment-backed placeholder configuration | revise |
| `src/ob_dev/postgres_runtime.py` | `b84e1f9a06d0d888e19bb251e9a17673afce139aae7c4f11b3e191b35f75fad9` | Binary discovery, readiness, identity, Windows service control | split/revise |
| `src/ob_dev/postgres_control.py` | `4132d02535f9d39369d2632ce80bf2c4d131fe9d2914236f5dfbf9af4f697ec5` | Database lifecycle and migration execution helpers | replace substantially |
| `src/ob_dev/postgres_hammers.py` | `4b64b6f74fe7bd6cfb1cf344dfbc6b5c81becb520448875000eb30452d813d73` | Static hammer catalog and selection | replace with fixed profile execution contract |
| `src/ob_dev/postgres_backup.py` | `b0a3ee76c44eba2bba0b01aacedc591a3a9c5e46ec868e514487148eb05babe3` | Disposable backup and restore helpers | revise |
| `src/ob_dev/server.py` | `52d819621c28b8784117f538cb5eb3da98da26ef8a45ff80673062bb9739667d` | 32 registered tools plus 17 dormant PostgreSQL wrappers | revise |
| `tests/test_postgres_runtime.py` | `78f94802a32dabb850a3597535d08c023b14567d151cd3047701192c5ca3d305` | Runtime and service-control fixture tests | revise |
| `tests/test_postgres_control.py` | `2e9f7aba6883ab90b19b591863d38cfde66a7a7e2fd483c1503214aeb24192b9` | Prefix, lifecycle, inventory, path/SHA fixture tests | replace substantially |
| `tests/test_postgres_hammers.py` | `ff0f797d1436f67f6be2f4ffb9e232ec0ee85148b75665ccc2805b594328e875` | Static catalog-selection tests | replace |
| `tests/test_postgres_backup.py` | `91e33391c4011fc1bc420cdac0d1436e5922258870272bd03a9f215619a4cfd3` | Backup path/hash fixture tests | revise |
| `tests/test_server.py` | `284b912769b5a98193b629ca018cf4e4773e150dd52292d3bbb380c57b809e52` | Exact 32-tool registry and schema safety | expand |
| `README.md` | `2ad83aa54cf3817d56204049461e82bb3d45437046b9317ec811875b1b34fe84` | Current surface and dormant posture | revise only after implementation |
| `pyproject.toml` | `7fe1c9047c403b9d8f2ada26df846f199eb7f9cfd5434bc74c7348344d60923b` | Version 0.4.0 and test/lint configuration | revise only after implementation |

## Structural gaps

| Accepted requirement | Dormant state | Disposition |
|---|---|---|
| 28 exact PostgreSQL tools | 17 dormant wrappers | replace wrapper set with exact 28 |
| Expected total 60 tools | 32 registered only | derive live count after exact registration |
| Registry digest | absent | add deterministic public-schema/name digest |
| Common result envelope | each module has unrelated result models | centralize in new `postgres_contract.py` |
| Capability classes | absent | implement closed six-value vocabulary; default `inspection_only` |
| Database classes | prefix-only boolean | implement protected/disposable/governed/production classification |
| Disposable prefix `observatory_test_` | `obs_tmp_` | replace; old prefix must be rejected |
| Disposable marker | absent | require marker for lifecycle mutation |
| Protected names | partial implicit protection | enforce `postgres`, `template0`, `template1`, `observatory` |
| Governed name protected until DB-5 | not modeled | make unconditional under DB-4 classes |
| Exact authority reference | absent | validate accepted repository decision paths |
| Server fingerprint | absent or incomplete | add deterministic non-secret fingerprint |
| Database identity expectation | absent | require before every mutation |
| Confirmation digest | absent | require for destructive lifecycle and restore operations |
| Secret exposure review | absent | central sanitized envelope and failure suppression |
| Fixed setting allowlist | absent | implement exact accepted list only |
| Role/extension/schema/history inspection | absent | implement in `postgres_inspection.py` |
| Constraint/index/privilege inspection | absent | implement bounded digest-only inspection |
| Bounded test roles | absent | fixed three-profile allowlist |
| Five hammer runners | catalog/selection only | replace with fixed repository-owned profile runners |
| Three backup/restore tools | two differently named helpers | implement exact three accepted names/contracts |
| Owner-controlled restart | dormant service-control wrapper exists | remove service mutation from public/future registry |
| Production absent | not explicit | hard reject production class |
| No arbitrary SQL input | caller does not submit SQL, but internal SQL is scattered | preserve fixed internal statements; central review and tests |
| No caller executable/path | mostly present | bind every path beneath fixed roots with SHA and suffix checks |

## Dormant wrapper disposition

| Current dormant wrapper | Accepted disposition |
|---|---|
| `postgres_create_disposable_backup` | replace with `postgres_create_bounded_backup` |
| `postgres_restore_disposable_backup` | replace with `postgres_restore_to_disposable_database` |
| `postgres_database_inventory` | retain name; replace schema and implementation |
| `postgres_create_disposable_database` | retain name; require exact name, marker, server fingerprint, class, capability, and authority |
| `postgres_drop_disposable_database` | retain name; add identity and confirmation digest |
| `postgres_reset_disposable_database` | retain name; add identity and confirmation digest |
| `postgres_validate_migration_file` | retain name; expand paired-file and metadata validation |
| `postgres_execute_disposable_migration` | remove; replace with separate apply-forward and apply-rollback tools |
| `postgres_hammer_catalog` | do not register; catalog becomes internal fixed metadata |
| `postgres_hammer_selection` | remove; replace with five fixed profile runners |
| `postgres_installation_status` | replace with `postgres_tooling_status` |
| `postgres_readiness` | retain name; replace result contract |
| `postgres_service_status` | keep internal inspection only if needed; not one of the 28 tools |
| `postgres_server_identity` | retain name; replace result contract |
| `postgres_service_control` | prohibit registration and remove from future public surface |
| backup/restore helper-only behavior | add semantic verification as the third accepted tool |
| database/migration helper-only behavior | add the missing inventory, history, role, and test-role contracts |

## Reuse rules

Reuse is allowed only when behavior is re-reviewed against the accepted contract.

Candidate reusable mechanisms:

- fixed executable derivation beneath a configured binary directory;
- direct subprocess argument arrays without a shell;
- bounded timeouts;
- repository-relative path containment;
- lowercase SHA-256 equality;
- Pydantic closed output models;
- current exact-registry and schema tests;
- fixed-root artifact handling.

Reuse is forbidden when it preserves drift:

- `obs_tmp_`;
- caller suffix construction instead of exact identity input;
- service start/stop/restart exposure;
- superuser-only role assumptions;
- unmarked disposable databases;
- unclassified databases;
- independent result shapes;
- raw subprocess output without centralized secret review;
- one combined forward/rollback execution wrapper;
- catalog selection in place of fixed hammer execution.

## Required new module boundaries

Future implementation should create:

- `src/ob_dev/postgres_contract.py` for vocabularies, validators, authority checks,
  identity expectations, result envelopes, redaction, confirmation digests, and
  registry digest support;
- `src/ob_dev/postgres_inspection.py` for the bounded inspection queries and result
  models that do not belong in lifecycle control.

No additional module is admitted unless implementation review proves one of these
boundaries cannot remain coherent.

## Proof debt

The existing 57 tests prove dormant fixture behavior only. They do not prove:

- registered MCP schemas;
- the accepted 28-tool registry;
- real PostgreSQL behavior;
- disposable marker enforcement;
- capability or authority enforcement;
- least-privilege roles;
- migration rollback;
- concurrency;
- semantic restore;
- secret-safe failure behavior under real subprocesses.

No current test may be relabeled as real PostgreSQL proof.

## Final disposition

The dormant implementation is useful scaffolding but not an accepted implementation
candidate. DB-4 must revise it as one coherent batch, preserve the safe fixed-command
mechanisms, delete or quarantine conflicting behavior, and prove the exact public
contract before owner restart.

This artifact creates no implementation authority.
