# DB-4 Proof, Security, and Operations Package v0.1

Status: planning candidate; no execution authority
Milestone: DB-4 remediation

## Purpose

Define the durable proof, security, cleanup, network, credential, and owner-operation requirements for the next DB-4 implementation and disposable campaign.

## Proof record model

### Local execution record

Every invocation of a DB-4 profile creates one immutable local execution record under an owner-configured ignored evidence root.

Required fields:

```text
schema_version
execution_id
campaign_id
profile_id
profile_sha256
check_id
hammer_ids
proof_class
result
started_at
finished_at
observatory_commit
ob_dev_commit
observatory_dirty_state
ob_dev_dirty_state
authority_reference
authority_sha256
server_identity
database_name
database_oid_or_identity
database_class
marker_version
marker_authority
capability_class
session_user
active_role
migration_versions_paths_and_sha256
before_fingerprint
after_fingerprint
expected_behavior
observed_behavior
sqlstate_or_semantic_code
cleanup_attempted
cleanup_result
cleanup_verified
evidence_paths
redaction_review
known_limits
supersedes_execution_id
review_state
```

No record may contain passwords, connection-string credentials, raw payloads, private content, prompts, reasoning, full rejected SQL output containing secrets, or filesystem/storage locators outside approved repository-relative evidence paths.

### Campaign register

One campaign register binds:

- exact owner decision;
- exact repository commits;
- exact PostgreSQL identity;
- exact database class/name/marker;
- exact role set;
- exact profile set and hashes;
- campaign start and stop conditions;
- every execution ID;
- cleanup and final inventory;
- owner/steward review outcome.

Campaign records append execution IDs. They are never rewritten to remove failed runs.

### Supersession

A correction creates a separate supersession record naming:

- prior execution ID;
- replacement execution ID;
- reason;
- authority/reference;
- reviewer;
- timestamp.

The prior record remains immutable and reviewable.

## Result truth rules

- A profile call is not a hammer pass.
- A structural precondition is not a behavioral pass.
- Every failed, blocked, and cleanup-failed check remains in the result set.
- A campaign cannot pass when one mandatory check is missing.
- A campaign cannot pass when a result has no proof class.
- A campaign cannot pass when the database identity or marker is missing.
- A campaign cannot pass when either repository is dirty unless the exact gate explicitly authorizes and records the dirty path set; the planned DB-4 campaign does not.
- A campaign cannot pass when redaction review is incomplete.
- Chat output is not closure evidence.

## Accepted record promotion

After the campaign:

1. validate every local record against the JSON schema;
2. run secret and locator scanning over the complete record envelope;
3. verify all referenced commits and file hashes;
4. verify campaign completeness;
5. generate compact redacted repository records;
6. stage exact accepted record paths;
7. review the full diff;
8. commit without altering prior accepted records.

Accepted records live beneath:

```text
database/proof/accepted/<campaign-id>/
```

## Authority binding

Startup environment must name one repository-relative accepted authority decision.

The runtime must verify:

- file exists beneath the Observatory root;
- path is not symlinked or escaped;
- exact file SHA is recorded at startup;
- decision status is accepted;
- decision names the active milestone;
- decision authorizes the requested operation class;
- decision authorizes the database class and prefix;
- decision has not been superseded by current authority files;
- `ACTIVE_CONTEXT.md` points to the same current authority.

A string that merely resembles a decision path is not authority.

## Confirmation digests

Confirmation digests protect against accidental destructive invocation only.

They do not create authority.

A destructive operation requires all of:

- accepted authority;
- matching capability;
- protected-name check;
- database class check;
- prefix check;
- marker identity check;
- exact operation digest;
- cleanup profile context where applicable.

## Disposable marker

Marker contents:

```text
marker_version
database_name
database_oid_or_identity
server_system_identifier_or_approved_identity
host_class
port
database_class
creation_authority_reference
creation_authority_sha256
created_at
campaign_id
```

Verification occurs before every reset, migration, rollback, hammer, backup, restore, role mutation tied to the campaign, and drop.

A missing or mismatched marker blocks.

## Database classification

Allowed classes:

```text
protected_system
disposable_postgres
governed_local
production
```

Operational rules:

- `protected_system`: read-only inventory only;
- `disposable_postgres`: mutation only under accepted DB-4 campaign authority;
- `governed_local`: unsupported until DB-5 owner gate;
- `production`: unsupported and forbidden;
- unknown: unauthorized.

Never classify an unknown database as production merely because its name is unfamiliar.

## Credential custody

- Password is owner-entered into a temporary process environment.
- Password is never supplied as an MCP argument.
- Password is never returned in tool output.
- Password is cleared when the owner stops the process or closes the proof window.
- No password is written to `.env`, Git, proof records, logs, PowerShell history, or repository files.
- Connection URIs are never returned unredacted.
- Errors redact URI user-info and password forms before serialization.

## Network and connector posture

Before any mutation-capable campaign, verify and record:

- exact bind address of `ob-dev`;
- exact tunnel process and destination;
- connector authentication mode;
- whether the tunnel URL is publicly reachable without authentication;
- whether any non-owner client can invoke mutation tools;
- whether credentials/capabilities survive outside the supervised proof window.

Required posture:

- mutation capability is enabled only during an owner-supervised proof window;
- password exists only during that window;
- connector/tunnel is disabled when not needed;
- mutation endpoint must have effective access control before execution;
- if effective authentication cannot be proven, real PostgreSQL mutation is blocked.

## Role lifecycle

Campaign role lifecycle is one recorded operation family:

1. preflight inventory;
2. verify names are in the exact campaign role allowlist;
3. verify absent or exact expected prior state;
4. create NOLOGIN roles with no elevated attributes;
5. apply exact profile grants/memberships;
6. run behavioral role/RLS checks;
7. revoke memberships/grants as required;
8. drop roles;
9. verify absence;
10. record final cluster inventory.

Any unexpected role attribute or membership blocks.

## RLS behavioral posture

Tests must execute with fixed bounded role switching and must record:

- session user;
- active role;
- current scope context;
- same-scope read success;
- cross-scope read returns no rows or uniform denial as specified;
- cross-scope insert/update fails through WITH CHECK;
- table owner and superuser bypass are not counted as proof;
- FORCE RLS is present;
- role lacks BYPASSRLS;
- cleanup is verified.

## Migration operational settings

Every migration session sets transaction-local:

```text
lock_timeout
statement_timeout
idle_in_transaction_session_timeout
search_path
application_name
```

Values are fixed in the accepted profile, not caller-selected.

Migration execution uses a fixed advisory lock key derived from the project/migration domain, not user input.

## Failure handling

On failure:

- transaction rolls back;
- success history is absent;
- failure record is written;
- before/after fingerprint comparison is recorded;
- residue inventory runs;
- cleanup is attempted where safe;
- cleanup result is recorded;
- campaign may continue only when the profile explicitly marks the failure as an expected hostile outcome and cleanup verified;
- unexpected failures stop the campaign.

## Backup and restore honesty

DB-4 may prove a disposable logical/physical backup-and-restore path only if separately authorized in the execution package.

A restore profile must not claim:

- encrypted off-machine backup;
- governed recovery;
- production recovery;
- evidence durability beyond the disposable fixture substrate.

Those belong to later gates.

## Cleanup closure

A campaign is not complete until it records:

- disposable database absent;
- campaign roles absent;
- no application schemas remain in any reused disposable target;
- no leftover fixture/sentinel objects;
- no active capability/password window;
- final database inventory;
- final role inventory;
- proof-record validation;
- protected database names untouched.

## Owner action sequence

The future accepted execution runbook should reduce owner interruption to:

1. ensure PostgreSQL service is running;
2. start `ob-dev` once with accepted capability and authority environment;
3. enter password once into the temporary environment;
4. refresh connector actions once if implementation changed;
5. allow the steward to run the exact campaign;
6. stop `ob-dev` or clear the temporary environment after campaign;
7. manually push accepted commits.

No repeated restart loop is acceptable for profile/check corrections that can be data-driven.
