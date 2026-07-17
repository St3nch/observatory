# DB-4 R5 Frozen ob-dev Compatibility Review

Status: accepted R5 preparation record
Date: 2026-07-17
Authority: `decisions/2026-07-17-db4-r5-live-campaign-gate-preparation-authorization.md`
Frozen ob-dev commit reviewed: `90083b90a3262b16b7232df213f39545e40f1a82`
Observatory baseline: `b4c02c87cbb27955245e89c2553491c1373a9435`

## Purpose

Determine whether the frozen `ob-dev` can execute the one owner-gated disposable DB-4 campaign without source changes. This review authorizes no execution and no `ob-dev` mutation.

## Compatibility verdict

```text
NOT READY FOR OWNER EXECUTION GATE
```

The frozen implementation provides several core capabilities, but five blocking gaps prevent an honest full campaign.

## Capability matrix

| Required capability | Verdict | Evidence | Gate effect |
|---|---|---|---|
| Atomic candidate DDL and history in one transaction | compatible | `postgres_atomic.run_atomic_migration()` begins one session transaction, configures it, acquires the advisory lock, fingerprints before/after, executes the candidate, inserts history, and commits; exceptions roll back | no blocker |
| Real catalog fingerprint | compatible | `postgres_fingerprint.fingerprint_query_bundle()` covers schemas, relations, columns, constraints, indexes, triggers, functions, policies, grants, and default privileges, then canonical SHA-256 hashing | no blocker |
| Allowlisted profile loading and SHA binding | compatible | `postgres_profiles.load_profile()` restricts paths to eight accepted profiles, rejects symlinks/path escape, hashes the profile, and verifies every bound fixture SHA | no blocker |
| Bounded role switching and role posture validation | partially compatible | six accepted NOLOGIN roles are allowlisted; `SET LOCAL ROLE` is generated only for those roles; role state rejects superuser/BYPASSRLS/CREATEDB/CREATEROLE/REPLICATION | blocker G4 remains because backup behavior is not directly exercised |
| Append-only redacted result records | compatible for per-profile records | `write_result_record()` validates profile SHA, redacts, creates with `O_EXCL`, mode `0600`, flushes, and fsyncs; records code commits and dirty-tree state | blocker G5 remains for campaign-level register and clean-tree precondition |
| Disposable marker enforcement | incompatible for profile execution | migration apply/reset/drop paths verify the marker, but `run_profile()` and `run_broken_candidate_profile()` only validate the database-name prefix and never call marker validation | blocker G1 |
| Accepted authority and operation-class enforcement | incompatible | `load_authority_record()` can validate accepted status and operation class, but no execution path calls it; profile/migration paths only validate authority-reference syntax | blocker G2 |
| Complete hostile-candidate execution | incompatible | the frozen broken-candidate executor has detector/residue maps for the original eight check IDs only; R3 contains sixteen concrete fixtures | blocker G3 |
| All-role cross-scope behavioral proof | incomplete | reader and ingest behavior execute under `SET LOCAL ROLE`; role catalog inspection covers six roles, but backup cross-scope reads are not directly attempted | blocker G4 |
| Campaign register and one-campaign identity | incomplete | per-profile result records use a default campaign ID, but no writer for `campaign-register.schema.json` exists and the campaign ID is not supplied by the MCP profile tool surface | blocker G5 |

## Blocking gaps

### G1 — profile execution lacks disposable-marker verification

Required correction in a separately accepted `ob-dev` decision:

- verify the existing marker before every behavioral, role/RLS, concurrency, migration-history, broken-candidate, cleanup, restore, backup, and result-emission operation;
- fail closed on missing, stale, mismatched, or unreadable marker;
- bind emitted database identity to the verified marker.

### G2 — authority helper is unused

Required correction in a separately accepted `ob-dev` decision:

- load the exact authority document before every mutation or live proof operation;
- require `Status: accepted`;
- require the exact operation class for creation/reset, migration, rollback, profile, broken-candidate, backup/restore, cleanup, and drop;
- reject a merely well-formed path that lacks accepted authority.

### G3 — only eight of sixteen concrete hostile fixtures are executable

Required correction in a separately accepted `ob-dev` decision:

- add bounded detector/residue definitions for the eight R3 fixtures not in the current executor;
- keep fixture selection allowlisted and SHA-bound;
- preserve atomic candidate execution and zero-history/zero-residue verification;
- emit one reviewable result item for every concrete fixture.

The eight currently unsupported fixtures are:

```text
009_search_path_hijack.sql
009_owner_bypass_rls.sql
009_rls_without_force.sql
009_missing_with_check.sql
009_default_privilege_leak.sql
009_public_schema_create.sql
009_not_valid_constraint.sql
009_cross_scope_foreign_key.sql
```

### G4 — backup-role cross-scope behavior is not directly proved

Required correction in a separately accepted `ob-dev` decision or an already-supported bounded profile extension:

- execute same-scope and cross-scope reads under `observatory_test_backup`;
- prove the accepted backup visibility rule for every protected base relation and typed-read surface;
- record active role, scope GUC, row counts, and SQLSTATE where applicable;
- do not substitute catalog inspection for behavior.

### G5 — campaign-level evidence and clean-tree preconditions are incomplete

Required correction before owner execution:

- add append-only emission and validation for one `campaign-register.schema.json` record binding all profile execution IDs;
- use one owner-selected unique campaign ID across all records;
- require clean Observatory and `ob-dev` trees before the campaign begins;
- resolve the protected untracked `audits/kaizen_to_slash_goal_prompt.md` outside this batch without modifying or deleting it here;
- preserve failed and blocked profile records rather than overwriting them.

## Capabilities that do not require ob-dev changes

The frozen implementation already supports:

- disposable database-name prefix enforcement;
- marker creation and strong marker identity validation on control/migration paths;
- SHA-bound migration files;
- one-transaction DDL plus history insertion;
- deterministic catalog fingerprinting;
- bounded role names and `SET LOCAL ROLE` generation;
- allowlisted closed profiles;
- per-profile append-only redacted result emission;
- cleanup-check linkage;
- code-commit and dirty-tree recording.

## Required next authority

R5 must not accept the live campaign now. The next technical action is a separate, exact-path `ob-dev` compatibility correction decision covering only G1–G5. After those corrections are implemented, validated, committed, and the connector is refreshed at the already planned restart boundary, this compatibility review must be repeated.

Only a blocker-free repeat review may promote the owner-decision draft into an accepted execution decision.
