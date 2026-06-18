from swaption_pricing.pricing.european import (
    SabrParams,
    bachelier_option_value,
    calibrate_sabr_across_beta_values,
    calibrate_sabr_for_multiple_initial_guesses,
    calibrate_sabr_to_vols,
    calibrate_shifted_sabr_across_shifts,
    calibrate_shifted_sabr_to_vols,
    calibration_diagnostics,
    calibration_rows,
    intrinsic_value,
    moneyness_label,
    price_shifted_black,
    price_swaption,
    price_swaption_bachelier,
    price_swaption_shifted_black,
    price_swaption_with_sabr,
    price_swaption_with_shifted_sabr,
    sabr_implied_volatility,
    time_value,
)
from swaption_pricing.pricing.european.sabr import shifted_sabr_implied_volatility
from swaption_pricing.core import (
    fixed_leg_pv,
    floating_leg_pv,
    forward_swap_rate,
    payment_schedule,
    swap_annuity,
    swap_present_value,
)
from swaption_pricing.data import (
    load_auto_bundle,
    load_curve_points_csv,
    load_example_bundle,
    load_market_bundle,
    load_market_quotes_csv,
    load_project_data,
    load_swaption_spec_csv,
    load_swaption_vol_slice_csv,
)
from swaption_pricing.market import (
    bootstrap_zero_curve,
    build_daily_zero_curve,
    build_fred_sofr_csv_url,
    build_ust_snapshot_url,
    curve_node_rows,
    discount_factor_rows,
    latest_sofr_observation,
    latest_sofr_observation_from_excel,
    load_json_metadata,
    load_sofr_history_csv,
    load_sofr_history_excel,
    snapshot_to_curve_points,
    sofr_to_market_quote,
    trade_summary,
    write_curve_points_csv,
    write_snapshot_metadata,
    write_sofr_history_csv_from_observations,
    write_sofr_market_quote_csv,
    write_sofr_metadata_json,
    zero_rate,
    prepare_sofr_data_bundle,
    prepare_sofr_data_bundle_from_excel,
    prepare_sofr_data_bundle_from_local_csv,
)
from swaption_pricing.pricing.bermudan import (
    bermudan_lsmc_skeleton_summary,
    bermudan_exercise_schedule,
    build_bermudan_calibration_targets,
    build_lsmc_time_grid,
    coterminal_tenors,
    hw_model_summary,
    polynomial_basis_vector,
)
from swaption_pricing.hedging import compare_model_hedging, swap_pv01
from swaption_pricing.risk import (
    calculate_bachelier_risk,
    calculate_sabr_risk,
    calculate_shifted_black_risk,
    calculate_shifted_sabr_risk,
    compare_all_model_risks,
    compare_black_and_sabr_risk,
)
from swaption_pricing.types import CurvePoint, MarketQuote, SwaptionSpec
from swaption_pricing.types import BermudanSwaptionSpec, HullWhiteParams, MonteCarloConfig, SwaptionVolQuote

from pathlib import Path


def sample_curve():
    return [
        CurvePoint(maturity=1.0, zero_rate=0.0420),
        CurvePoint(maturity=2.0, zero_rate=0.0415),
        CurvePoint(maturity=3.0, zero_rate=0.0410),
        CurvePoint(maturity=4.0, zero_rate=0.0408),
        CurvePoint(maturity=5.0, zero_rate=0.0405),
        CurvePoint(maturity=6.0, zero_rate=0.0403),
        CurvePoint(maturity=7.0, zero_rate=0.0402),
    ]


def sample_quotes():
    return [
        MarketQuote(instrument_type="deposit", maturity=1.0, rate=0.0420),
        MarketQuote(instrument_type="swap", maturity=2.0, rate=0.0415, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=3.0, rate=0.0410, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=4.0, rate=0.0408, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=5.0, rate=0.0405, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=6.0, rate=0.0403, pay_frequency=1),
        MarketQuote(instrument_type="swap", maturity=7.0, rate=0.0402, pay_frequency=1),
    ]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def test_swap_annuity_positive():
    annuity = swap_annuity(sample_curve(), expiry=2.0, tenor=5.0, pay_frequency=1)
    assert annuity > 0.0


def test_payment_schedule_has_expected_dates():
    assert payment_schedule(start=0.0, tenor=2.0, pay_frequency=2) == [0.5, 1.0, 1.5, 2.0]


def test_forward_swap_rate_positive():
    forward = forward_swap_rate(sample_curve(), expiry=2.0, tenor=5.0, pay_frequency=1)
    assert forward > 0.0


def test_fixed_and_floating_leg_pv_positive():
    curve = sample_curve()
    notional = 10_000_000.0
    fixed_rate = 0.0400
    assert fixed_leg_pv(curve, notional, fixed_rate, start=0.0, tenor=5.0, pay_frequency=1) > 0.0
    assert floating_leg_pv(curve, notional, start=0.0, tenor=5.0) > 0.0


def test_par_swap_value_is_close_to_zero():
    curve = sample_curve()
    notional = 10_000_000.0
    par_rate = forward_swap_rate(curve, expiry=0.0, tenor=5.0, pay_frequency=1)
    payer_value = swap_present_value(curve, notional, par_rate, start=0.0, tenor=5.0, pay_frequency=1, swap_type="payer")
    assert abs(payer_value) < 1e-6


def test_payer_and_receiver_swap_values_offset():
    curve = sample_curve()
    notional = 10_000_000.0
    fixed_rate = 0.0420
    payer_value = swap_present_value(curve, notional, fixed_rate, start=0.0, tenor=5.0, pay_frequency=1, swap_type="payer")
    receiver_value = swap_present_value(curve, notional, fixed_rate, start=0.0, tenor=5.0, pay_frequency=1, swap_type="receiver")
    assert payer_value == -receiver_value


def test_bootstrap_zero_curve_produces_ordered_nodes():
    curve = bootstrap_zero_curve(sample_quotes())
    assert len(curve) == len(sample_quotes())
    assert curve[0].maturity == 1.0
    assert curve[-1].maturity == 7.0


def test_example_bundle_has_curve_spec_and_vol_slice():
    bundle = load_example_bundle()
    assert len(bundle.curve) > 0
    assert bundle.spec.option_type == "payer"
    assert len(bundle.vol_slice) > 0


def test_csv_loaders_read_example_files():
    root = repo_root()
    curve = load_curve_points_csv(root / "data/european/example/curve_points.csv")
    quotes = load_market_quotes_csv(root / "data/european/example/market_quotes.csv")
    spec = load_swaption_spec_csv(root / "data/european/example/swaption_spec.csv")
    vol_slice = load_swaption_vol_slice_csv(root / "data/european/example/vol_slice.csv")
    assert len(curve) == 7
    assert len(quotes) == 7
    assert spec.strike == 0.0400
    assert len(vol_slice) == 5


def test_market_bundle_can_load_direct_curve_csv():
    root = repo_root()
    bundle = load_market_bundle(
        curve_csv=root / "data/european/example/curve_points.csv",
        spec_csv=root / "data/european/example/swaption_spec.csv",
        vol_slice_csv=root / "data/european/example/vol_slice.csv",
    )
    assert bundle.source == "market_csv"
    assert bundle.curve_source.endswith("data/european/example/curve_points.csv")
    assert bundle.spec_source.endswith("data/european/example/swaption_spec.csv")
    assert len(bundle.curve) == 7
    assert len(bundle.vol_slice) == 5


def test_market_bundle_can_bootstrap_from_market_quotes():
    root = repo_root()
    bundle = load_market_bundle(
        market_quotes_csv=root / "data/european/example/market_quotes.csv",
        spec_csv=root / "data/european/example/swaption_spec.csv",
        bootstrap_curve=True,
    )
    assert bundle.source == "market_csv"
    assert bundle.curve_source.endswith("data/european/example/market_quotes.csv")
    assert len(bundle.curve) == 7


def test_market_validation_helpers_return_expected_shapes():
    curve = sample_curve()
    rows = curve_node_rows(curve)
    discount_rows = discount_factor_rows(curve)
    summary = trade_summary(
        curve,
        SwaptionSpec(
            notional=10_000_000.0,
            expiry=2.0,
            tenor=5.0,
            strike=0.0400,
            pay_frequency=1,
            option_type="payer",
        ),
        black_vol=0.20,
    )
    assert len(rows) == len(curve)
    assert len(discount_rows) == len(curve)
    assert summary["black_price"] > 0.0


def test_load_json_metadata_reads_ust_snapshot():
    metadata = load_json_metadata(repo_root() / "data/european/market/ust_yield_curve_proxy/ust_yield_curve_snapshot.json")
    assert "yield_curve_date" in metadata


def test_load_project_data_supports_example_and_market_modes():
    root = repo_root()
    example_bundle = load_project_data(data_mode="example")
    market_bundle = load_project_data(
        data_mode="market",
        curve_csv=root / "data/european/example/curve_points.csv",
        spec_csv=root / "data/european/example/swaption_spec.csv",
    )
    assert example_bundle.source == "example"
    assert market_bundle.source == "market_csv"
    assert example_bundle.curve_source.endswith("data/european/example/curve_points.csv")


def test_auto_bundle_prefers_market_proxy_curve_when_available():
    bundle = load_auto_bundle()
    assert bundle.source == "market_auto"
    assert "data/european/market/curve_points.csv" in bundle.curve_source
    assert "data/european/market/swaption_spec.csv" in bundle.spec_source
    assert "data/european/market/vol_slice.csv" in bundle.vol_source


def test_load_project_data_supports_auto_mode():
    bundle = load_project_data(data_mode="auto")
    assert bundle.source == "market_auto"


def test_bermudan_helpers_build_expected_schedule_and_targets():
    spec = BermudanSwaptionSpec(
        notional=10_000_000.0,
        strike=0.0450,
        swap_tenor=10.0,
        pay_frequency=1,
        option_type="payer",
        exercise_dates=[1.0, 2.0, 3.0],
        maturity=10.0,
    )
    quotes = [
        SwaptionVolQuote(expiry=1.0, tenor=9.0, strike=0.0450, vol=0.22, vol_type="black"),
        SwaptionVolQuote(expiry=2.0, tenor=8.0, strike=0.0450, vol=0.21, vol_type="black"),
        SwaptionVolQuote(expiry=3.0, tenor=7.0, strike=0.0450, vol=0.20, vol_type="black"),
        SwaptionVolQuote(expiry=5.0, tenor=5.0, strike=0.0450, vol=0.17, vol_type="black"),
    ]
    assert bermudan_exercise_schedule(spec) == [1.0, 2.0, 3.0]
    assert coterminal_tenors(spec) == [9.0, 8.0, 7.0]
    assert len(build_bermudan_calibration_targets(spec, quotes)) == 3


def test_bermudan_lsmc_scaffold_helpers_return_expected_shapes():
    spec = BermudanSwaptionSpec(
        notional=10_000_000.0,
        strike=0.0450,
        swap_tenor=10.0,
        pay_frequency=1,
        option_type="payer",
        exercise_dates=[1.0, 2.0, 3.0],
        maturity=10.0,
    )
    grid = build_lsmc_time_grid(spec, MonteCarloConfig(num_paths=1000, delta_time=1.0))
    assert grid[0] == 0.0
    assert grid[-1] == 10.0
    assert polynomial_basis_vector(0.5) == [1.0, 0.5, 0.25]
    assert hw_model_summary(HullWhiteParams(mean_reversion=0.1, volatility=0.01))["volatility"] == 0.01


def test_bermudan_lsmc_summary_uses_namespaced_workflow():
    curve = sample_curve()
    spec = BermudanSwaptionSpec(
        notional=10_000_000.0,
        strike=0.0400,
        swap_tenor=5.0,
        pay_frequency=1,
        option_type="payer",
        exercise_dates=[1.0, 2.0, 3.0],
        maturity=7.0,
    )
    summary = bermudan_lsmc_skeleton_summary(
        curve,
        spec,
        HullWhiteParams(mean_reversion=0.03, volatility=0.01),
        MonteCarloConfig(num_paths=10, delta_time=0.5, seed=42, antithetic=True),
    )
    assert summary["exercise_dates"] == [1.0, 2.0, 3.0]
    assert len(summary["immediate_exercise_values"]) == 3
    assert summary["num_paths"] == 20


def test_load_sofr_history_csv_reads_sample_file():
    root = repo_root()
    observations = load_sofr_history_csv(root / "data/common/market/sofr/sofr_history.sample.csv")
    assert len(observations) == 5
    assert observations[-1].rate_percent == 3.65


def test_load_sofr_history_excel_reads_nyfed_export():
    root = repo_root()
    observations = load_sofr_history_excel(root / "data/common/market/sofr/SOFR_2026:01-0616.xlsx")
    assert len(observations) > 0
    assert observations[-1].date == "2026-06-12"
    assert observations[-1].rate_percent == 3.65


def test_latest_sofr_observation_from_excel_returns_last_row():
    root = repo_root()
    observation = latest_sofr_observation_from_excel(root / "data/common/market/sofr/SOFR_2026:01-0616.xlsx")
    assert observation.date == "2026-06-12"
    assert observation.rate_percent == 3.65


def test_latest_sofr_observation_returns_last_row():
    root = repo_root()
    observation = latest_sofr_observation(root / "data/common/market/sofr/sofr_history.sample.csv")
    assert observation.date == "2026-06-12"
    assert observation.rate_percent == 3.65


def test_sofr_observation_maps_to_market_quote():
    quote = sofr_to_market_quote(latest_sofr_observation(repo_root() / "data/common/market/sofr/sofr_history.sample.csv"))
    assert quote.instrument_type == "deposit"
    assert abs(quote.rate - 0.0365) < 1e-12


def test_write_sofr_market_quote_csv_creates_normalized_file(tmp_path):
    source = repo_root() / "data/common/market/sofr/sofr_history.sample.csv"
    output = tmp_path / "sofr_quote.csv"
    write_sofr_market_quote_csv(source, output)
    rows = load_market_quotes_csv(output)
    assert len(rows) == 1
    assert rows[0].instrument_type == "deposit"


def test_write_sofr_history_csv_from_observations_creates_fred_style_file(tmp_path):
    observations = [
        latest_sofr_observation(repo_root() / "data/common/market/sofr/sofr_history.sample.csv"),
    ]
    output = tmp_path / "history.csv"
    write_sofr_history_csv_from_observations(observations, output)
    text = output.read_text(encoding="utf-8")
    assert "DATE,SOFR" in text


def test_write_sofr_metadata_json_creates_summary_file(tmp_path):
    source = repo_root() / "data/common/market/sofr/sofr_history.sample.csv"
    output = tmp_path / "sofr_metadata.json"
    write_sofr_metadata_json(source, output)
    assert output.exists()
    assert "latest_rate_percent" in output.read_text(encoding="utf-8")


def test_build_fred_sofr_csv_url_contains_series_id():
    url = build_fred_sofr_csv_url(cosd="2026-01-01", coed="2026-06-12")
    assert "id=SOFR" in url
    assert "cosd=2026-01-01" in url
    assert "coed=2026-06-12" in url


def test_build_ust_snapshot_url_contains_date_and_offset():
    url = build_ust_snapshot_url(date="2026-06-12", offset=0)
    assert "date=2026-06-12" in url
    assert "offset=0" in url


def test_snapshot_to_curve_points_maps_expected_maturities():
    snapshot = {
        "yield_1m": 3.69,
        "yield_3m": 3.78,
        "yield_1y": 3.86,
        "yield_2y": 4.09,
        "yield_10y": 4.48,
        "yield_30y": 4.97,
    }
    points = snapshot_to_curve_points(snapshot)
    assert len(points) == 6
    assert abs(points[0].zero_rate - 0.0369) < 1e-12
    assert any(abs(point.maturity - 10.0) < 1e-12 for point in points)


def test_write_curve_points_csv_creates_loader_compatible_file(tmp_path):
    points = snapshot_to_curve_points({"yield_1m": 3.69, "yield_1y": 3.86, "yield_10y": 4.48})
    output = tmp_path / "curve_points.csv"
    write_curve_points_csv(points, output)
    loaded = load_curve_points_csv(output)
    assert len(loaded) == 3


def test_write_snapshot_metadata_creates_json(tmp_path):
    snapshot = {"yield_curve_date": "2026-06-12", "yield_10y": 4.48}
    output = tmp_path / "snapshot.json"
    write_snapshot_metadata(snapshot, output)
    assert output.exists()
    assert "yield_curve_date" in output.read_text(encoding="utf-8")


def test_prepare_sofr_data_bundle_writes_expected_outputs(tmp_path, monkeypatch):
    source = repo_root() / "data/common/market/sofr/sofr_history.sample.csv"

    def fake_download(output_path, *, cosd=None, coed=None):
        Path(output_path).write_bytes(source.read_bytes())
        return Path(output_path)

    monkeypatch.setattr("swaption_pricing.market.sofr.download_sofr_history_csv", fake_download)
    outputs = prepare_sofr_data_bundle(tmp_path)
    assert outputs["history_csv"].exists()
    assert outputs["quote_csv"].exists()
    assert outputs["metadata_json"].exists()


def test_prepare_sofr_data_bundle_from_local_csv_writes_expected_outputs(tmp_path):
    source = repo_root() / "data/common/market/sofr/sofr_history.sample.csv"
    outputs = prepare_sofr_data_bundle_from_local_csv(source, tmp_path)
    assert outputs["history_csv"].exists()
    assert outputs["quote_csv"].exists()
    assert outputs["metadata_json"].exists()


def test_prepare_sofr_data_bundle_from_excel_writes_expected_outputs(tmp_path):
    source = repo_root() / "data/common/market/sofr/SOFR_2026:01-0616.xlsx"
    outputs = prepare_sofr_data_bundle_from_excel(source, tmp_path)
    assert outputs["history_csv"].exists()
    assert outputs["quote_csv"].exists()
    assert outputs["metadata_json"].exists()


def test_daily_curve_builder_returns_daily_points():
    curve = bootstrap_zero_curve(sample_quotes())
    daily_curve = build_daily_zero_curve(curve, last_maturity=1.0)
    assert len(daily_curve) == 365
    assert daily_curve[0].maturity == 1.0 / 365.0
    assert daily_curve[-1].maturity == 1.0


def test_interpolated_zero_rate_is_between_neighboring_nodes():
    curve = bootstrap_zero_curve(sample_quotes())
    interpolated = zero_rate(curve, 2.5)
    lower = zero_rate(curve, 2.0)
    upper = zero_rate(curve, 3.0)
    assert min(lower, upper) <= interpolated <= max(lower, upper)


def test_swaption_price_positive():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    price = price_swaption(sample_curve(), spec, vol=0.20)
    assert price > 0.0


def test_black_price_increases_with_volatility():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    low_vol_price = price_swaption(sample_curve(), spec, vol=0.10)
    high_vol_price = price_swaption(sample_curve(), spec, vol=0.30)
    assert high_vol_price > low_vol_price


def test_payer_price_decreases_with_higher_strike():
    curve = sample_curve()
    low_strike_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0350,
        pay_frequency=1,
        option_type="payer",
    )
    high_strike_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0450,
        pay_frequency=1,
        option_type="payer",
    )
    assert price_swaption(curve, low_strike_spec, vol=0.20) > price_swaption(curve, high_strike_spec, vol=0.20)


def test_receiver_price_increases_with_higher_strike():
    curve = sample_curve()
    low_strike_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0350,
        pay_frequency=1,
        option_type="receiver",
    )
    high_strike_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0450,
        pay_frequency=1,
        option_type="receiver",
    )
    assert price_swaption(curve, high_strike_spec, vol=0.20) > price_swaption(curve, low_strike_spec, vol=0.20)


def test_intrinsic_value_not_greater_than_black_price():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    intrinsic = intrinsic_value(sample_curve(), spec)
    price = price_swaption(sample_curve(), spec, vol=0.20)
    assert intrinsic <= price


def test_time_value_is_non_negative():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    assert time_value(sample_curve(), spec, vol=0.20) >= 0.0


def test_moneyness_label_for_payer_changes_with_strike():
    curve = sample_curve()
    itm_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0350,
        pay_frequency=1,
        option_type="payer",
    )
    otm_spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0450,
        pay_frequency=1,
        option_type="payer",
    )
    assert moneyness_label(curve, itm_spec, tolerance=0.0010) == "ITM"
    assert moneyness_label(curve, otm_spec, tolerance=0.0010) == "OTM"


def test_sabr_implied_volatility_positive():
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    implied_vol = sabr_implied_volatility(forward=0.0400, strike=0.0400, expiry=2.0, params=params)
    assert implied_vol > 0.0


def test_higher_alpha_increases_atm_sabr_vol():
    low_alpha = SabrParams(alpha=0.0150, beta=0.50, rho=-0.25, nu=0.40)
    high_alpha = SabrParams(alpha=0.0300, beta=0.50, rho=-0.25, nu=0.40)
    low_vol = sabr_implied_volatility(forward=0.0400, strike=0.0400, expiry=2.0, params=low_alpha)
    high_vol = sabr_implied_volatility(forward=0.0400, strike=0.0400, expiry=2.0, params=high_alpha)
    assert high_vol > low_vol


def test_higher_nu_increases_smile_curvature_at_the_wings():
    low_nu = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.20)
    high_nu = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.70)
    low_nu_wing = sabr_implied_volatility(forward=0.0400, strike=0.0300, expiry=2.0, params=low_nu)
    high_nu_wing = sabr_implied_volatility(forward=0.0400, strike=0.0300, expiry=2.0, params=high_nu)
    assert high_nu_wing > low_nu_wing


def test_rho_changes_skew_direction_between_low_and_high_strikes():
    negative_rho = SabrParams(alpha=0.0200, beta=0.50, rho=-0.50, nu=0.40)
    positive_rho = SabrParams(alpha=0.0200, beta=0.50, rho=0.30, nu=0.40)
    neg_low = sabr_implied_volatility(forward=0.0400, strike=0.0300, expiry=2.0, params=negative_rho)
    neg_high = sabr_implied_volatility(forward=0.0400, strike=0.0500, expiry=2.0, params=negative_rho)
    pos_low = sabr_implied_volatility(forward=0.0400, strike=0.0300, expiry=2.0, params=positive_rho)
    pos_high = sabr_implied_volatility(forward=0.0400, strike=0.0500, expiry=2.0, params=positive_rho)
    assert neg_low > neg_high
    assert pos_low < pos_high


def test_sabr_adjusted_price_positive():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    price, implied_vol = price_swaption_with_sabr(sample_curve(), spec, params)
    assert implied_vol > 0.0
    assert price > 0.0


def test_shifted_black_handles_negative_forward_and_strike():
    payoff = price_shifted_black(-0.0020, -0.0010, 2.0, 0.20, 0.03, "payer")
    assert payoff >= 0.0


def test_shifted_sabr_implied_volatility_positive_for_negative_inputs():
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    implied_vol = shifted_sabr_implied_volatility(-0.0020, -0.0010, 2.0, params, 0.03)
    assert implied_vol > 0.0


def test_shifted_sabr_swaption_price_positive():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    price, implied_vol = price_swaption_with_shifted_sabr(sample_curve(), spec, params, 0.03)
    assert implied_vol > 0.0
    assert price > 0.0


def test_shifted_black_matches_standard_black_for_zero_shift_on_positive_inputs():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    standard = price_swaption(sample_curve(), spec, 0.20)
    shifted = price_swaption_shifted_black(sample_curve(), spec, 0.20, 0.0)
    assert abs(standard - shifted) < 1e-10


def test_shifted_black_price_changes_with_shift_choice():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    small_shift = price_swaption_shifted_black(sample_curve(), spec, 0.20, 0.01)
    large_shift = price_swaption_shifted_black(sample_curve(), spec, 0.20, 0.05)
    assert abs(large_shift - small_shift) > 1e-8


def test_shifted_sabr_vol_changes_with_shift_choice():
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    small_shift = shifted_sabr_implied_volatility(-0.0020, -0.0010, 2.0, params, 0.02)
    large_shift = shifted_sabr_implied_volatility(-0.0020, -0.0010, 2.0, params, 0.05)
    assert abs(large_shift - small_shift) > 1e-10


def test_sabr_risk_outputs_finite():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    risk = calculate_sabr_risk(sample_curve(), spec, params)
    assert isinstance(risk.pv01, float)
    assert isinstance(risk.vega, float)
    assert isinstance(risk.theta, float)


def test_black_and_sabr_comparison_result_positive_prices():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    result = compare_black_and_sabr_risk(sample_curve(), spec, black_vol=0.20, sabr_params=params)
    assert result.black_price > 0.0
    assert result.sabr_price > 0.0
    assert result.sabr_vol > 0.0


def test_sabr_calibration_recovers_synthetic_smile():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]
    result = calibrate_sabr_to_vols(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        initial_guess=(0.0180, -0.10, 0.30),
    )
    assert result.success
    assert result.objective_value < 1e-8


def test_calibration_rows_match_number_of_strikes():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]
    result = calibrate_sabr_to_vols(forward, strikes, expiry, market_vols, beta=0.50, initial_guess=(0.0180, -0.10, 0.30))
    rows = calibration_rows(result)
    assert len(rows) == len(strikes)
    assert all(isinstance(row.residual, float) for row in rows)


def test_calibration_diagnostics_are_small_for_synthetic_fit():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]
    result = calibrate_sabr_to_vols(forward, strikes, expiry, market_vols, beta=0.50, initial_guess=(0.0180, -0.10, 0.30))
    diagnostics = calibration_diagnostics(result)
    assert diagnostics.max_abs_error < 1e-6
    assert diagnostics.rmse < 1e-6


def test_multiple_initial_guesses_return_successful_calibrations():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]
    results = calibrate_sabr_for_multiple_initial_guesses(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        initial_guesses=[(0.0180, -0.10, 0.30), (0.0300, -0.50, 0.80)],
    )
    assert len(results) == 2
    assert all(result.success for result in results)


def test_beta_sweep_returns_one_result_per_beta():
    forward = 0.0400
    expiry = 2.0
    strikes = [0.0300, 0.0350, 0.0400, 0.0450, 0.0500]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [sabr_implied_volatility(forward, strike, expiry, true_params) for strike in strikes]
    results = calibrate_sabr_across_beta_values(
        forward,
        strikes,
        expiry,
        market_vols,
        beta_values=[0.0, 0.5, 1.0],
        initial_guess=(0.0180, -0.10, 0.30),
    )
    assert len(results) == 3
    assert [result.params.beta for result in results] == [0.0, 0.5, 1.0]


def test_shifted_sabr_calibration_recovers_shifted_synthetic_smile():
    forward = -0.0020
    expiry = 2.0
    strikes = [-0.0100, -0.0050, -0.0010, 0.0020, 0.0060]
    shift = 0.03
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [shifted_sabr_implied_volatility(forward, strike, expiry, true_params, shift) for strike in strikes]
    result = calibrate_shifted_sabr_to_vols(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        shift=shift,
        initial_guess=(0.0180, -0.10, 0.30),
    )
    assert result.success
    assert calibration_diagnostics(result).rmse < 1e-6


def test_shift_sweep_returns_one_result_per_shift():
    forward = -0.0020
    expiry = 2.0
    strikes = [-0.0100, -0.0050, -0.0010, 0.0020, 0.0060]
    true_params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    market_vols = [shifted_sabr_implied_volatility(forward, strike, expiry, true_params, 0.03) for strike in strikes]
    results = calibrate_shifted_sabr_across_shifts(
        forward,
        strikes,
        expiry,
        market_vols,
        beta=0.50,
        shifts=[0.02, 0.03, 0.05],
        initial_guess=(0.0180, -0.10, 0.30),
    )
    assert len(results) == 3
    assert [shift for shift, _ in results] == [0.02, 0.03, 0.05]


def test_bachelier_price_positive():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    price = price_swaption_bachelier(sample_curve(), spec, normal_vol=0.01)
    assert price > 0.0


def test_bachelier_price_increases_with_normal_vol():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    low_vol_price = price_swaption_bachelier(sample_curve(), spec, normal_vol=0.005)
    high_vol_price = price_swaption_bachelier(sample_curve(), spec, normal_vol=0.015)
    assert high_vol_price > low_vol_price


def test_bachelier_handles_negative_forward_and_strike():
    payer_payoff = bachelier_option_value(-0.0020, -0.0010, 2.0, 0.01, "payer")
    receiver_payoff = bachelier_option_value(-0.0020, -0.0010, 2.0, 0.01, "receiver")
    assert payer_payoff >= 0.0
    assert receiver_payoff >= 0.0


def test_shifted_black_risk_outputs_finite():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    risk = calculate_shifted_black_risk(sample_curve(), spec, vol=0.20, shift=0.03)
    assert isinstance(risk.pv01, float)
    assert isinstance(risk.vega, float)
    assert isinstance(risk.theta, float)


def test_shifted_sabr_risk_outputs_finite():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    risk = calculate_shifted_sabr_risk(sample_curve(), spec, params, shift=0.03)
    assert isinstance(risk.pv01, float)
    assert isinstance(risk.vega, float)
    assert isinstance(risk.theta, float)


def test_bachelier_risk_outputs_finite():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    risk = calculate_bachelier_risk(sample_curve(), spec, normal_vol=0.01)
    assert isinstance(risk.pv01, float)
    assert isinstance(risk.vega, float)
    assert isinstance(risk.theta, float)


def test_compare_all_model_risks_returns_positive_prices():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    comparison = compare_all_model_risks(
        curve=sample_curve(),
        spec=spec,
        black_vol=0.20,
        sabr_params=params,
        shift=0.03,
        normal_vol=0.01,
    )
    assert comparison.black.price > 0.0
    assert comparison.sabr.price > 0.0
    assert comparison.shifted_black.price > 0.0
    assert comparison.shifted_sabr.price > 0.0
    assert comparison.bachelier.price > 0.0


def test_swap_pv01_is_finite_for_forward_starting_swap():
    hedge_rate = forward_swap_rate(sample_curve(), expiry=2.0, tenor=5.0, pay_frequency=1)
    pv01 = swap_pv01(
        curve=sample_curve(),
        notional=1.0,
        fixed_rate=hedge_rate,
        start=2.0,
        tenor=5.0,
        pay_frequency=1,
        swap_type="payer",
    )
    assert isinstance(pv01, float)
    assert abs(pv01) > 0.0


def test_cross_model_hedging_reduces_parallel_shift_pnl_for_black():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    comparison = compare_model_hedging(
        curve=sample_curve(),
        spec=spec,
        black_vol=0.20,
        sabr_params=params,
        shift=0.03,
        normal_vol=0.01,
        rate_shift=0.0025,
    )
    assert abs(comparison.black.hedged_pnl) < abs(comparison.black.unhedged_pnl)


def test_cross_model_hedging_returns_results_for_all_models():
    spec = SwaptionSpec(
        notional=10_000_000.0,
        expiry=2.0,
        tenor=5.0,
        strike=0.0400,
        pay_frequency=1,
        option_type="payer",
    )
    params = SabrParams(alpha=0.0200, beta=0.50, rho=-0.25, nu=0.40)
    comparison = compare_model_hedging(
        curve=sample_curve(),
        spec=spec,
        black_vol=0.20,
        sabr_params=params,
        shift=0.03,
        normal_vol=0.01,
        rate_shift=-0.0025,
    )
    assert comparison.sabr.hedge_ratio != 0.0
    assert comparison.shifted_black.hedge_ratio != 0.0
    assert comparison.shifted_sabr.hedge_ratio != 0.0
    assert comparison.bachelier.hedge_ratio != 0.0
