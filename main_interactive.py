"""
Interactive backtest script with buy/sell visualization
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
import pandas as pd


def plot_strategy_with_signals(data, trades, strategy_name, results):
    """Plot price chart with buy/sell signals"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [2, 1]})

    # Plot price
    ax1.plot(data.index, data['close'], label='Close Price', linewidth=1.5, color='blue', alpha=0.7)

    # Plot buy signals
    buy_signals = [t for t in trades if t.entry_time is not None]
    if buy_signals:
        buy_times = [t.entry_time for t in buy_signals]
        buy_prices = [t.entry_price for t in buy_signals]
        ax1.scatter(buy_times, buy_prices, marker='^', color='green', s=200,
                   label='Buy', zorder=5, edgecolors='darkgreen', linewidth=2)

    # Plot sell signals
    sell_signals = [t for t in trades if t.exit_time is not None]
    if sell_signals:
        sell_times = [t.exit_time for t in sell_signals]
        sell_prices = [t.exit_price for t in sell_signals]
        ax1.scatter(sell_times, sell_prices, marker='v', color='red', s=200,
                   label='Sell', zorder=5, edgecolors='darkred', linewidth=2)

    # Add profit/loss annotations
    for trade in trades:
        if trade.exit_time:
            pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100
            color = 'green' if trade.pnl > 0 else 'red'
            mid_time = trade.entry_time + (trade.exit_time - trade.entry_time) / 2
            mid_price = (trade.entry_price + trade.exit_price) / 2
            ax1.annotate(f'{pnl_pct:+.1f}%',
                        xy=(mid_time, mid_price),
                        fontsize=9, color=color, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    ax1.set_title(f'{strategy_name} - Price Chart with Buy/Sell Signals', fontsize=14, weight='bold')
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Plot equity curve
    equity_df = results['equity_curve']
    ax2.plot(equity_df['time'], equity_df['equity'], label='Equity',
            linewidth=2, color='purple')
    ax2.axhline(y=results['initial_capital'], color='gray',
               linestyle='--', label='Initial Capital', alpha=0.7)
    ax2.fill_between(equity_df['time'], results['initial_capital'],
                     equity_df['equity'], alpha=0.3, color='purple')

    ax2.set_title('Equity Curve', fontsize=12, weight='bold')
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Equity ($)', fontsize=12)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def print_trade_log(trades):
    """Print detailed trade log"""
    print("\nDETAILED TRADE LOG")
    print("=" * 100)
    print(f"{'#':<4} {'Entry Time':<20} {'Entry $':<12} {'Exit Time':<20} {'Exit $':<12} {'P&L $':<12} {'P&L %':<10}")
    print("-" * 100)

    for i, trade in enumerate(trades, 1):
        pnl_pct = (trade.pnl / (trade.entry_price * trade.size)) * 100 if trade.entry_price else 0
        entry_time_str = str(trade.entry_time) if trade.entry_time else 'N/A'
        exit_time_str = str(trade.exit_time) if trade.exit_time else 'N/A'

        print(f"{i:<4} {entry_time_str:<20} ${trade.entry_price:<11.2f} "
              f"{exit_time_str:<20} ${trade.exit_price:<11.2f} "
              f"${trade.pnl:<11.2f} {pnl_pct:>7.2f}%")

    print("=" * 100)


def get_user_input():
    """Get trading parameters from user"""
    print("\n" + "=" * 50)
    print("TRADINGVIEW BACKTEST CONFIGURATION")
    print("=" * 50)

    # Symbol
    symbol = input("\nEnter symbol (e.g., BTCUSD, ETHUSD, AAPL): ").strip().upper()
    if not symbol:
        symbol = 'BTCUSD'
        print(f"Using default: {symbol}")

    # Exchange
    print("\nCommon exchanges:")
    print("  - BINANCE (crypto)")
    print("  - NASDAQ (stocks)")
    print("  - NYSE (stocks)")
    print("  - COINBASE (crypto)")
    exchange = input("Enter exchange (press Enter for default): ").strip().upper()
    if not exchange:
        exchange = 'BINANCE'
        print(f"Using default: {exchange}")

    # Interval
    print("\nAvailable intervals:")
    print("  1. 1 minute")
    print("  2. 5 minutes")
    print("  3. 15 minutes")
    print("  4. 1 hour")
    print("  5. 4 hours")
    print("  6. Daily (default)")
    print("  7. Weekly")

    interval_choice = input("Select interval (1-7, or press Enter for daily): ").strip()

    interval_map = {
        '1': Interval.in_1_minute,
        '2': Interval.in_5_minute,
        '3': Interval.in_15_minute,
        '4': Interval.in_1_hour,
        '5': Interval.in_4_hour,
        '6': Interval.in_daily,
        '7': Interval.in_weekly,
    }

    interval = interval_map.get(interval_choice, Interval.in_daily)
    interval_name = {
        '1': '1 minute', '2': '5 minutes', '3': '15 minutes',
        '4': '1 hour', '5': '4 hours', '6': 'Daily', '7': 'Weekly'
    }.get(interval_choice, 'Daily')

    # Number of bars
    n_bars_input = input("\nEnter number of bars to fetch (default 365): ").strip()
    n_bars = int(n_bars_input) if n_bars_input.isdigit() else 365

    # Capital
    capital_input = input("\nEnter initial capital (default 10000): ").strip()
    capital = float(capital_input) if capital_input else 10000

    # Strategy
    print("\nAvailable strategies:")
    print("  1. Simple Moving Average Crossover")
    print("  2. RSI Strategy")
    print("  3. Bollinger Bands")
    print("  4. Buy and Hold")
    print("  5. Test All Strategies")

    strategy_choice = input("Select strategy (1-5, default 5): ").strip()

    return {
        'symbol': symbol,
        'exchange': exchange,
        'interval': interval,
        'interval_name': interval_name,
        'n_bars': n_bars,
        'capital': capital,
        'strategy_choice': strategy_choice or '5'
    }


def main():
    print("\n" + "=" * 50)
    print("TRADINGVIEW BACKTEST SYSTEM")
    print("=" * 50)

    # Get user input
    config = get_user_input()

    # Fetch data
    print(f"\nFetching data from TradingView...")
    print(f"  Symbol: {config['symbol']}")
    print(f"  Exchange: {config['exchange']}")
    print(f"  Interval: {config['interval_name']}")
    print(f"  Bars: {config['n_bars']}")

    fetcher = TradingViewDataFetcher()

    try:
        data = fetcher.get_data(
            config['symbol'],
            config['exchange'],
            config['interval'],
            config['n_bars']
        )
        print(f"  ✓ Successfully fetched {len(data)} bars")
        print(f"  Data range: {data.index[0]} to {data.index[-1]}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return

    # Define strategies
    strategies = {
        '1': ("Simple Moving Average Crossover", simple_moving_average_crossover),
        '2': ("RSI Strategy", rsi_strategy),
        '3': ("Bollinger Bands", bollinger_bands_strategy),
        '4': ("Buy and Hold", buy_and_hold)
    }

    # Run backtest
    if config['strategy_choice'] == '5':
        # Test all strategies
        results_summary = []

        for key, (name, func) in strategies.items():
            print(f"\n{'='*50}")
            print(f"Testing: {name}")
            print('='*50)

            engine = BacktestEngine(
                initial_capital=config['capital'],
                commission=0.001
            )
            results = engine.run(data, func)
            engine.print_results(results)
            print_trade_log(results['trades'])

            results_summary.append({
                'name': name,
                'results': results
            })

        # Strategy comparison
        print("\n" + "=" * 80)
        print("STRATEGY COMPARISON")
        print("=" * 80)
        print(f"{'Strategy':<35} {'Return':<12} {'Trades':<10} {'Win Rate':<12} {'Max DD'}")
        print("-" * 80)

        for item in results_summary:
            name = item['name']
            res = item['results']
            print(f"{name:<35} {res['total_return_pct']:>6.2f}%      "
                  f"{res['total_trades']:<10} {res['win_rate_pct']:>6.2f}%      "
                  f"{res['max_drawdown_pct']:>6.2f}%")

        print("=" * 80)

        # Plot best strategy
        best = max(results_summary, key=lambda x: x['results']['total_return_pct'])
        print(f"\nPlotting best strategy: {best['name']}")
        plot_strategy_with_signals(
            data,
            best['results']['trades'],
            best['name'],
            best['results']
        )

    else:
        # Run single strategy
        name, func = strategies[config['strategy_choice']]
        print(f"\n{'='*50}")
        print(f"Testing: {name}")
        print('='*50)

        engine = BacktestEngine(
            initial_capital=config['capital'],
            commission=0.001
        )
        results = engine.run(data, func)
        engine.print_results(results)
        print_trade_log(results['trades'])

        # Plot results
        plot_strategy_with_signals(data, results['trades'], name, results)


if __name__ == "__main__":
    main()
