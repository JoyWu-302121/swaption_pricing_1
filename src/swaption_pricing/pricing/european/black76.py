"""Black-style European swaption pricing."""

from __future__ import annotations

from math import log, sqrt

from scipy.stats import norm

from ...core.swap import forward_swap_rate, swap_annuity
from ...types import Curve, SwaptionSpec


def _d1(forward: float, strike: float, vol: float, expiry: float) -> float:
    return (log(forward / strike) + 0.5 * vol * vol * expiry) / (vol * sqrt(expiry))


def _d2(forward: float, strike: float, vol: float, expiry: float) -> float:
    return _d1(forward, strike, vol, expiry) - vol * sqrt(expiry)


def moneyness_label(curve: Curve, spec: SwaptionSpec, tolerance: float = 1e-4) -> str:
    """Classify the option as ITM, ATM, or OTM against the forward swap rate."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    diff = forward - spec.strike

    if abs(diff) <= tolerance:
        return "ATM"
    if spec.option_type.lower() == "payer":
        return "ITM" if diff > 0.0 else "OTM"
    if spec.option_type.lower() == "receiver":
        return "ITM" if diff < 0.0 else "OTM"
    raise ValueError("option_type must be 'payer' or 'receiver'")


def intrinsic_value(curve: Curve, spec: SwaptionSpec) -> float:
    """Return the immediate-exercise value based on the forward swap rate."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)

    if spec.option_type.lower() == "payer":
        intrinsic_payoff = max(forward - spec.strike, 0.0)
    elif spec.option_type.lower() == "receiver":
        intrinsic_payoff = max(spec.strike - forward, 0.0)
    else:
        raise ValueError("option_type must be 'payer' or 'receiver'")

    return spec.notional * annuity * intrinsic_payoff


def price_swaption(curve: Curve, spec: SwaptionSpec, vol: float) -> float:
    """Price a European swaption using the Black framework."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    d1 = _d1(forward, spec.strike, vol, spec.expiry)
    d2 = _d2(forward, spec.strike, vol, spec.expiry)

    if spec.option_type.lower() == "payer":
        payoff = forward * norm.cdf(d1) - spec.strike * norm.cdf(d2)
    elif spec.option_type.lower() == "receiver":
        payoff = spec.strike * norm.cdf(-d2) - forward * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'payer' or 'receiver'")

    return spec.notional * annuity * payoff


def time_value(curve: Curve, spec: SwaptionSpec, vol: float) -> float:
    """Return the option time value as Black price minus intrinsic value."""
    return price_swaption(curve, spec, vol) - intrinsic_value(curve, spec)


def price_shifted_black(forward: float, strike: float, expiry: float, vol: float, shift: float, option_type: str) -> float:
    """Return a shifted-Black option value on the forward swap rate."""
    shifted_forward = forward + shift
    shifted_strike = strike + shift
    if shifted_forward <= 0.0 or shifted_strike <= 0.0:
        raise ValueError("shift must make forward and strike strictly positive")

    d1 = _d1(shifted_forward, shifted_strike, vol, expiry)
    d2 = _d2(shifted_forward, shifted_strike, vol, expiry)
    direction = option_type.lower()

    if direction == "payer":
        return shifted_forward * norm.cdf(d1) - shifted_strike * norm.cdf(d2)
    if direction == "receiver":
        return shifted_strike * norm.cdf(-d2) - shifted_forward * norm.cdf(-d1)
    raise ValueError("option_type must be 'payer' or 'receiver'")


def price_swaption_shifted_black(curve: Curve, spec: SwaptionSpec, vol: float, shift: float) -> float:
    """Price a European swaption under shifted Black."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    payoff = price_shifted_black(forward, spec.strike, spec.expiry, vol, shift, spec.option_type)
    return spec.notional * annuity * payoff
