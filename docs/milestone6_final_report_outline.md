# Milestone 6 Final Report Outline

## Purpose

This outline defines the final integrated report for the swaption pricing project.
The goal is not only to show model implementation, but to demonstrate:

- understanding of the swaption product
- understanding of pricing logic and market inputs
- understanding of volatility smile and calibration
- understanding of low-rate model choices
- understanding of risk and simple hedging interpretation
- awareness of how these analytics connect to real trading-desk workflows

The final report should read like a small quant research note or desk analytics study,
not like a list of coding tasks.

## Core Narrative

The project should tell one coherent story:

1. A swaption is an option on a forward-starting interest rate swap.
2. Correct swaption pricing requires a coherent curve and swap analytics layer.
3. Black provides a useful benchmark, but flat volatility is not enough to explain smile.
4. SABR provides a practical smile layer and can be calibrated to a volatility slice.
5. Low-rate and negative-rate environments force model regime choices such as shifted-lognormal or normal-vol frameworks.
6. Model choice changes not only price, but also risk numbers and hedging interpretation.
7. A practical implementation should eventually be connected to real market data rather than synthetic inputs alone.

## Recommended Deliverable Format

The final deliverable can be either:

- one integrated notebook, or
- one integrated markdown or PDF report supported by notebooks and scripts

The recommended primary artifact is:

- `notebooks/final_project_report.ipynb`

Supporting references can remain in the milestone notebooks.

## Section Structure

## 1. Executive Summary

### Objective

State clearly what the project builds and why it matters.

### Questions this section answers

- What problem does the project solve?
- What product is being analyzed?
- What models are implemented?
- What are the major findings?

### Key points to include

- The project builds a USD swaption analytics workflow from curve construction to pricing, calibration, low-rate model comparison, and risk/hedging analysis.
- Black is used as the benchmark pricing framework.
- SABR is used to model smile and strike-dependent implied volatility.
- Shifted-lognormal and Bachelier frameworks are studied for low-rate or negative-rate environments.
- The project currently supports both example data and a growing market-data ingestion path.

### Interview framing

If an interviewer reads only this section, they should already understand the full scope.

## 2. Product and Market Context

### Objective

Show that the project is grounded in the real product rather than only formulas.

### Questions this section answers

- What is a payer swaption?
- What is a receiver swaption?
- Who uses swaptions in practice?
- Why do these products matter?

### Key points to include

- A payer swaption gives the right to enter a payer swap in the future.
- A receiver swaption gives the right to enter a receiver swap in the future.
- Typical users include rates trading desks, treasury or ALM teams, insurers, and asset managers.
- Practical uses include hedging future swap execution risk, expressing convex rate views, and managing downside or rally protection.

### Suggested project references

- `docs/project_plan.md`
- `notebooks/milestone2_black_swaption_pricing.ipynb`

## 3. Market Data and Curve Architecture

### Objective

Explain the inputs required before any pricing model becomes meaningful.

### Questions this section answers

- What data does swaption pricing require?
- Which data is already implemented in example mode?
- Which parts are moving toward market mode?
- What can public data cover and what still usually requires vendor data?

### Key points to include

- Curve data drives discount factors, forward swap rates, annuity, and swap PV.
- Swaption pricing requires volatility inputs such as ATM vols or smile slices.
- The project currently supports:
  - example mode
  - CSV-backed market mode
  - first-stage SOFR ingestion
- SOFR should be framed as a front-end reference-rate input, not a complete swap curve by itself.

### Suggested project references

- `src/swaption_pricing/data_loader.py`
- `src/swaption_pricing/sofr.py`
- `data/european/market/README.md`
- `notebooks/milestone1_curve_and_swap_analytics.ipynb`

## 4. Curve Construction and Swap Analytics

### Objective

Establish the foundation for all later pricing work.

### Questions this section answers

- How is the curve used?
- Why are annuity and forward swap rate central?
- How is the underlying swap valued?

### Key points to include

- zero-rate interpolation
- simplified bootstrap
- discount factors
- fixed and floating leg valuation
- annuity
- forward par swap rate

### Suggested project references

- `src/swaption_pricing/market_data.py`
- `src/swaption_pricing/curve_bootstrap.py`
- `src/swaption_pricing/swap.py`
- `notebooks/milestone1_curve_and_swap_analytics.ipynb`

## 5. Black Pricing Benchmark

### Objective

Build the baseline pricing and intuition layer.

### Questions this section answers

- Why is Black a useful benchmark?
- Why is the underlying a forward swap rate?
- What does annuity do in the final price?
- How do moneyness, intrinsic value, and time value help interpretation?

### Key points to include

- payer and receiver pricing formulas
- moneyness
- intrinsic value
- time value
- PV01, vega, theta under the Black benchmark

### Suggested project references

- `src/swaption_pricing/black76.py`
- `notebooks/milestone2_black_swaption_pricing.ipynb`

## 6. SABR Smile Modeling

### Objective

Show why flat volatility is insufficient and how smile is introduced.

### Questions this section answers

- Why is flat Black vol not enough?
- What role does SABR play?
- How do alpha, beta, rho, and nu affect the smile?

### Key points to include

- SABR generates implied Black vol, not final price directly
- Black remains the final pricing layer
- smile shape affects ITM and OTM prices

### Suggested project references

- `src/swaption_pricing/sabr.py`
- `notebooks/milestone3_sabr_smile_module.ipynb`

## 7. Calibration and Low-Rate Model Extension

### Objective

Demonstrate that the project moves from exogenous parameters to fitted parameters and from standard-rate assumptions to low-rate model choices.

### Questions this section answers

- How is SABR calibrated?
- How stable is calibration?
- Why do shift choices matter?
- Why does low-rate modeling require alternatives to standard lognormal assumptions?

### Key points to include

- calibration objective
- residuals and RMSE
- beta stability
- shift sensitivity
- shifted Black
- shifted SABR
- Bachelier comparison

### Suggested project references

- `src/swaption_pricing/calibration.py`
- `src/swaption_pricing/bachelier.py`
- `notebooks/milestone4_overview_sabr_calibration_and_low_rate_extension.ipynb`
- `notebooks/milestone4_1_shift_sensitivity.ipynb`
- `notebooks/milestone4_2_calibration_stability.ipynb`
- `notebooks/milestone4_3_bachelier_comparison.ipynb`

## 8. Risk and Hedging Across Models

### Objective

Show that model choice affects not just valuation but also practical risk interpretation.

### Questions this section answers

- How do PV01, vega, and theta differ across models?
- Does a simple swap-based hedge reduce PnL under parallel shocks?
- Why can hedging conclusions depend on the pricing model?

### Key points to include

- cross-model sensitivity comparison
- simple underlying-swap PV01 hedge
- unhedged vs hedged PnL
- residual risk after hedge

### Suggested project references

- `src/swaption_pricing/risk.py`
- `src/swaption_pricing/hedging.py`
- `notebooks/milestone5_risk_and_hedging_across_models.ipynb`

## 9. Practical Trading and Risk Use Cases

### Objective

Connect the analytics stack to real desk usage.

### Questions this section answers

- How would a rates desk use this framework?
- How would treasury or ALM teams interpret this product?
- Where does model choice matter operationally?

### Suggested use cases

- desk pricing and marking for a European swaption
- hedging future swap execution risk
- low-rate regime model choice between shifted-lognormal and normal-vol frameworks

### Note

This section should sound practical and product-aware, not overly academic.

## 10. Limitations

### Objective

Show good model judgment by stating what is not yet included.

### Key limitations to include

- simplified single-curve setup
- limited public swaption market data
- no full day-count or business-day calendar engine
- calibration currently slice-based rather than full vol cube
- simple parallel-shift risk rather than full scenario framework
- no production trade capture or lifecycle logic

## 11. Next Steps

### Objective

Show how the project would move closer to production-grade desk analytics.

### Recommended next steps

- complete market-data ingestion for full USD SOFR curve inputs
- import ATM swaption grids and one or more smile slices
- validate calibration against real market snapshots
- extend to portfolio-level risk and hedging
- build scenario-based PnL explain
- prepare a polished final integrated notebook

## Presentation Guidance for Interviews

The final report should allow you to explain the project in three layers:

### 30-second version

I built a swaption analytics workflow covering curve construction, Black pricing, SABR smile modeling, calibration, low-rate model comparison, and cross-model risk and hedging.

### 2-minute version

I started from the underlying swap economics, built a benchmark Black pricer, extended it with SABR for smile, studied calibration stability and low-rate frameworks such as shifted Black and Bachelier, and then compared cross-model risk and hedging outcomes. I also added a data-ingestion layer so the project can move from synthetic inputs toward real market data.

### Deep-dive version

Use the milestone notebooks and code modules as supporting evidence, but tell the story in product order:

1. product
2. market data
3. curve and swap analytics
4. pricing
5. smile and calibration
6. low-rate model choice
7. risk and hedging
8. practical market relevance

## Recommended Next Action

After this outline is approved, the next best step is to build the market-data validation section.
That section will make the final report much more credible for interviews because it will show how the existing analytics stack begins to connect to live market inputs.

Reference planning document:

- `docs/market_validation_plan.md`
