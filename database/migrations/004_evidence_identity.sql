-- observatory-db4: {"version":"004","direction":"forward","responsibility":"evidence_identity","paired_path":"database/rollbacks/004_evidence_identity.sql","required_prior":"003","resulting_version":"004","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_evidence"],"destructive":"none"}

CREATE TABLE obs_evidence.observed_artifact_reference (
    observed_artifact_key text PRIMARY KEY CHECK (observed_artifact_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    capture_event_key text NOT NULL REFERENCES obs_capture.capture_event(capture_event_key),
    artifact_class text NOT NULL CHECK (artifact_class IN ('serp_item', 'marketplace_item', 'video_item', 'ai_answer_citation', 'public_document', 'manual_observation')),
    artifact_fingerprint text NOT NULL CHECK (artifact_fingerprint ~ '^[0-9a-f]{64}$'),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_event_key, artifact_class, artifact_fingerprint)
);

CREATE TABLE obs_evidence.observed_artifact_transition (
    observed_artifact_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    observed_artifact_key text NOT NULL REFERENCES obs_evidence.observed_artifact_reference(observed_artifact_key),
    transition_type text NOT NULL CHECK (transition_type IN ('recorded', 'invalidated', 'superseded')),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (observed_artifact_key, transition_type, effective_at)
);

CREATE TABLE obs_evidence.candidate_observation (
    candidate_observation_key text PRIMARY KEY CHECK (candidate_observation_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    capture_package_key text NOT NULL REFERENCES obs_capture.capture_package(capture_package_key),
    observed_artifact_key text NOT NULL REFERENCES obs_evidence.observed_artifact_reference(observed_artifact_key),
    candidate_fingerprint text NOT NULL CHECK (candidate_fingerprint ~ '^[0-9a-f]{64}$'),
    proposed_value jsonb NOT NULL CHECK (jsonb_typeof(proposed_value) IN ('object', 'array', 'string', 'number', 'boolean')),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (capture_package_key, observed_artifact_key, candidate_fingerprint)
);

CREATE TABLE obs_evidence.candidate_observation_transition (
    candidate_observation_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_observation_key text NOT NULL REFERENCES obs_evidence.candidate_observation(candidate_observation_key),
    transition_type text NOT NULL CHECK (transition_type IN ('proposed', 'validated', 'rejected', 'superseded')),
    reason_key text,
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (candidate_observation_key, transition_type, effective_at)
);

CREATE TABLE obs_evidence.admission_transition (
    admission_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    candidate_observation_key text NOT NULL REFERENCES obs_evidence.candidate_observation(candidate_observation_key),
    outcome text NOT NULL CHECK (outcome IN ('accepted', 'rejected', 'blocked')),
    rights_assignment_id bigint REFERENCES obs_governance.rights_assignment(rights_assignment_id),
    retention_assignment_id bigint REFERENCES obs_governance.retention_assignment(retention_assignment_id),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    CHECK (
        (outcome = 'accepted' AND rights_assignment_id IS NOT NULL AND retention_assignment_id IS NOT NULL)
        OR (outcome <> 'accepted' AND rights_assignment_id IS NULL AND retention_assignment_id IS NULL)
    ),
    UNIQUE (candidate_observation_key)
);

CREATE TABLE obs_evidence.observation (
    observation_key text PRIMARY KEY CHECK (observation_key ~ '^[a-z][a-z0-9_-]{7,127}$'),
    scope_key text NOT NULL REFERENCES obs_governance.scope(scope_key),
    target_key text NOT NULL REFERENCES obs_governance.governed_target(target_key),
    capture_package_key text NOT NULL REFERENCES obs_capture.capture_package(capture_package_key),
    candidate_observation_key text NOT NULL UNIQUE REFERENCES obs_evidence.candidate_observation(candidate_observation_key),
    admission_transition_id bigint NOT NULL UNIQUE REFERENCES obs_evidence.admission_transition(admission_transition_id),
    rights_assignment_id bigint NOT NULL REFERENCES obs_governance.rights_assignment(rights_assignment_id),
    retention_assignment_id bigint NOT NULL REFERENCES obs_governance.retention_assignment(retention_assignment_id),
    observed_value jsonb NOT NULL CHECK (jsonb_typeof(observed_value) IN ('object', 'array', 'string', 'number', 'boolean')),
    observed_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (scope_key, target_key, candidate_observation_key)
);

CREATE TABLE obs_evidence.observation_transition (
    observation_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    observation_key text NOT NULL REFERENCES obs_evidence.observation(observation_key),
    transition_type text NOT NULL CHECK (transition_type IN ('admitted', 'invalidated', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (observation_key, transition_type, effective_at)
);

CREATE TABLE obs_evidence.evidence_identity (
    evidence_key text PRIMARY KEY CHECK (evidence_key ~ '^ev_[a-z0-9_-]{20,120}$'),
    observation_key text NOT NULL UNIQUE REFERENCES obs_evidence.observation(observation_key),
    identity_fingerprint text NOT NULL UNIQUE CHECK (identity_fingerprint ~ '^[0-9a-f]{64}$'),
    minted_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_evidence.evidence_identity_transition (
    evidence_identity_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    evidence_key text NOT NULL REFERENCES obs_evidence.evidence_identity(evidence_key),
    transition_type text NOT NULL CHECK (transition_type IN ('minted', 'invalidated', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (evidence_key, transition_type, effective_at)
);

CREATE TABLE obs_evidence.citation_handle (
    citation_handle text PRIMARY KEY CHECK (citation_handle ~ '^cit_[A-Za-z0-9_-]{32,120}$'),
    evidence_key text NOT NULL UNIQUE REFERENCES obs_evidence.evidence_identity(evidence_key),
    handle_fingerprint text NOT NULL UNIQUE CHECK (handle_fingerprint ~ '^[0-9a-f]{64}$'),
    minted_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TABLE obs_evidence.citation_handle_transition (
    citation_handle_transition_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    citation_handle text NOT NULL REFERENCES obs_evidence.citation_handle(citation_handle),
    transition_type text NOT NULL CHECK (transition_type IN ('minted', 'revoked', 'superseded')),
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    effective_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp(),
    UNIQUE (citation_handle, transition_type, effective_at)
);

CREATE FUNCTION obs_evidence.enforce_accepted_admission()
RETURNS trigger
LANGUAGE plpgsql
SET search_path = pg_catalog, obs_evidence, obs_governance
AS $$
DECLARE admission obs_evidence.admission_transition%ROWTYPE;
BEGIN
    SELECT * INTO admission
    FROM obs_evidence.admission_transition
    WHERE admission_transition_id = NEW.admission_transition_id;

    IF admission.outcome <> 'accepted'
       OR admission.candidate_observation_key <> NEW.candidate_observation_key
       OR admission.rights_assignment_id <> NEW.rights_assignment_id
       OR admission.retention_assignment_id <> NEW.retention_assignment_id THEN
        RAISE EXCEPTION 'observation admission binding is invalid' USING ERRCODE = '23514';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER observation_accepted_admission
BEFORE INSERT ON obs_evidence.observation
FOR EACH ROW EXECUTE FUNCTION obs_evidence.enforce_accepted_admission();

CREATE INDEX observation_scope_time_idx ON obs_evidence.observation(scope_key, observed_at DESC, observation_key);
CREATE INDEX candidate_scope_time_idx ON obs_evidence.candidate_observation(scope_key, observed_at DESC, candidate_observation_key);

DO $$
DECLARE relation_name text;
BEGIN
    FOREACH relation_name IN ARRAY ARRAY[
        'observed_artifact_reference','observed_artifact_transition','candidate_observation',
        'candidate_observation_transition','admission_transition','observation','observation_transition',
        'evidence_identity','evidence_identity_transition','citation_handle','citation_handle_transition'
    ]
    LOOP
        EXECUTE format(
            'CREATE TRIGGER %I_append_only BEFORE UPDATE OR DELETE ON obs_evidence.%I FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation()',
            relation_name,
            relation_name
        );
    END LOOP;
END;
$$;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_evidence FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA obs_evidence FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_evidence FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_evidence REVOKE ALL ON TABLES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_evidence REVOKE ALL ON SEQUENCES FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_evidence REVOKE ALL ON FUNCTIONS FROM PUBLIC;
