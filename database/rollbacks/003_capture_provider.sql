-- observatory-db4: {"version":"003","direction":"rollback","responsibility":"capture_provider","paired_path":"database/migrations/003_capture_provider.sql","required_prior":"003","resulting_version":"002","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_capture"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_capture CASCADE;
COMMIT;
