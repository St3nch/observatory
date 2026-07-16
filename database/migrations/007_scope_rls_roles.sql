-- observatory-db4: {"version":"007","direction":"forward","responsibility":"scope_rls_roles","paired_path":"database/rollbacks/007_scope_rls_roles.sql","required_prior":"006","resulting_version":"007","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_governance","obs_capture","obs_evidence","obs_raw","obs_audit","obs_security","obs_read"],"destructive":"none"}

DO $$
DECLARE role_name text;
BEGIN
    FOREACH role_name IN ARRAY ARRAY[
        'observatory_test_migrator',
        'observatory_test_ingest',
        'observatory_test_reader',
        'observatory_test_auditor',
        'observatory_test_security_reader',
        'observatory_test_backup'
    ]
    LOOP
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
            EXECUTE format(
                'CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT',
                role_name
            );
        END IF;
    END LOOP;
END;
$$;

REVOKE ALL ON SCHEMA public FROM observatory_test_migrator, observatory_test_ingest, observatory_test_reader, observatory_test_auditor, observatory_test_security_reader, observatory_test_backup;

GRANT USAGE ON SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit, obs_security, obs_read TO observatory_test_migrator;
GRANT USAGE ON SCHEMA obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit TO observatory_test_ingest;
GRANT USAGE ON SCHEMA obs_read TO observatory_test_reader;
GRANT USAGE ON SCHEMA obs_audit, obs_read TO observatory_test_auditor;
GRANT USAGE ON SCHEMA obs_security TO observatory_test_security_reader;
GRANT USAGE ON SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit TO observatory_test_backup;

GRANT SELECT ON ALL TABLES IN SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit TO observatory_test_migrator;
GRANT INSERT ON obs_audit.audit_event, obs_audit.audit_supersession TO observatory_test_ingest;
GRANT INSERT ON obs_capture.capture_package, obs_capture.capture_package_transition, obs_capture.capture_event, obs_capture.capture_event_transition, obs_capture.validation_result, obs_capture.provider_testimony, obs_capture.provider_testimony_transition TO observatory_test_ingest;
GRANT INSERT ON obs_evidence.observed_artifact_reference, obs_evidence.observed_artifact_transition, obs_evidence.candidate_observation, obs_evidence.candidate_observation_transition, obs_evidence.admission_transition, obs_evidence.observation, obs_evidence.observation_transition, obs_evidence.evidence_identity, obs_evidence.evidence_identity_transition, obs_evidence.citation_handle, obs_evidence.citation_handle_transition TO observatory_test_ingest;
GRANT INSERT ON obs_raw.raw_manifest, obs_raw.raw_manifest_transition, obs_raw.raw_payload_identity, obs_raw.raw_payload_transition, obs_raw.opaque_artifact_token, obs_raw.opaque_artifact_token_transition, obs_raw.raw_integrity_observation TO observatory_test_ingest;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA obs_capture, obs_evidence, obs_raw, obs_audit TO observatory_test_ingest;
GRANT SELECT ON obs_audit.audit_event, obs_audit.audit_supersession TO observatory_test_auditor;
GRANT SELECT ON ALL TABLES IN SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit TO observatory_test_backup;

ALTER TABLE obs_governance.governed_target ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_governance.governed_target FORCE ROW LEVEL SECURITY;
CREATE POLICY governed_target_reader ON obs_governance.governed_target
FOR SELECT TO observatory_test_reader, observatory_test_auditor, observatory_test_backup
USING (scope_key = current_setting('ob.scope_key', true));

ALTER TABLE obs_capture.panel_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_capture.panel_run FORCE ROW LEVEL SECURITY;
CREATE POLICY panel_run_scope_policy ON obs_capture.panel_run
FOR ALL TO observatory_test_ingest, observatory_test_reader, observatory_test_auditor, observatory_test_backup
USING (scope_key = current_setting('ob.scope_key', true))
WITH CHECK (scope_key = current_setting('ob.scope_key', true));

ALTER TABLE obs_capture.capture_package ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_capture.capture_package FORCE ROW LEVEL SECURITY;
CREATE POLICY capture_package_scope_policy ON obs_capture.capture_package
FOR ALL TO observatory_test_ingest, observatory_test_reader, observatory_test_auditor, observatory_test_backup
USING (scope_key = current_setting('ob.scope_key', true))
WITH CHECK (scope_key = current_setting('ob.scope_key', true));

ALTER TABLE obs_evidence.candidate_observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_evidence.candidate_observation FORCE ROW LEVEL SECURITY;
CREATE POLICY candidate_observation_scope_policy ON obs_evidence.candidate_observation
FOR ALL TO observatory_test_ingest, observatory_test_reader, observatory_test_auditor, observatory_test_backup
USING (scope_key = current_setting('ob.scope_key', true))
WITH CHECK (scope_key = current_setting('ob.scope_key', true));

ALTER TABLE obs_evidence.observation ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_evidence.observation FORCE ROW LEVEL SECURITY;
CREATE POLICY observation_reader_policy ON obs_evidence.observation
FOR SELECT TO observatory_test_reader, observatory_test_auditor, observatory_test_backup
USING (scope_key = current_setting('ob.scope_key', true));
CREATE POLICY observation_ingest_policy ON obs_evidence.observation
FOR INSERT TO observatory_test_ingest
WITH CHECK (scope_key = current_setting('ob.scope_key', true));

ALTER TABLE obs_raw.raw_manifest ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_raw.raw_manifest FORCE ROW LEVEL SECURITY;
CREATE POLICY raw_manifest_scope_policy ON obs_raw.raw_manifest
FOR SELECT TO observatory_test_auditor, observatory_test_backup
USING (
    EXISTS (
        SELECT 1
        FROM obs_evidence.observation observation
        WHERE observation.observation_key = raw_manifest.observation_key
          AND observation.scope_key = current_setting('ob.scope_key', true)
    )
);
CREATE POLICY raw_manifest_ingest_policy ON obs_raw.raw_manifest
FOR INSERT TO observatory_test_ingest
WITH CHECK (
    EXISTS (
        SELECT 1
        FROM obs_evidence.observation observation
        WHERE observation.observation_key = raw_manifest.observation_key
          AND observation.scope_key = current_setting('ob.scope_key', true)
    )
);

CREATE TABLE obs_security.db4_scope_write_probe (
    probe_key text PRIMARY KEY CHECK (probe_key LIKE 'db4-%'),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);
ALTER TABLE obs_security.db4_scope_write_probe ENABLE ROW LEVEL SECURITY;
ALTER TABLE obs_security.db4_scope_write_probe FORCE ROW LEVEL SECURITY;
CREATE POLICY db4_scope_write_probe_ingest_policy ON obs_security.db4_scope_write_probe
FOR INSERT TO observatory_test_ingest
WITH CHECK (scope_key = current_setting('ob.scope_key', true));
GRANT INSERT ON obs_security.db4_scope_write_probe TO observatory_test_ingest;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit, obs_security, obs_read FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit, obs_security, obs_read FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit, obs_security, obs_read FROM PUBLIC;
