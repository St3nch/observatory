"""Apply the rebuildable PostgreSQL schema for Outcomes and Observations."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Final

import psycopg
from psycopg import Connection

from observatory.settings import get_settings

DERIVATION_VERSIONS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS derivation_versions (
    derivation_version_id TEXT PRIMARY KEY
        CHECK (derivation_version_id ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL
)
"""

OUTCOMES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS outcomes (
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    capture_id TEXT
        CHECK (capture_id IS NULL OR capture_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES derivation_versions (derivation_version_id),
    classification TEXT NOT NULL,
    observation_count BIGINT NOT NULL
        CHECK (observation_count >= 0 AND observation_count <= 9007199254740991),
    CONSTRAINT outcomes_identity
        UNIQUE NULLS NOT DISTINCT (derivation_version_id, attempt_id, capture_id)
)
"""

OBSERVATIONS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS observations (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES derivation_versions (derivation_version_id),
    within_capture_result_id TEXT NOT NULL
        CHECK (within_capture_result_id ~ '^result:[1-9][0-9]*$'),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    provider TEXT NOT NULL,
    panel_id TEXT NOT NULL,
    subject_key TEXT NOT NULL,
    result_index BIGINT NOT NULL
        CHECK (result_index >= 1 AND result_index <= 9007199254740991),
    label TEXT NOT NULL,
    score BIGINT NOT NULL
        CHECK (score >= -9007199254740991 AND score <= 9007199254740991),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_result_id)
)
"""

PROVIDER_RECIPES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS provider_recipes (
    derivation_version_id TEXT PRIMARY KEY
        CHECK (derivation_version_id ~ '^[0-9a-f]{64}$')
        REFERENCES derivation_versions (derivation_version_id),
    provider TEXT NOT NULL
        CHECK (provider ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL
        CHECK (adapter_contract ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    recipe_canonical_bytes BYTEA NOT NULL
        CHECK (octet_length(recipe_canonical_bytes) >= 1)
)
"""

OBSERVATION_ENVELOPES_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS observation_envelopes (
    capture_id TEXT NOT NULL
        CHECK (capture_id ~ '^[0-9a-f]{64}$'),
    attempt_id TEXT NOT NULL
        CHECK (attempt_id ~ '^[0-9a-f]{64}$'),
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    provider TEXT NOT NULL
        CHECK (provider ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    adapter_contract TEXT NOT NULL
        CHECK (adapter_contract ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    observation_kind TEXT NOT NULL
        CHECK (observation_kind ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    within_capture_identity TEXT NOT NULL
        CHECK (within_capture_identity ~ '^[0-9a-f]{64}$'),
    PRIMARY KEY (capture_id, derivation_version_id, within_capture_identity)
)
"""

DERIVATION_DIAGNOSTICS_SQL: Final[str] = """
CREATE TABLE IF NOT EXISTS derivation_diagnostics (
    derivation_version_id TEXT NOT NULL
        REFERENCES provider_recipes (derivation_version_id),
    attempt_id TEXT
        CHECK (attempt_id IS NULL OR attempt_id ~ '^[0-9a-f]{64}$'),
    capture_id TEXT
        CHECK (capture_id IS NULL OR capture_id ~ '^[0-9a-f]{64}$'),
    diagnostic_code TEXT NOT NULL
        CHECK (diagnostic_code ~ '^[A-Za-z0-9._+:-]{1,128}$'),
    provider_body_path TEXT NOT NULL
        CHECK (provider_body_path ~ '^(|(/([^/~]|~[01])*)+)$'),
    CONSTRAINT derivation_diagnostics_identity
        UNIQUE NULLS NOT DISTINCT (
            derivation_version_id, attempt_id, capture_id,
            diagnostic_code, provider_body_path
        ),
    CONSTRAINT derivation_diagnostics_event
        CHECK (attempt_id IS NOT NULL OR capture_id IS NOT NULL)
)
"""

SCHEMA_STATEMENTS: Final[tuple[str, ...]] = (
    DERIVATION_VERSIONS_SQL,
    OUTCOMES_SQL,
    OBSERVATIONS_SQL,
    PROVIDER_RECIPES_SQL,
    OBSERVATION_ENVELOPES_SQL,
    DERIVATION_DIAGNOSTICS_SQL,
)

WIDEN_IJSON_COLUMNS_SQL: Final[tuple[str, ...]] = (
    "ALTER TABLE outcomes ALTER COLUMN observation_count TYPE BIGINT",
    "ALTER TABLE observations ALTER COLUMN result_index TYPE BIGINT",
    "ALTER TABLE observations ALTER COLUMN score TYPE BIGINT",
)


def resolve_database_url(explicit: str | None) -> str:
    if explicit:
        return explicit
    configured = get_settings().database_url
    if configured:
        return configured
    raise ValueError("database URL is required (--database-url or OBSERVATORY_DATABASE_URL)")


def connect(dsn: str) -> Connection[Any]:
    return psycopg.connect(dsn)


def apply_schema(connection: Connection[Any]) -> None:
    """Create rebuildable tables if missing; widen leftover INTEGER I-JSON columns."""

    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    for statement in WIDEN_IJSON_COLUMNS_SQL:
        connection.execute(statement)
    connection.commit()


def apply_migrations(dsn: str) -> None:
    with connect(dsn) as connection:
        apply_schema(connection)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.migrate",
        description="Create rebuildable PostgreSQL tables for derivation.",
    )
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    apply_migrations(dsn)
    sys.stdout.write(
        "migrated derivation_versions outcomes observations "
        "provider_recipes observation_envelopes derivation_diagnostics\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
