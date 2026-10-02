"""Top Quant runner — Main orchestration across all phases."""

from datetime import datetime
from typing import Optional, List
from .models import (
    Candidate, CandidateRating, TopQuantReport, MarketRegimeSummary,
    PositioningData, TrajectoryMetrics, SmcStructure, PositioningCalculations
)
from .screener import QuantWheelScreener, TrajectoryAnalyzer
from .analyzer import PositioningAnalyzer, SmcAnalyzer, RankingEngine
from .reporter import TopQuantReporter
from .config import ScreeningConfig, DataSourceConfig


class TopQuantRunner:
    """
    Orchestrates all 9 phases of Top Quant analysis.

    Phase A: Market context
    Phase B: Weekly QuantWheel screen
    Phase C: Trajectory analysis
    Phase D: Monthly confirmation
    Phase E: FlashAlpha confirmation
    Phase F: SMC structure
    Phase G: Rank and score
    Phase H: Timing (nearest expiry)
    Phase I: Trade plan (pre-entry validation)
    """

    def __init__(
        self,
        screening_config: Optional[ScreeningConfig] = None,
        data_config: Optional[DataSourceConfig] = None
    ):
        self.screening_config = screening_config or ScreeningConfig()
        self.data_config = data_config or DataSourceConfig()
        self.screener = QuantWheelScreener(
            api_key=data_config.quantwheel_api_key if data_config else None,
            use_mock=data_config.allow_mock_data if data_config else True
        )
        self.trajectory = TrajectoryAnalyzer()
        self.reporter = TopQuantReporter()

    def run(self) -> TopQuantReport:
        """Execute complete Top Quant daily analysis."""
        report = TopQuantReport(as_of=datetime.utcnow())

        # Phase A: Market context
        print("📊 Phase A: Gathering market context...")
        report.market_regime = self._phase_a_market_context()

        # Phase B: Weekly QuantWheel screen
        print("🔍 Phase B: Running QuantWheel weekly screen...")
        screened_symbols = self._phase_b_weekly_screen()

        # Phase C–G: Deep dive on survivors
        print("📈 Phase C–G: Trajectory, monthly, FlashAlpha, SMC, ranking...")
        for symbol_data in screened_symbols:
            candidate = self._phase_c_to_g(symbol_data, report.market_regime)
            if candidate:
                report.candidates[candidate.symbol] = candidate

        # Phase H: Timing (nearest expiry context)
        print("⏰ Phase H: Entry timing analysis...")
        for candidate in report.candidates.values():
            candidate.entry_condition = self._phase_h_entry_timing(candidate)

        # Phase I: Trade plan validation
        print("✓ Phase I: Validating trade plans...")
        for candidate in report.candidates.values():
            self._phase_i_trade_plan(candidate)

        return report

    def _phase_a_market_context(self) -> MarketRegimeSummary:
        """
        Phase A: Check major event risk, broad dealer regime.
        """
        regime = MarketRegimeSummary(as_of=datetime.utcnow())
        regime.spy_gex_regime = "Positive (mock)"  # TODO: Fetch actual GEX
        regime.qqq_gex_regime = "Positive (mock)"
        regime.market_state = "Compressed"
        regime.iv_direction = "Declining"
        regime.major_events = ["CPI report (Thursday)", "Fed speaker (Friday)"]
        return regime

    def _phase_b_weekly_screen(self) -> List[dict]:
        """
        Phase B: Run QuantWheel screen, apply hard filters, promote core four.
        """
        raw_results = self.screener.run_screen(self.screening_config.universe)

        if self.screening_config.enforce_hard_filters:
            filtered = self.screener.apply_hard_filters(raw_results)
        else:
            filtered = raw_results

        # Promote core four to top
        ranked = self.screener.filter_core_four(filtered)
        print(f"   ✓ {len(ranked)} survivors (core four prioritized)")
        return ranked

    def _phase_c_to_g(self, symbol_data: dict, market_regime: MarketRegimeSummary) -> Optional[Candidate]:
        """
        Phases C–G: Build candidate from symbol_data through to ranking.
        """
        try:
            symbol = symbol_data["symbol"]
            spot = symbol_data["spot"]

            # Initialize candidate
            candidate = Candidate(
                symbol=symbol,
                spot=spot,
                rating=CandidateRating.WATCH,
                timestamp=datetime.utcnow()
            )

            # Phase C: Trajectory
            candidate.trajectory = self._phase_c_trajectory(symbol)

            # Phase D: Monthly confirmation
            candidate.monthly_aligned = self._phase_d_monthly(symbol)

            # Phase E: FlashAlpha confirmation
            candidate.flashalpha_confirmed = self._phase_e_flashalpha(symbol)

            # Phase F: SMC structure
            candidate.smc_1d, candidate.smc_1h = self._phase_f_smc(symbol)

            # Populate positioning from screener data
            candidate.weekly_positioning = self._build_positioning_data(symbol_data)

            # Calculate positioning metrics
            candidate.calcs = PositioningAnalyzer.calculate_positioning_metrics(
                spot,
                candidate.weekly_positioning.put_wall,
                candidate.weekly_positioning.call_wall,
                candidate.weekly_positioning.max_bull
            )

            # Classify runway
            candidate.runway = PositioningAnalyzer.classify_runway(
                candidate.weekly_positioning.call_wall,
                spot,
                candidate.weekly_positioning.max_bull,
                candidate.trajectory.put_wall_migration == "↑",
                candidate.trajectory.call_wall_migration == "↑"
            )

            # Phase G: Scoring and classification
            candidate.raw_score = RankingEngine.calculate_raw_score(candidate)
            candidate.rating = RankingEngine.classify_candidate(candidate, candidate.raw_score)

            return candidate

        except Exception as e:
            print(f"   ⚠ Error processing {symbol_data.get('symbol', '?')}: {e}")
            return None

    def _phase_c_trajectory(self, symbol: str) -> TrajectoryMetrics:
        """
        Phase C: Analyze direction and acceleration of key indicators.
        """
        traj_data = self.trajectory.analyze(symbol, {})
        return TrajectoryMetrics(
            iv_1d_change=traj_data.get("iv_1d_change"),
            iv_5d_change=traj_data.get("iv_5d_change"),
            gamma_buildup_acceleration=traj_data.get("gamma_buildup_acceleration"),
            vanna_bb_trajectory=traj_data.get("vanna_bb_trajectory"),
            put_wall_migration=traj_data.get("put_wall_migration"),
            call_wall_migration=traj_data.get("call_wall_migration"),
            max_bull_migration=traj_data.get("max_bull_migration")
        )

    def _phase_d_monthly(self, symbol: str) -> bool:
        """
        Phase D: Check monthly alignment with weekly.
        Returns True if weekly + monthly aligned.
        """
        # TODO: Fetch monthly GEX from QuantWheel
        # For now, return mock value
        return False

    def _phase_e_flashalpha(self, symbol: str) -> bool:
        """
        Phase E: Confirm with independent FlashAlpha GEX.
        """
        # TODO: Pull weekly, monthly, nearest expiry from FlashAlpha
        # Compare GEX regime, Gamma Flip, OI changes
        return False

    def _phase_f_smc(self, symbol: str) -> tuple:
        """
        Phase F: SMC structure confirmation (1D and 1H).
        """
        # TODO: Fetch price structure, demand/supply levels
        smc_1d = SmcStructure(daily_buyer_control=True)
        smc_1h = SmcStructure(
            daily_buyer_control=True,
            entry_quality="Clean"
        )
        return smc_1d, smc_1h

    def _phase_h_entry_timing(self, candidate: Candidate) -> str:
        """
        Phase H: Determine entry timing based on nearest expiry.
        """
        # TODO: Query 0DTE positioning + price action
        if candidate.rating == CandidateRating.A_PLUS_PRIME:
            return "Entry now / Wait for pullback"
        elif candidate.rating == CandidateRating.A:
            return "Wait for confirmation"
        elif candidate.rating == CandidateRating.WATCH:
            return "Monitor trajectory"
        else:
            return "No trade"

    def _phase_i_trade_plan(self, candidate: Candidate):
        """
        Phase I: Validate trade plan before entry.
        Set invalidation level, targets, and conditions.
        """
        # TODO: Finalize entry condition, stop level, targets
        if candidate.invalidation_level is None and candidate.weekly_positioning.put_wall:
            # Place stop just below Put Wall
            candidate.invalidation_level = candidate.weekly_positioning.put_wall * 0.98

        if candidate.first_target is None and candidate.weekly_positioning.call_wall:
            candidate.first_target = candidate.weekly_positioning.call_wall

        if candidate.second_target is None and candidate.weekly_positioning.max_bull:
            candidate.second_target = candidate.weekly_positioning.max_bull

    def _build_positioning_data(self, symbol_data: dict) -> PositioningData:
        """Convert screener output to PositioningData."""
        put_wall_dir = "↑" if symbol_data.get("put_wall_move_today") == "up" else "↓"

        return PositioningData(
            spot=symbol_data.get("spot", 0.0),
            gamma=symbol_data.get("gamma", "Unknown"),
            vanna=symbol_data.get("vanna", "Unknown"),
            vanna_bull_bear_ratio=symbol_data.get("vanna_bull_bear_ratio"),
            put_wall=symbol_data.get("put_wall"),
            put_wall_direction=put_wall_dir,
            call_wall=symbol_data.get("call_wall"),
            call_wall_direction="→",  # TODO: Compute from trajectory
            max_bull=symbol_data.get("max_bull"),
            rv_iv_ratio=symbol_data.get("rv_iv_ratio"),
            daily_move=symbol_data.get("daily_move_pct"),
            gamma_buildup_5d="rising" if symbol_data.get("gamma_buildup_5d") == "rising" else "stable",
            timestamp=datetime.utcnow().isoformat()
        )

    def format_report(self, report: TopQuantReport) -> str:
        """Format report for display."""
        return self.reporter.generate_report(report)
