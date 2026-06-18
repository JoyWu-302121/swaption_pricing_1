"""Bootstrap curve nodes from simplified market quotes."""

from __future__ import annotations

from math import log

from .market_data import year_fractions
from ..types import CurvePoint, MarketQuote


def zero_rate_from_discount_factor(discount_factor: float, maturity: float) -> float:
    """Convert a discount factor into a continuously compounded zero rate."""
    if maturity <= 0.0:
        raise ValueError("maturity must be positive")
    if discount_factor <= 0.0:
        raise ValueError("discount_factor must be positive")
    return -log(discount_factor) / maturity


def bootstrap_deposit_quote(quote: MarketQuote) -> CurvePoint:
    """Bootstrap one zero-rate node from a simplified deposit quote."""
    if quote.instrument_type.lower() != "deposit":
        raise ValueError("bootstrap_deposit_quote expects a deposit quote")
    discount_factor = 1.0 / (1.0 + quote.rate * quote.maturity)
    return CurvePoint(
        maturity=quote.maturity,
        zero_rate=zero_rate_from_discount_factor(discount_factor, quote.maturity),
    )


def bootstrap_swap_quote(existing_curve: list[CurvePoint], quote: MarketQuote) -> CurvePoint:
    """Bootstrap the final node of a par swap from earlier curve nodes."""
    if quote.instrument_type.lower() != "swap":
        raise ValueError("bootstrap_swap_quote expects a swap quote")

    previous_discount_factors = {
        point.maturity: exp_minus_rt(point.zero_rate, point.maturity) for point in existing_curve
    }
    accrual = 1.0 / quote.pay_frequency
    payment_dates = year_fractions(0.0, quote.maturity, quote.pay_frequency)
    prior_payment_dates = payment_dates[:-1]

    missing_dates = [payment_date for payment_date in prior_payment_dates if payment_date not in previous_discount_factors]
    if missing_dates:
        raise ValueError(
            "Cannot bootstrap swap quote because earlier payment dates are missing from the curve: "
            f"{missing_dates}"
        )

    fixed_leg_known = sum(accrual * previous_discount_factors[payment_date] for payment_date in prior_payment_dates)
    final_discount_factor = (1.0 - quote.rate * fixed_leg_known) / (1.0 + quote.rate * accrual)
    return CurvePoint(
        maturity=quote.maturity,
        zero_rate=zero_rate_from_discount_factor(final_discount_factor, quote.maturity),
    )


def bootstrap_zero_curve(quotes: list[MarketQuote]) -> list[CurvePoint]:
    """Bootstrap curve nodes from simplified deposit and par swap quotes."""
    ordered_quotes = sorted(quotes, key=lambda quote: quote.maturity)
    curve: list[CurvePoint] = []

    for quote in ordered_quotes:
        instrument_type = quote.instrument_type.lower()
        if instrument_type == "deposit":
            curve.append(bootstrap_deposit_quote(quote))
        elif instrument_type == "swap":
            curve.append(bootstrap_swap_quote(curve, quote))
        else:
            raise ValueError(f"Unsupported instrument_type: {quote.instrument_type}")

    return curve


def exp_minus_rt(zero_rate: float, maturity: float) -> float:
    """Return exp(-rT) without importing the full market-data helper layer."""
    return pow(2.718281828459045, -zero_rate * maturity)
