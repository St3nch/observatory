-- observatory-db4: {"version":"006","direction":"rollback","responsibility":"audit_append_only","paired_path":"database/migrations/006_audit_append_only.sql","required_prior":"006","resulting_version":"005","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_audit"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_audit CASCADE;
COMMIT;
