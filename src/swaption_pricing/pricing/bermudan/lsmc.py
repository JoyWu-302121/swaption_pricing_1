"""Regression helpers for Longstaff-Schwartz Monte Carlo."""

from __future__ import annotations


def polynomial_basis_vector(state_variable: float) -> list[float]:
    """Return a simple quadratic basis vector for continuation regression."""
    x = float(state_variable)
    return [1.0, x, x * x]
