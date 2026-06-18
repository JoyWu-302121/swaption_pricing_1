"""SABR implied volatility and SABR-adjusted swaption pricing."""

from __future__ import annotations

from dataclasses import dataclass
from math import log, sqrt

from .black76 import price_swaption, price_swaption_shifted_black
from ...core.swap import forward_swap_rate
from ...types import Curve, SwaptionSpec


@dataclass(frozen=True)
class SabrParams:
    alpha: float
    beta: float
    rho: float
    nu: float


def sabr_implied_volatility(forward: float, strike: float, expiry: float, params: SabrParams) -> float:
    """Return the Hagan-style SABR implied Black volatility."""
    if forward <= 0.0 or strike <= 0.0:
        raise ValueError("forward and strike must be positive for lognormal SABR")

    alpha = params.alpha
    beta = params.beta
    rho = params.rho
    nu = params.nu

    if not -1.0 < rho < 1.0:
        raise ValueError("rho must lie strictly between -1 and 1")

    one_minus_beta = 1.0 - beta

    if abs(forward - strike) < 1e-12:
        fk_beta = forward ** one_minus_beta
        term1 = alpha / fk_beta
        term2 = (
            (one_minus_beta ** 2 / 24.0) * (alpha ** 2 / (forward ** (2.0 * one_minus_beta)))
            + (rho * beta * nu * alpha) / (4.0 * fk_beta)
            + ((2.0 - 3.0 * rho * rho) * nu * nu / 24.0)
        )
        return term1 * (1.0 + term2 * expiry)

    log_fk = log(forward / strike)
    fk_beta = (forward * strike) ** (0.5 * one_minus_beta)
    z = (nu / alpha) * fk_beta * log_fk
    x_z_numerator = sqrt(1.0 - 2.0 * rho * z + z * z) + z - rho
    x_z_denominator = 1.0 - rho
    x_z = log(x_z_numerator / x_z_denominator)

    log_term = 1.0 + (one_minus_beta ** 2 / 24.0) * (log_fk ** 2) + (one_minus_beta ** 4 / 1920.0) * (log_fk ** 4)
    leading = alpha / (fk_beta * log_term)

    correction = (
        (one_minus_beta ** 2 / 24.0) * (alpha ** 2 / ((forward * strike) ** one_minus_beta))
        + (rho * beta * nu * alpha) / (4.0 * fk_beta)
        + ((2.0 - 3.0 * rho * rho) * nu * nu / 24.0)
    )
    return leading * (z / x_z) * (1.0 + correction * expiry)


def price_swaption_with_sabr(curve: Curve, spec: SwaptionSpec, params: SabrParams) -> tuple[float, float]:
    """Price a swaption using SABR-implied vol passed into the Black formula."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    implied_vol = sabr_implied_volatility(forward, spec.strike, spec.expiry, params)
    return price_swaption(curve, spec, implied_vol), implied_vol


def sabr_vol_surface_slice(
    curve: Curve,
    expiry: float,
    tenor: float,
    pay_frequency: int,
    strikes: list[float],
    params: SabrParams,
) -> list[tuple[float, float]]:
    """Return a strike-vol slice for one expiry-tenor point."""
    forward = forward_swap_rate(curve, expiry, tenor, pay_frequency)
    return [(strike, sabr_implied_volatility(forward, strike, expiry, params)) for strike in strikes]


def shifted_sabr_implied_volatility(
    forward: float,
    strike: float,
    expiry: float,
    params: SabrParams,
    shift: float,
) -> float:
    """Return SABR implied vol after shifting forward and strike."""
    return sabr_implied_volatility(forward + shift, strike + shift, expiry, params)


def price_swaption_with_shifted_sabr(
    curve: Curve,
    spec: SwaptionSpec,
    params: SabrParams,
    shift: float,
) -> tuple[float, float]:
    """Price a swaption using shifted SABR implied vol and shifted Black pricing."""
    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    implied_vol = shifted_sabr_implied_volatility(forward, spec.strike, spec.expiry, params, shift)
    return price_swaption_shifted_black(curve, spec, implied_vol, shift), implied_vol
