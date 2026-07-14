-- observatory-db4: {"version":"006","direction":"forward","responsibility":"audit_append_only","paired_path":"database/rollbacks/006_audit_append_only.sql","required_prior":"005","resulting_version":"006","database_class":"disposable_postgres","transaction":"required","proof_class":"real_postgres_disposable_pass","authority":"db4-accepted","namespaces":["observatory_audit"],"destructive":"none"}
BEGIN;
CREATE SCHEMA IF NOT EXISTS observatory_audit;
CREATE TABLE observatory_audit.event(event_id text PRIMARY KEY, event_type text NOT NULL, subject_id text NOT NULL, occurred_at timestamptz NOT NULL DEFAULT now(), detail jsonb NOT NULL DEFAULT '{}'::jsonb);
CREATE OR REPLACE FUNCTION observatory_audit.reject_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'append-only relation'; END $$;
CREATE TRIGGER event_append_only BEFORE UPDATE OR DELETE ON observatory_audit.event FOR EACH ROW EXECUTE FUNCTION observatory_audit.reject_mutation();
COMMIT;
