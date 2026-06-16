"""Run calibration diagnostics for Milestone 4."""

from swaption_pricing.calibration import (
    calibrate_sabr_across_beta_values,
    calibrate_sabr_for_multiple_initial_guesses,
    calibrate_sabr_to_vols,
    calibration_diagnostics,
    calibration_rows,
)
from swaption_pricing.black76 import price_shifted_black
from swaption_pricing.sabr import SabrParams, sabr_implied_volatility, shifted_sabr_implied_volatility


def main():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]

    base = calibrate_sabr_to_vols(forward, strikes, expiry, market_vols, beta=0.50, initial_guess=(0.0180, -0.10, 0.30))
    diagnostics = calibration_diagnostics(base)

    print("Base Calibration")
    print(
        f"alpha={base.params.alpha:.6f}, beta={base.params.beta:.2f}, "
        f"rho={base.params.rho:.6f}, nu={base.params.nu:.6f}"
    )
    print(
        f"objective={base.objective_value:.12f}, "
        f"max_abs_error={diagnostics.max_abs_error:.12f}, "
        f"rmse={diagnostics.rmse:.12f}"
    )
    print("Strike     MarketVol    FittedVol    Residual")
    for row in calibration_rows(base):
        print(f"{row.strike:0.4f}     {row.market_vol:0.6f}    {row.fitted_vol:0.6f}    {row.residual: .8f}")

    print("\nInitial Guess Comparison")
    guesses = [(0.0180, -0.10, 0.30), (0.0300, -0.50, 0.80), (0.0100, 0.20, 0.20)]
    for idx, result in enumerate(
        calibrate_sabr_for_multiple_initial_guesses(
            forward,
            strikes,
            expiry,
            market_vols,
            beta=0.50,
            initial_guesses=guesses,
        ),
        start=1,
    ):
        diag = calibration_diagnostics(result)
        print(
            f"guess_{idx}: alpha={result.params.alpha:.6f}, rho={result.params.rho:.6f}, "
            f"nu={result.params.nu:.6f}, rmse={diag.rmse:.12f}"
        )

    print("\nBeta Sweep")
    for result in calibrate_sabr_across_beta_values(
        forward,
        strikes,
        expiry,
        market_vols,
        beta_values=[0.0, 0.5, 1.0],
        initial_guess=(0.0180, -0.10, 0.30),
        ):
        diag = calibration_diagnostics(result)
        print(
            f"beta={result.params.beta:.2f}: alpha={result.params.alpha:.6f}, "
            f"rho={result.params.rho:.6f}, nu={result.params.nu:.6f}, rmse={diag.rmse:.12f}"
        )

    print("\nNegative-Rate Extension Snapshot")
    neg_forward = -0.0020
    neg_strike = -0.0010
    shift = 0.0300
    shifted_vol = shifted_sabr_implied_volatility(neg_forward, neg_strike, expiry, true_params, shift)
    shifted_payoff = price_shifted_black(neg_forward, neg_strike, expiry, shifted_vol, shift, "payer")
    print(
        f"neg_forward={neg_forward:.4f}, neg_strike={neg_strike:.4f}, shift={shift:.4f}, "
        f"shifted_vol={shifted_vol:.6f}, shifted_black_payoff={shifted_payoff:.8f}"
    )


if __name__ == "__main__":
    main()
