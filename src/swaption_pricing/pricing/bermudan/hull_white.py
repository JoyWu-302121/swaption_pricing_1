"""Hull-White parameter helpers for Bermudan LSMC scaffolding."""

from __future__ import annotations

from ...types import HullWhiteParams


def hw_model_summary(params: HullWhiteParams) -> dict[str, float]:
    """Return a serializable summary of the chosen Hull-White model."""
    return {
        "mean_reversion": params.mean_reversion,
        "volatility": params.volatility,
    }
