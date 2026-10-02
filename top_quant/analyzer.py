"""Top Quant analyzer — Positioning, trajectory, and SMC structure analysis."""

from typing import Optional, Tuple
from .models import (
    Candidate, CandidateRating, PositioningData, TrajectoryMetrics,
    SmcStructure, PositioningCalculations, RunwayStatus
)


class PositioningAnalyzer:
    """Phase D, E, F: Positioning structure, trajectory, and SMC confirmation."""

    @staticmethod
    def calculate_positioning_metrics(
        spot: float,
        put_wall: Optional[float],
        call_wall: Optional[float],
        max_bull: Optional[float]
    ) -> PositioningCalculations:
        """
        Phase H: Calculate positioning R/R and upside/downside.
        """
        calcs = PositioningCalculations()

        if call_wall and spot:
            calcs.upside_to_call_wall = ((call_wall - spot) / spot) * 100
        if max_bull and spot:
            calcs.upside_to_max_bull = ((max_bull - spot) / spot) * 100
        if put_wall and spot:
            calcs.downside_to_put_wall = ((spot - put_wall) / spot) * 100

        if calcs.upside_to_max_bull and calcs.downside_to_put_wall:
            calcs.positioning_rr = calcs.upside_to_max_bull / calcs.downside_to_put_wall

        return calcs

    @staticmethod
    def classify_runway(
        call_wall: Optional[float],
        spot: float,
        max_bull: Optional[float],
        put_wall_migrating_up: bool,
        call_wall_migrating_up: bool
    ) -> RunwayStatus:
        """
        Classify runway as OPEN / COMPRESSED / BLOCKED.
        """
        if not call_wall:
            return RunwayStatus.OPEN

        call_wall_distance = ((call_wall - spot) / spot) * 100

        # BLOCKED: Call Wall < 2% away + no upward migration
        if call_wall_distance < 2.0 and not call_wall_migrating_up:
            return RunwayStatus.BLOCKED

        # COMPRESSED: Call Wall 2-5% away + limited reward
        if 2.0 <= call_wall_distance < 5.0:
            return RunwayStatus.COMPRESSED

        # OPEN: Call Wall migrating up, or >5% away
        if call_wall_migrating_up or call_wall_distance >= 5.0:
            return RunwayStatus.OPEN

        return RunwayStatus.COMPRESSED

    @staticmethod
    def assess_wall_pressure(
        num_tests: int,
        rejection_magnitude: float,
        rejections_getting_shallower: bool,
        call_oi_weakening: bool,
        buying_displacement_rising: bool
    ) -> str:
        """
        Classify Call Wall pressure.
        Returns one of: WALL_WEAKENING | WALL_HOLDING | WALL_STRENGTHENING
        """
        if rejections_getting_shallower and call_oi_weakening and buying_displacement_rising:
            return "🟢 WALL WEAKENING → BREAKOUT WATCH"
        elif not rejections_getting_shallower and not call_oi_weakening:
            return "🟡 WALL HOLDING → WAIT"
        else:
            return "🔴 WALL STRENGTHENING → AVOID / REJECTION RISK"


class SmcAnalyzer:
    """Phase F: Smart Money Concepts structural confirmation."""

    @staticmethod
    def assess_daily_structure(
        higher_highs: bool,
        higher_lows: bool,
        bullish_bos_choch: bool,
        holding_demand_block: bool,
        not_trapped_under_supply: bool
    ) -> bool:
        """
        1D SMC = directional permission.
        Require buyers in control: HH/HL, bullish BOS/CHOCH, holding demand, no trapped price.
        """
        return (higher_highs or higher_lows) and bullish_bos_choch and holding_demand_block and not_trapped_under_supply

    @staticmethod
    def assess_hourly_entry(
        liquidity_sweep_reclaim: bool,
        bullish_choch_bos: bool,
        displacement_from_demand: bool,
        higher_low_formation: bool,
        buyers_defending: bool,
        no_entry_into_supply: bool
    ) -> Tuple[bool, str]:
        """
        1H SMC = entry confirmation.
        Look for sweep/reclaim, CHOCH/BOS, displacement, higher lows, buyers defending.
        Returns (is_clean_entry, quality_label).
        """
        checks = [
            liquidity_sweep_reclaim,
            bullish_choch_bos,
            displacement_from_demand,
            higher_low_formation,
            buyers_defending,
            no_entry_into_supply
        ]
        passed = sum(checks)

        if passed >= 5:
            return True, "Clean"
        elif passed >= 3:
            return True, "Mixed"
        else:
            return False, "Blocked"


class RankingEngine:
    """Phase G: Ranking and scoring."""

    WEIGHT_GAMMA = 0.30
    WEIGHT_VANNA = 0.25
    WEIGHT_PUT_WALL = 0.15
    WEIGHT_RR = 0.15
    WEIGHT_IV = 0.10
    WEIGHT_PRICE = 0.05

    @staticmethod
    def score_gamma_buildup(
        buildup_5d_rising: bool,
        buildup_acceleration: Optional[str],
        vanna_bb_trajectory: Optional[str]
    ) -> float:
        """Score 0-100 for gamma buildup component (30% weight)."""
        score = 0.0

        if buildup_5d_rising:
            score += 60.0

        if buildup_acceleration == "↑":
            score += 40.0
        elif buildup_acceleration == "→":
            score += 20.0

        return min(score, 100.0)

    @staticmethod
    def score_vanna_strength(
        vanna_bull_bear_ratio: Optional[float],
        vanna_bb_trajectory: Optional[str]
    ) -> float:
        """Score 0-100 for Vanna B/B component (25% weight)."""
        score = 0.0

        if vanna_bull_bear_ratio:
            if vanna_bull_bear_ratio >= 3.0:
                score += 70.0
            elif vanna_bull_bear_ratio >= 2.5:
                score += 55.0
            elif vanna_bull_bear_ratio >= 2.0:
                score += 40.0

        # Check trajectory if available (e.g., "2.1 → 2.8 → 3.6")
        if vanna_bb_trajectory:
            # Simple heuristic: if last > first, trajectory is rising
            try:
                vals = [float(x.strip()) for x in vanna_bb_trajectory.split("→")]
                if vals[-1] > vals[0]:
                    score += 30.0
            except ValueError:
                pass

        return min(score, 100.0)

    @staticmethod
    def score_put_wall_behavior(
        put_wall_distance_pct: Optional[float],
        put_wall_migrating_up: bool,
        put_wall_move_today: str
    ) -> float:
        """Score 0-100 for Put Wall behavior (15% weight)."""
        score = 0.0

        # Prefer 0-3% (close, supportive)
        if put_wall_distance_pct is not None:
            if put_wall_distance_pct <= 1.5:
                score += 60.0
            elif put_wall_distance_pct <= 3.0:
                score += 40.0

        # Migration up = strong
        if put_wall_migrating_up:
            score += 40.0

        # Move today up
        if put_wall_move_today == "up":
            score += 20.0

        return min(score, 100.0)

    @staticmethod
    def score_positioning_rr(positioning_rr: Optional[float]) -> float:
        """Score 0-100 for R/R (15% weight)."""
        if not positioning_rr:
            return 0.0

        if positioning_rr >= 2.0:
            return 100.0
        elif positioning_rr >= 1.5:
            return 75.0
        elif positioning_rr >= 1.0:
            return 50.0
        else:
            return 25.0

    @staticmethod
    def score_iv_contraction(iv_1d_change: Optional[float], iv_5d_change: Optional[float]) -> float:
        """Score 0-100 for IV contraction (10% weight)."""
        score = 0.0

        if iv_1d_change and iv_1d_change < 0:  # Declining
            score += 50.0
        if iv_5d_change and iv_5d_change < 0:
            score += 50.0

        return min(score, 100.0)

    @staticmethod
    def score_price_volume(smc_daily_clean: bool, smc_hourly_clean: bool, vol_positive: bool = True) -> float:
        """Score 0-100 for price/volume confirmation (5% weight)."""
        score = 0.0

        if smc_daily_clean:
            score += 40.0
        if smc_hourly_clean:
            score += 40.0
        if vol_positive:
            score += 20.0

        return min(score, 100.0)

    @classmethod
    def calculate_raw_score(cls, candidate: Candidate) -> float:
        """Calculate composite raw score 0-100."""
        gamma = cls.score_gamma_buildup(
            candidate.weekly_positioning.gamma_buildup_5d == "Rising",
            candidate.trajectory.gamma_buildup_acceleration,
            candidate.trajectory.vanna_bb_trajectory
        )
        vanna = cls.score_vanna_strength(
            candidate.weekly_positioning.vanna_bull_bear_ratio,
            candidate.trajectory.vanna_bb_trajectory
        )
        put_wall = cls.score_put_wall_behavior(
            # Rough calculation from positioning data
            (candidate.weekly_positioning.spot - candidate.weekly_positioning.put_wall) /
            candidate.weekly_positioning.spot * 100 if candidate.weekly_positioning.put_wall else None,
            candidate.trajectory.put_wall_migration == "↑",
            candidate.weekly_positioning.put_wall_direction or "→"
        )
        rr = cls.score_positioning_rr(candidate.calcs.positioning_rr)
        iv = cls.score_iv_contraction(
            candidate.trajectory.iv_1d_change,
            candidate.trajectory.iv_5d_change
        )
        price = cls.score_price_volume(
            candidate.smc_1d.daily_buyer_control,
            candidate.smc_1h.entry_quality == "Clean"
        )

        raw = (
            gamma * cls.WEIGHT_GAMMA +
            vanna * cls.WEIGHT_VANNA +
            put_wall * cls.WEIGHT_PUT_WALL +
            rr * cls.WEIGHT_RR +
            iv * cls.WEIGHT_IV +
            price * cls.WEIGHT_PRICE
        )

        return raw

    @classmethod
    def classify_candidate(cls, candidate: Candidate, raw_score: float) -> CandidateRating:
        """Classify candidate based on raw score + structural overlays."""

        # Core four check
        has_core_four = (
            candidate.weekly_positioning.gamma == "Positive" and
            candidate.weekly_positioning.vanna == "Positive" and
            candidate.trajectory.iv_1d_change and candidate.trajectory.iv_1d_change < 0 and
            candidate.weekly_positioning.gamma_buildup_5d == "Rising"
        )

        if not has_core_four:
            return CandidateRating.PASS

        # A+ PRIME: Core four + strong secondary + open runway
        if (raw_score >= 75 and
            candidate.monthly_aligned and
            candidate.flashalpha_confirmed and
            candidate.smc_1d.daily_buyer_control and
            candidate.runway == RunwayStatus.OPEN):
            return CandidateRating.A_PLUS_PRIME

        # A: Core four + minor weakness
        if raw_score >= 65 and candidate.smc_1d.daily_buyer_control:
            return CandidateRating.A

        # WATCH: Core four developing but not all confirmations ready
        if raw_score >= 55:
            return CandidateRating.WATCH

        # BREAKOUT: Negative gamma + weakening Call Wall (separate regime)
        if (candidate.weekly_positioning.gamma == "Negative" and
            candidate.trajectory.call_wall_migration == "↑"):
            return CandidateRating.BREAKOUT

        return CandidateRating.PASS
