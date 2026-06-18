"""Bootstrap simplified curve nodes and expand them into a daily zero curve."""

from swaption_pricing.market import bootstrap_zero_curve, build_daily_zero_curve
from swaption_pricing.types import MarketQuote


def sample_quotes():
    return [
        MarketQuote(instrument_type="deposit", maturity=1.0, rate=0.0420),
        MarketQuote(instrument_type="swap", maturity=2.0, rate=0.0415, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=3.0, rate=0.0410, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=4.0, rate=0.0408, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=5.0, rate=0.0405, pay_frequency=1),
    ]


def main():
    curve_nodes = bootstrap_zero_curve(sample_quotes())
    daily_curve = build_daily_zero_curve(curve_nodes, last_maturity=5.0)

    print("Bootstrapped Curve Nodes")
    for point in curve_nodes:
        print(f"{point.maturity:>4.1f}Y  zero={point.zero_rate:.6f}")

    print("\nDaily Curve Sample")
    for point in daily_curve[:3] + daily_curve[364:367] + daily_curve[-3:]:
        print(f"{point.maturity:>7.4f}Y  zero={point.zero_rate:.6f}")


if __name__ == "__main__":
    main()
