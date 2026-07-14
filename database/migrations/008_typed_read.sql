-- observatory-db4: {"version":"008","direction":"forward","responsibility":"typed_read","paired_path":"database/rollbacks/008_typed_read.sql","required_prior":"007","resulting_version":"008","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_read"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_read;
CREATE VIEW observatory_read.observation_summary AS SELECT o.evidence_handle, p.scope_id, p.provider, o.observed_at, o.observed_value FROM observatory_evidence.observation o JOIN observatory_capture.capture_package p ON p.package_id=o.package_id;
COMMIT;
