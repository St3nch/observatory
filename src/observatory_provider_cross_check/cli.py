from __future__ import annotations

import argparse

from .compare import build_cross_check_request, build_provider_cross_check, serialize_provider_cross_check
from .fixtures import SIDES, SCOPE_A


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local synthetic M16 cross-check fixture proof.")
    parser.add_argument("side_ids", nargs="*", default=["rank_a", "rank_b"])
    args = parser.parse_args()
    request = build_cross_check_request(
        request_id="m16_cli_fixture",
        scope_id=SCOPE_A,
        side_ids=args.side_ids,
    )
    print(serialize_provider_cross_check(build_provider_cross_check(request, SIDES)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
