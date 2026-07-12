from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

PROVIDER = "DataForSEO"
ENDPOINT = "/v3/serp/google/organic/live/advanced"
METHOD = "POST"
RECIPE_ID = "m13-dataforseo-serp-probe-v0-1"
APPROVAL_REFERENCE = "decisions/2026-07-11-m13-dataforseo-controlled-probe-approval.md"
MAXIMUM_EXPECTED_COST = 0.10
BILLABLE_TASK_CEILING = 1
API_REQUEST_CEILING = 1
RETRY_CEILING = 0
POLLING_CEILING = 0
REPEAT_CEILING = 0
NETWORK_EXECUTION_AUTHORIZED = False
EVIDENCE_ROOT = Path("probe-evidence") / "dataforseo"
CREDENTIAL_NAMES = ("DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD")
RAW_RETENTION_DAYS = 7

_REQUEST: dict[str, Any] = {
    "keyword": "observatory test page",
    "location_code": 2840,
    "language_code": "en",
    "device": "desktop",
    "os": "windows",
    "depth": 10,
}
_ALLOWED_REQUEST_KEYS = frozenset(_REQUEST)
_RESPONSE_CLASSES = {
    "normal_provider_response",
    "provider_authentication_error",
    "provider_request_error",
    "provider_throttle_or_limit",
    "provider_error_shape",
    "unknown_shape",
    "local_transport_failure",
    "local_evidence_failure",
}


class ProbeBlocked(RuntimeError):
    """Raised when a fail-closed probe gate blocks progress."""


@dataclass(frozen=True)
class PreflightInputs:
    decision_accepted: bool
    implementation_authorized: bool
    funding_authorized: bool
    network_authorized: bool
    exact_price: float | None
    account_limits_recorded: bool
    duplicate_exists: bool
    evidence_root_ignored: bool
    credentials_present: bool
    request_count: int = 1
    billable_task_count: int = 1
    retries: int = 0
    polling_requests: int = 0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_request() -> list[dict[str, Any]]:
    """Return a defensive copy of the only allowed provider request."""
    return [dict(_REQUEST)]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def request_sha256() -> str:
    return sha256_text(canonical_json(canonical_request()))


def duplicate_key() -> str:
    material = {
        "provider": PROVIDER,
        "endpoint": ENDPOINT,
        "request_payload_sha256": request_sha256(),
        "approval_reference": APPROVAL_REFERENCE,
    }
    return sha256_text(canonical_json(material))


def recipe_summary() -> dict[str, Any]:
    return {
        "provider": PROVIDER,
        "endpoint": ENDPOINT,
        "method": METHOD,
        "recipe_id": RECIPE_ID,
        "approval_reference": APPROVAL_REFERENCE,
        "request": canonical_request(),
        "request_sha256": request_sha256(),
        "duplicate_prevention_key": duplicate_key(),
        "maximum_expected_cost_usd": MAXIMUM_EXPECTED_COST,
        "billable_task_ceiling": BILLABLE_TASK_CEILING,
        "api_request_ceiling": API_REQUEST_CEILING,
        "retry_ceiling": RETRY_CEILING,
        "polling_ceiling": POLLING_CEILING,
        "repeat_ceiling": REPEAT_CEILING,
        "network_execution_authorized": NETWORK_EXECUTION_AUTHORIZED,
        "raw_retention_days": RAW_RETENTION_DAYS,
        "claim_use_warning": "provider_testimony_only_not_truth",
    }


def validate_request(candidate: Any) -> None:
    if not isinstance(candidate, list) or len(candidate) != 1:
        raise ProbeBlocked("request must contain exactly one task")
    task = candidate[0]
    if not isinstance(task, dict):
        raise ProbeBlocked("request task must be an object")
    if frozenset(task) != _ALLOWED_REQUEST_KEYS:
        raise ProbeBlocked("request contains missing, extra, or cost-bearing fields")
    if task != _REQUEST:
        raise ProbeBlocked("request differs from the accepted immutable recipe")


def credentials_present(env: Mapping[str, str] | None = None) -> bool:
    source = os.environ if env is None else env
    return all(bool(source.get(name)) for name in CREDENTIAL_NAMES)


def redact_text(value: str) -> str:
    redacted = value
    for name in CREDENTIAL_NAMES:
        secret = os.environ.get(name)
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    return redacted


def is_within_evidence_root(path: Path, root: Path | None = None) -> bool:
    active_root = EVIDENCE_ROOT if root is None else root
    try:
        path.resolve().relative_to(active_root.resolve())
        return True
    except ValueError:
        return False


def build_preflight(inputs: PreflightInputs, candidate_request: Any | None = None) -> dict[str, Any]:
    request = canonical_request() if candidate_request is None else candidate_request
    validate_request(request)

    blockers: list[str] = []
    if not inputs.decision_accepted:
        blockers.append("decision_not_accepted")
    if not inputs.implementation_authorized:
        blockers.append("implementation_not_authorized")
    if not inputs.funding_authorized:
        blockers.append("funding_not_authorized")
    if not inputs.network_authorized or not NETWORK_EXECUTION_AUTHORIZED:
        blockers.append("network_execution_not_authorized")
    if inputs.exact_price is None:
        blockers.append("exact_price_missing")
    elif inputs.exact_price > MAXIMUM_EXPECTED_COST:
        blockers.append("price_ceiling_exceeded")
    elif inputs.exact_price < 0:
        blockers.append("invalid_negative_price")
    if not inputs.account_limits_recorded:
        blockers.append("account_limits_not_recorded")
    if inputs.duplicate_exists:
        blockers.append("duplicate_request_detected")
    if not inputs.evidence_root_ignored:
        blockers.append("evidence_root_not_git_ignored")
    if not inputs.credentials_present:
        blockers.append("credentials_missing")
    if inputs.request_count != API_REQUEST_CEILING:
        blockers.append("api_request_count_invalid")
    if inputs.billable_task_count != BILLABLE_TASK_CEILING:
        blockers.append("billable_task_count_invalid")
    if inputs.retries != RETRY_CEILING:
        blockers.append("retry_count_invalid")
    if inputs.polling_requests != POLLING_CEILING:
        blockers.append("polling_count_invalid")

    return {
        "status": "blocked" if blockers else "ready",
        "blockers": blockers,
        "approval_reference": APPROVAL_REFERENCE,
        "recipe_id": RECIPE_ID,
        "request_payload_sha256": request_sha256(),
        "duplicate_prevention_key": duplicate_key(),
        "maximum_expected_cost_usd": MAXIMUM_EXPECTED_COST,
        "exact_price_usd": inputs.exact_price,
        "network_execution_authorized": NETWORK_EXECUTION_AUTHORIZED,
        "generated_at": utc_now().isoformat(),
    }


def assert_preflight_ready(preflight: Mapping[str, Any]) -> None:
    if preflight.get("status") != "ready":
        blockers = ",".join(str(x) for x in preflight.get("blockers", []))
        raise ProbeBlocked(f"preflight blocked: {blockers}")
    if not NETWORK_EXECUTION_AUTHORIZED:
        raise ProbeBlocked("network execution is disabled by accepted fixture-only authority")


def execute_request(*_: Any, **__: Any) -> None:
    """Permanent fixture-only guard until a later owner ruling changes source authority."""
    raise ProbeBlocked("network execution is not implemented or authorized")


def classify_response(payload: Any) -> str:
    if not isinstance(payload, dict):
        return "unknown_shape"
    status_code = payload.get("status_code")
    status_message = str(payload.get("status_message", "")).lower()
    tasks = payload.get("tasks")
    if status_code in {40100, 40101, 40102} or "auth" in status_message:
        return "provider_authentication_error"
    if status_code in {40200, 40201, 40202, 40203} or "limit" in status_message or "throttle" in status_message:
        return "provider_throttle_or_limit"
    if isinstance(status_code, int) and status_code >= 40000:
        return "provider_request_error"
    if not isinstance(tasks, list) or len(tasks) != 1:
        return "provider_error_shape"
    task = tasks[0]
    if not isinstance(task, dict):
        return "provider_error_shape"
    task_code = task.get("status_code")
    if isinstance(task_code, int) and task_code >= 40000:
        return "provider_error_shape"
    if "result" not in task:
        return "unknown_shape"
    return "normal_provider_response"


def _walk(value: Any, prefix: str = "$", paths: set[str] | None = None) -> set[str]:
    result = set() if paths is None else paths
    result.add(prefix)
    if isinstance(value, dict):
        for key in sorted(value):
            _walk(value[key], f"{prefix}.{key}", result)
    elif isinstance(value, list):
        for index, item in enumerate(value[:25]):
            _walk(item, f"{prefix}[{index}]", result)
    return result


def shape_fingerprint(payload: Any) -> dict[str, Any]:
    paths = sorted(_walk(payload))
    typed = []
    for path in paths:
        typed.append(path)
    return {
        "shape_fingerprint_version": "1",
        "field_path_count": len(paths),
        "field_path_set_sha256": sha256_text(canonical_json(paths)),
        "paths": paths,
    }


def summarize_payload(payload: Any) -> dict[str, Any]:
    response_class = classify_response(payload)
    if response_class != "normal_provider_response":
        raise ProbeBlocked(f"payload cannot be summarized as normal response: {response_class}")
    assert isinstance(payload, dict)
    task = payload["tasks"][0]
    fingerprint = shape_fingerprint(payload)
    return {
        "response_class": response_class,
        "top_level_keys": sorted(payload.keys()),
        "provider_status_code": payload.get("status_code"),
        "provider_status_message": payload.get("status_message"),
        "provider_top_level_cost": payload.get("cost"),
        "provider_task_level_cost": task.get("cost"),
        "task_status_code": task.get("status_code"),
        "task_status_message": task.get("status_message"),
        "shape_fingerprint": fingerprint,
        "claim_use_warning": "one_provider_payload_shape_not_schema_or_truth",
    }


def write_json(path: Path, value: Any) -> None:
    if not is_within_evidence_root(path):
        raise ProbeBlocked("evidence write target is outside approved root")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def purge_raw_payload(path: Path, probe_id: str, actor: str) -> dict[str, Any]:
    if not is_within_evidence_root(path):
        raise ProbeBlocked("purge target is outside approved evidence root")
    if not path.is_file():
        raise ProbeBlocked("raw payload does not exist")
    before_hash = hash_file(path)
    before_bytes = path.stat().st_size
    path.unlink()
    return {
        "probe_id": probe_id,
        "purged_at": utc_now().isoformat(),
        "purge_actor": actor,
        "purge_reason": "accepted_capture_and_purge_posture",
        "pre_purge_sha256": before_hash,
        "pre_purge_bytes": before_bytes,
        "payload_exists_after_purge": path.exists(),
    }


def retention_deadline(captured_at: datetime) -> datetime:
    if captured_at.tzinfo is None:
        raise ProbeBlocked("captured_at must be timezone-aware")
    return captured_at + timedelta(days=RAW_RETENTION_DAYS)


def validate_response_class(value: str) -> None:
    if value not in _RESPONSE_CLASSES:
        raise ProbeBlocked("unknown response class")
