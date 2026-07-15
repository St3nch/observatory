-- db4-broken-fixture: excess_role_privilege
CREATE TABLE public.db4_privilege_probe(id integer PRIMARY KEY);
GRANT ALL PRIVILEGES ON TABLE public.db4_privilege_probe TO PUBLIC;
