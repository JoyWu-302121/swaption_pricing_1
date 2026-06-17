"""Load example or market CSV data into normalized project objects."""

from __future__ import annotations

import csv
from pathlib import Path

from .curve_bootstrap import bootstrap_zero_curve
from .types import CurvePoint, MarketQuote, ProjectDataBundle, SwaptionSpec, SwaptionVolQuote

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXAMPLE_DIR = PROJECT_ROOT / "data/european/example"
DEFAULT_EXAMPLE_CURVE_CSV = DEFAULT_EXAMPLE_DIR / "curve_points.csv"
DEFAULT_EXAMPLE_MARKET_QUOTES_CSV = DEFAULT_EXAMPLE_DIR / "market_quotes.csv"
DEFAULT_EXAMPLE_SPEC_CSV = DEFAULT_EXAMPLE_DIR / "swaption_spec.csv"
DEFAULT_EXAMPLE_VOL_SLICE_CSV = DEFAULT_EXAMPLE_DIR / "vol_slice.csv"
DEFAULT_MARKET_DIR = PROJECT_ROOT / "data/european/market"
DEFAULT_MARKET_CURVE_CSV = DEFAULT_MARKET_DIR / "curve_points.csv"
DEFAULT_MARKET_SPEC_CSV = DEFAULT_MARKET_DIR / "swaption_spec.csv"
DEFAULT_MARKET_VOL_SLICE_CSV = DEFAULT_MARKET_DIR / "vol_slice.csv"
DEFAULT_MARKET_QUOTES_CSV = DEFAULT_MARKET_DIR / "market_quotes.csv"
DEFAULT_PROXY_CURVE_CSV = DEFAULT_MARKET_DIR / "ust_yield_curve_proxy/curve_points.csv"


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def load_example_bundle() -> ProjectDataBundle:
    """Load the example bundle from CSV files under data/european/example."""
    return ProjectDataBundle(
        curve=load_curve_points_csv(DEFAULT_EXAMPLE_CURVE_CSV),
        spec=load_swaption_spec_csv(DEFAULT_EXAMPLE_SPEC_CSV),
        market_quotes=load_market_quotes_csv(DEFAULT_EXAMPLE_MARKET_QUOTES_CSV),
        vol_slice=load_swaption_vol_slice_csv(DEFAULT_EXAMPLE_VOL_SLICE_CSV),
        source="example",
        curve_source=str(DEFAULT_EXAMPLE_CURVE_CSV),
        spec_source=str(DEFAULT_EXAMPLE_SPEC_CSV),
        vol_source=str(DEFAULT_EXAMPLE_VOL_SLICE_CSV),
    )


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
        curve_source = str(Path(market_quotes_csv))
    else:
        if curve_csv is None:
            raise ValueError("curve_csv is required when bootstrap_curve=False")
        curve = load_curve_points_csv(curve_csv)
        market_quotes = load_market_quotes_csv(market_quotes_csv) if market_quotes_csv else []
        curve_source = str(Path(curve_csv))

    if spec_csv:
        spec = load_swaption_spec_csv(spec_csv)
        spec_source = str(Path(spec_csv))
    else:
        spec = load_swaption_spec_csv(DEFAULT_EXAMPLE_SPEC_CSV)
        spec_source = f"{DEFAULT_EXAMPLE_SPEC_CSV} (example fallback)"
    vol_slice = load_swaption_vol_slice_csv(vol_slice_csv) if vol_slice_csv else []
    vol_source = str(Path(vol_slice_csv)) if vol_slice_csv else "no market vol slice loaded"
    return ProjectDataBundle(
        curve=curve,
        spec=spec,
        market_quotes=market_quotes,
        vol_slice=vol_slice,
        source="market_csv",
        curve_source=curve_source,
        spec_source=spec_source,
        vol_source=vol_source,
    )


def load_auto_bundle(
    *,
    curve_csv: str | Path | None = None,
    market_quotes_csv: str | Path | None = None,
    spec_csv: str | Path | None = None,
    vol_slice_csv: str | Path | None = None,
    bootstrap_curve: bool = False,
) -> ProjectDataBundle:
    """Load market data when available, otherwise fall back to the example bundle."""
    explicit_curve_csv = Path(curve_csv) if curve_csv else None
    explicit_market_quotes_csv = Path(market_quotes_csv) if market_quotes_csv else None
    explicit_spec_csv = Path(spec_csv) if spec_csv else None
    explicit_vol_slice_csv = Path(vol_slice_csv) if vol_slice_csv else None

    if bootstrap_curve:
        candidate_market_quotes = explicit_market_quotes_csv or DEFAULT_MARKET_QUOTES_CSV
        if candidate_market_quotes.exists():
            candidate_spec = explicit_spec_csv if explicit_spec_csv and explicit_spec_csv.exists() else (
                DEFAULT_MARKET_SPEC_CSV if DEFAULT_MARKET_SPEC_CSV.exists() else None
            )
            candidate_vol = explicit_vol_slice_csv if explicit_vol_slice_csv and explicit_vol_slice_csv.exists() else (
                DEFAULT_MARKET_VOL_SLICE_CSV if DEFAULT_MARKET_VOL_SLICE_CSV.exists() else None
            )
            return load_market_bundle(
                market_quotes_csv=candidate_market_quotes,
                spec_csv=candidate_spec,
                vol_slice_csv=candidate_vol,
                bootstrap_curve=True,
            )

    candidate_curve = None
    if explicit_curve_csv and explicit_curve_csv.exists():
        candidate_curve = explicit_curve_csv
    elif DEFAULT_MARKET_CURVE_CSV.exists():
        candidate_curve = DEFAULT_MARKET_CURVE_CSV
    elif DEFAULT_PROXY_CURVE_CSV.exists():
        candidate_curve = DEFAULT_PROXY_CURVE_CSV

    if candidate_curve is not None:
        candidate_spec = explicit_spec_csv if explicit_spec_csv and explicit_spec_csv.exists() else (
            DEFAULT_MARKET_SPEC_CSV if DEFAULT_MARKET_SPEC_CSV.exists() else None
        )
        candidate_vol = explicit_vol_slice_csv if explicit_vol_slice_csv and explicit_vol_slice_csv.exists() else (
            DEFAULT_MARKET_VOL_SLICE_CSV if DEFAULT_MARKET_VOL_SLICE_CSV.exists() else None
        )
        bundle = load_market_bundle(
            curve_csv=candidate_curve,
            spec_csv=candidate_spec,
            vol_slice_csv=candidate_vol,
            bootstrap_curve=False,
        )
        source = "market_auto"
        curve_source = str(candidate_curve)
        if candidate_curve == DEFAULT_PROXY_CURVE_CSV:
            source = "market_proxy_auto"
            curve_source = f"{candidate_curve} (UST proxy)"
        return ProjectDataBundle(
            curve=bundle.curve,
            spec=bundle.spec,
            market_quotes=bundle.market_quotes,
            vol_slice=bundle.vol_slice,
            source=source,
            curve_source=curve_source,
            spec_source=bundle.spec_source,
            vol_source=bundle.vol_source,
        )

    example_bundle = load_example_bundle()
    return ProjectDataBundle(
        curve=example_bundle.curve,
        spec=example_bundle.spec,
        market_quotes=example_bundle.market_quotes,
        vol_slice=example_bundle.vol_slice,
        source="example_fallback",
        curve_source=example_bundle.curve_source,
        spec_source=example_bundle.spec_source,
        vol_source=example_bundle.vol_source,
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
    """Load project data using example, market, or auto-prefer-market mode."""
    normalized_mode = data_mode.lower()
    if normalized_mode == "example":
        return load_example_bundle()
    if normalized_mode == "auto":
        return load_auto_bundle(
            curve_csv=curve_csv,
            market_quotes_csv=market_quotes_csv,
            spec_csv=spec_csv,
            vol_slice_csv=vol_slice_csv,
            bootstrap_curve=bootstrap_curve,
        )
    if normalized_mode == "market":
        return load_market_bundle(
            curve_csv=curve_csv,
            market_quotes_csv=market_quotes_csv,
            spec_csv=spec_csv,
            vol_slice_csv=vol_slice_csv,
            bootstrap_curve=bootstrap_curve,
        )
    raise ValueError("data_mode must be 'auto', 'example', or 'market'")
