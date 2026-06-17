# Bermudan Market Data Scaffold

This folder contains the market-style Bermudan swaption inputs used for the
planned LSMC extension.

Files:

- `bermudan_spec.csv`: Bermudan trade specification
- `bermudan_european_calibration_vols.csv`: co-terminal European swaption vol
  slice used as Bermudan calibration targets

Notes:

- The Bermudan itself does not have a directly observed market volatility
  surface in this project.
- The calibration file is intentionally structured like market European data,
  because the intended workflow is:

  1. calibrate Hull-White to co-terminal European swaptions
  2. simulate rates with Monte Carlo
  3. value the Bermudan with LSMC
