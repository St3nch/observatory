-- db4-broken-fixture: schema_version_divergence
-- fixture_id: 009_schema_version_divergence
-- violated_invariant: migration history rows require valid SHA-bound fingerprints and accepted direction grammar
-- rejection_class: postgresql_native
-- rejection_point: obs_meta.schema_migration CHECK constraints
-- expected_sqlstate: 23514
-- residue_relation: none
-- history_expectation: zero version-999 rows and zero accepted candidate history rows
-- cleanup_expectation: failed INSERT leaves accepted history unchanged
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
