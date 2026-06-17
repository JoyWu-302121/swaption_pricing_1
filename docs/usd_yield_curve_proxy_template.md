# USD Yield Curve Proxy Template

## Purpose

This template is for a manually curated USD yield curve proxy when full SOFR swap-tenor benchmark access is unavailable.

The file is designed to plug directly into the project's existing market-data loader:

- `data/european/market/usd_yield_curve_proxy.template.csv`

Expected columns:

- `maturity`
- `zero_rate`

The current loader reads this format through:

- `main.py --curve-csv ...`
- `src/swaption_pricing/data_loader.py`

## Recommended Use

Use this file when:

- you have real SOFR data for the front end
- you do not have licensed ICE SOFR swap rates
- you still want a market-consistent USD curve proxy for project validation

This is a proxy curve, not a full dealer-grade SOFR OIS curve.

## Suggested Maturities

The template includes:

- `0.083333` = about 1M
- `0.25` = 3M
- `0.5` = 6M
- `1.0` = 1Y
- `2.0` = 2Y
- `3.0` = 3Y
- `5.0` = 5Y
- `7.0` = 7Y
- `10.0` = 10Y
- `20.0` = 20Y
- `30.0` = 30Y

These points are enough for a practical first-stage proxy curve.

## Data Source Guidance

If you are using a U.S. Treasury yield curve as a proxy, fill the `zero_rate` column with the yield level you observe for each maturity.

This should be documented in your report as:

- `public-data proxy curve`
- not a true USD SOFR swap curve

That wording is important because Treasury yields and SOFR swap rates are not identical instruments.

## Example Workflow

1. Copy the template into a working file, for example:
   - `data/european/market/curve_points.csv`
2. Fill in the `zero_rate` column with the yields you collected
3. Run:

```bash
PYTHONPATH=src python3 main.py pricing --data-mode market --curve-csv data/european/market/curve_points.csv --spec-csv data/european/market/swaption_spec.csv
```

4. Use the resulting curve in:
   - pricing
   - calibration
   - risk comparison

## Reporting Guidance

In the final report, describe this input as:

- a manually curated USD yield curve proxy
- used because fully licensed SOFR swap benchmark data was not publicly accessible
- sufficient for market-consistent validation, but not a substitute for full production curve construction
