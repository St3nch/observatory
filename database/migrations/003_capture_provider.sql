-- observatory-db4: {"version":"003","direction":"forward","responsibility":"capture_provider","paired_path":"database/rollbacks/003_capture_provider.sql","required_prior":"002","resulting_version":"003","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_capture"],"destructive":"none"}

CREATE TABLE obs_capture.query_panel (
    query_panel_key text PRIMARY KEY CHECK (query_panel_key ~ '^[a-z][a-z0-9_-]{2,127}$'),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    panel_class text NOT NULL CHECK (panel_class IN ('search', 'marketplace', 'video', 'ai_answer', 'manual_public_evidence')),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_capture.query_panel_version (
    query_panel_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    query_panel_key text NOT NULL REFERENCES obs_capture.query_panel(query_panel_key),
    version_key text NOT NULL CHECK (version_key ~ '^[a-z0-9][a-z0-9._-]{0,63}$'),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (query_panel_key, version_key)
);

CREATE TABLE obs_capture.query_panel_item (
    query_panel_item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    query_panel_version_id bigint NOT NULL REFERENCES obs_capture.query_panel_version(query_panel_version_id),
    item_ordinal integer NOT NULL CHECK (item_ordinal BETWEEN 1 AND 100000),
    query_text text NOT NULL CHECK (length(query_text) BETWEEN 1 AND 2000),
    locale_key text,
    device_class text CHECK (device_class IS NULL OR device_class IN ('desktop', 'mobile', 'tablet', 'unspecified')),
    UNIQUE (query_panel_version_id, item_ordinal),
    UNIQUE (query_panel_version_id, query_text, locale_key, device_class)
);

CREATE TABLE obs_capture.query_panel_transition (
    query_panel_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    query_panel_version_id bigint NOT NULL REFERENCES obs_capture.query_panel_version(query_panel_version_id),
    transition_type text NOT NULL CHECK (transition_type IN ('published', 'used', 'retired', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (query_panel_version_id, transition_type, effective_at)
);

CREATE TABLE obs_capture.panel_run (
    panel_run_key text PRIMARY KEY CHECK (panel_run_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    query_panel_version_id bigint NOT NULL REFERENCES obs_capture.query_panel_version(query_panel_version_id),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    requested_at timestamptz NOT NULL,
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (query_panel_version_id, scope_key, target_key, requested_at)
);

CREATE TABLE obs_capture.panel_run_transition (
    panel_run_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    panel_run_key text NOT NULL REFERENCES obs_capture.panel_run(panel_run_key),
    transition_type text NOT NULL CHECK (transition_type IN ('started', 'completed', 'failed', 'aborted')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (panel_run_key, transition_type, effective_at)
);

CREATE TABLE obs_capture.provider (
    provider_key text PRIMARY KEY CHECK (provider_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    provider_class text NOT NULL CHECK (provider_class IN ('official_api', 'commercial_api', 'public_surface', 'manual_witness')),
    display_label text NOT NULL CHECK (length(display_label) BETWEEN 1 AND 200),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_capture.provider_transition (
    provider_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_key text NOT NULL REFERENCES obs_capture.provider(provider_key),
    transition_type text NOT NULL CHECK (transition_type IN ('admitted', 'suspended', 'retired', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (provider_key, transition_type, effective_at)
);

CREATE TABLE obs_capture.capture_package (
    capture_package_key text PRIMARY KEY CHECK (capture_package_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    panel_run_key text NOT NULL REFERENCES obs_capture.panel_run(panel_run_key),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    capture_instrument_key text NOT NULL REFERENCES obs_governance.capture_instrument(capture_instrument_key),
    provider_key text REFERENCES obs_capture.provider(provider_key),
    requested_at timestamptz NOT NULL,
    completed_at timestamptz,
    request_fingerprint text NOT NULL CHECK (request_fingerprint ~ '^[0-9a-f]{64}$'),
    response_fingerprint text CHECK (response_fingerprint IS NULL OR response_fingerprint ~ '^[0-9a-f]{64}$'),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (completed_at IS NULL OR completed_at >= requested_at),
    CHECK ((completed_at IS NULL AND response_fingerprint IS NULL) OR (completed_at IS NOT NULL AND response_fingerprint IS NOT NULL)),
    UNIQUE (panel_run_key, capture_instrument_key, provider_key, request_fingerprint)
);

CREATE TABLE obs_capture.capture_package_transition (
    capture_package_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capture_package_key text NOT NULL REFERENCES obs_capture.capture_package(capture_package_key),
    transition_type text NOT NULL CHECK (transition_type IN ('created', 'sealed', 'validated', 'rejected', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_package_key, transition_type, effective_at)
);

CREATE TABLE obs_capture.capture_event (
    capture_event_key text PRIMARY KEY CHECK (capture_event_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    capture_package_key text NOT NULL REFERENCES obs_capture.capture_package(capture_package_key),
    query_panel_item_id bigint NOT NULL REFERENCES obs_capture.query_panel_item(query_panel_item_id),
    observed_at timestamptz NOT NULL,
    event_fingerprint text NOT NULL CHECK (event_fingerprint ~ '^[0-9a-f]{64}$'),
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_package_key, query_panel_item_id, event_fingerprint)
);

CREATE TABLE obs_capture.capture_event_transition (
    capture_event_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capture_event_key text NOT NULL REFERENCES obs_capture.capture_event(capture_event_key),
    transition_type text NOT NULL CHECK (transition_type IN ('observed', 'validated', 'rejected', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_event_key, transition_type, effective_at)
);

CREATE TABLE obs_capture.validation_failure_version (
    validation_failure_version_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version_key text NOT NULL UNIQUE CHECK (version_key ~ '^[a-z0-9][a-z0-9._-]{0,63}$'),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_capture.validation_failure_entry (
    validation_failure_entry_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    validation_failure_version_id bigint NOT NULL REFERENCES obs_capture.validation_failure_version(validation_failure_version_id),
    failure_key text NOT NULL CHECK (failure_key ~ '^[a-z][a-z0-9_-]{2,63}$'),
    definition text NOT NULL CHECK (length(definition) BETWEEN 1 AND 1000),
    UNIQUE (validation_failure_version_id, failure_key)
);

CREATE TABLE obs_capture.validation_result (
    validation_result_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    capture_event_key text NOT NULL REFERENCES obs_capture.capture_event(capture_event_key),
    validation_failure_entry_id bigint REFERENCES obs_capture.validation_failure_entry(validation_failure_entry_id),
    result text NOT NULL CHECK (result IN ('passed', 'failed', 'blocked')),
    validator_reference text NOT NULL CHECK (length(validator_reference) BETWEEN 1 AND 500),
    validated_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK ((result = 'failed' AND validation_failure_entry_id IS NOT NULL) OR (result <> 'failed' AND validation_failure_entry_id IS NULL)),
    UNIQUE (capture_event_key, validator_reference, validated_at)
);

CREATE TABLE obs_capture.provider_testimony (
    provider_testimony_key text PRIMARY KEY CHECK (provider_testimony_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    provider_key text NOT NULL REFERENCES obs_capture.provider(provider_key),
    capture_event_key text NOT NULL REFERENCES obs_capture.capture_event(capture_event_key),
    testimony_fingerprint text NOT NULL CHECK (testimony_fingerprint ~ '^[0-9a-f]{64}$'),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (provider_key, capture_event_key, testimony_fingerprint)
);

CREATE TABLE obs_capture.provider_testimony_transition (
    provider_testimony_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_testimony_key text NOT NULL REFERENCES obs_capture.provider_testimony(provider_testimony_key),
    transition_type text NOT NULL CHECK (transition_type IN ('recorded', 'invalidated', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (provider_testimony_key, transition_type, effective_at)
);

CREATE TABLE obs_capture.shape_fingerprint (
    shape_fingerprint_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provider_key text NOT NULL REFERENCES obs_capture.provider(provider_key),
    shape_sha256 text NOT NULL CHECK (shape_sha256 ~ '^[0-9a-f]{64}$'),
    first_observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (provider_key, shape_sha256)
);

CREATE TABLE obs_capture.shape_recognition_transition (
    shape_recognition_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    shape_fingerprint_id bigint NOT NULL REFERENCES obs_capture.shape_fingerprint(shape_fingerprint_id),
    transition_type text NOT NULL CHECK (transition_type IN ('recognized', 'unknown', 'deprecated', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (shape_fingerprint_id, transition_type, effective_at)
);

CREATE TABLE obs_capture.parser_reference (
    parser_reference_key text PRIMARY KEY CHECK (parser_reference_key ~ '^[a-z][a-z0-9_.-]{2,127}$'),
    implementation_sha256 text NOT NULL CHECK (implementation_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_capture.parser_support_transition (
    parser_support_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parser_reference_key text NOT NULL REFERENCES obs_capture.parser_reference(parser_reference_key),
    shape_fingerprint_id bigint NOT NULL REFERENCES obs_capture.shape_fingerprint(shape_fingerprint_id),
    transition_type text NOT NULL CHECK (transition_type IN ('supported', 'unsupported', 'deprecated', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (parser_reference_key, shape_fingerprint_id, transition_type, effective_at)
);

CREATE TABLE obs_capture.drift_event (
    drift_event_key text PRIMARY KEY CHECK (drift_event_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    provider_key text NOT NULL REFERENCES obs_capture.provider(provider_key),
    prior_shape_fingerprint_id bigint REFERENCES obs_capture.shape_fingerprint(shape_fingerprint_id),
    observed_shape_fingerprint_id bigint NOT NULL REFERENCES obs_capture.shape_fingerprint(shape_fingerprint_id),
    detected_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (prior_shape_fingerprint_id IS NULL OR prior_shape_fingerprint_id <> observed_shape_fingerprint_id)
);

CREATE TABLE obs_capture.drift_review_transition (
    drift_review_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    drift_event_key text NOT NULL REFERENCES obs_capture.drift_event(drift_event_key),
    transition_type text NOT NULL CHECK (transition_type IN ('opened', 'acknowledged', 'resolved', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (drift_event_key, transition_type, effective_at)
);

CREATE INDEX capture_package_scope_idx ON obs_capture.capture_package(scope_key, target_key, requested_at DESC);
CREATE INDEX capture_event_package_idx ON obs_capture.capture_event(capture_package_key, observed_at DESC);
CREATE INDEX provider_testimony_event_idx ON obs_capture.provider_testimony(capture_event_key, provider_key);

DO $$
DECLARE relation_name text;
BEGIN
    FOREACH relation_name IN ARRAY ARRAY[
        'query_panel_version','query_panel_item','query_panel_transition','panel_run','panel_run_transition',
        'provider_transition','capture_package','capture_package_transition','capture_event','capture_event_transition',
        'validation_failure_version','validation_failure_entry','validation_result','provider_testimony',
        'provider_testimony_transition','shape_fingerprint','shape_recognition_transition','parser_reference',
        'parser_support_transition','drift_event','drift_review_transition'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON obs_capture.%I FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation()',
            relation_name,
            relation_name
        );
    END LOOP;
END;
$$;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_capture FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_capture FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_capture REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_capture REVOKE ALL ON SEQUENCES FROM PUBLIC;
