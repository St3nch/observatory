from __future__ import annotations

import argparse
import json

from .errors import ReadError
from .reader import coverage_blind_spot_read, evidence_lookup


def main() -> int:
    parser = argparse.ArgumentParser(description="Local fixture-only Observatory typed-read prototype")
    parser.add_argument("request_type", choices=["evidence_lookup", "coverage_blind_spot_read"])
    parser.add_argument("--caller", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--claim-intent", required=True)
    parser.add_argument("--evidence-id")
    args = parser.parse_args()
    try:
        if args.request_type == "evidence_lookup":
            if not args.evidence_id:
                raise ReadError("blocked_filter")
            payload = evidence_lookup(caller_class=args.caller, scope_id=args.scope, evidence_id=args.evidence_id, claim_intent=args.claim_intent)
        else:
            payload = coverage_blind_spot_read(caller_class=args.caller, scope_id=args.scope, claim_intent=args.claim_intent)
    except ReadError as exc:
        print(json.dumps(exc.as_payload(), sort_keys=True))
        return 2
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
