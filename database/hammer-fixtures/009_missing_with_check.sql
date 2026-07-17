-- db4-broken-fixture: missing_with_check
-- fixture_id: 009_missing_with_check
-- violated_invariant: ingest RLS policies must enforce scope on INSERT through WITH CHECK
-- rejection_class: runner_detected
-- rejection_point: catalog detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_missing_with_check
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes sabotage relation
CREATE TABLE public.db4_missing_with_check(scope_key text NOT NULL, payload text NOT NULL);
ALTER TABLE public.db4_missing_with_check ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.db4_missing_with_check FORCE ROW LEVEL SECURITY;
CREATE POLICY db4_missing_with_check_select ON public.db4_missing_with_check FOR SELECT USING (scope_key = current_setting('ob.scope_key', true));
CREATE POLICY db4_missing_with_check_insert ON public.db4_missing_with_check FOR INSERT WITH CHECK (true);
