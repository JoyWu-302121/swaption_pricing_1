"""Fetch a U.S. Treasury yield-curve proxy snapshot from ustreasuryyieldcurve.com."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.market import prepare_ust_yield_curve_proxy_bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch U.S. Treasury yield-curve proxy data")
    parser.add_argument("--date", required=True, help="Snapshot date in YYYY-MM-DD format")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "data/raw/market/ust_yield_curve_proxy"),
        help="Directory where normalized snapshot files will be written",
    )
    parser.add_argument("--offset", type=int, default=0, help="Optional API offset parameter")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    outputs = prepare_ust_yield_curve_proxy_bundle(
        date=args.date,
        output_dir=args.output_dir,
        offset=args.offset,
    )
    print("UST yield curve proxy fetch finished")
    for label, path in outputs.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
