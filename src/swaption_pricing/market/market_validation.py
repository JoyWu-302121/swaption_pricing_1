"""Helpers for market-validation views and summaries."""

from __future__ import annotations

import json
from pathlib import Path

from ..core.swap import forward_swap_rate, swap_annuity
from ..pricing.european.black76 import price_swaption
from ..types import Curve, SwaptionSpec
from .market_data import discount_factor


def curve_node_rows(curve: Curve) -> list[dict[str, float]]:
    """Return simple table rows for curve-node display."""
    return [
        {
            "maturity": point.maturity,
            "zero_rate": point.zero_rate,
        }
        for point in curve
    ]


def discount_factor_rows(curve: Curve) -> list[dict[str, float]]:
    """Return discount-factor rows implied by the curve nodes."""
    return [
        {
            "maturity": point.maturity,
            "zero_rate": point.zero_rate,
            "discount_factor": discount_factor(point.zero_rate, point.maturity),
        }
        for point in curve
    ]


def trade_summary(curve: Curve, spec: SwaptionSpec, black_vol: float) -> dict[str, float | str]:
    """Return a compact pricing summary for one representative swaption."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    price = price_swaption(curve, spec, black_vol)
    return {
        "option_type": spec.option_type,
        "notional": spec.notional,
        "expiry": spec.expiry,
        "tenor": spec.tenor,
        "strike": spec.strike,
        "forward": forward,
        "annuity": annuity,
        "black_vol": black_vol,
        "black_price": price,
    }


def load_json_metadata(path: str | Path) -> dict:
    """Load a JSON metadata file for display in validation notebooks."""
    return json.loads(Path(path).read_text(encoding="utf-8"))
