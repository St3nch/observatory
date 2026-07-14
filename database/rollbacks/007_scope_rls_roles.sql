-- observatory-db4: {"version":"007","direction":"rollback","responsibility":"scope_rls_roles","paired_path":"database/migrations/007_scope_rls_roles.sql","required_prior":"007","resulting_version":"006","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_evidence"],"destructive":"disposable_only"}
BEGIN;
DROP POLICY IF EXISTS observation_scope_policy ON observatory_evidence.observation;
ALTER TABLE observatory_evidence.observation DISABLE ROW LEVEL SECURITY;
COMMIT;
