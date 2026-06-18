# Swaption Pricing Project

This project is a beginner-focused interest rate swaption analytics project.
The current scope targets USD European swaptions and covers:

- swap curve and annuity calculations
- simplified curve bootstrapping from market quotes
- daily zero-curve construction by linear interpolation
- vanilla swap valuation
- Black swaption pricing
- SABR-implied volatility and SABR-adjusted pricing
- SABR calibration skeleton for market-vol fitting
- basic risk sensitivities
- simple hedging analysis

## Project Objective

Build a small but complete analytics workflow:

1. Construct market inputs for a swaption trade
2. Bootstrap a zero curve from simplified market quotes
3. Price a European payer or receiver swaption
4. Compare flat-vol Black pricing with SABR smile-adjusted pricing
5. Compute core sensitivities such as PV01 and vega
6. Compare unhedged and hedged risk under simple rate shocks

## Scope for Version 1

- Market: USD
- Product: European payer and receiver swaptions
- Models: Black and SABR-adjusted Black
- Calibration: SABR alpha-rho-nu fitting with fixed beta
- Risk: PV01, vega, theta across multiple pricing models
- Hedging: underlying swap based hedge under parallel shocks

## Suggested Workflow

1. Implement curve utilities
2. Implement curve bootstrapping
3. Implement swap pricing
4. Implement Black swaption pricing
5. Implement SABR implied volatility
6. Implement SABR calibration
7. Implement risk calculations
8. Implement hedging scenarios
9. Summarize results in a notebook or report

## Run the Project

Use the single entry point below:

```bash
python3 main.py
python3 main.py pricing
python3 main.py pricing --model black
python3 main.py pricing --model sabr
python3 main.py pricing --model bachelier
python3 main.py comparison
python3 main.py risk
python3 main.py calibration
python3 main.py sofr
```

`python3 main.py` defaults to `pricing`.
`pricing` defaults to `--data-mode auto`, which prefers market data when available and falls back to the built-in example bundle only when needed.

Example mode and market mode can coexist:

```bash
python3 main.py pricing
python3 main.py pricing --data-mode auto
python3 main.py pricing --data-mode example
python3 main.py pricing --model sabr --data-mode example
python3 main.py pricing --data-mode market --curve-csv data/european/market/ust_yield_curve_proxy/curve_points.csv
python3 main.py pricing --data-mode market --curve-csv data/european/market/curve_points.csv --spec-csv data/european/market/swaption_spec.csv
python3 main.py calibration --data-mode market --curve-csv data/european/market/curve_points.csv --spec-csv data/european/market/swaption_spec.csv --vol-slice-csv data/european/market/vol_slice.csv
python3 main.py pricing --data-mode market --bootstrap-curve --market-quotes-csv data/european/market/market_quotes.csv --spec-csv data/european/market/swaption_spec.csv
python3 main.py sofr --sofr-csv data/common/market/sofr/sofr_history.csv --sofr-quote-csv data/processed/sofr_latest_quote.csv
python3 scripts/fetch_sofr_data.py --output-dir data/common/market/sofr --start-date 2026-01-01
python3 scripts/fetch_ust_yield_curve_proxy.py --date 2026-06-12 --output-dir data/european/market/ust_yield_curve_proxy
python3 examples/run_market_curve_validation.py
```

## Repository Layout

```text
docs/                   Project notes and research plans
data/european/          European example and market inputs
data/bermudan/          Bermudan trade and calibration inputs
data/common/market/     Shared market-source inputs such as SOFR history
notebooks/              Exploratory analysis and final presentation notebooks
src/swaption_pricing/   Core pricing and risk modules
tests/                  Unit tests
```

## Pricing Architecture

The pricing package is now conceptually split into:

- `src/swaption_pricing/core/`
  Product-agnostic rates contract analytics such as vanilla swap valuation
- `src/swaption_pricing/market/`
  Curve construction, market-data ingestion, and market validation helpers
- `src/swaption_pricing/data/`
  CSV and bundle loaders that orchestrate project inputs
- `src/swaption_pricing/pricing/european/`
  European pricing workflow exports for Black, SABR, and Bachelier
- `src/swaption_pricing/pricing/bermudan/`
  Bermudan LSMC scaffolding for market-calibrated Hull-White workflows
- `src/swaption_pricing/risk/`
  Shared risk helpers, including common curve shocks and European model risk summaries
- `src/swaption_pricing/hedging/`
  Shared hedging helpers, currently centered on swap-based hedge evaluation

The current Bermudan market-style data scaffold lives in:

- `data/bermudan/market/bermudan_spec.csv`
- `data/bermudan/market/bermudan_european_calibration_vols.csv`

The current Bermudan code entry point is:

- `src/swaption_pricing/pricing/bermudan/`

The current Bermudan research driver is:

- `python3 examples/run_bermudan_lsmc.py`

## Repository Roles

- `main.py`: primary CLI entry point for pricing, comparison, risk, calibration, and SOFR ingestion
- `src/swaption_pricing/`: reusable library code
- `notebooks/`: milestone-by-milestone research notebooks
- `usecase/`: business-style scenario walkthroughs
- `examples/`: focused diagnostic scripts that still add incremental value
- `archive/examples_legacy/`: older one-off scripts preserved after `main.py` replaced them

## Milestone Structure

- Milestone 1: Curve Construction and Swap Analytics
- Milestone 2: Black Swaption Pricing Benchmark
- Milestone 3: SABR Smile Module
- Milestone 4: SABR Calibration and Low-Rate Model Extension
- Milestone 4.1: Shift Sensitivity
- Milestone 4.2: Calibration Stability
- Milestone 4.3: Bachelier Comparison
- Milestone 5: Risk and Hedging Across Models
- Milestone 6: Final Integrated Report
- Milestone 7: Bermudan Swaption Pricing with LSMC
