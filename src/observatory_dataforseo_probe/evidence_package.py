from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .campaign import CAMPAIGN_ID, get_recipe
from .core import EVIDENCE_ROOT, ProbeBlocked, canonical_json, is_within_evidence_root, sha256_text, utc_now, write_json

PACKAGE_VERSION = "1"
CAMPAIGN_INDEX_PATH = EVIDENCE_ROOT / "campaign-index.json"
CAMPAIGN_REVIEW_PATH = EVIDENCE_ROOT / "campaign-review.md"


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _safe_probe_id(recipe_id: str, captured_at: datetime, suffix: str) -> str:
    if captured_at.tzinfo is None:
        raise ProbeBlocked("captured_at must be timezone-aware")
    clean_suffix = "".join(ch for ch in suffix if ch.isalnum() or ch in "-_")
    if not clean_suffix:
        raise ProbeBlocked("probe suffix must contain a safe character")
    return f"{captured_at.astimezone(timezone.utc):%Y-%m-%d}_{recipe_id}_{clean_suffix}"


def build_request_manifest(recipe_id: str, captured_at: datetime, expected_price_usd: Decimal, suffix: str) -> dict[str, Any]:
    recipe = get_recipe(recipe_id)
    probe_id = _safe_probe_id(recipe_id, captured_at, suffix)
    return {
        "package_version": PACKAGE_VERSION,
        "campaign_id": CAMPAIGN_ID,
        "probe_id": probe_id,
        "recipe_id": recipe.recipe_id,
        "stage_id": recipe.stage_id,
        "provider": "DataForSEO",
        "family": recipe.family,
        "endpoint": recipe.endpoint,
        "method": recipe.method,
        "request": recipe.request(),
        "request_sha256": recipe.request_sha256(),
        "duplicate_prevention_key": recipe.duplicate_key(),
        "expected_price_usd": str(expected_price_usd),
        "conservative_request_ceiling_usd": str(recipe.conservative_request_ceiling_usd),
        "captured_at": captured_at.astimezone(timezone.utc).isoformat(),
        "raw_retention_class": recipe.retention_class,
        "rights_class": recipe.rights_class,
        "claim_use_warning": recipe.claim_use_warning,
    }


def _field_paths(value: Any, prefix: str) -> list[str]:
    paths: set[str] = set()

    def walk(current: Any, current_prefix: str) -> None:
        paths.add(current_prefix)
        if isinstance(current, dict):
            for key in sorted(current):
                walk(current[key], f"{current_prefix}.{key}")
        elif isinstance(current, list):
            for item in current[:25]:
                walk(item, f"{current_prefix}[]")

    walk(value, prefix)
    return sorted(paths)


def build_field_inventory(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbeBlocked("field inventory requires an object payload")
    tasks = payload.get("tasks")
    task = tasks[0] if isinstance(tasks, list) and len(tasks) == 1 and isinstance(tasks[0], dict) else {}
    results = task.get("result") if isinstance(task, dict) else None
    result_list = results if isinstance(results, list) else []
    items: list[Any] = []
    for result in result_list:
        if isinstance(result, dict) and isinstance(result.get("items"), list):
            items.extend(result["items"])

    sections = {
        "response": _field_paths({key: value for key, value in payload.items() if key != "tasks"}, "$.response"),
        "task": _field_paths({key: value for key, value in task.items() if key != "result"}, "$.task"),
        "result": _field_paths(result_list, "$.result"),
        "items": _field_paths(items, "$.items"),
    }
    all_paths = sorted({path for paths in sections.values() for path in paths})
    return {
        "field_inventory_version": "1",
        "section_counts": {name: len(paths) for name, paths in sections.items()},
        "sections": sections,
        "all_field_path_count": len(all_paths),
        "all_field_path_set_sha256": sha256_text(canonical_json(all_paths)),
    }


def build_item_type_summary(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbeBlocked("item summary requires an object payload")
    counts: Counter[str] = Counter()
    result_count = 0
    item_count = 0
    tasks = payload.get("tasks")
    if isinstance(tasks, list) and len(tasks) == 1 and isinstance(tasks[0], dict):
        results = tasks[0].get("result")
        if isinstance(results, list):
            result_count = len(results)
            for result in results:
                if not isinstance(result, dict):
                    continue
                items = result.get("items")
                if not isinstance(items, list):
                    continue
                for item in items:
                    item_count += 1
                    if isinstance(item, dict):
                        item_type = item.get("type")
                        counts[str(item_type) if item_type else "unknown"] += 1
                    else:
                        counts["unknown"] += 1
    return {
        "result_count": result_count,
        "item_count": item_count,
        "item_type_counts": dict(sorted(counts.items())),
        "unknown_item_type_count": counts.get("unknown", 0),
    }


def build_cost_reconciliation(expected_price_usd: Decimal, payload: Any, usage_sheet_cost_usd: Decimal | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProbeBlocked("cost reconciliation requires an object payload")
    tasks = payload.get("tasks")
    task = tasks[0] if isinstance(tasks, list) and len(tasks) == 1 and isinstance(tasks[0], dict) else {}
    top_cost = _decimal(payload.get("cost"))
    task_cost = _decimal(task.get("cost"))
    witnesses = [value for value in (top_cost, task_cost, usage_sheet_cost_usd) if value is not None]
    conservative = max(witnesses) if witnesses else None
    differences = {
        "top_level_minus_expected": str(top_cost - expected_price_usd) if top_cost is not None else None,
        "task_level_minus_expected": str(task_cost - expected_price_usd) if task_cost is not None else None,
        "usage_sheet_minus_expected": str(usage_sheet_cost_usd - expected_price_usd) if usage_sheet_cost_usd is not None else None,
    }
    status = "reconciled"
    if not witnesses:
        status = "missing_cost_witness"
    elif any(value != expected_price_usd for value in witnesses):
        status = "review_required"
    return {
        "expected_price_usd": str(expected_price_usd),
        "provider_top_level_cost_usd": str(top_cost) if top_cost is not None else None,
        "provider_task_level_cost_usd": str(task_cost) if task_cost is not None else None,
        "usage_sheet_cost_usd": str(usage_sheet_cost_usd) if usage_sheet_cost_usd is not None else None,
        "conservative_cost_usd": str(conservative) if conservative is not None else None,
        "differences": differences,
        "reconciliation_status": status,
    }


def build_review_notes(manifest: dict[str, Any], item_summary: dict[str, Any], cost_summary: dict[str, Any]) -> str:
    return (
        f"# {manifest['recipe_id']} Review\n\n"
        f"Probe: `{manifest['probe_id']}`  \n"
        f"Captured: `{manifest['captured_at']}`  \n"
        f"Endpoint: `{manifest['endpoint']}`\n\n"
        "## What this pull proved\n\n"
        "- [ ] Review pending.\n\n"
        "## Result and item shape\n\n"
        f"- Result records: `{item_summary['result_count']}`\n"
        f"- Items: `{item_summary['item_count']}`\n"
        f"- Item types: `{json.dumps(item_summary['item_type_counts'], sort_keys=True)}`\n\n"
        "## Cost result\n\n"
        f"- Expected: `${cost_summary['expected_price_usd']}`\n"
        f"- Conservative observed: `{cost_summary['conservative_cost_usd']}`\n"
        f"- Reconciliation: `{cost_summary['reconciliation_status']}`\n\n"
        "## New structures observed\n\n"
        "- [ ] Review field inventory.\n\n"
        "## Unexpected fields or behavior\n\n"
        "- None recorded yet.\n\n"
        "## Questions for the next pull\n\n"
        "- [ ] Add after review.\n\n"
        "## Promotion decision\n\n"
        "- [ ] Do not promote automatically.\n"
    )


def write_text(path: Path, text: str) -> None:
    if not is_within_evidence_root(path):
        raise ProbeBlocked("evidence write target is outside approved root")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def create_review_package(recipe_id: str, payload: Any, captured_at: datetime, expected_price_usd: Decimal, suffix: str, usage_sheet_cost_usd: Decimal | None = None) -> dict[str, Any]:
    manifest = build_request_manifest(recipe_id, captured_at, expected_price_usd, suffix)
    probe_root = EVIDENCE_ROOT / manifest["probe_id"]
    field_inventory = build_field_inventory(payload)
    item_summary = build_item_type_summary(payload)
    cost_summary = build_cost_reconciliation(expected_price_usd, payload, usage_sheet_cost_usd)
    response_summary = {
        "package_version": PACKAGE_VERSION,
        "probe_id": manifest["probe_id"],
        "provider_status_code": payload.get("status_code") if isinstance(payload, dict) else None,
        "provider_status_message": payload.get("status_message") if isinstance(payload, dict) else None,
        "task_status_code": payload.get("tasks", [{}])[0].get("status_code") if isinstance(payload, dict) and isinstance(payload.get("tasks"), list) and payload["tasks"] and isinstance(payload["tasks"][0], dict) else None,
        "task_status_message": payload.get("tasks", [{}])[0].get("status_message") if isinstance(payload, dict) and isinstance(payload.get("tasks"), list) and payload["tasks"] and isinstance(payload["tasks"][0], dict) else None,
        **item_summary,
        "cost_reconciliation_status": cost_summary["reconciliation_status"],
        "claim_use_warning": "provider_testimony_only_not_truth",
    }
    write_json(probe_root / "00-request-manifest.json", manifest)
    write_json(probe_root / "02-raw-response.json", payload)
    write_json(probe_root / "03-response-summary.json", response_summary)
    write_json(probe_root / "04-field-inventory.json", field_inventory)
    write_json(probe_root / "05-item-type-summary.json", item_summary)
    write_json(probe_root / "06-cost-reconciliation.json", cost_summary)
    write_text(probe_root / "07-review-notes.md", build_review_notes(manifest, item_summary, cost_summary))
    return {
        "probe_id": manifest["probe_id"],
        "probe_root": str(probe_root),
        "files_written": [
            "00-request-manifest.json",
            "02-raw-response.json",
            "03-response-summary.json",
            "04-field-inventory.json",
            "05-item-type-summary.json",
            "06-cost-reconciliation.json",
            "07-review-notes.md",
        ],
    }


def update_campaign_index(entry: dict[str, Any], index_path: Path | None = None, review_path: Path | None = None) -> dict[str, Any]:
    target_index = CAMPAIGN_INDEX_PATH if index_path is None else index_path
    target_review = CAMPAIGN_REVIEW_PATH if review_path is None else review_path
    if not is_within_evidence_root(target_index) or not is_within_evidence_root(target_review):
        raise ProbeBlocked("campaign index target is outside approved evidence root")
    existing: dict[str, Any] = {"campaign_id": CAMPAIGN_ID, "updated_at": None, "pulls": []}
    if target_index.is_file():
        existing = json.loads(target_index.read_text(encoding="utf-8"))
    pulls = [pull for pull in existing.get("pulls", []) if pull.get("probe_id") != entry.get("probe_id")]
    pulls.append(entry)
    pulls.sort(key=lambda value: (str(value.get("captured_at", "")), str(value.get("probe_id", ""))))
    updated = {"campaign_id": CAMPAIGN_ID, "updated_at": utc_now().isoformat(), "pulls": pulls}
    write_json(target_index, updated)
    lines = ["# DataForSEO Campaign Review", "", "| Probe | Recipe | Endpoint | Status | Cost | Raw state | Review |", "|---|---|---|---|---:|---|---|"]
    for pull in pulls:
        lines.append(
            f"| {pull.get('probe_id', '')} | {pull.get('recipe_id', '')} | {pull.get('endpoint', '')} | "
            f"{pull.get('status', '')} | {pull.get('cost_usd', '')} | {pull.get('raw_state', '')} | {pull.get('review_status', '')} |"
        )
    write_text(target_review, "\n".join(lines) + "\n")
    return updated
