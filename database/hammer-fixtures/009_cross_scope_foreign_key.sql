-- db4-broken-fixture: cross_scope_foreign_key
-- fixture_id: 009_cross_scope_foreign_key
-- violated_invariant: scope-bound lineage must use composite scope-preserving foreign keys
-- rejection_class: postgresql_native
-- rejection_point: violating INSERT against composite foreign key
-- expected_sqlstate: 23503
-- residue_relation: public.db4_cross_scope_child
-- history_expectation: zero accepted history rows
-- cleanup_expectation: candidate transaction rollback removes parent and child relations
CREATE TABLE public.db4_cross_scope_parent(
    scope_key text NOT NULL,
    parent_key text NOT NULL,
    PRIMARY KEY (scope_key, parent_key)
);
CREATE TABLE public.db4_cross_scope_child(
    scope_key text NOT NULL,
    parent_key text NOT NULL,
    FOREIGN KEY (scope_key, parent_key)
      REFERENCES public.db4_cross_scope_parent(scope_key, parent_key)
);
INSERT INTO public.db4_cross_scope_parent VALUES ('scope-a', 'parent-a');
INSERT INTO public.db4_cross_scope_child VALUES ('scope-b', 'parent-a');
