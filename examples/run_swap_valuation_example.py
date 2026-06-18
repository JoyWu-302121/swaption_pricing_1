"""Value a vanilla swap under the simplified single-curve setup."""

from swaption_pricing.core import fixed_leg_pv, floating_leg_pv, forward_swap_rate, swap_present_value
from swaption_pricing.types import CurvePoint


def build_sample_curve():
    return [
        CurvePoint(maturity=1.0, zero_rate=0.0420),
        CurvePoint(maturity=2.0, zero_rate=0.0415),
        CurvePoint(maturity=3.0, zero_rate=0.0410),
        CurvePoint(maturity=4.0, zero_rate=0.0408),
        CurvePoint(maturity=5.0, zero_rate=0.0405),
        CurvePoint(maturity=6.0, zero_rate=0.0403),
        CurvePoint(maturity=7.0, zero_rate=0.0402),
    ]


def main():
    curve = build_sample_curve()
    notional = 10_000_000.0
    start = 0.0
    tenor = 5.0
    pay_frequency = 1
    par_rate = forward_swap_rate(curve, expiry=start, tenor=tenor, pay_frequency=pay_frequency)
    rich_fixed_rate = par_rate + 0.0025

    print("Vanilla Swap Example")
    print(f"Par swap rate:      {par_rate:.6f}")
    print(f"Fixed leg PV:       {fixed_leg_pv(curve, notional, rich_fixed_rate, start, tenor, pay_frequency):,.2f}")
    print(f"Floating leg PV:    {floating_leg_pv(curve, notional, start, tenor):,.2f}")
    print(f"Payer swap PV:      {swap_present_value(curve, notional, rich_fixed_rate, start, tenor, pay_frequency, 'payer'):,.2f}")
    print(f"Receiver swap PV:   {swap_present_value(curve, notional, rich_fixed_rate, start, tenor, pay_frequency, 'receiver'):,.2f}")


if __name__ == "__main__":
    main()
