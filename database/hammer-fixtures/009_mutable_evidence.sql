-- db4-broken-fixture: mutable_evidence
-- fixture_id: 009_mutable_evidence
-- violated_invariant: evidence facts must be append-only and reject direct UPDATE or DELETE
-- rejection_class: runner_detected
-- rejection_point: append-only trigger detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.mutable_evidence
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes mutable relation
CREATE TABLE public.mutable_evidence(evidence_id text PRIMARY KEY, value jsonb NOT NULL);
INSERT INTO public.mutable_evidence VALUES ('db4-mutable-evidence', '{"value":"original"}'::jsonb);
UPDATE public.mutable_evidence SET value = '{"value":"changed"}'::jsonb WHERE evidence_id = 'db4-mutable-evidence';
