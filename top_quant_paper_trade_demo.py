#!/usr/bin/env python3
"""
TOP QUANT PAPER TRADING DEMO - Quick simulation
Shows paper trading in action with accelerated market updates
"""

import json
from datetime import datetime
from top_quant_paper_trade import PaperTradingEngine, LiveSignalGenerator, print_trading_dashboard, print_session_report, save_session_data
import time

def run_demo_session():
    """Run quick demo paper trading session"""

    watchlist = ["SPY", "AAPL", "NVDA", "MSFT", "QQQ"]
    engine = PaperTradingEngine(account_size=100000, risk_per_trade=1.0)
    generator = LiveSignalGenerator(watchlist)

    print("\n" + "="*100)
    print("  TOP QUANT PAPER TRADING - QUICK DEMO")
    print("="*100)
    print(f"\nRunning 50-iteration demo (accelerated market simulation)...")
    print(f"Watchlist: {', '.join(watchlist)}\n")

    session_trades = []

    for iteration in range(50):
        # Generate market data
        generator.generate_market_data()

        # Check for signals and place orders
        for ticker in watchlist:
            signal = generator.get_signal(ticker)

            if signal and signal['strength'] in ["STRONG", "MODERATE"]:
                has_position = any(o.ticker == ticker for o in engine.open_orders.values())

                if not has_position and len(engine.open_orders) < 5:
                    order = engine.create_order(
                        ticker=ticker,
                        side=signal['type'],
                        entry_price=signal['price'],
                        signal_strength=signal['strength']
                    )
                    engine.submit_order(order)
                    session_trades.append({
                        "action": "ENTRY",
                        "order": order,
                        "signal": signal
                    })
                    print(f"  ✓ {order.order_id}: {ticker} {signal['type']} @ ${signal['price']:.2f} ({signal['strength']})")

        # Update all open orders
        for order_id in list(engine.open_orders.keys()):
            current_price = generator.prices.get(engine.open_orders[order_id].ticker, 0)
            engine.update_order(order_id, current_price)

        # Print updates every 10 iterations
        if (iteration + 1) % 10 == 0:
            print(f"\n  Iteration {iteration + 1}/50 | Open Trades: {len(engine.open_orders)} | Closed Trades: {len(engine.closed_orders)}")

    # Close remaining orders
    for order_id in list(engine.open_orders.keys()):
        current_price = generator.prices.get(engine.open_orders[order_id].ticker)
        if current_price:
            engine.close_order(order_id, current_price, "DEMO_END")

    # Print final report
    print_session_report(engine, session_trades)
    save_session_data(engine, generator, session_trades)

    return engine

def main():
    """Run demo"""
    engine = run_demo_session()
    print("\nDemo complete! Open top_quant_paper_trade_session.json to view detailed results.\n")

if __name__ == "__main__":
    main()
