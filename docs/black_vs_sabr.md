# Black vs SABR in This Project

## Core Difference

Black and SABR are not competing at exactly the same layer.

- Black is a pricing formula once a volatility is given
- SABR is a volatility model that generates a strike-dependent implied
  Black volatility

In practical terms:

1. Black pricing takes:
   - forward swap rate
   - strike
   - expiry
   - annuity
   - Black volatility
2. SABR takes:
   - forward swap rate
   - strike
   - expiry
   - alpha
   - beta
   - rho
   - nu
3. SABR then produces an implied Black volatility, which is fed back into the
   Black formula for final pricing

## Why Build Both

### Black

Use Black to:
- build the first pricing engine
- understand the core economics of a European swaption
- compute fast benchmark prices
- support simple Greeks and hedging analysis

### SABR

Use SABR to:
- model smile and skew across strikes
- explain why OTM and ITM options should not share one flat volatility
- compare pricing under flat vol and smile-adjusted vol
- prepare for later calibration work

## Project Positioning

The recommended project sequence is:

1. Build the Black pricing engine
2. Add SABR implied volatility
3. Use SABR-implied vol inside the Black pricing formula
4. Compare prices and risk metrics under both setups
5. Later add SABR calibration to market quotes

## Research Questions You Can Answer

1. How sensitive is a swaption price to the volatility input under Black?
2. How much does SABR smile adjustment change price across strikes?
3. Does a flat-vol assumption understate or overstate OTM or ITM value?
4. How might smile-aware pricing affect hedging interpretation?

## Scope for the Current Version

Current implementation target:

- Black pricing for European payer and receiver swaptions
- SABR implied volatility using the standard approximation
- SABR-adjusted Black pricing
- SABR calibration skeleton for one strike slice
- side-by-side Black and SABR risk comparison
- strike comparison examples

Not yet in scope:

- SABR calibration to market vol cube
- dynamic SABR hedging
- stochastic rates plus stochastic vol joint modeling
