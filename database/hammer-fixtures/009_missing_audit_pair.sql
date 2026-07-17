-- db4-broken-fixture: missing_audit_pair
-- fixture_id: 009_missing_audit_pair
-- violated_invariant: consequential transition relations require same-transaction audit enforcement
-- rejection_class: runner_detected
-- rejection_point: trigger and audit-pair detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.unaudited_transition
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes unaudited relation
CREATE TABLE public.unaudited_transition(subject_id text PRIMARY KEY, state text NOT NULL);
INSERT INTO public.unaudited_transition VALUES ('db4-unaudited-subject', 'accepted');
