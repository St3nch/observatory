-- db4-broken-fixture: partial_migration_failure
-- fixture_id: 009_partial_migration_failure
-- violated_invariant: candidate DDL and migration history must commit or roll back atomically
-- rejection_class: postgresql_native
-- rejection_point: division-by-zero after prior DDL inside runner-owned transaction
-- expected_sqlstate: 22012
-- residue_relation: public.partial_before_failure
-- history_expectation: zero accepted history rows
-- cleanup_expectation: transaction rollback removes partial_before_failure
CREATE TABLE public.partial_before_failure(id integer PRIMARY KEY);
SELECT 1 / 0;
