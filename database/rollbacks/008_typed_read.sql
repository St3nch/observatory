-- observatory-db4: {"version":"008","direction":"rollback","responsibility":"typed_read","paired_path":"database/migrations/008_typed_read.sql","required_prior":"008","resulting_version":"007","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_read"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_read CASCADE;
COMMIT;
