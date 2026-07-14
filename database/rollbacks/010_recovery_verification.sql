-- observatory-db4: {"version":"010","direction":"rollback","responsibility":"recovery_verification","paired_path":"database/migrations/010_recovery_verification.sql","required_prior":"010","resulting_version":"008","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_meta"],"destructive":"disposable_only"}
BEGIN;
DROP TABLE IF EXISTS observatory_meta.restore_verification;
COMMIT;
