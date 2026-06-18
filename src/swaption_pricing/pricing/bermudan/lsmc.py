"""Regression helpers for Longstaff-Schwartz Monte Carlo."""

from __future__ import annotations

import numpy as np


def polynomial_basis(x: np.ndarray) -> np.ndarray:
    """Return a simple `[1, x, x^2]` basis matrix."""
    return np.column_stack([np.ones_like(x), x, x * x])


def fit_continuation_regression(state_variable: np.ndarray, continuation_values: np.ndarray) -> np.ndarray:
    """Fit least-squares coefficients for continuation-value regression."""
    design_matrix = polynomial_basis(state_variable)
    coefficients, *_ = np.linalg.lstsq(design_matrix, continuation_values, rcond=None)
    return coefficients


def evaluate_continuation_value(state_variable: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """Evaluate continuation values from fitted coefficients."""
    return polynomial_basis(state_variable) @ coefficients


def polynomial_basis_vector(state_variable: float) -> list[float]:
    """Return a simple quadratic basis vector for continuation regression."""
    x = float(state_variable)
    return [1.0, x, x * x]
