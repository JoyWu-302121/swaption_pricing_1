"""Bachelier swaption pricing helpers for normal-vol comparisons."""

from __future__ import annotations

from math import sqrt

from scipy.stats import norm

from ...core.swap import forward_swap_rate, swap_annuity
from ...types import Curve, SwaptionSpec


def bachelier_option_value(forward: float, strike: float, expiry: float, normal_vol: float, option_type: str) -> float:
    """Return the normal-model option value on the forward swap rate."""
    if normal_vol <= 0.0:
        raise ValueError("normal_vol must be positive")
    std_dev = normal_vol * sqrt(expiry)
    d = (forward - strike) / std_dev
    direction = option_type.lower()

    if direction == "payer":
        return (forward - strike) * norm.cdf(d) + std_dev * norm.pdf(d)
    if direction == "receiver":
        return (strike - forward) * norm.cdf(-d) + std_dev * norm.pdf(d)
    raise ValueError("option_type must be 'payer' or 'receiver'")


def price_swaption_bachelier(curve: Curve, spec: SwaptionSpec, normal_vol: float) -> float:
    """Price a European swaption using the Bachelier normal-vol framework."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    payoff = bachelier_option_value(forward, spec.strike, spec.expiry, normal_vol, spec.option_type)
    return spec.notional * annuity * payoff
