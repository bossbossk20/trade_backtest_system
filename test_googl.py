"""
Test GOOGL with 60 bars to verify P&L calculations
"""

from data_fetcher import TradingViewDataFetcher
from backtest_engine import BacktestEngine
from strategies import rsi_strategy
from tvDatafeed import Interval


print("="*100)
print("TESTING GOOGL WITH 60 BARS - RSI STRATEGY")
print("="*100)

# Fetch data
fetcher = TradingViewDataFetcher()
data = fetcher.get_data('GOOGL', '', Interval.in_daily, n_bars=60)

print(f"\n✓ Fetched {len(data)} bars")
print(f"Date range: {data.index[0]} to {data.index[-1]}")

# Run backtest
initial_capital = 10000
engine = BacktestEngine(initial_capital=initial_capital, commission=0.001)
results = engine.run(data, rsi_strategy)

print(f"\n{'='*100}")
print("BACKTEST RESULTS")
print('='*100)
print(f"Initial Capital:     ${results['initial_capital']:,.2f}")
print(f"Final Equity:        ${results['final_equity']:,.2f}")
print(f"Total Return:        {results['total_return_pct']:.2f}%")
print(f"Total Trades:        {results['total_trades']}")

# Detailed trade analysis
print(f"\n{'='*100}")
print("DETAILED TRADE LOG WITH P&L VERIFICATION")
print('='*100)

total_pnl = 0
for i, trade in enumerate(results['trades'], 1):
    print(f"\n--- Trade {i} ---")
    print(f"Entry Time:    {trade.entry_time}")
    print(f"Entry Price:   ${trade.entry_price:.2f}")
    print(f"Position Size: {trade.size:.6f} shares")
    print(f"Entry Value:   ${trade.entry_price * trade.size:.2f}")

    print(f"\nExit Time:     {trade.exit_time}")
    print(f"Exit Price:    ${trade.exit_price:.2f}")
    print(f"Exit Value:    ${trade.exit_price * trade.size:.2f}")

    # Calculate P&L
    if trade.position_type == 'long':
        calculated_pnl = (trade.exit_price - trade.entry_price) * trade.size
    else:
        calculated_pnl = (trade.entry_price - trade.exit_price) * trade.size

    print(f"\nP&L (reported): ${trade.pnl:.2f}")
    print(f"P&L (calculated): ${calculated_pnl:.2f}")
    print(f"Match: {'✓' if abs(trade.pnl - calculated_pnl) < 0.01 else '✗ MISMATCH!'}")

    pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100
    print(f"P&L %:          {pnl_pct:+.2f}%")

    total_pnl += trade.pnl
    print(f"Running Total P&L: ${total_pnl:.2f}")

# Verify total return calculation
print(f"\n{'='*100}")
print("VERIFICATION")
print('='*100)
print(f"Sum of all trade P&L:           ${total_pnl:.2f}")
print(f"Expected final equity:          ${initial_capital + total_pnl:.2f}")
print(f"Actual final equity:            ${results['final_equity']:.2f}")
print(f"Difference:                     ${results['final_equity'] - (initial_capital + total_pnl):.2f}")

calculated_return = ((results['final_equity'] - initial_capital) / initial_capital) * 100
print(f"\nReported return:                {results['total_return_pct']:.2f}%")
print(f"Calculated return:              {calculated_return:.2f}%")
print(f"Match: {'✓' if abs(results['total_return_pct'] - calculated_return) < 0.01 else '✗ MISMATCH!'}")

# Check commission impact
print(f"\n{'='*100}")
print("COMMISSION ANALYSIS")
print('='*100)
total_commission = 0
for i, trade in enumerate(results['trades'], 1):
    entry_commission = trade.entry_price * trade.size * 0.001
    exit_commission = trade.exit_price * trade.size * 0.001
    trade_commission = entry_commission + exit_commission
    total_commission += trade_commission
    print(f"Trade {i} commission: ${trade_commission:.2f} (entry: ${entry_commission:.2f}, exit: ${exit_commission:.2f})")

print(f"\nTotal commission paid: ${total_commission:.2f}")
print(f"Net P&L after commission: ${total_pnl - total_commission:.2f}")
print(f"Expected final: ${initial_capital + total_pnl - total_commission:.2f}")

print(f"\n{'='*100}")
