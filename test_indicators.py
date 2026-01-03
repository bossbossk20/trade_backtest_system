"""
Test the new indicator-based strategies
"""

from data_fetcher import TradingViewDataFetcher
from backtest_engine import BacktestEngine
from strategies import (
    macd_strategy,
    stochastic_strategy,
    ema_crossover_strategy,
    multi_indicator_strategy
)
from tvDatafeed import Interval


print("="*80)
print("TESTING NEW INDICATOR STRATEGIES - TSLA")
print("="*80)

# Fetch TSLA data
fetcher = TradingViewDataFetcher()
data = fetcher.get_data('TSLA', '', Interval.in_daily, n_bars=365)

print(f"\n✓ Fetched {len(data)} bars")
print(f"Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")

# Test new indicator strategies
strategies = {
    "MACD Strategy": macd_strategy,
    "Stochastic Oscillator": stochastic_strategy,
    "EMA Crossover": ema_crossover_strategy,
    "Multi-Indicator": multi_indicator_strategy
}

print("\n" + "="*80)
print("STRATEGY COMPARISON")
print("="*80)
print(f"{'Strategy':<30} {'Return':<15} {'Trades':<10} {'Win Rate':<12} {'Max DD'}")
print("-"*80)

initial_capital = 10000

for name, func in strategies.items():
    engine = BacktestEngine(initial_capital=initial_capital, commission=0.001)
    results = engine.run(data, func)

    print(f"{name:<30} {results['total_return_pct']:>7.2f}%       "
          f"{results['total_trades']:<10} {results['win_rate_pct']:>6.2f}%      "
          f"{results['max_drawdown_pct']:>6.2f}%")

print("="*80)
print("\nAll new indicator strategies are working! 🎉")
