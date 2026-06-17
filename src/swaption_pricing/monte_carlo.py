"""Monte Carlo helpers for the Bermudan LSMC prototype."""

from __future__ import annotations

from math import ceil

import numpy as np

from .types import MonteCarloConfig


def build_time_grid(maturity: float, delta_time: float) -> np.ndarray:
    """Return a uniform time grid from zero to maturity."""
    if maturity <= 0.0:
        raise ValueError("maturity must be positive")
    if delta_time <= 0.0:
        raise ValueError("delta_time must be positive")

    num_steps = max(1, ceil(maturity / delta_time))
    return np.linspace(0.0, maturity, num_steps + 1)


def generate_standard_normal_draws(config: MonteCarloConfig, num_steps: int) -> np.ndarray:
    """Return standard normal draws for path simulation."""
    rng = np.random.default_rng(config.seed)
    return rng.standard_normal((config.num_paths, num_steps))


def apply_antithetic_variates(draws: np.ndarray) -> np.ndarray:
    """Double the path set using antithetic shocks."""
    return np.vstack([draws, -draws])
