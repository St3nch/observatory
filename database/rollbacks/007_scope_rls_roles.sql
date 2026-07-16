-- observatory-db4: {"version":"007","direction":"rollback","responsibility":"scope_rls_roles","paired_path":"database/migrations/007_scope_rls_roles.sql","required_prior":"007","resulting_version":"006","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_governance","obs_capture","obs_evidence","obs_raw","obs_audit","obs_security","obs_read"],"destructive":"disposable_only"}

DROP POLICY IF EXISTS db4_scope_write_probe_ingest_policy ON obs_security.db4_scope_write_probe;
DROP TABLE IF EXISTS obs_security.db4_scope_write_probe;

DROP POLICY IF EXISTS raw_manifest_ingest_policy ON obs_raw.raw_manifest;
DROP POLICY IF EXISTS raw_manifest_scope_policy ON obs_raw.raw_manifest;
ALTER TABLE obs_raw.raw_manifest DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS observation_ingest_policy ON obs_evidence.observation;
DROP POLICY IF EXISTS observation_reader_policy ON obs_evidence.observation;
ALTER TABLE obs_evidence.observation DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS candidate_observation_scope_policy ON obs_evidence.candidate_observation;
ALTER TABLE obs_evidence.candidate_observation DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS capture_package_scope_policy ON obs_capture.capture_package;
ALTER TABLE obs_capture.capture_package DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS panel_run_scope_policy ON obs_capture.panel_run;
ALTER TABLE obs_capture.panel_run DISABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS governed_target_reader ON obs_governance.governed_target;
ALTER TABLE obs_governance.governed_target DISABLE ROW LEVEL SECURITY;

DROP OWNED BY observatory_test_migrator;
DROP OWNED BY observatory_test_ingest;
DROP OWNED BY observatory_test_reader;
DROP OWNED BY observatory_test_auditor;
DROP OWNED BY observatory_test_security_reader;
DROP OWNED BY observatory_test_backup;

DROP ROLE IF EXISTS observatory_test_migrator;
DROP ROLE IF EXISTS observatory_test_ingest;
DROP ROLE IF EXISTS observatory_test_reader;
DROP ROLE IF EXISTS observatory_test_auditor;
DROP ROLE IF EXISTS observatory_test_security_reader;
DROP ROLE IF EXISTS observatory_test_backup;
