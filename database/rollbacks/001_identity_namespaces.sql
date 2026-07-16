-- observatory-db4: {"version":"001","direction":"rollback","responsibility":"identity_namespaces","paired_path":"database/migrations/001_identity_namespaces.sql","required_prior":"001","resulting_version":"000","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_meta","obs_governance","obs_capture","obs_evidence","obs_raw","obs_audit","obs_security","obs_read"],"destructive":"disposable_only"}

DROP SCHEMA IF EXISTS obs_read CASCADE;
DROP SCHEMA IF EXISTS obs_security CASCADE;
DROP SCHEMA IF EXISTS obs_audit CASCADE;
DROP SCHEMA IF EXISTS obs_raw CASCADE;
DROP SCHEMA IF EXISTS obs_evidence CASCADE;
DROP SCHEMA IF EXISTS obs_capture CASCADE;
DROP SCHEMA IF EXISTS obs_governance CASCADE;
DROP SCHEMA IF EXISTS obs_meta CASCADE;
