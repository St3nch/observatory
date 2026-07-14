-- observatory-db4: {"version":"010","direction":"forward","responsibility":"recovery_verification","paired_path":"database/rollbacks/010_recovery_verification.sql","required_prior":"008","resulting_version":"010","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_meta"],"destructive":"none"}
BEGIN;
CREATE TABLE observatory_meta.restore_verification(verification_id text PRIMARY KEY, verified_at timestamptz NOT NULL DEFAULT now(), schema_fingerprint text NOT NULL, migration_count integer NOT NULL CHECK (migration_count >= 0));
COMMIT;
