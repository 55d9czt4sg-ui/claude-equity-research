"""Data models for Top Quant analysis."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class CandidateRating(Enum):
    """Top Quant candidate classification."""
    A_PLUS_PRIME = "🔥 A+ PRIME"
    A = "🟢 A"
    WATCH = "🟡 WATCH"
    BREAKOUT = "⚡ BREAKOUT"
    PASS = "❌ PASS"


class RunwayStatus(Enum):
    """Positioning runway classification."""
    OPEN = "🟢 OPEN"
    COMPRESSED = "🟡 COMPRESSED"
    BLOCKED = "🔴 BLOCKED"


@dataclass
class PositioningData:
    """Options positioning snapshot."""
    spot: Optional[float] = None
    gamma: Optional[str] = None  # "Positive" | "Negative"
    vanna: Optional[str] = None  # "Positive" | "Negative"
    vanna_bull_bear_ratio: Optional[float] = None
    put_wall: Optional[float] = None
    put_wall_direction: Optional[str] = None  # "↑" | "↓"
    call_wall: Optional[float] = None
    call_wall_direction: Optional[str] = None
    max_bull: Optional[float] = None
    gamma_flip: Optional[float] = None
    vanna_flip: Optional[float] = None
    rv_iv_ratio: Optional[float] = None
    daily_move: Optional[float] = None  # e.g., -1.2 to +2.5
    gamma_buildup_5d: Optional[str] = None  # "Rising" | "Stable" | "Falling"
    timestamp: Optional[str] = None
    expiry: Optional[str] = None


@dataclass
class TrajectoryMetrics:
    """Position/indicator trajectory over time."""
    iv_1d_change: Optional[float] = None  # % change
    iv_5d_change: Optional[float] = None
    gamma_buildup_acceleration: Optional[str] = None  # "↑" | "→" | "↓"
    vanna_bb_trajectory: Optional[str] = None  # e.g., "2.1 → 2.8 → 3.6"
    put_wall_migration: Optional[str] = None  # "↑" | "↓" | "Static"
    call_wall_migration: Optional[str] = None
    max_bull_migration: Optional[str] = None


@dataclass
class SmcStructure:
    """Smart Money Concepts price structure."""
    daily_buyer_control: bool = False  # Higher highs, bullish BOS/CHOCH
    daily_demand_level: Optional[float] = None
    daily_supply_level: Optional[float] = None
    hourly_bos_choch: Optional[str] = None  # "Bullish" | "Bearish" | "Neutral"
    hourly_order_block: Optional[float] = None
    hourly_sweep_reclaim: bool = False
    entry_quality: Optional[str] = None  # "Clean" | "Mixed" | "Blocked"


@dataclass
class PositioningCalculations:
    """Derived positioning metrics."""
    upside_to_call_wall: Optional[float] = None  # %
    upside_to_max_bull: Optional[float] = None  # %
    downside_to_put_wall: Optional[float] = None  # %
    positioning_rr: Optional[float] = None  # Upside / Downside


@dataclass
class Candidate:
    """Top Quant candidate setup."""
    symbol: str
    rating: CandidateRating
    spot: float
    timestamp: datetime

    # Positioning regime
    weekly_positioning: PositioningData = field(default_factory=PositioningData)
    monthly_positioning: Optional[PositioningData] = None
    nearest_expiry_positioning: Optional[PositioningData] = None

    # Trajectory
    trajectory: TrajectoryMetrics = field(default_factory=TrajectoryMetrics)

    # Structure confirmation
    smc_1d: SmcStructure = field(default_factory=SmcStructure)
    smc_1h: SmcStructure = field(default_factory=SmcStructure)

    # Calculations
    calcs: PositioningCalculations = field(default_factory=PositioningCalculations)

    # Additional
    runway: RunwayStatus = RunwayStatus.OPEN
    monthly_aligned: bool = False
    flashalpha_confirmed: bool = False
    event_risk: Optional[str] = None
    entry_condition: Optional[str] = None
    invalidation_level: Optional[float] = None
    first_target: Optional[float] = None
    second_target: Optional[float] = None

    # Scoring
    raw_score: float = 0.0  # 0-100
    final_rank: int = 0

    def score_summary(self) -> dict:
        """Return breakdown of scoring components (0-100 each)."""
        return {
            "gamma_buildup": 0,  # 30%
            "vanna_strength": 0,  # 25%
            "put_wall_behavior": 0,  # 15%
            "positioning_rr": 0,  # 15%
            "iv_contraction": 0,  # 10%
            "price_volume": 0,  # 5%
        }


@dataclass
class MarketRegimeSummary:
    """Broad market context."""
    as_of: datetime
    spy_gex_regime: Optional[str] = None  # "Positive" | "Negative" | "Neutral"
    qqq_gex_regime: Optional[str] = None
    market_state: Optional[str] = None  # "Compressed" | "Trending" | "Acceleration"
    major_events: list = field(default_factory=list)
    iv_direction: Optional[str] = None  # "Declining" | "Rising"


@dataclass
class TopQuantReport:
    """Complete Top Quant daily report."""
    as_of: datetime
    market_regime: Optional[MarketRegimeSummary] = None
    candidates: dict[str, Candidate] = field(default_factory=dict)  # symbol -> Candidate

    def get_by_rating(self, rating: CandidateRating) -> list[Candidate]:
        """Filter candidates by rating."""
        return [c for c in self.candidates.values() if c.rating == rating]

    def ranked_board(self) -> list[Candidate]:
        """Return candidates ranked by final_rank (ascending = best)."""
        return sorted(self.candidates.values(), key=lambda x: x.final_rank)
