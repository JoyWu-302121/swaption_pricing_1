"""Compare pricing and risk outputs under Black and SABR-adjusted pricing."""

from swaption_pricing.risk import compare_black_and_sabr_risk
from swaption_pricing.sabr import SabrParams
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
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    result = compare_black_and_sabr_risk(
        curve=curve,
        spec=spec,
        black_vol=0.20,
        sabr_params=SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40),
    )

    print("Black vs SABR Risk Comparison")
    print(f"Black price: {result.black_price:,.2f} at vol {result.black_vol:.4f}")
    print(f"SABR price:  {result.sabr_price:,.2f} at implied vol {result.sabr_vol:.4f}")
    print(
        "Black risk: "
        f"PV01={result.black_risk.pv01:,.2f}, "
        f"Vega={result.black_risk.vega:,.2f}, "
        f"Theta={result.black_risk.theta:,.2f}"
    )
    print(
        "SABR risk:  "
        f"PV01={result.sabr_risk.pv01:,.2f}, "
        f"AlphaRisk={result.sabr_risk.vega:,.2f}, "
        f"Theta={result.sabr_risk.theta:,.2f}"
    )


if __name__ == "__main__":
    main()
