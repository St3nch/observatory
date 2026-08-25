"""PF-08: adapter-specific current provider recipe selection."""

from __future__ import annotations

from pathlib import Path

import pytest
from psycopg.errors import ForeignKeyViolation

from observatory.capture_event import (
    PAID_ADAPTER_CONTRACT,
    TARGET_METRICS_ADAPTER_CONTRACT,
    body_ref,
    paid_http_attempt_document,
    paid_http_capture_document,
    target_metrics_http_attempt_document,
    target_metrics_http_capture_document,
)
from observatory.dataforseo_ai_optimization_target_metrics_paid_probe import (
    closed_target_metrics_parameters,
    target_metrics_request_body_bytes,
)
from observatory.dataforseo_keyword_overview import (
    CORE_RECIPE,
    CORE_RECIPE_ID,
    EXTENDED_RECIPE,
    EXTENDED_RECIPE_ID,
)
from observatory.dataforseo_paid_probe import closed_paid_parameters, paid_request_body_bytes
from observatory.evidence_store import create_store
from observatory.keyword_overview_derive import (
    derive_keyword_overview,
    derive_keyword_overview_extended,
)
from observatory.migrate import (
    DERIVATION_VERSIONS_SQL,
    PROVIDER_RECIPES_SQL,
    apply_migrations,
    connect,
)
from observatory.provider_recipe import TEST_RECIPE, TEST_RECIPE_ID, register_provider_recipe
from observatory.provider_recipe_selection import (
    NOT_SELECTED_SIGNAL,
    InvalidProviderRecipeId,
    ProviderRecipeNotSelected,
    UnknownProviderRecipe,
    WrongAdapterRecipe,
    main,
    resolve_provider_recipe,
    select_provider_recipe,
)
from observatory.target_metrics_derive import (
    TARGET_METRICS_RECIPE,
    TARGET_METRICS_RECIPE_ID,
    derive_target_metrics,
)

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "dataforseo_keyword_overview_pf03.json"
)
KEYWORDS = (
    "seo api",
    "keyword research",
    "local seo",
    "generative engine optimization",
    "ai search optimization",
)


def test_additive_selection_schema_works_on_populated_pf07_tables(postgres_dsn: str) -> None:
    with connect(postgres_dsn) as connection:
        connection.execute(DERIVATION_VERSIONS_SQL)
        connection.execute(PROVIDER_RECIPES_SQL)
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, EXTENDED_RECIPE)
        before = connection.execute(
            """
            SELECT derivation_version_id, adapter_contract
            FROM provider_recipes
            ORDER BY derivation_version_id
            """
        ).fetchall()
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        after = connection.execute(
            """
            SELECT derivation_version_id, adapter_contract
            FROM provider_recipes
            ORDER BY derivation_version_id
            """
        ).fetchall()
        constraint = connection.execute(
            """
            SELECT 1
            FROM pg_constraint
            WHERE conrelid = 'provider_recipes'::regclass
              AND conname = 'provider_recipes_adapter_version'
            """
        ).fetchone()
        apply_migrations(postgres_dsn)
        resolved = select_provider_recipe(
            connection, PAID_ADAPTER_CONTRACT, EXTENDED_RECIPE_ID
        )
    assert after == before
    assert constraint == (1,)
    assert resolved.derivation_version_id == EXTENDED_RECIPE_ID
    assert resolved.adapter_contract == PAID_ADAPTER_CONTRACT


def test_wrong_adapter_selection_is_structurally_refused(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, TEST_RECIPE)
        with pytest.raises(WrongAdapterRecipe):
            select_provider_recipe(
                connection, str(TEST_RECIPE["adapter_contract"]), CORE_RECIPE_ID
            )
        with pytest.raises(ForeignKeyViolation), connection.transaction():
            connection.execute(
                """
                INSERT INTO provider_recipe_selections (
                    adapter_contract, derivation_version_id
                )
                VALUES (%s, %s)
                """,
                (TEST_RECIPE["adapter_contract"], CORE_RECIPE_ID),
            )


def test_select_and_resolve_are_adapter_specific(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    other_adapter = str(TEST_RECIPE["adapter_contract"])
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, EXTENDED_RECIPE)
        register_provider_recipe(connection, TEST_RECIPE)
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, EXTENDED_RECIPE_ID)
        select_provider_recipe(connection, other_adapter, TEST_RECIPE_ID)
        paid = resolve_provider_recipe(connection, PAID_ADAPTER_CONTRACT)
        other = resolve_provider_recipe(connection, other_adapter)
        pinned = resolve_provider_recipe(
            connection, PAID_ADAPTER_CONTRACT, pinned_version=CORE_RECIPE_ID
        )
        select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, CORE_RECIPE_ID)
        after = resolve_provider_recipe(connection, PAID_ADAPTER_CONTRACT)
        still_other = resolve_provider_recipe(connection, other_adapter)
        recipes = connection.execute(
            "SELECT derivation_version_id FROM provider_recipes ORDER BY 1"
        ).fetchall()
    assert paid.derivation_version_id == EXTENDED_RECIPE_ID
    assert paid.resolution == "selected"
    assert other.derivation_version_id == TEST_RECIPE_ID
    assert pinned.derivation_version_id == CORE_RECIPE_ID
    assert pinned.resolution == "pinned"
    assert after.derivation_version_id == CORE_RECIPE_ID
    assert still_other.derivation_version_id == TEST_RECIPE_ID
    assert {row[0] for row in recipes} == {
        CORE_RECIPE_ID,
        EXTENDED_RECIPE_ID,
        TEST_RECIPE_ID,
    }


def test_resolve_fails_closed_without_guessing(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    missing = "ab" * 32
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, TEST_RECIPE)
        with pytest.raises(ProviderRecipeNotSelected) as not_selected:
            resolve_provider_recipe(connection, PAID_ADAPTER_CONTRACT)
        with pytest.raises(UnknownProviderRecipe):
            resolve_provider_recipe(
                connection, PAID_ADAPTER_CONTRACT, pinned_version=missing
            )
        with pytest.raises(WrongAdapterRecipe):
            resolve_provider_recipe(
                connection,
                PAID_ADAPTER_CONTRACT,
                pinned_version=TEST_RECIPE_ID,
            )
        with pytest.raises(InvalidProviderRecipeId):
            resolve_provider_recipe(
                connection,
                PAID_ADAPTER_CONTRACT,
                pinned_version="fixture-panel-v1-derive-v1",
            )
        with pytest.raises(UnknownProviderRecipe):
            select_provider_recipe(connection, PAID_ADAPTER_CONTRACT, missing)
    assert str(not_selected.value) == NOT_SELECTED_SIGNAL


def test_derive_does_not_set_current_selection(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    parameters = closed_paid_parameters(keywords=list(KEYWORDS))
    attempt = paid_http_attempt_document(
        parameters=parameters,
        attempt_nonce="11" * 32,
        authorized_at="2026-08-16T21:37:00.000000Z",
        observatory_version="pf08-test-v1",
    )
    body = FIXTURE.read_bytes()
    store.commit_attempt(attempt, request_body=paid_request_body_bytes(parameters))
    store.commit_capture(
        paid_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-16T21:37:01.100000Z",
            transport_ended_at="2026-08-16T21:37:01.400000Z",
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_nonempty", "body": body_ref(body)},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at="2026-08-16T21:37:01.200000Z",
            response_body_ended_at="2026-08-16T21:37:01.300000Z",
        ),
        response_body=body,
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_keyword_overview(store, connection)
        derive_keyword_overview_extended(store, connection)
        rows = connection.execute("SELECT * FROM provider_recipe_selections").fetchall()
        with pytest.raises(ProviderRecipeNotSelected):
            resolve_provider_recipe(connection, PAID_ADAPTER_CONTRACT)
    assert rows == []


def test_selection_cli_sets_and_replaces(postgres_dsn: str) -> None:
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        register_provider_recipe(connection, CORE_RECIPE)
        register_provider_recipe(connection, EXTENDED_RECIPE)
    first = main(
        [
            "--database-url",
            postgres_dsn,
            "--adapter-contract",
            PAID_ADAPTER_CONTRACT,
            "--derivation-version-id",
            EXTENDED_RECIPE_ID,
        ]
    )
    second = main(
        [
            "--database-url",
            postgres_dsn,
            "--adapter-contract",
            PAID_ADAPTER_CONTRACT,
            "--derivation-version-id",
            CORE_RECIPE_ID,
        ]
    )
    refused = main(
        [
            "--database-url",
            postgres_dsn,
            "--adapter-contract",
            PAID_ADAPTER_CONTRACT,
            "--derivation-version-id",
            "ab" * 32,
        ]
    )
    with connect(postgres_dsn) as connection:
        current = resolve_provider_recipe(connection, PAID_ADAPTER_CONTRACT)
    assert first == 0
    assert second == 0
    assert refused == 1
    assert current.derivation_version_id == CORE_RECIPE_ID


def test_target_metrics_derive_does_not_select_and_selection_resolves(
    tmp_path: Path, postgres_dsn: str
) -> None:
    store = create_store(tmp_path / "evidence")
    fixture = (
        Path(__file__).resolve().parent
        / "fixtures"
        / "dataforseo_ai_optimization_target_metrics_ai09.json"
    )
    body = fixture.read_bytes()
    parameters = closed_target_metrics_parameters(keyword="generative engine optimization")
    attempt = target_metrics_http_attempt_document(
        parameters=parameters,
        attempt_nonce="11" * 32,
        authorized_at="2026-08-24T03:09:00.000000Z",
        observatory_version="ai12-selection-v1",
    )
    store.commit_attempt(attempt, request_body=target_metrics_request_body_bytes(parameters))
    store.commit_capture(
        target_metrics_http_capture_document(
            attempt=attempt,
            request_started_at="2026-08-24T03:09:01.100000Z",
            transport_ended_at="2026-08-24T03:09:01.400000Z",
            transport_state="response_complete",
            response={
                "status": 200,
                "http_version": "HTTP/1.1",
                "header_policy": "http-headers-v1",
                "headers": [["content-type", "application/json"]],
                "omitted_headers": [],
                "body": {"state": "present_nonempty", "body": body_ref(body)},
                "completeness": "complete",
            },
            transport_failure=None,
            response_headers_at="2026-08-24T03:09:01.200000Z",
            response_body_ended_at="2026-08-24T03:09:01.300000Z",
        ),
        response_body=body,
    )
    apply_migrations(postgres_dsn)
    with connect(postgres_dsn) as connection:
        derive_target_metrics(store, connection)
        rows = connection.execute(
            """
            SELECT adapter_contract FROM provider_recipe_selections
            WHERE adapter_contract = %s
            """,
            (TARGET_METRICS_ADAPTER_CONTRACT,),
        ).fetchall()
        with pytest.raises(ProviderRecipeNotSelected):
            resolve_provider_recipe(connection, TARGET_METRICS_ADAPTER_CONTRACT)
        registered = connection.execute(
            """
            SELECT derivation_version_id FROM provider_recipes
            WHERE adapter_contract = %s
            """,
            (TARGET_METRICS_ADAPTER_CONTRACT,),
        ).fetchone()
        register_provider_recipe(connection, CORE_RECIPE)
        select_provider_recipe(
            connection, TARGET_METRICS_ADAPTER_CONTRACT, TARGET_METRICS_RECIPE_ID
        )
        resolved = resolve_provider_recipe(connection, TARGET_METRICS_ADAPTER_CONTRACT)
        pinned = resolve_provider_recipe(
            connection,
            TARGET_METRICS_ADAPTER_CONTRACT,
            pinned_version=TARGET_METRICS_RECIPE_ID,
        )
        with pytest.raises(WrongAdapterRecipe):
            resolve_provider_recipe(
                connection,
                TARGET_METRICS_ADAPTER_CONTRACT,
                pinned_version=CORE_RECIPE_ID,
            )
    assert rows == []
    assert registered == (TARGET_METRICS_RECIPE_ID,)
    assert resolved.derivation_version_id == TARGET_METRICS_RECIPE_ID
    assert resolved.resolution == "selected"
    assert pinned.resolution == "pinned"
    assert TARGET_METRICS_RECIPE["adapter_contract"] == TARGET_METRICS_ADAPTER_CONTRACT
