-- db4-broken-fixture: unbounded_raw_locator
BEGIN;
CREATE TABLE leaked_raw_locator(id text PRIMARY KEY, absolute_path text NOT NULL);
COMMIT;
