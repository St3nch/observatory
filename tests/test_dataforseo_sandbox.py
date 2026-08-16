"""PF-02: DataForSEO sandbox transport gate, mock branches, and loopback."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import socket
import threading
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import httpx
import pytest

from observatory.capture_event import (
    HTTP_ADAPTER_CONTRACT,
    DocumentError,
    canonical_json,
    content_digest,
    http_attempt_document,
    validate_attempt,
    validate_http_parameters,
)
from observatory.dataforseo_sandbox import (
    MAX_RESPONSE_BODY_BYTES,
    SandboxCaptureInputs,
    _exchange,
    _issue_verified_attempt,
    _run_gated_capture,
    _VerifiedAttempt,
    capture_dataforseo_sandbox,
    closed_sandbox_parameters,
    main,
    request_body_bytes,
)
from observatory.evidence import scrub_store
from observatory.evidence_store import EvidenceStore, StoreError, create_store
from observatory.settings import (
    DATAFORSEO_LOGIN_ENV,
    DATAFORSEO_PASSWORD_ENV,
    CredentialError,
    DataForSEOCredentials,
    Settings,
    load_dataforseo_credentials,
)

SENTINEL_LOGIN = "sentinel-login-pf02-aa11"
SENTINEL_PASSWORD = "sentinel-password-pf02-bb22"
SENTINEL_BASIC = "Basic " + base64.b64encode(
    f"{SENTINEL_LOGIN}:{SENTINEL_PASSWORD}".encode()
).decode("ascii")

HTTP_REQUEST_BODY = (
    b'[{"depth":10,"device":"desktop","keyword":"observatory test",'
    b'"language_code":"en","location_code":2840,"os":"windows"}]'
)
HTTP_REQUEST_BODY_SHA256 = "d10484d2237e4b08e37a4f3fe66bd678a3dbc2dab96f9b712af1b858b8d6d070"
V1_AR_ATTEMPT_ID = "46d5fb97c109b9f64a42ff3a5e62978e2c25551d6b7274603fc88456acfd9a0f"
V1_AR_ATTEMPT = (
    b'{"adapter_contract":"fixture-panel-v1","attempt_nonce":'
    b'"0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",'
    b'"authorized_at":"2026-08-11T20:15:30.123456Z",'
    b'"parameters":{"contract":"fixture-panel-v1","depth":2,'
    b'"panel_id":"panel-alpha","scenario":"admitted_results",'
    b'"subject_key":"subject-one"},"policy":{"mode":"fixture_no_spend",'
    b'"policy_version":"fixture-v1"},"provider":"fixture","request":'
    b'{"body":{"body":{"bytes":124,"sha256":'
    b'"f16972cae6bea7a84acc0c6d0b181a2de3fabf7870663b1fb76f389aed4c38ec"},'
    b'"state":"present_nonempty"},"headers":[["content-type","application/json"]],'
    b'"host":"fixture-panel","method":"POST","path":"/v1/measure","port":null,'
    b'"query":[],"scheme":"fixture"},"request_fingerprint":'
    b'"d18682cc029a8db08b0b761b900db2c7c91f92a99087597281cbdbdaec70e88b",'
    b'"schema":"observatory.attempt-event","software":'
    b'{"observatory_version":"conformance-v1"},"version":1}'
)

KEYWORD = "observatory test"
LOCATION = 2840
LANGUAGE = "en"
NONCE = "3333333333333333333333333333333333333333333333333333333333333333"
AUTHORIZED_AT = "2026-08-14T20:00:00.000000Z"
SOFTWARE = "conformance-http-v2"
TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

COMPLETE_BODY = b'{"status_code":20000,"status_message":"Ok.","tasks":[]}'
DENYLIST = (
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
)


@pytest.fixture(autouse=True)
def _no_public_network(monkeypatch: pytest.MonkeyPatch) -> None:
    real = socket.create_connection

    def guarded(address: Any, *args: Any, **kwargs: Any) -> socket.socket:
        host = address[0] if isinstance(address, tuple) else address
        if host not in {"127.0.0.1", "::1"}:
            raise AssertionError(f"public-network request forbidden: {host}")
        return real(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", guarded)


@pytest.fixture(autouse=True)
def _isolate_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DATAFORSEO_LOGIN_ENV, raising=False)
    monkeypatch.delenv(DATAFORSEO_PASSWORD_ENV, raising=False)


def _credentials() -> DataForSEOCredentials:
    return DataForSEOCredentials(SENTINEL_LOGIN, SENTINEL_PASSWORD)


def _inputs() -> SandboxCaptureInputs:
    return SandboxCaptureInputs(
        keyword=KEYWORD,
        location_code=LOCATION,
        language_code=LANGUAGE,
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )


def _streamed_response(
    status: int,
    content: bytes,
    headers: list[tuple[str, str]] | None = None,
) -> httpx.Response:
    hdrs: list[tuple[str, str]] = list(headers or [])
    if not any(name.lower() == "content-length" for name, _ in hdrs):
        hdrs.append(("content-length", str(len(content))))
    return httpx.Response(status, headers=hdrs, stream=httpx.ByteStream(content))


def _mock_client(handler: Any) -> httpx.Client:
    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        trust_env=False,
        follow_redirects=False,
        timeout=httpx.Timeout(30.0),
    )
    client.headers.clear()
    return client


def _capture_mock(
    store: EvidenceStore,
    handler: Any,
    inputs: SandboxCaptureInputs | None = None,
) -> Any:
    client = _mock_client(handler)
    try:
        return _run_gated_capture(store, inputs or _inputs(), _credentials(), client=client)
    finally:
        client.close()


def _tree_bytes(root: Path) -> bytes:
    chunks: list[bytes] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            chunks.append(path.read_bytes())
    return b"\n".join(chunks)


def _assert_no_secrets(*surfaces: object) -> None:
    for surface in surfaces:
        text = surface if isinstance(surface, str) else repr(surface)
        assert SENTINEL_LOGIN not in text
        assert SENTINEL_PASSWORD not in text
        assert SENTINEL_BASIC not in text


# ===========================================================================
# Closed construction
# ===========================================================================


def test_closed_parameters_and_independent_jcs_request_bytes() -> None:
    parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=LOCATION, language_code=LANGUAGE
    )
    body = request_body_bytes(parameters)
    assert body == HTTP_REQUEST_BODY
    assert len(body) == 119
    assert hashlib.sha256(body).hexdigest() == HTTP_REQUEST_BODY_SHA256
    task = json.loads(body)
    assert isinstance(task, list) and len(task) == 1
    assert task[0]["depth"] == 10
    assert task[0]["device"] == "desktop"
    assert task[0]["os"] == "windows"
    assert "contract" not in task[0]


def test_fresh_nonce_shape_and_timestamp_format() -> None:
    from observatory.dataforseo_sandbox import _fresh_nonce, _utc_now

    nonce = _fresh_nonce()
    assert HEX64_RE.fullmatch(nonce)
    assert _fresh_nonce() != nonce
    stamp = _utc_now()
    assert TIMESTAMP_RE.fullmatch(stamp)


def test_caller_cannot_override_fixed_depth_device_os() -> None:
    parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=LOCATION, language_code=LANGUAGE
    )
    assert parameters["depth"] == 10
    assert parameters["device"] == "desktop"
    assert parameters["os"] == "windows"
    with pytest.raises(DocumentError):
        validate_http_parameters({**parameters, "depth": 11})


# ===========================================================================
# Structural gate
# ===========================================================================


def test_forged_capability_cannot_reach_send() -> None:
    with pytest.raises(TypeError, match="cannot construct"):
        _VerifiedAttempt()
    forged: Any = object.__new__(_VerifiedAttempt)
    object.__setattr__(forged, "attempt_id", "0" * 64)
    object.__setattr__(forged, "document", {"adapter_contract": HTTP_ADAPTER_CONTRACT})
    object.__setattr__(forged, "request_body", HTTP_REQUEST_BODY)
    object.__setattr__(forged, "_used", False)
    with pytest.raises(TypeError, match="verified committed Attempt"):
        _exchange(forged, _credentials())


def test_subclassed_store_cannot_issue(tmp_path: Path) -> None:
    class LyingStore(EvidenceStore):
        def commit_attempt(
            self, document: Mapping[str, object], *, request_body: bytes | None
        ) -> str:
            raise AssertionError("lying store must not commit")

    parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=LOCATION, language_code=LANGUAGE
    )
    document = http_attempt_document(
        parameters=parameters,
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )
    with pytest.raises(TypeError, match="concrete EvidenceStore"):
        _issue_verified_attempt(LyingStore(tmp_path / "lie"), document, HTTP_REQUEST_BODY)


def test_failed_commit_prevents_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    sent: list[object] = []

    def boom(*_args: object, **_kwargs: object) -> str:
        raise StoreError("commit failed")

    def spy(*_args: object, **_kwargs: object) -> object:
        sent.append("sent")
        raise AssertionError("send must not run")

    monkeypatch.setattr(store, "commit_attempt", boom)
    monkeypatch.setattr("observatory.dataforseo_sandbox._exchange", spy)
    with pytest.raises(StoreError, match="commit failed"):
        capture_dataforseo_sandbox(store, _inputs(), _credentials())
    assert sent == []
    assert store.list_committed_ids("attempts") == []


def test_failed_readback_prevents_send(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    sent: list[object] = []
    real_commit = store.commit_attempt

    def commit_then_hide(
        document: dict[str, object], *, request_body: bytes | None
    ) -> str:
        return real_commit(document, request_body=request_body)

    monkeypatch.setattr(store, "commit_attempt", commit_then_hide)
    monkeypatch.setattr(store, "read_attempt", lambda _id: None)

    def spy(*_args: object, **_kwargs: object) -> object:
        sent.append("sent")
        raise AssertionError("send must not run")

    monkeypatch.setattr("observatory.dataforseo_sandbox._exchange", spy)
    with pytest.raises(StoreError, match="not readable"):
        capture_dataforseo_sandbox(store, _inputs(), _credentials())
    assert sent == []


def test_wrong_adapter_paid_host_and_unknown_version_cannot_issue(
    tmp_path: Path,
) -> None:
    store = create_store(tmp_path / "evidence")
    parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=LOCATION, language_code=LANGUAGE
    )
    document = http_attempt_document(
        parameters=parameters,
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )
    paid = dict(document)
    raw_request = paid["request"]
    assert isinstance(raw_request, dict)
    request = dict(raw_request)
    request["host"] = "api.dataforseo.com"
    paid["request"] = request
    with pytest.raises((DocumentError, StoreError)):
        _issue_verified_attempt(store, paid, HTTP_REQUEST_BODY)
    paid_policy = dict(document)
    paid_policy["policy"] = {"mode": "paid", "policy_version": "dataforseo-sandbox-v1"}
    with pytest.raises((DocumentError, StoreError)):
        _issue_verified_attempt(store, paid_policy, HTTP_REQUEST_BODY)
    unknown = dict(document)
    unknown["version"] = 3
    with pytest.raises((DocumentError, StoreError)):
        _issue_verified_attempt(store, unknown, HTTP_REQUEST_BODY)
    fixture = validate_attempt(V1_AR_ATTEMPT)
    with pytest.raises((DocumentError, StoreError, TypeError)):
        _issue_verified_attempt(store, fixture, HTTP_REQUEST_BODY)
    assert store.list_committed_ids("attempts") == []


def test_issue_then_send_is_one_exchange(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return _streamed_response(200, COMPLETE_BODY)

    outcome = _capture_mock(store, handler)
    assert calls["n"] == 1
    assert len(store.list_committed_ids("attempts")) == 1
    assert len(store.list_committed_ids("captures")) == 1
    loaded = store.read_attempt(outcome.attempt_id)
    assert loaded is not None
    parameters = closed_sandbox_parameters(
        keyword=KEYWORD, location_code=LOCATION, language_code=LANGUAGE
    )
    document = http_attempt_document(
        parameters=parameters,
        attempt_nonce=NONCE,
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )
    verified = _issue_verified_attempt(
        store,
        http_attempt_document(
            parameters=parameters,
            attempt_nonce="4444444444444444444444444444444444444444444444444444444444444444",
            authorized_at="2026-08-14T20:00:01.000000Z",
            observatory_version=SOFTWARE,
        ),
        request_body_bytes(parameters),
    )
    client = _mock_client(handler)
    try:
        _exchange(verified, _credentials(), client=client)
        with pytest.raises(StoreError, match="one-exchange"):
            _exchange(verified, _credentials(), client=client)
    finally:
        client.close()
    frozen_request = document["request"]
    assert isinstance(frozen_request, dict)
    assert frozen_request["host"] == "sandbox.dataforseo.com"


# ===========================================================================
# Headers, credentials
# ===========================================================================


def test_mock_sent_headers_and_body_equation(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return _streamed_response(200, COMPLETE_BODY)

    _capture_mock(store, handler)
    assert len(seen) == 1
    request = seen[0]
    assert bytes(request.content) == HTTP_REQUEST_BODY
    items = [(k.lower(), v) for k, v in request.headers.multi_items()]
    names = [name for name, _ in items]
    assert names.count("accept") == 1
    assert names.count("accept-encoding") == 1
    assert names.count("user-agent") == 1
    assert ("accept", "application/json") in items
    assert ("accept-encoding", "identity") in items
    assert ("connection", "close") in items
    assert ("content-type", "application/json") in items
    assert ("user-agent", "observatory-dataforseo-v1") in items
    assert ("authorization", SENTINEL_BASIC) in items
    assert ("host", "sandbox.dataforseo.com") in items
    assert ("content-length", str(len(HTTP_REQUEST_BODY))) in items
    assert "transfer-encoding" not in names
    assert "cookie" not in names
    assert "proxy-authorization" not in names
    assert names.count("accept") == 1
    assert request.headers.get("user-agent") == "observatory-dataforseo-v1"


def test_credentials_absent_from_evidence_stdout_repr_and_exceptions(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = create_store(tmp_path / "evidence")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200,
            COMPLETE_BODY,
            headers=[("set-cookie", "sid=secret"), ("authorization", SENTINEL_BASIC)],
        )

    outcome = _capture_mock(store, handler)
    tree = _tree_bytes(store.root)
    assert SENTINEL_LOGIN.encode() not in tree
    assert SENTINEL_PASSWORD.encode() not in tree
    assert SENTINEL_BASIC.encode() not in tree
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, dict)
    assert ["authorization", SENTINEL_BASIC] not in response["headers"]
    creds = _credentials()
    _assert_no_secrets(creds, Settings(), load_dataforseo_credentials.__doc__)
    try:
        raise RuntimeError("transport exploded")
    except RuntimeError as exc:
        _assert_no_secrets(exc, repr(exc))
    captured = capsys.readouterr()
    _assert_no_secrets(captured.out, captured.err)


def test_missing_credentials_fail_before_attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = create_store(tmp_path / "evidence")
    monkeypatch.delenv(DATAFORSEO_LOGIN_ENV, raising=False)
    with pytest.raises(CredentialError):
        load_dataforseo_credentials()
    code = main(
        [
            "--evidence-root",
            str(store.root),
            "--keyword",
            KEYWORD,
            "--location-code",
            str(LOCATION),
            "--language-code",
            LANGUAGE,
        ]
    )
    assert code == 2
    assert store.list_committed_ids("attempts") == []


# ===========================================================================
# Deterministic mock branches
# ===========================================================================


def test_complete_nonempty_zero_byte_and_status_classes(tmp_path: Path) -> None:
    cases = (
        (200, COMPLETE_BODY),
        (200, b""),
        (302, b"moved"),
        (404, b"missing"),
        (500, b"failed"),
    )
    for index, (status, body) in enumerate(cases):
        store = create_store(tmp_path / f"case-{index}")

        def handler(
            request: httpx.Request, status: int = status, body: bytes = body
        ) -> httpx.Response:
            return _streamed_response(status, body)

        nonce = f"{index:064x}"
        inputs = SandboxCaptureInputs(
            keyword=KEYWORD,
            location_code=LOCATION,
            language_code=LANGUAGE,
            attempt_nonce=nonce,
            authorized_at=AUTHORIZED_AT,
            observatory_version=SOFTWARE,
        )
        outcome = _capture_mock(store, handler, inputs)
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "response_complete"
        assert capture["transport_failure"] is None
        response = capture["response"]
        assert isinstance(response, dict)
        assert response["status"] == status
        assert response["completeness"] == "complete"
        stored = store.read_capture_body(outcome.capture_id)
        assert stored == (body if body else b"")
        assert scrub_store(store) == []


def test_duplicate_retained_and_every_denylisted_header(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")
    secret_headers = [(name, f"secret-{name}") for name in DENYLIST]
    retained = [
        ("content-type", "application/json"),
        ("x-request-id", "one"),
        ("x-request-id", "two"),
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, COMPLETE_BODY, headers=retained + secret_headers)

    outcome = _capture_mock(store, handler)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    response = capture["response"]
    assert isinstance(response, dict)
    assert response["headers"][:3] == [
        ["content-type", "application/json"],
        ["x-request-id", "one"],
        ["x-request-id", "two"],
    ]
    assert ["content-type", "application/json"] in response["headers"]
    assert ["x-request-id", "one"] in response["headers"]
    assert ["x-request-id", "two"] in response["headers"]
    omitted = response["omitted_headers"]
    assert omitted == [{"count": 1, "name": name} for name in sorted(DENYLIST)]
    tree = _tree_bytes(store.root)
    for name in DENYLIST:
        assert f"secret-{name}".encode() not in tree


def test_connect_send_and_header_failures_are_no_response(tmp_path: Path) -> None:
    failures: list[BaseException] = [
        httpx.ConnectError("no"),
        httpx.ConnectTimeout("no"),
        httpx.WriteError("no"),
        httpx.WriteTimeout("no"),
        httpx.RemoteProtocolError("no"),
    ]
    for index, exc in enumerate(failures):
        store = create_store(tmp_path / f"fail-{index}")

        def handler(request: httpx.Request, exc: BaseException = exc) -> httpx.Response:
            raise exc

        inputs = SandboxCaptureInputs(
            keyword=KEYWORD,
            location_code=LOCATION,
            language_code=LANGUAGE,
            attempt_nonce=f"{index + 10:064x}",
            authorized_at=AUTHORIZED_AT,
            observatory_version=SOFTWARE,
        )
        outcome = _capture_mock(store, handler, inputs)
        capture = store.read_capture(outcome.capture_id)
        assert capture is not None
        assert capture["transport_state"] == "no_response"
        assert capture["response"] is None
        failure = capture["transport_failure"]
        assert isinstance(failure, dict)
        assert failure["phase"] != "receive_body"
        assert failure.get("message") is None
        dumped = json.dumps(capture["transport_failure"])
        assert "no" not in dumped
        assert store.read_attempt(outcome.attempt_id) is not None
        assert scrub_store(store) == []


def test_partial_body_read_failure(tmp_path: Path) -> None:
    store = create_store(tmp_path / "partial")

    class _RaisingStream(httpx.SyncByteStream):
        def __iter__(self) -> Iterator[bytes]:
            yield b'{"partial":'
            raise httpx.ReadError("cut")

    class PartialTransport(httpx.BaseTransport):
        def handle_request(self, request: httpx.Request) -> httpx.Response:
            return httpx.Response(
                200,
                headers=[("content-type", "application/json")],
                stream=_RaisingStream(),
            )

    client = httpx.Client(
        transport=PartialTransport(),
        trust_env=False,
        follow_redirects=False,
        timeout=httpx.Timeout(30.0),
    )
    client.headers.clear()
    try:
        outcome = _run_gated_capture(store, _inputs(), _credentials(), client=client)
    finally:
        client.close()
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_partial"
    failure = capture["transport_failure"]
    assert isinstance(failure, dict)
    assert failure["phase"] == "receive_body"
    assert store.read_capture_body(outcome.capture_id) == b'{"partial":'
    assert "cut" not in json.dumps(capture)


@pytest.mark.parametrize(
    ("size", "state"),
    [
        (MAX_RESPONSE_BODY_BYTES - 1, "response_complete"),
        (MAX_RESPONSE_BODY_BYTES, "response_complete"),
        (MAX_RESPONSE_BODY_BYTES + 1, "response_partial"),
    ],
)
def test_eight_mib_boundary(tmp_path: Path, size: int, state: str) -> None:
    store = create_store(tmp_path / f"bound-{size}")
    payload = b"x" * size

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, payload)

    inputs = SandboxCaptureInputs(
        keyword=KEYWORD,
        location_code=LOCATION,
        language_code=LANGUAGE,
        attempt_nonce=hashlib.sha256(str(size).encode()).hexdigest(),
        authorized_at=AUTHORIZED_AT,
        observatory_version=SOFTWARE,
    )
    outcome = _capture_mock(store, handler, inputs)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == state
    body = store.read_capture_body(outcome.capture_id)
    assert body is not None
    if state == "response_complete":
        assert len(body) == size
        assert capture["transport_failure"] is None
    else:
        assert len(body) == MAX_RESPONSE_BODY_BYTES
        failure = capture["transport_failure"]
        assert isinstance(failure, dict)
        assert failure == {"phase": "receive_body", "code": "read_failed"}


# ===========================================================================
# Loopback
# ===========================================================================


def _serve_once(response: bytes, recorded: dict[str, bytes]) -> tuple[int, threading.Thread]:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = int(sock.getsockname()[1])

    def run() -> None:
        try:
            conn, _ = sock.accept()
            with conn:
                data = bytearray()
                while b"\r\n\r\n" not in data:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data.extend(chunk)
                header_blob, rest = data.split(b"\r\n\r\n", 1)
                length = 0
                for line in header_blob.split(b"\r\n"):
                    if line.lower().startswith(b"content-length:"):
                        length = int(line.split(b":", 1)[1].strip())
                body = bytearray(rest)
                while len(body) < length:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    body.extend(chunk)
                recorded["raw"] = bytes(header_blob) + b"\r\n\r\n" + bytes(body)
                conn.sendall(response)
        finally:
            sock.close()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return port, thread


def _parse_raw_request(raw: bytes) -> tuple[dict[str, list[str]], bytes]:
    header_blob, body = raw.split(b"\r\n\r\n", 1)
    headers: dict[str, list[str]] = {}
    for line in header_blob.split(b"\r\n")[1:]:
        name, value = line.split(b":", 1)
        key = name.decode("iso-8859-1").lower()
        headers.setdefault(key, []).append(value.decode("iso-8859-1").strip())
    return headers, body


def test_loopback_on_wire_headers_body_and_single_request(tmp_path: Path) -> None:
    store = create_store(tmp_path / "loopback")
    recorded: dict[str, bytes] = {}
    payload = COMPLETE_BODY
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: "
        + str(len(payload)).encode()
        + b"\r\n"
        b"Set-Cookie: sid=loop\r\n"
        b"\r\n"
        + payload
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}{ '/v3/serp/google/organic/live/advanced' }"
    outcome = _run_gated_capture(
        store, _inputs(), _credentials(), endpoint=endpoint
    )
    thread.join(timeout=5)
    raw = recorded["raw"]
    headers, body = _parse_raw_request(raw)
    assert body == HTTP_REQUEST_BODY
    assert headers["content-length"] == [str(len(HTTP_REQUEST_BODY))]
    assert headers["accept"] == ["application/json"]
    assert headers["accept-encoding"] == ["identity"]
    assert headers["connection"] == ["close"]
    assert headers["content-type"] == ["application/json"]
    assert headers["user-agent"] == ["observatory-dataforseo-v1"]
    assert headers["authorization"] == [SENTINEL_BASIC]
    assert headers["host"] == [f"127.0.0.1:{port}"]
    assert set(headers) == {
        "accept",
        "accept-encoding",
        "authorization",
        "connection",
        "content-length",
        "content-type",
        "host",
        "user-agent",
    }
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_complete"
    assert store.read_capture_body(outcome.capture_id) == payload
    attempt = store.read_attempt(outcome.attempt_id)
    assert attempt is not None
    attempt_request = attempt["request"]
    assert isinstance(attempt_request, dict)
    assert attempt_request["host"] == "sandbox.dataforseo.com"
    assert scrub_store(store) == []
    assert SENTINEL_LOGIN.encode() not in _tree_bytes(store.root)


def test_loopback_truncated_body_is_partial(tmp_path: Path) -> None:
    store = create_store(tmp_path / "trunc")
    recorded: dict[str, bytes] = {}
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: application/json\r\n"
        b"Content-Length: 80\r\n"
        b"\r\n"
        b'{"truncated":'
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}/v3/serp/google/organic/live/advanced"
    outcome = _run_gated_capture(store, _inputs(), _credentials(), endpoint=endpoint)
    thread.join(timeout=5)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_partial"
    failure = capture["transport_failure"]
    assert isinstance(failure, dict)
    assert failure["phase"] == "receive_body"
    body = store.read_capture_body(outcome.capture_id)
    assert body == b'{"truncated":'
    assert store.read_attempt(outcome.attempt_id) is not None


def test_loopback_redirect_is_complete_and_not_followed(tmp_path: Path) -> None:
    store = create_store(tmp_path / "redir")
    recorded: dict[str, bytes] = {}
    response = (
        b"HTTP/1.1 302 Found\r\n"
        b"Location: https://sandbox.dataforseo.com/elsewhere\r\n"
        b"Content-Length: 0\r\n"
        b"\r\n"
    )
    port, thread = _serve_once(response, recorded)
    endpoint = f"http://127.0.0.1:{port}/v3/serp/google/organic/live/advanced"
    outcome = _run_gated_capture(store, _inputs(), _credentials(), endpoint=endpoint)
    thread.join(timeout=5)
    capture = store.read_capture(outcome.capture_id)
    assert capture is not None
    assert capture["transport_state"] == "response_complete"
    response_obj = capture["response"]
    assert isinstance(response_obj, dict)
    assert response_obj["status"] == 302
    assert capture["transport_failure"] is None


# ===========================================================================
# Commit, scrub, CLI, regressions
# ===========================================================================


def test_each_branch_commits_one_verified_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "evidence")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, COMPLETE_BODY)

    outcome = _capture_mock(store, handler)
    assert store.list_committed_ids("attempts") == [outcome.attempt_id]
    assert store.list_committed_ids("captures") == [outcome.capture_id]
    assert store.read_attempt(outcome.attempt_id) is not None
    assert store.read_capture(outcome.capture_id) is not None
    assert store.read_capture_body(outcome.capture_id) == COMPLETE_BODY
    assert scrub_store(store) == []


def test_event_v1_bytes_remain_unchanged() -> None:
    assert content_digest(V1_AR_ATTEMPT) == V1_AR_ATTEMPT_ID
    loaded = validate_attempt(V1_AR_ATTEMPT)
    assert loaded["version"] == 1
    assert canonical_json(loaded) == V1_AR_ATTEMPT


def test_cli_prints_only_ids(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    store_root = tmp_path / "cli"
    monkeypatch.setenv(DATAFORSEO_LOGIN_ENV, SENTINEL_LOGIN)
    monkeypatch.setenv(DATAFORSEO_PASSWORD_ENV, SENTINEL_PASSWORD)

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, COMPLETE_BODY)

    client = _mock_client(handler)

    def fake_run(
        store: EvidenceStore,
        inputs: SandboxCaptureInputs,
        credentials: DataForSEOCredentials,
    ) -> Any:
        return _run_gated_capture(store, inputs, credentials, client=client)

    monkeypatch.setattr(
        "observatory.dataforseo_sandbox.capture_dataforseo_sandbox", fake_run
    )
    code = main(
        [
            "--evidence-root",
            str(store_root),
            "--keyword",
            KEYWORD,
            "--location-code",
            str(LOCATION),
            "--language-code",
            LANGUAGE,
        ]
    )
    client.close()
    assert code == 0
    out = capsys.readouterr()
    assert out.out.startswith("attempt_id ")
    assert "capture_id " in out.out
    assert SENTINEL_LOGIN not in out.out
    assert SENTINEL_PASSWORD not in out.out
    assert COMPLETE_BODY.decode() not in out.out
    assert "status_message" not in out.out


def test_cli_rejects_credential_arguments(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        main(
            [
                "--evidence-root",
                str(tmp_path),
                "--keyword",
                KEYWORD,
                "--location-code",
                "2840",
                "--language-code",
                "en",
                "--login",
                SENTINEL_LOGIN,
            ]
        )


def test_public_api_has_no_url_or_header_injection(tmp_path: Path) -> None:
    import inspect

    signature = inspect.signature(capture_dataforseo_sandbox)
    assert "endpoint" not in signature.parameters
    assert "url" not in signature.parameters
    assert "headers" not in signature.parameters
    assert "client" not in signature.parameters


def _assert_endpoint_rejected(tmp_path: Path, endpoint: str) -> None:
    store = create_store(tmp_path / hashlib.sha256(endpoint.encode()).hexdigest()[:16])
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, COMPLETE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(StoreError):
            _run_gated_capture(
                store, _inputs(), _credentials(), endpoint=endpoint, client=client
            )
    finally:
        client.close()
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []


def test_paid_and_remote_endpoint_override_rejected_before_attempt(
    tmp_path: Path,
) -> None:
    _assert_endpoint_rejected(
        tmp_path, "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    )
    _assert_endpoint_rejected(
        tmp_path, "https://example.invalid/v3/serp/google/organic/live/advanced"
    )


def test_credential_echo_in_body_commits_no_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-body")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(200, SENTINEL_LOGIN.encode())

    with pytest.raises(StoreError) as raised:
        _capture_mock(store, handler)
    _assert_no_secrets(raised.value, repr(raised.value), str(raised.value))
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1
    tree = _tree_bytes(store.root)
    assert SENTINEL_LOGIN.encode() not in tree
    assert SENTINEL_PASSWORD.encode() not in tree
    assert SENTINEL_BASIC.encode() not in tree
    token = SENTINEL_BASIC.removeprefix("Basic ").encode()
    assert token not in tree


def test_credential_echo_in_retained_header_commits_no_capture(tmp_path: Path) -> None:
    store = create_store(tmp_path / "echo-header")
    token = SENTINEL_BASIC.removeprefix("Basic ")

    def handler(request: httpx.Request) -> httpx.Response:
        return _streamed_response(
            200, COMPLETE_BODY, headers=[("x-echo", token)]
        )

    with pytest.raises(StoreError) as raised:
        _capture_mock(store, handler)
    _assert_no_secrets(raised.value, repr(raised.value), str(raised.value))
    assert store.list_committed_ids("captures") == []
    assert len(store.list_committed_ids("attempts")) == 1
    tree = _tree_bytes(store.root)
    assert SENTINEL_LOGIN.encode() not in tree
    assert SENTINEL_PASSWORD.encode() not in tree
    assert SENTINEL_BASIC.encode() not in tree
    assert token.encode() not in tree


@pytest.mark.parametrize(
    ("login", "password"),
    [("", SENTINEL_PASSWORD), (SENTINEL_LOGIN, "")],
)
def test_direct_empty_credentials_fail_before_attempt(
    tmp_path: Path, login: str, password: str
) -> None:
    store = create_store(tmp_path / ("empty-" + hashlib.sha256(login.encode()).hexdigest()[:8]))
    calls: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return _streamed_response(200, COMPLETE_BODY)

    client = _mock_client(handler)
    try:
        with pytest.raises(CredentialError) as raised:
            empty = DataForSEOCredentials(login, password)
            _run_gated_capture(store, _inputs(), empty, client=client)
    finally:
        client.close()
    _assert_no_secrets(raised.value, repr(raised.value), str(raised.value))
    assert calls == []
    assert store.list_committed_ids("attempts") == []
    assert store.list_committed_ids("captures") == []
