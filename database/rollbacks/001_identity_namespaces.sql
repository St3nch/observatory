-- observatory-db4: {"version":"001","direction":"rollback","responsibility":"identity_namespaces","paired_path":"database/migrations/001_identity_namespaces.sql","required_prior":"001","resulting_version":"000","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_meta"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_meta CASCADE;
COMMIT;
