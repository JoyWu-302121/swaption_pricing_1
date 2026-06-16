"""Calibrate SABR parameters to a synthetic volatility smile."""

from swaption_pricing.calibration import calibrate_sabr_to_vols
from swaption_pricing.sabr import SabrParams, sabr_implied_volatility


def main():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]

    result = calibrate_sabr_to_vols(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        initial_guess=(0.0180, -0.10, 0.30),
    )

    print("SABR Calibration Example")
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(
        "Params: "
        f"alpha={result.params.alpha:.6f}, "
        f"beta={result.params.beta:.2f}, "
        f"rho={result.params.rho:.6f}, "
        f"nu={result.params.nu:.6f}"
    )
    print(f"Objective value: {result.objective_value:.12f}")
    print("Strike     MarketVol    FittedVol")
    for strike, market_vol, fitted_vol in zip(result.strikes, result.market_vols, result.fitted_vols):
        print(f"{strike:0.4f}     {market_vol:0.6f}    {fitted_vol:0.6f}")


if __name__ == "__main__":
    main()

