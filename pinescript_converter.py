"""
Pine Script to Python Strategy Converter
Helps convert TradingView Pine Script strategies to Python
"""

import pandas as pd


class PineScriptHelper:
    """
    Helper class to provide Pine Script equivalent functions in Python
    """

    @staticmethod
    def ta_sma(series, length):
        """Pine: ta.sma(close, length)"""
        return series.rolling(window=length).mean()

    @staticmethod
    def ta_ema(series, length):
        """Pine: ta.ema(close, length)"""
        return series.ewm(span=length, adjust=False).mean()

    @staticmethod
    def ta_rsi(series, length=14):
        """Pine: ta.rsi(close, length)"""
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def ta_macd(series, fast=12, slow=26, signal=9):
        """Pine: [macdLine, signalLine, histLine] = ta.macd(close, fast, slow, signal)"""
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def ta_stoch(high, low, close, k_period=14, d_period=3):
        """Pine: ta.stoch(close, high, low, k_period)"""
        low_min = low.rolling(window=k_period).min()
        high_max = high.rolling(window=k_period).max()
        k = 100 * ((close - low_min) / (high_max - low_min))
        d = k.rolling(window=d_period).mean()
        return k, d

    @staticmethod
    def ta_bb(series, length=20, mult=2):
        """Pine: [middle, upper, lower] = ta.bb(close, length, mult)"""
        middle = series.rolling(window=length).mean()
        std = series.rolling(window=length).std()
        upper = middle + (std * mult)
        lower = middle - (std * mult)
        return middle, upper, lower

    @staticmethod
    def ta_atr(high, low, close, length=14):
        """Pine: ta.atr(length)"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=length).mean()

    @staticmethod
    def ta_crossover(series1, series2):
        """Pine: ta.crossover(fast, slow)"""
        return (series1 > series2) & (series1.shift(1) <= series2.shift(1))

    @staticmethod
    def ta_crossunder(series1, series2):
        """Pine: ta.crossunder(fast, slow)"""
        return (series1 < series2) & (series1.shift(1) >= series2.shift(1))


def convert_pinescript_example():
    """
    Example: How to convert a Pine Script strategy to Python
    """

    print("="*80)
    print("PINE SCRIPT TO PYTHON CONVERSION GUIDE")
    print("="*80)

    pinescript_example = """
    // PINE SCRIPT EXAMPLE
    //@version=5
    strategy("My Strategy", overlay=true)

    // Inputs
    fastLength = input(12, "Fast Length")
    slowLength = input(26, "Slow Length")

    // Indicators
    fastMA = ta.ema(close, fastLength)
    slowMA = ta.ema(close, slowLength)

    // Strategy Logic
    if (ta.crossover(fastMA, slowMA))
        strategy.entry("Long", strategy.long)

    if (ta.crossunder(fastMA, slowMA))
        strategy.close("Long")
    """

    python_equivalent = """
    # PYTHON EQUIVALENT
    def my_strategy(data, index, position, fast_length=12, slow_length=26):
        '''
        Converted from Pine Script
        Buy when fast EMA crosses above slow EMA
        Sell when fast EMA crosses below slow EMA
        '''
        if index < slow_length:
            return 'hold'

        close = data['close'].iloc[:index+1]

        # Calculate EMAs
        fast_ma = close.ewm(span=fast_length, adjust=False).mean()
        slow_ma = close.ewm(span=slow_length, adjust=False).mean()

        # Current and previous values
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        prev_fast = fast_ma.iloc[-2]
        prev_slow = slow_ma.iloc[-2]

        # Check for crossover/crossunder
        crossover = (prev_fast <= prev_slow) and (current_fast > current_slow)
        crossunder = (prev_fast >= prev_slow) and (current_fast < current_slow)

        if position is None and crossover:
            return 'buy'

        if position is not None and crossunder:
            return 'sell'

        return 'hold'
    """

    print("\nORIGINAL PINE SCRIPT:")
    print(pinescript_example)

    print("\nCONVERTED TO PYTHON:")
    print(python_equivalent)

    print("\n" + "="*80)
    print("COMMON PINE SCRIPT CONVERSIONS")
    print("="*80)

    conversions = [
        ("Pine Script", "Python Equivalent"),
        ("-"*35, "-"*40),
        ("ta.sma(close, 20)", "close.rolling(20).mean()"),
        ("ta.ema(close, 20)", "close.ewm(span=20, adjust=False).mean()"),
        ("ta.rsi(close, 14)", "PineScriptHelper.ta_rsi(close, 14)"),
        ("ta.macd(close, 12, 26, 9)", "PineScriptHelper.ta_macd(close, 12, 26, 9)"),
        ("ta.crossover(a, b)", "PineScriptHelper.ta_crossover(a, b)"),
        ("ta.crossunder(a, b)", "PineScriptHelper.ta_crossunder(a, b)"),
        ("high[1]", "high.shift(1)  or  high.iloc[-2]"),
        ("close > open", "close > open"),
        ("strategy.entry('Long')", "return 'buy'"),
        ("strategy.close('Long')", "return 'sell'"),
    ]

    for pine, python in conversions:
        print(f"{pine:<35} → {python}")

    print("\n" + "="*80)
    print("STEP-BY-STEP CONVERSION PROCESS")
    print("="*80)
    print("""
    1. COPY your Pine Script strategy from TradingView

    2. IDENTIFY the indicators used (SMA, EMA, RSI, MACD, etc.)

    3. CONVERT indicators using PineScriptHelper or pandas functions

    4. TRANSLATE entry/exit conditions:
       - strategy.entry() → return 'buy'
       - strategy.close() → return 'sell'
       - No action → return 'hold'

    5. TEST your converted strategy with the backtest engine

    6. SAVE the strategy function in strategies.py
    """)

    print("="*80)


if __name__ == "__main__":
    convert_pinescript_example()
