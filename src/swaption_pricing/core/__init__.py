"""Core product-agnostic rates analytics."""

from .swap import (
    curve_discount_factor,
    fixed_leg_pv,
    floating_leg_pv,
    forward_swap_rate,
    payment_schedule,
    swap_annuity,
    swap_present_value,
)

__all__ = [
    "curve_discount_factor",
    "fixed_leg_pv",
    "floating_leg_pv",
    "forward_swap_rate",
    "payment_schedule",
    "swap_annuity",
    "swap_present_value",
]
