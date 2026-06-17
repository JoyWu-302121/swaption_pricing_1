"""Shared dataclasses for core analytics inputs."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CurvePoint:
    maturity: float
    zero_rate: float


@dataclass(frozen=True)
class MarketQuote:
    instrument_type: str
    maturity: float
    rate: float
    pay_frequency: int = 1


@dataclass(frozen=True)
class SwaptionSpec:
    notional: float
    expiry: float
    tenor: float
    strike: float
    pay_frequency: int
    option_type: str


@dataclass(frozen=True)
class BermudanSwaptionSpec:
    notional: float
    strike: float
    swap_tenor: float
    pay_frequency: int
    option_type: str
    exercise_dates: Sequence[float]
    maturity: float


@dataclass(frozen=True)
class SwaptionVolQuote:
    expiry: float
    tenor: float
    strike: float
    vol: float
    vol_type: str


@dataclass(frozen=True)
class HullWhiteParams:
    mean_reversion: float
    volatility: float


@dataclass(frozen=True)
class MonteCarloConfig:
    num_paths: int
    delta_time: float
    seed: int | None = None
    antithetic: bool = True


@dataclass(frozen=True)
class BermudanLSMCResult:
    price: float
    exercise_probabilities: Sequence[float]
    exercise_counts: Sequence[int]
    time_grid: Sequence[float]


@dataclass(frozen=True)
class SofrObservation:
    date: str
    rate_percent: float


@dataclass(frozen=True)
class ProjectDataBundle:
    curve: Sequence["CurvePoint"]
    spec: SwaptionSpec
    market_quotes: Sequence[MarketQuote]
    vol_slice: Sequence[SwaptionVolQuote]
    source: str
    curve_source: str
    spec_source: str
    vol_source: str


@dataclass(frozen=True)
class RiskResult:
    pv01: float
    vega: float
    theta: float


@dataclass(frozen=True)
class ModelComparisonResult:
    black_price: float
    black_vol: float
    sabr_price: float
    sabr_vol: float
    black_risk: RiskResult
    sabr_risk: RiskResult


@dataclass(frozen=True)
class ModelRiskSummary:
    model: str
    price: float
    volatility: float
    risk: RiskResult


@dataclass(frozen=True)
class MultiModelRiskComparison:
    black: ModelRiskSummary
    sabr: ModelRiskSummary
    shifted_black: ModelRiskSummary
    shifted_sabr: ModelRiskSummary
    bachelier: ModelRiskSummary


@dataclass(frozen=True)
class HedgeEvaluation:
    model: str
    hedge_rate: float
    hedge_instrument_pv01: float
    hedge_ratio: float
    unhedged_pnl: float
    hedge_pnl: float
    hedged_pnl: float


@dataclass(frozen=True)
class MultiModelHedgingComparison:
    black: HedgeEvaluation
    sabr: HedgeEvaluation
    shifted_black: HedgeEvaluation
    shifted_sabr: HedgeEvaluation
    bachelier: HedgeEvaluation


Curve = Sequence[CurvePoint]
