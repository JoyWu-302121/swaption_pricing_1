"""Study SABR calibration stability across guesses, betas, and shifts."""

from swaption_pricing.pricing.european import (
    SabrParams,
    calibrate_sabr_across_beta_values,
    calibrate_sabr_for_multiple_initial_guesses,
    calibrate_shifted_sabr_across_shifts,
    calibration_diagnostics,
)
from swaption_pricing.pricing.european.sabr import sabr_implied_volatility, shifted_sabr_implied_volatility


def main():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]

    print("Initial Guess Stability")
    guess_results = calibrate_sabr_for_multiple_initial_guesses(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        initial_guesses=[(0.0180, -0.10, 0.30), (0.0300, -0.50, 0.80), (0.0100, 0.20, 0.20)],
    )
    for idx, result in enumerate(guess_results, start=1):
        diag = calibration_diagnostics(result)
        print(
            f"guess_{idx}: alpha={result.params.alpha:.6f}, rho={result.params.rho:.6f}, "
            f"nu={result.params.nu:.6f}, rmse={diag.rmse:.12f}"
        )

    print("\nBeta Stability")
    beta_results = calibrate_sabr_across_beta_values(
        forward,
        strikes,
        expiry,
        market_vols,
        beta_values=[0.0, 0.5, 1.0],
        initial_guess=(0.0180, -0.10, 0.30),
    )
    for result in beta_results:
        diag = calibration_diagnostics(result)
        print(
            f"beta={result.params.beta:.2f}: alpha={result.params.alpha:.6f}, "
            f"rho={result.params.rho:.6f}, nu={result.params.nu:.6f}, rmse={diag.rmse:.12f}"
        )

    print("\nShift Stability")
    neg_forward = -0.0020
    neg_strikes = [-0.0100, -0.0050, -0.0010, 0.0020, 0.0060]
    shifts = [0.02, 0.03, 0.05]
    shifted_market_vols = [
        shifted_sabr_implied_volatility(neg_forward, strike, expiry, true_params, 0.03) for strike in neg_strikes
    ]
    shift_results = calibrate_shifted_sabr_across_shifts(
        neg_forward,
        neg_strikes,
        expiry,
        shifted_market_vols,
        beta=0.50,
        shifts=shifts,
        initial_guess=(0.0180, -0.10, 0.30),
    )
    for shift, result in shift_results:
        diag = calibration_diagnostics(result)
        print(
            f"shift={shift:.2f}: alpha={result.params.alpha:.6f}, rho={result.params.rho:.6f}, "
            f"nu={result.params.nu:.6f}, rmse={diag.rmse:.12f}"
        )


if __name__ == "__main__":
    main()
