"""Load example or CSV-based market data into normalized project objects."""

from __future__ import annotations

import csv
from pathlib import Path

from .curve_bootstrap import bootstrap_zero_curve
from .types import CurvePoint, MarketQuote, ProjectDataBundle, SwaptionSpec, SwaptionVolQuote


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_example_curve() -> list[CurvePoint]:
    """Return the synthetic curve used throughout the project examples."""
    return [
        CurvePoint(maturity=1.0, zero_rate=0.0420),
        CurvePoint(maturity=2.0, zero_rate=0.0415),
        CurvePoint(maturity=3.0, zero_rate=0.0410),
        CurvePoint(maturity=4.0, zero_rate=0.0408),
        CurvePoint(maturity=5.0, zero_rate=0.0405),
        CurvePoint(maturity=6.0, zero_rate=0.0403),
        CurvePoint(maturity=7.0, zero_rate=0.0402),
    ]


def build_example_market_quotes() -> list[MarketQuote]:
    """Return the synthetic market-quote ladder used for bootstrap demos."""
    return [
        MarketQuote(instrument_type="deposit", maturity=1.0, rate=0.0420),
        MarketQuote(instrument_type="swap", maturity=2.0, rate=0.0415, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=3.0, rate=0.0410, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=4.0, rate=0.0408, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=5.0, rate=0.0405, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=6.0, rate=0.0403, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=7.0, rate=0.0402, pay_frequency=1),
    ]


def build_example_spec(strike: float = 0.0400, option_type: str = "payer") -> SwaptionSpec:
    """Return the default example swaption specification."""
    return SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=strike,
        pay_frequency=1,
        option_type=option_type,
    )


def build_example_vol_slice() -> list[SwaptionVolQuote]:
    """Return a synthetic smile slice around the example trade."""
    return [
        SwaptionVolQuote(expiry=2.0, tenor=5.0, strike=0.0300, vol=0.1350, vol_type="black"),
        SwaptionVolQuote(expiry=2.0, tenor=5.0, strike=0.0350, vol=0.1180, vol_type="black"),
        SwaptionVolQuote(expiry=2.0, tenor=5.0, strike=0.0400, vol=0.1025, vol_type="black"),
        SwaptionVolQuote(expiry=2.0, tenor=5.0, strike=0.0450, vol=0.0940, vol_type="black"),
        SwaptionVolQuote(expiry=2.0, tenor=5.0, strike=0.0500, vol=0.0915, vol_type="black"),
    ]


def build_example_bundle() -> ProjectDataBundle:
    """Return the complete synthetic data bundle used across the project."""
    return ProjectDataBundle(
        curve=build_example_curve(),
        spec=build_example_spec(),
        market_quotes=build_example_market_quotes(),
        vol_slice=build_example_vol_slice(),
        source="example",
    )


def load_curve_points_csv(path: str | Path) -> list[CurvePoint]:
    """Load a zero-curve node file with columns maturity,zero_rate."""
    return [
        CurvePoint(maturity=float(row["maturity"]), zero_rate=float(row["zero_rate"]))
        for row in _read_csv_rows(path)
    ]


def load_market_quotes_csv(path: str | Path) -> list[MarketQuote]:
    """Load bootstrap inputs with columns instrument_type,maturity,rate,pay_frequency."""
    rows = _read_csv_rows(path)
    return [
        MarketQuote(
            instrument_type=row["instrument_type"],
            maturity=float(row["maturity"]),
            rate=float(row["rate"]),
            pay_frequency=int(row.get("pay_frequency") or 1),
        )
        for row in rows
    ]


def load_swaption_spec_csv(path: str | Path) -> SwaptionSpec:
    """Load a one-row swaption specification CSV."""
    rows = _read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError("swaption spec CSV must contain exactly one row")
    row = rows[0]
    return SwaptionSpec(
        notional=float(row["notional"]),
        expiry=float(row["expiry"]),
        tenor=float(row["tenor"]),
        strike=float(row["strike"]),
        pay_frequency=int(row["pay_frequency"]),
        option_type=row["option_type"],
    )


def load_swaption_vol_slice_csv(path: str | Path) -> list[SwaptionVolQuote]:
    """Load a swaption volatility slice CSV."""
    return [
        SwaptionVolQuote(
            expiry=float(row["expiry"]),
            tenor=float(row["tenor"]),
            strike=float(row["strike"]),
            vol=float(row["vol"]),
            vol_type=row.get("vol_type", "black"),
        )
        for row in _read_csv_rows(path)
    ]


def load_market_bundle(
    *,
    curve_csv: str | Path | None = None,
    market_quotes_csv: str | Path | None = None,
    spec_csv: str | Path | None = None,
    vol_slice_csv: str | Path | None = None,
    bootstrap_curve: bool = False,
) -> ProjectDataBundle:
    """Load a market-data bundle from CSV files.

    If ``bootstrap_curve`` is True, ``market_quotes_csv`` is required and the curve is
    built from quotes. Otherwise ``curve_csv`` is required.
    """
    if bootstrap_curve:
        if market_quotes_csv is None:
            raise ValueError("market_quotes_csv is required when bootstrap_curve=True")
        market_quotes = load_market_quotes_csv(market_quotes_csv)
        curve = bootstrap_zero_curve(market_quotes)
    else:
        if curve_csv is None:
            raise ValueError("curve_csv is required when bootstrap_curve=False")
        curve = load_curve_points_csv(curve_csv)
        market_quotes = load_market_quotes_csv(market_quotes_csv) if market_quotes_csv else []

    spec = load_swaption_spec_csv(spec_csv) if spec_csv else build_example_spec()
    vol_slice = load_swaption_vol_slice_csv(vol_slice_csv) if vol_slice_csv else []
    return ProjectDataBundle(
        curve=curve,
        spec=spec,
        market_quotes=market_quotes,
        vol_slice=vol_slice,
        source="market_csv",
    )


def load_project_data(
    *,
    data_mode: str,
    curve_csv: str | Path | None = None,
    market_quotes_csv: str | Path | None = None,
    spec_csv: str | Path | None = None,
    vol_slice_csv: str | Path | None = None,
    bootstrap_curve: bool = False,
) -> ProjectDataBundle:
    """Load either the built-in example bundle or a CSV-backed market bundle."""
    normalized_mode = data_mode.lower()
    if normalized_mode == "example":
        return build_example_bundle()
    if normalized_mode == "market":
        return load_market_bundle(
            curve_csv=curve_csv,
            market_quotes_csv=market_quotes_csv,
            spec_csv=spec_csv,
            vol_slice_csv=vol_slice_csv,
            bootstrap_curve=bootstrap_curve,
        )
    raise ValueError("data_mode must be 'example' or 'market'")
