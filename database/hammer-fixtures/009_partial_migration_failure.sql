-- db4-broken-fixture: partial_migration_failure
CREATE TABLE partial_before_failure(id integer PRIMARY KEY);
SELECT 1/0;
