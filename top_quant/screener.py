"""Top Quant screener — QuantWheel integration and filtering."""

import json
from typing import Optional, List
from datetime import datetime
from .models import Candidate, CandidateRating, PositioningData, MarketRegimeSummary
from .config import WEEKLY_FILTERS


class QuantWheelScreener:
    """Phase B: Weekly QuantWheel screen against SPX 500 + NDX 100."""

    def __init__(self, api_key: Optional[str] = None, use_mock: bool = True):
        self.api_key = api_key
        self.use_mock = use_mock
        self.candidates_raw = []

    def run_screen(self, universes: List[str]) -> List[dict]:
        """
        Run QuantWheel screen with established hard filters.
        Returns list of raw screening results.
        """
        if not self.api_key and self.use_mock:
            return self._mock_screen_results()

        # TODO: Integrate actual QuantWheel API
        # POST https://quantwheel.com/api/v1/screener
        # with filters from WEEKLY_FILTERS
        return self._mock_screen_results()

    def filter_core_four(self, results: List[dict]) -> List[dict]:
        """
        Phase B: Promote candidates with core four regime to top of board.
        Core four:
        - Gamma: Positive
        - Vanna: Positive
        - IV: Declining
        - 5-day Gamma buildup: Rising
        """
        core_four_survivors = []
        others = []

        for result in results:
            has_core_four = (
                result.get("gamma") == "Positive"
                and result.get("vanna") == "Positive"
                and result.get("iv_direction") == "declining"
                and result.get("gamma_buildup_5d") == "rising"
            )
            if has_core_four:
                core_four_survivors.append(result)
            else:
                others.append(result)

        return core_four_survivors + others

    def apply_hard_filters(self, results: List[dict]) -> List[dict]:
        """Apply hard filters from WEEKLY_FILTERS."""
        filtered = []
        for r in results:
            # Put Wall distance 0–3%
            if r.get("put_wall_distance_pct") is not None:
                if not (WEEKLY_FILTERS["put_wall_distance_min"] <=
                        r["put_wall_distance_pct"] <=
                        WEEKLY_FILTERS["put_wall_distance_max"]):
                    continue

            # Vanna bull/bear ratio >= 2.0x
            if r.get("vanna_bull_bear_ratio", 0) < WEEKLY_FILTERS["vanna_bull_bear_ratio_min"]:
                continue

            # RV/IV 1.00–1.50
            rv_iv = r.get("rv_iv_ratio")
            if rv_iv is not None:
                if not (WEEKLY_FILTERS["rv_iv_min"] <= rv_iv <= WEEKLY_FILTERS["rv_iv_max"]):
                    continue

            # Daily move -1% to +2%
            daily_move = r.get("daily_move_pct", 0)
            if not (WEEKLY_FILTERS["daily_move_min"] <= daily_move <= WEEKLY_FILTERS["daily_move_max"]):
                continue

            filtered.append(r)

        return filtered

    def _mock_screen_results(self) -> List[dict]:
        """Return mock screening results for development."""
        return [
            {
                "symbol": "AAPL",
                "spot": 230.50,
                "gamma": "Positive",
                "vanna": "Positive",
                "iv_direction": "declining",
                "gamma_buildup_5d": "rising",
                "vanna_bull_bear_ratio": 2.5,
                "put_wall": 227.0,
                "put_wall_distance_pct": 1.5,
                "call_wall": 235.0,
                "max_bull": 242.0,
                "rv_iv_ratio": 1.15,
                "daily_move_pct": -0.8,
                "put_wall_move_today": "up",
            },
            {
                "symbol": "MSFT",
                "spot": 450.75,
                "gamma": "Positive",
                "vanna": "Positive",
                "iv_direction": "declining",
                "gamma_buildup_5d": "rising",
                "vanna_bull_bear_ratio": 2.2,
                "put_wall": 445.0,
                "put_wall_distance_pct": 1.3,
                "call_wall": 460.0,
                "max_bull": 470.0,
                "rv_iv_ratio": 1.08,
                "daily_move_pct": 0.5,
                "put_wall_move_today": "up",
            },
            {
                "symbol": "NVDA",
                "spot": 140.25,
                "gamma": "Positive",
                "vanna": "Negative",  # Fails vanna filter
                "iv_direction": "declining",
                "gamma_buildup_5d": "rising",
                "vanna_bull_bear_ratio": 1.8,
                "put_wall": 138.0,
                "put_wall_distance_pct": 1.6,
                "call_wall": 148.0,
                "max_bull": 155.0,
                "rv_iv_ratio": 1.22,
                "daily_move_pct": 0.3,
                "put_wall_move_today": "up",
            },
            {
                "symbol": "TSLA",
                "spot": 280.00,
                "gamma": "Negative",  # Fails gamma filter
                "vanna": "Positive",
                "iv_direction": "rising",  # Fails IV filter
                "gamma_buildup_5d": "falling",
                "vanna_bull_bear_ratio": 1.5,
                "put_wall": 270.0,
                "put_wall_distance_pct": 3.6,  # Fails put wall distance
                "call_wall": 290.0,
                "max_bull": 300.0,
                "rv_iv_ratio": 0.95,  # Fails RV/IV
                "daily_move_pct": 2.2,  # Fails daily move max
                "put_wall_move_today": "down",
            },
        ]


class TrajectoryAnalyzer:
    """Phase C: Trajectory analysis for survivors."""

    def analyze(self, symbol: str, positioning_data: dict) -> dict:
        """
        Analyze direction and acceleration of:
        - IV 1D / 5D
        - Gamma buildup
        - Vanna B/B
        - Put Wall, Call Wall, Max Bull
        """
        # TODO: Fetch historical data from QuantWheel
        # For now, return structure with mock data
        return {
            "iv_1d_change": -2.5,  # % change
            "iv_5d_change": -8.2,
            "gamma_buildup_acceleration": "↑",
            "vanna_bb_trajectory": "2.1 → 2.5 → 2.8",
            "put_wall_migration": "↑",
            "call_wall_migration": "↑",
            "max_bull_migration": "↑",
        }
