-- db4-broken-fixture: schema_version_divergence
INSERT INTO obs_meta.schema_migration(
    version,
    direction,
    relative_path,
    file_sha256,
    authority_reference,
    before_fingerprint,
    after_fingerprint
) VALUES (
    '999',
    'up',
    'database/hammer-fixtures/009_schema_version_divergence.sql',
    '0',
    'decisions/invalid.md',
    'divergent',
    'divergent'
);
