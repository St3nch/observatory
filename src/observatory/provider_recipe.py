"""Provider Derivation Recipe registration and Observation foundation."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from psycopg import Connection, sql

from observatory.capture_event import DocumentError, canonical_json, content_digest

SCHEMA: Final[str] = "observatory.derivation-recipe"
SCHEMA_VERSION: Final[int] = 1
IDENTITY_SCHEMA: Final[str] = "observatory.observation-identity"
IDENTITY_VERSION: Final[int] = 1
TEST_RECIPE_ID: Final[str] = (
    "b234ea5315eaf7499a20dc0c612332576fd9af4a748b0ca380b2bae60897eb13"
)

_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._+:-]{1,128}$")
_HEX64_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_POINTER_RE: Final[re.Pattern[str]] = re.compile(r"^(|(?:/(?:[^/~]|~[01])*)+)$")
_SAFE_INTEGER_MAX: Final[int] = 9007199254740991
_SAFE_INTEGER_MIN: Final[int] = -9007199254740991
_AXIS_TYPES: Final[frozenset[str]] = frozenset({"integer", "string"})

_RECIPE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "adapter_contract",
        "admission",
        "data_period",
        "extension_policy",
        "field_state",
        "numeric",
        "observation_identity",
        "observation_kinds",
        "parser_contract",
        "provider",
        "provider_update_time",
        "reconciliation",
        "schema",
        "version",
    }
)
_ADMISSION_KEYS: Final[frozenset[str]] = frozenset({"capture_outcomes", "rule"})
_DATA_PERIOD_KEYS: Final[frozenset[str]] = frozenset({"inheritance", "rule"})
_EXTENSION_KEYS: Final[frozenset[str]] = frozenset(
    {
        "closed_objects",
        "extension_permitted_objects",
        "unknown_closed_field",
        "unknown_extension_field",
    }
)
_FIELD_STATE_KEYS: Final[frozenset[str]] = frozenset({"states"})
_NUMERIC_KEYS: Final[frozenset[str]] = frozenset({"normalization"})
_PROVIDER_TIME_KEYS: Final[frozenset[str]] = frozenset({"inheritance", "rule"})
_RECONCILIATION_KEYS: Final[frozenset[str]] = frozenset({"rule"})
_OBSERVATION_IDENTITY_KEYS: Final[frozenset[str]] = frozenset(
    {"document_schema", "document_version", "kinds"}
)
_KIND_IDENTITY_KEYS: Final[frozenset[str]] = frozenset({"axes", "observation_kind"})
_IDENTITY_KEYS: Final[frozenset[str]] = frozenset(
    {"axes", "observation_kind", "schema", "version"}
)

_ENVELOPE_IDENTITY: Final[frozenset[str]] = frozenset(
    {"capture_id", "derivation_version_id", "within_capture_identity"}
)
_ENVELOPE_CONTENT: Final[frozenset[str]] = frozenset(
    {"attempt_id", "provider", "adapter_contract", "observation_kind"}
)
_DIAGNOSTIC_IDENTITY: Final[frozenset[str]] = frozenset(
    {
        "derivation_version_id",
        "attempt_id",
        "capture_id",
        "diagnostic_code",
        "provider_body_path",
    }
)
_TABLE_SPEC: Final[dict[str, tuple[frozenset[str], frozenset[str]]]] = {
    "observation_envelopes": (_ENVELOPE_IDENTITY, _ENVELOPE_CONTENT),
    "derivation_diagnostics": (_DIAGNOSTIC_IDENTITY, frozenset()),
}

TEST_RECIPE: Final[dict[str, object]] = {
    "adapter_contract": "test-provider-recipe-foundation-v1",
    "admission": {
        "capture_outcomes": [
            "no_response",
            "observation_admitted",
            "provider_envelope_rejected",
            "provider_error",
            "reconciliation_failed",
            "response_partial",
            "transport_complete_non_admissible",
        ],
        "rule": "recipe_closed_classifications",
    },
    "data_period": {
        "inheritance": "never_from_capture",
        "rule": "provider_stated_or_unstated",
    },
    "extension_policy": {
        "closed_objects": ["/envelope"],
        "extension_permitted_objects": ["/items"],
        "unknown_closed_field": "fail_closed",
        "unknown_extension_field": "diagnostic",
    },
    "field_state": {
        "states": [
            "absent",
            "inapplicable",
            "json_null",
            "not_requested",
            "stated",
        ]
    },
    "numeric": {"normalization": "exact_decimal"},
    "observation_identity": {
        "document_schema": IDENTITY_SCHEMA,
        "document_version": IDENTITY_VERSION,
        "kinds": [
            {
                "axes": {"requested_keyword": "string"},
                "observation_kind": "test.provider.coverage.v1",
            }
        ],
    },
    "observation_kinds": ["test.provider.coverage.v1"],
    "parser_contract": "test-parser-v1",
    "provider": "test-provider",
    "provider_update_time": {
        "inheritance": "never_from_capture_or_sibling",
        "rule": "structure_stated_or_unstated",
    },
    "reconciliation": {"rule": "exact_requested_subject"},
    "schema": SCHEMA,
    "version": SCHEMA_VERSION,
}


class ProviderRecipeError(Exception):
    """Provider recipe registration or same-recipe write refused."""


@dataclass(frozen=True)
class RegisteredRecipe:
    derivation_version_id: str
    provider: str
    adapter_contract: str
    recipe_canonical_bytes: bytes


@dataclass(frozen=True)
class ObservationEnvelope:
    capture_id: str
    attempt_id: str
    derivation_version_id: str
    provider: str
    adapter_contract: str
    observation_kind: str
    within_capture_identity: str


@dataclass(frozen=True)
class DerivationDiagnostic:
    derivation_version_id: str
    attempt_id: str | None
    capture_id: str | None
    diagnostic_code: str
    provider_body_path: str


def validate_recipe(value: object) -> dict[str, object]:
    """Validate a closed derivation-recipe v1 document."""

    document = _object(value, "recipe")
    _reject_unknown(document, _RECIPE_KEYS, "recipe")
    _exact_string(_require(document, "schema", "recipe"), SCHEMA, "recipe.schema")
    if _json_int(_require(document, "version", "recipe"), "recipe.version") != SCHEMA_VERSION:
        raise DocumentError("recipe.version must be 1")
    adapter = _token(_require(document, "adapter_contract", "recipe"), "recipe.adapter_contract")
    provider = _token(_require(document, "provider", "recipe"), "recipe.provider")
    parser = _token(_require(document, "parser_contract", "recipe"), "recipe.parser_contract")
    admission = _closed_object(
        _require(document, "admission", "recipe"), _ADMISSION_KEYS, "recipe.admission"
    )
    data_period = _closed_object(
        _require(document, "data_period", "recipe"),
        _DATA_PERIOD_KEYS,
        "recipe.data_period",
    )
    extension = _closed_object(
        _require(document, "extension_policy", "recipe"),
        _EXTENSION_KEYS,
        "recipe.extension_policy",
    )
    field_state = _closed_object(
        _require(document, "field_state", "recipe"),
        _FIELD_STATE_KEYS,
        "recipe.field_state",
    )
    numeric = _closed_object(
        _require(document, "numeric", "recipe"), _NUMERIC_KEYS, "recipe.numeric"
    )
    provider_time = _closed_object(
        _require(document, "provider_update_time", "recipe"),
        _PROVIDER_TIME_KEYS,
        "recipe.provider_update_time",
    )
    reconciliation = _closed_object(
        _require(document, "reconciliation", "recipe"),
        _RECONCILIATION_KEYS,
        "recipe.reconciliation",
    )
    kinds = _token_list(
        _require(document, "observation_kinds", "recipe"), "recipe.observation_kinds"
    )
    observation_identity_section = _closed_object(
        _require(document, "observation_identity", "recipe"),
        _OBSERVATION_IDENTITY_KEYS,
        "recipe.observation_identity",
    )
    return {
        "adapter_contract": adapter,
        "admission": {
            "capture_outcomes": _token_list(
                _require(admission, "capture_outcomes", "recipe.admission"),
                "recipe.admission.capture_outcomes",
            ),
            "rule": _token(
                _require(admission, "rule", "recipe.admission"),
                "recipe.admission.rule",
            ),
        },
        "data_period": {
            "inheritance": _token(
                _require(data_period, "inheritance", "recipe.data_period"),
                "recipe.data_period.inheritance",
            ),
            "rule": _token(
                _require(data_period, "rule", "recipe.data_period"),
                "recipe.data_period.rule",
            ),
        },
        "extension_policy": {
            "closed_objects": _pointer_list(
                _require(extension, "closed_objects", "recipe.extension_policy"),
                "recipe.extension_policy.closed_objects",
            ),
            "extension_permitted_objects": _pointer_list(
                _require(
                    extension,
                    "extension_permitted_objects",
                    "recipe.extension_policy",
                ),
                "recipe.extension_policy.extension_permitted_objects",
            ),
            "unknown_closed_field": _token(
                _require(extension, "unknown_closed_field", "recipe.extension_policy"),
                "recipe.extension_policy.unknown_closed_field",
            ),
            "unknown_extension_field": _token(
                _require(
                    extension, "unknown_extension_field", "recipe.extension_policy"
                ),
                "recipe.extension_policy.unknown_extension_field",
            ),
        },
        "field_state": {
            "states": _token_list(
                _require(field_state, "states", "recipe.field_state"),
                "recipe.field_state.states",
            )
        },
        "numeric": {
            "normalization": _token(
                _require(numeric, "normalization", "recipe.numeric"),
                "recipe.numeric.normalization",
            )
        },
        "observation_identity": {
            "document_schema": _token(
                _require(
                    observation_identity_section,
                    "document_schema",
                    "recipe.observation_identity",
                ),
                "recipe.observation_identity.document_schema",
            ),
            "document_version": _json_int(
                _require(
                    observation_identity_section,
                    "document_version",
                    "recipe.observation_identity",
                ),
                "recipe.observation_identity.document_version",
            ),
            "kinds": _kind_identity_list(
                _require(
                    observation_identity_section,
                    "kinds",
                    "recipe.observation_identity",
                ),
                kinds,
                "recipe.observation_identity.kinds",
            ),
        },
        "observation_kinds": kinds,
        "parser_contract": parser,
        "provider": provider,
        "provider_update_time": {
            "inheritance": _token(
                _require(provider_time, "inheritance", "recipe.provider_update_time"),
                "recipe.provider_update_time.inheritance",
            ),
            "rule": _token(
                _require(provider_time, "rule", "recipe.provider_update_time"),
                "recipe.provider_update_time.rule",
            ),
        },
        "reconciliation": {
            "rule": _token(
                _require(reconciliation, "rule", "recipe.reconciliation"),
                "recipe.reconciliation.rule",
            ),
        },
        "schema": SCHEMA,
        "version": SCHEMA_VERSION,
    }


def recipe_bytes(recipe: Mapping[str, object]) -> bytes:
    """Return JCS bytes of a validated recipe."""

    return canonical_json(validate_recipe(recipe))


def recipe_derivation_version_id(recipe: Mapping[str, object]) -> str:
    """Return sha256(JCS(recipe)) as a lowercase 64-hex digest."""

    return content_digest(recipe_bytes(recipe))


def observation_identity(
    document: Mapping[str, object], recipe: Mapping[str, object]
) -> str:
    """Return sha256(JCS(closed per-kind semantic-identity document))."""

    validated_recipe = validate_recipe(recipe)
    identity_section = _object(
        validated_recipe["observation_identity"], "recipe.observation_identity"
    )
    schema = str(identity_section["document_schema"])
    version = _json_int(
        identity_section["document_version"],
        "recipe.observation_identity.document_version",
    )
    kind_defs = identity_section["kinds"]
    if not isinstance(kind_defs, list):
        raise DocumentError("recipe.observation_identity.kinds must be an array")
    declared = validated_recipe["observation_kinds"]
    if not isinstance(declared, list):
        raise DocumentError("recipe.observation_kinds must be an array")
    value = _object(document, "observation identity")
    _reject_unknown(value, _IDENTITY_KEYS, "observation identity")
    kind = _token(
        _require(value, "observation_kind", "observation identity"),
        "observation identity.observation_kind",
    )
    if kind not in declared:
        raise DocumentError(
            "observation identity.observation_kind is not declared by the recipe"
        )
    selected = _kind_identity_definition(kind_defs, kind)
    _exact_string(
        _require(value, "schema", "observation identity"),
        schema,
        "observation identity.schema",
    )
    if (
        _json_int(
            _require(value, "version", "observation identity"),
            "observation identity.version",
        )
        != version
    ):
        raise DocumentError("observation identity.version must match the recipe")
    axes = _object(_require(value, "axes", "observation identity"), "observation identity.axes")
    axis_types = _object(selected["axes"], "kind identity axes")
    if set(axes) != set(axis_types):
        raise DocumentError(
            "observation identity.axes must match the kind identity definition"
        )
    closed_axes: dict[str, object] = {}
    for name, axis_type in axis_types.items():
        closed_axes[name] = _axis_value(
            axes[name], str(axis_type), f"observation identity.axes.{name}"
        )
    closed = {
        "axes": closed_axes,
        "observation_kind": kind,
        "schema": schema,
        "version": version,
    }
    return content_digest(canonical_json(closed))


def register_provider_recipe(
    connection: Connection[Any], recipe: Mapping[str, object]
) -> RegisteredRecipe:
    """Register a provider recipe, or reuse identical stored bytes and metadata."""

    validated = validate_recipe(recipe)
    raw = canonical_json(validated)
    digest = content_digest(raw)
    provider = str(validated["provider"])
    adapter = str(validated["adapter_contract"])
    with connection.transaction():
        version = connection.execute(
            """
            SELECT adapter_contract
            FROM derivation_versions
            WHERE derivation_version_id = %s
            """,
            (digest,),
        ).fetchone()
        existing = connection.execute(
            """
            SELECT provider, adapter_contract, recipe_canonical_bytes
            FROM provider_recipes
            WHERE derivation_version_id = %s
            """,
            (digest,),
        ).fetchone()
        if existing is not None:
            existing_provider, existing_adapter, existing_bytes = existing
            if bytes(existing_bytes) != raw:
                raise ProviderRecipeError("conflicting canonical bytes")
            if existing_provider != provider or existing_adapter != adapter:
                raise ProviderRecipeError("conflicting adapter metadata")
            if version is None or version[0] != adapter:
                raise ProviderRecipeError("conflicting adapter metadata")
            return RegisteredRecipe(
                derivation_version_id=digest,
                provider=provider,
                adapter_contract=adapter,
                recipe_canonical_bytes=raw,
            )
        if version is not None:
            raise ProviderRecipeError(
                "derivation version is already registered without recipe bytes"
            )
        connection.execute(
            """
            INSERT INTO derivation_versions (
                derivation_version_id, adapter_contract, registered_at
            )
            VALUES (%s, %s, now())
            """,
            (digest, adapter),
        )
        connection.execute(
            """
            INSERT INTO provider_recipes (
                derivation_version_id, provider, adapter_contract,
                recipe_canonical_bytes
            )
            VALUES (%s, %s, %s, %s)
            """,
            (digest, provider, adapter, raw),
        )
        return RegisteredRecipe(
            derivation_version_id=digest,
            provider=provider,
            adapter_contract=adapter,
            recipe_canonical_bytes=raw,
        )


def write_derived_row(
    connection: Connection[Any],
    *,
    table: str,
    identity: Mapping[str, object],
    content: Mapping[str, object],
) -> None:
    """Insert one allowlisted derived row, or require exact existing content."""

    spec = _TABLE_SPEC.get(table)
    if spec is None:
        raise ProviderRecipeError(f"unsupported derived table {table!r}")
    identity_keys, content_keys = spec
    if set(identity) != identity_keys:
        raise ProviderRecipeError(f"{table} identity columns are closed")
    if set(content) != content_keys:
        raise ProviderRecipeError(f"{table} content columns are closed")
    where = sql.SQL(" AND ").join(
        sql.SQL("{} IS NOT DISTINCT FROM {}").format(sql.Identifier(key), sql.Placeholder())
        for key in sorted(identity)
    )
    selected: sql.Composable
    if content:
        selected = sql.SQL(", ").join(sql.Identifier(key) for key in sorted(content))
    else:
        selected = sql.SQL("1")
    existing = connection.execute(
        sql.SQL("SELECT {} FROM {} WHERE {}").format(
            selected, sql.Identifier(table), where
        ),
        [identity[key] for key in sorted(identity)],
    ).fetchone()
    if existing is None:
        values = {**dict(identity), **dict(content)}
        columns = sorted(values)
        connection.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(", ").join(sql.Identifier(key) for key in columns),
                sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            ),
            [values[key] for key in columns],
        )
        return
    intended = tuple(content[key] for key in sorted(content))
    if content and existing != intended:
        raise ProviderRecipeError(f"conflicting {table} row")


def write_observation_envelope(
    connection: Connection[Any], envelope: ObservationEnvelope
) -> None:
    """Insert or exact-content reuse one provider Observation envelope."""

    _hex64(envelope.capture_id, "envelope.capture_id")
    _hex64(envelope.attempt_id, "envelope.attempt_id")
    _hex64(envelope.derivation_version_id, "envelope.derivation_version_id")
    _hex64(envelope.within_capture_identity, "envelope.within_capture_identity")
    _token(envelope.provider, "envelope.provider")
    _token(envelope.adapter_contract, "envelope.adapter_contract")
    _token(envelope.observation_kind, "envelope.observation_kind")
    registered = _load_registered_recipe(connection, envelope.derivation_version_id)
    if (
        envelope.provider != registered.provider
        or envelope.adapter_contract != registered.adapter_contract
    ):
        raise ProviderRecipeError("envelope adapter metadata does not match the recipe")
    kinds = _load_recipe_document(registered.recipe_canonical_bytes)["observation_kinds"]
    if not isinstance(kinds, list) or envelope.observation_kind not in kinds:
        raise ProviderRecipeError("observation_kind is not declared by the recipe")
    write_derived_row(
        connection,
        table="observation_envelopes",
        identity={
            "capture_id": envelope.capture_id,
            "derivation_version_id": envelope.derivation_version_id,
            "within_capture_identity": envelope.within_capture_identity,
        },
        content={
            "attempt_id": envelope.attempt_id,
            "provider": envelope.provider,
            "adapter_contract": envelope.adapter_contract,
            "observation_kind": envelope.observation_kind,
        },
    )


def write_derivation_diagnostic(
    connection: Connection[Any], diagnostic: DerivationDiagnostic
) -> None:
    """Insert or reuse one rebuildable Derivation diagnostic."""

    _hex64(diagnostic.derivation_version_id, "diagnostic.derivation_version_id")
    if diagnostic.attempt_id is not None:
        _hex64(diagnostic.attempt_id, "diagnostic.attempt_id")
    if diagnostic.capture_id is not None:
        _hex64(diagnostic.capture_id, "diagnostic.capture_id")
    if diagnostic.attempt_id is None and diagnostic.capture_id is None:
        raise ProviderRecipeError("diagnostic requires attempt_id or capture_id")
    _token(diagnostic.diagnostic_code, "diagnostic.diagnostic_code")
    if _POINTER_RE.fullmatch(diagnostic.provider_body_path) is None:
        raise DocumentError("diagnostic.provider_body_path is not a JSON Pointer")
    write_derived_row(
        connection,
        table="derivation_diagnostics",
        identity={
            "derivation_version_id": diagnostic.derivation_version_id,
            "attempt_id": diagnostic.attempt_id,
            "capture_id": diagnostic.capture_id,
            "diagnostic_code": diagnostic.diagnostic_code,
            "provider_body_path": diagnostic.provider_body_path,
        },
        content={},
    )


def _load_registered_recipe(
    connection: Connection[Any], derivation_version_id: str
) -> RegisteredRecipe:
    row = connection.execute(
        """
        SELECT provider, adapter_contract, recipe_canonical_bytes
        FROM provider_recipes
        WHERE derivation_version_id = %s
        """,
        (derivation_version_id,),
    ).fetchone()
    if row is None:
        raise ProviderRecipeError("provider recipe is not registered")
    provider, adapter, raw = row
    return RegisteredRecipe(
        derivation_version_id=derivation_version_id,
        provider=str(provider),
        adapter_contract=str(adapter),
        recipe_canonical_bytes=bytes(raw),
    )


def _load_recipe_document(raw: bytes) -> dict[str, object]:
    try:
        parsed: object = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderRecipeError("stored recipe bytes are not valid UTF-8 JSON") from exc
    validated = validate_recipe(parsed)
    if canonical_json(validated) != raw:
        raise ProviderRecipeError("stored recipe bytes are not exact JCS")
    return validated


def _object(value: object, name: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        result: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise DocumentError(f"{name} keys must be strings")
            result[key] = item
        return result
    raise DocumentError(f"{name} must be an object")


def _closed_object(value: object, allowed: frozenset[str], name: str) -> dict[str, object]:
    document = _object(value, name)
    _reject_unknown(document, allowed, name)
    return document


def _reject_unknown(value: Mapping[str, object], allowed: frozenset[str], name: str) -> None:
    extra = [key for key in value if key not in allowed]
    if extra:
        raise DocumentError(f"{name} has unknown properties: {', '.join(sorted(extra))}")


def _require(value: Mapping[str, object], key: str, name: str) -> object:
    if key not in value:
        raise DocumentError(f"{name} missing {key}")
    return value[key]


def _exact_string(value: object, expected: str, name: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise DocumentError(f"{name} must be exactly {expected!r}")
    return value


def _token(value: object, name: str) -> str:
    if not isinstance(value, str) or _TOKEN_RE.fullmatch(value) is None:
        raise DocumentError(f"{name} is not a valid token")
    return value


def _json_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DocumentError(f"{name} must be a JSON integer")
    if value < _SAFE_INTEGER_MIN or value > _SAFE_INTEGER_MAX:
        raise DocumentError(f"{name} is outside the I-JSON safe-integer range")
    return value


def _axis_value(value: object, axis_type: str, name: str) -> str | int:
    if axis_type == "string":
        if not isinstance(value, str):
            raise DocumentError(f"{name} must be a string")
        return value
    if axis_type == "integer":
        return _json_int(value, name)
    raise DocumentError(f"{name} type must be string or integer")


def _axis_map(value: object, name: str) -> dict[str, str]:
    axes = _object(value, name)
    if len(axes) == 0:
        raise DocumentError(f"{name} must be a non-empty object")
    result: dict[str, str] = {}
    for key, axis_type in axes.items():
        _token(key, f"{name} name")
        if axis_type not in _AXIS_TYPES:
            raise DocumentError(f"{name} type must be string or integer")
        result[key] = str(axis_type)
    return result


def _kind_identity_list(
    value: object, declared_kinds: list[str], name: str
) -> list[dict[str, object]]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise DocumentError(f"{name} must be an array")
    if len(value) == 0:
        raise DocumentError(f"{name} must be a non-empty array")
    seen: list[str] = []
    items: list[dict[str, object]] = []
    for item in value:
        entry = _closed_object(item, _KIND_IDENTITY_KEYS, f"{name} item")
        kind = _token(
            _require(entry, "observation_kind", f"{name} item"),
            f"{name} item.observation_kind",
        )
        if kind in seen:
            raise DocumentError(f"{name} has duplicate observation_kind")
        seen.append(kind)
        items.append(
            {
                "axes": _axis_map(_require(entry, "axes", f"{name} item"), f"{name} item.axes"),
                "observation_kind": kind,
            }
        )
    if set(seen) != set(declared_kinds):
        raise DocumentError(f"{name} must declare exactly the recipe observation_kinds")
    return items


def _kind_identity_definition(
    kind_defs: list[object], kind: str
) -> dict[str, object]:
    for item in kind_defs:
        entry = _object(item, "kind identity")
        if entry.get("observation_kind") == kind:
            return entry
    raise DocumentError("observation identity has no identity rule for this kind")


def _hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or _HEX64_RE.fullmatch(value) is None:
        raise DocumentError(f"{name} must be 64-character lowercase hex")
    return value


def _token_list(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise DocumentError(f"{name} must be an array")
    if len(value) == 0:
        raise DocumentError(f"{name} must be a non-empty array")
    items = [_token(item, f"{name} item") for item in value]
    if len(set(items)) != len(items):
        raise DocumentError(f"{name} must not contain duplicates")
    return items


def _pointer_list(value: object, name: str) -> list[str]:
    if not isinstance(value, list) or isinstance(value, (str, bytes, bytearray)):
        raise DocumentError(f"{name} must be an array")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or _POINTER_RE.fullmatch(item) is None:
            raise DocumentError(f"{name} item is not a JSON Pointer")
        items.append(item)
    if len(set(items)) != len(items):
        raise DocumentError(f"{name} must not contain duplicates")
    return items
