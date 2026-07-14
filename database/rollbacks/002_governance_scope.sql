-- observatory-db4: {"version":"002","direction":"rollback","responsibility":"governance_scope","paired_path":"database/migrations/002_governance_scope.sql","required_prior":"002","resulting_version":"001","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_core"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_core CASCADE;
COMMIT;
