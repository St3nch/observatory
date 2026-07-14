# DB-4 Security, Credentials, Restart, and Owner-Action Runbook

Status: planning runbook; owner-approved artifact inventory; not operational authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-4 — Database Hammer Harness and Migration Specification

## Purpose

Define the future owner-controlled security and operational sequence for an exact
DB-4 implementation. This runbook does not create a credential, inspect a password,
start or stop PostgreSQL, restart `ob-dev`, refresh a connector, create a database,
or authorize any action.

## Security invariants

1. No password or secret appears in Git, MCP arguments, MCP results, logs, proof
   metadata, screenshots, chat, or committed test fixtures.
2. PostgreSQL binaries, host, port, operator, maintenance database, protected names,
   disposable prefix, roots, timeouts, and capability class are fixed configuration.
3. Callers cannot submit executables, commands, SQL, connection strings, environment
   values, role names, grants, passwords, or arbitrary paths.
4. Default capability is `inspection_only`.
5. A running server, available credential, existing database, or registered tool never
   creates authority.
6. Production is unsupported and rejected.
7. The owner controls every service and connector restart.
8. There is no self-update, self-edit, self-restart, service-control, or capability-
   escalation MCP tool.

## Planned non-secret configuration

Proposed implementation-owned configuration keys:

| Key | Meaning | Safe exposure |
|---|---|---|
| `OB_DEV_POSTGRES_BIN_DIR` | fixed PostgreSQL binary directory | presence plus sanitized fixed path |
| `OB_DEV_POSTGRES_HOST` | fixed local host | safe configured value |
| `OB_DEV_POSTGRES_PORT` | fixed port | safe configured value |
| `OB_DEV_POSTGRES_MAINTENANCE_DATABASE` | protected maintenance DB | safe name |
| `OB_DEV_POSTGRES_OPERATOR` | fixed operator identity | safe name; never auth material |
| `OB_DEV_POSTGRES_PASSWORD_ENV_VAR` | fixed name of the password-bearing variable | variable name and presence boolean only |
| `OB_DEV_POSTGRES_CAPABILITY_CLASS` | closed capability value | safe value |
| `OB_DEV_POSTGRES_AUTHORITY_REFERENCE` | accepted decision path for active class | sanitized path |
| `OB_DEV_POSTGRES_GOVERNED_DATABASE` | fixed future governed name | `observatory` |
| `OB_DEV_POSTGRES_DISPOSABLE_PREFIX` | fixed disposable prefix | `observatory_test_` |
| `OB_DEV_POSTGRES_MIGRATION_ROOT` | fixed root beneath Observatory | safe contained path |
| `OB_DEV_POSTGRES_PROFILE_ROOT` | fixed root beneath Observatory | safe contained path |
| `OB_DEV_POSTGRES_BACKUP_ROOT` | bounded owner-controlled artifact root | safe root identifier/path only |
| `OB_DEV_POSTGRES_PROOF_ROOT` | bounded working proof root | safe root identifier/path only |

Implementation may choose fixed constants instead of environment configuration for
values that should never vary. The public contract remains unchanged.

The actual password-bearing environment variable name is owner-selected once during
the implementation gate and then configured as a fixed name. Its value is never read
for health, tooling-status, registry, or configuration inspection.

## Credential custody

The owner alone:

- creates or selects the local PostgreSQL operator credential;
- places the secret in the fixed process environment outside the repositories;
- starts the `ob-dev` process with that environment;
- rotates or removes the secret;
- confirms the secret is absent from shell history, Git, files, logs, and chat.

The project steward may verify only:

- the configured variable name;
- presence as a boolean;
- authenticated success/failure result code;
- sanitized failure category.

The project steward must never request the password value.

## Functional-role credential posture

DB-4 test-role profiles should prefer fixed local role setup that does not expose
passwords to MCP. If role login credentials are required for a real disposable
hammer:

- each credential variable name is fixed by the accepted profile;
- the owner sets values outside Git;
- tools receive only the profile ID;
- results report boolean presence and sanitized role identity;
- direct credential echo, environment dump, or connection string is forbidden;
- missing role credentials block the profile before any partial execution.

DB-4 may create only fixed disposable test roles after separate implementation
authorization. Governed roles remain DB-5 work.

## Secret redaction contract

Every PostgreSQL subprocess result passes a centralized secret-exposure review before
serialization.

The review must suppress or fail on:

- exact configured secret values;
- common password/key/token assignment forms;
- URI user-info;
- connection strings;
- environment dumps;
- command lines containing secret-bearing arguments;
- PostgreSQL authentication hashes;
- unbounded stack traces;
- raw process environment.

A redaction match returns `blocked_secret_exposure` or fails the operation with
unsafe stdout/stderr omitted. Replacing a secret with mask characters is insufficient
when surrounding material remains sensitive.

Tests use synthetic sentinels only.

## Binary and endpoint posture

Allowed binaries are derived beneath one fixed directory:

- `psql.exe`;
- `pg_isready.exe`;
- `pg_dump.exe`;
- `pg_restore.exe`.

Implementation verifies regular files, expected names, contained paths, and supported
PostgreSQL major 18 before mutation eligibility.

Host is local and fixed. A non-local host requires a future owner decision and is not
part of DB-4. The caller cannot override host or port.

## Authority binding

A mutation-shaped tool requires:

- active capability class;
- exact accepted authority-reference path;
- operation permitted by that decision;
- expected server fingerprint;
- expected database class/name/marker;
- expected schema or migration state where applicable;
- exact path/SHA inputs;
- confirmation digest where destructive.

Checking that a decision file exists is necessary but not sufficient. The
implementation must compare the requested operation against a closed operation set
bound to the configured decision.

Unknown or ambiguous authority fails closed.

## Pre-implementation owner gate

Before any `ob_dev` edit, the owner must accept exact SHA-256 values for:

- the DB-4 gap matrix;
- the exact `ob_dev` implementation specification;
- the migration/harness specification;
- this runbook;
- the DB-4 readiness review.

The owner decision must explicitly authorize:

- the exact 17-path `ob_dev` implementation manifest;
- version 0.5.0;
- the exact 28-tool registry;
- the exact future 46-path Observatory implementation manifest;
- local credential setup without disclosure;
- permitted disposable PostgreSQL actions;
- migration/profile fixture scope;
- real disposable hammer proof;
- owner restart/connector refresh;
- continued prohibition of the governed database and DB-5.

## Future implementation sequence

### Step 1 — before-image

Record through read-only inspection:

- `ob_dev` commit, branch, clean status, version, Python, framework;
- current 32-tool names/count and generic execution false;
- current roots;
- current endpoint;
- existing 57-test/Ruff baseline;
- PostgreSQL binary presence only, without a server call if not authorized.

No credential is needed for code implementation or fixture tests.

### Step 2 — code implementation

Implement only the accepted 17 `ob_dev` paths. Keep capability default
`inspection_only`. Run fixture/unit/schema validation. Commit locally with the exact
manifest. Do not restart automatically.

### Step 3 — owner credential setup

Only after the code commit is reviewed, the owner configures:

- fixed non-secret values;
- the password-bearing environment value;
- `inspection_only` capability;
- the exact accepted implementation decision reference.

The owner confirms no secret was written into either repository.

### Step 4 — owner restart

The owner:

1. records current healthy endpoint details;
2. stops the existing local `ob-dev` process using the normal owner-controlled
   process;
3. starts the committed server through `C:\dev\ob-dev\start.ps1`;
4. leaves PostgreSQL service control outside MCP;
5. verifies `http://127.0.0.1:8781/mcp`;
6. verifies the fixed ngrok route `https://ob-dev.ngrok.dev/mcp`;
7. refreshes the ChatGPT Desktop connector catalog.

The project steward does not perform these owner-only actions.

### Step 5 — post-restart inspection

Verify:

- version 0.5.0;
- total tool count 60;
- PostgreSQL tool count 28;
- exact registry digest;
- exact three roots;
- generic execution false;
- capability `inspection_only`;
- mutation enabled false;
- protected/governed names and disposable prefix;
- no service-control or generic execution tool.

Then run tooling status, readiness, and identity only to the degree the implementation
decision permits.

### Step 6 — capability transition

The owner separately sets the exact DB-4 capability named by the implementation
decision. A restart may be required if configuration is process-bound.

The steward rechecks health, authority reference, server fingerprint, and protected
names before any disposable action.

### Step 7 — disposable proof

Use the accepted tools only:

- create one exact marked disposable database;
- create an accepted bounded test-role profile;
- validate exact migration/rollback pairs;
- apply exact candidates;
- run fixed profiles and expected broken candidates;
- create/restore/verify only if `restore_proof_authorized` is explicitly included;
- reconcile identity after any timeout;
- drop only the exact marked disposable target.

No generic PowerShell, shell, Python, or SQL execution is a fallback.

## Failure recovery

### Connector or endpoint failure

- stop at the failed verification step;
- record endpoint, version/commit, and sanitized error;
- verify local endpoint before ngrok;
- verify ngrok before connector refresh;
- do not repeat restart loops blindly;
- keep mutation disabled.

### Registry mismatch

- do not enable a mutation class;
- compare live names/schemas to the accepted registry digest;
- return to the reviewed code state;
- correct only through a new exact code review/commit.

### Credential failure

- report missing/rejected status only;
- do not display or request the value;
- owner repairs the process environment;
- no retry after partial mutation without database identity reconciliation.

### PostgreSQL timeout

- treat outcome as unknown;
- re-read server/database/migration identity through inspection tools;
- do not blindly retry create/drop/reset/apply/rollback/restore;
- record the reconciliation result.

### Disposable cleanup failure

- preserve proof of failure;
- do not target a prefix-only or marker-missing database;
- owner reviews the live inventory;
- no generic database command is authorized as a shortcut.

### ob-dev regression

Before restart, return to the last healthy committed `ob_dev` version through an
owner-reviewed local Git action. After restart, disable mutation and restore the last
healthy committed service version. No MCP self-rollback tool exists.

## Proof and logging

Safe proof metadata may record:

- tool and schema digest;
- capability and database classes;
- safe database identity/marker;
- authority path;
- code commit;
- migration/profile paths and SHA-256;
- timestamps;
- result codes;
- before/after fingerprints;
- secret-exposure review;
- bounded evidence path.

It must not record:

- secret values;
- connection strings;
- raw SQL;
- full command lines;
- raw dumps;
- customer/private/provider payloads;
- strategy, conclusions, recommendations, or LLM reasoning.

## Stop conditions

Stop and return to the owner if:

- a secret must cross the MCP boundary;
- PostgreSQL major is not 18;
- a non-local endpoint is required;
- service control appears necessary in MCP;
- the live registry differs from 60/28;
- default capability is not `inspection_only`;
- a protected or governed target appears in a mutation request;
- a required file lies outside an accepted manifest;
- a new dependency is required;
- the owner cannot establish a bounded backup/proof root;
- a timeout cannot be reconciled safely;
- generic execution appears to be the only path forward.

## Manual push posture

The owner performs every push. The steward may create reviewed local commits only in
`ob_dev` and `observatory`. The `ob_dev` repository currently has no remote, so
no push command is proposed for it.

## DB-5 prohibition

Even after successful DB-4 disposable proof:

- `observatory` remains a protected database name;
- governed roles are not created;
- governed migrations are not executed;
- no evidence is persisted;
- `governed_bootstrap_authorized` remains blocked;
- DB-5 requires a new exact owner decision.

## Final rule

Secrets stay with the owner, service control stays with the owner, and every
database mutation stays behind an exact class, identity, authority, and proof gate.
