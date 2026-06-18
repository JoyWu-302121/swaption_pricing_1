"""Exercise-date and payoff helpers for Bermudan swaption workflows."""

from __future__ import annotations

import numpy as np

from ...core.swap import swap_present_value
from ...types import BermudanSwaptionSpec, Curve


def validate_exercise_dates(spec: BermudanSwaptionSpec) -> list[float]:
    """Return sorted exercise dates and validate the Bermudan specification."""
    exercise_dates = sorted(float(date) for date in spec.exercise_dates)
    if not exercise_dates:
        raise ValueError("exercise_dates must not be empty")
    if exercise_dates[-1] >= spec.maturity:
        raise ValueError("final exercise date must be strictly before maturity")
    return exercise_dates


def bermudan_exercise_schedule(spec: BermudanSwaptionSpec) -> list[float]:
    """Return the validated Bermudan exercise schedule."""
    return validate_exercise_dates(spec)


def exercise_payoff_from_swap_value(swap_value: float, option_type: str) -> float:
    """Convert a swap value into immediate Bermudan exercise payoff."""
    direction = option_type.lower()
    if direction == "payer":
        return max(swap_value, 0.0)
    if direction == "receiver":
        return max(-swap_value, 0.0)
    raise ValueError("option_type must be 'payer' or 'receiver'")


def coterminal_tenors(spec: BermudanSwaptionSpec) -> list[float]:
    """Return co-terminal European swap tenors used for Bermudan calibration."""
    return [max(spec.maturity - exercise_date, 0.0) for exercise_date in bermudan_exercise_schedule(spec)]


def immediate_exercise_values(curve: Curve, spec: BermudanSwaptionSpec) -> np.ndarray:
    """Return deterministic exercise values under the current curve as a placeholder."""
    values = []
    for exercise_date in validate_exercise_dates(spec):
        remaining_tenor = max(spec.maturity - exercise_date, 0.0)
        swap_value = swap_present_value(
            curve=curve,
            notional=spec.notional,
            fixed_rate=spec.strike,
            start=exercise_date,
            tenor=remaining_tenor,
            pay_frequency=spec.pay_frequency,
            swap_type=spec.option_type,
        )
        values.append(exercise_payoff_from_swap_value(swap_value, spec.option_type))
    return np.array(values, dtype=float)
