# DB-3 Future ob-dev PostgreSQL Control-Plane Contract

Status: planning candidate; not authority
Version: 0.1
Date: 2026-07-14
Milestone: DB-3 — Postgres Operational Boundary and Physical Schema Specification
Implementation authority: none
Target implementation milestone: DB-4 only after a separate owner gate

## Purpose

Freeze the exact future bounded PostgreSQL capability surface required in ob-dev
before DB-4 implementation begins.

The owner requires one coherent, tested expansion and one planned restart/connector
refresh cycle. Database work must not depend on emergency server edits, generic
execution, arbitrary SQL, or a forgotten control plane.

This contract does not authorize:

- editing C:\dev\ob-dev;
- changing the current 32-tool registry;
- restarting ob-dev or ngrok;
- starting PostgreSQL;
- creating databases, roles, credentials, or migration files;
- executing SQL, migrations, hammers, backup, or restore;
- DB-4 activation.

## Authority and lineage

Controlling DB-3 authority:

- decisions/2026-07-14-db2-freeze-acceptance-and-db3-planning-authorization.md
- POST_V1_DATABASE_ROADMAP.md
- hammers/hammer-matrix-v0-2.md
- hammers/acceptance-gate-policy-v0-2.md
- hammers/per-hammer-result-register-v0-1.md
- planning-inbox/db3-fresh-postgres-design-specification-v0-1.md

Historical planning input only:

- planning-inbox/db1-ob-dev-database-control-plane-requirements.md

Current ob-dev truth at drafting:

| Item | Current state |
|---|---|
| Service | ob-dev |
| Version | 0.4.0 |
| Tool count | 32 |
| Generic execution | false |
| Local endpoint | http://127.0.0.1:8781/mcp |
| Connector endpoint | https://ob-dev.ngrok.dev/mcp |
| Roots | ob_dev, observatory, chatgpt_mcp |
| Git mutation | ob_dev and observatory only |
| PostgreSQL tools | none |

Current truth is context, not permission to change the service.

## Non-negotiable architecture

1. Fixed configured binaries only.
2. Fixed configured host and port only.
3. Password read only from an owner-controlled environment variable at call time.
4. No password, secret, token, connection string, or environment value in arguments
   or results.
5. No arbitrary SQL argument.
6. No arbitrary shell, PowerShell, Python, module, script, command, executable path,
   Git command, or GitHub command.
7. Database identifiers use grammar [a-z_][a-z0-9_]* and maximum 63 characters.
8. Migration execution uses an exact registered-root relative path and expected
   SHA-256.
9. Every mutation is database-class and capability-class gated.
10. Protected system and governed database names fail closed.
11. Disposable identity requires both allowed name and database marker proof.
12. Results are structured, deterministic, bounded, and secret-redacted.
13. Tool availability never creates roadmap authority.
14. Governed-database mutation remains impossible until DB-5 owner authorization.
15. No production mode exists.

## Registry delta and health contract

This candidate defines 28 new PostgreSQL tools.

If the current 32 tools remain unchanged, the expected total after DB-4 implementation
is 60. Health must derive the count from the live registry rather than hardcoding it.

Future health fields:

| Field | Required meaning |
|---|---|
| service | ob-dev |
| version | New version accepted during DB-4 |
| framework | Derived installed framework version |
| tool_count | Derived total registered tools |
| generic_execution | Always false |
| postgres_tool_count | Derived registered PostgreSQL tool count; expected 28 for this contract |
| postgres_capability_class | Active class from the closed vocabulary below |
| postgres_configured | Whether all required fixed non-secret settings exist |
| postgres_mutation_enabled | Derived boolean; false unless class and authority admit it |
| roots | Existing fixed roots |
| registry_digest | Deterministic digest of registered tool names and public schemas |

A health response never proves that a database action is authorized.

## Capability classes

Closed ordered vocabulary:

| Class | Permitted surface |
|---|---|
| inspection_only | Read-only tooling/readiness/identity/settings/inventory |
| postgres_disposable_only | Inspection plus disposable create/reset/drop and bounded test roles |
| migration_spec_proof_only | Disposable migration validation/execution and migration/role hammer profiles |
| governed_bootstrap_authorized | Exact DB-5 governed create/role/migration actions after owner decision |
| real_ingestion_authorized | Later exact real-ingestion actions after DB-9 gates |
| restore_proof_authorized | Exact backup/restore proof actions for the separately authorized target class |

Rules:

- default is inspection_only;
- missing or unknown class fails closed;
- classes do not accumulate authority beyond their named surface;
- restore_proof_authorized does not imply governed mutation or ingestion;
- real_ingestion_authorized does not imply production;
- production is absent from the vocabulary;
- class changes require owner-controlled configuration and a decision reference;
- a tool checks the active class again at execution time;
- credentials or existing objects cannot substitute for class authorization.

## Database classes

Closed vocabulary:

| Class | Meaning |
|---|---|
| protected_system | postgres, template0, template1, and configured protected names |
| disposable_postgres | DB-4 test database with accepted prefix and marker |
| governed_local | Future durable local Observatory database |
| production | Always rejected |

Proposed configured values:

- governed database name: observatory
- disposable prefix: observatory_test_
- protected names: postgres, template0, template1, observatory
- maximum disposable databases per operation: 1
- caller cannot override the protected list or prefix

The governed name appears in the protected list until governed_bootstrap_authorized
is active under an exact DB-5 decision.

## Fixed configuration contract

Non-secret configuration:

| Setting | Requirement |
|---|---|
| postgres_bin_dir | Fixed absolute owner-configured directory |
| psql_path | Derived beneath fixed bin directory; caller cannot supply |
| pg_isready_path | Derived beneath fixed bin directory |
| pg_dump_path | Derived beneath fixed bin directory when backup gate opens |
| pg_restore_path | Derived beneath fixed bin directory when restore gate opens |
| host | Fixed configured local host |
| port | Fixed configured port |
| maintenance_database | Fixed protected maintenance database |
| superuser_name | Fixed configured operator identity; never returned with secret |
| password_env_var_name | Fixed name only; value never returned |
| governed_database_name | Fixed protected name |
| disposable_prefix | Fixed value |
| migration_root | Future earned exact path beneath observatory root |
| hammer_profile_root | Future earned exact path beneath observatory root |
| backup_root | Future accepted bounded artifact path |
| statement_timeout | Fixed bounded duration by operation class |
| operation_timeout | Fixed bounded duration by operation class |

Configuration output reports presence and safe paths/versions only. It must not report
environment values or credential-bearing connection details.

## Common validation types

### Identifier

- string;
- 1 through 63 characters;
- grammar [a-z_][a-z0-9_]*;
- no quoting, dots, spaces, dashes, uppercase, wildcards, path characters, or SQL
  punctuation;
- normalized value must equal caller value.

### Repository path

- repository-relative UTF-8 text;
- exact registered root;
- required suffix by operation;
- no absolute path;
- no drive letter;
- no parent traversal;
- no symlink escape;
- file must exist and be regular;
- exact SHA-256 required for executable migration/profile input.

### Authority reference

- repository-relative decision path;
- fixed decisions/ prefix;
- no URL or free-form phrase;
- file existence and accepted status must be checkable;
- tool does not infer that the decision covers the requested action;
- DB-4 disposable proof may use the exact future DB-4 decision;
- governed actions require the exact DB-5 or later decision.

### Database identity expectation

Required mutation input:

- database_name;
- database_class;
- expected_server_fingerprint;
- expected_database_marker;
- expected_schema_version where applicable;
- expected_capability_class.

Mismatch blocks before mutation.

### SHA-256

- lowercase 64-character hexadecimal;
- compared against bytes read by the server;
- mismatch returns blocked_sha_mismatch;
- caller cannot request bypass.

## Common result envelope

Every PostgreSQL tool returns:

| Field | Meaning |
|---|---|
| operation | Fixed tool operation name |
| status | ok, blocked, failed, timed_out |
| result_code | Closed operation-specific code |
| capability_class | Active class observed during execution |
| database_class | Target class or none |
| database_name | Sanitized identifier or null |
| server_fingerprint | Non-secret deterministic fingerprint or null |
| database_marker | Non-secret bounded marker or null |
| started_at | UTC timestamp |
| finished_at | UTC timestamp |
| return_code | Process return code where applicable |
| timed_out | Boolean |
| authority_reference | Sanitized decision path or null |
| evidence | Operation-specific structured fields |
| warnings | Closed bounded warning codes |
| secret_exposure_review | pass or fail |
| stdout | Bounded sanitized output only when contract explicitly permits |
| stderr | Bounded sanitized error category/message without secret echo |
| truncated | Boolean |

Results never contain:

- passwords or environment values;
- connection strings;
- raw command lines containing secrets;
- arbitrary SQL;
- filesystem paths outside configured safe path reporting;
- provider/customer/private content;
- raw database dumps;
- stack traces with environment values.

A failed secret-exposure review makes the entire operation failed and suppresses
unsafe output.

## Inspection tools

Inspection tools require inspection_only or any later class. They perform no mutation.

### postgres_tooling_status

Input: none.

Returns:

- configured fixed binary presence;
- binary versions;
- safe configured host/port;
- password environment variable set: boolean only;
- active capability class;
- protected names;
- governed name;
- disposable prefix;
- PostgreSQL tool registry digest/count.

Must not call the server if basic binary/config validation fails.

### postgres_readiness

Input:

- expected_server_fingerprint: optional for first inspection;
- timeout profile: fixed internal default only.

Returns:

- ready boolean;
- readiness result code;
- sanitized server endpoint class;
- server fingerprint when available.

No caller-selected timeout or executable.

### postgres_server_identity

Input:

- expected_server_fingerprint: optional.

Returns:

- server version number/string;
- major version;
- server fingerprint;
- encoding;
- timezone;
- selected safe settings;
- mismatch status.

It rejects an unsupported major version for mutation eligibility.

### postgres_database_inventory

Input:

- include_system: boolean, default false.

Returns bounded items:

- name;
- database class;
- marker presence;
- owner identifier;
- encoding;
- connection allowed;
- protected boolean.

No sizes, paths, secrets, or arbitrary query filters.

### postgres_role_inventory

Input: none.

Returns bounded role facts needed for least-privilege proof:

- role name;
- login boolean;
- superuser boolean;
- create database/role booleans;
- replication/bypass-RLS booleans;
- membership names.

No password/hash/auth configuration output.

### postgres_extension_inventory

Input:

- database_name;
- expected database identity for non-protected target.

Returns:

- installed extension name/version/schema;
- allowed/blocked disposition under accepted spec.

No install/update operation.

### postgres_setting_read

Input:

- setting_name from a fixed allowlist.

Initial allowlist:

- server_version;
- server_version_num;
- server_encoding;
- TimeZone;
- password_encryption;
- max_connections;
- statement_timeout;
- lock_timeout;
- idle_in_transaction_session_timeout;
- search_path;
- default_transaction_isolation;
- standard_conforming_strings;

Returns name, sanitized value, source, and expected-disposition code.

Arbitrary setting names are rejected.

### postgres_schema_inventory

Input:

- database_name;
- database identity expectation;
- include_system: false only for Observatory proof.

Returns bounded schemas and relation counts plus owner/privilege summaries. It does
not return row data.

### postgres_migration_history_read

Input:

- database_name;
- database identity expectation;
- expected migration relation identity.

Returns immutable migration records:

- version;
- path;
- SHA-256;
- direction;
- applied_at;
- code commit;
- authority reference;
- result.

It refuses an unknown migration-history shape.

## Disposable lifecycle tools

Require postgres_disposable_only or migration_spec_proof_only and exact DB-4
authority. They can never target governed_local or production.

### postgres_create_disposable_database

Input:

- database_name;
- expected disposable prefix;
- expected server fingerprint;
- requested database marker;
- authority reference.

Validation:

- strict identifier;
- prefix match;
- not protected;
- database absent;
- one database only;
- capability/authority match.

Returns before/after inventory, marker, and operation result.

### postgres_drop_disposable_database

Input:

- database identity expectation;
- exact confirmation digest derived from server fingerprint, database name, marker,
  and requested operation;
- authority reference.

Validation:

- class is disposable_postgres;
- prefix and marker both match;
- not protected/governed;
- no active unapproved sessions;
- exact confirmation digest.

Returns bounded before/after inventory. No generic drop mode exists.

### postgres_reset_disposable_database

Input:

- database identity expectation;
- exact confirmation digest;
- authority reference.

Behavior:

- performs the fixed accepted reset lifecycle;
- preserves operation proof outside the target;
- never accepts custom SQL or cleanup steps.

### postgres_create_bounded_test_roles

Input:

- disposable database identity expectation;
- fixed role profile ID from allowlist;
- authority reference.

Initial profile IDs:

- db4_minimal_migration_roles_v1;
- db4_scope_isolation_roles_v1;
- db4_typed_read_roles_v1.

Caller cannot submit role names, passwords, grants, or SQL.

## Migration inspection and execution tools

Validation may run under inspection_only. Execution requires
migration_spec_proof_only for disposable targets or governed_bootstrap_authorized
for an exact later governed action.

### postgres_validate_migration_file

Input:

- root: observatory only;
- path beneath future earned migration root;
- expected_sha256;
- migration_direction: forward or rollback;
- expected paired path and SHA-256;
- expected migration version;
- target database class;
- authority reference.

Returns:

- actual SHA-256;
- containment/suffix/encoding checks;
- forbidden-pattern findings;
- transaction posture;
- parsed bounded metadata;
- paired-file consistency;
- executable: false or true under active class.

Validation never executes SQL.

### postgres_apply_migration_file

Input:

- disposable or governed database identity expectation;
- exact validated forward path and SHA-256;
- exact rollback path and SHA-256;
- expected schema version;
- expected code commit;
- authority reference;
- exact confirmation digest.

Rules:

- no raw SQL;
- one file;
- transaction and stop-on-error;
- dirty-tree governed execution rejected;
- governed target requires governed_bootstrap_authorized and exact DB-5 authority;
- result records before/after schema fingerprint and transaction outcome.

### postgres_apply_rollback_file

Same shape as forward execution, with:

- expected current migration version;
- exact target prior version;
- rollback SHA;
- dependency/precondition result;
- disposable only during DB-4;
- governed rollback forbidden unless a later exact owner decision permits it.

### postgres_migration_status

Input:

- database identity expectation;
- expected accepted migration manifest digest.

Returns:

- applied/pending/divergent status;
- exact version/path/hash comparison;
- dirty/unknown migration block.

### postgres_constraint_inventory

Input: database identity expectation plus optional fixed namespace allowlist.

Returns relation, constraint name/type, validated/enforced state, and bounded
definition digest. It does not return arbitrary SQL definitions.

### postgres_index_inventory

Returns index identity, relation, uniqueness, validity, and bounded definition digest.
No row statistics or arbitrary query plan.

### postgres_privilege_inventory

Returns bounded role/schema/relation/function privilege facts for accepted application
namespaces. No credential/auth secret data.

## Hammer profile tools

All profiles are fixed repository-owned entry points. Caller supplies no command,
module, test name, Python argument, SQL, or concurrency primitive.

Common input:

- profile_id from allowlist;
- database identity expectation;
- accepted code commit;
- migration manifest digest;
- hammer IDs expected;
- authority reference;
- expected profile file SHA-256.

Common output conforms to per-hammer-result-register-v0-1.md and includes one
structured result per hammer execution.

### postgres_run_hammer_profile

General accepted database-invariant profile groups.

### postgres_run_migration_hammer_profile

Forward, rollback, broken-candidate, partial-failure, and recovery profiles.

### postgres_run_role_hammer_profile

Least-privilege, RLS, direct CRUD denial, raw-locator denial, and bypass rejection.

### postgres_run_concurrency_hammer_profile

Fixed concurrent attempts for duplicate capture, admission, evidence mint, policy
assignment, append-only, and audit-first behavior.

### postgres_run_restore_verification_profile

Fixed restored-database semantic checks. Execution remains blocked until the restore
gate permits it.

Rules:

- fixture/in-memory results cannot be labeled real PostgreSQL proof;
- disposable execution may earn real_postgres_disposable_pass only;
- governed execution may earn real_local_database_pass only under its exact gate;
- intentionally broken candidates remain recorded as expected failures;
- profiles write evidence only to accepted bounded roots;
- a tool success is not automatic hammer acceptance.

## Backup and restore tools

These are implemented in the coherent batch only if DB-4 scope accepts them, but
remain disabled until restore_proof_authorized.

### postgres_create_bounded_backup

Input:

- governed or disposable database identity expectation;
- fixed backup profile ID;
- exact bounded destination identifier beneath configured backup root;
- expected schema version/migration digest;
- authority reference.

Returns:

- artifact identifier;
- size;
- SHA-256;
- database identity/class;
- schema/migration binding;
- creation timestamps;
- semantic manifest path.

No cloud upload, arbitrary destination, or encryption claim.

### postgres_restore_to_disposable_database

Input:

- exact backup artifact path beneath bounded root;
- expected backup SHA-256;
- new disposable database identity/marker;
- authority reference;
- exact confirmation digest.

Restores only to disposable_postgres. Governed overwrite is impossible.

### postgres_verify_semantic_restore

Input:

- restored disposable identity;
- source backup manifest SHA-256;
- fixed verification profile ID;
- authority reference.

Must verify:

- schema/migration history;
- evidence identity resolution;
- raw manifest/hash continuity;
- audit continuity;
- scope isolation;
- append-only constraints;
- role/read boundaries.

## Protected-operation error vocabulary

Minimum closed result codes:

- blocked_capability_class;
- blocked_authority_missing;
- blocked_authority_mismatch;
- blocked_identifier_invalid;
- blocked_protected_database;
- blocked_database_class;
- blocked_database_identity_mismatch;
- blocked_disposable_marker_missing;
- blocked_confirmation_mismatch;
- blocked_binary_missing;
- blocked_binary_version;
- blocked_server_identity;
- blocked_credentials_missing;
- blocked_path_outside_root;
- blocked_path_suffix;
- blocked_sha_mismatch;
- blocked_dirty_tree;
- blocked_migration_divergence;
- blocked_schema_version;
- blocked_profile_unknown;
- blocked_profile_sha_mismatch;
- blocked_secret_exposure;
- blocked_active_sessions;
- failed_subprocess;
- failed_transaction;
- timed_out;
- ok.

Unknown errors fail closed and return a sanitized classification.

## Audit and proof requirements

Every mutation attempt records bounded proof metadata outside Observatory evidence:

- operation ID;
- tool name/version/schema digest;
- capability class;
- database class and safe identity;
- authority reference;
- code commit;
- migration/profile paths and SHA-256;
- start/finish time;
- result code;
- before/after fingerprints;
- secret-exposure review;
- evidence path.

Proof metadata contains no credential, connection string, raw SQL, raw payload,
customer/private content, strategy, recommendation, or LLM reasoning.

## ob-dev self-proof requirements

Before owner restart/refresh:

- unit tests for every input validator and result shape;
- protected-name and governed-name rejection;
- disposable marker mismatch rejection;
- traversal, symlink escape, suffix, and SHA mismatch rejection;
- setting allowlist rejection;
- raw SQL and arbitrary executable injection rejection;
- missing/wrong credential redaction;
- binary path/version mismatch;
- capability-class and database-class mismatch;
- timeout and subprocess error sanitization;
- deterministic registry digest and health count;
- fixture result-shape proof;
- intentionally broken migration/profile failures;
- disposable create/apply/rollback/drop real-Postgres proof when DB-4 authorizes it;
- no generic execution introduced;
- complete existing ob-dev regression suite.

The coherent expansion must be committed in ob_dev before the owner restarts it.
The Observatory repo does not stage or commit ob_dev changes.

## Planned restart and connector recovery procedure

Owner-controlled procedure after an accepted, tested DB-4 implementation commit:

1. Record current healthy ob-dev version, commit, tool count, registry digest, roots,
   endpoint, and capability class.
2. Confirm the ob_dev worktree contains only the reviewed committed expansion.
3. Confirm existing and new unit tests pass.
4. Confirm the default capability class is inspection_only.
5. Stop the current local ob-dev server through the owner's normal bounded process.
6. Start the committed server through the repository's documented fixed entrypoint.
7. Verify local health at http://127.0.0.1:8781/mcp.
8. Start or verify the owner's fixed ngrok route for ob-dev.ngrok.dev.
9. Verify connector health at https://ob-dev.ngrok.dev/mcp.
10. Refresh the ChatGPT Desktop connector/tool catalog.
11. Call health and list_roots.
12. Confirm version, total tool count, postgres tool count, registry digest,
    generic_execution false, and exact roots.
13. Run inspection-only tooling status and readiness.
14. Do not enable disposable or governed mutation merely because tools appear.

If any verification fails:

- stop after the exact failed step;
- record the failed tool/endpoint/result;
- do not retry an identical mutation;
- keep governed mutation disabled;
- return to the last known committed healthy ob_dev version through an owner-reviewed
  recovery action;
- reverify local endpoint before ngrok;
- reverify ngrok before refreshing the connector;
- never improvise generic execution or edit the live server blindly.

There is no MCP self-restart, self-update, self-edit, or capability-escalation tool.

## DB-4 entry and exit dependency

DB-4 may implement this contract only after a separate owner decision names:

- exact ob_dev implementation scope;
- exact tool registry contract/version;
- disposable PostgreSQL authority;
- allowed credential setup;
- allowed test database prefix/class;
- migration/profile fixture scope;
- required restart/refresh.

DB-4 cannot close until:

- the accepted tools exist and match this public contract or an owner-accepted
  revision;
- the owner completes restart/refresh;
- health/registry evidence matches;
- default capability remains inspection_only;
- disposable lifecycle works through bounded tools;
- exact-path SHA-bound migration/rollback works;
- mandatory hammers can fail against intentionally broken candidates;
- real disposable passes are recorded honestly;
- no governed database or real evidence exists.

## DB-5 boundary

Governed bootstrap remains blocked until a separate DB-5 owner decision authorizes:

- exact governed database creation;
- exact role creation/profile;
- exact accepted migration paths and SHA-256;
- exact capability transition;
- exact validation and hammer profiles.

Manual ad-hoc bootstrap is not the default. If a bounded manual exception is ever
needed, it requires its own explicit owner decision.

## Non-authorizations

No current tool registry change. No ob_dev edit, install, restart, connector refresh,
PostgreSQL action, database, role, credential, SQL, migration, hammer, backup,
restore, persistence, provider, capture, customer/private data, raw storage,
recurring work, DB-4, production, or implementation is authorized.

## Final rule

Build the control plane once, make every dangerous mode visibly gated, and make a
missing authority easier to detect than a missing semicolon.
