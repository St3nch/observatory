-- observatory-db4: {"version":"001","direction":"forward","responsibility":"identity_namespaces","paired_path":"database/rollbacks/001_identity_namespaces.sql","required_prior":"000","resulting_version":"001","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_meta","obs_governance","obs_capture","obs_evidence","obs_raw","obs_audit","obs_security","obs_read"],"destructive":"none"}

CREATE SCHEMA obs_meta;
CREATE SCHEMA obs_governance;
CREATE SCHEMA obs_capture;
CREATE SCHEMA obs_evidence;
CREATE SCHEMA obs_raw;
CREATE SCHEMA obs_audit;
CREATE SCHEMA obs_security;
CREATE SCHEMA obs_read;

REVOKE ALL ON SCHEMA obs_meta, obs_governance, obs_capture, obs_evidence, obs_raw, obs_audit, obs_security, obs_read FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

CREATE FUNCTION obs_meta.reject_mutation()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog
AS $$
DECLARE
    relation_owner name;
    row_data jsonb;
    candidate_key text;
    key_name text;
    cleanup_key_names constant text[] := ARRAY[
        'probe_key',
        'scope_key',
        'target_key',
        'capture_instrument_key',
        'query_panel_key',
        'panel_run_key',
        'capture_package_key',
        'capture_event_key',
        'observed_artifact_key',
        'candidate_observation_key',
        'observation_key',
        'evidence_key',
        'citation_handle',
        'raw_manifest_key',
        'raw_payload_key',
        'opaque_token_key',
        'subject_key',
        'version',
        'restore_verification_key'
    ];
BEGIN
    SELECT pg_get_userbyid(relowner) INTO relation_owner
    FROM pg_class
    WHERE oid = TG_RELID;

    IF TG_OP = 'DELETE'
       AND current_user = relation_owner
       AND current_setting('ob.db4_cleanup', true) = 'authorized' THEN
        row_data := to_jsonb(OLD);
        FOREACH key_name IN ARRAY cleanup_key_names LOOP
            candidate_key := row_data ->> key_name;
            IF candidate_key IS NOT NULL
               AND (
                    candidate_key ~ '^db4-[a-z0-9_-]+$'
                    OR candidate_key ~ '^ev_db4_[a-z0-9_-]+$'
                    OR candidate_key ~ '^cit_db4_[A-Za-z0-9_-]+$'
                    OR candidate_key IN ('scope-a', 'scope-b')
               ) THEN
                RETURN OLD;
            END IF;
        END LOOP;
    END IF;

    RAISE EXCEPTION 'append-only relation % does not allow %', TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME, TG_OP
        USING ERRCODE = '42501';
END;
$$;

CREATE TABLE obs_meta.database_identity (
    singleton boolean PRIMARY KEY DEFAULT true CHECK (singleton),
    database_name name NOT NULL CHECK (database_name::text ~ '^observatory_test_[a-z0-9_]+$'),
    database_oid oid NOT NULL,
    server_version_num integer NOT NULL CHECK (server_version_num > 0),
    server_address text,
    server_port integer CHECK (server_port IS NULL OR server_port BETWEEN 1 AND 65535),
    database_class text NOT NULL CHECK (database_class = 'disposable_postgres'),
    creation_authority_reference text NOT NULL CHECK (creation_authority_reference ~ '^decisions/.+\.md$'),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (database_name, database_oid)
);

CREATE TABLE obs_meta.schema_migration (
    migration_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version text NOT NULL CHECK (version ~ '^[0-9]{3}$'),
    direction text NOT NULL CHECK (direction IN ('up', 'down')),
    relative_path text NOT NULL CHECK (relative_path ~ '^database/(migrations|rollbacks)/[0-9]{3}_[a-z0-9_]+\.sql$'),
    file_sha256 text NOT NULL CHECK (file_sha256 ~ '^[0-9a-f]{64}$'),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    before_fingerprint text NOT NULL CHECK (before_fingerprint ~ '^[0-9a-f]{64}$'),
    after_fingerprint text NOT NULL CHECK (after_fingerprint ~ '^[0-9a-f]{64}$'),
    applied_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (version, direction),
    UNIQUE (relative_path, file_sha256)
);

CREATE TABLE obs_meta.capability_history (
    capability_history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capability_class text NOT NULL CHECK (capability_class IN (
        'inspection_only',
        'postgres_disposable_only',
        'migration_spec_proof_only',
        'governed_bootstrap_authorized',
        'real_ingestion_authorized',
        'restore_proof_authorized'
    )),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (effective_at <= recorded_at)
);

CREATE TRIGGER database_identity_append_only
BEFORE UPDATE OR DELETE ON obs_meta.database_identity
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

CREATE TRIGGER schema_migration_append_only
BEFORE UPDATE OR DELETE ON obs_meta.schema_migration
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

CREATE TRIGGER capability_history_append_only
BEFORE UPDATE OR DELETE ON obs_meta.capability_history
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

REVOKE ALL ON ALL TABLES IN SCHEMA obs_meta FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_meta FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_meta REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_meta REVOKE ALL ON FUNCTIONS FROM PUBLIC;
