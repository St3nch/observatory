from __future__ import annotations

import argparse

from .fixtures import SEARCHCLARITY_SCOPE
from .models import ALLOWED_OUTPUT_USE, CONTRACT_VERSION
from .report_support import build_report_support_pack, build_report_support_request, serialize_report_support_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one synthetic M15 SearchClarity report-support proof request.")
    parser.add_argument("--evidence-id", default="ev_f19b6e40")
    parser.add_argument("--claim-intent", default="historical_observation")
    args = parser.parse_args()
    request = build_report_support_request(
        contract_version=CONTRACT_VERSION,
        request_id="m15_cli_fixture",
        request_type="report_support_evidence_lookup",
        scope_id=SEARCHCLARITY_SCOPE,
        claim_intent=args.claim_intent,
        current_or_historical_use="historical" if args.claim_intent == "historical_observation" else "current",
        requested_evidence_families=("controlled_public_manual",),
        freshness_requirement="fixture_contract_only",
        report_support_purpose_code="synthetic_contract_proof",
        allowed_output_use=ALLOWED_OUTPUT_USE,
        evidence_id=args.evidence_id,
    )
    print(serialize_report_support_pack(build_report_support_pack(request)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
