"""In-memory Capture Event documents: JCS, closed schemas, content IDs."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Final, cast

EMPTY_BODY_SHA256: Final[str] = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
)

# I-JSON / IEEE 754 safe-integer range. Observatory policy on identity-bearing
# integers; see capture-event-v2.md §Scalar constraints.
_SAFE_INTEGER_MAX: Final[int] = 9007199254740991
_SAFE_INTEGER_MIN: Final[int] = -9007199254740991

_HEX64_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$"
)
_PANEL_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_SOFTWARE_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._+:-]{1,128}$")

_SCENARIOS: Final[frozenset[str]] = frozenset(
    {
        "admitted_results",
        "admitted_empty",
        "provider_refusal",
        "provider_failure",
        "malformed_response",
        "wrong_media_type",
        "response_partial",
        "no_response",
        "extra_subject",
        "too_many_results",
    }
)

_FIXTURE_HEADERS: Final[list[list[str]]] = [["content-type", "application/json"]]
_FIXTURE_POLICY: Final[dict[str, str]] = {
    "mode": "fixture_no_spend",
    "policy_version": "fixture-v1",
}

HTTP_ADAPTER_CONTRACT: Final[str] = (
    "dataforseo-serp-google-organic-live-advanced-sandbox-v1"
)
HTTP_PROVIDER: Final[str] = "dataforseo"
HTTP_HOST: Final[str] = "sandbox.dataforseo.com"
HTTP_PATH: Final[str] = "/v3/serp/google/organic/live/advanced"
HTTP_HEADERS: Final[list[list[str]]] = [
    ["accept", "application/json"],
    ["accept-encoding", "identity"],
    ["connection", "close"],
    ["content-type", "application/json"],
    ["user-agent", "observatory-dataforseo-v1"],
]
HTTP_POLICY: Final[dict[str, str]] = {
    "mode": "sandbox_no_spend",
    "policy_version": "dataforseo-sandbox-v1",
}
_LANGUAGE_RE: Final[re.Pattern[str]] = re.compile(r"^[a-z]{2}$")
_REQUEST_CREDENTIAL_HEADERS: Final[frozenset[str]] = frozenset(
    {"authorization", "cookie", "proxy-authorization"}
)
_SECRET_RESPONSE_HEADERS: Final[frozenset[str]] = frozenset(
    {
        "api-key",
        "authentication-info",
        "authorization",
        "cookie",
        "proxy-authentication-info",
        "proxy-authorization",
        "set-cookie",
        "x-access-token",
        "x-api-key",
        "x-auth-token",
    }
)
_HTTP_VERSIONS: Final[frozenset[str]] = frozenset({"HTTP/1.0", "HTTP/1.1", "HTTP/2"})
_HTTP_FAILURE_CODES: Final[dict[str, frozenset[str]]] = {
    "connect": frozenset({"timeout", "connection_failed"}),
    "send_request": frozenset({"timeout", "connection_failed", "write_failed"}),
    "receive_headers": frozenset(
        {"timeout", "connection_failed", "protocol_failed", "read_failed"}
    ),
    "receive_body": frozenset(
        {"timeout", "connection_failed", "protocol_failed", "read_failed"}
    ),
}

_STRING_ESCAPES: Final[dict[int, str]] = {
    0x08: r"\b",
    0x09: r"\t",
    0x0A: r"\n",
    0x0C: r"\f",
    0x0D: r"\r",
    0x22: r"\"",
    0x5C: r"\\",
}

_BODY_REF_KEYS: Final[frozenset[str]] = frozenset({"sha256", "bytes"})
_REQUEST_KEYS: Final[frozenset[str]] = frozenset(
    {"method", "scheme", "host", "port", "path", "query", "headers", "body"}
)
_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {"contract", "panel_id", "subject_key", "depth", "scenario"}
)
_HTTP_PARAMETER_KEYS: Final[frozenset[str]] = frozenset(
    {
        "contract",
        "keyword",
        "location_code",
        "language_code",
        "depth",
        "device",
        "os",
    }
)
_SOFTWARE_KEYS: Final[frozenset[str]] = frozenset({"observatory_version"})
_POLICY_KEYS: Final[frozenset[str]] = frozenset({"mode", "policy_version"})
_FINGERPRINT_KEYS: Final[frozenset[str]] = frozenset(
    {"schema", "version", "provider", "adapter_contract", "request"}
)
_ATTEMPT_REQUIRED: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "attempt_nonce",
        "provider",
        "adapter_contract",
        "authorized_at",
        "request_fingerprint",
        "request",
        "parameters",
        "policy",
        "software",
    }
)
_ATTEMPT_OPTIONAL: Final[frozenset[str]] = frozenset({"prior_attempt_id"})
_RESPONSE_KEYS: Final[frozenset[str]] = frozenset({"headers", "body", "completeness"})
_HTTP_RESPONSE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "status",
        "http_version",
        "header_policy",
        "headers",
        "omitted_headers",
        "body",
        "completeness",
    }
)
_OMITTED_HEADER_KEYS: Final[frozenset[str]] = frozenset({"name", "count"})
_FAILURE_KEYS: Final[frozenset[str]] = frozenset({"phase", "code"})
_CAPTURE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "schema",
        "version",
        "attempt_id",
        "provider",
        "adapter_contract",
        "transport_state",
        "request",
        "request_fingerprint",
        "software",
        "request_started_at",
        "response_headers_at",
        "response_body_ended_at",
        "transport_ended_at",
        "response",
        "transport_failure",
    }
)


class DocumentError(ValueError):
    """Closed-schema or canonicalization failure."""


__all__ = [
    "EMPTY_BODY_SHA256",
    "HTTP_ADAPTER_CONTRACT",
    "DocumentError",
    "attempt_document",
    "body_ref",
    "canonical_json",
    "capture_document",
    "content_digest",
    "fingerprint_document",
    "fixture_request",
    "http_attempt_document",
    "http_capture_document",
    "http_fingerprint_document",
    "http_request",
    "validate_attempt",
    "validate_capture",
    "validate_fingerprint",
    "validate_fixture_request",
    "validate_http_parameters",
    "validate_http_request",
    "validate_parameters",
]


def content_digest(data: bytes) -> str:
    """Return the 64-character lowercase hex SHA-256 of *data*."""

    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    """Serialize *value* as RFC 8785 JCS UTF-8 with no trailing newline.

    Floats are rejected: identity-bearing documents have no floating-point values.
    """

    try:
        return _jcs(value).encode("utf-8")
    except UnicodeEncodeError as exc:
        raise DocumentError("JCS output is not valid UTF-8") from exc


def body_ref(data: bytes) -> dict[str, int | str]:
    """Return a closed `body_ref` for the exact *data* bytes."""

    size = len(data)
    if size > _SAFE_INTEGER_MAX:
        raise DocumentError("body length is outside the I-JSON safe-integer range")
    return {"bytes": size, "sha256": content_digest(data)}


def fixture_request(*, body: bytes) -> dict[str, object]:
    """Build the closed fixture-panel-v1 `request` wrapping *body*."""

    if len(body) < 1:
        raise DocumentError("fixture request body must be present_nonempty")
    return _validate_fixture_request(
        {
            "body": {"body": body_ref(body), "state": "present_nonempty"},
            "headers": [list(pair) for pair in _FIXTURE_HEADERS],
            "host": "fixture-panel",
            "method": "POST",
            "path": "/v1/measure",
            "port": None,
            "query": [],
            "scheme": "fixture",
        }
    )


def fingerprint_document(*, request: Mapping[str, object]) -> dict[str, object]:
    """Build the closed request-fingerprint preimage for a fixture request."""

    return _validate_fingerprint(
        {
            "adapter_contract": "fixture-panel-v1",
            "provider": "fixture",
            "request": dict(request),
            "schema": "observatory.request-fingerprint",
            "version": 1,
        }
    )


def attempt_document(
    *,
    parameters: Mapping[str, object],
    attempt_nonce: str,
    authorized_at: str,
    observatory_version: str,
    prior_attempt_id: str | None = None,
) -> dict[str, object]:
    """Construct a closed Attempt from fixture parameters and authorization fields."""

    params = _validate_parameters(dict(parameters))
    request = fixture_request(body=canonical_json(params))
    fingerprint = fingerprint_document(request=request)
    document: dict[str, object] = {
        "adapter_contract": "fixture-panel-v1",
        "attempt_nonce": attempt_nonce,
        "authorized_at": authorized_at,
        "parameters": params,
        "policy": dict(_FIXTURE_POLICY),
        "provider": "fixture",
        "request": request,
        "request_fingerprint": content_digest(canonical_json(fingerprint)),
        "schema": "observatory.attempt-event",
        "software": {"observatory_version": observatory_version},
        "version": 1,
    }
    if prior_attempt_id is not None:
        document["prior_attempt_id"] = prior_attempt_id
    return _validate_attempt(document)


def capture_document(
    *,
    attempt: Mapping[str, object],
    request_started_at: str,
    transport_ended_at: str,
    transport_state: str,
    response: Mapping[str, object] | None,
    transport_failure: Mapping[str, object] | None,
    response_headers_at: str | None,
    response_body_ended_at: str | None,
    observatory_version: str | None = None,
) -> dict[str, object]:
    """Construct a closed Capture citing a validated parent Attempt."""

    parent = validate_attempt(attempt)
    software = (
        {"observatory_version": observatory_version}
        if observatory_version is not None
        else dict(cast(Mapping[str, object], parent["software"]))
    )
    document: dict[str, object] = {
        "adapter_contract": "fixture-panel-v1",
        "attempt_id": content_digest(canonical_json(parent)),
        "provider": "fixture",
        "request": parent["request"],
        "request_fingerprint": parent["request_fingerprint"],
        "request_started_at": request_started_at,
        "response": None if response is None else dict(response),
        "response_body_ended_at": response_body_ended_at,
        "response_headers_at": response_headers_at,
        "schema": "observatory.capture-event",
        "software": software,
        "transport_ended_at": transport_ended_at,
        "transport_failure": None if transport_failure is None else dict(transport_failure),
        "transport_state": transport_state,
        "version": 1,
    }
    return _validate_capture(document, attempt=parent)


def http_request(*, body: bytes) -> dict[str, object]:
    """Build the closed HTTP-v2 sandbox request wrapping *body*."""

    if len(body) < 1:
        raise DocumentError("HTTP request body must be present_nonempty")
    return _validate_http_request(
        {
            "body": {"body": body_ref(body), "state": "present_nonempty"},
            "headers": [list(pair) for pair in HTTP_HEADERS],
            "host": HTTP_HOST,
            "method": "POST",
            "path": HTTP_PATH,
            "port": None,
            "query": [],
            "scheme": "https",
        }
    )


def http_fingerprint_document(*, request: Mapping[str, object]) -> dict[str, object]:
    """Build the closed request-fingerprint preimage for an HTTP-v2 request."""

    return _validate_fingerprint(
        {
            "adapter_contract": HTTP_ADAPTER_CONTRACT,
            "provider": HTTP_PROVIDER,
            "request": dict(request),
            "schema": "observatory.request-fingerprint",
            "version": 2,
        }
    )


def http_attempt_document(
    *,
    parameters: Mapping[str, object],
    attempt_nonce: str,
    authorized_at: str,
    observatory_version: str,
) -> dict[str, object]:
    """Construct a closed HTTP-v2 Attempt. ``prior_attempt_id`` is not permitted."""

    params = _validate_http_parameters(dict(parameters))
    request = http_request(body=_http_request_body_bytes(params))
    fingerprint = http_fingerprint_document(request=request)
    document: dict[str, object] = {
        "adapter_contract": HTTP_ADAPTER_CONTRACT,
        "attempt_nonce": attempt_nonce,
        "authorized_at": authorized_at,
        "parameters": params,
        "policy": dict(HTTP_POLICY),
        "provider": HTTP_PROVIDER,
        "request": request,
        "request_fingerprint": content_digest(canonical_json(fingerprint)),
        "schema": "observatory.attempt-event",
        "software": {"observatory_version": observatory_version},
        "version": 2,
    }
    return _validate_attempt(document)


def http_capture_document(
    *,
    attempt: Mapping[str, object],
    request_started_at: str,
    transport_ended_at: str,
    transport_state: str,
    response: Mapping[str, object] | None,
    transport_failure: Mapping[str, object] | None,
    response_headers_at: str | None,
    response_body_ended_at: str | None,
    observatory_version: str | None = None,
) -> dict[str, object]:
    """Construct a closed HTTP-v2 Capture citing a validated parent Attempt."""

    parent = validate_attempt(attempt)
    software = (
        {"observatory_version": observatory_version}
        if observatory_version is not None
        else dict(cast(Mapping[str, object], parent["software"]))
    )
    document: dict[str, object] = {
        "adapter_contract": HTTP_ADAPTER_CONTRACT,
        "attempt_id": content_digest(canonical_json(parent)),
        "provider": HTTP_PROVIDER,
        "request": parent["request"],
        "request_fingerprint": parent["request_fingerprint"],
        "request_started_at": request_started_at,
        "response": None if response is None else dict(response),
        "response_body_ended_at": response_body_ended_at,
        "response_headers_at": response_headers_at,
        "schema": "observatory.capture-event",
        "software": software,
        "transport_ended_at": transport_ended_at,
        "transport_failure": None if transport_failure is None else dict(transport_failure),
        "transport_state": transport_state,
        "version": 2,
    }
    return _validate_capture(document, attempt=parent)


def validate_parameters(value: object) -> dict[str, object]:
    """Validate a closed fixture request / Attempt `parameters` document."""

    parsed, original = _parse(value)
    document = _validate_parameters(parsed)
    _require_re_jcs(document, original)
    return document


def validate_fixture_request(value: object) -> dict[str, object]:
    """Validate a closed fixture-panel-v1 `request` object."""

    parsed, original = _parse(value)
    document = _validate_fixture_request(parsed)
    _require_re_jcs(document, original)
    return document


def validate_http_parameters(value: object) -> dict[str, object]:
    """Validate a closed HTTP-v2 sandbox `parameters` document."""

    parsed, original = _parse(value)
    document = _validate_http_parameters(parsed)
    _require_re_jcs(document, original)
    return document


def validate_http_request(value: object) -> dict[str, object]:
    """Validate a closed HTTP-v2 sandbox `request` object."""

    parsed, original = _parse(value)
    document = _validate_http_request(parsed)
    _require_re_jcs(document, original)
    return document


def validate_fingerprint(value: object) -> dict[str, object]:
    """Validate a closed `observatory.request-fingerprint` document."""

    parsed, original = _parse(value)
    document = _validate_fingerprint(parsed)
    _require_re_jcs(document, original)
    return document


def validate_attempt(value: object) -> dict[str, object]:
    """Validate a closed `observatory.attempt-event` document."""

    parsed, original = _parse(value)
    document = _validate_attempt(parsed)
    _require_re_jcs(document, original)
    return document


def validate_capture(
    value: object,
    *,
    attempt: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Validate a closed `observatory.capture-event` document.

    When *attempt* is supplied, parent-identity cross-field rules are enforced.
    """

    parsed, original = _parse(value)
    document = _validate_capture(parsed, attempt=attempt)
    _require_re_jcs(document, original)
    return document


def _jcs(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return _jcs_int(value)
    if isinstance(value, float):
        raise DocumentError("floating-point values are forbidden in identity documents")
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, Mapping):
        items = sorted(
            ((_utf16_key(key), key, item) for key, item in value.items()),
            key=lambda row: row[0],
        )
        inner = ",".join(f"{_jcs_string(key)}:{_jcs(item)}" for _, key, item in items)
        return f"{{{inner}}}"
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        inner = ",".join(_jcs(item) for item in value)
        return f"[{inner}]"
    raise DocumentError(f"unsupported JSON value type: {type(value).__name__}")


def _jcs_int(value: int) -> str:
    if value < _SAFE_INTEGER_MIN or value > _SAFE_INTEGER_MAX:
        raise DocumentError("integer is outside the I-JSON safe-integer range")
    return str(value)


def _utf16_key(key: object) -> bytes:
    if not isinstance(key, str):
        raise DocumentError("object keys must be strings")
    return key.encode("utf-16-be")


def _is_noncharacter(code: int) -> bool:
    return 0xFDD0 <= code <= 0xFDEF or code & 0xFFFE == 0xFFFE


def _reject_inadmissible_code_point(code: int) -> None:
    if 0xD800 <= code <= 0xDFFF:
        raise DocumentError("surrogate code points are forbidden")
    if _is_noncharacter(code):
        raise DocumentError("noncharacter code points are forbidden")


def _jcs_string(value: str) -> str:
    chunks: list[str] = ['"']
    for char in value:
        code = ord(char)
        _reject_inadmissible_code_point(code)
        escape = _STRING_ESCAPES.get(code)
        if escape is not None:
            chunks.append(escape)
        elif code < 0x20:
            chunks.append(f"\\u{code:04x}")
        else:
            chunks.append(char)
    chunks.append('"')
    return "".join(chunks)


def _reject_inadmissible_strings(value: object) -> None:
    if isinstance(value, str):
        for char in value:
            _reject_inadmissible_code_point(ord(char))
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str):
                for char in key:
                    _reject_inadmissible_code_point(ord(char))
            _reject_inadmissible_strings(item)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            _reject_inadmissible_strings(item)


def _object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    seen: set[str] = set()
    result: dict[str, object] = {}
    for key, item in pairs:
        if key in seen:
            raise DocumentError("duplicate object member name")
        seen.add(key)
        result[key] = item
    return result


def _parse(value: object) -> tuple[object, bytes | None]:
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocumentError("invalid UTF-8") from exc
        try:
            parsed: object = json.loads(text, object_pairs_hook=_object_pairs)
        except json.JSONDecodeError as exc:
            raise DocumentError("invalid JSON") from exc
        _reject_inadmissible_strings(parsed)
        return parsed, raw
    _reject_inadmissible_strings(value)
    return value, None


def _require_re_jcs(document: object, original: bytes | None) -> None:
    if original is not None and canonical_json(document) != original:
        raise DocumentError("re-JCS does not equal original bytes")


def _object(value: object, name: str) -> dict[str, object]:
    if isinstance(value, Mapping) and not isinstance(value, (str, bytes, bytearray)):
        result: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise DocumentError(f"{name} keys must be strings")
            result[key] = item
        return result
    raise DocumentError(f"{name} must be an object")


def _reject_unknown(value: Mapping[str, object], allowed: frozenset[str], name: str) -> None:
    extra = [key for key in value if key not in allowed]
    if extra:
        raise DocumentError(f"{name} has unknown properties: {', '.join(sorted(extra))}")


def _require(value: Mapping[str, object], key: str, name: str) -> object:
    if key not in value:
        raise DocumentError(f"{name} missing {key}")
    return value[key]


def _hex64(value: object, name: str) -> str:
    if not isinstance(value, str) or _HEX64_RE.fullmatch(value) is None:
        raise DocumentError(f"{name} must be 64-character lowercase hex")
    return value


def _timestamp(value: object, name: str) -> str:
    if not isinstance(value, str) or _TIMESTAMP_RE.fullmatch(value) is None:
        raise DocumentError(f"{name} is not a frozen timestamp")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as exc:
        raise DocumentError(f"{name} is not a frozen timestamp") from exc
    return value


def _json_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise DocumentError(f"{name} must be a JSON integer")
    if value < _SAFE_INTEGER_MIN or value > _SAFE_INTEGER_MAX:
        raise DocumentError(f"{name} is outside the I-JSON safe-integer range")
    return value


def _exact_string(value: object, expected: str, name: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise DocumentError(f"{name} must be exactly {expected!r}")
    return value


def _token(value: object, pattern: re.Pattern[str], name: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise DocumentError(f"{name} is not a valid token")
    return value


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or value == "":
        raise DocumentError(f"{name} must be a non-empty string")
    return value


def _pairs(value: object, name: str, *, names_lowercase: bool = False) -> list[list[str]]:
    if not isinstance(value, list):
        raise DocumentError(f"{name} must be an array of pairs")
    pairs: list[list[str]] = []
    for index, item in enumerate(value):
        if not isinstance(item, list) or len(item) != 2:
            raise DocumentError(f"{name}[{index}] must be a pair of two strings")
        left, right = item[0], item[1]
        if not isinstance(left, str) or not isinstance(right, str):
            raise DocumentError(f"{name}[{index}] must be a pair of two strings")
        if names_lowercase and left != left.lower():
            raise DocumentError(f"{name}[{index}] name must be lowercase")
        pairs.append([left, right])
    return pairs


def _validate_body_ref(value: object, name: str) -> dict[str, int | str]:
    obj = _object(value, name)
    _reject_unknown(obj, _BODY_REF_KEYS, name)
    digest = _hex64(_require(obj, "sha256", name), f"{name}.sha256")
    size = _json_int(_require(obj, "bytes", name), f"{name}.bytes")
    if size < 0:
        raise DocumentError(f"{name}.bytes must be >= 0")
    if size == 0 and digest != EMPTY_BODY_SHA256:
        raise DocumentError(f"{name} empty-body digest mismatch")
    return {"bytes": size, "sha256": digest}


def _validate_body_state(value: object, name: str) -> dict[str, object]:
    obj = _object(value, name)
    state = _require(obj, "state", name)
    if state == "absent":
        _reject_unknown(obj, frozenset({"state"}), name)
        return {"state": "absent"}
    if state == "present_zero_bytes":
        _reject_unknown(obj, frozenset({"body", "state"}), name)
        ref = _validate_body_ref(_require(obj, "body", name), f"{name}.body")
        if ref["bytes"] != 0:
            raise DocumentError(f"{name}.body.bytes must be 0")
        return {"state": "present_zero_bytes", "body": ref}
    if state == "present_nonempty":
        _reject_unknown(obj, frozenset({"body", "state"}), name)
        ref = _validate_body_ref(_require(obj, "body", name), f"{name}.body")
        size = ref["bytes"]
        if not isinstance(size, int) or size < 1:
            raise DocumentError(f"{name}.body.bytes must be >= 1")
        return {"state": "present_nonempty", "body": ref}
    raise DocumentError(f"{name}.state is not a valid body_state")


def _validate_request_shape(value: object) -> dict[str, object]:
    obj = _object(value, "request")
    _reject_unknown(obj, _REQUEST_KEYS, "request")
    method = _nonempty_string(_require(obj, "method", "request"), "request.method")
    scheme = _nonempty_string(_require(obj, "scheme", "request"), "request.scheme")
    host = _nonempty_string(_require(obj, "host", "request"), "request.host")
    raw_port = _require(obj, "port", "request")
    if raw_port is None:
        port: int | None = None
    else:
        port = _json_int(raw_port, "request.port")
        if port < 1 or port > 65535:
            raise DocumentError("request.port must be 1..65535")
    path = _nonempty_string(_require(obj, "path", "request"), "request.path")
    if not path.startswith("/"):
        raise DocumentError("request.path must begin with /")
    query = _pairs(_require(obj, "query", "request"), "request.query")
    headers = _pairs(_require(obj, "headers", "request"), "request.headers", names_lowercase=True)
    body = _validate_body_state(_require(obj, "body", "request"), "request.body")
    return {
        "body": body,
        "headers": headers,
        "host": host,
        "method": method,
        "path": path,
        "port": port,
        "query": query,
        "scheme": scheme,
    }


def _validate_fixture_request(value: object) -> dict[str, object]:
    request = _validate_request_shape(value)
    if (
        request["method"] != "POST"
        or request["scheme"] != "fixture"
        or request["host"] != "fixture-panel"
        or request["port"] is not None
        or request["path"] != "/v1/measure"
        or request["query"] != []
        or request["headers"] != _FIXTURE_HEADERS
        or not isinstance(request["body"], Mapping)
        or request["body"].get("state") != "present_nonempty"
    ):
        raise DocumentError("request does not match fixture-panel-v1 constants")
    return request


def _validate_http_request(value: object) -> dict[str, object]:
    request = _validate_request_shape(value)
    headers = request["headers"]
    if not isinstance(headers, list):
        raise DocumentError("request.headers must be an array of pairs")
    for index, pair in enumerate(headers):
        if not isinstance(pair, list) or len(pair) != 2:
            raise DocumentError(f"request.headers[{index}] must be a pair of two strings")
        name = pair[0]
        if not isinstance(name, str):
            raise DocumentError(f"request.headers[{index}] must be a pair of two strings")
        if name in _REQUEST_CREDENTIAL_HEADERS:
            raise DocumentError(f"request.headers[{index}] is a credential-class header")
    if (
        request["method"] != "POST"
        or request["scheme"] != "https"
        or request["host"] != HTTP_HOST
        or request["port"] is not None
        or request["path"] != HTTP_PATH
        or request["query"] != []
        or request["headers"] != HTTP_HEADERS
        or not isinstance(request["body"], Mapping)
        or request["body"].get("state") != "present_nonempty"
    ):
        raise DocumentError("request does not match the sandbox HTTP adapter contract")
    return request


def _validate_parameters(value: object) -> dict[str, object]:
    obj = _object(value, "parameters")
    _reject_unknown(obj, _PARAMETER_KEYS, "parameters")
    contract = _exact_string(
        _require(obj, "contract", "parameters"),
        "fixture-panel-v1",
        "parameters.contract",
    )
    panel_id = _token(_require(obj, "panel_id", "parameters"), _PANEL_RE, "parameters.panel_id")
    subject_key = _token(
        _require(obj, "subject_key", "parameters"),
        _PANEL_RE,
        "parameters.subject_key",
    )
    depth = _json_int(_require(obj, "depth", "parameters"), "parameters.depth")
    if depth < 1 or depth > 16:
        raise DocumentError("parameters.depth must be 1..16")
    scenario = _require(obj, "scenario", "parameters")
    if not isinstance(scenario, str) or scenario not in _SCENARIOS:
        raise DocumentError("parameters.scenario is not a fixture-panel-v1 scenario")
    return {
        "contract": contract,
        "depth": depth,
        "panel_id": panel_id,
        "scenario": scenario,
        "subject_key": subject_key,
    }


def _http_task(parameters: Mapping[str, object]) -> dict[str, object]:
    return {
        "depth": parameters["depth"],
        "device": parameters["device"],
        "keyword": parameters["keyword"],
        "language_code": parameters["language_code"],
        "location_code": parameters["location_code"],
        "os": parameters["os"],
    }


def _http_request_body_bytes(parameters: Mapping[str, object]) -> bytes:
    return canonical_json([_http_task(parameters)])


def _validate_http_parameters(value: object) -> dict[str, object]:
    obj = _object(value, "parameters")
    _reject_unknown(obj, _HTTP_PARAMETER_KEYS, "parameters")
    contract = _exact_string(
        _require(obj, "contract", "parameters"),
        HTTP_ADAPTER_CONTRACT,
        "parameters.contract",
    )
    keyword = _require(obj, "keyword", "parameters")
    if not isinstance(keyword, str) or not (1 <= len(keyword) <= 700):
        raise DocumentError("parameters.keyword must be 1..700 Unicode scalar values")
    location_code = _json_int(
        _require(obj, "location_code", "parameters"),
        "parameters.location_code",
    )
    if location_code < 1:
        raise DocumentError("parameters.location_code must be 1..9007199254740991")
    language_code = _token(
        _require(obj, "language_code", "parameters"),
        _LANGUAGE_RE,
        "parameters.language_code",
    )
    depth = _json_int(_require(obj, "depth", "parameters"), "parameters.depth")
    if depth != 10:
        raise DocumentError("parameters.depth must be exactly 10")
    device = _exact_string(_require(obj, "device", "parameters"), "desktop", "parameters.device")
    os_name = _exact_string(_require(obj, "os", "parameters"), "windows", "parameters.os")
    return {
        "contract": contract,
        "depth": depth,
        "device": device,
        "keyword": keyword,
        "language_code": language_code,
        "location_code": location_code,
        "os": os_name,
    }


def _validate_software(value: object) -> dict[str, object]:
    obj = _object(value, "software")
    _reject_unknown(obj, _SOFTWARE_KEYS, "software")
    version = _token(
        _require(obj, "observatory_version", "software"),
        _SOFTWARE_RE,
        "software.observatory_version",
    )
    return {"observatory_version": version}


def _validate_policy(value: object) -> dict[str, object]:
    obj = _object(value, "policy")
    _reject_unknown(obj, _POLICY_KEYS, "policy")
    mode = _exact_string(_require(obj, "mode", "policy"), "fixture_no_spend", "policy.mode")
    policy_version = _exact_string(
        _require(obj, "policy_version", "policy"),
        "fixture-v1",
        "policy.policy_version",
    )
    return {"mode": mode, "policy_version": policy_version}


def _validate_http_policy(value: object) -> dict[str, object]:
    obj = _object(value, "policy")
    _reject_unknown(obj, _POLICY_KEYS, "policy")
    mode = _exact_string(_require(obj, "mode", "policy"), "sandbox_no_spend", "policy.mode")
    policy_version = _exact_string(
        _require(obj, "policy_version", "policy"),
        "dataforseo-sandbox-v1",
        "policy.policy_version",
    )
    return {"mode": mode, "policy_version": policy_version}


def _schema_version(obj: Mapping[str, object]) -> tuple[object, object]:
    """Read only schema and version to choose a validator branch."""

    return obj.get("schema"), obj.get("version")


def _is_version(value: object, expected: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value == expected


def _validate_fingerprint(value: object) -> dict[str, object]:
    obj = _object(value, "fingerprint")
    schema, version = _schema_version(obj)
    if schema == "observatory.request-fingerprint" and _is_version(version, 1):
        return _validate_fingerprint_v1(obj)
    if schema == "observatory.request-fingerprint" and _is_version(version, 2):
        return _validate_fingerprint_v2(obj)
    raise DocumentError("unknown fingerprint schema or version")


def _validate_fingerprint_v1(obj: Mapping[str, object]) -> dict[str, object]:
    _reject_unknown(obj, _FINGERPRINT_KEYS, "fingerprint")
    schema = _exact_string(
        _require(obj, "schema", "fingerprint"),
        "observatory.request-fingerprint",
        "fingerprint.schema",
    )
    version = _json_int(_require(obj, "version", "fingerprint"), "fingerprint.version")
    if version != 1:
        raise DocumentError("fingerprint.version must be 1")
    provider = _exact_string(
        _require(obj, "provider", "fingerprint"),
        "fixture",
        "fingerprint.provider",
    )
    adapter = _exact_string(
        _require(obj, "adapter_contract", "fingerprint"),
        "fixture-panel-v1",
        "fingerprint.adapter_contract",
    )
    request = _validate_fixture_request(_require(obj, "request", "fingerprint"))
    return {
        "adapter_contract": adapter,
        "provider": provider,
        "request": request,
        "schema": schema,
        "version": version,
    }


def _validate_fingerprint_v2(obj: Mapping[str, object]) -> dict[str, object]:
    _reject_unknown(obj, _FINGERPRINT_KEYS, "fingerprint")
    schema = _exact_string(
        _require(obj, "schema", "fingerprint"),
        "observatory.request-fingerprint",
        "fingerprint.schema",
    )
    version = _json_int(_require(obj, "version", "fingerprint"), "fingerprint.version")
    if version != 2:
        raise DocumentError("fingerprint.version must be 2")
    provider = _exact_string(
        _require(obj, "provider", "fingerprint"),
        HTTP_PROVIDER,
        "fingerprint.provider",
    )
    adapter = _exact_string(
        _require(obj, "adapter_contract", "fingerprint"),
        HTTP_ADAPTER_CONTRACT,
        "fingerprint.adapter_contract",
    )
    request = _validate_http_request(_require(obj, "request", "fingerprint"))
    return {
        "adapter_contract": adapter,
        "provider": provider,
        "request": request,
        "schema": schema,
        "version": version,
    }


def _expected_fingerprint(
    request: Mapping[str, object],
    *,
    version: int,
    provider: str,
    adapter_contract: str,
) -> str:
    return content_digest(
        canonical_json(
            {
                "adapter_contract": adapter_contract,
                "provider": provider,
                "request": request,
                "schema": "observatory.request-fingerprint",
                "version": version,
            }
        )
    )


def _parameters_match_request_body(
    parameters: Mapping[str, object],
    request: Mapping[str, object],
    *,
    encoded: bytes,
) -> None:
    body = request["body"]
    if not isinstance(body, Mapping):
        raise DocumentError("request.body is not an object")
    ref = body.get("body")
    if not isinstance(ref, Mapping):
        raise DocumentError("request body_ref is missing")
    if ref.get("sha256") != content_digest(encoded) or ref.get("bytes") != len(encoded):
        raise DocumentError("parameters do not match request body identity")


def _validate_attempt(value: object) -> dict[str, object]:
    obj = _object(value, "attempt")
    schema, version = _schema_version(obj)
    if schema == "observatory.attempt-event" and _is_version(version, 1):
        return _validate_attempt_v1(obj)
    if schema == "observatory.attempt-event" and _is_version(version, 2):
        return _validate_attempt_v2(obj)
    raise DocumentError("unknown attempt schema or version")


def _validate_attempt_v1(obj: Mapping[str, object]) -> dict[str, object]:
    _reject_unknown(obj, _ATTEMPT_REQUIRED | _ATTEMPT_OPTIONAL, "attempt")
    missing = sorted(key for key in _ATTEMPT_REQUIRED if key not in obj)
    if missing:
        raise DocumentError(f"attempt missing {', '.join(missing)}")
    schema = _exact_string(
        _require(obj, "schema", "attempt"),
        "observatory.attempt-event",
        "attempt.schema",
    )
    version = _json_int(_require(obj, "version", "attempt"), "attempt.version")
    if version != 1:
        raise DocumentError("attempt.version must be 1")
    nonce = _hex64(_require(obj, "attempt_nonce", "attempt"), "attempt.attempt_nonce")
    provider = _exact_string(_require(obj, "provider", "attempt"), "fixture", "attempt.provider")
    adapter = _exact_string(
        _require(obj, "adapter_contract", "attempt"),
        "fixture-panel-v1",
        "attempt.adapter_contract",
    )
    authorized_at = _timestamp(_require(obj, "authorized_at", "attempt"), "attempt.authorized_at")
    request_fingerprint = _hex64(
        _require(obj, "request_fingerprint", "attempt"),
        "attempt.request_fingerprint",
    )
    request = _validate_fixture_request(_require(obj, "request", "attempt"))
    parameters = _validate_parameters(_require(obj, "parameters", "attempt"))
    policy = _validate_policy(_require(obj, "policy", "attempt"))
    software = _validate_software(_require(obj, "software", "attempt"))
    if request_fingerprint != _expected_fingerprint(
        request, version=1, provider=provider, adapter_contract=adapter
    ):
        raise DocumentError("request_fingerprint does not match recompute")
    _parameters_match_request_body(parameters, request, encoded=canonical_json(parameters))
    document: dict[str, object] = {
        "adapter_contract": adapter,
        "attempt_nonce": nonce,
        "authorized_at": authorized_at,
        "parameters": parameters,
        "policy": policy,
        "provider": provider,
        "request": request,
        "request_fingerprint": request_fingerprint,
        "schema": schema,
        "software": software,
        "version": version,
    }
    if "prior_attempt_id" in obj:
        if obj["prior_attempt_id"] is None:
            raise DocumentError("prior_attempt_id must be omitted, not null")
        document["prior_attempt_id"] = _hex64(obj["prior_attempt_id"], "attempt.prior_attempt_id")
    return document


def _validate_attempt_v2(obj: Mapping[str, object]) -> dict[str, object]:
    _reject_unknown(obj, _ATTEMPT_REQUIRED, "attempt")
    missing = sorted(key for key in _ATTEMPT_REQUIRED if key not in obj)
    if missing:
        raise DocumentError(f"attempt missing {', '.join(missing)}")
    schema = _exact_string(
        _require(obj, "schema", "attempt"),
        "observatory.attempt-event",
        "attempt.schema",
    )
    version = _json_int(_require(obj, "version", "attempt"), "attempt.version")
    if version != 2:
        raise DocumentError("attempt.version must be 2")
    nonce = _hex64(_require(obj, "attempt_nonce", "attempt"), "attempt.attempt_nonce")
    provider = _exact_string(
        _require(obj, "provider", "attempt"),
        HTTP_PROVIDER,
        "attempt.provider",
    )
    adapter = _exact_string(
        _require(obj, "adapter_contract", "attempt"),
        HTTP_ADAPTER_CONTRACT,
        "attempt.adapter_contract",
    )
    authorized_at = _timestamp(_require(obj, "authorized_at", "attempt"), "attempt.authorized_at")
    request_fingerprint = _hex64(
        _require(obj, "request_fingerprint", "attempt"),
        "attempt.request_fingerprint",
    )
    request = _validate_http_request(_require(obj, "request", "attempt"))
    parameters = _validate_http_parameters(_require(obj, "parameters", "attempt"))
    policy = _validate_http_policy(_require(obj, "policy", "attempt"))
    software = _validate_software(_require(obj, "software", "attempt"))
    if request_fingerprint != _expected_fingerprint(
        request, version=2, provider=provider, adapter_contract=adapter
    ):
        raise DocumentError("request_fingerprint does not match recompute")
    _parameters_match_request_body(
        parameters, request, encoded=_http_request_body_bytes(parameters)
    )
    return {
        "adapter_contract": adapter,
        "attempt_nonce": nonce,
        "authorized_at": authorized_at,
        "parameters": parameters,
        "policy": policy,
        "provider": provider,
        "request": request,
        "request_fingerprint": request_fingerprint,
        "schema": schema,
        "software": software,
        "version": version,
    }


def _validate_response(value: object) -> dict[str, object]:
    obj = _object(value, "response")
    _reject_unknown(obj, _RESPONSE_KEYS, "response")
    headers = _pairs(_require(obj, "headers", "response"), "response.headers", names_lowercase=True)
    body = _validate_body_state(_require(obj, "body", "response"), "response.body")
    completeness = _require(obj, "completeness", "response")
    if completeness not in {"complete", "partial"}:
        raise DocumentError("response.completeness must be complete or partial")
    return {"body": body, "completeness": completeness, "headers": headers}


def _validate_omitted_headers(value: object) -> list[dict[str, int | str]]:
    if not isinstance(value, list):
        raise DocumentError("response.omitted_headers must be an array")
    omitted: list[dict[str, int | str]] = []
    names: list[str] = []
    for index, item in enumerate(value):
        obj = _object(item, f"response.omitted_headers[{index}]")
        _reject_unknown(obj, _OMITTED_HEADER_KEYS, f"response.omitted_headers[{index}]")
        name = _require(obj, "name", f"response.omitted_headers[{index}]")
        if not isinstance(name, str) or name != name.lower():
            raise DocumentError(f"response.omitted_headers[{index}].name must be lowercase")
        if name not in _SECRET_RESPONSE_HEADERS:
            raise DocumentError(f"response.omitted_headers[{index}].name is not secret-class")
        count = _json_int(
            _require(obj, "count", f"response.omitted_headers[{index}]"),
            f"response.omitted_headers[{index}].count",
        )
        if count < 1:
            raise DocumentError(f"response.omitted_headers[{index}].count must be >= 1")
        if name in names:
            raise DocumentError("response.omitted_headers names must be unique")
        names.append(name)
        omitted.append({"count": count, "name": name})
    if names != sorted(names):
        raise DocumentError("response.omitted_headers must be sorted by name")
    return omitted


def _validate_http_response(value: object) -> dict[str, object]:
    obj = _object(value, "response")
    _reject_unknown(obj, _HTTP_RESPONSE_KEYS, "response")
    status = _json_int(_require(obj, "status", "response"), "response.status")
    if status < 100 or status > 599:
        raise DocumentError("response.status must be 100..599")
    http_version = _require(obj, "http_version", "response")
    if not isinstance(http_version, str) or http_version not in _HTTP_VERSIONS:
        raise DocumentError("response.http_version is not a permitted HTTP version")
    header_policy = _exact_string(
        _require(obj, "header_policy", "response"),
        "http-headers-v1",
        "response.header_policy",
    )
    headers = _pairs(_require(obj, "headers", "response"), "response.headers", names_lowercase=True)
    retained: set[str] = set()
    for index, pair in enumerate(headers):
        name = pair[0]
        if name in _SECRET_RESPONSE_HEADERS:
            raise DocumentError(f"response.headers[{index}] retains a secret-class header")
        retained.add(name)
    omitted = _validate_omitted_headers(_require(obj, "omitted_headers", "response"))
    omitted_names = {item["name"] for item in omitted}
    if retained & omitted_names:
        raise DocumentError("response headers and omitted_headers must not overlap")
    body = _validate_body_state(_require(obj, "body", "response"), "response.body")
    completeness = _require(obj, "completeness", "response")
    if completeness not in {"complete", "partial"}:
        raise DocumentError("response.completeness must be complete or partial")
    return {
        "body": body,
        "completeness": completeness,
        "header_policy": header_policy,
        "headers": headers,
        "http_version": http_version,
        "omitted_headers": omitted,
        "status": status,
    }


def _validate_transport_failure(value: object) -> dict[str, object]:
    obj = _object(value, "transport_failure")
    _reject_unknown(obj, _FAILURE_KEYS, "transport_failure")
    phase = _exact_string(
        _require(obj, "phase", "transport_failure"),
        "receive_response",
        "transport_failure.phase",
    )
    code = _exact_string(
        _require(obj, "code", "transport_failure"),
        "fixture_no_response",
        "transport_failure.code",
    )
    return {"code": code, "phase": phase}


def _validate_http_transport_failure(value: object) -> dict[str, object]:
    obj = _object(value, "transport_failure")
    _reject_unknown(obj, _FAILURE_KEYS, "transport_failure")
    phase = _require(obj, "phase", "transport_failure")
    if not isinstance(phase, str) or phase not in _HTTP_FAILURE_CODES:
        raise DocumentError("transport_failure.phase is not a permitted HTTP phase")
    code = _require(obj, "code", "transport_failure")
    allowed = _HTTP_FAILURE_CODES[phase]
    if not isinstance(code, str) or code not in allowed:
        raise DocumentError("transport_failure.code is not permitted for this phase")
    return {"code": code, "phase": phase}


def _optional_timestamp(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _timestamp(value, name)


def _enforce_capture_branch(
    *,
    transport_state: str,
    response_headers_at: str | None,
    response_body_ended_at: str | None,
    response: Mapping[str, object] | None,
    transport_failure: Mapping[str, object] | None,
) -> None:
    if transport_state == "response_complete":
        if response_headers_at is None or response_body_ended_at is None:
            raise DocumentError("response_complete requires response timestamps")
        if response is None:
            raise DocumentError("response_complete requires a response object")
        if transport_failure is not None:
            raise DocumentError("response_complete requires transport_failure null")
        if response.get("completeness") != "complete":
            raise DocumentError("response_complete requires completeness=complete")
        return
    if transport_state == "response_partial":
        if response_headers_at is None or response_body_ended_at is None:
            raise DocumentError("response_partial requires response timestamps")
        if response is None:
            raise DocumentError("response_partial requires a response object")
        if transport_failure is not None:
            raise DocumentError("response_partial requires transport_failure null")
        if response.get("completeness") != "partial":
            raise DocumentError("response_partial requires completeness=partial")
        body = response.get("body")
        if not isinstance(body, Mapping) or body.get("state") != "present_nonempty":
            raise DocumentError("response_partial body must be present_nonempty")
        return
    if transport_state == "no_response":
        if response_headers_at is not None or response_body_ended_at is not None:
            raise DocumentError("no_response requires null response timestamps")
        if response is not None:
            raise DocumentError("no_response requires response null")
        if transport_failure is None:
            raise DocumentError("no_response requires a transport_failure object")
        return
    raise DocumentError("transport_state is not a valid Capture transport_state")


def _enforce_http_capture_branch(
    *,
    transport_state: str,
    response_headers_at: str | None,
    response_body_ended_at: str | None,
    response: Mapping[str, object] | None,
    transport_failure: Mapping[str, object] | None,
) -> None:
    if transport_state == "response_complete":
        if response_headers_at is None or response_body_ended_at is None:
            raise DocumentError("response_complete requires response timestamps")
        if response is None:
            raise DocumentError("response_complete requires a response object")
        if transport_failure is not None:
            raise DocumentError("response_complete requires transport_failure null")
        if response.get("completeness") != "complete":
            raise DocumentError("response_complete requires completeness=complete")
        return
    if transport_state == "response_partial":
        if response_headers_at is None or response_body_ended_at is None:
            raise DocumentError("response_partial requires response timestamps")
        if response is None:
            raise DocumentError("response_partial requires a response object")
        if transport_failure is None:
            raise DocumentError("response_partial requires a transport_failure object")
        if transport_failure.get("phase") != "receive_body":
            raise DocumentError("response_partial requires phase receive_body")
        if response.get("completeness") != "partial":
            raise DocumentError("response_partial requires completeness=partial")
        body = response.get("body")
        if not isinstance(body, Mapping) or body.get("state") not in {
            "present_nonempty",
            "present_zero_bytes",
        }:
            raise DocumentError("response_partial body must be present")
        return
    if transport_state == "no_response":
        if response_headers_at is not None or response_body_ended_at is not None:
            raise DocumentError("no_response requires null response timestamps")
        if response is not None:
            raise DocumentError("no_response requires response null")
        if transport_failure is None:
            raise DocumentError("no_response requires a transport_failure object")
        if transport_failure.get("phase") == "receive_body":
            raise DocumentError("no_response forbids phase receive_body")
        return
    raise DocumentError("transport_state is not a valid Capture transport_state")


def _enforce_timestamp_order(
    request_started_at: str,
    response_headers_at: str | None,
    response_body_ended_at: str | None,
    transport_ended_at: str,
) -> None:
    if request_started_at > transport_ended_at:
        raise DocumentError("request_started_at must be <= transport_ended_at")
    if response_headers_at is None or response_body_ended_at is None:
        return
    if not (
        request_started_at
        <= response_headers_at
        <= response_body_ended_at
        <= transport_ended_at
    ):
        raise DocumentError("Capture timestamps are out of order")


def _enforce_parent_attempt(document: Mapping[str, object], attempt: Mapping[str, object]) -> None:
    parent = _validate_attempt(attempt)
    if document["attempt_id"] != content_digest(canonical_json(parent)):
        raise DocumentError("capture.attempt_id does not match parent Attempt")
    if document["request"] != parent["request"]:
        raise DocumentError("capture.request does not equal parent request")
    if document["request_fingerprint"] != parent["request_fingerprint"]:
        raise DocumentError("capture.request_fingerprint does not equal parent")
    if document["provider"] != parent["provider"]:
        raise DocumentError("capture.provider does not equal parent")
    if document["adapter_contract"] != parent["adapter_contract"]:
        raise DocumentError("capture.adapter_contract does not equal parent")


def _validate_capture(
    value: object,
    *,
    attempt: Mapping[str, object] | None,
) -> dict[str, object]:
    obj = _object(value, "capture")
    schema, version = _schema_version(obj)
    if schema == "observatory.capture-event" and _is_version(version, 1):
        return _validate_capture_v1(obj, attempt=attempt)
    if schema == "observatory.capture-event" and _is_version(version, 2):
        return _validate_capture_v2(obj, attempt=attempt)
    raise DocumentError("unknown capture schema or version")


def _validate_capture_v1(
    obj: Mapping[str, object],
    *,
    attempt: Mapping[str, object] | None,
) -> dict[str, object]:
    _reject_unknown(obj, _CAPTURE_KEYS, "capture")
    missing = sorted(key for key in _CAPTURE_KEYS if key not in obj)
    if missing:
        raise DocumentError(f"capture missing {', '.join(missing)}")
    schema = _exact_string(
        _require(obj, "schema", "capture"),
        "observatory.capture-event",
        "capture.schema",
    )
    version = _json_int(_require(obj, "version", "capture"), "capture.version")
    if version != 1:
        raise DocumentError("capture.version must be 1")
    attempt_id = _hex64(_require(obj, "attempt_id", "capture"), "capture.attempt_id")
    provider = _exact_string(_require(obj, "provider", "capture"), "fixture", "capture.provider")
    adapter = _exact_string(
        _require(obj, "adapter_contract", "capture"),
        "fixture-panel-v1",
        "capture.adapter_contract",
    )
    transport_state = _require(obj, "transport_state", "capture")
    if transport_state not in {"response_complete", "response_partial", "no_response"}:
        raise DocumentError("capture.transport_state is invalid")
    request = _validate_fixture_request(_require(obj, "request", "capture"))
    request_fingerprint = _hex64(
        _require(obj, "request_fingerprint", "capture"),
        "capture.request_fingerprint",
    )
    if request_fingerprint != _expected_fingerprint(
        request, version=1, provider=provider, adapter_contract=adapter
    ):
        raise DocumentError("request_fingerprint does not match recompute")
    software = _validate_software(_require(obj, "software", "capture"))
    request_started_at = _timestamp(
        _require(obj, "request_started_at", "capture"),
        "capture.request_started_at",
    )
    response_headers_at = _optional_timestamp(
        _require(obj, "response_headers_at", "capture"),
        "capture.response_headers_at",
    )
    response_body_ended_at = _optional_timestamp(
        _require(obj, "response_body_ended_at", "capture"),
        "capture.response_body_ended_at",
    )
    transport_ended_at = _timestamp(
        _require(obj, "transport_ended_at", "capture"),
        "capture.transport_ended_at",
    )
    raw_response = _require(obj, "response", "capture")
    response = None if raw_response is None else _validate_response(raw_response)
    raw_failure = _require(obj, "transport_failure", "capture")
    transport_failure = (
        None if raw_failure is None else _validate_transport_failure(raw_failure)
    )
    _enforce_capture_branch(
        transport_state=str(transport_state),
        response_headers_at=response_headers_at,
        response_body_ended_at=response_body_ended_at,
        response=response,
        transport_failure=transport_failure,
    )
    _enforce_timestamp_order(
        request_started_at,
        response_headers_at,
        response_body_ended_at,
        transport_ended_at,
    )
    document: dict[str, object] = {
        "adapter_contract": adapter,
        "attempt_id": attempt_id,
        "provider": provider,
        "request": request,
        "request_fingerprint": request_fingerprint,
        "request_started_at": request_started_at,
        "response": response,
        "response_body_ended_at": response_body_ended_at,
        "response_headers_at": response_headers_at,
        "schema": schema,
        "software": software,
        "transport_ended_at": transport_ended_at,
        "transport_failure": transport_failure,
        "transport_state": transport_state,
        "version": version,
    }
    if attempt is not None:
        _enforce_parent_attempt(document, attempt)
    return document


def _validate_capture_v2(
    obj: Mapping[str, object],
    *,
    attempt: Mapping[str, object] | None,
) -> dict[str, object]:
    _reject_unknown(obj, _CAPTURE_KEYS, "capture")
    missing = sorted(key for key in _CAPTURE_KEYS if key not in obj)
    if missing:
        raise DocumentError(f"capture missing {', '.join(missing)}")
    schema = _exact_string(
        _require(obj, "schema", "capture"),
        "observatory.capture-event",
        "capture.schema",
    )
    version = _json_int(_require(obj, "version", "capture"), "capture.version")
    if version != 2:
        raise DocumentError("capture.version must be 2")
    attempt_id = _hex64(_require(obj, "attempt_id", "capture"), "capture.attempt_id")
    provider = _exact_string(
        _require(obj, "provider", "capture"),
        HTTP_PROVIDER,
        "capture.provider",
    )
    adapter = _exact_string(
        _require(obj, "adapter_contract", "capture"),
        HTTP_ADAPTER_CONTRACT,
        "capture.adapter_contract",
    )
    transport_state = _require(obj, "transport_state", "capture")
    if transport_state not in {"response_complete", "response_partial", "no_response"}:
        raise DocumentError("capture.transport_state is invalid")
    request = _validate_http_request(_require(obj, "request", "capture"))
    request_fingerprint = _hex64(
        _require(obj, "request_fingerprint", "capture"),
        "capture.request_fingerprint",
    )
    if request_fingerprint != _expected_fingerprint(
        request, version=2, provider=provider, adapter_contract=adapter
    ):
        raise DocumentError("request_fingerprint does not match recompute")
    software = _validate_software(_require(obj, "software", "capture"))
    request_started_at = _timestamp(
        _require(obj, "request_started_at", "capture"),
        "capture.request_started_at",
    )
    response_headers_at = _optional_timestamp(
        _require(obj, "response_headers_at", "capture"),
        "capture.response_headers_at",
    )
    response_body_ended_at = _optional_timestamp(
        _require(obj, "response_body_ended_at", "capture"),
        "capture.response_body_ended_at",
    )
    transport_ended_at = _timestamp(
        _require(obj, "transport_ended_at", "capture"),
        "capture.transport_ended_at",
    )
    raw_response = _require(obj, "response", "capture")
    response = None if raw_response is None else _validate_http_response(raw_response)
    raw_failure = _require(obj, "transport_failure", "capture")
    transport_failure = (
        None if raw_failure is None else _validate_http_transport_failure(raw_failure)
    )
    _enforce_http_capture_branch(
        transport_state=str(transport_state),
        response_headers_at=response_headers_at,
        response_body_ended_at=response_body_ended_at,
        response=response,
        transport_failure=transport_failure,
    )
    _enforce_timestamp_order(
        request_started_at,
        response_headers_at,
        response_body_ended_at,
        transport_ended_at,
    )
    document: dict[str, object] = {
        "adapter_contract": adapter,
        "attempt_id": attempt_id,
        "provider": provider,
        "request": request,
        "request_fingerprint": request_fingerprint,
        "request_started_at": request_started_at,
        "response": response,
        "response_body_ended_at": response_body_ended_at,
        "response_headers_at": response_headers_at,
        "schema": schema,
        "software": software,
        "transport_ended_at": transport_ended_at,
        "transport_failure": transport_failure,
        "transport_state": transport_state,
        "version": version,
    }
    if attempt is not None:
        _enforce_parent_attempt(document, attempt)
    return document
