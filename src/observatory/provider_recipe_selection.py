"""Adapter-specific current provider recipe selection.

Selection is mutable operational state. It is not Evidence and is not a Derivation.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from typing import Any, Final, Literal

from psycopg import Connection
from psycopg.errors import ForeignKeyViolation

from observatory.migrate import apply_schema, connect, resolve_database_url

ADAPTER_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._+:-]{1,128}$")
RECIPE_ID_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
NOT_SELECTED_SIGNAL: Final[str] = "provider_recipe_not_selected"


class ProviderRecipeSelectionError(Exception):
    """Provider recipe selection or resolution refused."""


class InvalidProviderRecipeId(ProviderRecipeSelectionError):
    """The supplied derivation_version_id is not a provider recipe digest."""


class UnknownProviderRecipe(ProviderRecipeSelectionError):
    """No registered provider recipe has this derivation_version_id."""


class WrongAdapterRecipe(ProviderRecipeSelectionError):
    """The recipe is registered, but not for the requested adapter."""


class ProviderRecipeNotSelected(ProviderRecipeSelectionError):
    """The adapter has no current operational recipe selection."""


@dataclass(frozen=True)
class ResolvedProviderRecipe:
    derivation_version_id: str
    provider: str
    adapter_contract: str
    resolution: Literal["selected", "pinned"]


def _require_adapter(adapter_contract: str) -> str:
    if ADAPTER_RE.fullmatch(adapter_contract) is None:
        raise ProviderRecipeSelectionError(
            "adapter_contract must match [A-Za-z0-9._+:-]{1,128}"
        )
    return adapter_contract


def _require_recipe_id(derivation_version_id: str) -> str:
    if RECIPE_ID_RE.fullmatch(derivation_version_id) is None:
        raise InvalidProviderRecipeId(
            "derivation_version_id must be a 64-character lowercase SHA-256"
        )
    return derivation_version_id


def _load_registered(
    connection: Connection[Any], derivation_version_id: str
) -> tuple[str, str] | None:
    row = connection.execute(
        """
        SELECT provider, adapter_contract
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (derivation_version_id,),
    ).fetchone()
    if row is None:
        return None
    return str(row[0]), str(row[1])


def select_provider_recipe(
    connection: Connection[Any],
    adapter_contract: str,
    derivation_version_id: str,
) -> ResolvedProviderRecipe:
    """Atomically set the current recipe for one exact adapter contract."""

    adapter = _require_adapter(adapter_contract)
    recipe_id = _require_recipe_id(derivation_version_id)
    registered = _load_registered(connection, recipe_id)
    if registered is None:
        raise UnknownProviderRecipe(
            f"provider recipe {recipe_id} is not registered"
        )
    provider, recipe_adapter = registered
    if recipe_adapter != adapter:
        raise WrongAdapterRecipe(
            f"provider recipe {recipe_id} is registered for {recipe_adapter}"
        )
    try:
        connection.execute(
            """
            INSERT INTO provider_recipe_selections (
                adapter_contract, derivation_version_id
            )
            VALUES (%s, %s)
            ON CONFLICT (adapter_contract) DO UPDATE
            SET derivation_version_id = EXCLUDED.derivation_version_id
            """,
            (adapter, recipe_id),
        )
    except ForeignKeyViolation as exc:
        raise WrongAdapterRecipe(
            f"provider recipe {recipe_id} is not registered for {adapter}"
        ) from exc
    return ResolvedProviderRecipe(
        derivation_version_id=recipe_id,
        provider=provider,
        adapter_contract=adapter,
        resolution="selected",
    )


def resolve_provider_recipe(
    connection: Connection[Any],
    adapter_contract: str,
    pinned_version: str | None = None,
) -> ResolvedProviderRecipe:
    """Return the pinned recipe or the adapter's current selection."""

    adapter = _require_adapter(adapter_contract)
    if pinned_version is not None:
        recipe_id = _require_recipe_id(pinned_version)
        registered = _load_registered(connection, recipe_id)
        if registered is None:
            raise UnknownProviderRecipe(
                f"provider recipe {recipe_id} is not registered"
            )
        provider, recipe_adapter = registered
        if recipe_adapter != adapter:
            raise WrongAdapterRecipe(
                f"provider recipe {recipe_id} is registered for {recipe_adapter}"
            )
        return ResolvedProviderRecipe(
            derivation_version_id=recipe_id,
            provider=provider,
            adapter_contract=adapter,
            resolution="pinned",
        )
    selected = connection.execute(
        """
        SELECT derivation_version_id
        FROM provider_recipe_selections
        WHERE adapter_contract = %s
        """,
        (adapter,),
    ).fetchone()
    if selected is None:
        raise ProviderRecipeNotSelected(NOT_SELECTED_SIGNAL)
    recipe_id = str(selected[0])
    registered = _load_registered(connection, recipe_id)
    if registered is None:
        raise ProviderRecipeNotSelected(NOT_SELECTED_SIGNAL)
    provider, recipe_adapter = registered
    if recipe_adapter != adapter:
        raise ProviderRecipeNotSelected(NOT_SELECTED_SIGNAL)
    return ResolvedProviderRecipe(
        derivation_version_id=recipe_id,
        provider=provider,
        adapter_contract=adapter,
        resolution="selected",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="observatory.provider_recipe_selection",
        description="Set the current provider recipe for one adapter contract.",
    )
    parser.add_argument("--adapter-contract", required=True)
    parser.add_argument("--derivation-version-id", required=True)
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args(argv)
    try:
        dsn = resolve_database_url(args.database_url)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 2
    try:
        with connect(dsn) as connection:
            apply_schema(connection)
            resolved = select_provider_recipe(
                connection,
                args.adapter_contract,
                args.derivation_version_id,
            )
    except ProviderRecipeSelectionError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    sys.stdout.write(f"adapter_contract {resolved.adapter_contract}\n")
    sys.stdout.write(f"derivation_version {resolved.derivation_version_id}\n")
    sys.stdout.write("resolution selected\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
