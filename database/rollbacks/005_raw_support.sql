-- observatory-db4: {"version":"005","direction":"rollback","responsibility":"raw_support","paired_path":"database/migrations/005_raw_support.sql","required_prior":"005","resulting_version":"004","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_raw"],"destructive":"disposable_only"}

DROP FUNCTION IF EXISTS obs_raw.db4_probe_reversible_locator_rejection();
DROP TABLE IF EXISTS obs_raw.raw_integrity_observation;
DROP TABLE IF EXISTS obs_raw.opaque_artifact_token_transition;
DROP TABLE IF EXISTS obs_raw.opaque_artifact_token;
DROP TABLE IF EXISTS obs_raw.raw_payload_transition;
DROP TABLE IF EXISTS obs_raw.raw_payload_identity;
DROP TABLE IF EXISTS obs_raw.raw_manifest_transition;
DROP TABLE IF EXISTS obs_raw.raw_manifest;
