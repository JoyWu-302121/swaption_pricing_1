# Bermudan Swaption LSMC Design

## Objective

Extend the current European swaption project into a Bermudan swaption pricing
prototype using Longstaff-Schwartz Monte Carlo (LSMC).

The goal of this milestone is not to replace the existing Black, SABR, or
Bachelier pricing engines. Instead, it introduces an early-exercise pricing
framework for Bermudan swaptions that can later support callable-style rates
products and model-risk comparisons.

## Scope

The first implementation target is:

- payer and receiver Bermudan swaptions
- annual exercise dates
- Hull-White one-factor short-rate simulation
- LSMC continuation-value regression
- single-curve setup
- price and basic exercise diagnostics

Out of scope for the first version:

- full calibration of Hull-White to a market swaption cube
- Bermudan Greeks
- multi-factor rate models
- callable note or callable bond wrappers
- production-grade hedging workflow

## Architecture Overview

The Bermudan extension is separated into a dedicated group of modules:

```text
src/swaption_pricing/
  pricing/
    bermudan/
      __init__.py
      bermudan.py
      monte_carlo.py
      hull_white.py
      lsmc.py
      exercise.py

docs/
  bermudan_lsmc_design.md

examples/
  run_bermudan_lsmc.py

notebooks/
  milestone7_bermudan_lsmc.ipynb
```

## Module Responsibilities

### `types.py`

Relevant Bermudan-related dataclasses:

- `BermudanSwaptionSpec`
- `HullWhiteParams`
- `MonteCarloConfig`
- `BermudanLSMCResult`

These define the contract, model parameters, simulation settings, and result
container.

### `monte_carlo.py`

Purpose:

- build simulation time grids
- generate reproducible normal shocks
- provide path-level utilities shared by the short-rate model and LSMC engine

### `hull_white.py`

Purpose:

- simulate short-rate paths under Hull-White 1F
- produce pathwise discount factors
- provide the base rate-model layer for the Bermudan prototype

### `exercise.py`

Purpose:

- define exercise schedules
- compute pathwise swap present values at exercise dates
- convert swap values into immediate exercise payoffs

### `lsmc.py`

Purpose:

- implement basis functions
- fit continuation values with regression
- perform backward induction
- store exercise decisions and diagnostics

### `bermudan.py`

Purpose:

- expose the high-level pricing API
- orchestrate the curve, model, simulation, exercise, and regression layers
- later serve as the single entry point for Bermudan pricing from notebooks or
  CLI tooling

Current exported entry point:

- `swaption_pricing.pricing.bermudan`

## Data Flow

The intended pricing workflow is:

1. Load `BermudanSwaptionSpec`
2. Load the initial zero curve
3. Set `HullWhiteParams`
4. Set `MonteCarloConfig`
5. Build the simulation time grid
6. Simulate short-rate paths
7. Compute pathwise exercise values at each Bermudan exercise date
8. Run LSMC backward induction to estimate continuation values
9. Determine optimal stopping decisions path by path
10. Discount the optimal payoffs back to time zero
11. Return a `BermudanLSMCResult`

## Proposed MVP

The first Bermudan MVP should implement:

- deterministic exercise schedule
- Hull-White 1F Euler simulation
- simple polynomial basis functions such as `[1, x, x^2]`
- continuation-value regression using in-the-money paths only
- exercise probabilities by date
- final Bermudan price estimate

## Incremental Build Plan

1. Create the types and empty module structure
2. Implement time-grid and random-shock helpers
3. Implement Hull-White short-rate simulation
4. Implement exercise-value generation
5. Implement regression basis functions and backward induction
6. Add notebook diagnostics and convergence experiments

## Validation Plan

The Bermudan prototype should be validated in stages:

1. unit tests for time-grid and shape logic
2. unit tests for exercise schedule construction
3. path-simulation sanity checks
4. regression output sanity checks
5. qualitative comparison against European pricing bounds

## Integration Guidance

This Bermudan track should remain separate from the current `main.py pricing`
flow until the prototype is stable.

Recommended first-stage integration:

- keep European pricing inside `main.py`
- use `examples/run_bermudan_lsmc.py` for the Bermudan prototype
- use `notebooks/milestone7_bermudan_lsmc.ipynb` for research and diagnostics

After the core LSMC engine is stable, a dedicated CLI mode such as
`python3 main.py bermudan-lsmc` can be added.
