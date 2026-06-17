"""Monte Carlo scaffolding for Bermudan LSMC pricing."""

from __future__ import annotations

from ...types import BermudanSwaptionSpec, MonteCarloConfig
from .exercise import bermudan_exercise_schedule


def build_lsmc_time_grid(spec: BermudanSwaptionSpec, config: MonteCarloConfig) -> list[float]:
    """Build a simulation grid aligned to exercise dates and maturity."""
    grid = {0.0, spec.maturity}
    grid.update(bermudan_exercise_schedule(spec))
    step = config.delta_time
    current = 0.0
    while current < spec.maturity:
        current = round(current + step, 10)
        if current <= spec.maturity:
            grid.add(current)
    return sorted(grid)
