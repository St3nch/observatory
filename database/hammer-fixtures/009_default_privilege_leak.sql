-- db4-broken-fixture: default_privilege_leak
-- fixture_id: 009_default_privilege_leak
-- violated_invariant: future objects must not inherit PUBLIC privileges
-- rejection_class: runner_detected
-- rejection_point: default-privilege catalog detector before history insertion
-- expected_sqlstate: none
-- residue_relation: none
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes altered default privilege
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO PUBLIC;
