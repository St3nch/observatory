-- db4-broken-fixture: search_path_hijack
-- fixture_id: 009_search_path_hijack
-- violated_invariant: security-definer and migration execution must not resolve attacker-controlled objects through public search_path
-- rejection_class: runner_detected
-- rejection_point: post-execution semantic detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_search_path_hijack
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes attacker object
CREATE FUNCTION public.db4_search_path_hijack() RETURNS integer
LANGUAGE sql AS $$ SELECT 1 $$;
SET LOCAL search_path = public, pg_catalog;
SELECT db4_search_path_hijack();
