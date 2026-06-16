"""Unified command-line entry point for the swaption pricing project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.black76 import price_swaption
from swaption_pricing.calibration import calibrate_sabr_to_vols
from swaption_pricing.data_loader import load_project_data
from swaption_pricing.risk import calculate_risk, compare_black_and_sabr_risk
from swaption_pricing.sabr import SabrParams, price_swaption_with_sabr, sabr_implied_volatility
from swaption_pricing.sofr import (
    prepare_sofr_data_bundle,
    prepare_sofr_data_bundle_from_local_csv,
    prepare_sofr_data_bundle_from_excel,
    download_sofr_history_csv,
    latest_sofr_observation,
    latest_sofr_observation_from_excel,
    write_sofr_market_quote_csv,
)
from swaption_pricing.swap import forward_swap_rate, swap_annuity


def run_pricing(args: argparse.Namespace) -> None:
    bundle = load_project_data(
        data_mode=args.data_mode,
        curve_csv=args.curve_csv,
        market_quotes_csv=args.market_quotes_csv,
        spec_csv=args.spec_csv,
        vol_slice_csv=args.vol_slice_csv,
        bootstrap_curve=args.bootstrap_curve,
    )
    curve = bundle.curve
    spec = bundle.spec
    vol = 0.20

    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    price = price_swaption(curve, spec, vol)
    risk = calculate_risk(curve, spec, vol)

    print("Swaption Example")
    print(f"Forward swap rate: {forward:.6f}")
    print(f"Swap annuity:      {annuity:.6f}")
    print(f"Price:             {price:,.2f}")
    print(f"PV01:              {risk.pv01:,.2f}")
    print(f"Vega:              {risk.vega:,.2f}")
    print(f"Theta:             {risk.theta:,.2f}")
    print(f"Data source:       {bundle.source}")


def run_comparison(args: argparse.Namespace) -> None:
    bundle = load_project_data(
        data_mode=args.data_mode,
        curve_csv=args.curve_csv,
        market_quotes_csv=args.market_quotes_csv,
        spec_csv=args.spec_csv,
        vol_slice_csv=args.vol_slice_csv,
        bootstrap_curve=args.bootstrap_curve,
    )
    curve = bundle.curve
    sabr_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    flat_black_vol = 0.20
    strikes = [quote.strike for quote in bundle.vol_slice] if bundle.vol_slice else [0.0350, 0.0400, 0.0450]

    print("Black vs SABR Comparison")
    print("Strike     Forward    FlatVolPx    SABRVol    SABRPx")

    for strike in strikes:
        spec = bundle.spec.__class__(
            notional=bundle.spec.notional,
            expiry=bundle.spec.expiry,
            tenor=bundle.spec.tenor,
            strike=strike,
            pay_frequency=bundle.spec.pay_frequency,
            option_type=bundle.spec.option_type,
        )
        forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
        black_price = price_swaption(curve, spec, flat_black_vol)
        sabr_price, sabr_vol = price_swaption_with_sabr(curve, spec, sabr_params)
        print(f"{strike:0.4f}     {forward:0.4f}     {black_price:10.2f}   {sabr_vol:0.4f}   {sabr_price:10.2f}")
    print(f"Data source: {bundle.source}")


def run_risk(args: argparse.Namespace) -> None:
    bundle = load_project_data(
        data_mode=args.data_mode,
        curve_csv=args.curve_csv,
        market_quotes_csv=args.market_quotes_csv,
        spec_csv=args.spec_csv,
        vol_slice_csv=args.vol_slice_csv,
        bootstrap_curve=args.bootstrap_curve,
    )
    curve = bundle.curve
    spec = bundle.spec
    result = compare_black_and_sabr_risk(
        curve=curve,
        spec=spec,
        black_vol=0.20,
        sabr_params=SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40),
    )

    print("Black vs SABR Risk Comparison")
    print(f"Black price: {result.black_price:,.2f} at vol {result.black_vol:.4f}")
    print(f"SABR price:  {result.sabr_price:,.2f} at implied vol {result.sabr_vol:.4f}")
    print(
        "Black risk: "
        f"PV01={result.black_risk.pv01:,.2f}, "
        f"Vega={result.black_risk.vega:,.2f}, "
        f"Theta={result.black_risk.theta:,.2f}"
    )
    print(
        "SABR risk:  "
        f"PV01={result.sabr_risk.pv01:,.2f}, "
        f"AlphaRisk={result.sabr_risk.vega:,.2f}, "
        f"Theta={result.sabr_risk.theta:,.2f}"
    )
    print(f"Data source: {bundle.source}")


def run_calibration(args: argparse.Namespace) -> None:
    bundle = load_project_data(
        data_mode=args.data_mode,
        curve_csv=args.curve_csv,
        market_quotes_csv=args.market_quotes_csv,
        spec_csv=args.spec_csv,
        vol_slice_csv=args.vol_slice_csv,
        bootstrap_curve=args.bootstrap_curve,
    )
    forward = forward_swap_rate(bundle.curve, bundle.spec.expiry, bundle.spec.tenor, bundle.spec.pay_frequency)
    expiry = bundle.spec.expiry
    if bundle.vol_slice:
        strikes = [quote.strike for quote in bundle.vol_slice]
        market_vols = [quote.vol for quote in bundle.vol_slice]
    else:
        strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
        true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
        market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]

    result = calibrate_sabr_to_vols(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        initial_guess=(0.0180, -0.10, 0.30),
    )

    print("SABR Calibration Example")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(
        "Params: "
        f"alpha={result.params.alpha:.6f}, "
        f"beta={result.params.beta:.2f}, "
        f"rho={result.params.rho:.6f}, "
        f"nu={result.params.nu:.6f}"
    )
    print(f"Objective value: {result.objective_value:.12f}")
    print("Strike     MarketVol    FittedVol")
    for strike, market_vol, fitted_vol in zip(result.strikes, result.market_vols, result.fitted_vols):
        print(f"{strike:0.4f}     {market_vol:0.6f}    {fitted_vol:0.6f}")
    print(f"Data source: {bundle.source}")


def run_sofr(args: argparse.Namespace) -> None:
    if args.sofr_prepare_dir:
        if args.sofr_csv:
            outputs = prepare_sofr_data_bundle_from_local_csv(
                args.sofr_csv,
                args.sofr_prepare_dir,
                maturity_years=args.sofr_maturity_years,
            )
        elif args.sofr_excel:
            outputs = prepare_sofr_data_bundle_from_excel(
                args.sofr_excel,
                args.sofr_prepare_dir,
                maturity_years=args.sofr_maturity_years,
            )
        else:
            outputs = prepare_sofr_data_bundle(
                args.sofr_prepare_dir,
                cosd=args.sofr_start,
                coed=args.sofr_end,
                maturity_years=args.sofr_maturity_years,
            )
        print("SOFR Ingestion")
        for label, path in outputs.items():
            print(f"{label}: {path}")
        return

    if args.sofr_excel:
        observation = latest_sofr_observation_from_excel(args.sofr_excel)
        print("SOFR Ingestion")
        print(f"Source Excel: {args.sofr_excel}")
        print(f"Latest observation date: {observation.date}")
        print(f"Latest SOFR (%):        {observation.rate_percent:.4f}")
        return

    if args.sofr_csv:
        source_path = Path(args.sofr_csv)
    else:
        source_path = PROJECT_ROOT / "data/raw/market/sofr/sofr_history.csv"
        download_sofr_history_csv(source_path, cosd=args.sofr_start, coed=args.sofr_end)

    observation = latest_sofr_observation(source_path)
    print("SOFR Ingestion")
    print(f"Source CSV: {source_path}")
    print(f"Latest observation date: {observation.date}")
    print(f"Latest SOFR (%):        {observation.rate_percent:.4f}")

    if args.sofr_quote_csv:
        quote_path = write_sofr_market_quote_csv(
            source_path,
            args.sofr_quote_csv,
            maturity_years=args.sofr_maturity_years,
            pay_frequency=1,
        )
        print(f"Normalized market quote CSV: {quote_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Swaption pricing project entry point")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["pricing", "comparison", "risk", "calibration", "sofr"],
        default="pricing",
        help="Which workflow to run",
    )
    parser.add_argument("--data-mode", choices=["example", "market"], default="example", help="Select built-in example data or CSV-backed market data")
    parser.add_argument("--curve-csv", help="Path to curve node CSV with columns maturity,zero_rate")
    parser.add_argument("--market-quotes-csv", help="Path to market quotes CSV with columns instrument_type,maturity,rate,pay_frequency")
    parser.add_argument("--spec-csv", help="Path to one-row swaption spec CSV")
    parser.add_argument("--vol-slice-csv", help="Path to swaption vol slice CSV")
    parser.add_argument("--bootstrap-curve", action="store_true", help="Bootstrap the curve from market quotes instead of reading curve nodes directly")
    parser.add_argument("--sofr-csv", help="Existing local SOFR history CSV with DATE,SOFR columns")
    parser.add_argument("--sofr-excel", help="Existing local New York Fed SOFR Excel export")
    parser.add_argument("--sofr-start", help="Optional SOFR download start date in YYYY-MM-DD format")
    parser.add_argument("--sofr-end", help="Optional SOFR download end date in YYYY-MM-DD format")
    parser.add_argument("--sofr-prepare-dir", help="Prepare a full SOFR data bundle in this directory")
    parser.add_argument(
        "--sofr-quote-csv",
        help="Write the latest SOFR fixing as a normalized market quote CSV",
    )
    parser.add_argument(
        "--sofr-maturity-years",
        type=float,
        default=1.0 / 360.0,
        help="Year fraction used when mapping SOFR into a short-end deposit quote",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.mode == "pricing":
        run_pricing(args)
    elif args.mode == "comparison":
        run_comparison(args)
    elif args.mode == "risk":
        run_risk(args)
    elif args.mode == "calibration":
        run_calibration(args)
    elif args.mode == "sofr":
        run_sofr(args)


if __name__ == "__main__":
    main()
