"""Hull-White helpers for Bermudan LSMC scaffolding."""

from __future__ import annotations

import numpy as np

from ...types import Curve, HullWhiteParams, MonteCarloConfig
from .monte_carlo import apply_antithetic_variates, build_time_grid, generate_standard_normal_draws


def initial_short_rate(curve: Curve) -> float:
    """Use the first curve node as a simple initial short-rate proxy."""
    if not curve:
        raise ValueError("curve must not be empty")
    return curve[0].zero_rate


def simulate_short_rate_paths(
    curve: Curve,
    params: HullWhiteParams,
    config: MonteCarloConfig,
    maturity: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a time grid and short-rate paths under a simple Euler scheme."""
    time_grid = build_time_grid(maturity, config.delta_time)
    dt = np.diff(time_grid)
    draws = generate_standard_normal_draws(config, len(dt))
    if config.antithetic:
        draws = apply_antithetic_variates(draws)

    rate_paths = np.zeros((draws.shape[0], len(time_grid)))
    short_rate_0 = initial_short_rate(curve)
    rate_paths[:, 0] = short_rate_0

    for step_index, step_dt in enumerate(dt, start=1):
        previous = rate_paths[:, step_index - 1]
        drift = params.mean_reversion * (short_rate_0 - previous) * step_dt
        diffusion = params.volatility * np.sqrt(step_dt) * draws[:, step_index - 1]
        rate_paths[:, step_index] = previous + drift + diffusion

    return time_grid, rate_paths


def hw_model_summary(params: HullWhiteParams) -> dict[str, float]:
    """Return a serializable summary of the chosen Hull-White model."""
    return {
        "mean_reversion": params.mean_reversion,
        "volatility": params.volatility,
    }
