"""Top Quant configuration and constants."""

from dataclasses import dataclass

# Universe
SPX_500_UNIVERSE = "SPX_500"
NDX_100_UNIVERSE = "NDX_100"
UNIVERSE = [SPX_500_UNIVERSE, NDX_100_UNIVERSE]

# Weekly QuantWheel Filter (Phase B)
WEEKLY_FILTERS = {
    "anchor": "weekly",
    "gamma": "positive",
    "vanna": "positive",
    "put_wall_distance_min": 0,  # 0–3%
    "put_wall_distance_max": 3,
    "gamma_buildup_5d": "rising",
    "put_wall_move_today": "up",
    "vanna_bull_bear_ratio_min": 2.0,
    "rv_iv_min": 1.00,
    "rv_iv_max": 1.50,
    "daily_move_min": -1.0,  # -1% to +2%
    "daily_move_max": 2.0,
    "iv_confirmation": "declining",
}

# RV/IV flexibility
RV_IV_RESEARCH_MIN = 0.80
RV_IV_RESEARCH_MAX = 1.75

# Ranking Weights (Phase G)
RANKING_WEIGHTS = {
    "gamma_buildup": 0.30,
    "vanna_strength": 0.25,
    "put_wall_behavior": 0.15,
    "positioning_rr": 0.15,
    "iv_contraction": 0.10,
    "price_volume": 0.05,
}

# Thresholds for classification (Phase A/B)
CORE_FOUR_REQUIRED = ["gamma_positive", "vanna_positive", "iv_declining", "gamma_buildup_rising"]

# Call Wall Pressure Classifications (Phase E)
WALL_PRESSURE_WEAKENING = "🟢 WALL WEAKENING → BREAKOUT WATCH"
WALL_PRESSURE_HOLDING = "🟡 WALL HOLDING → WAIT"
WALL_PRESSURE_STRENGTHENING = "🔴 WALL STRENGTHENING → AVOID / REJECTION RISK"

# Confidence Levels
CONFIDENCE_A_PLUS = "A+ PRIME"
CONFIDENCE_A = "A"
CONFIDENCE_WATCH = "WATCH"
CONFIDENCE_BREAKOUT = "BREAKOUT"
CONFIDENCE_PASS = "PASS"


@dataclass
class ScreeningConfig:
    """Screening configuration."""
    universe: list = None
    weekly_filters: dict = None
    enforce_hard_filters: bool = True
    use_research_range: bool = False  # Allow 0.80–1.75 RV/IV

    def __post_init__(self):
        if self.universe is None:
            self.universe = UNIVERSE
        if self.weekly_filters is None:
            self.weekly_filters = WEEKLY_FILTERS


@dataclass
class DataSourceConfig:
    """Data source configuration."""
    quantwheel_api_key: str = None
    flashalpha_api_key: str = None
    tradingview_access: bool = True
    bigdata_access: bool = True
    allow_mock_data: bool = True  # Fall back to mock if API unavailable
