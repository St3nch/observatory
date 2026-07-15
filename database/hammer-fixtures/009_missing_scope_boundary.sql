-- db4-broken-fixture: missing_scope_boundary
CREATE TABLE broken_observation(observation_id text PRIMARY KEY, observed_value jsonb NOT NULL);
