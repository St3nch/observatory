-- observatory-db4: {"version":"002","direction":"forward","responsibility":"governance_scope","paired_path":"database/rollbacks/002_governance_scope.sql","required_prior":"001","resulting_version":"002","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_governance"],"destructive":"none"}

CREATE TABLE obs_governance.scope (
    scope_key text PRIMARY KEY CHECK (scope_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    scope_class text NOT NULL CHECK (scope_class IN ('public_subject', 'system_test')),
    display_label text NOT NULL CHECK (length(display_label) BETWEEN 1 AND 200),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_governance.scope_transition (
    scope_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    transition_type text NOT NULL CHECK (transition_type IN ('activated', 'suspended', 'retired', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (scope_key, transition_type, effective_at)
);

CREATE TABLE obs_governance.vocabulary_family (
    vocabulary_family_key text PRIMARY KEY CHECK (vocabulary_family_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    purpose text NOT NULL CHECK (length(purpose) BETWEEN 1 AND 500),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_governance.vocabulary_version (
    vocabulary_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vocabulary_family_key text NOT NULL REFERENCES obs_governance.vocabulary_family(vocabulary_family_key),
    version_key text NOT NULL CHECK (version_key ~ '^[a-z0-9][a-z0-9._-]{0,63}$'),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (vocabulary_family_key, version_key)
);

CREATE TABLE obs_governance.vocabulary_entry (
    vocabulary_entry_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vocabulary_version_id bigint NOT NULL REFERENCES obs_governance.vocabulary_version(vocabulary_version_id),
    entry_key text NOT NULL CHECK (entry_key ~ '^[a-z][a-z0-9_-]{1,63}$'),
    entry_label text NOT NULL CHECK (length(entry_label) BETWEEN 1 AND 200),
    definition text NOT NULL CHECK (length(definition) BETWEEN 1 AND 2000),
    UNIQUE (vocabulary_version_id, entry_key)
);

CREATE TABLE obs_governance.vocabulary_transition (
    vocabulary_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vocabulary_version_id bigint NOT NULL REFERENCES obs_governance.vocabulary_version(vocabulary_version_id),
    transition_type text NOT NULL CHECK (transition_type IN ('published', 'deprecated', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (vocabulary_version_id, transition_type, effective_at)
);

CREATE TABLE obs_governance.source_family (
    source_family_key text PRIMARY KEY CHECK (source_family_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    source_class text NOT NULL CHECK (source_class IN ('public_web', 'search_surface', 'marketplace', 'video_surface', 'provider_testimony', 'manual_public_evidence')),
    description text NOT NULL CHECK (length(description) BETWEEN 1 AND 1000),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_governance.source_family_transition (
    source_family_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_family_key text NOT NULL REFERENCES obs_governance.source_family(source_family_key),
    transition_type text NOT NULL CHECK (transition_type IN ('admitted', 'suspended', 'retired', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (source_family_key, transition_type, effective_at)
);

CREATE TABLE obs_governance.capture_instrument (
    capture_instrument_key text PRIMARY KEY CHECK (capture_instrument_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    instrument_class text NOT NULL CHECK (instrument_class IN ('api', 'manual_capture', 'browser_capture', 'file_import', 'first_party_export')),
    implementation_reference text NOT NULL CHECK (length(implementation_reference) BETWEEN 1 AND 500),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_governance.capture_instrument_transition (
    capture_instrument_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capture_instrument_key text NOT NULL REFERENCES obs_governance.capture_instrument(capture_instrument_key),
    transition_type text NOT NULL CHECK (transition_type IN ('admitted', 'suspended', 'retired', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_instrument_key, transition_type, effective_at)
);

CREATE TABLE obs_governance.governed_target (
    target_key text PRIMARY KEY CHECK (target_key ~ '^[a-z][a-z0-9_-]{2,127}$'),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    target_class text NOT NULL CHECK (target_class IN ('domain', 'url', 'marketplace_listing', 'video_channel', 'public_entity')),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (scope_key, target_key)
);

CREATE TABLE obs_governance.target_binding (
    target_binding_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    binding_class text NOT NULL CHECK (binding_class IN ('domain', 'url', 'marketplace_listing', 'video_channel', 'public_entity')),
    domain_name text,
    url_value text,
    marketplace_key text,
    listing_key text,
    video_platform_key text,
    channel_key text,
    public_entity_key text,
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (
        (binding_class = 'domain' AND domain_name IS NOT NULL AND url_value IS NULL AND marketplace_key IS NULL AND listing_key IS NULL AND video_platform_key IS NULL AND channel_key IS NULL AND public_entity_key IS NULL)
        OR (binding_class = 'url' AND domain_name IS NULL AND url_value IS NOT NULL AND marketplace_key IS NULL AND listing_key IS NULL AND video_platform_key IS NULL AND channel_key IS NULL AND public_entity_key IS NULL)
        OR (binding_class = 'marketplace_listing' AND domain_name IS NULL AND url_value IS NULL AND marketplace_key IS NOT NULL AND listing_key IS NOT NULL AND video_platform_key IS NULL AND channel_key IS NULL AND public_entity_key IS NULL)
        OR (binding_class = 'video_channel' AND domain_name IS NULL AND url_value IS NULL AND marketplace_key IS NULL AND listing_key IS NULL AND video_platform_key IS NOT NULL AND channel_key IS NOT NULL AND public_entity_key IS NULL)
        OR (binding_class = 'public_entity' AND domain_name IS NULL AND url_value IS NULL AND marketplace_key IS NULL AND listing_key IS NULL AND video_platform_key IS NULL AND channel_key IS NULL AND public_entity_key IS NOT NULL)
    ),
    UNIQUE (target_key, effective_at)
);

CREATE TABLE obs_governance.source_family_assignment (
    source_family_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    source_family_key text NOT NULL REFERENCES obs_governance.source_family(source_family_key),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    expires_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (expires_at IS NULL OR expires_at > effective_at),
    UNIQUE (target_key, source_family_key, effective_at)
);

CREATE TABLE obs_governance.rights_assignment (
    rights_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    rights_class text NOT NULL CHECK (rights_class IN ('public_observation_allowed', 'metadata_only', 'prohibited')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    expires_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (expires_at IS NULL OR expires_at > effective_at),
    UNIQUE (target_key, effective_at)
);

CREATE TABLE obs_governance.retention_assignment (
    retention_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    retention_class text NOT NULL CHECK (retention_class IN ('ephemeral', 'bounded', 'durable_evidence')),
    retention_days integer CHECK (retention_days IS NULL OR retention_days BETWEEN 1 AND 36500),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    expires_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (expires_at IS NULL OR expires_at > effective_at),
    UNIQUE (target_key, effective_at)
);

CREATE TABLE obs_governance.freshness_assignment (
    freshness_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    freshness_seconds integer NOT NULL CHECK (freshness_seconds BETWEEN 60 AND 31536000),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    expires_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (expires_at IS NULL OR expires_at > effective_at),
    UNIQUE (target_key, effective_at)
);

CREATE TABLE obs_governance.volatility_assignment (
    volatility_assignment_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    volatility_class text NOT NULL CHECK (volatility_class IN ('low', 'moderate', 'high', 'event_driven', 'unknown')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    expires_at timestamptz,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (expires_at IS NULL OR expires_at > effective_at),
    UNIQUE (target_key, effective_at)
);

CREATE TABLE obs_governance.assignment_transition (
    assignment_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    assignment_class text NOT NULL CHECK (assignment_class IN ('source_family', 'rights', 'retention', 'freshness', 'volatility')),
    assignment_id bigint NOT NULL,
    transition_type text NOT NULL CHECK (transition_type IN ('activated', 'expired', 'revoked', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (assignment_class, assignment_id, transition_type, effective_at)
);

CREATE INDEX governance_target_scope_idx ON obs_governance.governed_target(scope_key, target_key);
CREATE INDEX rights_assignment_effective_idx ON obs_governance.rights_assignment(target_key, effective_at DESC);
CREATE INDEX retention_assignment_effective_idx ON obs_governance.retention_assignment(target_key, effective_at DESC);
CREATE INDEX freshness_assignment_effective_idx ON obs_governance.freshness_assignment(target_key, effective_at DESC);
CREATE INDEX volatility_assignment_effective_idx ON obs_governance.volatility_assignment(target_key, effective_at DESC);

DO $$
DECLARE relation_name text;
BEGIN
    FOREACH relation_name IN ARRAY ARRAY[
        'scope_transition','vocabulary_version','vocabulary_entry','vocabulary_transition',
        'source_family_transition','capture_instrument_transition','target_binding',
        'source_family_assignment','rights_assignment','retention_assignment',
        'freshness_assignment','volatility_assignment','assignment_transition'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON obs_governance.%I FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation()',
            relation_name,
            relation_name
        );
    END LOOP;
END;
$$;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_governance FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_governance FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_governance REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_governance REVOKE ALL ON SEQUENCES FROM PUBLIC;
