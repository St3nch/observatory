-- db4-broken-fixture: unbounded_raw_locator
-- fixture_id: 009_unbounded_raw_locator
-- violated_invariant: ordinary relational storage must not persist reversible raw paths or locators
-- rejection_class: runner_detected
-- rejection_point: semantic raw-locator detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.leaked_raw_locator
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes locator relation and value
CREATE TABLE public.leaked_raw_locator(id text PRIMARY KEY, absolute_path text NOT NULL);
INSERT INTO public.leaked_raw_locator VALUES ('db4-raw-leak', 'C:\\private\\capture.json');
