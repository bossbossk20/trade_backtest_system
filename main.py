"""
Main script to run backtests with TradingView data
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
import matplotlib.pyplot as plt


def plot_equity_curve(results, title="Equity Curve"):
    """Plot the equity curve"""
    equity_df = results['equity_curve']

    plt.figure(figsize=(12, 6))
    plt.plot(equity_df['time'], equity_df['equity'], label='Equity', linewidth=2)
    plt.axhline(y=results['initial_capital'], color='r', linestyle='--', label='Initial Capital')
    plt.xlabel('Date')
    plt.ylabel('Equity ($)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    print("TradingView Backtest System")
    print("=" * 50)

    # Initialize data fetcher
    print("\n1. Fetching data from TradingView...")
    fetcher = TradingViewDataFetcher()

    # Fetch data (you can change these parameters)
    symbol = 'BTCUSD'
    exchange = 'BINANCE'
    interval = Interval.in_daily
    n_bars = 365

    print(f"   Symbol: {symbol}")
    print(f"   Exchange: {exchange}")
    print(f"   Interval: Daily")
    print(f"   Bars: {n_bars}")

    try:
        data = fetcher.get_data(symbol, exchange, interval, n_bars)
        print(f"   ✓ Successfully fetched {len(data)} bars")
        print(f"\nData range: {data.index[0]} to {data.index[-1]}")
    except Exception as e:
        print(f"   ✗ Error fetching data: {str(e)}")
        return

    # Initialize backtest engine
    initial_capital = 10000
    commission = 0.001  # 0.1%

    print(f"\n2. Backtest Configuration")
    print(f"   Initial Capital: ${initial_capital:,.2f}")
    print(f"   Commission: {commission*100}%")

    # Test different strategies
    strategies_to_test = [
        ("Simple Moving Average Crossover", simple_moving_average_crossover),
        ("RSI Strategy", rsi_strategy),
        ("Bollinger Bands", bollinger_bands_strategy),
        ("Buy and Hold", buy_and_hold)
    ]

    print(f"\n3. Running Backtests...")
    results_summary = []

    for strategy_name, strategy_func in strategies_to_test:
        print(f"\n   Testing: {strategy_name}")
        engine = BacktestEngine(initial_capital=initial_capital, commission=commission)

        results = engine.run(data, strategy_func)
        results_summary.append({
            'name': strategy_name,
            'results': results
        })

        engine.print_results(results)

    # Compare strategies
    print("\n4. Strategy Comparison")
    print("=" * 50)
    print(f"{'Strategy':<35} {'Return':<12} {'Trades':<10} {'Win Rate'}")
    print("-" * 50)

    for item in results_summary:
        name = item['name']
        res = item['results']
        print(f"{name:<35} {res['total_return_pct']:>6.2f}%      {res['total_trades']:<10} {res['win_rate_pct']:>6.2f}%")

    print("=" * 50)

    # Plot best strategy
    best_strategy = max(results_summary, key=lambda x: x['results']['total_return_pct'])
    print(f"\nBest performing strategy: {best_strategy['name']}")
    print("Plotting equity curve...")

    plot_equity_curve(
        best_strategy['results'],
        title=f"{best_strategy['name']} - Equity Curve"
    )


if __name__ == "__main__":
    main()
