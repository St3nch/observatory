-- observatory-db4: {"version":"005","direction":"rollback","responsibility":"raw_support","paired_path":"database/migrations/005_raw_support.sql","required_prior":"005","resulting_version":"004","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_raw"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_raw CASCADE;
COMMIT;
