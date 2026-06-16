"""Vanilla swap analytics used by the swaption pricer."""

from __future__ import annotations

from .market_data import discount_factor, year_fractions, zero_rate
from .types import Curve


def payment_schedule(start: float, tenor: float, pay_frequency: int) -> list[float]:
    """Return payment dates for a vanilla swap leg."""
    return year_fractions(start, tenor, pay_frequency)


def curve_discount_factor(curve: Curve, maturity: float) -> float:
    """Return a discount factor from the interpolated zero curve."""
    return discount_factor(zero_rate(curve, maturity), maturity)


def swap_annuity(curve: Curve, expiry: float, tenor: float, pay_frequency: int) -> float:
    """Compute the fixed leg annuity in a simplified single-curve setup."""
    accrual = 1.0 / pay_frequency
    payment_dates = payment_schedule(expiry, tenor, pay_frequency)
    return sum(accrual * curve_discount_factor(curve, payment_date) for payment_date in payment_dates)


def fixed_leg_pv(
    curve: Curve,
    notional: float,
    fixed_rate: float,
    start: float,
    tenor: float,
    pay_frequency: int,
) -> float:
    """Return the present value of the fixed leg."""
    annuity = swap_annuity(curve, start, tenor, pay_frequency)
    return notional * fixed_rate * annuity


def floating_leg_pv(curve: Curve, notional: float, start: float, tenor: float) -> float:
    """Return the present value of the floating leg in a single-curve setup."""
    start_df = 1.0 if start == 0.0 else curve_discount_factor(curve, start)
    end_df = curve_discount_factor(curve, start + tenor)
    return notional * (start_df - end_df)


def swap_present_value(
    curve: Curve,
    notional: float,
    fixed_rate: float,
    start: float,
    tenor: float,
    pay_frequency: int,
    swap_type: str,
) -> float:
    """Return the value of a payer or receiver vanilla swap."""
    fixed_value = fixed_leg_pv(curve, notional, fixed_rate, start, tenor, pay_frequency)
    floating_value = floating_leg_pv(curve, notional, start, tenor)
    direction = swap_type.lower()

    if direction == "payer":
        return floating_value - fixed_value
    if direction == "receiver":
        return fixed_value - floating_value
    raise ValueError("swap_type must be 'payer' or 'receiver'")


def forward_swap_rate(curve: Curve, expiry: float, tenor: float, pay_frequency: int) -> float:
    """Compute the forward par swap rate from discount factors."""
    annuity = swap_annuity(curve, expiry, tenor, pay_frequency)
    start_df = curve_discount_factor(curve, expiry)
    end_df = curve_discount_factor(curve, expiry + tenor)
    return (start_df - end_df) / annuity
