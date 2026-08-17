"""PF-04: provider recipe registration and Observation foundation."""

from __future__ import annotations

import copy
import hashlib
from typing import Any

import pytest
from psycopg.errors import CheckViolation, UniqueViolation

from observatory.capture import PUBLISHED_AR_INPUTS, capture_admitted_results
from observatory.capture_event import DocumentError, canonical_json
from observatory.derive import DEFAULT_VERSION, derive_admitted_results
from observatory.evidence_store import create_store
from observatory.migrate import apply_migrations, apply_schema, connect
from observatory.provider_recipe import (
    TEST_RECIPE,
    TEST_RECIPE_ID,
    DerivationDiagnostic,
    ObservationEnvelope,
    ProviderRecipeError,
    observation_identity,
    recipe_bytes,
    recipe_derivation_version_id,
    register_provider_recipe,
    validate_recipe,
    write_derivation_diagnostic,
    write_derived_row,
    write_observation_envelope,
)

# Published PF-04 test recipe. Digest is hashlib of this literal, not the constructor.
TEST_RECIPE_JCS = (
    b'{"adapter_contract":"test-provider-recipe-foundation-v1","admission":{"c'
    b'apture_outcomes":["no_response","observation_admitted","provider_envelop'
    b'e_rejected","provider_error","reconciliation_failed","response_partial",'
    b'"transport_complete_non_admissible"],"rule":"recipe_closed_classificatio'
    b'ns"},"data_period":{"inheritance":"never_from_capture","rule":"provider_'
    b'stated_or_unstated"},"extension_policy":{"closed_objects":["/envelope"],'
    b'"extension_permitted_objects":["/items"],"unknown_closed_field":"fail_cl'
    b'osed","unknown_extension_field":"diagnostic"},"field_state":{"states":["'
    b'absent","inapplicable","json_null","not_requested","stated"]},"numeric":'
    b'{"normalization":"exact_decimal"},"observation_identity":{"document_sche'
    b'ma":"observatory.observation-identity","document_version":1,"kinds":[{"a'
    b'xes":{"requested_keyword":"string"},"observation_kind":"test.provider.co'
    b'verage.v1"}]},"observation_kinds":["test.provider.coverage.v1"],"parser_'
    b'contract":"test-parser-v1","provider":"test-provider","provider_update_t'
    b'ime":{"inheritance":"never_from_capture_or_sibling","rule":"structure_st'
    b'ated_or_unstated"},"reconciliation":{"rule":"exact_requested_subject"},"'
    b'schema":"observatory.derivation-recipe","version":1}'
)
TEST_RECIPE_SHA256 = "b234ea5315eaf7499a20dc0c612332576fd9af4a748b0ca380b2bae60897eb13"

IDENTITY_JCS = (
    b'{"axes":{"requested_keyword":"alpha"},"observation_kind":"test.provider.cove'
    b'rage.v1","schema":"observatory.observation-identity","version":1}'
)
IDENTITY_SHA256 = "884fef9385834e5923658eb07ba986e85b3d61cb27c88e068b3cd406f2218100"

IDENTITY_DOCUMENT: dict[str, object] = {
    "axes": {"requested_keyword": "alpha"},
    "observation_kind": "test.provider.coverage.v1",
    "schema": "observatory.observation-identity",
    "version": 1,
}

HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64


def _tables(connection: Any) -> set[str]:
    rows = connection.execute(
        """
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'public'
        """
    ).fetchall()
    return {str(row[0]) for row in rows}


def test_published_test_recipe_jcs_sha256_equals_derivation_version_id() -> None:
    assert not TEST_RECIPE_JCS.endswith(b"\n")
    assert len(TEST_RECIPE_JCS) == 1204
    independent = hashlib.sha256(TEST_RECIPE_JCS).hexdigest()
    assert independent == TEST_RECIPE_SHA256
    assert TEST_RECIPE_ID == TEST_RECIPE_SHA256
    assert recipe_bytes(TEST_RECIPE) == TEST_RECIPE_JCS
    assert recipe_derivation_version_id(TEST_RECIPE) == TEST_RECIPE_SHA256
    assert canonical_json(validate_recipe(TEST_RECIPE)) == TEST_RECIPE_JCS


def test_recipe_schema_rejects_unknown_and_missing_members() -> None:
    extra = copy.deepcopy(TEST_RECIPE)
    extra["unexpected"] = "no"
    with pytest.raises(DocumentError, match="unknown"):
        validate_recipe(extra)

    missing = copy.deepcopy(TEST_RECIPE)
    del missing["provider"]
    with pytest.raises(DocumentError, match="missing"):
        validate_recipe(missing)

    kinds = copy.deepcopy(TEST_RECIPE)
    kinds["observation_kinds"] = []
    with pytest.raises(DocumentError, match="observation_kinds"):
        validate_recipe(kinds)

    kinds["observation_kinds"] = ["test.provider.coverage.v1", "test.provider.coverage.v1"]
    with pytest.raises(DocumentError, match="observation_kinds"):
        validate_recipe(kinds)


def test_recipe_schema_rejects_float_and_non_v1_identity() -> None:
    floated = copy.deepcopy(TEST_RECIPE)
    floated["version"] = 1.0
    with pytest.raises(DocumentError):
        validate_recipe(floated)

    wrong_schema = copy.deepcopy(TEST_RECIPE)
    wrong_schema["schema"] = "observatory.attempt-event"
    with pytest.raises(DocumentError, match="schema"):
        validate_recipe(wrong_schema)


def test_observation_identity_is_sha256_of_canonical_semantic_document() -> None:
    assert not IDENTITY_JCS.endswith(b"\n")
    assert hashlib.sha256(IDENTITY_JCS).hexdigest() == IDENTITY_SHA256
    assert observation_identity(IDENTITY_DOCUMENT, TEST_RECIPE) == IDENTITY_SHA256
    assert observation_identity(IDENTITY_DOCUMENT, TEST_RECIPE) != "result:1"

    other = copy.deepcopy(IDENTITY_DOCUMENT)
    other["axes"] = {"requested_keyword": "beta"}
    assert observation_identity(other, TEST_RECIPE) != IDENTITY_SHA256
    assert len(observation_identity(other, TEST_RECIPE)) == 64

    extra_axis = copy.deepcopy(IDENTITY_DOCUMENT)
    extra_axis["axes"] = {"requested_keyword": "alpha", "rank": 1}
    with pytest.raises(DocumentError, match="kind identity definition"):
        observation_identity(extra_axis, TEST_RECIPE)


def _multi_kind_recipe() -> dict[str, object]:
    recipe = copy.deepcopy(TEST_RECIPE)
    recipe["observation_kinds"] = [
        "test.provider.coverage.v1",
        "test.provider.monthly_search_volume.v1",
    ]
    recipe["observation_identity"] = {
        "document_schema": "observatory.observation-identity",
        "document_version": 1,
        "kinds": [
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.coverage.v1",
            },
            {
                "axes": {
                    "month": "integer",
                    "requested_keyword": "string",
                    "year": "integer",
                },
                "observation_kind": "test.provider.monthly_search_volume.v1",
            },
        ],
    }
    return recipe


def test_recipe_identity_kinds_must_match_declared_kinds() -> None:
    missing = _multi_kind_recipe()
    missing["observation_identity"] = {
        "document_schema": "observatory.observation-identity",
        "document_version": 1,
        "kinds": [
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.coverage.v1",
            }
        ],
    }
    with pytest.raises(DocumentError, match="observation_kinds"):
        validate_recipe(missing)

    extra = copy.deepcopy(TEST_RECIPE)
    extra["observation_identity"] = {
        "document_schema": "observatory.observation-identity",
        "document_version": 1,
        "kinds": [
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.coverage.v1",
            },
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.undeclared.v1",
            },
        ],
    }
    with pytest.raises(DocumentError, match="observation_kinds"):
        validate_recipe(extra)

    duplicate = copy.deepcopy(TEST_RECIPE)
    duplicate["observation_identity"] = {
        "document_schema": "observatory.observation-identity",
        "document_version": 1,
        "kinds": [
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.coverage.v1",
            },
            {
                "axes": {"requested_keyword": "string", "year": "integer"},
                "observation_kind": "test.provider.coverage.v1",
            },
        ],
    }
    with pytest.raises(DocumentError, match="duplicate"):
        validate_recipe(duplicate)

    bad_type = copy.deepcopy(TEST_RECIPE)
    identity = copy.deepcopy(TEST_RECIPE["observation_identity"])
    assert isinstance(identity, dict)
    kinds = copy.deepcopy(identity["kinds"])
    assert isinstance(kinds, list)
    first = copy.deepcopy(kinds[0])
    assert isinstance(first, dict)
    first["axes"] = {"requested_keyword": "decimal"}
    identity["kinds"] = [first]
    bad_type["observation_identity"] = identity
    with pytest.raises(DocumentError, match="string or integer"):
        validate_recipe(bad_type)


def test_multi_kind_recipe_identity_is_kind_specific() -> None:
    recipe = _multi_kind_recipe()
    validate_recipe(recipe)
    coverage = {
        "axes": {"requested_keyword": "alpha"},
        "observation_kind": "test.provider.coverage.v1",
        "schema": "observatory.observation-identity",
        "version": 1,
    }
    monthly = {
        "axes": {"month": 8, "requested_keyword": "alpha", "year": 2024},
        "observation_kind": "test.provider.monthly_search_volume.v1",
        "schema": "observatory.observation-identity",
        "version": 1,
    }
    monthly_jcs = (
        b'{"axes":{"month":8,"requested_keyword":"alpha","year":2024},"observat'
        b'ion_kind":"test.provider.monthly_search_volume.v1","schema":"observato'
        b'ry.observation-identity","version":1}'
    )
    other_month = copy.deepcopy(monthly)
    other_month["axes"] = {"month": 9, "requested_keyword": "alpha", "year": 2024}

    assert observation_identity(coverage, recipe) == IDENTITY_SHA256
    assert hashlib.sha256(monthly_jcs).hexdigest() == observation_identity(monthly, recipe)
    assert observation_identity(monthly, recipe) != observation_identity(other_month, recipe)

    with pytest.raises(DocumentError, match="kind identity definition"):
        observation_identity(
            {
                "axes": {
                    "month": 8,
                    "requested_keyword": "alpha",
                    "year": 2024,
                },
                "observation_kind": "test.provider.coverage.v1",
                "schema": "observatory.observation-identity",
                "version": 1,
            },
            recipe,
        )
    missing_period = copy.deepcopy(monthly)
    missing_period["axes"] = {"requested_keyword": "alpha"}
    with pytest.raises(DocumentError, match="kind identity definition"):
        observation_identity(missing_period, recipe)
    extra = copy.deepcopy(monthly)
    extra["axes"] = {
        "month": 8,
        "requested_keyword": "alpha",
        "source": "provider",
        "year": 2024,
    }
    with pytest.raises(DocumentError, match="kind identity definition"):
        observation_identity(extra, recipe)
    wrong_type = copy.deepcopy(monthly)
    wrong_type["axes"] = {"month": "8", "requested_keyword": "alpha", "year": 2024}
    with pytest.raises(DocumentError, match="JSON integer"):
        observation_identity(wrong_type, recipe)
    undeclared = copy.deepcopy(coverage)
    undeclared["observation_kind"] = "test.provider.undeclared.v1"
    with pytest.raises(DocumentError, match="not declared"):
        observation_identity(undeclared, recipe)


def test_empty_schema_creates_provider_substrate_without_fixture_meaning(
    postgres_dsn: str,
) -> None:
    apply_migrations(postgres_dsn)
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        names = _tables(connection)
        fixture_columns = connection.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'observations'
            ORDER BY ordinal_position
            """
        ).fetchall()
        recipe_pk = connection.execute(
            """
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'provider_recipes'::regclass AND contype = 'p'
            """
        ).fetchone()
        envelope_pk = connection.execute(
            """
            SELECT pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'observation_envelopes'::regclass AND contype = 'p'
            """
        ).fetchone()
        diagnostic_unique = connection.execute(
            """
            SELECT conname, pg_get_constraintdef(oid)
            FROM pg_constraint
            WHERE conrelid = 'derivation_diagnostics'::regclass
              AND conname = 'derivation_diagnostics_identity'
            """
        ).fetchone()
    assert {
        "derivation_versions",
        "outcomes",
        "observations",
        "provider_recipes",
        "observation_envelopes",
        "derivation_diagnostics",
    }.issubset(names)
    assert [row[0] for row in fixture_columns] == [
        "capture_id",
        "derivation_version_id",
        "within_capture_result_id",
        "attempt_id",
        "provider",
        "panel_id",
        "subject_key",
        "result_index",
        "label",
        "score",
    ]
    assert recipe_pk is not None and "derivation_version_id" in str(recipe_pk[0])
    assert envelope_pk is not None
    assert "capture_id" in str(envelope_pk[0])
    assert "derivation_version_id" in str(envelope_pk[0])
    assert "within_capture_identity" in str(envelope_pk[0])
    assert diagnostic_unique is not None
    assert "UNIQUE NULLS NOT DISTINCT" in str(diagnostic_unique[1])


def test_register_test_recipe_stores_and_recovers_exact_canonical_bytes(
    postgres_dsn: str,
) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        first = register_provider_recipe(connection, TEST_RECIPE)
        again = register_provider_recipe(connection, TEST_RECIPE)
        row = connection.execute(
            """
            SELECT derivation_version_id, provider, adapter_contract,
                   recipe_canonical_bytes
            FROM provider_recipes
            WHERE derivation_version_id = %s
            """,
            (TEST_RECIPE_SHA256,),
        ).fetchone()
        version = connection.execute(
            """
            SELECT adapter_contract FROM derivation_versions
            WHERE derivation_version_id = %s
            """,
            (TEST_RECIPE_SHA256,),
        ).fetchone()
    assert first.derivation_version_id == TEST_RECIPE_SHA256
    assert first.recipe_canonical_bytes == TEST_RECIPE_JCS
    assert again == first
    assert row is not None
    assert row[0] == TEST_RECIPE_SHA256
    assert row[1] == "test-provider"
    assert row[2] == "test-provider-recipe-foundation-v1"
    assert bytes(row[3]) == TEST_RECIPE_JCS
    assert version == ("test-provider-recipe-foundation-v1",)


def test_conflicting_recipe_bytes_or_adapter_metadata_fail_before_write(
    postgres_dsn: str,
) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO derivation_versions (
                derivation_version_id, adapter_contract, registered_at
            )
            VALUES (%s, 'fixture-panel-v1', now())
            """,
            (TEST_RECIPE_SHA256,),
        )
        with pytest.raises(ProviderRecipeError, match="without recipe"):
            register_provider_recipe(connection, TEST_RECIPE)
        connection.execute(
            "DELETE FROM derivation_versions WHERE derivation_version_id = %s",
            (TEST_RECIPE_SHA256,),
        )
        register_provider_recipe(connection, TEST_RECIPE)
        with pytest.raises(ProviderRecipeError, match="canonical bytes"), connection.transaction():
            connection.execute(
                """
                UPDATE provider_recipes
                SET recipe_canonical_bytes = %s
                WHERE derivation_version_id = %s
                """,
                (TEST_RECIPE_JCS + b" ", TEST_RECIPE_SHA256),
            )
            register_provider_recipe(connection, TEST_RECIPE)

        with pytest.raises(ProviderRecipeError, match="adapter"), connection.transaction():
            connection.execute(
                """
                UPDATE provider_recipes
                SET provider = 'other-provider'
                WHERE derivation_version_id = %s
                """,
                (TEST_RECIPE_SHA256,),
            )
            register_provider_recipe(connection, TEST_RECIPE)


def test_fixture_version_registers_without_recipe_bytes(
    postgres_dsn: str, tmp_path: Any
) -> None:
    apply_migrations(postgres_dsn)
    store = create_store(tmp_path / "evidence")
    capture_admitted_results(store, PUBLISHED_AR_INPUTS)
    with connect(postgres_dsn) as connection:
        derive_admitted_results(store, connection, DEFAULT_VERSION)
        fixture_row = connection.execute(
            """
            SELECT adapter_contract FROM derivation_versions
            WHERE derivation_version_id = %s
            """,
            (DEFAULT_VERSION,),
        ).fetchone()
        recipe_count = connection.execute(
            "SELECT count(*) FROM provider_recipes"
        ).fetchone()
        observation_shape = connection.execute(
            """
            SELECT within_capture_result_id FROM observations
            ORDER BY within_capture_result_id
            """
        ).fetchall()
    assert fixture_row == ("fixture-panel-v1",)
    assert recipe_count == (0,)
    assert [row[0] for row in observation_shape] == ["result:1", "result:2"]


def test_envelope_and_diagnostic_identity_constraints(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    identity = observation_identity(IDENTITY_DOCUMENT, TEST_RECIPE)
    envelope = ObservationEnvelope(
        capture_id=HEX_A,
        attempt_id=HEX_B,
        derivation_version_id=TEST_RECIPE_SHA256,
        provider="test-provider",
        adapter_contract="test-provider-recipe-foundation-v1",
        observation_kind="test.provider.coverage.v1",
        within_capture_identity=identity,
    )
    diagnostic = DerivationDiagnostic(
        derivation_version_id=TEST_RECIPE_SHA256,
        attempt_id=HEX_B,
        capture_id=HEX_A,
        diagnostic_code="unknown_extension_field",
        provider_body_path="/items/extra",
    )
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        write_observation_envelope(connection, envelope)
        write_derivation_diagnostic(connection, diagnostic)
        with pytest.raises(UniqueViolation), connection.transaction():
            connection.execute(
                """
                INSERT INTO observation_envelopes (
                    capture_id, attempt_id, derivation_version_id, provider,
                    adapter_contract, observation_kind, within_capture_identity
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    envelope.capture_id,
                    envelope.attempt_id,
                    envelope.derivation_version_id,
                    envelope.provider,
                    envelope.adapter_contract,
                    envelope.observation_kind,
                    envelope.within_capture_identity,
                ),
            )
        with pytest.raises(CheckViolation), connection.transaction():
            connection.execute(
                """
                INSERT INTO observation_envelopes (
                    capture_id, attempt_id, derivation_version_id, provider,
                    adapter_contract, observation_kind, within_capture_identity
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    envelope.capture_id,
                    envelope.attempt_id,
                    envelope.derivation_version_id,
                    envelope.provider,
                    envelope.adapter_contract,
                    envelope.observation_kind,
                    "result:1",
                ),
            )
        with pytest.raises(UniqueViolation), connection.transaction():
            connection.execute(
                """
                INSERT INTO derivation_diagnostics (
                    derivation_version_id, attempt_id, capture_id,
                    diagnostic_code, provider_body_path
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    diagnostic.derivation_version_id,
                    diagnostic.attempt_id,
                    diagnostic.capture_id,
                    diagnostic.diagnostic_code,
                    diagnostic.provider_body_path,
                ),
            )


def test_exact_content_comparison_reuses_identical_and_refuses_conflict(
    postgres_dsn: str,
) -> None:
    apply_migrations(postgres_dsn)
    identity = observation_identity(IDENTITY_DOCUMENT, TEST_RECIPE)
    envelope = ObservationEnvelope(
        capture_id=HEX_A,
        attempt_id=HEX_B,
        derivation_version_id=TEST_RECIPE_SHA256,
        provider="test-provider",
        adapter_contract="test-provider-recipe-foundation-v1",
        observation_kind="test.provider.coverage.v1",
        within_capture_identity=identity,
    )
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, TEST_RECIPE)
        write_observation_envelope(connection, envelope)
        write_observation_envelope(connection, envelope)
        count = connection.execute(
            "SELECT count(*) FROM observation_envelopes"
        ).fetchone()
        assert count == (1,)
        conflicting = ObservationEnvelope(
            capture_id=HEX_A,
            attempt_id=HEX_C,
            derivation_version_id=TEST_RECIPE_SHA256,
            provider="test-provider",
            adapter_contract="test-provider-recipe-foundation-v1",
            observation_kind="test.provider.coverage.v1",
            within_capture_identity=identity,
        )
        with pytest.raises(ProviderRecipeError, match="conflicting"):
            write_observation_envelope(connection, conflicting)
        helper_identity = {
            "capture_id": HEX_A,
            "derivation_version_id": TEST_RECIPE_SHA256,
            "within_capture_identity": identity,
        }
        write_derived_row(
            connection,
            table="observation_envelopes",
            identity=helper_identity,
            content={
                "attempt_id": HEX_B,
                "provider": "test-provider",
                "adapter_contract": "test-provider-recipe-foundation-v1",
                "observation_kind": "test.provider.coverage.v1",
            },
        )
        with pytest.raises(ProviderRecipeError, match="conflicting"):
            write_derived_row(
                connection,
                table="observation_envelopes",
                identity=helper_identity,
                content={
                    "attempt_id": HEX_B,
                    "provider": "other-provider",
                    "adapter_contract": "test-provider-recipe-foundation-v1",
                    "observation_kind": "test.provider.coverage.v1",
                },
            )
        wrong_kind = ObservationEnvelope(
            capture_id=HEX_C,
            attempt_id=HEX_B,
            derivation_version_id=TEST_RECIPE_SHA256,
            provider="test-provider",
            adapter_contract="test-provider-recipe-foundation-v1",
            observation_kind="test.provider.undeclared.v1",
            within_capture_identity=identity,
        )
        with pytest.raises(ProviderRecipeError, match="observation_kind"):
            write_observation_envelope(connection, wrong_kind)
        wrong_provider = ObservationEnvelope(
            capture_id=HEX_C,
            attempt_id=HEX_B,
            derivation_version_id=TEST_RECIPE_SHA256,
            provider="other-provider",
            adapter_contract="test-provider-recipe-foundation-v1",
            observation_kind="test.provider.coverage.v1",
            within_capture_identity=identity,
        )
        with pytest.raises(ProviderRecipeError, match="adapter metadata"):
            write_observation_envelope(connection, wrong_provider)


def test_prior_integer_schema_upgrade_still_preserves_fixture_rows(
    postgres_dsn: str,
) -> None:
    version = "v-pf04-upgrade"
    with connect(postgres_dsn) as connection:
        connection.execute(
            """
            CREATE TABLE derivation_versions (
                derivation_version_id TEXT PRIMARY KEY,
                adapter_contract TEXT NOT NULL,
                registered_at TIMESTAMPTZ NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE outcomes (
                attempt_id TEXT NOT NULL,
                capture_id TEXT,
                derivation_version_id TEXT NOT NULL
                    REFERENCES derivation_versions (derivation_version_id),
                classification TEXT NOT NULL,
                observation_count INTEGER NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE observations (
                capture_id TEXT NOT NULL,
                derivation_version_id TEXT NOT NULL
                    REFERENCES derivation_versions (derivation_version_id),
                within_capture_result_id TEXT NOT NULL,
                attempt_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                panel_id TEXT NOT NULL,
                subject_key TEXT NOT NULL,
                result_index INTEGER NOT NULL,
                label TEXT NOT NULL,
                score INTEGER NOT NULL,
                PRIMARY KEY (capture_id, derivation_version_id, within_capture_result_id)
            )
            """
        )
        connection.execute(
            """
            INSERT INTO derivation_versions (
                derivation_version_id, adapter_contract, registered_at
            )
            VALUES (%s, 'fixture-panel-v1', TIMESTAMPTZ '2026-08-14T00:00:00Z')
            """,
            (version,),
        )
        connection.execute(
            """
            INSERT INTO observations (
                capture_id, derivation_version_id, within_capture_result_id,
                attempt_id, provider, panel_id, subject_key,
                result_index, label, score
            )
            VALUES (
                %s, %s, 'result:3', %s, 'fixture', 'panel-alpha', 'subject-one',
                3, 'kept', -42
            )
            """,
            (HEX_B, version, HEX_A),
        )
        before = connection.execute(
            """
            SELECT within_capture_result_id, score FROM observations
            """
        ).fetchall()
        connection.commit()

    with connect(postgres_dsn) as connection:
        apply_schema(connection)
        after = connection.execute(
            """
            SELECT within_capture_result_id, score FROM observations
            """
        ).fetchall()
        names = _tables(connection)
    assert after == before == [("result:3", -42)]
    assert "provider_recipes" in names
    assert "observation_envelopes" in names
    assert "derivation_diagnostics" in names
