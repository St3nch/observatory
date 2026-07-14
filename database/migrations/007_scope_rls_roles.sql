-- observatory-db4: {"version":"007","direction":"forward","responsibility":"scope_rls_roles","paired_path":"database/rollbacks/007_scope_rls_roles.sql","required_prior":"006","resulting_version":"007","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_core","observatory_evidence"],"destructive":"none"}
BEGIN;
ALTER TABLE observatory_evidence.observation ENABLE ROW LEVEL SECURITY;
CREATE POLICY observation_scope_policy ON observatory_evidence.observation USING (EXISTS (SELECT 1 FROM observatory_capture.capture_package p WHERE p.package_id = observation.package_id AND p.scope_id = current_setting('observatory.scope_id', true)));
COMMIT;
