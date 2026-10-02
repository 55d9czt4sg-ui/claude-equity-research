# Top Quant Framework

**A bullish swing-trading analysis system** focused on identifying high-probability setups where dealer hedging mechanics, volatility, positioning trajectory, and price structure converge.

**Status:** Beta v0.1.0  
**Universe:** S&P 500 + Nasdaq-100  
**Primary Data Source:** QuantWheel (gamma, vanna, walls) + FlashAlpha (independent GEX confirmation)  
**Secondary Confirmation:** TradingView (SMC structure) + Pineify, Robinhood (flow/positioning)

---

## Quick Start

### CLI Usage

```bash
# Run Top Quant with mock data (development)
python3 -m top_quant.cli --run --mock

# Run with mock data, save to file
python3 -m top_quant.cli --run --mock --output report.txt

# Run with QuantWheel API
python3 -m top_quant.cli --run --quantwheel-key YOUR_KEY_HERE

# Run executable
python3 run_top_quant.py --run --mock
```

### Python API

```python
from top_quant import TopQuantRunner

# Default (mock data)
runner = TopQuantRunner()
report = runner.run()

# Print formatted report
print(runner.format_report(report))

# Access candidates programmatically
for candidate in report.ranked_board():
    print(f"{candidate.symbol}: {candidate.rating.value} | Score: {candidate.raw_score:.1f}/100")

# Filter by rating
a_plus = report.get_by_rating(__import__("top_quant.models", fromlist=["CandidateRating"]).CandidateRating.A_PLUS_PRIME)
print(f"A+ PRIME candidates: {len(a_plus)}")
```

---

## Architecture

### Module Structure

```
top_quant/
├── __init__.py           # Package exports
├── models.py             # Data classes (Candidate, Positioning, etc.)
├── config.py             # Constants, filtering rules, weights
├── screener.py           # QuantWheel integration (Phase B, C)
├── analyzer.py           # Positioning, trajectory, SMC, ranking (Phases D–G)
├── reporter.py           # Report formatting and output
├── runner.py             # Main orchestration (Phases A–I)
└── cli.py                # Command-line interface
```

### 9-Phase Workflow

**Phase A: Market Context**  
- Check major scheduled events (earnings, economic releases)
- Review SPY/QQQ broad dealer regime (GEX)
- Establish baseline market state (compressed, trending, acceleration)

**Phase B: Weekly QuantWheel Screen**  
- Run SPX 500 + NDX 100 screen with hard filters (see config.py)
- Promote candidates with core four regime to top of board
- Apply RV/IV bounds, daily move filters, wall proximity

**Phase C: Trajectory Analysis**  
- Measure IV 1D/5D direction and rate of change
- Analyze gamma buildup acceleration (not just static reading)
- Track Vanna B/B evolution, Put/Call/Max Bull migration
- Identify rising vs deteriorating structures

**Phase D: Monthly Confirmation**  
- Rerun finalists using Monthly anchor
- Flag 🔥 **WEEKLY + MONTHLY ALIGNED** when both agree
- Use monthly for structural conviction, not replacement

**Phase E: FlashAlpha Confirmation**  
- Pull independent GEX data (weekly, monthly, nearest expiry)
- Compare Gamma Flip locations, GEX concentration, OI changes
- Assess whether dealer positioning trends match QuantWheel

**Phase F: SMC (Smart Money Concepts) Structure**  
- **1D permission:** Verify buyers in control (HH/HL, bullish BOS/CHOCH, holding demand)
- **1H entry:** Look for clean sweep/reclaim, displacement, no entry into supply
- Reject entries directly into major overhead resistance

**Phase G: Ranking & Classification**  
- Score 6 components (30% gamma, 25% vanna, 15% put wall, 15% R/R, 10% IV, 5% price)
- Calculate raw score (0–100)
- Apply structural overlays: monthly alignment, SMC quality, runway, event risk
- Classify: 🔥 A+ PRIME | 🟢 A | 🟡 WATCH | ⚡ BREAKOUT | ❌ PASS

**Phase H: Entry Timing**  
- Use nearest expiry (0DTE) data only on finalists
- Decide: entry now, wait for pullback, wait for breakout confirmation, no trade

**Phase I: Trade Plan Validation**  
- Set invalidation level (structural break points)
- Define profit targets (Call Wall, Max Bull, key SMC levels)
- Record entry trigger, position size, exit conditions

---

## Data Model

### Core Objects

**`Candidate`**  
- Symbol, rating, spot price, timestamp
- Weekly/monthly/nearest expiry positioning data
- Trajectory metrics, SMC structure (1D + 1H)
- Positioning calculations (upside, downside, R/R)
- Entry condition, invalidation level, targets

**`PositioningData`**  
- Spot, gamma regime, vanna regime
- Put/Call walls, Max Bull, Gamma/Vanna flips
- RV/IV ratio, daily move %, buildup status
- Optional: expiry, timestamp (for multi-expiry)

**`TrajectoryMetrics`**  
- IV 1D/5D change (%)
- Gamma buildup acceleration direction
- Vanna B/B trajectory (string, e.g., "2.1 → 2.8 → 3.6")
- Wall migration direction (put, call, max bull)

**`SmcStructure`**  
- Daily: buyer control (bool), demand/supply levels
- Hourly: BOS/CHOCH (bullish/bearish/neutral), order block, sweep/reclaim status
- Entry quality: "Clean" | "Mixed" | "Blocked"

**`TopQuantReport`**  
- Market regime summary (date, GEX state, events, IV direction)
- Candidates dict {symbol → Candidate}
- Methods: `get_by_rating()`, `ranked_board()`

---

## Configuration & Constants

### Hard Filters (config.py)

```python
WEEKLY_FILTERS = {
    "anchor": "weekly",
    "gamma": "positive",
    "vanna": "positive",
    "put_wall_distance": (0, 3),  # %
    "gamma_buildup_5d": "rising",
    "vanna_bull_bear_ratio_min": 2.0,
    "rv_iv": (1.00, 1.50),  # Research range: 0.80–1.75
    "daily_move": (-1.0, 2.0),  # %
    "iv_confirmation": "declining",
}
```

### Ranking Weights

- **30%** Gamma buildup (magnitude + acceleration)
- **25%** Vanna B/B strength and trajectory
- **15%** Put Wall behavior/proximity
- **15%** Positioning R/R
- **10%** IV contraction
- **5%** Price/volume confirmation

---

## Integration Points

### Required (Primary)

**QuantWheel**  
- Endpoint: GET `https://quantwheel.com/api/v1/screener` (POST with filters)
- Returns: gamma, vanna, walls, GEX, builder state
- Fallback: mock data (included for dev)

**FlashAlpha** (Independent Confirmation)  
- Endpoint: GET `/v1/exposure/gex/{symbol}?expiration=YYYY-MM-DD`
- Returns: Net GEX, Gamma Flip, OI/volume by strike, VEX/DEX
- Status: Basic plan queries one expiration at a time

### Optional (Confirmation Layers)

**TradingView** (SMC structure)  
- Via MCP: `analyze_smc_tool`, `get_technicals`, `get_ohlcv`
- Returns: demand/supply levels, BOS/CHOCH, higher highs/lows

**Pineify** (Flow confirmation)  
- Tools: `find_technical_setups`, `get-market-tide`, `get-stock-research-snapshot`
- Confirms: technical regime, sector flow, institutional activity

**Robinhood** (Positioning depth)  
- Tools: `get_option_quotes`, `get_option_chains`, `get_option_positions`
- Confirms: unusual flow, max pain, dealer hedging

---

## Usage Examples

### Example 1: Run Daily Screening

```bash
python3 run_top_quant.py --run --mock
```

Output: Report with market regime, candidate ratings, ranked board.

### Example 2: Custom Configuration

```python
from top_quant import TopQuantRunner
from top_quant.config import ScreeningConfig

config = ScreeningConfig(
    enforce_hard_filters=True,
    use_research_range=False  # Stick to 1.00–1.50
)

runner = TopQuantRunner(screening_config=config)
report = runner.run()

# Access A+ candidates
a_plus = [c for c in report.candidates.values() 
          if c.rating.value == "🔥 A+ PRIME"]
print(f"Found {len(a_plus)} A+ setups")
```

### Example 3: Export to CSV

```python
import csv

report = runner.run()
ranked = report.ranked_board()

with open("top_quant_board.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["Symbol", "Rating", "Score", "Spot", "R/R", "Runway", "Monthly Aligned"])
    for c in ranked:
        writer.writerow([
            c.symbol,
            c.rating.value,
            f"{c.raw_score:.1f}",
            f"{c.spot:.2f}",
            f"{c.calcs.positioning_rr:.2f}" if c.calcs.positioning_rr else "—",
            c.runway.value,
            "✓" if c.monthly_aligned else "✗"
        ])
```

---

## Key Principles

1. **Dealer Positioning First.** The system is built around gamma/vanna mechanics, not price action alone.
2. **Trajectory Over Snapshots.** Acceleration and direction matter more than raw readings.
3. **Confluence Required.** No single data source wins—dealer regime + trajectory + SMC + event risk.
4. **No Certainty.** The thesis is probabilistic. Positions can deteriorate; adapt or exit.
5. **Hard Filters Enforce Discipline.** Screen first, then rank. Don't chase already-extended names.
6. **Runway Classification Decides Rank.** A strong candidate with blocked runway ranks below a slightly weaker candidate with open runway.

---

## Development Roadmap

- [ ] Live QuantWheel API integration
- [ ] FlashAlpha API integration
- [ ] TradingView MCP connector for SMC analysis
- [ ] Pineify flow confirmation layer
- [ ] Robinhood positioning sync
- [ ] Historical backtest suite
- [ ] Real-time 1H entry alerts
- [ ] Database logging of results for performance tracking
- [ ] Web dashboard for live monitoring

---

## Troubleshooting

**No candidates in report?**  
- Check market regime (Positive Gamma + Positive Vanna + IV declining?)
- Verify hard filters aren't too restrictive (try `use_research_range=True`)
- Confirm QuantWheel data is available (not in market halts/early mornings)

**Mock data not realistic?**  
- Mock screener returns AAPL, MSFT, NVDA, TSLA with synthetic positioning
- For real data, supply QuantWheel API key via `--quantwheel-key` or `DataSourceConfig`

**Report shows PASS candidates only?**  
- Core four regime not present in the universe today (gamma/vanna mismatch, IV rising, buildup falling)
- This is normal—Top Quant is selective, not a "everything" screener

---

## References

- **Main Framework:** `Section 18–20` (daily procedure + output format)
- **Positioning Math:** `Section 8` (R/R calculations)
- **Ranking Model:** `Section 9` (weights and overlays)
- **SMC Confirmation:** `Section 11` (1D/1H logic)
- **Wall Pressure:** `Section 13` (WEAKENING/HOLDING/STRENGTHENING)
- **Two Regimes:** `Section 14` (drift/support vs. breakout/acceleration)

---

**Last updated:** 2026-10-02  
**Version:** 0.1.0 (Beta)  
**Author:** Top Quant Framework
