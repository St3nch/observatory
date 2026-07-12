from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Mapping

from .campaign import CAMPAIGN_APPROVAL_REFERENCE, get_recipe
from .core import EVIDENCE_ROOT, ProbeBlocked, credentials_present, redact_text, utc_now, write_json
from .evidence_package import create_review_package, update_campaign_index

API_BASE_URL = "https://api.dataforseo.com"
LIVE_RECIPE_ID = "C00"
EXPECTED_PRICE_USD = Decimal("0.002")
REQUEST_TIMEOUT_SECONDS = 30
LIVE_EXECUTION_IMPLEMENTED = True
LIVE_EXECUTION_AUTHORIZED = True
OWNER_CONFIRMATION_PHRASE = "AUTHORIZE ONE PAID C00 REQUEST"
REPLACEMENT_CONFIRMATION_PHRASE = "AUTHORIZE ONE REPLACEMENT PAID C00 REQUEST AFTER NON-BILLABLE 401 INCIDENT"
REPLACEMENT_INCIDENT_PROBE_ID = "2026-07-12_C00_143020Z-f0b5410c"
ATTEMPT_REGISTRY_PATH = EVIDENCE_ROOT / "attempt-registry.json"


@dataclass(frozen=True)
class TransportResponse:
    status: int
    body: bytes
    headers: Mapping[str, str]


Transport = Callable[[urllib.request.Request, int], TransportResponse]


def _default_transport(request: urllib.request.Request, timeout: int) -> TransportResponse:
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS provider URL
        return TransportResponse(
            status=int(response.status),
            body=response.read(),
            headers=dict(response.headers.items()),
        )


def credential_state(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    return {
        "credentials_present": credentials_present(source),
        "credential_names": ["DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"],
        "credential_values_recorded": False,
    }


def build_live_preflight(
    *,
    env: Mapping[str, str] | None = None,
    exact_price_usd: Decimal = EXPECTED_PRICE_USD,
    account_limits_recorded: bool,
    evidence_root_ignored: bool,
    duplicate_exists: bool,
    replacement_allowed: bool = False,
    owner_confirmation: str | None = None,
) -> dict[str, Any]:
    recipe = get_recipe(LIVE_RECIPE_ID)
    blockers: list[str] = []
    if recipe.live_status != "promoted_for_preflight":
        blockers.append("recipe_not_promoted")
    if exact_price_usd != EXPECTED_PRICE_USD:
        blockers.append("exact_price_mismatch")
    if exact_price_usd > recipe.conservative_request_ceiling_usd:
        blockers.append("price_ceiling_exceeded")
    if not account_limits_recorded:
        blockers.append("account_limits_not_recorded")
    if not evidence_root_ignored:
        blockers.append("evidence_root_not_git_ignored")
    replacement_requested = owner_confirmation == REPLACEMENT_CONFIRMATION_PHRASE
    if duplicate_exists and not (replacement_requested and replacement_allowed):
        blockers.append("duplicate_request_detected")
    if replacement_requested and not duplicate_exists:
        blockers.append("replacement_incident_not_present")
    if replacement_requested and duplicate_exists and not replacement_allowed:
        blockers.append("replacement_request_not_authorized_by_incident_state")
    if not credentials_present(env):
        blockers.append("credentials_missing")
    if owner_confirmation not in {OWNER_CONFIRMATION_PHRASE, REPLACEMENT_CONFIRMATION_PHRASE}:
        blockers.append("owner_paid_request_confirmation_missing")
    if not LIVE_EXECUTION_IMPLEMENTED:
        blockers.append("live_execution_not_implemented")
    if not LIVE_EXECUTION_AUTHORIZED:
        blockers.append("network_execution_not_authorized")
    return {
        "status": "ready" if not blockers else "blocked",
        "blockers": blockers,
        "recipe_id": recipe.recipe_id,
        "campaign_approval_reference": CAMPAIGN_APPROVAL_REFERENCE,
        "endpoint": recipe.endpoint,
        "request_sha256": recipe.request_sha256(),
        "duplicate_prevention_key": recipe.duplicate_key(),
        "expected_price_usd": str(exact_price_usd),
        "conservative_request_ceiling_usd": str(recipe.conservative_request_ceiling_usd),
        "api_request_ceiling": 1,
        "billable_task_ceiling": 1,
        "retry_ceiling": 0,
        "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "credentials_present": credentials_present(env),
        "network_execution_authorized": LIVE_EXECUTION_AUTHORIZED,
        "replacement_requested": replacement_requested,
        "replacement_allowed": replacement_allowed,
        "replacement_incident_probe_id": REPLACEMENT_INCIDENT_PROBE_ID if replacement_requested else None,
        "generated_at": utc_now().isoformat(),
    }


def _load_attempt_registry(path: Path = ATTEMPT_REGISTRY_PATH) -> dict[str, Any]:
    if not path.is_file():
        return {"version": "1", "attempts": []}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ProbeBlocked("attempt registry cannot be read safely") from exc
    if not isinstance(value, dict) or not isinstance(value.get("attempts"), list):
        raise ProbeBlocked("attempt registry has an invalid shape")
    return value


def duplicate_attempt_exists(path: Path = ATTEMPT_REGISTRY_PATH) -> bool:
    key = get_recipe(LIVE_RECIPE_ID).duplicate_key()
    registry = _load_attempt_registry(path)
    return any(isinstance(item, dict) and item.get("duplicate_prevention_key") == key for item in registry["attempts"])


def replacement_attempt_allowed(path: Path = ATTEMPT_REGISTRY_PATH) -> bool:
    key = get_recipe(LIVE_RECIPE_ID).duplicate_key()
    registry = _load_attempt_registry(path)
    incident_ok = any(
        isinstance(item, dict)
        and item.get("probe_id") == REPLACEMENT_INCIDENT_PROBE_ID
        and item.get("duplicate_prevention_key") == key
        and item.get("status") == "provider_authentication_error"
        and item.get("http_status") == 401
        and item.get("retry_permitted") is False
        for item in registry["attempts"]
    )
    replacement_already_recorded = any(
        isinstance(item, dict) and item.get("replacement_for") == REPLACEMENT_INCIDENT_PROBE_ID
        for item in registry["attempts"]
    )
    return incident_ok and not replacement_already_recorded


def reserve_attempt(
    probe_id: str,
    path: Path = ATTEMPT_REGISTRY_PATH,
    replacement_for: str | None = None,
) -> dict[str, Any]:
    recipe = get_recipe(LIVE_RECIPE_ID)
    registry = _load_attempt_registry(path)
    duplicate_recorded = any(
        isinstance(item, dict) and item.get("duplicate_prevention_key") == recipe.duplicate_key()
        for item in registry["attempts"]
    )
    if duplicate_recorded and not (
        replacement_for == REPLACEMENT_INCIDENT_PROBE_ID and replacement_attempt_allowed(path)
    ):
        raise ProbeBlocked("duplicate C00 attempt already recorded")
    record = {
        "probe_id": probe_id,
        "recipe_id": recipe.recipe_id,
        "request_sha256": recipe.request_sha256(),
        "duplicate_prevention_key": recipe.duplicate_key(),
        "reserved_at": utc_now().isoformat(),
        "status": "reserved_before_transport",
        "retry_permitted": False,
    }
    if replacement_for is not None:
        record["replacement_for"] = replacement_for
        record["replacement_authorization"] = REPLACEMENT_CONFIRMATION_PHRASE
    registry["attempts"].append(record)
    write_json(path, registry)
    return record


def _authorization_header(env: Mapping[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    login = source.get("DATAFORSEO_LOGIN", "")
    password = source.get("DATAFORSEO_PASSWORD", "")
    if not login or not password:
        raise ProbeBlocked("DataForSEO credentials are missing")
    token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def build_http_request(env: Mapping[str, str] | None = None) -> urllib.request.Request:
    recipe = get_recipe(LIVE_RECIPE_ID)
    body = json.dumps(recipe.request(), separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return urllib.request.Request(
        f"{API_BASE_URL}{recipe.endpoint}",
        data=body,
        headers={
            "Authorization": _authorization_header(env),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Observatory-M13-C00/0.1",
        },
        method="POST",
    )


def _safe_suffix(now: datetime) -> str:
    return f"{now.astimezone(timezone.utc):%H%M%SZ}-{get_recipe(LIVE_RECIPE_ID).request_sha256()[:8]}"


def execute_one_c00(
    *,
    owner_confirmation: str,
    env: Mapping[str, str] | None = None,
    account_limits_recorded: bool,
    evidence_root_ignored: bool,
    transport: Transport = _default_transport,
    now: datetime | None = None,
    registry_path: Path = ATTEMPT_REGISTRY_PATH,
) -> dict[str, Any]:
    captured_at = utc_now() if now is None else now
    if captured_at.tzinfo is None:
        raise ProbeBlocked("execution timestamp must be timezone-aware")
    duplicate_exists = duplicate_attempt_exists(registry_path)
    replacement_allowed = replacement_attempt_allowed(registry_path)
    preflight = build_live_preflight(
        env=env,
        account_limits_recorded=account_limits_recorded,
        evidence_root_ignored=evidence_root_ignored,
        duplicate_exists=duplicate_exists,
        replacement_allowed=replacement_allowed,
        owner_confirmation=owner_confirmation,
    )
    if preflight["status"] != "ready":
        raise ProbeBlocked("live preflight blocked: " + ",".join(preflight["blockers"]))

    recipe = get_recipe(LIVE_RECIPE_ID)
    suffix = _safe_suffix(captured_at)
    probe_id = f"{captured_at.astimezone(timezone.utc):%Y-%m-%d}_{recipe.recipe_id}_{suffix}"
    replacement_for = (
        REPLACEMENT_INCIDENT_PROBE_ID
        if owner_confirmation == REPLACEMENT_CONFIRMATION_PHRASE
        else None
    )
    reserve_attempt(probe_id, registry_path, replacement_for=replacement_for)
    request = build_http_request(env)

    try:
        response = transport(request, REQUEST_TIMEOUT_SECONDS)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ProbeBlocked(redact_text(f"provider HTTP error {exc.code}: {body[:500]}")) from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ProbeBlocked(redact_text(f"provider transport failure: {exc}")) from exc

    if response.status < 200 or response.status >= 300:
        raise ProbeBlocked(f"provider returned unexpected HTTP status {response.status}")
    try:
        payload = json.loads(response.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProbeBlocked("provider response was not valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise ProbeBlocked("provider response JSON was not an object")

    package = create_review_package(
        LIVE_RECIPE_ID,
        payload,
        captured_at,
        EXPECTED_PRICE_USD,
        suffix,
    )
    cost_path = EVIDENCE_ROOT / package["probe_id"] / "06-cost-reconciliation.json"
    cost = json.loads(cost_path.read_text(encoding="utf-8"))
    index = update_campaign_index(
        {
            "probe_id": package["probe_id"],
            "recipe_id": LIVE_RECIPE_ID,
            "endpoint": recipe.endpoint,
            "captured_at": captured_at.astimezone(timezone.utc).isoformat(),
            "status": "captured_pending_review",
            "cost_usd": cost.get("conservative_cost_usd"),
            "raw_state": "captured_pending_purge",
            "review_status": "pending",
        }
    )
    return {
        "status": "captured_pending_review",
        "probe_id": package["probe_id"],
        "probe_root": package["probe_root"],
        "request_count": 1,
        "retry_count": 0,
        "http_status": response.status,
        "campaign_pull_count": len(index["pulls"]),
        "credentials_recorded": False,
    }

