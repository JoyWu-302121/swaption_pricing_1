"""Hull-White one-factor path simulation skeleton for Bermudan pricing."""

from __future__ import annotations

import numpy as np

from .monte_carlo import apply_antithetic_variates, build_time_grid, generate_standard_normal_draws
from .types import Curve, HullWhiteParams, MonteCarloConfig


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
    rate_paths[:, 0] = initial_short_rate(curve)

    for step_index, step_dt in enumerate(dt, start=1):
        previous = rate_paths[:, step_index - 1]
        drift = params.mean_reversion * (initial_short_rate(curve) - previous) * step_dt
        diffusion = params.volatility * np.sqrt(step_dt) * draws[:, step_index - 1]
        rate_paths[:, step_index] = previous + drift + diffusion

    return time_grid, rate_paths
