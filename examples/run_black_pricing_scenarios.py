"""Run simple Black swaption pricing scenarios for Milestone 2."""

from swaption_pricing.black76 import intrinsic_value, moneyness_label, price_swaption, time_value
from swaption_pricing.curve_bootstrap import bootstrap_zero_curve
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
    vol = 0.20
    strikes = [0.0350, 0.0400, 0.0450]

    print("Black Swaption Scenario Analysis")
    print("Strike     Type      Label    Price         Intrinsic     TimeValue")

    for strike in strikes:
        spec = SwaptionSpec(
            notional=10_000_000.0,
            expiry=2.0,
            tenor=5.0,
            strike=strike,
            pay_frequency=1,
            option_type="payer",
        )
        label = moneyness_label(curve, spec, tolerance=0.0010)
        price = price_swaption(curve, spec, vol)
        intrinsic = intrinsic_value(curve, spec)
        extrinsic = time_value(curve, spec, vol)
        print(f"{strike:0.4f}     payer     {label:>3}   {price:11.2f}   {intrinsic:11.2f}   {extrinsic:11.2f}")

    receiver_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="receiver",
    )
    receiver_price = price_swaption(curve, receiver_spec, vol)
    receiver_intrinsic = intrinsic_value(curve, receiver_spec)
    receiver_time_value = time_value(curve, receiver_spec, vol)
    print("\nReceiver ATM-ish comparison")
    print(
        f"0.0400     receiver  {moneyness_label(curve, receiver_spec, tolerance=0.0010):>3}   "
        f"{receiver_price:11.2f}   {receiver_intrinsic:11.2f}   {receiver_time_value:11.2f}"
    )


if __name__ == "__main__":
    main()
