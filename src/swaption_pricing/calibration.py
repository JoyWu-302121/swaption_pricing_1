"""SABR calibration helpers for simplified market-vol fitting."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares

from .sabr import SabrParams, sabr_implied_volatility, shifted_sabr_implied_volatility


@dataclass(frozen=True)
class SabrCalibrationResult:
    params: SabrParams
    objective_value: float
    market_vols: tuple[float, ...]
    fitted_vols: tuple[float, ...]
    strikes: tuple[float, ...]
    success: bool
    message: str


@dataclass(frozen=True)
class CalibrationDiagnostics:
    max_abs_error: float
    mean_abs_error: float
    rmse: float


@dataclass(frozen=True)
class CalibrationRow:
    strike: float
    market_vol: float
    fitted_vol: float
    residual: float


def sabr_residuals(
    parameter_vector: np.ndarray,
    forward: float,
    strikes: np.ndarray,
    expiry: float,
    market_vols: np.ndarray,
    beta: float,
) -> np.ndarray:
    """Return strike-by-strike volatility residuals for SABR calibration."""
    params = SabrParams(
        alpha=float(parameter_vector[0]),
        beta=beta,
        rho=float(parameter_vector[1]),
        nu=float(parameter_vector[2]),
    )
    fitted = np.array([sabr_implied_volatility(forward, strike, expiry, params) for strike in strikes])
    return fitted - market_vols


def calibrate_sabr_to_vols(
    forward: float,
    strikes: list[float],
    expiry: float,
    market_vols: list[float],
    *,
    beta: float = 0.50,
    initial_guess: tuple[float, float, float] = (0.02, -0.10, 0.40),
) -> SabrCalibrationResult:
    """Calibrate alpha, rho, and nu to a strike slice of market Black vols."""
    strike_array = np.array(strikes, dtype=float)
    market_vol_array = np.array(market_vols, dtype=float)

    optimization = least_squares(
        sabr_residuals,
        x0=np.array(initial_guess, dtype=float),
        bounds=(
            np.array([1e-6, -0.999, 1e-6], dtype=float),
            np.array([5.0, 0.999, 5.0], dtype=float),
        ),
        args=(forward, strike_array, expiry, market_vol_array, beta),
    )

    calibrated_params = SabrParams(
        alpha=float(optimization.x[0]),
        beta=beta,
        rho=float(optimization.x[1]),
        nu=float(optimization.x[2]),
    )
    fitted_vols = tuple(
        sabr_implied_volatility(forward, float(strike), expiry, calibrated_params) for strike in strike_array
    )
    return SabrCalibrationResult(
        params=calibrated_params,
        objective_value=float(np.sum(optimization.fun ** 2)),
        market_vols=tuple(float(vol) for vol in market_vol_array),
        fitted_vols=fitted_vols,
        strikes=tuple(float(strike) for strike in strike_array),
        success=bool(optimization.success),
        message=optimization.message,
    )


def calibration_rows(result: SabrCalibrationResult) -> tuple[CalibrationRow, ...]:
    """Return strike-level calibration diagnostics."""
    return tuple(
        CalibrationRow(
            strike=strike,
            market_vol=market_vol,
            fitted_vol=fitted_vol,
            residual=fitted_vol - market_vol,
        )
        for strike, market_vol, fitted_vol in zip(result.strikes, result.market_vols, result.fitted_vols)
    )


def calibration_diagnostics(result: SabrCalibrationResult) -> CalibrationDiagnostics:
    """Summarize absolute and squared fitting errors."""
    residuals = np.array([row.residual for row in calibration_rows(result)], dtype=float)
    abs_residuals = np.abs(residuals)
    return CalibrationDiagnostics(
        max_abs_error=float(np.max(abs_residuals)),
        mean_abs_error=float(np.mean(abs_residuals)),
        rmse=float(np.sqrt(np.mean(residuals ** 2))),
    )


def calibrate_sabr_for_multiple_initial_guesses(
    forward: float,
    strikes: list[float],
    expiry: float,
    market_vols: list[float],
    *,
    beta: float = 0.50,
    initial_guesses: list[tuple[float, float, float]],
) -> list[SabrCalibrationResult]:
    """Run calibration from multiple initial guesses."""
    return [
        calibrate_sabr_to_vols(
            forward,
            strikes,
            expiry,
            market_vols,
            beta=beta,
            initial_guess=initial_guess,
        )
        for initial_guess in initial_guesses
    ]


def calibrate_sabr_across_beta_values(
    forward: float,
    strikes: list[float],
    expiry: float,
    market_vols: list[float],
    *,
    beta_values: list[float],
    initial_guess: tuple[float, float, float] = (0.02, -0.10, 0.40),
) -> list[SabrCalibrationResult]:
    """Run calibration for a list of fixed beta values."""
    return [
        calibrate_sabr_to_vols(
            forward,
            strikes,
            expiry,
            market_vols,
            beta=beta,
            initial_guess=initial_guess,
        )
        for beta in beta_values
    ]


def shifted_sabr_residuals(
    parameter_vector: np.ndarray,
    forward: float,
    strikes: np.ndarray,
    expiry: float,
    market_vols: np.ndarray,
    beta: float,
    shift: float,
) -> np.ndarray:
    """Return residuals for shifted-SABR calibration."""
    params = SabrParams(
        alpha=float(parameter_vector[0]),
        beta=beta,
        rho=float(parameter_vector[1]),
        nu=float(parameter_vector[2]),
    )
    fitted = np.array(
        [shifted_sabr_implied_volatility(forward, strike, expiry, params, shift) for strike in strikes]
    )
    return fitted - market_vols


def calibrate_shifted_sabr_to_vols(
    forward: float,
    strikes: list[float],
    expiry: float,
    market_vols: list[float],
    *,
    beta: float = 0.50,
    shift: float,
    initial_guess: tuple[float, float, float] = (0.02, -0.10, 0.40),
) -> SabrCalibrationResult:
    """Calibrate shifted SABR with fixed beta and shift."""
    strike_array = np.array(strikes, dtype=float)
    market_vol_array = np.array(market_vols, dtype=float)

    optimization = least_squares(
        shifted_sabr_residuals,
        x0=np.array(initial_guess, dtype=float),
        bounds=(
            np.array([1e-6, -0.999, 1e-6], dtype=float),
            np.array([5.0, 0.999, 5.0], dtype=float),
        ),
        args=(forward, strike_array, expiry, market_vol_array, beta, shift),
    )

    calibrated_params = SabrParams(
        alpha=float(optimization.x[0]),
        beta=beta,
        rho=float(optimization.x[1]),
        nu=float(optimization.x[2]),
    )
    fitted_vols = tuple(
        shifted_sabr_implied_volatility(forward, float(strike), expiry, calibrated_params, shift)
        for strike in strike_array
    )
    return SabrCalibrationResult(
        params=calibrated_params,
        objective_value=float(np.sum(optimization.fun ** 2)),
        market_vols=tuple(float(vol) for vol in market_vol_array),
        fitted_vols=fitted_vols,
        strikes=tuple(float(strike) for strike in strike_array),
        success=bool(optimization.success),
        message=optimization.message,
    )


def calibrate_shifted_sabr_across_shifts(
    forward: float,
    strikes: list[float],
    expiry: float,
    market_vols: list[float],
    *,
    beta: float = 0.50,
    shifts: list[float],
    initial_guess: tuple[float, float, float] = (0.02, -0.10, 0.40),
) -> list[tuple[float, SabrCalibrationResult]]:
    """Run shifted SABR calibration for a list of shift values."""
    return [
        (
            shift,
            calibrate_shifted_sabr_to_vols(
                forward,
                strikes,
                expiry,
                market_vols,
                beta=beta,
                shift=shift,
                initial_guess=initial_guess,
            ),
        )
        for shift in shifts
    ]
