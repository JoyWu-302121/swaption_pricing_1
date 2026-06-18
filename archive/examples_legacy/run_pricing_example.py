"""Minimal example for pricing a USD European payer swaption."""

from swaption_pricing.pricing.european import price_swaption
from swaption_pricing.risk import calculate_risk
from swaption_pricing.core import forward_swap_rate, swap_annuity
from swaption_pricing.types import CurvePoint, SwaptionSpec


def build_sample_curve():
    """Return a small synthetic USD zero curve for initial testing."""
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
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    vol = 0.20

    forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    annuity = swap_annuity(curve, spec.expiry, spec.tenor, spec.pay_frequency)
    price = price_swaption(curve, spec, vol)
    risk = calculate_risk(curve, spec, vol)

    print("Swaption Example")
    print(f"Forward swap rate: {forward:.6f}")
    print(f"Swap annuity:      {annuity:.6f}")
    print(f"Price:             {price:,.2f}")
    print(f"PV01:              {risk.pv01:,.2f}")
    print(f"Vega:              {risk.vega:,.2f}")
    print(f"Theta:             {risk.theta:,.2f}")


if __name__ == "__main__":
    main()
