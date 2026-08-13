"""Session-scoped real PostgreSQL. Fail closed; never skip."""

from __future__ import annotations

import os
import secrets
import socket
import subprocess
import time
import uuid
from collections.abc import Iterator

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo

IMAGE = "postgres:18-alpine"
USER = "observatory"
PASSWORD = "observatory"
ADMIN_DB = "observatory"


def _env_dsn() -> str | None:
    value = os.environ.get("OBSERVATORY_TEST_DATABASE_URL")
    return value if value else None


def _docker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["docker", *args], check=False, capture_output=True, text=True)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_ready(dsn: str, timeout: float = 90.0) -> None:
    deadline = time.monotonic() + timeout
    last: BaseException | None = None
    while time.monotonic() < deadline:
        try:
            with psycopg.connect(dsn, connect_timeout=2) as connection:
                connection.execute("SELECT 1")
            return
        except Exception as exc:
            last = exc
            time.sleep(0.2)
    raise RuntimeError(f"PostgreSQL did not become ready: {last}") from last


def _replace_dbname(dsn: str, dbname: str) -> str:
    info = conninfo_to_dict(dsn)
    info["dbname"] = dbname
    return make_conninfo("", **info)


def _start_container() -> tuple[str, str]:
    name = f"observatory-ce05-{os.getpid()}-{secrets.token_hex(4)}"
    port = _free_port()
    result = _docker(
        "run",
        "-d",
        "--rm",
        "--name",
        name,
        "-e",
        f"POSTGRES_USER={USER}",
        "-e",
        f"POSTGRES_PASSWORD={PASSWORD}",
        "-e",
        f"POSTGRES_DB={ADMIN_DB}",
        "-p",
        f"127.0.0.1:{port}:5432",
        IMAGE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "CE-05 requires real PostgreSQL. Failed to start "
            f"{IMAGE}: {result.stderr.strip() or result.stdout.strip()}"
        )
    return name, f"postgresql://{USER}:{PASSWORD}@127.0.0.1:{port}/{ADMIN_DB}"


@pytest.fixture(scope="session")
def postgres_admin_dsn() -> Iterator[str]:
    env = _env_dsn()
    if env is not None:
        try:
            _wait_ready(env)
        except RuntimeError as exc:
            pytest.fail(f"OBSERVATORY_TEST_DATABASE_URL is set but not reachable: {exc}")
        yield env
        return
    try:
        name, dsn = _start_container()
    except RuntimeError as exc:
        pytest.fail(str(exc))
    try:
        _wait_ready(dsn)
        yield dsn
    finally:
        _docker("stop", "-t", "2", name)


@pytest.fixture
def postgres_dsn(postgres_admin_dsn: str) -> Iterator[str]:
    dbname = "ce05_" + uuid.uuid4().hex
    with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    dsn = _replace_dbname(postgres_admin_dsn, dbname)
    try:
        yield dsn
    finally:
        with psycopg.connect(postgres_admin_dsn, autocommit=True) as admin:
            admin.execute(
                sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(dbname))
            )
