"""Fetch SOFR history and prepare normalized files for the project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.sofr import (
    prepare_sofr_data_bundle,
    prepare_sofr_data_bundle_from_excel,
    prepare_sofr_data_bundle_from_local_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch SOFR and prepare normalized project files")
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "data/raw/market/sofr"),
        help="Directory where SOFR files will be written",
    )
    parser.add_argument("--start-date", help="Optional SOFR download start date in YYYY-MM-DD format")
    parser.add_argument("--end-date", help="Optional SOFR download end date in YYYY-MM-DD format")
    parser.add_argument("--source-csv", help="Use an existing local SOFR history CSV instead of downloading")
    parser.add_argument("--source-excel", help="Use an existing local New York Fed SOFR Excel export instead of downloading")
    parser.add_argument(
        "--maturity-years",
        type=float,
        default=1.0 / 360.0,
        help="Year fraction used when mapping the latest SOFR fixing into a market quote",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.source_csv:
        outputs = prepare_sofr_data_bundle_from_local_csv(
            args.source_csv,
            args.output_dir,
            maturity_years=args.maturity_years,
        )
    elif args.source_excel:
        outputs = prepare_sofr_data_bundle_from_excel(
            args.source_excel,
            args.output_dir,
            maturity_years=args.maturity_years,
        )
    else:
        outputs = prepare_sofr_data_bundle(
            args.output_dir,
            cosd=args.start_date,
            coed=args.end_date,
            maturity_years=args.maturity_years,
        )
    print("SOFR crawler finished")
    for label, path in outputs.items():
        print(f"{label}: {path}")


if __name__ == "__main__":
    main()
