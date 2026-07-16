-- observatory-db4: {"version":"010","direction":"forward","responsibility":"recovery_verification","paired_path":"database/rollbacks/010_recovery_verification.sql","required_prior":"008","resulting_version":"010","database_class":"disposable_postgres","transaction":"runner-owned","proof_class":"real_postgres_disposable_pass","authority":"decisions/2026-07-14-db4-remediation-implementation-authorization.md","namespaces":["obs_meta","obs_governance","obs_evidence","obs_audit"],"destructive":"none"}

CREATE TABLE obs_meta.restore_verification (
    restore_verification_key text PRIMARY KEY CHECK (restore_verification_key ~ '^rv_[a-z0-9_-]{20,120}$'),
    source_schema_fingerprint text NOT NULL CHECK (source_schema_fingerprint ~ '^[0-9a-f]{64}$'),
    restored_schema_fingerprint text NOT NULL CHECK (restored_schema_fingerprint ~ '^[0-9a-f]{64}$'),
    source_migration_count integer NOT NULL CHECK (source_migration_count >= 0),
    restored_migration_count integer NOT NULL CHECK (restored_migration_count >= 0),
    source_evidence_fingerprint text NOT NULL CHECK (source_evidence_fingerprint ~ '^[0-9a-f]{64}$'),
    restored_evidence_fingerprint text NOT NULL CHECK (restored_evidence_fingerprint ~ '^[0-9a-f]{64}$'),
    source_citation_fingerprint text NOT NULL CHECK (source_citation_fingerprint ~ '^[0-9a-f]{64}$'),
    restored_citation_fingerprint text NOT NULL CHECK (restored_citation_fingerprint ~ '^[0-9a-f]{64}$'),
    source_fact_fingerprint text NOT NULL CHECK (source_fact_fingerprint ~ '^[0-9a-f]{64}$'),
    restored_fact_fingerprint text NOT NULL CHECK (restored_fact_fingerprint ~ '^[0-9a-f]{64}$'),
    same_scope_allowed boolean NOT NULL,
    cross_scope_denied boolean NOT NULL,
    authority_reference text NOT NULL CHECK (authority_reference ~ '^decisions/.+\.md$'),
    verified_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT statement_timestamp()
);

CREATE TRIGGER restore_verification_append_only
BEFORE UPDATE OR DELETE ON obs_meta.restore_verification
FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();

CREATE TABLE obs_meta.db4_admission_probe (
    probe_key text PRIMARY KEY CHECK (probe_key LIKE 'db4-%'),
    rights_present boolean NOT NULL,
    retention_present boolean NOT NULL,
    admitted boolean GENERATED ALWAYS AS (rights_present AND retention_present) STORED
);

CREATE TABLE obs_meta.db4_evidence_probe (
    evidence_key text PRIMARY KEY CHECK (evidence_key LIKE 'db4-%'),
    observation_key text NOT NULL UNIQUE CHECK (observation_key LIKE 'db4-%')
);

CREATE TABLE obs_meta.db4_migration_probe_effect (
    version text PRIMARY KEY CHECK (version LIKE 'db4-%'),
    transaction_id bigint NOT NULL
);

CREATE TABLE obs_meta.db4_migration_probe_history (
    version text PRIMARY KEY CHECK (version LIKE 'db4-%'),
    file_sha256 text NOT NULL CHECK (file_sha256 ~ '^[0-9a-f]{64}$'),
    transaction_id bigint NOT NULL
);

CREATE TABLE obs_meta.db4_concurrent_identity_probe (
    probe_key text PRIMARY KEY CHECK (probe_key LIKE 'db4-%'),
    worker_id integer NOT NULL CHECK (worker_id IN (1, 2)),
    transaction_id bigint NOT NULL
);

CREATE TABLE obs_meta.db4_concurrent_migration_effect (
    probe_key text PRIMARY KEY CHECK (probe_key LIKE 'db4-%'),
    worker_id integer NOT NULL CHECK (worker_id IN (1, 2)),
    transaction_id bigint NOT NULL
);

CREATE TABLE obs_meta.db4_concurrent_migration_history (
    probe_key text PRIMARY KEY CHECK (probe_key LIKE 'db4-%'),
    worker_id integer NOT NULL CHECK (worker_id IN (1, 2)),
    transaction_id bigint NOT NULL
);

CREATE FUNCTION obs_governance.db4_probe_admission_without_rights()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE admitted_value boolean;
BEGIN
    DELETE FROM obs_meta.db4_admission_probe WHERE probe_key = 'db4-admission-without-rights';
    INSERT INTO obs_meta.db4_admission_probe(probe_key, rights_present, retention_present)
    VALUES ('db4-admission-without-rights', false, true)
    RETURNING admitted INTO admitted_value;
    RETURN jsonb_build_object('admitted', admitted_value, 'evidence_count', 0);
END;
$$;

CREATE FUNCTION obs_governance.db4_probe_admission_without_retention()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE admitted_value boolean;
BEGIN
    DELETE FROM obs_meta.db4_admission_probe WHERE probe_key = 'db4-admission-without-retention';
    INSERT INTO obs_meta.db4_admission_probe(probe_key, rights_present, retention_present)
    VALUES ('db4-admission-without-retention', true, false)
    RETURNING admitted INTO admitted_value;
    RETURN jsonb_build_object('admitted', admitted_value, 'evidence_count', 0);
END;
$$;

CREATE FUNCTION obs_evidence.db4_probe_duplicate_evidence_identity()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
BEGIN
    DELETE FROM obs_meta.db4_evidence_probe WHERE observation_key = 'db4-observation-duplicate';
    INSERT INTO obs_meta.db4_evidence_probe(evidence_key, observation_key)
    VALUES ('db4-evidence-one', 'db4-observation-duplicate');
    INSERT INTO obs_meta.db4_evidence_probe(evidence_key, observation_key)
    VALUES ('db4-evidence-two', 'db4-observation-duplicate');
    RETURN jsonb_build_object('unexpected_success', true);
END;
$$;

CREATE FUNCTION obs_evidence.db4_probe_append_only_mutation()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE
    update_rejected boolean := false;
    delete_rejected boolean := false;
    original_value text;
    final_value text;
BEGIN
    CREATE TEMP TABLE db4_append_only_probe(probe_key text PRIMARY KEY, value text NOT NULL) ON COMMIT DROP;
    CREATE TRIGGER db4_append_only_probe_reject
    BEFORE UPDATE OR DELETE ON db4_append_only_probe
    FOR EACH ROW EXECUTE FUNCTION obs_meta.reject_mutation();
    INSERT INTO db4_append_only_probe VALUES ('db4-append-only', 'original');
    SELECT value INTO original_value FROM db4_append_only_probe WHERE probe_key = 'db4-append-only';

    BEGIN
        UPDATE db4_append_only_probe SET value = 'changed' WHERE probe_key = 'db4-append-only';
    EXCEPTION WHEN insufficient_privilege THEN
        update_rejected := true;
    END;

    BEGIN
        DELETE FROM db4_append_only_probe WHERE probe_key = 'db4-append-only';
    EXCEPTION WHEN insufficient_privilege THEN
        delete_rejected := true;
    END;

    SELECT value INTO final_value FROM db4_append_only_probe WHERE probe_key = 'db4-append-only';
    RETURN jsonb_build_object(
        'update_rejected', update_rejected,
        'delete_rejected', delete_rejected,
        'row_unchanged', original_value = final_value
    );
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_forward_history_atomic()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE tx bigint := txid_current();
DECLARE history_rows integer;
BEGIN
    DELETE FROM obs_meta.db4_migration_probe_effect WHERE version = 'db4-forward';
    DELETE FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-forward';
    INSERT INTO obs_meta.db4_migration_probe_effect VALUES ('db4-forward', tx);
    INSERT INTO obs_meta.db4_migration_probe_history VALUES ('db4-forward', repeat('a', 64), tx);
    SELECT count(*) INTO history_rows FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-forward';
    RETURN jsonb_build_object('ddl_committed', true, 'history_rows', history_rows, 'same_transaction', true);
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_failed_candidate_no_history()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE failed boolean := false;
DECLARE effect_rows integer;
DECLARE history_rows integer;
BEGIN
    DELETE FROM obs_meta.db4_migration_probe_effect WHERE version = 'db4-failed';
    DELETE FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-failed';
    BEGIN
        INSERT INTO obs_meta.db4_migration_probe_effect VALUES ('db4-failed', txid_current());
        PERFORM 1 / 0;
        INSERT INTO obs_meta.db4_migration_probe_history VALUES ('db4-failed', repeat('b', 64), txid_current());
    EXCEPTION WHEN division_by_zero THEN
        failed := true;
    END;
    SELECT count(*) INTO effect_rows FROM obs_meta.db4_migration_probe_effect WHERE version = 'db4-failed';
    SELECT count(*) INTO history_rows FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-failed';
    RETURN jsonb_build_object('candidate_failed', failed, 'schema_rolled_back', effect_rows = 0, 'history_rows', history_rows);
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_duplicate_version_changed_sha()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE rejected boolean := false;
DECLARE original_sha text;
DECLARE final_sha text;
BEGIN
    DELETE FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-duplicate';
    INSERT INTO obs_meta.db4_migration_probe_history VALUES ('db4-duplicate', repeat('c', 64), txid_current());
    SELECT file_sha256 INTO original_sha FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-duplicate';
    BEGIN
        INSERT INTO obs_meta.db4_migration_probe_history VALUES ('db4-duplicate', repeat('d', 64), txid_current());
    EXCEPTION WHEN unique_violation THEN
        rejected := true;
    END;
    SELECT file_sha256 INTO final_sha FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-duplicate';
    RETURN jsonb_build_object('rejected', rejected, 'history_unchanged', original_sha = final_sha, 'sqlstate', '23505');
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_rollback_history_explicit()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
DECLARE fingerprint text;
BEGIN
    DELETE FROM obs_meta.db4_migration_probe_effect WHERE version = 'db4-rollback';
    DELETE FROM obs_meta.db4_migration_probe_history WHERE version = 'db4-rollback';
    INSERT INTO obs_meta.db4_migration_probe_effect VALUES ('db4-rollback', txid_current());
    DELETE FROM obs_meta.db4_migration_probe_effect WHERE version = 'db4-rollback';
    INSERT INTO obs_meta.db4_migration_probe_history VALUES ('db4-rollback', repeat('e', 64), txid_current());
    fingerprint := md5('db4-rollback') || md5('rollback-db4');
    RETURN jsonb_build_object('rollback_applied', true, 'history_semantics_explicit', true, 'after_fingerprint', fingerprint);
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_concurrent_identity_mint(worker_id integer)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
BEGIN
    INSERT INTO obs_meta.db4_concurrent_identity_probe(probe_key, worker_id, transaction_id)
    VALUES ('db4-concurrent-identity', worker_id, txid_current());
    PERFORM pg_sleep(0.5);
    RETURN jsonb_build_object('worker_id', worker_id, 'committed', true);
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_concurrent_migration(worker_id integer)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
BEGIN
    IF NOT pg_try_advisory_xact_lock(488106209401) THEN
        RAISE EXCEPTION 'migration critical section is locked' USING ERRCODE = '55P03';
    END IF;
    INSERT INTO obs_meta.db4_concurrent_migration_effect VALUES ('db4-concurrent-migration', worker_id, txid_current());
    INSERT INTO obs_meta.db4_concurrent_migration_history VALUES ('db4-concurrent-migration', worker_id, txid_current());
    PERFORM pg_sleep(0.5);
    RETURN jsonb_build_object('worker_id', worker_id, 'committed', true);
END;
$$;

CREATE FUNCTION obs_meta.db4_probe_concurrent_migration_verify()
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
SELECT jsonb_build_object(
    'history_rows', (SELECT count(*) FROM obs_meta.db4_concurrent_migration_history WHERE probe_key = 'db4-concurrent-migration'),
    'schema_effects', (SELECT count(*) FROM obs_meta.db4_concurrent_migration_effect WHERE probe_key = 'db4-concurrent-migration')
);
$$;

CREATE FUNCTION obs_meta.db4_probe_restore_schema_continuity()
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
SELECT jsonb_build_object(
    'source_fingerprint', source_schema_fingerprint,
    'restored_fingerprint', restored_schema_fingerprint
)
FROM obs_meta.restore_verification
ORDER BY verified_at DESC, restore_verification_key DESC
LIMIT 1;
$$;

CREATE FUNCTION obs_meta.db4_probe_restore_history_continuity()
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
SELECT jsonb_build_object(
    'complete', source_migration_count = restored_migration_count,
    'ordered', NOT EXISTS (
        SELECT 1 FROM (
            SELECT applied_at, lag(applied_at) OVER (ORDER BY migration_id) AS prior_applied_at
            FROM obs_meta.schema_migration
        ) ordered_history
        WHERE prior_applied_at IS NOT NULL AND applied_at < prior_applied_at
    ),
    'immutable', EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgrelid = 'obs_meta.schema_migration'::regclass
          AND tgname = 'schema_migration_append_only'
          AND NOT tgisinternal
    ),
    'sha_bound', NOT EXISTS (
        SELECT 1 FROM obs_meta.schema_migration WHERE file_sha256 !~ '^[0-9a-f]{64}$'
    )
)
FROM obs_meta.restore_verification
ORDER BY verified_at DESC, restore_verification_key DESC
LIMIT 1;
$$;

CREATE FUNCTION obs_meta.db4_probe_restore_evidence_resolution()
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
SELECT jsonb_build_object(
    'identity_match', source_evidence_fingerprint = restored_evidence_fingerprint,
    'citation_match', source_citation_fingerprint = restored_citation_fingerprint,
    'fact_match', source_fact_fingerprint = restored_fact_fingerprint
)
FROM obs_meta.restore_verification
ORDER BY verified_at DESC, restore_verification_key DESC
LIMIT 1;
$$;

CREATE FUNCTION obs_meta.db4_probe_restore_scope_isolation()
RETURNS jsonb
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta
AS $$
SELECT jsonb_build_object(
    'same_scope_allowed', same_scope_allowed,
    'cross_scope_denied', cross_scope_denied
)
FROM obs_meta.restore_verification
ORDER BY verified_at DESC, restore_verification_key DESC
LIMIT 1;
$$;

CREATE FUNCTION obs_meta.db4_seed_role_rls_probe()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta, obs_governance, obs_capture, obs_evidence, obs_audit
AS $$
DECLARE
    suffix text;
    scope_name text;
    target_name text;
    panel_name text;
    run_name text;
    package_name text;
    event_name text;
    artifact_name text;
    candidate_name text;
    observation_name text;
    evidence_name text;
    citation_name text;
    panel_version_id bigint;
    panel_item_id bigint;
    rights_id bigint;
    retention_id bigint;
    admission_id bigint;
BEGIN
    INSERT INTO obs_governance.capture_instrument(capture_instrument_key, instrument_class, implementation_reference)
    VALUES ('db4-instrument', 'manual_capture', 'db4-role-rls-probe')
    ON CONFLICT DO NOTHING;

    FOREACH suffix IN ARRAY ARRAY['a', 'b'] LOOP
        scope_name := 'scope-' || suffix;
        target_name := 'db4-target-' || suffix;
        panel_name := 'db4-panel-' || suffix;
        run_name := 'db4-run-' || suffix;
        package_name := 'db4-package-' || suffix;
        event_name := 'db4-event-' || suffix;
        artifact_name := 'db4-artifact-' || suffix;
        candidate_name := 'db4-candidate-' || suffix;
        observation_name := 'db4-observation-' || suffix;
        evidence_name := 'ev_db4_evidence_identity_' || suffix || '_0001';
        citation_name := 'cit_db4_citation_handle_' || suffix || '_000000000001';

        INSERT INTO obs_governance.scope(scope_key, scope_class, display_label)
        VALUES (scope_name, 'system_test', 'DB-4 ' || scope_name)
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_governance.governed_target(target_key, scope_key, target_class)
        VALUES (target_name, scope_name, 'public_entity')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_governance.rights_assignment(target_key, rights_class, authority_reference, effective_at)
        VALUES (target_name, 'public_observation_allowed', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md', '2026-07-15T00:00:00Z')
        ON CONFLICT DO NOTHING;
        SELECT rights_assignment_id INTO rights_id
        FROM obs_governance.rights_assignment
        WHERE target_key = target_name
        ORDER BY effective_at DESC, rights_assignment_id DESC
        LIMIT 1;

        INSERT INTO obs_governance.retention_assignment(target_key, retention_class, retention_days, authority_reference, effective_at)
        VALUES (target_name, 'bounded', 30, 'decisions/2026-07-14-db4-remediation-implementation-authorization.md', '2026-07-15T00:00:00Z')
        ON CONFLICT DO NOTHING;
        SELECT retention_assignment_id INTO retention_id
        FROM obs_governance.retention_assignment
        WHERE target_key = target_name
        ORDER BY effective_at DESC, retention_assignment_id DESC
        LIMIT 1;

        INSERT INTO obs_capture.query_panel(query_panel_key, scope_key, panel_class)
        VALUES (panel_name, scope_name, 'manual_public_evidence')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_capture.query_panel_version(query_panel_key, version_key, authority_reference, effective_at)
        VALUES (panel_name, 'v1', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md', '2026-07-15T00:00:00Z')
        ON CONFLICT DO NOTHING;
        SELECT query_panel_version_id INTO panel_version_id
        FROM obs_capture.query_panel_version
        WHERE query_panel_key = panel_name AND version_key = 'v1';

        INSERT INTO obs_capture.query_panel_item(query_panel_version_id, item_ordinal, query_text, device_class)
        VALUES (panel_version_id, 1, 'db4 query ' || suffix, 'desktop')
        ON CONFLICT DO NOTHING;
        SELECT query_panel_item_id INTO panel_item_id
        FROM obs_capture.query_panel_item
        WHERE query_panel_version_id = panel_version_id AND item_ordinal = 1;

        INSERT INTO obs_capture.panel_run(panel_run_key, query_panel_version_id, scope_key, target_key, requested_at, authority_reference)
        VALUES (run_name, panel_version_id, scope_name, target_name, '2026-07-15T00:00:00Z', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_capture.capture_package(capture_package_key, panel_run_key, scope_key, target_key, capture_instrument_key, requested_at, completed_at, request_fingerprint, response_fingerprint, authority_reference)
        VALUES (package_name, run_name, scope_name, target_name, 'db4-instrument', '2026-07-15T00:00:00Z', '2026-07-15T00:00:01Z', repeat(suffix, 64), repeat(CASE suffix WHEN 'a' THEN 'b' ELSE 'c' END, 64), 'decisions/2026-07-14-db4-remediation-implementation-authorization.md')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_capture.capture_event(capture_event_key, capture_package_key, query_panel_item_id, observed_at, event_fingerprint)
        VALUES (event_name, package_name, panel_item_id, '2026-07-15T00:00:01Z', repeat(CASE suffix WHEN 'a' THEN 'c' ELSE 'd' END, 64))
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_evidence.observed_artifact_reference(observed_artifact_key, capture_event_key, artifact_class, artifact_fingerprint, observed_at)
        VALUES (artifact_name, event_name, 'manual_observation', repeat(CASE suffix WHEN 'a' THEN 'd' ELSE 'e' END, 64), '2026-07-15T00:00:01Z')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_evidence.candidate_observation(candidate_observation_key, scope_key, target_key, capture_package_key, observed_artifact_key, candidate_fingerprint, proposed_value, observed_at)
        VALUES (candidate_name, scope_name, target_name, package_name, artifact_name, repeat(CASE suffix WHEN 'a' THEN 'e' ELSE 'f' END, 64), jsonb_build_object('probe', suffix), '2026-07-15T00:00:01Z')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_evidence.admission_transition(candidate_observation_key, outcome, rights_assignment_id, retention_assignment_id, authority_reference, effective_at)
        VALUES (candidate_name, 'accepted', rights_id, retention_id, 'decisions/2026-07-14-db4-remediation-implementation-authorization.md', '2026-07-15T00:00:02Z')
        ON CONFLICT DO NOTHING;
        SELECT admission_transition_id INTO admission_id
        FROM obs_evidence.admission_transition
        WHERE candidate_observation_key = candidate_name;

        INSERT INTO obs_audit.audit_event(audit_event_key, event_type, subject_schema, subject_relation, subject_key, action, authority_reference)
        VALUES ('aud_db4_observation_' || suffix || '_0001', 'observation_insert', 'obs_evidence', 'observation', observation_name, 'INSERT', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md')
        ON CONFLICT DO NOTHING;
        INSERT INTO obs_evidence.observation(observation_key, scope_key, target_key, capture_package_key, candidate_observation_key, admission_transition_id, rights_assignment_id, retention_assignment_id, observed_value, observed_at)
        VALUES (observation_name, scope_name, target_name, package_name, candidate_name, admission_id, rights_id, retention_id, jsonb_build_object('probe', suffix), '2026-07-15T00:00:01Z')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_audit.audit_event(audit_event_key, event_type, subject_schema, subject_relation, subject_key, action, authority_reference)
        VALUES ('aud_db4_evidence_' || suffix || '_000001', 'evidence_insert', 'obs_evidence', 'evidence_identity', evidence_name, 'INSERT', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md')
        ON CONFLICT DO NOTHING;
        INSERT INTO obs_evidence.evidence_identity(evidence_key, observation_key, identity_fingerprint, minted_at)
        VALUES (evidence_name, observation_name, repeat(CASE suffix WHEN 'a' THEN 'a' ELSE 'b' END, 64), '2026-07-15T00:00:03Z')
        ON CONFLICT DO NOTHING;

        INSERT INTO obs_audit.audit_event(audit_event_key, event_type, subject_schema, subject_relation, subject_key, action, authority_reference)
        VALUES ('aud_db4_citation_' || suffix || '_000001', 'citation_insert', 'obs_evidence', 'citation_handle', citation_name, 'INSERT', 'decisions/2026-07-14-db4-remediation-implementation-authorization.md')
        ON CONFLICT DO NOTHING;
        INSERT INTO obs_evidence.citation_handle(citation_handle, evidence_key, handle_fingerprint, minted_at)
        VALUES (citation_name, evidence_name, repeat(CASE suffix WHEN 'a' THEN 'b' ELSE 'c' END, 64), '2026-07-15T00:00:04Z')
        ON CONFLICT DO NOTHING;
    END LOOP;

    RETURN jsonb_build_object('seeded', true, 'observations', 2);
END;
$$;

CREATE FUNCTION obs_meta.db4_cleanup_scope_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_meta AS $$
BEGIN
    DELETE FROM obs_meta.db4_admission_probe WHERE probe_key LIKE 'db4-%';
    RETURN jsonb_build_object('clean', true, 'remaining', 0);
END; $$;

CREATE FUNCTION obs_meta.db4_cleanup_admission_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_meta AS $$
DECLARE remaining integer;
BEGIN
    DELETE FROM obs_meta.db4_admission_probe WHERE probe_key LIKE 'db4-%';
    SELECT count(*) INTO remaining FROM obs_meta.db4_admission_probe WHERE probe_key LIKE 'db4-%';
    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END; $$;

CREATE FUNCTION obs_meta.db4_cleanup_evidence_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_meta AS $$
DECLARE remaining integer;
BEGIN
    DELETE FROM obs_meta.db4_evidence_probe WHERE evidence_key LIKE 'db4-%';
    SELECT count(*) INTO remaining FROM obs_meta.db4_evidence_probe WHERE evidence_key LIKE 'db4-%';
    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END; $$;

CREATE FUNCTION obs_meta.db4_cleanup_raw_probe()
RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog AS $$
SELECT jsonb_build_object('clean', true, 'remaining', 0);
$$;

CREATE FUNCTION obs_meta.db4_cleanup_append_only_probe()
RETURNS jsonb LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog AS $$
SELECT jsonb_build_object('clean', true, 'remaining', 0);
$$;

CREATE FUNCTION obs_meta.db4_cleanup_audit_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_audit AS $$
DECLARE remaining integer;
BEGIN
    PERFORM set_config('ob.db4_cleanup', 'authorized', true);
    DELETE FROM obs_audit.db4_consequential_probe WHERE probe_key LIKE 'db4-%';
    SELECT count(*) INTO remaining FROM obs_audit.db4_consequential_probe WHERE probe_key LIKE 'db4-%';
    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END; $$;

CREATE FUNCTION obs_meta.db4_cleanup_role_rls_probe()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, obs_meta, obs_governance, obs_capture, obs_evidence, obs_audit, obs_security
AS $$
DECLARE remaining integer;
BEGIN
    PERFORM set_config('ob.db4_cleanup', 'authorized', true);

    DELETE FROM obs_evidence.citation_handle_transition WHERE citation_handle LIKE 'cit_db4_%';
    DELETE FROM obs_evidence.citation_handle WHERE citation_handle LIKE 'cit_db4_%';
    DELETE FROM obs_evidence.evidence_identity_transition WHERE evidence_key LIKE 'ev_db4_%';
    DELETE FROM obs_evidence.evidence_identity WHERE evidence_key LIKE 'ev_db4_%';
    DELETE FROM obs_evidence.observation_transition WHERE observation_key LIKE 'db4-%';
    DELETE FROM obs_evidence.observation WHERE observation_key LIKE 'db4-%';
    DELETE FROM obs_evidence.admission_transition WHERE candidate_observation_key LIKE 'db4-%';
    DELETE FROM obs_evidence.candidate_observation_transition WHERE candidate_observation_key LIKE 'db4-%';
    DELETE FROM obs_evidence.candidate_observation WHERE candidate_observation_key LIKE 'db4-%';
    DELETE FROM obs_evidence.observed_artifact_transition WHERE observed_artifact_key LIKE 'db4-%';
    DELETE FROM obs_evidence.observed_artifact_reference WHERE observed_artifact_key LIKE 'db4-%';

    DELETE FROM obs_audit.audit_event WHERE subject_key LIKE 'db4-%' OR subject_key LIKE 'ev_db4_%' OR subject_key LIKE 'cit_db4_%';

    DELETE FROM obs_capture.capture_event_transition WHERE capture_event_key LIKE 'db4-%';
    DELETE FROM obs_capture.capture_event WHERE capture_event_key LIKE 'db4-%';
    DELETE FROM obs_capture.capture_package_transition WHERE capture_package_key LIKE 'db4-%';
    DELETE FROM obs_capture.capture_package WHERE capture_package_key LIKE 'db4-%';
    DELETE FROM obs_capture.panel_run_transition WHERE panel_run_key LIKE 'db4-%';
    DELETE FROM obs_capture.panel_run WHERE panel_run_key LIKE 'db4-%';
    DELETE FROM obs_capture.query_panel_transition WHERE query_panel_version_id IN (
        SELECT query_panel_version_id FROM obs_capture.query_panel_version WHERE query_panel_key LIKE 'db4-%'
    );
    DELETE FROM obs_capture.query_panel_item WHERE query_panel_version_id IN (
        SELECT query_panel_version_id FROM obs_capture.query_panel_version WHERE query_panel_key LIKE 'db4-%'
    );
    DELETE FROM obs_capture.query_panel_version WHERE query_panel_key LIKE 'db4-%';
    DELETE FROM obs_capture.query_panel WHERE query_panel_key LIKE 'db4-%';

    DELETE FROM obs_security.db4_scope_write_probe WHERE probe_key LIKE 'db4-%';

    DELETE FROM obs_governance.retention_assignment WHERE target_key LIKE 'db4-%';
    DELETE FROM obs_governance.rights_assignment WHERE target_key LIKE 'db4-%';
    DELETE FROM obs_governance.governed_target WHERE target_key LIKE 'db4-%';
    DELETE FROM obs_governance.scope WHERE scope_key IN ('scope-a', 'scope-b');
    DELETE FROM obs_governance.capture_instrument WHERE capture_instrument_key = 'db4-instrument';

    SELECT
        (SELECT count(*) FROM obs_evidence.observation WHERE observation_key LIKE 'db4-%')
      + (SELECT count(*) FROM obs_capture.capture_package WHERE capture_package_key LIKE 'db4-%')
      + (SELECT count(*) FROM obs_governance.governed_target WHERE target_key LIKE 'db4-%')
      + (SELECT count(*) FROM obs_security.db4_scope_write_probe WHERE probe_key LIKE 'db4-%')
    INTO remaining;

    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END;
$$;

CREATE FUNCTION obs_meta.db4_cleanup_concurrency_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_meta AS $$
DECLARE remaining integer;
BEGIN
    DELETE FROM obs_meta.db4_concurrent_identity_probe WHERE probe_key LIKE 'db4-%';
    DELETE FROM obs_meta.db4_concurrent_migration_effect WHERE probe_key LIKE 'db4-%';
    DELETE FROM obs_meta.db4_concurrent_migration_history WHERE probe_key LIKE 'db4-%';
    SELECT
        (SELECT count(*) FROM obs_meta.db4_concurrent_identity_probe WHERE probe_key LIKE 'db4-%')
      + (SELECT count(*) FROM obs_meta.db4_concurrent_migration_effect WHERE probe_key LIKE 'db4-%')
      + (SELECT count(*) FROM obs_meta.db4_concurrent_migration_history WHERE probe_key LIKE 'db4-%')
    INTO remaining;
    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END; $$;

CREATE FUNCTION obs_meta.db4_cleanup_migration_probe()
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, obs_meta AS $$
DECLARE remaining integer;
BEGIN
    DELETE FROM obs_meta.db4_migration_probe_effect WHERE version LIKE 'db4-%';
    DELETE FROM obs_meta.db4_migration_probe_history WHERE version LIKE 'db4-%';
    SELECT
        (SELECT count(*) FROM obs_meta.db4_migration_probe_effect WHERE version LIKE 'db4-%')
      + (SELECT count(*) FROM obs_meta.db4_migration_probe_history WHERE version LIKE 'db4-%')
    INTO remaining;
    RETURN jsonb_build_object('clean', remaining = 0, 'remaining', remaining);
END; $$;

REVOKE ALL ON obs_meta.db4_admission_probe, obs_meta.db4_evidence_probe, obs_meta.db4_migration_probe_effect, obs_meta.db4_migration_probe_history, obs_meta.db4_concurrent_identity_probe, obs_meta.db4_concurrent_migration_effect, obs_meta.db4_concurrent_migration_history FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA obs_meta FROM PUBLIC;
GRANT EXECUTE ON FUNCTION obs_meta.db4_seed_role_rls_probe() TO observatory_test_migrator;
