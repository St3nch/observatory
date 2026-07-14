-- db4-broken-fixture: mutable_evidence
BEGIN;
CREATE TABLE mutable_evidence(evidence_id text PRIMARY KEY, value jsonb NOT NULL);
COMMIT;
