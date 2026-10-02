"""Top Quant reporter — Report generation and formatting."""

from datetime import datetime
from typing import List
from .models import TopQuantReport, Candidate, CandidateRating, MarketRegimeSummary


class TopQuantReporter:
    """Formats Top Quant output per Section 20 spec."""

    def __init__(self):
        self.report: TopQuantReport = None

    def generate_report(self, report: TopQuantReport) -> str:
        """Generate formatted Top Quant report."""
        self.report = report
        sections = [
            self._section_header(),
            self._section_market_regime(),
            self._section_a_plus_prime(),
            self._section_a_candidates(),
            self._section_watch_candidates(),
            self._section_breakout_candidates(),
            self._section_pass_candidates(),
            self._section_finalist_details(),
            self._section_ranked_board(),
        ]
        return "\n".join(sections)

    def _section_header(self) -> str:
        """Report header."""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                    TOP QUANT DAILY REPORT                         ║
║            Dealer Positioning × Structure × Volatility             ║
╚════════════════════════════════════════════════════════════════════╝

As of: {self.report.as_of.strftime('%Y-%m-%d %H:%M UTC')}
Universe: SPX 500 + NDX 100
Data Source: QuantWheel (primary) + FlashAlpha (confirmation)
"""

    def _section_market_regime(self) -> str:
        """Market regime summary."""
        regime = self.report.market_regime
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. MARKET REGIME SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SPY Dealer Regime: {regime.spy_gex_regime or 'Unknown'}
  QQQ Dealer Regime: {regime.qqq_gex_regime or 'Unknown'}
  Market State: {regime.market_state or 'Neutral'}
  IV Direction: {regime.iv_direction or 'Neutral'}

  Major Events: {', '.join(regime.major_events) if regime.major_events else 'None scheduled'}

  📌 Thesis: {"Bullish backdrop for drift/support setups." if regime.spy_gex_regime == "Positive" else "Monitor for regime changes."}
"""

    def _section_a_plus_prime(self) -> str:
        """A+ PRIME candidates."""
        candidates = self.report.get_by_rating(CandidateRating.A_PLUS_PRIME)
        if not candidates:
            return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. 🔥 A+ PRIME CANDIDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No A+ PRIME setups today.
"""
        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "2. 🔥 A+ PRIME CANDIDATES",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for c in candidates:
            lines.append(self._format_candidate_summary(c))
        return "\n".join(lines)

    def _section_a_candidates(self) -> str:
        """A candidates."""
        candidates = self.report.get_by_rating(CandidateRating.A)
        if not candidates:
            return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. 🟢 A CANDIDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No A candidates today.
"""
        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "3. 🟢 A CANDIDATES",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for c in candidates:
            lines.append(self._format_candidate_summary(c))
        return "\n".join(lines)

    def _section_watch_candidates(self) -> str:
        """WATCH candidates."""
        candidates = self.report.get_by_rating(CandidateRating.WATCH)
        if not candidates:
            return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. 🟡 WATCH CANDIDATES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No WATCH candidates today.
"""
        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "4. 🟡 WATCH CANDIDATES",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for c in candidates:
            lines.append(self._format_candidate_summary(c))
        return "\n".join(lines)

    def _section_breakout_candidates(self) -> str:
        """BREAKOUT candidates."""
        candidates = self.report.get_by_rating(CandidateRating.BREAKOUT)
        if not candidates:
            return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. ⚡ BREAKOUT CANDIDATES (Mode 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  No BREAKOUT setups today.
"""
        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "5. ⚡ BREAKOUT CANDIDATES (Mode 2)",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for c in candidates:
            lines.append(self._format_candidate_summary(c))
        return "\n".join(lines)

    def _section_pass_candidates(self) -> str:
        """PASS / Notable failures."""
        candidates = self.report.get_by_rating(CandidateRating.PASS)
        if not candidates:
            return ""
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. ❌ PASS / NOTABLE FAILURES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  {len(candidates)} names excluded from finalist board.
"""

    def _section_finalist_details(self) -> str:
        """Detailed finalist breakdown."""
        finalists = [c for c in self.report.candidates.values()
                    if c.rating != CandidateRating.PASS]
        if not finalists:
            return ""

        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "7. FINALIST DETAILS",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]
        for c in finalists:
            lines.append(self._format_full_candidate(c))
        return "\n".join(lines)

    def _section_ranked_board(self) -> str:
        """Ranked board."""
        ranked = self.report.ranked_board()
        finalists = [c for c in ranked if c.rating != CandidateRating.PASS]
        if not finalists:
            return ""

        lines = [
            "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "8. FINAL RANKED BOARD",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "Rank  Symbol    Score   Rating          Monthly  FlashAlpha  Runway     R/R",
            "─────────────────────────────────────────────────────────────────────────",
        ]
        for rank, c in enumerate(finalists, 1):
            monthly = "✓" if c.monthly_aligned else "✗"
            flash = "✓" if c.flashalpha_confirmed else "✗"
            rr_str = f"{c.calcs.positioning_rr:.2f}" if c.calcs.positioning_rr else "—"
            lines.append(
                f"{rank:<5} {c.symbol:<8} {c.raw_score:>6.1f}  {c.rating.value:<15} "
                f"{monthly:<7} {flash:<10} {c.runway.value:<10} {rr_str:>6}"
            )
        return "\n".join(lines)

    def _format_candidate_summary(self, c: Candidate) -> str:
        """Brief candidate summary."""
        return f"""
  {c.rating.value} | {c.symbol} @ {c.spot:.2f}
    Score: {c.raw_score:.1f}/100 | Monthly: {'✓' if c.monthly_aligned else '✗'} | FlashAlpha: {'✓' if c.flashalpha_confirmed else '✗'}
"""

    def _format_full_candidate(self, c: Candidate) -> str:
        """Full candidate detail card."""
        positioning = c.weekly_positioning
        return f"""
  ┌─ {c.symbol} {c.rating.value} ─────────────────────────────────────────────┐
  │
  │  Price: ${c.spot:.2f}  |  Score: {c.raw_score:.1f}/100  |  Runway: {c.runway.value}
  │
  │  WEEKLY (Primary):
  │    Gamma: {positioning.gamma} | Vanna: {positioning.vanna} ({positioning.vanna_bull_bear_ratio:.1f}x)
  │    Put Wall: ${positioning.put_wall:.2f} {positioning.put_wall_direction or '→'}
  │    Call Wall: ${positioning.call_wall:.2f} {positioning.call_wall_direction or '→'}
  │    Max Bull: ${positioning.max_bull:.2f}
  │    Gamma Flip: ${positioning.gamma_flip:.2f} | Vanna Flip: ${positioning.vanna_flip:.2f}
  │    RV/IV: {positioning.rv_iv_ratio:.2f} | Daily Move: {positioning.daily_move:.1f}%
  │
  │  TRAJECTORY:
  │    IV 1D: {c.trajectory.iv_1d_change or '?'}% | IV 5D: {c.trajectory.iv_5d_change or '?'}%
  │    Gamma Buildup: {c.trajectory.gamma_buildup_acceleration or '?'}
  │    Vanna B/B: {c.trajectory.vanna_bb_trajectory or '?'}
  │    Put Wall: {c.trajectory.put_wall_migration or '?'} | Call Wall: {c.trajectory.call_wall_migration or '?'}
  │
  │  POSITIONING MATH:
  │    Upside to Call Wall: {c.calcs.upside_to_call_wall:.1f}% | Upside to Max Bull: {c.calcs.upside_to_max_bull:.1f}%
  │    Downside to Put Wall: {c.calcs.downside_to_put_wall:.1f}% | R/R: {c.calcs.positioning_rr:.2f}
  │
  │  CONFIRMATION:
  │    Monthly Aligned: {'✓' if c.monthly_aligned else '✗'} | FlashAlpha: {'✓' if c.flashalpha_confirmed else '✗'}
  │    1D Buyer Control: {'✓' if c.smc_1d.daily_buyer_control else '✗'} | 1H Entry Quality: {c.smc_1h.entry_quality or '?'}
  │
  │  ENTRY:
  │    Condition: {c.entry_condition or 'Awaiting setup'}
  │    Invalidation Level: ${c.invalidation_level:.2f} | Target 1: ${c.first_target:.2f} | Target 2: ${c.second_target:.2f}
  │
  │  EVENT RISK: {c.event_risk or 'None identified'}
  │
  └──────────────────────────────────────────────────────────────────┘
"""
