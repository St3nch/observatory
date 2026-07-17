-- db4-broken-fixture: missing_scope_boundary
-- fixture_id: 009_missing_scope_boundary
-- violated_invariant: every observation-like relation must carry an explicit governed scope lineage boundary
-- rejection_class: runner_detected
-- rejection_point: relation and foreign-key detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.broken_observation
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes unscoped relation
CREATE TABLE public.broken_observation(
    observation_id text PRIMARY KEY,
    observed_value jsonb NOT NULL
);
INSERT INTO public.broken_observation VALUES ('db4-unscoped-observation', '{"probe":true}'::jsonb);
