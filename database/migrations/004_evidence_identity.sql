-- observatory-db4: {"version":"004","direction":"forward","responsibility":"evidence_identity","paired_path":"database/rollbacks/004_evidence_identity.sql","required_prior":"003","resulting_version":"004","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_evidence"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_evidence;
CREATE TABLE observatory_evidence.observation(observation_id text PRIMARY KEY, package_id text NOT NULL REFERENCES observatory_capture.capture_package(package_id), evidence_handle text NOT NULL UNIQUE, observed_value jsonb NOT NULL, observed_at timestamptz NOT NULL);
COMMIT;
