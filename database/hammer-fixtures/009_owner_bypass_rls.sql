-- db4-broken-fixture: owner_bypass_rls
-- fixture_id: 009_owner_bypass_rls
-- violated_invariant: scope-bound relations must not rely on owner-bypassable RLS
-- rejection_class: runner_detected
-- rejection_point: catalog and role-semantic detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_owner_bypass_rls
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes sabotage relation
CREATE TABLE public.db4_owner_bypass_rls(scope_key text NOT NULL, payload text NOT NULL);
ALTER TABLE public.db4_owner_bypass_rls ENABLE ROW LEVEL SECURITY;
CREATE POLICY db4_owner_bypass_policy ON public.db4_owner_bypass_rls USING (scope_key = current_setting('ob.scope_key', true));
