-- observatory-db4: {"version":"002","direction":"forward","responsibility":"governance_scope","paired_path":"database/rollbacks/002_governance_scope.sql","required_prior":"001","resulting_version":"002","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_core"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_core;
CREATE TABLE observatory_core.scope(scope_id text PRIMARY KEY, scope_class text NOT NULL CHECK (scope_class IN ('public_subject','system_test')), created_at timestamptz NOT NULL DEFAULT now());
COMMIT;
