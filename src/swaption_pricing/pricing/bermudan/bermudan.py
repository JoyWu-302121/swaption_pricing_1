"""High-level Bermudan calibration helpers for market-style workflows."""

from __future__ import annotations

from ...types import BermudanSwaptionSpec, SwaptionVolQuote
from .exercise import coterminal_tenors


def build_bermudan_calibration_targets(
    spec: BermudanSwaptionSpec,
    european_vol_quotes: list[SwaptionVolQuote],
) -> list[SwaptionVolQuote]:
    """Select co-terminal European swaptions for Bermudan model calibration."""
    target_tenors = {round(tenor, 10) for tenor in coterminal_tenors(spec) if tenor > 0.0}
    target_expiries = {round(expiry, 10) for expiry in spec.exercise_dates}
    return [
        quote
        for quote in european_vol_quotes
        if round(quote.expiry, 10) in target_expiries and round(quote.tenor, 10) in target_tenors
    ]
