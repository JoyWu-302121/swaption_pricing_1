"""Run smile and pricing scenarios for Milestone 3 SABR analysis."""

from swaption_pricing.black76 import price_swaption
from swaption_pricing.curve_bootstrap import bootstrap_zero_curve
from swaption_pricing.sabr import SabrParams, price_swaption_with_sabr, sabr_vol_surface_slice
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
    sabr_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    flat_black_vol = 0.20
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]

    print("SABR Smile Scenario")
    print("Strike     SABRVol    BlackPx      SABRPx")

    for strike, sabr_vol in sabr_vol_surface_slice(curve, 2.0, 5.0, 1, strikes, sabr_params):
        spec = SwaptionSpec(
            notional=10_000_000.0,
            expiry=2.0,
            tenor=5.0,
            strike=strike,
            pay_frequency=1,
            option_type="payer",
        )
        black_price = price_swaption(curve, spec, flat_black_vol)
        sabr_price, _ = price_swaption_with_sabr(curve, spec, sabr_params)
        print(f"{strike:0.4f}     {sabr_vol:0.4f}   {black_price:10.2f}   {sabr_price:10.2f}")

    print("\nParameter Sensitivity Snapshot")
    for label, params in [
        ("Higher alpha", SabrParams(alpha=0.0300, beta=0.50, rho=-0.25, nu=0.40)),
        ("Less negative rho", SabrParams(alpha=0.0200, beta=0.50, rho=0.10, nu=0.40)),
        ("Higher nu", SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.70)),
    ]:
        atm_spec = SwaptionSpec(
            notional=10_000_000.0,
            expiry=2.0,
            tenor=5.0,
            strike=0.0400,
            pay_frequency=1,
            option_type="payer",
        )
        price, vol = price_swaption_with_sabr(curve, atm_spec, params)
        print(f"{label:16}  ATM vol={vol:0.4f}  ATM price={price:10.2f}")


if __name__ == "__main__":
    main()

