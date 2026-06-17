"""Show the Bermudan LSMC project skeleton and planned inputs."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.bermudan import bermudan_lsmc_skeleton_summary
from swaption_pricing.data_loader import load_project_data
from swaption_pricing.types import BermudanSwaptionSpec, HullWhiteParams, MonteCarloConfig


def main() -> None:
    bundle = load_project_data(data_mode="auto")
    spec = BermudanSwaptionSpec(
        notional=10_000_000.0,
        strike=bundle.spec.strike,
        swap_tenor=bundle.spec.tenor,
        pay_frequency=bundle.spec.pay_frequency,
        option_type=bundle.spec.option_type,
        exercise_dates=[1.0, 1.5, 2.0, 2.5],
        maturity=7.0,
    )
    hw_params = HullWhiteParams(mean_reversion=0.03, volatility=0.01)
    mc_config = MonteCarloConfig(num_paths=500, delta_time=0.25, seed=42, antithetic=True)
    summary = bermudan_lsmc_skeleton_summary(bundle.curve, spec, hw_params, mc_config)

    print("Bermudan LSMC Skeleton")
    print(f"Data source:           {bundle.source}")
    print(f"Curve source:          {bundle.curve_source}")
    print(f"Exercise dates:        {summary['exercise_dates']}")
    print(f"Immediate payoffs:     {summary['immediate_exercise_values']}")
    print(f"Simulated path count:  {summary['num_paths']}")
    print(f"Time grid points:      {summary['num_time_points']}")
    print("Pricing engine status: architecture ready, backward induction pending")


if __name__ == "__main__":
    main()
