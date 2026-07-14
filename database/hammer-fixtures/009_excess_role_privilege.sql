-- db4-broken-fixture: excess_role_privilege
BEGIN;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO PUBLIC;
COMMIT;
