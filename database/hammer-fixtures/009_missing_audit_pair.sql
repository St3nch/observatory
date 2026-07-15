-- db4-broken-fixture: missing_audit_pair
CREATE TABLE unaudited_transition(subject_id text PRIMARY KEY, state text NOT NULL);
