# TOP QUANT - Quantitative Trading Framework

**TOP QUANT** is a comprehensive quantitative trading analysis framework that combines **Smart Money Concepts**, **options flow analysis**, and **gamma exposure** monitoring to identify high-conviction trade setups.

## What It Does

TOP QUANT integrates three core quantitative pillars:

1. **Options Flow Analysis** (via QuantWheel)
   - Unusual options activity detection
   - Put/call ratio analysis
   - IV percentile tracking
   - Dealer positioning

2. **Gamma Exposure (GEX)** (via QuantWheel)
   - Real-time gamma level monitoring
   - Gamma flip detection
   - Max pain analysis
   - Key strike identification

3. **Smart Money Positioning** (via QuantWheel + Market Data)
   - Insider buying/selling activity
   - Hedge fund flows
   - Institutional positioning
   - Dark pool tracking

4. **Technical Structure** (via Smart Money Concepts)
   - Order block identification
   - Liquidity level mapping
   - Fair value gap detection
   - Break of structure confirmation
   - Swing level analysis

5. **Journal Performance** (via QuantWheel Trading Journal)
   - Win rate tracking
   - Profit factor analysis
   - Max drawdown monitoring
   - Risk/reward ratio measurement

## Quick Start

### Run TOP QUANT for a single ticker:
```bash
python3 top_quant_core.py SPY
```

### Run TOP QUANT for multiple tickers:
```bash
python3 top_quant_core.py SPY AAPL NVDA QQQ
```

### Run TOP QUANT with specific timeframe:
```bash
python3 top_quant_core.py SPY --timeframe 4h
```

## Analysis Output

Each run generates:

- **Quant Metrics**: Options flow, gamma exposure, smart money positioning, technical structure
- **Signals**: Strong/Moderate/Weak signals with actionable details
- **Recommendations**: Entry rules, exit rules, position sizing, risk/reward targets
- **Journal Performance**: Historical trading metrics for validation

## Trade Setup Rules

### Entry Conditions (Confluence Required)
1. Options flow signal from QuantWheel
2. GEX level alignment (no gamma flip risk)
3. Smart money positioning confirmation
4. Technical structure alignment (order block + liquidity)

### Exit Conditions
1. Stop loss at technical level break
2. Take profits at major resistance/support
3. Risk/reward target achieved (2:1 minimum)

### Position Sizing
- **Risk per trade**: 1-5% of account
- **Risk/reward minimum**: 2:1
- **Max drawdown**: Monitor against journal metrics

## Integration Points

### QuantWheel Connection
- Live options flow data
- GEX heatmaps and gamma levels
- Smart money positioning
- Trading journal performance

### TradingView Connection
- Real-time price data
- Technical indicators
- Multi-timeframe analysis
- Screener integration

### Smart Money Concepts
- Order block detection
- Liquidity level identification
- Fair value gap mapping
- Break of structure signals

## Key Metrics Tracked

| Metric | Source | Purpose |
|--------|--------|---------|
| Options Flow | QuantWheel | Detect unusual activity |
| GEX Level | QuantWheel | Identify gamma reversals |
| IV Percentile | QuantWheel | Volatility extremes |
| Dealer Position | QuantWheel | Smart money alignment |
| Order Blocks | SMC | Support/resistance zones |
| Liquidity Levels | SMC | Sweep probability |
| Win Rate | QuantWheel Journal | Strategy validation |
| Profit Factor | QuantWheel Journal | Risk/reward effectiveness |

## Command Examples

### Scan S&P 500 components
```bash
python3 top_quant_core.py SPY QQQ IWM
```

### Watch multiple sectors
```bash
python3 top_quant_core.py XLK XLV XLF XLE
```

### Run daily analysis
```bash
# Add to cron for daily execution
python3 top_quant_core.py $(cat ~/top_quant_watchlist.txt)
```

## Backtesting

### Run Single Ticker Backtest
```bash
python3 top_quant_backtest.py SPY 252
```

### Run Batch Backtest (Multiple Tickers)
```bash
python3 top_quant_batch_backtest.py
# Tests: SPY, AAPL, NVDA, MSFT, TSLA, QQQ, GLD, IWM
```

### Backtest Output Includes
- Total return and final capital
- Win rate and trade count
- Profit factor and max drawdown
- Average win/loss per trade
- Average bars held
- Individual trade details (entry/exit/P&L)

### Recent Batch Results (252-day backtest)
- **Best Performer**: NVDA (+0.42%)
- **Profitable Tickers**: 50% (4 of 8)
- **Average Win Rate**: 31.39%
- **Average Profit Factor**: 0.95

## Status

✓ Framework initialized  
✓ Analysis engine operational  
✓ Backtesting engine complete with batch validation
✓ Multi-ticker strategy validation
⏳ Awaiting QuantWheel live data connection  
⏳ Awaiting TradingView integration  
⏳ Awaiting Smart Money Concepts data feed  

## Next Steps

1. ✓ Build core framework
2. ✓ Implement backtesting engine
3. ✓ Validate strategy across tickers
4. Connect QuantWheel API for live options flow
5. Integrate TradingView data for price/volume
6. Import Smart Money Concepts indicators
7. Paper trade for validation
8. Track journal performance with real capital

---

**Created with Claude Code**  
Framework Version: 0.1.0  
Status: Beta
