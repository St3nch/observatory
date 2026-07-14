-- observatory-db4: {"version":"001","direction":"forward","responsibility":"identity_namespaces","paired_path":"database/rollbacks/001_identity_namespaces.sql","required_prior":"000","resulting_version":"001","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_meta"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_meta;
CREATE TABLE observatory_meta.schema_migration(version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now(), file_sha256 text NOT NULL, schema_fingerprint text NOT NULL);
COMMIT;
