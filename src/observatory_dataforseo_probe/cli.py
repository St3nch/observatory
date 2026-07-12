from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .campaign import campaign_budget_summary, get_recipe, list_recipes, validate_catalog
from .evidence_package import create_review_package, update_campaign_index
from .live_execution import (
    EXPECTED_PRICE_USD,
    build_live_preflight,
    duplicate_attempt_exists,
    execute_one_c00,
    replacement_attempt_allowed,
)
from .core import (
    EVIDENCE_ROOT,
    ProbeBlocked,
    PreflightInputs,
    build_preflight,
    canonical_request,
    execute_request,
    purge_raw_payload,
    recipe_summary,
    request_sha256,
    summarize_payload,
    write_json,
)


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def command_show_recipe(_: argparse.Namespace) -> int:
    _print(recipe_summary())
    return 0


def command_preflight(args: argparse.Namespace) -> int:
    inputs = PreflightInputs(
        decision_accepted=True,
        implementation_authorized=True,
        funding_authorized=False,
        network_authorized=False,
        exact_price=args.exact_price,
        account_limits_recorded=args.account_limits_recorded,
        duplicate_exists=args.duplicate_exists,
        evidence_root_ignored=args.evidence_root_ignored,
        credentials_present=False,
    )
    result = build_preflight(inputs)
    _print(result)
    return 0 if result["status"] == "ready" else 2


def command_execute(args: argparse.Namespace) -> int:
    if args.confirm_paid_request != request_sha256():
        raise ProbeBlocked("confirmation hash does not match immutable request")
    execute_request(canonical_request())
    return 0


def _probe_dir(probe_id: str) -> Path:
    if not probe_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in probe_id):
        raise ProbeBlocked("invalid probe id")
    return EVIDENCE_ROOT / probe_id


def command_summarize(args: argparse.Namespace) -> int:
    root = _probe_dir(args.probe_id)
    raw = root / "raw-response.json"
    if not raw.is_file():
        raise ProbeBlocked("raw response fixture does not exist")
    payload = json.loads(raw.read_text(encoding="utf-8"))
    summary = summarize_payload(payload)
    write_json(root / "field-summary.json", summary)
    _print(summary)
    return 0


def command_purge(args: argparse.Namespace) -> int:
    root = _probe_dir(args.probe_id)
    proof = purge_raw_payload(root / "raw-response.json", args.probe_id, args.actor)
    write_json(root / "purge-proof.json", proof)
    _print(proof)
    return 0


def command_campaign_list(_: argparse.Namespace) -> int:
    _print(list_recipes())
    return 0


def command_campaign_show(args: argparse.Namespace) -> int:
    _print(get_recipe(args.recipe_id).summary())
    return 0


def command_campaign_budget(_: argparse.Namespace) -> int:
    _print(campaign_budget_summary())
    return 0


def command_campaign_validate(_: argparse.Namespace) -> int:
    result = validate_catalog()
    _print(result)
    return 0 if result["valid"] else 2


def command_package_review(args: argparse.Namespace) -> int:
    raw_path = Path(args.raw_json)
    if not raw_path.is_file() or not raw_path.resolve().is_relative_to(EVIDENCE_ROOT.resolve()):
        raise ProbeBlocked("raw JSON must exist within the approved evidence root")
    try:
        expected_price = Decimal(args.expected_price)
        usage_cost = Decimal(args.usage_cost) if args.usage_cost is not None else None
        captured_at = datetime.fromisoformat(args.captured_at.replace("Z", "+00:00"))
    except (InvalidOperation, ValueError) as exc:
        raise ProbeBlocked("invalid price or captured-at value") from exc
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    result = create_review_package(
        args.recipe_id,
        payload,
        captured_at,
        expected_price,
        args.suffix,
        usage_cost,
    )
    _print(result)
    return 0


def command_campaign_index_add(args: argparse.Namespace) -> int:
    entry = {
        "probe_id": args.probe_id,
        "recipe_id": args.recipe_id,
        "endpoint": get_recipe(args.recipe_id).endpoint,
        "captured_at": args.captured_at,
        "status": args.status,
        "cost_usd": args.cost_usd,
        "raw_state": args.raw_state,
        "review_status": args.review_status,
    }
    _print(update_campaign_index(entry))
    return 0


def command_live_preflight(args: argparse.Namespace) -> int:
    try:
        exact_price = Decimal(args.exact_price)
    except InvalidOperation as exc:
        raise ProbeBlocked("invalid exact price") from exc
    result = build_live_preflight(
        exact_price_usd=exact_price,
        account_limits_recorded=args.account_limits_recorded,
        evidence_root_ignored=args.evidence_root_ignored,
        duplicate_exists=duplicate_attempt_exists(),
        replacement_allowed=replacement_attempt_allowed(),
        owner_confirmation=args.owner_confirmation,
    )
    _print(result)
    return 0 if result["status"] == "ready" else 2


def command_live_execute(args: argparse.Namespace) -> int:
    result = execute_one_c00(
        owner_confirmation=args.owner_confirmation,
        account_limits_recorded=args.account_limits_recorded,
        evidence_root_ignored=args.evidence_root_ignored,
    )
    _print(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fixture-only M13 DataForSEO probe safety cage")
    sub = parser.add_subparsers(dest="command", required=True)

    show = sub.add_parser("show-recipe")
    show.set_defaults(func=command_show_recipe)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--exact-price", type=float)
    preflight.add_argument("--account-limits-recorded", action="store_true")
    preflight.add_argument("--duplicate-exists", action="store_true")
    preflight.add_argument("--evidence-root-ignored", action="store_true")
    preflight.set_defaults(func=command_preflight)

    execute = sub.add_parser("execute")
    execute.add_argument("--confirm-paid-request", required=True)
    execute.set_defaults(func=command_execute)

    summarize = sub.add_parser("summarize")
    summarize.add_argument("--probe-id", required=True)
    summarize.set_defaults(func=command_summarize)

    purge = sub.add_parser("purge")
    purge.add_argument("--probe-id", required=True)
    purge.add_argument("--actor", required=True)
    purge.set_defaults(func=command_purge)

    campaign_list = sub.add_parser("campaign-list")
    campaign_list.set_defaults(func=command_campaign_list)

    campaign_show = sub.add_parser("campaign-show")
    campaign_show.add_argument("--recipe-id", required=True)
    campaign_show.set_defaults(func=command_campaign_show)

    campaign_budget = sub.add_parser("campaign-budget")
    campaign_budget.set_defaults(func=command_campaign_budget)

    campaign_validate = sub.add_parser("campaign-validate")
    campaign_validate.set_defaults(func=command_campaign_validate)

    package_review = sub.add_parser("package-review")
    package_review.add_argument("--recipe-id", required=True)
    package_review.add_argument("--raw-json", required=True)
    package_review.add_argument("--captured-at", required=True)
    package_review.add_argument("--expected-price", required=True)
    package_review.add_argument("--usage-cost")
    package_review.add_argument("--suffix", required=True)
    package_review.set_defaults(func=command_package_review)

    campaign_index = sub.add_parser("campaign-index-add")
    campaign_index.add_argument("--probe-id", required=True)
    campaign_index.add_argument("--recipe-id", required=True)
    campaign_index.add_argument("--captured-at", required=True)
    campaign_index.add_argument("--status", required=True)
    campaign_index.add_argument("--cost-usd", required=True)
    campaign_index.add_argument("--raw-state", required=True)
    campaign_index.add_argument("--review-status", required=True)
    campaign_index.set_defaults(func=command_campaign_index_add)

    live_preflight = sub.add_parser("live-preflight")
    live_preflight.add_argument("--exact-price", default=str(EXPECTED_PRICE_USD))
    live_preflight.add_argument("--account-limits-recorded", action="store_true")
    live_preflight.add_argument("--evidence-root-ignored", action="store_true")
    live_preflight.add_argument("--owner-confirmation")
    live_preflight.set_defaults(func=command_live_preflight)

    live_execute = sub.add_parser("live-execute")
    live_execute.add_argument("--account-limits-recorded", action="store_true")
    live_execute.add_argument("--evidence-root-ignored", action="store_true")
    live_execute.add_argument("--owner-confirmation", required=True)
    live_execute.set_defaults(func=command_live_execute)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return int(args.func(args))
    except (ProbeBlocked, json.JSONDecodeError, OSError) as exc:
        print(f"blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
