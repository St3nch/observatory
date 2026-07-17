-- db4-broken-fixture: rls_without_force
-- fixture_id: 009_rls_without_force
-- violated_invariant: every scope-bound relation with RLS must also FORCE RLS
-- rejection_class: runner_detected
-- rejection_point: catalog detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_rls_without_force
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes sabotage relation
CREATE TABLE public.db4_rls_without_force(scope_key text NOT NULL, payload text NOT NULL);
ALTER TABLE public.db4_rls_without_force ENABLE ROW LEVEL SECURITY;
CREATE POLICY db4_rls_without_force_policy ON public.db4_rls_without_force USING (scope_key = current_setting('ob.scope_key', true));
