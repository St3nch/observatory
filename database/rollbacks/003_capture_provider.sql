-- observatory-db4: {"version":"003","direction":"rollback","responsibility":"capture_provider","paired_path":"database/migrations/003_capture_provider.sql","required_prior":"003","resulting_version":"002","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_capture"],"destructive":"disposable_only"}

DROP TABLE IF EXISTS obs_capture.drift_review_transition;
DROP TABLE IF EXISTS obs_capture.drift_event;
DROP TABLE IF EXISTS obs_capture.parser_support_transition;
DROP TABLE IF EXISTS obs_capture.parser_reference;
DROP TABLE IF EXISTS obs_capture.shape_recognition_transition;
DROP TABLE IF EXISTS obs_capture.shape_fingerprint;
DROP TABLE IF EXISTS obs_capture.provider_testimony_transition;
DROP TABLE IF EXISTS obs_capture.provider_testimony;
DROP TABLE IF EXISTS obs_capture.validation_result;
DROP TABLE IF EXISTS obs_capture.validation_failure_entry;
DROP TABLE IF EXISTS obs_capture.validation_failure_version;
DROP TABLE IF EXISTS obs_capture.capture_event_transition;
DROP TABLE IF EXISTS obs_capture.capture_event;
DROP TABLE IF EXISTS obs_capture.capture_package_transition;
DROP TABLE IF EXISTS obs_capture.capture_package;
DROP TABLE IF EXISTS obs_capture.provider_transition;
DROP TABLE IF EXISTS obs_capture.provider;
DROP TABLE IF EXISTS obs_capture.panel_run_transition;
DROP TABLE IF EXISTS obs_capture.panel_run;
DROP TABLE IF EXISTS obs_capture.query_panel_transition;
DROP TABLE IF EXISTS obs_capture.query_panel_item;
DROP TABLE IF EXISTS obs_capture.query_panel_version;
DROP TABLE IF EXISTS obs_capture.query_panel;
