"""Compare Black, shifted Black, and Bachelier pricing across rate regimes."""

from swaption_pricing.core import forward_swap_rate, swap_annuity
from swaption_pricing.market import bootstrap_zero_curve
from swaption_pricing.pricing.european import (
    bachelier_option_value,
    price_shifted_black,
    price_swaption,
    price_swaption_bachelier,
    price_swaption_shifted_black,
)
from swaption_pricing.types import MarketQuote, SwaptionSpec


def positive_curve_quotes():
    return [
        MarketQuote(instrument_type="deposit", maturity=1.0, rate=0.0420),
        MarketQuote(instrument_type="swap", maturity=2.0, rate=0.0415, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=3.0, rate=0.0410, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=4.0, rate=0.0408, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=5.0, rate=0.0405, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=6.0, rate=0.0403, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=7.0, rate=0.0402, pay_frequency=1),
    ]


def build_spec(strike: float, option_type: str) -> SwaptionSpec:
    return SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=strike,
        pay_frequency=1,
        option_type=option_type,
    )


def main():
    curve = bootstrap_zero_curve(positive_curve_quotes())
    black_vol = 0.20
    normal_vol = 0.01
    shift = 0.03

    print("Positive-Rate Regime")
    for option_type in ["payer", "receiver"]:
        spec = build_spec(0.0400, option_type)
        print(
            f"{option_type:8} Black={price_swaption(curve, spec, black_vol):12.2f}  "
            f"ShiftedBlack={price_swaption_shifted_black(curve, spec, black_vol, shift):12.2f}  "
            f"Bachelier={price_swaption_bachelier(curve, spec, normal_vol):12.2f}"
        )

    print("\nNegative-Rate Regime (direct forward comparison)")
    negative_forward = -0.0020
    negative_strike = -0.0010
    negative_expiry = 2.0
    negative_shift = 0.03
    for option_type in ["payer", "receiver"]:
        shifted_black_payoff = price_shifted_black(
            negative_forward, negative_strike, negative_expiry, black_vol, negative_shift, option_type
        )
        bachelier_payoff = bachelier_option_value(
            negative_forward, negative_strike, negative_expiry, normal_vol, option_type
        )
        print(
            f"{option_type:8} ShiftedBlackPayoff={shifted_black_payoff:12.8f}  "
            f"BachelierPayoff={bachelier_payoff:12.8f}"
        )


if __name__ == "__main__":
    main()
