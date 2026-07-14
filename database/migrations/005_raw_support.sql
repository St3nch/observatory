-- observatory-db4: {"version":"005","direction":"forward","responsibility":"raw_support","paired_path":"database/rollbacks/005_raw_support.sql","required_prior":"004","resulting_version":"005","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_raw"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_raw;
CREATE TABLE observatory_raw.support_manifest(manifest_id text PRIMARY KEY, observation_id text NOT NULL REFERENCES observatory_evidence.observation(observation_id), content_sha256 text NOT NULL, retention_status text NOT NULL CHECK (retention_status IN ('retained','purged_with_proof','blocked_by_rights')), locator_exposed boolean NOT NULL DEFAULT false CHECK (locator_exposed = false));
COMMIT;
