"""
Quick test script for TSLA backtest
"""

from data_fetcher import TradingViewDataFetcher
from backtest_engine import BacktestEngine
from strategies import (
    simple_moving_average_crossover,
    rsi_strategy,
    bollinger_bands_strategy,
    buy_and_hold
)
from tvDatafeed import Interval
import pandas as pd


def print_detailed_summary(results, symbol, exchange):
    """Print detailed backtest summary"""
    print("\n" + "="*80)
    print("DETAILED BACKTEST SUMMARY")
    print("="*80)

    print("\n📈 PERFORMANCE METRICS")
    print("-" * 80)
    print(f"Initial Capital:        ${results['initial_capital']:,.2f}")
    print(f"Final Equity:           ${results['final_equity']:,.2f}")
    print(f"Net Profit/Loss:        ${results['final_equity'] - results['initial_capital']:,.2f}")
    print(f"Total Return:           {results['total_return_pct']:.2f}%")

    print("\n💰 TRADE STATISTICS")
    print("-" * 80)
    print(f"Total Trades:           {results['total_trades']}")
    print(f"Winning Trades:         {results['winning_trades']}")
    print(f"Losing Trades:          {results['losing_trades']}")
    print(f"Win Rate:               {results['win_rate_pct']:.2f}%")

    if results['losing_trades'] > 0 and results['avg_loss'] != 0:
        profit_factor = abs(results['avg_win'] * results['winning_trades'] / (results['avg_loss'] * results['losing_trades']))
        print(f"Profit Factor:          {profit_factor:.2f}")

    print("\n📊 WIN/LOSS ANALYSIS")
    print("-" * 80)
    print(f"Average Win:            ${results['avg_win']:,.2f}")
    print(f"Average Loss:           ${results['avg_loss']:,.2f}")
    if results['trades']:
        largest_win = max([t.pnl for t in results['trades']])
        largest_loss = min([t.pnl for t in results['trades']])
        print(f"Largest Win:            ${largest_win:,.2f}")
        print(f"Largest Loss:           ${largest_loss:,.2f}")
        total_wins = results['avg_win'] * results['winning_trades']
        total_losses = results['avg_loss'] * results['losing_trades']
        print(f"Total Wins:             ${total_wins:,.2f}")
        print(f"Total Losses:           ${total_losses:,.2f}")

    print("\n⏱️  POSITION METRICS")
    print("-" * 80)
    if results['trades']:
        completed_trades = [t for t in results['trades'] if t.exit_time and t.entry_time]
        if completed_trades:
            hold_times = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in completed_trades]
            avg_hold = sum(hold_times) / len(hold_times)
            print(f"Avg Hold Time:          {avg_hold:.1f} hours ({avg_hold/24:.1f} days)")
            print(f"Longest Trade:          {max(hold_times):.1f} hours ({max(hold_times)/24:.1f} days)")
            print(f"Shortest Trade:         {min(hold_times):.1f} hours ({min(hold_times)/24:.1f} days)")

        avg_trade_return = sum([t.pnl for t in results['trades']]) / len(results['trades'])
        print(f"Avg Trade Return:       ${avg_trade_return:,.2f}")

    print("\n⚠️  RISK METRICS")
    print("-" * 80)
    print(f"Max Drawdown:           {results['max_drawdown_pct']:.2f}%")

    if results['avg_loss'] != 0:
        risk_reward = abs(results['avg_win'] / results['avg_loss'])
        print(f"Risk/Reward Ratio:      {risk_reward:.2f}")

    # Calculate Sharpe ratio
    equity_curve = results['equity_curve']
    returns = equity_curve['equity'].pct_change().dropna()
    if len(returns) > 0 and returns.std() != 0:
        sharpe = returns.mean() / returns.std() * (252 ** 0.5)
        print(f"Sharpe Ratio (approx):  {sharpe:.2f}")
        print(f"Volatility:             {returns.std() * 100:.2f}%")

    print("\n📍 MARKET INFORMATION")
    print("-" * 80)
    print(f"Symbol:                 {symbol}")
    print(f"Exchange:               {exchange}")
    print("="*80)


def print_trade_log(trades):
    """Print detailed trade log"""
    if not trades:
        return

    print("\n" + "="*100)
    print("TRADE LOG - EACH BUY/SELL POINT")
    print("="*100)
    print(f"{'#':<4} {'Entry Date':<20} {'Entry $':<12} {'Exit Date':<20} {'Exit $':<12} {'P&L $':<12} {'P&L %':<10}")
    print("-"*100)

    for i, trade in enumerate(trades, 1):
        pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100 if trade.entry_price else 0
        entry_date = trade.entry_time.strftime('%Y-%m-%d %H:%M') if trade.entry_time else 'N/A'
        exit_date = trade.exit_time.strftime('%Y-%m-%d %H:%M') if trade.exit_time else 'N/A'

        # Color coding for terminal
        if trade.pnl > 0:
            pnl_str = f"${trade.pnl:>11,.2f}"
            pnl_pct_str = f"{pnl_pct:>7.2f}%"
        else:
            pnl_str = f"${trade.pnl:>11,.2f}"
            pnl_pct_str = f"{pnl_pct:>7.2f}%"

        print(f"{i:<4} {entry_date:<20} ${trade.entry_price:<11.2f} "
              f"{exit_date:<20} ${trade.exit_price:<11.2f} "
              f"{pnl_str:<12} {pnl_pct_str:<10}")

    print("="*100)


print("="*80)
print("TESTING TSLA (Tesla) FROM NASDAQ")
print("="*80)

# Fetch TSLA data
print("\n1. Fetching TSLA data from NASDAQ...")
fetcher = TradingViewDataFetcher()

try:
    # Try default exchange first (works better for stocks)
    data = fetcher.get_data('TSLA', '', Interval.in_daily, n_bars=365)
    print(f"   ✓ Successfully fetched {len(data)} bars")
    print(f"   Data range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
    print(f"   Current price: ${data['close'].iloc[-1]:.2f}")
    print(f"   Year high: ${data['high'].max():.2f}")
    print(f"   Year low: ${data['low'].min():.2f}")
except Exception as e:
    print(f"   ✗ Error: {str(e)}")
    exit(1)

# Test all strategies
strategies = {
    "Simple Moving Average Crossover": simple_moving_average_crossover,
    "RSI Strategy": rsi_strategy,
    "Bollinger Bands": bollinger_bands_strategy,
    "Buy and Hold": buy_and_hold
}

print("\n2. Running backtests with $10,000 initial capital...")

results_list = []
initial_capital = 10000
commission = 0.001

for name, func in strategies.items():
    print(f"\n{'='*80}")
    print(f"Strategy: {name}")
    print('='*80)

    engine = BacktestEngine(initial_capital=initial_capital, commission=commission)
    results = engine.run(data, func)

    # Quick summary
    print(f"\nReturn: {results['total_return_pct']:.2f}% | "
          f"Trades: {results['total_trades']} | "
          f"Win Rate: {results['win_rate_pct']:.2f}% | "
          f"Final: ${results['final_equity']:,.2f}")

    results_list.append({
        'name': name,
        'results': results,
        'return': results['total_return_pct']
    })

# Find best strategy
best = max(results_list, key=lambda x: x['return'])

print("\n" + "="*80)
print(f"🏆 BEST STRATEGY: {best['name']}")
print("="*80)

# Show detailed summary for best strategy
print_detailed_summary(best['results'], 'TSLA', 'Default/Auto')

# Show all trade points
print_trade_log(best['results']['trades'])

# Comparison table
print("\n" + "="*80)
print("STRATEGY COMPARISON")
print("="*80)
print(f"{'Strategy':<40} {'Return':<15} {'Trades':<10} {'Win Rate':<12} {'Max DD'}")
print("-"*80)

for item in results_list:
    res = item['results']
    print(f"{item['name']:<40} {res['total_return_pct']:>7.2f}%       "
          f"{res['total_trades']:<10} {res['win_rate_pct']:>6.2f}%      "
          f"{res['max_drawdown_pct']:>6.2f}%")

print("="*80)
