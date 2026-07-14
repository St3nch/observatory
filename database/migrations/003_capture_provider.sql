-- observatory-db4: {"version":"003","direction":"forward","responsibility":"capture_provider","paired_path":"database/rollbacks/003_capture_provider.sql","required_prior":"002","resulting_version":"003","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_capture"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_capture;
CREATE TABLE observatory_capture.capture_package(package_id text PRIMARY KEY, scope_id text NOT NULL REFERENCES observatory_core.scope(scope_id), provider text NOT NULL, captured_at timestamptz NOT NULL, request_fingerprint text NOT NULL, response_fingerprint text NOT NULL);
COMMIT;
