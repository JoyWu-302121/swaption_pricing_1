"""Run a first-stage market-validation workflow using the UST yield-curve proxy."""

from pathlib import Path

from swaption_pricing.data_loader import load_curve_points_csv, load_swaption_spec_csv
from swaption_pricing.market_validation import curve_node_rows, discount_factor_rows, load_json_metadata, trade_summary


def main():
    project_root = Path(__file__).resolve().parent.parent
    curve_csv = project_root / "data/raw/market/ust_yield_curve_proxy/curve_points.csv"
    metadata_json = project_root / "data/raw/market/ust_yield_curve_proxy/ust_yield_curve_snapshot.json"
    spec_csv = project_root / "data/raw/example/swaption_spec.csv"

    curve = load_curve_points_csv(curve_csv)
    spec = load_swaption_spec_csv(spec_csv)
    metadata = load_json_metadata(metadata_json)

    print("Market Curve Validation")
    print(f"Snapshot date: {metadata.get('yield_curve_date')}")
    print(f"Proxy source:  ustreasuryyieldcurve.com")
    print("\nCurve Nodes")
    for row in curve_node_rows(curve):
        print(f"  maturity={row['maturity']:>6.4f}y  zero_rate={row['zero_rate']:.6f}")

    print("\nDiscount Factors")
    for row in discount_factor_rows(curve):
        print(
            f"  maturity={row['maturity']:>6.4f}y  "
            f"zero_rate={row['zero_rate']:.6f}  "
            f"df={row['discount_factor']:.6f}"
        )

    summary = trade_summary(curve, spec, black_vol=0.20)
    print("\nRepresentative Trade Summary")
    for key, value in summary.items():
        if isinstance(value, float):
            print(f"  {key}: {value:,.6f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
