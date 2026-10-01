#!/usr/bin/env python3
"""
TOP QUANT BATCH BACKTEST - Run backtests across multiple tickers
Generates comparison report and strategy validation
"""

import json
from datetime import datetime
from top_quant_backtest import BacktestEngine

def run_batch_backtest(tickers: list, days: int = 252) -> dict:
    """Run backtest across multiple tickers"""

    print("\n" + "="*90)
    print("  ╔════════════════════════════════════════════════════════════════════════════════╗")
    print("  ║     TOP QUANT BATCH BACKTEST - MULTI-TICKER STRATEGY VALIDATION                ║")
    print("  ║                                                                                ║")
    print("  ║  Testing signal confluence across different instruments and sectors           ║")
    print("  ╚════════════════════════════════════════════════════════════════════════════════╝")
    print("="*90)

    results = {}
    summary_stats = {
        "total_tickers": len(tickers),
        "avg_return": 0,
        "avg_win_rate": 0,
        "avg_profit_factor": 0,
        "tickers_profitable": 0,
        "best_performer": None,
        "worst_performer": None,
        "best_return": float('-inf'),
        "worst_return": float('inf')
    }

    print(f"\nBacktesting {len(tickers)} tickers across {days} days...\n")

    for ticker in tickers:
        print(f"  ⏳ {ticker}...", end=" ", flush=True)

        engine = BacktestEngine(ticker, starting_capital=100000)
        report = engine.backtest(days=days)

        if "error" not in report:
            results[ticker] = report

            # Extract metrics
            total_return = float(report['total_return'].rstrip('%'))
            win_rate = float(report['win_rate'].rstrip('%'))
            profit_factor = float(report['profit_factor']) if report['profit_factor'] != "N/A" else 1.0

            summary_stats["avg_return"] += total_return
            summary_stats["avg_win_rate"] += win_rate
            summary_stats["avg_profit_factor"] += profit_factor

            if total_return > 0:
                summary_stats["tickers_profitable"] += 1

            if total_return > summary_stats["best_return"]:
                summary_stats["best_return"] = total_return
                summary_stats["best_performer"] = ticker

            if total_return < summary_stats["worst_return"]:
                summary_stats["worst_return"] = total_return
                summary_stats["worst_performer"] = ticker

            status = "✓" if total_return > 0 else "✗"
            print(f"{status} {total_return:+.2f}% | Win Rate: {win_rate:.1f}%")
        else:
            print("❌ No trades")

    # Calculate averages
    if results:
        summary_stats["avg_return"] /= len(results)
        summary_stats["avg_win_rate"] /= len(results)
        summary_stats["avg_profit_factor"] /= len(results)

    return results, summary_stats

def print_batch_report(results: dict, summary: dict, tickers: list):
    """Print formatted batch backtest report"""

    print(f"\n{'='*90}")
    print("BACKTEST RESULTS - PERFORMANCE COMPARISON")
    print(f"{'='*90}\n")

    # Summary statistics
    print("📊 SUMMARY STATISTICS")
    print(f"{'-'*90}")
    print(f"Tickers Tested:           {summary['total_tickers']}")
    print(f"Profitable Tickers:       {summary['tickers_profitable']} ({(summary['tickers_profitable']/summary['total_tickers']*100):.0f}%)")
    print(f"Average Return:           {summary['avg_return']:+.2f}%")
    print(f"Average Win Rate:         {summary['avg_win_rate']:.2f}%")
    print(f"Average Profit Factor:    {summary['avg_profit_factor']:.2f}")
    print(f"Best Performer:           {summary['best_performer']} ({summary['best_return']:+.2f}%)")
    print(f"Worst Performer:          {summary['worst_performer']} ({summary['worst_return']:+.2f}%)")

    # Individual ticker results
    print(f"\n📈 INDIVIDUAL TICKER RESULTS")
    print(f"{'-'*90}")
    print(f"{'Ticker':<10} {'Return':<15} {'Win Rate':<15} {'Profit Factor':<15} {'Status':<10}")
    print(f"{'-'*90}")

    for ticker in tickers:
        if ticker in results:
            report = results[ticker]
            total_return = float(report['total_return'].rstrip('%'))
            win_rate = report['win_rate']
            profit_factor = report['profit_factor']
            status = "✓ PROFIT" if total_return > 0 else "✗ LOSS"

            print(f"{ticker:<10} {total_return:>6.2f}%        {win_rate:>10}     {profit_factor:>12}     {status:<10}")

    # Detailed reports
    print(f"\n{'='*90}")
    print("DETAILED TICKER REPORTS")
    print(f"{'='*90}")

    for ticker in tickers:
        if ticker in results:
            report = results[ticker]
            print(f"\n{'─'*90}")
            print(f"TICKER: {ticker}")
            print(f"{'─'*90}")
            print(f"Starting Capital: {report['starting_capital']}")
            print(f"Ending Capital:   {report['ending_capital']}")
            print(f"Total Return:     {report['total_return']}")
            print(f"\nTrades:      {report['total_trades']} (W:{report['winning_trades']} L:{report['losing_trades']})")
            print(f"Win Rate:    {report['win_rate']}")
            print(f"Profit Factor: {report['profit_factor']}")
            print(f"Max Drawdown: {report['max_drawdown']}")
            print(f"Avg Win:     {report['avg_win']}")
            print(f"Avg Loss:    {report['avg_loss']}")

    # Strategy validation
    print(f"\n{'='*90}")
    print("STRATEGY VALIDATION")
    print(f"{'='*90}\n")

    if summary['avg_profit_factor'] > 1.5:
        print("✓ Excellent: Profit factor > 1.5 indicates strong edge")
    elif summary['avg_profit_factor'] > 1.0:
        print("✓ Good: Profit factor > 1.0 indicates positive expectancy")
    else:
        print("⚠ Caution: Profit factor < 1.0 suggests strategy needs refinement")

    if summary['avg_win_rate'] > 50:
        print("✓ Good: Win rate > 50% with 2:1 risk/reward validates signal quality")
    else:
        print("⚠ Note: Win rate < 50% acceptable with 2:1 risk/reward (breakeven at 33%)")

    if summary['tickers_profitable'] >= summary['total_tickers'] * 0.5:
        print(f"✓ Solid: {summary['tickers_profitable']}/{summary['total_tickers']} tickers profitable")
    else:
        print(f"⚠ Review: Only {summary['tickers_profitable']}/{summary['total_tickers']} tickers profitable")

    print(f"\n{'='*90}")
    print("✓ Batch backtest complete - Ready for paper trading or optimization")
    print(f"{'='*90}\n")

def main():
    """Run batch backtest"""
    # Test across different sectors
    tickers = ["SPY", "AAPL", "NVDA", "MSFT", "TSLA", "QQQ", "GLD", "IWM"]

    results, summary = run_batch_backtest(tickers, days=252)
    print_batch_report(results, summary, tickers)

    # Save results to JSON
    output = {
        "timestamp": datetime.now().isoformat(),
        "backtest_type": "batch",
        "tickers": tickers,
        "summary": summary,
        "results": results
    }

    with open("top_quant_backtest_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print("\n✓ Results saved to top_quant_backtest_results.json\n")

if __name__ == "__main__":
    main()
