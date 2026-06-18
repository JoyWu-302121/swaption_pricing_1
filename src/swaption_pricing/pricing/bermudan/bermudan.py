"""High-level Bermudan pricing and calibration helpers for market-style workflows."""

from __future__ import annotations

import numpy as np

from ...types import BermudanSwaptionSpec, SwaptionVolQuote
from ...types import BermudanLSMCResult, Curve, HullWhiteParams, MonteCarloConfig
from .exercise import coterminal_tenors, immediate_exercise_values, validate_exercise_dates
from .hull_white import simulate_short_rate_paths


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


def bermudan_lsmc_skeleton_summary(
    curve: Curve,
    spec: BermudanSwaptionSpec,
    hw_params: HullWhiteParams,
    mc_config: MonteCarloConfig,
) -> dict[str, object]:
    """Return a summary of the planned Bermudan LSMC setup."""
    exercise_dates = validate_exercise_dates(spec)
    time_grid, rate_paths = simulate_short_rate_paths(curve, hw_params, mc_config, spec.maturity)
    exercise_values = immediate_exercise_values(curve, spec)
    return {
        "num_paths": int(rate_paths.shape[0]),
        "num_time_points": int(len(time_grid)),
        "exercise_dates": exercise_dates,
        "immediate_exercise_values": exercise_values.tolist(),
    }


def price_bermudan_swaption_lsmc(
    curve: Curve,
    spec: BermudanSwaptionSpec,
    hw_params: HullWhiteParams,
    mc_config: MonteCarloConfig,
) -> BermudanLSMCResult:
    """Placeholder Bermudan pricing API for the upcoming LSMC implementation."""
    _ = bermudan_lsmc_skeleton_summary(curve, spec, hw_params, mc_config)
    raise NotImplementedError(
        "Bermudan LSMC pricing is not implemented yet. "
        "This milestone currently provides the architecture and simulation skeleton."
    )


def empty_lsmc_result(time_grid: np.ndarray, num_exercise_dates: int) -> BermudanLSMCResult:
    """Return a zeroed Bermudan result container for future incremental development."""
    return BermudanLSMCResult(
        price=0.0,
        exercise_probabilities=[0.0] * num_exercise_dates,
        exercise_counts=[0] * num_exercise_dates,
        time_grid=time_grid.tolist(),
    )
