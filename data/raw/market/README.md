# Market Data Input Templates

This folder is for real market-data snapshots that you collect manually, export from a terminal, or download from public sources.

Recommended files:

- `curve_points.csv`
  - direct zero-curve nodes
  - columns: `maturity,zero_rate`
  - if licensed SOFR swap benchmarks are unavailable, you can start from `usd_yield_curve_proxy.template.csv` and use U.S. Treasury yields as a documented proxy

- `market_quotes.csv`
  - curve-building quotes for bootstrap
  - columns: `instrument_type,maturity,rate,pay_frequency`

- `swaption_spec.csv`
  - one-row trade specification
  - columns: `notional,expiry,tenor,strike,pay_frequency,option_type`

- `vol_slice.csv`
  - one expiry-tenor smile slice for calibration
  - columns: `expiry,tenor,strike,vol,vol_type`

- `sofr/sofr_history.csv`
  - public SOFR daily history from FRED or New York Fed-linked exports
  - columns: `DATE,SOFR`
  - use this as a raw reference-rate series, then map the latest fixing into a short-end quote

Usage examples:

```bash
PYTHONPATH=src python3 main.py pricing --data-mode market --curve-csv data/raw/market/curve_points.csv --spec-csv data/raw/market/swaption_spec.csv

PYTHONPATH=src python3 main.py calibration --data-mode market --curve-csv data/raw/market/curve_points.csv --spec-csv data/raw/market/swaption_spec.csv --vol-slice-csv data/raw/market/vol_slice.csv

PYTHONPATH=src python3 main.py pricing --data-mode market --bootstrap-curve --market-quotes-csv data/raw/market/market_quotes.csv --spec-csv data/raw/market/swaption_spec.csv

PYTHONPATH=src python3 main.py sofr --sofr-csv data/raw/market/sofr/sofr_history.csv --sofr-quote-csv data/processed/sofr_latest_quote.csv

python3 scripts/fetch_sofr_data.py --output-dir data/raw/market/sofr --start-date 2026-01-01

python3 scripts/fetch_ust_yield_curve_proxy.py --date 2026-06-12 --output-dir data/raw/market/ust_yield_curve_proxy
```
