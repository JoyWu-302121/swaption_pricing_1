"""Compare flat-vol Black pricing against SABR-adjusted pricing."""

from swaption_pricing.pricing.european import SabrParams, price_swaption, price_swaption_with_sabr
from swaption_pricing.core import forward_swap_rate
from swaption_pricing.types import CurvePoint, SwaptionSpec


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
    strikes = [0.0350, 0.0400, 0.0450]
    sabr_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    flat_black_vol = 0.20

    print("Black vs SABR Comparison")
    print("Strike     Forward    FlatVolPx    SABRVol    SABRPx")

    for strike in strikes:
        spec = SwaptionSpec(
            notional=10_000_000.0,
            expiry=2.0,
            tenor=5.0,
            strike=strike,
            pay_frequency=1,
            option_type="payer",
        )
        forward = forward_swap_rate(curve, spec.expiry, spec.tenor, spec.pay_frequency)
        black_price = price_swaption(curve, spec, flat_black_vol)
        sabr_price, sabr_vol = price_swaption_with_sabr(curve, spec, sabr_params)
        print(f"{strike:0.4f}     {forward:0.4f}     {black_price:10.2f}   {sabr_vol:0.4f}   {sabr_price:10.2f}")


if __name__ == "__main__":
    main()
