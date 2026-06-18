"""Shared market-data, curve, and validation helpers."""

from __future__ import annotations

from importlib import import_module

_EXPORTS = {
    "bootstrap_deposit_quote": ".curve_bootstrap",
    "bootstrap_swap_quote": ".curve_bootstrap",
    "bootstrap_zero_curve": ".curve_bootstrap",
    "exp_minus_rt": ".curve_bootstrap",
    "zero_rate_from_discount_factor": ".curve_bootstrap",
    "build_daily_zero_curve": ".market_data",
    "curve_as_dict": ".market_data",
    "discount_factor": ".market_data",
    "year_fractions": ".market_data",
    "zero_rate": ".market_data",
    "curve_node_rows": ".market_validation",
    "discount_factor_rows": ".market_validation",
    "load_json_metadata": ".market_validation",
    "trade_summary": ".market_validation",
    "build_fred_sofr_csv_url": ".sofr",
    "download_sofr_history_csv": ".sofr",
    "latest_sofr_observation": ".sofr",
    "latest_sofr_observation_from_excel": ".sofr",
    "load_sofr_history_csv": ".sofr",
    "load_sofr_history_excel": ".sofr",
    "prepare_sofr_data_bundle": ".sofr",
    "prepare_sofr_data_bundle_from_excel": ".sofr",
    "prepare_sofr_data_bundle_from_local_csv": ".sofr",
    "sofr_to_market_quote": ".sofr",
    "write_sofr_history_csv_from_observations": ".sofr",
    "write_sofr_market_quote_csv": ".sofr",
    "write_sofr_metadata_json": ".sofr",
    "build_ust_snapshot_url": ".ust_yield_curve_proxy",
    "fetch_ust_yield_curve_snapshot": ".ust_yield_curve_proxy",
    "prepare_ust_yield_curve_proxy_bundle": ".ust_yield_curve_proxy",
    "snapshot_to_curve_points": ".ust_yield_curve_proxy",
    "write_curve_points_csv": ".ust_yield_curve_proxy",
    "write_snapshot_metadata": ".ust_yield_curve_proxy",
}

__all__ = sorted(_EXPORTS)


def __getattr__(name: str):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(_EXPORTS[name], __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
