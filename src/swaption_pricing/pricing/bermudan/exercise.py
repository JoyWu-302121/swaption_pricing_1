"""Exercise-date helpers for Bermudan swaption workflows."""

from __future__ import annotations

from ...types import BermudanSwaptionSpec


def bermudan_exercise_schedule(spec: BermudanSwaptionSpec) -> list[float]:
    """Return sorted exercise dates from the Bermudan specification."""
    return sorted(float(date) for date in spec.exercise_dates)


def coterminal_tenors(spec: BermudanSwaptionSpec) -> list[float]:
    """Return co-terminal European swap tenors used for Bermudan calibration."""
    return [max(spec.maturity - exercise_date, 0.0) for exercise_date in bermudan_exercise_schedule(spec)]
