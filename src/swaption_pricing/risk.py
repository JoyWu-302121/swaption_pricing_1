"""Finite-difference risk calculations for the pricing engine."""

from __future__ import annotations

from dataclasses import replace

from .bachelier import price_swaption_bachelier
from .black76 import price_swaption, price_swaption_shifted_black
from .sabr import SabrParams, price_swaption_with_sabr, price_swaption_with_shifted_sabr
from .types import (
    Curve,
    ModelComparisonResult,
    ModelRiskSummary,
    MultiModelRiskComparison,
    RiskResult,
    SwaptionSpec,
)


def parallel_shift_curve(curve: Curve, shift: float) -> list:
    """Apply a parallel shift to all zero rates."""
    return [replace(point, zero_rate=point.zero_rate + shift) for point in curve]


def price_with_curve_shift(curve: Curve, spec: SwaptionSpec, vol: float, shift: float) -> float:
    shifted_curve = parallel_shift_curve(curve, shift)
    return price_swaption(shifted_curve, spec, vol)


def calculate_risk(curve: Curve, spec: SwaptionSpec, vol: float, rate_bump: float = 1e-4, vol_bump: float = 1e-4) -> RiskResult:
    """Compute simple finite-difference PV01, vega, and theta."""
    base_price = price_swaption(curve, spec, vol)
    up_curve = price_with_curve_shift(curve, spec, vol, rate_bump)
    down_curve = price_with_curve_shift(curve, spec, vol, -rate_bump)
    pv01 = (down_curve - up_curve) / 2.0

    up_vol = price_swaption(curve, spec, vol + vol_bump)
    down_vol = price_swaption(curve, spec, vol - vol_bump)
    vega = (up_vol - down_vol) / (2.0 * vol_bump)

    theta_spec = replace(spec, expiry=max(spec.expiry - 1.0 / 252.0, 1e-8))
    theta = price_swaption(curve, theta_spec, vol) - base_price
    return RiskResult(pv01=pv01, vega=vega, theta=theta)


def calculate_shifted_black_risk(
    curve: Curve,
    spec: SwaptionSpec,
    vol: float,
    shift: float,
    rate_bump: float = 1e-4,
    vol_bump: float = 1e-4,
) -> RiskResult:
    """Compute PV01, vega, and theta under shifted-Black pricing."""
    base_price = price_swaption_shifted_black(curve, spec, vol, shift)
    up_curve = price_swaption_shifted_black(parallel_shift_curve(curve, rate_bump), spec, vol, shift)
    down_curve = price_swaption_shifted_black(parallel_shift_curve(curve, -rate_bump), spec, vol, shift)
    pv01 = (down_curve - up_curve) / 2.0

    up_vol = price_swaption_shifted_black(curve, spec, vol + vol_bump, shift)
    down_vol = price_swaption_shifted_black(curve, spec, max(vol - vol_bump, 1e-8), shift)
    vega = (up_vol - down_vol) / (2.0 * vol_bump)

    theta_spec = replace(spec, expiry=max(spec.expiry - 1.0 / 252.0, 1e-8))
    theta = price_swaption_shifted_black(curve, theta_spec, vol, shift) - base_price
    return RiskResult(pv01=pv01, vega=vega, theta=theta)


def calculate_sabr_risk(
    curve: Curve,
    spec: SwaptionSpec,
    params: SabrParams,
    rate_bump: float = 1e-4,
    alpha_bump: float = 1e-4,
) -> RiskResult:
    """Compute PV01, alpha sensitivity, and theta under SABR-adjusted pricing."""
    base_price, _ = price_swaption_with_sabr(curve, spec, params)
    up_curve, _ = price_swaption_with_sabr(parallel_shift_curve(curve, rate_bump), spec, params)
    down_curve, _ = price_swaption_with_sabr(parallel_shift_curve(curve, -rate_bump), spec, params)
    pv01 = (down_curve - up_curve) / 2.0

    up_params = replace(params, alpha=params.alpha + alpha_bump)
    down_params = replace(params, alpha=max(params.alpha - alpha_bump, 1e-8))
    up_alpha, _ = price_swaption_with_sabr(curve, spec, up_params)
    down_alpha, _ = price_swaption_with_sabr(curve, spec, down_params)
    vega = (up_alpha - down_alpha) / (2.0 * alpha_bump)

    theta_spec = replace(spec, expiry=max(spec.expiry - 1.0 / 252.0, 1e-8))
    theta, _ = price_swaption_with_sabr(curve, theta_spec, params)
    return RiskResult(pv01=pv01, vega=vega, theta=theta - base_price)


def calculate_shifted_sabr_risk(
    curve: Curve,
    spec: SwaptionSpec,
    params: SabrParams,
    shift: float,
    rate_bump: float = 1e-4,
    alpha_bump: float = 1e-4,
) -> RiskResult:
    """Compute PV01, alpha sensitivity, and theta under shifted-SABR pricing."""
    base_price, _ = price_swaption_with_shifted_sabr(curve, spec, params, shift)
    up_curve, _ = price_swaption_with_shifted_sabr(parallel_shift_curve(curve, rate_bump), spec, params, shift)
    down_curve, _ = price_swaption_with_shifted_sabr(parallel_shift_curve(curve, -rate_bump), spec, params, shift)
    pv01 = (down_curve - up_curve) / 2.0

    up_params = replace(params, alpha=params.alpha + alpha_bump)
    down_params = replace(params, alpha=max(params.alpha - alpha_bump, 1e-8))
    up_alpha, _ = price_swaption_with_shifted_sabr(curve, spec, up_params, shift)
    down_alpha, _ = price_swaption_with_shifted_sabr(curve, spec, down_params, shift)
    vega = (up_alpha - down_alpha) / (2.0 * alpha_bump)

    theta_spec = replace(spec, expiry=max(spec.expiry - 1.0 / 252.0, 1e-8))
    theta, _ = price_swaption_with_shifted_sabr(curve, theta_spec, params, shift)
    return RiskResult(pv01=pv01, vega=vega, theta=theta - base_price)


def calculate_bachelier_risk(
    curve: Curve,
    spec: SwaptionSpec,
    normal_vol: float,
    rate_bump: float = 1e-4,
    vol_bump: float = 1e-4,
) -> RiskResult:
    """Compute PV01, normal-vega, and theta under Bachelier pricing."""
    base_price = price_swaption_bachelier(curve, spec, normal_vol)
    up_curve = price_swaption_bachelier(parallel_shift_curve(curve, rate_bump), spec, normal_vol)
    down_curve = price_swaption_bachelier(parallel_shift_curve(curve, -rate_bump), spec, normal_vol)
    pv01 = (down_curve - up_curve) / 2.0

    up_vol = price_swaption_bachelier(curve, spec, normal_vol + vol_bump)
    down_vol = price_swaption_bachelier(curve, spec, max(normal_vol - vol_bump, 1e-8))
    vega = (up_vol - down_vol) / (2.0 * vol_bump)

    theta_spec = replace(spec, expiry=max(spec.expiry - 1.0 / 252.0, 1e-8))
    theta = price_swaption_bachelier(curve, theta_spec, normal_vol) - base_price
    return RiskResult(pv01=pv01, vega=vega, theta=theta)


def compare_black_and_sabr_risk(
    curve: Curve,
    spec: SwaptionSpec,
    black_vol: float,
    sabr_params: SabrParams,
) -> ModelComparisonResult:
    """Return pricing and finite-difference risk outputs for both models."""
    black_price = price_swaption(curve, spec, black_vol)
    sabr_price, sabr_vol = price_swaption_with_sabr(curve, spec, sabr_params)
    return ModelComparisonResult(
        black_price=black_price,
        black_vol=black_vol,
        sabr_price=sabr_price,
        sabr_vol=sabr_vol,
        black_risk=calculate_risk(curve, spec, black_vol),
        sabr_risk=calculate_sabr_risk(curve, spec, sabr_params),
    )


def compare_all_model_risks(
    curve: Curve,
    spec: SwaptionSpec,
    black_vol: float,
    sabr_params: SabrParams,
    shift: float,
    normal_vol: float,
) -> MultiModelRiskComparison:
    """Return price and risk summaries across all pricing models in the project."""
    black_price = price_swaption(curve, spec, black_vol)
    sabr_price, sabr_vol = price_swaption_with_sabr(curve, spec, sabr_params)
    shifted_black_price = price_swaption_shifted_black(curve, spec, black_vol, shift)
    shifted_sabr_price, shifted_sabr_vol = price_swaption_with_shifted_sabr(curve, spec, sabr_params, shift)
    bachelier_price = price_swaption_bachelier(curve, spec, normal_vol)

    return MultiModelRiskComparison(
        black=ModelRiskSummary(
            model="black",
            price=black_price,
            volatility=black_vol,
            risk=calculate_risk(curve, spec, black_vol),
        ),
        sabr=ModelRiskSummary(
            model="sabr",
            price=sabr_price,
            volatility=sabr_vol,
            risk=calculate_sabr_risk(curve, spec, sabr_params),
        ),
        shifted_black=ModelRiskSummary(
            model="shifted_black",
            price=shifted_black_price,
            volatility=black_vol,
            risk=calculate_shifted_black_risk(curve, spec, black_vol, shift),
        ),
        shifted_sabr=ModelRiskSummary(
            model="shifted_sabr",
            price=shifted_sabr_price,
            volatility=shifted_sabr_vol,
            risk=calculate_shifted_sabr_risk(curve, spec, sabr_params, shift),
        ),
        bachelier=ModelRiskSummary(
            model="bachelier",
            price=bachelier_price,
            volatility=normal_vol,
            risk=calculate_bachelier_risk(curve, spec, normal_vol),
        ),
    )
