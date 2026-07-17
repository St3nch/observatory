-- db4-broken-fixture: excess_role_privilege
-- fixture_id: 009_excess_role_privilege
-- violated_invariant: no application or proof relation may grant privileges to PUBLIC
-- rejection_class: runner_detected
-- rejection_point: privilege catalog detector before history insertion
-- expected_sqlstate: none
-- residue_relation: public.db4_privilege_probe
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes relation and grant
CREATE TABLE public.db4_privilege_probe(id integer PRIMARY KEY);
GRANT ALL PRIVILEGES ON TABLE public.db4_privilege_probe TO PUBLIC;
