-- observatory-db4: {"version":"006","direction":"rollback","responsibility":"audit_append_only","paired_path":"database/migrations/006_audit_append_only.sql","required_prior":"006","resulting_version":"005","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_audit"],"destructive":"disposable_only"}

DROP TRIGGER IF EXISTS raw_manifest_audit_required ON obs_raw.raw_manifest;
DROP TRIGGER IF EXISTS citation_handle_audit_required ON obs_evidence.citation_handle;
DROP TRIGGER IF EXISTS evidence_identity_audit_required ON obs_evidence.evidence_identity;
DROP TRIGGER IF EXISTS observation_audit_required ON obs_evidence.observation;
DROP FUNCTION IF EXISTS obs_audit.db4_probe_unpaired_consequential_write();
DROP TABLE IF EXISTS obs_audit.db4_consequential_probe;
DROP FUNCTION IF EXISTS obs_audit.require_same_transaction_audit();
DROP TABLE IF EXISTS obs_audit.audit_supersession;
DROP TABLE IF EXISTS obs_audit.audit_event;
