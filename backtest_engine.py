"""
Simple Custom Backtesting Engine
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Optional


class Position:
    """Represents a trading position"""

    def __init__(self, entry_price, entry_time, size, position_type):
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.size = size
        self.position_type = position_type  # 'long' or 'short'
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0

    def close(self, exit_price, exit_time):
        """Close the position"""
        self.exit_price = exit_price
        self.exit_time = exit_time

        if self.position_type == 'long':
            self.pnl = (exit_price - self.entry_price) * self.size
        else:  # short
            self.pnl = (self.entry_price - exit_price) * self.size

        return self.pnl


class BacktestEngine:
    """Simple backtesting engine"""

    def __init__(self, initial_capital=10000, commission=0.001):
        """
        Initialize backtest engine

        Args:
            initial_capital: Starting capital
            commission: Commission rate (e.g., 0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.reset()

    def reset(self):
        """Reset the backtest state"""
        self.cash = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_curve = []

    def run(self, data: pd.DataFrame, strategy: Callable):
        """
        Run backtest on historical data

        Args:
            data: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            strategy: Strategy function that takes (data, index, position) and returns signal
                     Signal: 'buy', 'sell', or 'hold'

        Returns:
            Dictionary with backtest results
        """
        self.reset()
        data = data.copy()

        for i in range(len(data)):
            current_bar = data.iloc[i]
            current_price = current_bar['close']
            current_time = data.index[i]

            # Get strategy signal
            signal = strategy(data, i, self.position)

            # Execute signal
            if signal == 'buy' and self.position is None:
                # Open long position
                position_size = (self.cash * 0.95) / current_price  # Use 95% of cash
                position_value = position_size * current_price
                commission_cost = position_value * self.commission
                self.cash -= (position_value + commission_cost)  # Deduct purchase cost AND commission

                self.position = Position(
                    entry_price=current_price,
                    entry_time=current_time,
                    size=position_size,
                    position_type='long'
                )

            elif signal == 'sell' and self.position is not None:
                # Close position
                pnl = self.position.close(current_price, current_time)
                position_value = self.position.size * current_price
                commission_cost = position_value * self.commission

                self.cash += position_value - commission_cost
                self.trades.append(self.position)
                self.position = None

            # Calculate current equity
            if self.position:
                position_value = self.position.size * current_price
                equity = self.cash + position_value
            else:
                equity = self.cash

            self.equity_curve.append({
                'time': current_time,
                'equity': equity,
                'cash': self.cash,
                'position_value': position_value if self.position else 0
            })

        # Close any open position at the end
        if self.position:
            final_price = data.iloc[-1]['close']
            final_time = data.index[-1]
            self.position.close(final_price, final_time)
            position_value = self.position.size * final_price
            self.cash += position_value * (1 - self.commission)
            self.trades.append(self.position)
            self.position = None

        return self.calculate_metrics()

    def calculate_metrics(self) -> Dict:
        """Calculate performance metrics"""
        equity_df = pd.DataFrame(self.equity_curve)
        final_equity = equity_df['equity'].iloc[-1] if len(equity_df) > 0 else self.initial_capital

        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100

        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]

        win_rate = (len(winning_trades) / len(self.trades) * 100) if self.trades else 0

        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0

        # Calculate max drawdown
        equity_series = equity_df['equity']
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()

        return {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return_pct': total_return,
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown_pct': max_drawdown,
            'equity_curve': equity_df,
            'trades': self.trades
        }

    def print_results(self, results: Dict):
        """Print backtest results"""
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Initial Capital:    ${results['initial_capital']:,.2f}")
        print(f"Final Equity:       ${results['final_equity']:,.2f}")
        print(f"Total Return:       {results['total_return_pct']:.2f}%")
        print(f"\nTotal Trades:       {results['total_trades']}")
        print(f"Winning Trades:     {results['winning_trades']}")
        print(f"Losing Trades:      {results['losing_trades']}")
        print(f"Win Rate:           {results['win_rate_pct']:.2f}%")
        print(f"\nAvg Win:            ${results['avg_win']:.2f}")
        print(f"Avg Loss:           ${results['avg_loss']:.2f}")
        print(f"Max Drawdown:       {results['max_drawdown_pct']:.2f}%")
        print("="*50 + "\n")
