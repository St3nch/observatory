-- observatory-db4: {"version":"010","direction":"rollback","responsibility":"recovery_verification","paired_path":"database/migrations/010_recovery_verification.sql","required_prior":"010","resulting_version":"008","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_meta","obs_governance","obs_evidence","obs_audit"],"destructive":"disposable_only"}

DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_migration_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_concurrency_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_role_rls_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_audit_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_append_only_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_raw_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_evidence_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_admission_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_cleanup_scope_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_seed_role_rls_probe();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_restore_scope_isolation();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_restore_evidence_resolution();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_restore_history_continuity();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_restore_schema_continuity();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_concurrent_migration_verify();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_concurrent_migration(integer);
DROP FUNCTION IF EXISTS obs_meta.db4_probe_concurrent_identity_mint(integer);
DROP FUNCTION IF EXISTS obs_meta.db4_probe_rollback_history_explicit();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_duplicate_version_changed_sha();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_failed_candidate_no_history();
DROP FUNCTION IF EXISTS obs_meta.db4_probe_forward_history_atomic();
DROP FUNCTION IF EXISTS obs_evidence.db4_probe_append_only_mutation();
DROP FUNCTION IF EXISTS obs_evidence.db4_probe_duplicate_evidence_identity();
DROP FUNCTION IF EXISTS obs_governance.db4_probe_admission_without_retention();
DROP FUNCTION IF EXISTS obs_governance.db4_probe_admission_without_rights();

DROP TABLE IF EXISTS obs_meta.db4_concurrent_migration_history;
DROP TABLE IF EXISTS obs_meta.db4_concurrent_migration_effect;
DROP TABLE IF EXISTS obs_meta.db4_concurrent_identity_probe;
DROP TABLE IF EXISTS obs_meta.db4_migration_probe_history;
DROP TABLE IF EXISTS obs_meta.db4_migration_probe_effect;
DROP TABLE IF EXISTS obs_meta.db4_evidence_probe;
DROP TABLE IF EXISTS obs_meta.db4_admission_probe;
DROP TABLE IF EXISTS obs_meta.restore_verification;
