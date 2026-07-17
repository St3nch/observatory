-- db4-broken-fixture: public_schema_create
-- fixture_id: 009_public_schema_create
-- violated_invariant: bounded roles must not retain CREATE on schema public
-- rejection_class: runner_detected
-- rejection_point: schema privilege detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_public_schema_create
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes created relation
CREATE TABLE public.db4_public_schema_create(probe_key text PRIMARY KEY);
