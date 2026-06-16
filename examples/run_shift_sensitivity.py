"""Compare shifted-Black and shifted-SABR outputs across shift choices."""

from swaption_pricing.black76 import price_swaption_shifted_black
from swaption_pricing.curve_bootstrap import bootstrap_zero_curve
from swaption_pricing.sabr import SabrParams, price_swaption_with_shifted_sabr
from swaption_pricing.types import MarketQuote, SwaptionSpec


def sample_quotes():
    return [
        MarketQuote(instrument_type="deposit", maturity=1.0, rate=0.0420),
        MarketQuote(instrument_type="swap", maturity=2.0, rate=0.0415, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=3.0, rate=0.0410, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=4.0, rate=0.0408, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=5.0, rate=0.0405, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=6.0, rate=0.0403, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=7.0, rate=0.0402, pay_frequency=1),
    ]


def main():
    curve = bootstrap_zero_curve(sample_quotes())
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    shifts = [0.01, 0.02, 0.03, 0.05]

    payer_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    receiver_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="receiver",
    )

    print("Shift Sensitivity")
    print("Shift     Type       ShiftedBlack    ShiftedSABRVol    ShiftedSABR")

    for shift in shifts:
        for spec in [payer_spec, receiver_spec]:
            shifted_black = price_swaption_shifted_black(curve, spec, vol=0.20, shift=shift)
            shifted_sabr_price, shifted_sabr_vol = price_swaption_with_shifted_sabr(curve, spec, params, shift)
            print(
                f"{shift:0.4f}    {spec.option_type:8}  "
                f"{shifted_black:12.2f}    {shifted_sabr_vol:0.6f}      {shifted_sabr_price:12.2f}"
            )


if __name__ == "__main__":
    main()

