# DB-4 R4 Test/Profile Completion Authorization

Date: 2026-07-17
Status: Accepted owner authorization

## Decision

The owner instruction to continue after the successful R3 push authorizes Route C Batch R4 only.

R4 completes and de-stales the static PostgreSQL test/profile layer by:

1. deleting the five retired `_v1` profiles;
2. deleting the five stale tests that load only those profiles;
3. creating the six planned contract tests:
   - `test_db4_history_atomicity.py`
   - `test_db4_profile_manifest.py`
   - `test_db4_broken_candidate_manifest.py`
   - `test_db4_result_register.py`
   - `test_db4_cleanup.py`
   - `test_db4_security_posture.py`
4. updating the conformance manifest and package validator so the retired artifacts cannot return silently;
5. synchronizing active authority documents to R4.

## Proof boundary

These six tests are static or contract tests. They verify repository structure, profile ownership, SHA binding, result-schema closure, cleanup references, migration-history contracts, and declared security posture. They do not constitute PostgreSQL behavioral proof and may not be used to close DB-4.

## Explicit exclusions

R4 does not authorize:

- PostgreSQL execution or connection;
- creation, reset, restore, or deletion of a disposable database;
- R5 live-campaign gate preparation;
- changes to `ob-dev`;
- wiring unsupported hostile-candidate check IDs into the frozen executor;
- DB-5;
- providers, customer/private data, recurring work, or production work.

## Stop condition

R4 stops when:

- no retired `_v1` profile exists;
- no test loads a retired profile;
- all six planned tests exist and pass;
- the conformance manifest reports 6 current tests, 0 required-absent tests, 8 active profiles, and 0 stale profiles;
- authority sync and the full static/unit suite pass;
- the exact R4 path set is committed.

No batch implies the next batch. R5 remains separately bounded.
