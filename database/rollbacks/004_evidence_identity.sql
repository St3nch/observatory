-- observatory-db4: {"version":"004","direction":"rollback","responsibility":"evidence_identity","paired_path":"database/migrations/004_evidence_identity.sql","required_prior":"004","resulting_version":"003","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_evidence"],"destructive":"disposable_only"}

DROP TABLE IF EXISTS obs_evidence.citation_handle_transition;
DROP TABLE IF EXISTS obs_evidence.citation_handle;
DROP TABLE IF EXISTS obs_evidence.evidence_identity_transition;
DROP TABLE IF EXISTS obs_evidence.evidence_identity;
DROP TABLE IF EXISTS obs_evidence.observation_transition;
DROP FUNCTION IF EXISTS obs_evidence.enforce_accepted_admission();
DROP TABLE IF EXISTS obs_evidence.observation;
DROP TABLE IF EXISTS obs_evidence.admission_transition;
DROP TABLE IF EXISTS obs_evidence.candidate_observation_transition;
DROP TABLE IF EXISTS obs_evidence.candidate_observation;
DROP TABLE IF EXISTS obs_evidence.observed_artifact_transition;
DROP TABLE IF EXISTS obs_evidence.observed_artifact_reference;
