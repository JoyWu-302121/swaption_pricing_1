"""Common curve-shock helpers shared by pricing and hedging workflows."""

from __future__ import annotations

from dataclasses import replace

from ..pricing.european.black76 import price_swaption
from ..types import Curve, SwaptionSpec


def parallel_shift_curve(curve: Curve, shift: float) -> list:
    """Apply a parallel shift to all zero rates."""
    return [replace(point, zero_rate=point.zero_rate + shift) for point in curve]


def price_with_curve_shift(curve: Curve, spec: SwaptionSpec, vol: float, shift: float) -> float:
    """Price a European swaption after a parallel curve shift."""
    shifted_curve = parallel_shift_curve(curve, shift)
    return price_swaption(shifted_curve, spec, vol)
