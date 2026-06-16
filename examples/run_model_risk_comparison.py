"""Compare risk and simple hedging results across all pricing models."""

from swaption_pricing.hedging import compare_model_hedging
from swaption_pricing.risk import compare_all_model_risks
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
    sabr_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    black_vol = 0.20
    shift = 0.03
    normal_vol = 0.01
    rate_shift = 0.0025

    risk_comparison = compare_all_model_risks(
        curve=curve,
        spec=spec,
        black_vol=black_vol,
        sabr_params=sabr_params,
        shift=shift,
        normal_vol=normal_vol,
    )
    hedging_comparison = compare_model_hedging(
        curve=curve,
        spec=spec,
        black_vol=black_vol,
        sabr_params=sabr_params,
        shift=shift,
        normal_vol=normal_vol,
        rate_shift=rate_shift,
    )

    risk_rows = [
        risk_comparison.black,
        risk_comparison.sabr,
        risk_comparison.shifted_black,
        risk_comparison.shifted_sabr,
        risk_comparison.bachelier,
    ]
    hedge_rows = [
        hedging_comparison.black,
        hedging_comparison.sabr,
        hedging_comparison.shifted_black,
        hedging_comparison.shifted_sabr,
        hedging_comparison.bachelier,
    ]

    print("Model Risk Comparison")
    print("Model           Price          Vol        PV01         Vega        Theta")
    for row in risk_rows:
        print(
            f"{row.model:14}{row.price:12,.2f}  {row.volatility:8.4f}  "
            f"{row.risk.pv01:10,.2f}  {row.risk.vega:11,.2f}  {row.risk.theta:11,.2f}"
        )

    print("\nSimple PV01 Hedge Comparison")
    print("Model           HedgeRatio      UnhedgedPnL      HedgePnL        HedgedPnL")
    for row in hedge_rows:
        print(
            f"{row.model:14}{row.hedge_ratio:12,.2f}  {row.unhedged_pnl:14,.2f}  "
            f"{row.hedge_pnl:12,.2f}  {row.hedged_pnl:12,.2f}"
        )


if __name__ == "__main__":
    main()
