#!/usr/bin/env python3
"""
TOP QUANT PAPER TRADING - Live Simulated Trading System
Real-time signal generation and trade execution without real capital
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

@dataclass
class Order:
    """Paper trade order"""
    order_id: str
    ticker: str
    side: str  # LONG/SHORT
    entry_price: float
    entry_time: str
    quantity: float
    stop_loss: float
    profit_target: float
    status: OrderStatus
    signal_strength: str

    current_price: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0
    bars_held: int = 0

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "ticker": self.ticker,
            "side": self.side,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "quantity": self.quantity,
            "current_price": self.current_price,
            "stop_loss": self.stop_loss,
            "profit_target": self.profit_target,
            "pnl": f"${self.pnl:.2f}",
            "pnl_percent": f"{self.pnl_percent:.2f}%",
            "bars_held": self.bars_held,
            "status": self.status.value,
            "signal_strength": self.signal_strength
        }

class PaperTradingEngine:
    """Live paper trading engine"""

    def __init__(self, account_size: float = 100000, risk_per_trade: float = 1.0):
        self.account_size = account_size
        self.starting_capital = account_size
        self.current_capital = account_size
        self.risk_per_trade = risk_per_trade

        self.open_orders: Dict[str, Order] = {}
        self.closed_orders: List[Order] = []
        self.order_counter = 0

        self.running = False
        self.session_start = datetime.now()
        self.last_price_update = {}

    def generate_order_id(self) -> str:
        """Generate unique order ID"""
        self.order_counter += 1
        return f"ORDER-{self.order_counter:05d}"

    def create_order(self, ticker: str, side: str, entry_price: float,
                    signal_strength: str, quantity: float = 1.0) -> Order:
        """Create a paper trade order"""

        # Risk management
        stop_loss_pct = 0.02
        profit_target_pct = 0.04

        if side == "LONG":
            stop_loss = entry_price * (1 - stop_loss_pct)
            profit_target = entry_price * (1 + profit_target_pct)
        else:
            stop_loss = entry_price * (1 + stop_loss_pct)
            profit_target = entry_price * (1 - profit_target_pct)

        order = Order(
            order_id=self.generate_order_id(),
            ticker=ticker,
            side=side,
            entry_price=entry_price,
            entry_time=datetime.now().isoformat(),
            quantity=quantity,
            stop_loss=stop_loss,
            profit_target=profit_target,
            status=OrderStatus.PENDING,
            signal_strength=signal_strength
        )

        return order

    def submit_order(self, order: Order) -> bool:
        """Submit order to paper trading"""
        self.open_orders[order.order_id] = order
        order.status = OrderStatus.FILLED
        return True

    def update_order(self, order_id: str, current_price: float) -> Optional[Order]:
        """Update order with current price and check for exit"""

        if order_id not in self.open_orders:
            return None

        order = self.open_orders[order_id]
        order.current_price = current_price
        order.bars_held += 1

        # Calculate P&L
        if order.side == "LONG":
            pnl_percent = ((current_price - order.entry_price) / order.entry_price) * 100
        else:
            pnl_percent = ((order.entry_price - current_price) / order.entry_price) * 100

        order.pnl_percent = pnl_percent
        order.pnl = (self.current_capital * self.risk_per_trade / 100) * (pnl_percent / 100)

        # Check exit conditions
        should_close = False
        exit_reason = ""

        if order.side == "LONG":
            if current_price >= order.profit_target:
                should_close = True
                exit_reason = "PROFIT_TARGET"
            elif current_price <= order.stop_loss:
                should_close = True
                exit_reason = "STOP_LOSS"
        else:
            if current_price <= order.profit_target:
                should_close = True
                exit_reason = "PROFIT_TARGET"
            elif current_price >= order.stop_loss:
                should_close = True
                exit_reason = "STOP_LOSS"

        if should_close:
            self.close_order(order_id, current_price, exit_reason)

        return order

    def close_order(self, order_id: str, exit_price: float, reason: str):
        """Close an open order"""

        if order_id not in self.open_orders:
            return

        order = self.open_orders[order_id]
        order.current_price = exit_price
        order.status = OrderStatus.CLOSED

        # Update capital
        self.current_capital += order.pnl

        # Move to closed orders
        self.closed_orders.append(order)
        del self.open_orders[order_id]

    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""

        if not self.closed_orders:
            return {
                "open_trades": len(self.open_orders),
                "closed_trades": 0,
                "current_capital": f"${self.current_capital:,.2f}",
                "account_return": "0.00%",
                "win_rate": "N/A",
                "profit_factor": "N/A",
                "unrealized_pnl": "$0.00"
            }

        wins = [t for t in self.closed_orders if t.pnl > 0]
        losses = [t for t in self.closed_orders if t.pnl < 0]

        total_return = ((self.current_capital - self.starting_capital) / self.starting_capital) * 100
        win_rate = (len(wins) / len(self.closed_orders)) * 100 if self.closed_orders else 0
        profit_factor = sum(t.pnl for t in wins) / abs(sum(t.pnl for t in losses)) if losses and sum(t.pnl for t in losses) != 0 else 0

        unrealized_pnl = sum(o.pnl for o in self.open_orders.values())

        return {
            "open_trades": len(self.open_orders),
            "closed_trades": len(self.closed_orders),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "current_capital": f"${self.current_capital:,.2f}",
            "starting_capital": f"${self.starting_capital:,.2f}",
            "account_return": f"{total_return:+.2f}%",
            "win_rate": f"{win_rate:.2f}%" if self.closed_orders else "N/A",
            "profit_factor": f"{profit_factor:.2f}" if profit_factor > 0 else "N/A",
            "unrealized_pnl": f"${unrealized_pnl:+.2f}",
            "session_duration": str(datetime.now() - self.session_start).split('.')[0]
        }

class LiveSignalGenerator:
    """Generate TOP QUANT signals from simulated market data"""

    def __init__(self, watchlist: List[str]):
        self.watchlist = watchlist
        self.prices = {t: 100.0 for t in watchlist}
        self.price_history = {t: [] for t in watchlist}
        self.signal_history = []

    def generate_market_data(self):
        """Simulate realistic market data"""
        import random

        for ticker in self.watchlist:
            # Simulate price movement
            daily_return = random.gauss(0.0005, 0.015)
            self.prices[ticker] *= (1 + daily_return)

            # Keep history
            if len(self.price_history[ticker]) < 50:
                self.price_history[ticker].append(self.prices[ticker])
            else:
                self.price_history[ticker] = self.price_history[ticker][1:] + [self.prices[ticker]]

    def get_signal(self, ticker: str) -> Optional[Dict]:
        """Generate signal for ticker"""

        if ticker not in self.price_history or len(self.price_history[ticker]) < 20:
            return None

        prices = self.price_history[ticker]
        current = prices[-1]
        sma_20 = sum(prices[-20:]) / 20
        sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20

        signal_strength = "NEUTRAL"
        signal_type = None

        if current > sma_20 > sma_50:
            signal_strength = "STRONG"
            signal_type = "LONG"
        elif current > sma_20:
            signal_strength = "MODERATE"
            signal_type = "LONG"
        elif current < sma_20 < sma_50:
            signal_strength = "STRONG"
            signal_type = "SHORT"
        elif current < sma_20:
            signal_strength = "MODERATE"
            signal_type = "SHORT"

        if signal_type:
            return {
                "ticker": ticker,
                "price": current,
                "type": signal_type,
                "strength": signal_strength,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "timestamp": datetime.now().isoformat()
            }

        return None

def print_trading_dashboard(engine: PaperTradingEngine, generator: LiveSignalGenerator):
    """Print live trading dashboard"""

    print("\n" + "="*100)
    print("  ╔════════════════════════════════════════════════════════════════════════════════════════════╗")
    print("  ║               TOP QUANT PAPER TRADING - LIVE DASHBOARD                                    ║")
    print("  ║                                                                                            ║")
    print("  ║  Real-time signal generation • Order execution • Performance tracking                     ║")
    print("  ╚════════════════════════════════════════════════════════════════════════════════════════════╝")
    print("="*100)

    stats = engine.get_portfolio_stats()

    print(f"\n⏰ SESSION: Started {engine.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 PORTFOLIO STATUS")
    print(f"{'-'*100}")
    print(f"Starting Capital:     {stats['starting_capital']}")
    print(f"Current Capital:      {stats['current_capital']}")
    print(f"Account Return:       {stats['account_return']}")
    print(f"Session Duration:     {stats['session_duration']}")

    print(f"\n📈 TRADE STATISTICS")
    print(f"{'-'*100}")
    print(f"Open Trades:          {stats['open_trades']}")
    print(f"Closed Trades:        {stats['closed_trades']}")
    print(f"Winning Trades:       {stats.get('winning_trades', 'N/A')}")
    print(f"Losing Trades:        {stats.get('losing_trades', 'N/A')}")
    print(f"Win Rate:             {stats['win_rate']}")
    print(f"Profit Factor:        {stats['profit_factor']}")
    print(f"Unrealized P&L:       {stats['unrealized_pnl']}")

    if engine.open_orders:
        print(f"\n🟢 OPEN POSITIONS")
        print(f"{'-'*100}")
        for order_id, order in engine.open_orders.items():
            print(f"{order.ticker} | Entry: ${order.entry_price:.2f} | Current: ${order.current_price:.2f} | P&L: {order.pnl_percent:+.2f}% | {order.signal_strength}")

    if engine.closed_orders:
        print(f"\n📋 RECENT CLOSED TRADES (Last 5)")
        print(f"{'-'*100}")
        for order in engine.closed_orders[-5:]:
            result = "✓ WIN" if order.pnl > 0 else "✗ LOSS"
            print(f"{order.ticker} | {order.side} | Entry: ${order.entry_price:.2f} → Exit: ${order.current_price:.2f} | P&L: {order.pnl_percent:+.2f}% | {result}")

    print(f"\n💱 CURRENT PRICES")
    print(f"{'-'*100}")
    for ticker, price in generator.prices.items():
        signal = generator.get_signal(ticker)
        if signal:
            signal_str = f"🟢 {signal['strength']} {signal['type']}"
        else:
            signal_str = "⚫ NEUTRAL"
        print(f"{ticker}: ${price:.2f} | {signal_str}")

    print(f"\n{'='*100}")
    print("✓ Paper trading active - Use Ctrl+C to stop session and generate final report")
    print(f"{'='*100}\n")

def run_paper_trading_session(watchlist: List[str] = None, duration_hours: int = 1):
    """Run paper trading session"""

    if watchlist is None:
        watchlist = ["SPY", "AAPL", "NVDA", "MSFT", "QQQ"]

    engine = PaperTradingEngine(account_size=100000, risk_per_trade=1.0)
    generator = LiveSignalGenerator(watchlist)

    print("\n" + "="*100)
    print("  TOP QUANT PAPER TRADING SESSION INITIATED")
    print("="*100)
    print(f"\nAccount Size:    $100,000")
    print(f"Risk Per Trade:  1%")
    print(f"Watchlist:       {', '.join(watchlist)}")
    print(f"Duration:        {duration_hours} hour(s)")
    print(f"\nGenerating live signals and executing paper trades...")
    print("Press Ctrl+C to end session\n")

    engine.running = True
    session_trades = []

    try:
        iteration = 0
        while engine.running and iteration < (duration_hours * 60):  # Simulate per-minute updates

            # Generate market data
            generator.generate_market_data()

            # Check for signals and place orders
            for ticker in watchlist:
                signal = generator.get_signal(ticker)

                if signal and signal['strength'] in ["STRONG", "MODERATE"]:
                    # Check if already have open position
                    has_position = any(o.ticker == ticker for o in engine.open_orders.values())

                    if not has_position and len(engine.open_orders) < 5:  # Max 5 concurrent trades
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

            # Update all open orders
            for order_id in list(engine.open_orders.keys()):
                current_price = generator.prices.get(engine.open_orders[order_id].ticker, 0)
                engine.update_order(order_id, current_price)

            # Print dashboard every 10 iterations
            if iteration % 10 == 0:
                print("\033[2J\033[H")  # Clear screen
                print_trading_dashboard(engine, generator)

            iteration += 1
            time.sleep(0.1)  # Simulate real-time updates

    except KeyboardInterrupt:
        print("\n\n⏹ Stopping paper trading session...")

    finally:
        engine.running = False

        # Close remaining open orders at market price
        for order_id in list(engine.open_orders.keys()):
            current_price = generator.prices.get(engine.open_orders[order_id].ticker)
            if current_price:
                engine.close_order(order_id, current_price, "SESSION_END")

        # Print final report
        print_session_report(engine, session_trades)

        # Save session
        save_session_data(engine, generator, session_trades)

def print_session_report(engine: PaperTradingEngine, trades: List):
    """Print final session report"""

    print("\n" + "="*100)
    print("  PAPER TRADING SESSION FINAL REPORT")
    print("="*100)

    stats = engine.get_portfolio_stats()

    print(f"\n💰 ACCOUNT SUMMARY")
    print(f"{'-'*100}")
    print(f"Starting Capital:     {stats['starting_capital']}")
    print(f"Ending Capital:       {stats['current_capital']}")
    print(f"Total Return:         {stats['account_return']}")
    print(f"Session Duration:     {stats['session_duration']}")

    print(f"\n📊 PERFORMANCE METRICS")
    print(f"{'-'*100}")
    print(f"Trades Executed:      {stats['closed_trades']}")
    print(f"Winning Trades:       {stats.get('winning_trades', 'N/A')}")
    print(f"Losing Trades:        {stats.get('losing_trades', 'N/A')}")
    print(f"Win Rate:             {stats['win_rate']}")
    print(f"Profit Factor:        {stats['profit_factor']}")

    if engine.closed_orders:
        wins = [t for t in engine.closed_orders if t.pnl > 0]
        losses = [t for t in engine.closed_orders if t.pnl < 0]

        avg_win = sum(t.pnl for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t.pnl for t in losses) / len(losses) if losses else 0

        print(f"Avg Win:              ${avg_win:.2f}")
        print(f"Avg Loss:             ${avg_loss:.2f}")

    print(f"\n{'='*100}")
    print("✓ Session complete - Data saved to top_quant_paper_trade_session.json")
    print(f"{'='*100}\n")

def save_session_data(engine: PaperTradingEngine, generator: LiveSignalGenerator, trades: List):
    """Save session data to JSON"""

    data = {
        "timestamp": datetime.now().isoformat(),
        "session_type": "paper_trading",
        "starting_capital": engine.starting_capital,
        "ending_capital": engine.current_capital,
        "total_return": ((engine.current_capital - engine.starting_capital) / engine.starting_capital) * 100,
        "trades": [t.to_dict() for t in engine.closed_orders],
        "session_stats": engine.get_portfolio_stats()
    }

    with open("top_quant_paper_trade_session.json", "w") as f:
        json.dump(data, f, indent=2)

def main():
    """Run paper trading"""
    watchlist = ["SPY", "AAPL", "NVDA", "MSFT", "QQQ"]
    run_paper_trading_session(watchlist=watchlist, duration_hours=1)

if __name__ == "__main__":
    main()
