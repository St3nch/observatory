-- observatory-db4: {"version":"006","direction":"forward","responsibility":"audit_append_only","paired_path":"database/rollbacks/006_audit_append_only.sql","required_prior":"005","resulting_version":"006","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_audit"],"destructive":"none"}

CREATE TABLE obs_audit.audit_event (
    audit_event_key text PRIMARY KEY CHECK (audit_event_key ~ '^aud_[a-z0-9_-]{20,120}$'),
    transaction_id bigint NOT NULL DEFAULT txid_current(),
    event_type text NOT NULL CHECK (event_type ~ '^[a-z][a-z0-9_-]{2,63}$'),
    subject_schema name NOT NULL,
    subject_relation name NOT NULL,
    subject_key text NOT NULL CHECK (length(subject_key) BETWEEN 1 AND 200),
    action text NOT NULL CHECK (action IN ('INSERT', 'TRANSITION', 'SUPERSEDE', 'PURGE_PROOF')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    detail jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(detail) = 'object'),
    occurred_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (transaction_id, subject_schema, subject_relation, subject_key, action)
);

CREATE TABLE obs_audit.audit_supersession (
    audit_supersession_key text PRIMARY KEY CHECK (audit_supersession_key ~ '^sup_[a-z0-9_-]{20,120}$'),
    prior_audit_event_key text NOT NULL REFERENCES obs_audit.audit_event(audit_event_key),
    replacement_audit_event_key text NOT NULL REFERENCES obs_audit.audit_event(audit_event_key),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    reason text NOT NULL CHECK (length(reason) BETWEEN 1 AND 2000),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (prior_audit_event_key <> replacement_audit_event_key),
    UNIQUE (prior_audit_event_key)
);

CREATE FUNCTION obs_audit.require_same_transaction_audit()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, obs_audit
AS $$
DECLARE
    subject_key text;
    paired boolean;
BEGIN
    subject_key := to_jsonb(NEW) ->> TG_ARGV[0];
    IF subject_key IS NULL OR subject_key = '' THEN
        RAISE EXCEPTION 'audit subject key is missing for %.%', TG_TABLE_SCHEMA, TG_TABLE_NAME
            USING ERRCODE = '23514';
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM obs_audit.audit_event event
        WHERE event.transaction_id = txid_current()
          AND event.subject_schema = TG_TABLE_SCHEMA::name
          AND event.subject_relation = TG_TABLE_NAME::name
          AND event.subject_key = subject_key
          AND event.action = TG_OP
    ) INTO paired;

    IF NOT paired THEN
        RAISE EXCEPTION 'same-transaction audit pair is required for %.% subject %', TG_TABLE_SCHEMA, TG_TABLE_NAME, subject_key
            USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE CONSTRAINT TRIGGER observation_audit_required
AFTER INSERT ON obs_evidence.observation
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION obs_audit.require_same_transaction_audit('observation_key');

CREATE CONSTRAINT TRIGGER evidence_identity_audit_required
AFTER INSERT ON obs_evidence.evidence_identity
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION obs_audit.require_same_transaction_audit('evidence_key');

CREATE CONSTRAINT TRIGGER citation_handle_audit_required
AFTER INSERT ON obs_evidence.citation_handle
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION obs_audit.require_same_transaction_audit('citation_handle');

CREATE CONSTRAINT TRIGGER raw_manifest_audit_required
AFTER INSERT ON obs_raw.raw_manifest
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION obs_audit.require_same_transaction_audit('raw_manifest_key');

CREATE TABLE obs_audit.db4_consequential_probe (
    probe_key text PRIMARY KEY,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE CONSTRAINT TRIGGER db4_consequential_probe_audit_required
AFTER INSERT ON obs_audit.db4_consequential_probe
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION obs_audit.require_same_transaction_audit('probe_key');

CREATE FUNCTION obs_audit.db4_probe_unpaired_consequential_write()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_audit
AS $$
DECLARE
    rejected boolean := false;
    remaining integer;
BEGIN
    BEGIN
        INSERT INTO obs_audit.db4_consequential_probe(probe_key)
        VALUES ('db4-unpaired-write');
        SET CONSTRAINTS db4_consequential_probe_audit_required IMMEDIATE;
    EXCEPTION WHEN check_violation THEN
        rejected := true;
    END;

    SELECT count(*) INTO remaining
    FROM obs_audit.db4_consequential_probe
    WHERE probe_key = 'db4-unpaired-write';

    RETURN jsonb_build_object(
        'commit_rejected', rejected,
        'consequential_rows', remaining
    );
END;
$$;

CREATE TRIGGER audit_event_append_only
BEFORE UPDATE OR DELETE ON obs_audit.audit_event
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

CREATE TRIGGER audit_supersession_append_only
BEFORE UPDATE OR DELETE ON obs_audit.audit_supersession
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

REVOKE ALL ON ALL TABLES IN SCHEMA obs_audit FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_audit FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_audit FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_audit REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_audit REVOKE ALL ON FUNCTIONS FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_audit REVOKE ALL ON SEQUENCES FROM PUBLIC;
