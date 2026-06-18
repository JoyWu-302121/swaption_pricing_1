"""Market data helpers for simplified curve-based analytics."""

from __future__ import annotations

from bisect import bisect_left
from math import exp

from ..types import Curve, CurvePoint


def discount_factor(zero_rate: float, maturity: float) -> float:
    """Return a continuously compounded discount factor."""
    return exp(-zero_rate * maturity)


def year_fractions(expiry: float, tenor: float, pay_frequency: int) -> list[float]:
    """Build payment dates for the fixed leg after option expiry."""
    step = 1.0 / pay_frequency
    periods = int(round(tenor * pay_frequency))
    return [expiry + step * idx for idx in range(1, periods + 1)]


def curve_as_dict(curve: Curve) -> dict[float, float]:
    """Expose curve points as a simple maturity-to-rate mapping."""
    return {point.maturity: point.zero_rate for point in curve}


def zero_rate(curve: Curve, maturity: float) -> float:
    """Return a zero rate using linear interpolation across curve points."""
    ordered_curve = sorted(curve, key=lambda point: point.maturity)
    maturities = [point.maturity for point in ordered_curve]

    if maturity <= maturities[0]:
        return ordered_curve[0].zero_rate
    if maturity >= maturities[-1]:
        return ordered_curve[-1].zero_rate

    upper_index = bisect_left(maturities, maturity)
    lower_point = ordered_curve[upper_index - 1]
    upper_point = ordered_curve[upper_index]

    if maturity == upper_point.maturity:
        return upper_point.zero_rate

    weight = (maturity - lower_point.maturity) / (upper_point.maturity - lower_point.maturity)
    return lower_point.zero_rate + weight * (upper_point.zero_rate - lower_point.zero_rate)


def build_daily_zero_curve(curve: Curve, last_maturity: float, day_count_basis: int = 365) -> list[CurvePoint]:
    """Interpolate a node-based zero curve into a daily zero-rate curve."""
    total_days = int(round(last_maturity * day_count_basis))
    return [
        CurvePoint(maturity=day / day_count_basis, zero_rate=zero_rate(curve, day / day_count_basis))
        for day in range(1, total_days + 1)
    ]
