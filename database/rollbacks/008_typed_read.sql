-- observatory-db4: {"version":"008","direction":"rollback","responsibility":"typed_read","paired_path":"database/migrations/008_typed_read.sql","required_prior":"008","resulting_version":"007","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_read"],"destructive":"disposable_only"}

DROP VIEW IF EXISTS obs_read.raw_support_status;
DROP VIEW IF EXISTS obs_read.observation_warning;
DROP VIEW IF EXISTS obs_read.current_governance_disposition;
DROP VIEW IF EXISTS obs_read.provider_attribution;
DROP VIEW IF EXISTS obs_read.observation_package_read;
DROP VIEW IF EXISTS obs_read.evidence_lookup;
DROP VIEW IF EXISTS obs_read.citation_resolution;
DROP VIEW IF EXISTS obs_read.observation_summary;
