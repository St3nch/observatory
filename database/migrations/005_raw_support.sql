-- observatory-db4: {"version":"005","direction":"forward","responsibility":"raw_support","paired_path":"database/rollbacks/005_raw_support.sql","required_prior":"004","resulting_version":"005","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_raw"],"destructive":"none"}

CREATE TABLE obs_raw.raw_manifest (
    raw_manifest_key text PRIMARY KEY CHECK (raw_manifest_key ~ '^rm_[a-z0-9_-]{20,120}$'),
    observation_key text NOT NULL UNIQUE REFERENCES obs_evidence.observation(observation_key),
    rights_assignment_id bigint NOT NULL REFERENCES obs_governance.rights_assignment(rights_assignment_id),
    retention_assignment_id bigint NOT NULL REFERENCES obs_governance.retention_assignment(retention_assignment_id),
    manifest_fingerprint text NOT NULL UNIQUE CHECK (manifest_fingerprint ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_raw.raw_manifest_transition (
    raw_manifest_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raw_manifest_key text NOT NULL REFERENCES obs_raw.raw_manifest(raw_manifest_key),
    transition_type text NOT NULL CHECK (transition_type IN ('recorded', 'verified', 'purged_with_proof', 'blocked_by_rights', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (raw_manifest_key, transition_type, effective_at)
);

CREATE TABLE obs_raw.raw_payload_identity (
    raw_payload_key text PRIMARY KEY CHECK (raw_payload_key ~ '^rp_[a-z0-9_-]{20,120}$'),
    raw_manifest_key text NOT NULL REFERENCES obs_raw.raw_manifest(raw_manifest_key),
    hash_algorithm text NOT NULL CHECK (hash_algorithm IN ('sha256', 'sha512')),
    content_digest text NOT NULL,
    byte_count bigint NOT NULL CHECK (byte_count >= 0),
    media_type text NOT NULL CHECK (length(media_type) BETWEEN 1 AND 255 AND media_type ~ '^[A-Za-z0-9.+-]+/[A-Za-z0-9.+-]+$'),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (
        (hash_algorithm = 'sha256' AND content_digest ~ '^[0-9a-f]{64}$')
        OR (hash_algorithm = 'sha512' AND content_digest ~ '^[0-9a-f]{128}$')
    ),
    UNIQUE (hash_algorithm, content_digest, byte_count)
);

CREATE TABLE obs_raw.raw_payload_transition (
    raw_payload_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raw_payload_key text NOT NULL REFERENCES obs_raw.raw_payload_identity(raw_payload_key),
    transition_type text NOT NULL CHECK (transition_type IN ('recorded', 'verified', 'missing', 'purged_with_proof', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (raw_payload_key, transition_type, effective_at)
);

CREATE TABLE obs_raw.opaque_artifact_token (
    opaque_token_key text PRIMARY KEY CHECK (opaque_token_key ~ '^tok_[A-Za-z0-9_-]{32,160}$'),
    raw_payload_key text NOT NULL UNIQUE REFERENCES obs_raw.raw_payload_identity(raw_payload_key),
    token_fingerprint text NOT NULL UNIQUE CHECK (token_fingerprint ~ '^[0-9a-f]{64}$'),
    issued_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_raw.opaque_artifact_token_transition (
    opaque_artifact_token_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    opaque_token_key text NOT NULL REFERENCES obs_raw.opaque_artifact_token(opaque_token_key),
    transition_type text NOT NULL CHECK (transition_type IN ('issued', 'revoked', 'expired', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (opaque_token_key, transition_type, effective_at)
);

CREATE TABLE obs_raw.raw_integrity_observation (
    raw_integrity_observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    raw_payload_key text NOT NULL REFERENCES obs_raw.raw_payload_identity(raw_payload_key),
    observed_hash_algorithm text NOT NULL CHECK (observed_hash_algorithm IN ('sha256', 'sha512')),
    observed_digest text NOT NULL,
    observed_byte_count bigint NOT NULL CHECK (observed_byte_count >= 0),
    result text NOT NULL CHECK (result IN ('matched', 'mismatched', 'missing', 'blocked')),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (
        (observed_hash_algorithm = 'sha256' AND observed_digest ~ '^[0-9a-f]{64}$')
        OR (observed_hash_algorithm = 'sha512' AND observed_digest ~ '^[0-9a-f]{128}$')
    ),
    UNIQUE (raw_payload_key, observed_at)
);

CREATE FUNCTION obs_raw.db4_probe_reversible_locator_rejection()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_raw
AS $$
DECLARE
    bad_locator constant text := 'file:///C:/private/raw.json?signature=secret';
    persisted_count integer;
BEGIN
    IF bad_locator ~* '(^[a-z]:[\\/]|^[a-z][a-z0-9+.-]*://|bucket|signed|signature=|connection)' THEN
        SELECT count(*) INTO persisted_count
        FROM information_schema.columns
        WHERE table_schema = 'obs_raw'
          AND column_name ~* '(path|uri|url|bucket|locator|connection|string|drive|key_name)';
        RETURN jsonb_build_object('rejected', true, 'persisted_count', persisted_count);
    END IF;
    RETURN jsonb_build_object('rejected', false, 'persisted_count', 0);
END;
$$;

DO $$
DECLARE relation_name text;
BEGIN
    FOREACH relation_name IN ARRAY ARRAY[
        'raw_manifest','raw_manifest_transition','raw_payload_identity','raw_payload_transition',
        'opaque_artifact_token','opaque_artifact_token_transition','raw_integrity_observation'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON obs_raw.%I FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation()',
            relation_name,
            relation_name
        );
    END LOOP;
END;
$$;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_raw FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_raw FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_raw FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_raw REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_raw REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_raw REVOKE ALL ON FUNCTIONS FROM PUBLIC;
