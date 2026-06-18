# Project Plan

## Project Title

USD European Swaption Pricing, Greeks, and Basic Hedging Analysis

## Research Question

How can a beginner build a practical swaption analytics workflow that links
pricing, risk sensitivities, and simple hedging decisions in a way that reflects
real-world rates desk thinking?

## Version 1 Deliverables

1. A swap analytics module that computes:
   - discount factors
   - forward swap rates
   - swap annuity
   - swap present value
2. A swaption pricing module that computes:
   - payer swaption price
   - receiver swaption price
   - intrinsic and time value intuition
3. A volatility modeling module that computes:
   - SABR implied Black volatility
   - strike-by-strike smile comparison
   - Black vs SABR-adjusted pricing comparison
4. A calibration module that computes:
   - SABR parameter fitting to a market volatility slice
   - fitted vs market volatility comparison
5. A risk module that computes:
   - PV01
   - vega
   - theta
   - Black vs SABR-adjusted risk comparison
6. A hedging module that:
   - estimates a simple hedge ratio
   - compares hedged and unhedged PnL under rate shocks
7. A notebook or report that explains the methods and findings
8. A data-ingestion layer that supports both example data and CSV-based market snapshots

## Assumptions for Version 1

- Single-curve setup
- Flat or simplified volatility input
- SABR parameters supplied exogenously before calibration is added
- European exercise only
- Plain vanilla fixed-for-floating underlying swap
- Finite-difference Greeks

## Learning Roadmap

### Phase 1: Rates Foundations

- discount factors
- zero rates
- forward rates
- swap fixed and floating legs
- par swap rate

### Phase 2: Swaption Foundations

- payer vs receiver swaptions
- expiry and tenor
- moneyness
- Black model inputs and interpretation

### Phase 3: Risk and Hedging

- PV01 and DV01
- vega and theta
- parallel curve shocks
- hedge ratio using underlying swap

### Phase 4: Volatility Smile Modeling

- why Black alone does not explain smile
- SABR parameter roles
- strike-dependent implied volatility
- effect of smile on ITM and OTM pricing

### Phase 5: Calibration and Low-Rate Extension

- fit SABR parameters to a smile slice
- diagnose residuals and calibration stability
- study shift sensitivity in low-rate setups
- compare shifted-lognormal and normal-vol approaches

## Module Plan

### `market_data.py`

Purpose:
- handle curve inputs
- compute discount factors and accrual schedules

### `data_loader.py`

Purpose:
- load normalized project inputs from either built-in examples or CSV-backed market data
- keep the pricing and risk modules independent of raw data-source formats

### `swap.py`

Purpose:
- compute par swap rate
- value fixed and floating legs
- compute annuity

### `pricing/european/black76.py`

Purpose:
- price payer and receiver swaptions using the Black framework

### `pricing/european/sabr.py`

Purpose:
- compute SABR-implied Black volatility
- feed smile-adjusted vol into Black pricing
- compare flat-vol and strike-dependent-vol valuations

### `pricing/european/calibration.py`

Purpose:
- calibrate SABR parameters to a volatility smile slice
- compare fitted vols with input market vols
- prepare for later vol cube work

### `risk/`

Purpose:
- compute finite-difference sensitivities
- compare Black and SABR-adjusted risk outputs
- create small scenario tables

### `hedging/`

Purpose:
- estimate hedge ratio against swap PV01
- compare hedged and unhedged outcomes

## Recommended Next Step

Start with the curve and swap modules first. If the forward swap rate and
annuity are correct, the pricing module becomes much easier to verify.

After the Black engine is stable, add SABR as a volatility layer rather than a
replacement for Black. In practice, SABR generates the strike-dependent
implied vol, and the Black formula still performs the final pricing step.

## Milestone Structure

### Milestone 1: Curve Construction and Swap Analytics

- bootstrap the zero curve from simplified market quotes
- compute annuity, forward swap rate, and vanilla swap PV

### Milestone 2: Black Swaption Pricing Benchmark

- build and validate the European swaption pricing benchmark
- explain intrinsic value, time value, and core Greeks

### Milestone 3: SABR Smile Module

- generate strike-dependent implied volatilities
- compare Black and SABR smile-adjusted prices

### Milestone 4: SABR Calibration and Low-Rate Model Extension

Purpose:
- move from exogenous SABR parameters to fitted parameters
- extend the framework toward low-rate and negative-rate use cases

Subsections:
- `4.1 Shift Sensitivity`
- `4.2 Calibration Stability`
- `4.3 Bachelier Comparison`

### Milestone 4.1: Shift Sensitivity

- study how shift changes shifted-Black and shifted-SABR outputs
- treat shift as a modeling choice rather than a technical patch

### Milestone 4.2: Calibration Stability

- compare calibration results across initial guesses, fixed beta values, and shifts
- interpret stability as part of model risk

### Milestone 4.3: Bachelier Comparison

- add a normal-vol benchmark for low-rate and negative-rate environments
- compare Black, shifted Black, and Bachelier model behavior

### Milestone 5: Risk and Hedging Across Models

- compare PV01, vega, and theta across Black, SABR, shifted Black, shifted SABR, and Bachelier
- evaluate a simple underlying-swap PV01 hedge under parallel curve shocks
- compare unhedged and hedged PnL across the model set

### Milestone 6: Final Integrated Report

- consolidate the full project into one coherent research narrative
- explain the project in product, market-data, pricing, calibration, and risk terms suitable for interviews
