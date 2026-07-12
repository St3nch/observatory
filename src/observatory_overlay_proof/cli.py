from __future__ import annotations

import argparse

from .align import build_overlay_alignment_response, build_overlay_request, serialize_overlay_alignment_response
from .errors import OverlayProofError


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one synthetic local M17 overlay fixture.")
    parser.add_argument("fixture")
    args = parser.parse_args()
    try:
        response = build_overlay_alignment_response(build_overlay_request(args.fixture))
    except OverlayProofError as exc:
        print(f"blocked: {exc.code}")
        return 2
    print(serialize_overlay_alignment_response(response))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
