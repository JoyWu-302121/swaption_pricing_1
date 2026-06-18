"""Unified command-line entry point for the swaption pricing project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.data import load_project_data
from swaption_pricing.core import forward_swap_rate, swap_annuity
from swaption_pricing.market import (
    download_sofr_history_csv,
    latest_sofr_observation,
    latest_sofr_observation_from_excel,
    prepare_sofr_data_bundle,
    prepare_sofr_data_bundle_from_excel,
    prepare_sofr_data_bundle_from_local_csv,
    write_sofr_market_quote_csv,
)
from swaption_pricing.pricing.european import (
    SabrParams,
    calibrate_sabr_to_vols,
    price_swaption,
    price_swaption_bachelier,
    price_swaption_with_sabr,
    sabr_implied_volatility,
)
from swaption_pricing.risk import (
    calculate_bachelier_risk,
    calculate_risk,
    calculate_sabr_risk,
    compare_black_and_sabr_risk,
)


def select_market_vol(bundle, spec, default_vol: float, vol_type: str) -> float:
    """Pick a strike-matched market vol when available, otherwise use the fallback."""
    matching_quotes = [
        quote
        for quote in bundle.vol_slice
        if quote.vol_type.lower() == vol_type.lower()
        and abs(quote.expiry - spec.expiry) < 1e-12
        and abs(quote.tenor - spec.tenor) < 1e-12
        and abs(quote.strike - spec.strike) < 1e-12
    ]
    if matching_quotes:
        return matching_quotes[0].vol
    return default_vol


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

    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)

    print("Swaption Example")
    print(f"Model:             {args.model}")
    print(f"Forward swap rate: {forward:.6f}")
    print(f"Swap annuity:      {annuity:.6f}")

    if args.model == "black":
        vol = select_market_vol(bundle, spec, args.black_vol, "black")
        price = price_swaption(curve, spec, vol)
        risk = calculate_risk(curve, spec, vol)
        print(f"Quoted vol:        {vol:.6f}")
        print(f"Price:             {price:,.2f}")
        print(f"PV01:              {risk.pv01:,.2f}")
        print(f"Vega:              {risk.vega:,.2f}")
        print(f"Theta:             {risk.theta:,.2f}")
    elif args.model == "sabr":
        params = SabrParams(alpha=args.sabr_alpha, beta=args.sabr_beta, rho=args.sabr_rho, nu=args.sabr_nu)
        price, implied_vol = price_swaption_with_sabr(curve, spec, params)
        risk = calculate_sabr_risk(curve, spec, params)
        print(
            "SABR params:       "
            f"alpha={params.alpha:.4f}, beta={params.beta:.4f}, rho={params.rho:.4f}, nu={params.nu:.4f}"
        )
        print(f"Implied Black vol: {implied_vol:.6f}")
        print(f"Price:             {price:,.2f}")
        print(f"PV01:              {risk.pv01:,.2f}")
        print(f"Alpha risk:        {risk.vega:,.2f}")
        print(f"Theta:             {risk.theta:,.2f}")
    elif args.model == "bachelier":
        normal_vol = select_market_vol(bundle, spec, args.normal_vol, "normal")
        price = price_swaption_bachelier(curve, spec, normal_vol)
        risk = calculate_bachelier_risk(curve, spec, normal_vol)
        print(f"Normal vol:        {normal_vol:.6f}")
        print(f"Price:             {price:,.2f}")
        print(f"PV01:              {risk.pv01:,.2f}")
        print(f"Normal vega:       {risk.vega:,.2f}")
        print(f"Theta:             {risk.theta:,.2f}")

    print(f"Data source:       {bundle.source}")
    print(f"Curve source:      {bundle.curve_source}")
    print(f"Spec source:       {bundle.spec_source}")
    print(f"Vol source:        {bundle.vol_source}")


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
    print(f"Curve source: {bundle.curve_source}")
    print(f"Spec source: {bundle.spec_source}")
    print(f"Vol source: {bundle.vol_source}")


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
    print(f"Curve source: {bundle.curve_source}")
    print(f"Spec source: {bundle.spec_source}")
    print(f"Vol source: {bundle.vol_source}")


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
    print(f"Curve source: {bundle.curve_source}")
    print(f"Spec source: {bundle.spec_source}")
    print(f"Vol source: {bundle.vol_source}")


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
        source_path = PROJECT_ROOT / "data/common/market/sofr/sofr_history.csv"
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
    parser.add_argument(
        "--data-mode",
        choices=["auto", "example", "market"],
        default="auto",
        help="Prefer market data when available, or force built-in example / explicit market modes",
    )
    parser.add_argument("--curve-csv", help="Path to curve node CSV with columns maturity,zero_rate")
    parser.add_argument("--market-quotes-csv", help="Path to market quotes CSV with columns instrument_type,maturity,rate,pay_frequency")
    parser.add_argument("--spec-csv", help="Path to one-row swaption spec CSV")
    parser.add_argument("--vol-slice-csv", help="Path to swaption vol slice CSV")
    parser.add_argument("--bootstrap-curve", action="store_true", help="Bootstrap the curve from market quotes instead of reading curve nodes directly")
    parser.add_argument(
        "--model",
        choices=["black", "sabr", "bachelier"],
        default="black",
        help="Pricing model used in pricing mode",
    )
    parser.add_argument("--black-vol", type=float, default=0.20, help="Fallback Black volatility when no market Black vol is available")
    parser.add_argument("--normal-vol", type=float, default=0.01, help="Fallback Bachelier normal volatility when no market normal vol is available")
    parser.add_argument("--sabr-alpha", type=float, default=0.0200, help="SABR alpha parameter for pricing mode")
    parser.add_argument("--sabr-beta", type=float, default=0.50, help="SABR beta parameter for pricing mode")
    parser.add_argument("--sabr-rho", type=float, default=-0.25, help="SABR rho parameter for pricing mode")
    parser.add_argument("--sabr-nu", type=float, default=0.40, help="SABR nu parameter for pricing mode")
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
