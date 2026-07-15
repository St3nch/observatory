-- db4-broken-fixture: dirty_constraint_seed
CREATE TABLE dirty_seed(id integer PRIMARY KEY, status text NOT NULL);
INSERT INTO dirty_seed VALUES (1,'invalid');
ALTER TABLE dirty_seed ADD CONSTRAINT valid_status CHECK (status IN ('valid'));
