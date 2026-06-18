"""Show the Bermudan LSMC project skeleton and planned inputs."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from swaption_pricing.data import (
    DEFAULT_BERMUDAN_MARKET_SPEC_CSV,
    DEFAULT_BERMUDAN_MARKET_VOLS_CSV,
    load_bermudan_calibration_vols_csv,
    load_bermudan_spec_csv,
    load_project_data,
)
from swaption_pricing.pricing.bermudan import bermudan_lsmc_skeleton_summary, build_bermudan_calibration_targets
from swaption_pricing.types import HullWhiteParams, MonteCarloConfig


def main() -> None:
    bundle = load_project_data(data_mode="auto")
    spec = load_bermudan_spec_csv(DEFAULT_BERMUDAN_MARKET_SPEC_CSV)
    european_quotes = load_bermudan_calibration_vols_csv(DEFAULT_BERMUDAN_MARKET_VOLS_CSV)
    calibration_targets = build_bermudan_calibration_targets(spec, european_quotes)
    hw_params = HullWhiteParams(mean_reversion=0.03, volatility=0.01)
    mc_config = MonteCarloConfig(num_paths=500, delta_time=0.25, seed=42, antithetic=True)
    summary = bermudan_lsmc_skeleton_summary(bundle.curve, spec, hw_params, mc_config)

    print("Bermudan LSMC Skeleton")
    print(f"Data source:           {bundle.source}")
    print(f"Curve source:          {bundle.curve_source}")
    print(f"Trade ID:              {spec.trade_id}")
    print(f"Settlement type:       {spec.settlement_type}")
    print(f"Calibration quotes:    {len(european_quotes)} loaded")
    print(
        "Calibration targets:   "
        + ", ".join(f"{quote.expiry:.0f}Yx{quote.tenor:.0f}Y" for quote in calibration_targets)
    )
    print(f"Exercise dates:        {summary['exercise_dates']}")
    print(f"Immediate payoffs:     {summary['immediate_exercise_values']}")
    print(f"Simulated path count:  {summary['num_paths']}")
    print(f"Time grid points:      {summary['num_time_points']}")
    print("Pricing engine status: architecture ready, backward induction pending")


if __name__ == "__main__":
    main()
