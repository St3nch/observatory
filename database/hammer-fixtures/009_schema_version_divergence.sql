-- db4-broken-fixture: schema_version_divergence
BEGIN;
INSERT INTO observatory_meta.schema_migration(version,file_sha256,schema_fingerprint) VALUES ('999','0','divergent');
COMMIT;
