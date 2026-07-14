-- observatory-db4: {"version":"004","direction":"rollback","responsibility":"evidence_identity","paired_path":"database/migrations/004_evidence_identity.sql","required_prior":"004","resulting_version":"003","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_evidence"],"destructive":"disposable_only"}
BEGIN;
DROP SCHEMA IF EXISTS observatory_evidence CASCADE;
COMMIT;
