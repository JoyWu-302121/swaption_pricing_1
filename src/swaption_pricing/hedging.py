"""Basic swaption hedging utilities."""

from __future__ import annotations

from collections.abc import Callable

from .bachelier import price_swaption_bachelier
from .black76 import price_swaption, price_swaption_shifted_black
from .risk import (
    calculate_bachelier_risk,
    calculate_risk,
    calculate_sabr_risk,
    calculate_shifted_black_risk,
    calculate_shifted_sabr_risk,
    parallel_shift_curve,
    price_with_curve_shift,
)
from .sabr import SabrParams, price_swaption_with_sabr, price_swaption_with_shifted_sabr
from .swap import forward_swap_rate, swap_present_value
from .types import Curve, HedgeEvaluation, MultiModelHedgingComparison, SwaptionSpec


def hedge_ratio_from_pv01(target_pv01: float, hedge_instrument_pv01: float) -> float:
    """Return the hedge notionals required to offset PV01."""
    if hedge_instrument_pv01 == 0:
        raise ZeroDivisionError("hedge_instrument_pv01 must be non-zero")
    return -target_pv01 / hedge_instrument_pv01


def shocked_pnl(curve: Curve, spec: SwaptionSpec, vol: float, rate_shift: float) -> float:
    """Return the swaption price change under a parallel curve shock."""
    base = price_with_curve_shift(curve, spec, vol, 0.0)
    shocked = price_with_curve_shift(curve, spec, vol, rate_shift)
    return shocked - base


def swap_price_with_curve_shift(
    curve: Curve,
    notional: float,
    fixed_rate: float,
    start: float,
    tenor: float,
    pay_frequency: int,
    swap_type: str,
    rate_shift: float,
) -> float:
    """Return the swap PV after a parallel shift to the zero curve."""
    shifted_curve = parallel_shift_curve(curve, rate_shift)
    return swap_present_value(shifted_curve, notional, fixed_rate, start, tenor, pay_frequency, swap_type)


def swap_pv01(
    curve: Curve,
    notional: float,
    fixed_rate: float,
    start: float,
    tenor: float,
    pay_frequency: int,
    swap_type: str,
    rate_bump: float = 1e-4,
) -> float:
    """Compute swap PV01 via parallel finite differences."""
    up_value = swap_price_with_curve_shift(curve, notional, fixed_rate, start, tenor, pay_frequency, swap_type, rate_bump)
    down_value = swap_price_with_curve_shift(curve, notional, fixed_rate, start, tenor, pay_frequency, swap_type, -rate_bump)
    return (down_value - up_value) / 2.0


def swap_shocked_pnl(
    curve: Curve,
    notional: float,
    fixed_rate: float,
    start: float,
    tenor: float,
    pay_frequency: int,
    swap_type: str,
    rate_shift: float,
) -> float:
    """Return swap PnL under a parallel curve shock."""
    base = swap_present_value(curve, notional, fixed_rate, start, tenor, pay_frequency, swap_type)
    shocked = swap_price_with_curve_shift(curve, notional, fixed_rate, start, tenor, pay_frequency, swap_type, rate_shift)
    return shocked - base


def _generic_shocked_pnl(curve: Curve, price_fn: Callable[[Curve], float], rate_shift: float) -> float:
    """Return model price PnL under a parallel shift using a pricing closure."""
    return price_fn(parallel_shift_curve(curve, rate_shift)) - price_fn(curve)


def evaluate_swap_hedge(
    curve: Curve,
    price_fn: Callable[[Curve], float],
    target_pv01: float,
    hedge_start: float,
    hedge_tenor: float,
    pay_frequency: int,
    rate_shift: float,
    hedge_swap_type: str = "payer",
    model_name: str = "generic",
) -> HedgeEvaluation:
    """Evaluate a simple PV01 hedge using a forward-starting underlying swap."""
    hedge_rate = forward_swap_rate(curve, hedge_start, hedge_tenor, pay_frequency)
    hedge_instrument_pv01 = swap_pv01(
        curve=curve,
        notional=1.0,
        fixed_rate=hedge_rate,
        start=hedge_start,
        tenor=hedge_tenor,
        pay_frequency=pay_frequency,
        swap_type=hedge_swap_type,
    )
    hedge_ratio = hedge_ratio_from_pv01(target_pv01, hedge_instrument_pv01)
    unhedged_pnl = _generic_shocked_pnl(curve, price_fn, rate_shift)
    hedge_pnl = hedge_ratio * swap_shocked_pnl(
        curve=curve,
        notional=1.0,
        fixed_rate=hedge_rate,
        start=hedge_start,
        tenor=hedge_tenor,
        pay_frequency=pay_frequency,
        swap_type=hedge_swap_type,
        rate_shift=rate_shift,
    )
    return HedgeEvaluation(
        model=model_name,
        hedge_rate=hedge_rate,
        hedge_instrument_pv01=hedge_instrument_pv01,
        hedge_ratio=hedge_ratio,
        unhedged_pnl=unhedged_pnl,
        hedge_pnl=hedge_pnl,
        hedged_pnl=unhedged_pnl + hedge_pnl,
    )


def compare_model_hedging(
    curve: Curve,
    spec: SwaptionSpec,
    black_vol: float,
    sabr_params: SabrParams,
    shift: float,
    normal_vol: float,
    rate_shift: float,
    hedge_swap_type: str = "payer",
) -> MultiModelHedgingComparison:
    """Compare simple PV01 hedging performance across all pricing models."""
    black_eval = evaluate_swap_hedge(
        curve=curve,
        price_fn=lambda c: price_swaption(c, spec, black_vol),
        target_pv01=calculate_risk(curve, spec, black_vol).pv01,
        hedge_start=spec.expiry,
        hedge_tenor=spec.tenor,
        pay_frequency=spec.pay_frequency,
        rate_shift=rate_shift,
        hedge_swap_type=hedge_swap_type,
        model_name="black",
    )
    sabr_eval = evaluate_swap_hedge(
        curve=curve,
        price_fn=lambda c: price_swaption_with_sabr(c, spec, sabr_params)[0],
        target_pv01=calculate_sabr_risk(curve, spec, sabr_params).pv01,
        hedge_start=spec.expiry,
        hedge_tenor=spec.tenor,
        pay_frequency=spec.pay_frequency,
        rate_shift=rate_shift,
        hedge_swap_type=hedge_swap_type,
        model_name="sabr",
    )
    shifted_black_eval = evaluate_swap_hedge(
        curve=curve,
        price_fn=lambda c: price_swaption_shifted_black(c, spec, black_vol, shift),
        target_pv01=calculate_shifted_black_risk(curve, spec, black_vol, shift).pv01,
        hedge_start=spec.expiry,
        hedge_tenor=spec.tenor,
        pay_frequency=spec.pay_frequency,
        rate_shift=rate_shift,
        hedge_swap_type=hedge_swap_type,
        model_name="shifted_black",
    )
    shifted_sabr_eval = evaluate_swap_hedge(
        curve=curve,
        price_fn=lambda c: price_swaption_with_shifted_sabr(c, spec, sabr_params, shift)[0],
        target_pv01=calculate_shifted_sabr_risk(curve, spec, sabr_params, shift).pv01,
        hedge_start=spec.expiry,
        hedge_tenor=spec.tenor,
        pay_frequency=spec.pay_frequency,
        rate_shift=rate_shift,
        hedge_swap_type=hedge_swap_type,
        model_name="shifted_sabr",
    )
    bachelier_eval = evaluate_swap_hedge(
        curve=curve,
        price_fn=lambda c: price_swaption_bachelier(c, spec, normal_vol),
        target_pv01=calculate_bachelier_risk(curve, spec, normal_vol).pv01,
        hedge_start=spec.expiry,
        hedge_tenor=spec.tenor,
        pay_frequency=spec.pay_frequency,
        rate_shift=rate_shift,
        hedge_swap_type=hedge_swap_type,
        model_name="bachelier",
    )

    return MultiModelHedgingComparison(
        black=black_eval,
        sabr=sabr_eval,
        shifted_black=shifted_black_eval,
        shifted_sabr=shifted_sabr_eval,
        bachelier=bachelier_eval,
    )
