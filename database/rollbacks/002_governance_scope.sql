-- observatory-db4: {"version":"002","direction":"rollback","responsibility":"governance_scope","paired_path":"database/migrations/002_governance_scope.sql","required_prior":"002","resulting_version":"001","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_governance"],"destructive":"disposable_only"}

DROP TABLE IF EXISTS obs_governance.assignment_transition;
DROP TABLE IF EXISTS obs_governance.volatility_assignment;
DROP TABLE IF EXISTS obs_governance.freshness_assignment;
DROP TABLE IF EXISTS obs_governance.retention_assignment;
DROP TABLE IF EXISTS obs_governance.rights_assignment;
DROP TABLE IF EXISTS obs_governance.source_family_assignment;
DROP TABLE IF EXISTS obs_governance.target_binding;
DROP TABLE IF EXISTS obs_governance.governed_target;
DROP TABLE IF EXISTS obs_governance.capture_instrument_transition;
DROP TABLE IF EXISTS obs_governance.capture_instrument;
DROP TABLE IF EXISTS obs_governance.source_family_transition;
DROP TABLE IF EXISTS obs_governance.source_family;
DROP TABLE IF EXISTS obs_governance.vocabulary_transition;
DROP TABLE IF EXISTS obs_governance.vocabulary_entry;
DROP TABLE IF EXISTS obs_governance.vocabulary_version;
DROP TABLE IF EXISTS obs_governance.vocabulary_family;
DROP TABLE IF EXISTS obs_governance.scope_transition;
DROP TABLE IF EXISTS obs_governance.scope;
