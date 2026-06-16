# Market Validation Plan

## Purpose

This document defines the market-validation section for the swaption pricing project.
Its objective is to move the project from a synthetic demonstration toward a market-aware analytics study.

The validation plan should show:

- which model inputs can already be connected to real market data
- how to test whether the implemented analytics behave consistently with those inputs
- which parts can be validated with public data
- which parts usually require vendor or broker data

This section should strengthen the final project for interviews by showing practical market-data awareness.

## Validation Philosophy

The project should not present all results as if they were already fully vendor-validated.
Instead, it should clearly separate:

- example-mode verification
- public-data validation
- market-consistent but limited-scope validation
- future full vendor-data validation

This distinction is a strength, not a weakness, because it shows model judgment.

## Recommended Validation Layers

Market validation should be split into three layers:

1. Curve validation
2. Volatility and smile validation
3. Market-regime and model-choice validation

## 1. Curve Validation

### Objective

Demonstrate that the rates-input layer is coherent and usable for swaption analytics.

### Questions this layer answers

- Can the project ingest real front-end reference-rate data?
- Can the project reconstruct or represent a market curve consistently?
- Do the curve outputs generate reasonable swap analytics?

### Current project assets

- `src/swaption_pricing/curve_bootstrap.py`
- `src/swaption_pricing/market_data.py`
- `src/swaption_pricing/swap.py`
- `src/swaption_pricing/sofr.py`
- `src/swaption_pricing/data_loader.py`

### Minimum market-data inputs

- SOFR history or latest SOFR fixing
- curve node snapshot or market quotes for bootstrap
- one trade specification for the sample swaption

### Recommended validation outputs

#### Table 1: Raw Input Market Quotes

Columns:

- instrument type
- maturity
- market quote
- source
- valuation date

#### Table 2: Reconstructed Quotes vs Input Quotes

Columns:

- maturity
- input quote
- reconstructed quote
- error

This is the core bootstrap validation table.

#### Figure 1: Zero Curve

Show:

- node-based zero curve
- optionally the interpolated daily zero curve

#### Figure 2: Discount Factor Curve

Show:

- maturity on x-axis
- discount factor on y-axis

#### Table 3: SOFR Front-End Normalization

Columns:

- latest SOFR date
- latest SOFR fixing
- mapped maturity
- normalized short-end quote

### Interpretation points

- SOFR is only the front-end reference-rate input, not the full swap curve.
- The curve layer should be presented as partially market-connected, with room for fuller swap-tenor ingestion.
- If the reconstructed quotes line up well with the inputs, the curve is usable for pricing.

## 2. Volatility and Smile Validation

### Objective

Demonstrate that the volatility layer is informed by market-style inputs rather than only hard-coded assumptions.

### Questions this layer answers

- Can the benchmark pricing engine be anchored to market vols?
- Can SABR fit a market or market-like smile slice?
- Are the fitted smile and pricing outputs reasonable?

### Current project assets

- `src/swaption_pricing/black76.py`
- `src/swaption_pricing/sabr.py`
- `src/swaption_pricing/calibration.py`
- `notebooks/milestone2_black_swaption_pricing.ipynb`
- `notebooks/milestone3_sabr_smile_module.ipynb`
- `notebooks/milestone4_2_calibration_stability.ipynb`

### Minimum market-data inputs

At least one of the following:

- one ATM swaption vol point
- one market smile slice for a fixed expiry-tenor point

### Public-data reality

Public curve data is relatively accessible.
Public OTC swaption smile data is much less accessible.
Therefore this layer can be framed in three possible levels:

1. real ATM point only
2. one manually collected or exported smile slice
3. illustrative market-consistent smile when full public data is unavailable

### Recommended validation outputs

#### Table 4: ATM Validation

Columns:

- expiry
- tenor
- market vol
- model used
- price
- PV01
- vega

#### Table 5: Smile Slice Input

Columns:

- strike
- market vol
- vol type
- valuation date

#### Table 6: SABR Fitted Vol vs Market Vol

Columns:

- strike
- market vol
- fitted vol
- residual

#### Figure 3: Market Vol vs Fitted SABR Vol

Show:

- market smile points
- fitted SABR curve

#### Figure 4: Residual by Strike

Show:

- strike on x-axis
- residual on y-axis

### Interpretation points

- The report should state explicitly whether the smile slice is fully real market data, partially real, or market-consistent synthetic.
- The calibration section should emphasize fit quality and parameter stability, not only the fitted parameter values.

## 3. Market-Regime and Model-Choice Validation

### Objective

Demonstrate that the project is aware of model regime issues rather than assuming one pricing model fits all rate environments.

### Questions this layer answers

- Does model behavior change meaningfully in low-rate or negative-rate settings?
- Why might shifted-lognormal and normal-vol models lead to different prices?
- How does model choice affect interpretation of the same trade?

### Current project assets

- `src/swaption_pricing/black76.py`
- `src/swaption_pricing/sabr.py`
- `src/swaption_pricing/bachelier.py`
- `notebooks/milestone4_1_shift_sensitivity.ipynb`
- `notebooks/milestone4_3_bachelier_comparison.ipynb`

### Recommended validation outputs

#### Table 7: Cross-Model Price Comparison

Columns:

- scenario
- Black price
- shifted Black price
- SABR price
- shifted SABR price
- Bachelier price

#### Table 8: Calibration Stability Across Beta and Shift

Columns:

- beta
- shift
- fitted alpha
- fitted rho
- fitted nu
- RMSE

#### Figure 5: Shift Sensitivity

Show:

- shift on x-axis
- shifted Black price
- shifted SABR price

#### Figure 6: Cross-Model Comparison in Low-Rate Regime

Show:

- bar chart or comparison table for Black, shifted Black, and Bachelier outputs

### Interpretation points

- Model choice is a practical decision, not only a mathematical one.
- Low-rate environments justify regime-aware comparisons rather than blind use of standard lognormal assumptions.
- This section should connect directly to how a desk might interpret pricing or risk under different rate environments.

## What Can Be Done Immediately

The following validation items can be built now using the existing project and current data pipeline:

### Immediate

- SOFR ingestion demonstration
- SOFR latest-fixing normalization
- curve validation using example or CSV-backed quote snapshots
- market-mode vs example-mode workflow comparison
- smile-fit diagnostics on one slice
- low-rate model comparison

### Requires More Data

- full USD SOFR swap curve snapshot
- ATM swaption market grid
- real market smile slice
- repeated historical market snapshots

## Proposed Report Placement

The market-validation material should sit mainly in:

- Section 3: Market Data and Curve Architecture
- Section 7: Calibration and Low-Rate Model Extension
- Section 8: Risk and Hedging Across Models

It should also be referenced in:

- Section 11: Next Steps

## Recommended File Outputs

The market-validation section will likely need:

- one dedicated notebook
- one or two CSV-backed examples
- one supporting markdown summary

Recommended notebook:

- `notebooks/market_validation_workbook.ipynb`

Supporting example script:

- `examples/run_market_curve_validation.py`

Potential supporting docs:

- `docs/market_validation_plan.md`

## Suggested Interview Framing

The market-validation section should allow you to say:

I did not treat the project as a pure formula exercise. I separated example-mode analytics from market-connected validation, built an ingestion path for SOFR, and structured the pricing and calibration layers so they can absorb real market curve and volatility inputs progressively.

## Recommended Next Action

After approving this plan, the next step should be to build the market-validation workbook and populate the first version with:

1. SOFR ingestion results
2. curve reconstruction checks
3. one volatility-slice validation view
4. one low-rate model comparison view
