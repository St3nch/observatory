-- db4-broken-fixture: not_valid_constraint
-- fixture_id: 009_not_valid_constraint
-- violated_invariant: accepted schema must not carry unvalidated constraints
-- rejection_class: runner_detected
-- rejection_point: constraint validation-state detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_not_valid_constraint
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes sabotage relation
CREATE TABLE public.db4_not_valid_constraint(id integer PRIMARY KEY, status text NOT NULL);
ALTER TABLE public.db4_not_valid_constraint
ADD CONSTRAINT db4_not_valid_status CHECK (status = 'valid') NOT VALID;
