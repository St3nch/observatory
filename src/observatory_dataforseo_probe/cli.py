from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .campaign import campaign_budget_summary, get_recipe, list_recipes, validate_catalog
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
