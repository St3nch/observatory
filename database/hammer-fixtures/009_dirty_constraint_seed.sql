-- db4-broken-fixture: dirty_constraint_seed
-- fixture_id: 009_dirty_constraint_seed
-- violated_invariant: a new validated constraint must reject pre-existing violating rows atomically
-- rejection_class: postgresql_native
-- rejection_point: ALTER TABLE constraint validation
-- expected_sqlstate: 23514
-- residue_relation: public.dirty_seed
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes dirty_seed
CREATE TABLE public.dirty_seed(id integer PRIMARY KEY, status text NOT NULL);
INSERT INTO public.dirty_seed VALUES (1, 'invalid');
ALTER TABLE public.dirty_seed ADD CONSTRAINT valid_status CHECK (status IN ('valid'));
