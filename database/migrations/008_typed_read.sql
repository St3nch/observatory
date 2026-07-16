-- observatory-db4: {"version":"008","direction":"forward","responsibility":"typed_read","paired_path":"database/rollbacks/008_typed_read.sql","required_prior":"007","resulting_version":"008","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_read"],"destructive":"none"}

CREATE VIEW obs_read.observation_summary
WITH (security_barrier = true)
AS
SELECT
    observation.scope_key,
    observation.observation_key,
    evidence.evidence_key,
    citation.citation_handle,
    observation.target_key,
    observation.observed_at,
    observation.observed_value
FROM obs_evidence.observation observation
JOIN obs_evidence.evidence_identity evidence
  ON evidence.observation_key = observation.observation_key
LEFT JOIN obs_evidence.citation_handle citation
  ON citation.evidence_key = evidence.evidence_key
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.citation_resolution
WITH (security_barrier = true)
AS
SELECT
    candidate.candidate_observation_key AS candidate_probe_key,
    citation.citation_handle,
    evidence.evidence_key,
    observation.observation_key,
    observation.scope_key,
    observation.target_key,
    observation.observed_at,
    observation.observed_value
FROM obs_evidence.candidate_observation candidate
JOIN obs_evidence.admission_transition admission
  ON admission.candidate_observation_key = candidate.candidate_observation_key
 AND admission.outcome = 'accepted'
JOIN obs_evidence.observation observation
  ON observation.candidate_observation_key = candidate.candidate_observation_key
 AND observation.admission_transition_id = admission.admission_transition_id
JOIN obs_evidence.evidence_identity evidence
  ON evidence.observation_key = observation.observation_key
JOIN obs_evidence.citation_handle citation
  ON citation.evidence_key = evidence.evidence_key
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.evidence_lookup
WITH (security_barrier = true)
AS
SELECT
    evidence.evidence_key,
    citation.citation_handle,
    observation.scope_key,
    observation.target_key,
    observation.observed_at,
    observation.observed_value,
    observation.capture_package_key
FROM obs_evidence.evidence_identity evidence
JOIN obs_evidence.observation observation
  ON observation.observation_key = evidence.observation_key
LEFT JOIN obs_evidence.citation_handle citation
  ON citation.evidence_key = evidence.evidence_key
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.observation_package_read
WITH (security_barrier = true)
AS
SELECT
    observation.scope_key,
    observation.observation_key,
    observation.capture_package_key,
    package.panel_run_key,
    package.target_key,
    package.capture_instrument_key,
    package.provider_key,
    package.requested_at,
    package.completed_at,
    package.request_fingerprint,
    package.response_fingerprint,
    observation.observed_at
FROM obs_evidence.observation observation
JOIN obs_capture.capture_package package
  ON package.capture_package_key = observation.capture_package_key
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.provider_attribution
WITH (security_barrier = true)
AS
SELECT
    observation.scope_key,
    observation.observation_key,
    package.provider_key,
    provider.provider_class,
    provider.display_label,
    testimony.provider_testimony_key,
    testimony.observed_at AS testimony_observed_at
FROM obs_evidence.observation observation
JOIN obs_capture.capture_package package
  ON package.capture_package_key = observation.capture_package_key
LEFT JOIN obs_capture.provider provider
  ON provider.provider_key = package.provider_key
LEFT JOIN obs_capture.capture_event event
  ON event.capture_package_key = package.capture_package_key
LEFT JOIN obs_capture.provider_testimony testimony
  ON testimony.capture_event_key = event.capture_event_key
 AND testimony.provider_key = package.provider_key
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.current_governance_disposition
WITH (security_barrier = true)
AS
SELECT
    target.scope_key,
    target.target_key,
    rights.rights_class,
    rights.effective_at AS rights_effective_at,
    rights.expires_at AS rights_expires_at,
    retention.retention_class,
    retention.retention_days,
    retention.effective_at AS retention_effective_at,
    retention.expires_at AS retention_expires_at,
    freshness.freshness_seconds,
    freshness.effective_at AS freshness_effective_at,
    volatility.volatility_class,
    volatility.effective_at AS volatility_effective_at
FROM obs_governance.governed_target target
LEFT JOIN LATERAL (
    SELECT assignment.*
    FROM obs_governance.rights_assignment assignment
    WHERE assignment.target_key = target.target_key
      AND assignment.effective_at <= statement_timestamp()
      AND (assignment.expires_at IS NULL OR assignment.expires_at > statement_timestamp())
    ORDER BY assignment.effective_at DESC, assignment.rights_assignment_id DESC
    LIMIT 1
) rights ON true
LEFT JOIN LATERAL (
    SELECT assignment.*
    FROM obs_governance.retention_assignment assignment
    WHERE assignment.target_key = target.target_key
      AND assignment.effective_at <= statement_timestamp()
      AND (assignment.expires_at IS NULL OR assignment.expires_at > statement_timestamp())
    ORDER BY assignment.effective_at DESC, assignment.retention_assignment_id DESC
    LIMIT 1
) retention ON true
LEFT JOIN LATERAL (
    SELECT assignment.*
    FROM obs_governance.freshness_assignment assignment
    WHERE assignment.target_key = target.target_key
      AND assignment.effective_at <= statement_timestamp()
      AND (assignment.expires_at IS NULL OR assignment.expires_at > statement_timestamp())
    ORDER BY assignment.effective_at DESC, assignment.freshness_assignment_id DESC
    LIMIT 1
) freshness ON true
LEFT JOIN LATERAL (
    SELECT assignment.*
    FROM obs_governance.volatility_assignment assignment
    WHERE assignment.target_key = target.target_key
      AND assignment.effective_at <= statement_timestamp()
      AND (assignment.expires_at IS NULL OR assignment.expires_at > statement_timestamp())
    ORDER BY assignment.effective_at DESC, assignment.volatility_assignment_id DESC
    LIMIT 1
) volatility ON true
WHERE target.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.observation_warning
WITH (security_barrier = true)
AS
SELECT
    observation.scope_key,
    observation.observation_key,
    warning.warning_key,
    warning.warning_text
FROM obs_evidence.observation observation
CROSS JOIN LATERAL (
    SELECT 'missing_provider_attribution'::text AS warning_key,
           'No provider attribution was recorded for the capture package.'::text AS warning_text
    WHERE NOT EXISTS (
        SELECT 1
        FROM obs_capture.capture_package package
        WHERE package.capture_package_key = observation.capture_package_key
          AND package.provider_key IS NOT NULL
    )
    UNION ALL
    SELECT 'retention_expired', 'The bound retention assignment is no longer effective.'
    WHERE EXISTS (
        SELECT 1
        FROM obs_governance.retention_assignment retention
        WHERE retention.retention_assignment_id = observation.retention_assignment_id
          AND retention.expires_at IS NOT NULL
          AND retention.expires_at <= statement_timestamp()
    )
) warning
WHERE observation.scope_key = current_setting('ob.scope_key', true);

CREATE VIEW obs_read.raw_support_status
WITH (security_barrier = true)
AS
SELECT
    observation.scope_key,
    observation.observation_key,
    manifest.raw_manifest_key,
    payload.raw_payload_key,
    payload.hash_algorithm,
    payload.content_digest,
    payload.byte_count,
    payload.media_type,
    latest.result AS latest_integrity_result,
    latest.observed_at AS latest_integrity_observed_at
FROM obs_evidence.observation observation
JOIN obs_raw.raw_manifest manifest
  ON manifest.observation_key = observation.observation_key
LEFT JOIN obs_raw.raw_payload_identity payload
  ON payload.raw_manifest_key = manifest.raw_manifest_key
LEFT JOIN LATERAL (
    SELECT integrity.result, integrity.observed_at
    FROM obs_raw.raw_integrity_observation integrity
    WHERE integrity.raw_payload_key = payload.raw_payload_key
    ORDER BY integrity.observed_at DESC, integrity.raw_integrity_observation_id DESC
    LIMIT 1
) latest ON true
WHERE observation.scope_key = current_setting('ob.scope_key', true);

GRANT SELECT ON obs_read.observation_summary, obs_read.citation_resolution, obs_read.evidence_lookup, obs_read.observation_package_read, obs_read.provider_attribution, obs_read.current_governance_disposition, obs_read.observation_warning, obs_read.raw_support_status TO observatory_test_reader, observatory_test_auditor, observatory_test_backup;

REVOKE ALL ON ALL TABLES IN SCHEMA obs_read FROM PUBLIC;
ALTER DEFAULT PRIVILEGES IN SCHEMA obs_read REVOKE ALL ON TABLES FROM PUBLIC;
