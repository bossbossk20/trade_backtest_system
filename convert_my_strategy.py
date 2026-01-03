"""
Interactive Pine Script to Python Converter
Paste your Pine Script strategy and get a Python template
"""


def show_template():
    """Show the basic template for a strategy"""

    template = '''
def my_custom_strategy(data, index, position):
    """
    Your strategy description here
    Converted from Pine Script

    Args:
        data: OHLCV DataFrame with columns: open, high, low, close, volume
        index: Current bar index
        position: Current position (None if no position)

    Returns:
        'buy' - Open a long position
        'sell' - Close current position
        'hold' - Do nothing
    """

    # Need minimum bars for indicators
    if index < 50:  # Adjust based on your longest indicator period
        return 'hold'

    # Get price data up to current bar
    close = data['close'].iloc[:index+1]
    high = data['high'].iloc[:index+1]
    low = data['low'].iloc[:index+1]
    open_price = data['open'].iloc[:index+1]

    # ========================================
    # STEP 1: CALCULATE YOUR INDICATORS HERE
    # ========================================

    # Example: Simple Moving Average
    # sma_20 = close.rolling(window=20).mean()

    # Example: EMA
    # ema_12 = close.ewm(span=12, adjust=False).mean()

    # Example: RSI
    # delta = close.diff()
    # gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    # loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    # rs = gain / loss
    # rsi = 100 - (100 / (1 + rs))

    # ========================================
    # STEP 2: DEFINE YOUR CONDITIONS
    # ========================================

    # Example: Get current and previous values
    # current_sma = sma_20.iloc[-1]
    # prev_sma = sma_20.iloc[-2]
    # current_price = close.iloc[-1]

    # ========================================
    # STEP 3: IMPLEMENT YOUR ENTRY/EXIT LOGIC
    # ========================================

    if position is None:
        # No position - check for BUY conditions

        # Example: Buy when price crosses above SMA
        # if prev_price <= prev_sma and current_price > current_sma:
        #     return 'buy'

        pass  # Replace with your buy logic

    else:
        # Have position - check for SELL conditions

        # Example: Sell when price crosses below SMA
        # if prev_price >= prev_sma and current_price < current_sma:
        #     return 'sell'

        pass  # Replace with your sell logic

    return 'hold'
'''

    return template


def show_examples():
    """Show common Pine Script patterns and their Python equivalents"""

    examples = """
================================================================================
COMMON PINE SCRIPT PATTERNS AND PYTHON EQUIVALENTS
================================================================================

1. MOVING AVERAGE CROSSOVER
----------------------------
Pine Script:
    fastMA = ta.ema(close, 12)
    slowMA = ta.ema(close, 26)
    if ta.crossover(fastMA, slowMA)
        strategy.entry("Long", strategy.long)
    if ta.crossunder(fastMA, slowMA)
        strategy.close("Long")

Python:
    fast_ma = close.ewm(span=12, adjust=False).mean()
    slow_ma = close.ewm(span=26, adjust=False).mean()

    current_fast = fast_ma.iloc[-1]
    current_slow = slow_ma.iloc[-1]
    prev_fast = fast_ma.iloc[-2]
    prev_slow = slow_ma.iloc[-2]

    if position is None:
        if prev_fast <= prev_slow and current_fast > current_slow:
            return 'buy'
    else:
        if prev_fast >= prev_slow and current_fast < current_slow:
            return 'sell'


2. RSI OVERSOLD/OVERBOUGHT
---------------------------
Pine Script:
    rsiValue = ta.rsi(close, 14)
    if rsiValue < 30
        strategy.entry("Long", strategy.long)
    if rsiValue > 70
        strategy.close("Long")

Python:
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    if position is None:
        if current_rsi < 30:
            return 'buy'
    else:
        if current_rsi > 70:
            return 'sell'


3. BOLLINGER BANDS
------------------
Pine Script:
    [middle, upper, lower] = ta.bb(close, 20, 2)
    if close < lower
        strategy.entry("Long", strategy.long)
    if close > upper
        strategy.close("Long")

Python:
    middle = close.rolling(window=20).mean()
    std = close.rolling(window=20).std()
    upper = middle + (std * 2)
    lower = middle - (std * 2)

    current_price = close.iloc[-1]
    current_upper = upper.iloc[-1]
    current_lower = lower.iloc[-1]

    if position is None:
        if current_price < current_lower:
            return 'buy'
    else:
        if current_price > current_upper:
            return 'sell'


4. MACD CROSSOVER
-----------------
Pine Script:
    [macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)
    if ta.crossover(macdLine, signalLine)
        strategy.entry("Long", strategy.long)
    if ta.crossunder(macdLine, signalLine)
        strategy.close("Long")

Python:
    exp1 = close.ewm(span=12, adjust=False).mean()
    exp2 = close.ewm(span=26, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    prev_macd = macd_line.iloc[-2]
    prev_signal = signal_line.iloc[-2]

    if position is None:
        if prev_macd <= prev_signal and current_macd > current_signal:
            return 'buy'
    else:
        if prev_macd >= prev_signal and current_macd < current_signal:
            return 'sell'


5. MULTIPLE CONDITIONS (AND/OR)
--------------------------------
Pine Script:
    condition1 = close > ta.sma(close, 50)
    condition2 = ta.rsi(close, 14) < 30
    if condition1 and condition2
        strategy.entry("Long", strategy.long)

Python:
    sma_50 = close.rolling(window=50).mean()
    current_price = close.iloc[-1]
    current_sma = sma_50.iloc[-1]

    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    condition1 = current_price > current_sma
    condition2 = current_rsi < 30

    if position is None:
        if condition1 and condition2:
            return 'buy'

================================================================================
"""
    return examples


def main():
    print("="*80)
    print("PINE SCRIPT TO PYTHON STRATEGY CONVERTER")
    print("="*80)
    print()
    print("This tool helps you convert TradingView Pine Script strategies to Python")
    print()

    while True:
        print("\nWhat would you like to do?")
        print("1. See the Python strategy template")
        print("2. See conversion examples")
        print("3. Get help with specific Pine Script functions")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            print("\n" + "="*80)
            print("PYTHON STRATEGY TEMPLATE")
            print("="*80)
            print(show_template())
            print("\nCopy this template to strategies.py and fill in your logic!")

        elif choice == "2":
            print(show_examples())

        elif choice == "3":
            print("\n" + "="*80)
            print("PINE SCRIPT FUNCTION REFERENCE")
            print("="*80)
            print("""
Common Pine Script functions and their Python equivalents:

Indicators:
  ta.sma(source, length)      → source.rolling(length).mean()
  ta.ema(source, length)      → source.ewm(span=length, adjust=False).mean()
  ta.rsi(source, length)      → (see RSI example above)
  ta.macd(...)                → (see MACD example above)
  ta.bb(source, length, mult) → (see Bollinger Bands example)
  ta.stoch(...)               → (see stochastic_strategy in strategies.py)
  ta.atr(length)              → (see PineScriptHelper.ta_atr)

Crossovers:
  ta.crossover(a, b)          → (a > b) & (a.shift(1) <= b.shift(1))
  ta.crossunder(a, b)         → (a < b) & (a.shift(1) >= b.shift(1))

Historical Data:
  close[1]                    → close.iloc[-2] or close.shift(1)
  high[0]                     → high.iloc[-1]

Math:
  math.max(a, b)              → max(a, b)
  math.min(a, b)              → min(a, b)
  math.abs(a)                 → abs(a)

Entry/Exit:
  strategy.entry("Long")      → return 'buy'
  strategy.close("Long")      → return 'sell'
  strategy.exit(...)          → return 'sell'
  (no action)                 → return 'hold'
            """)

        elif choice == "4":
            print("\nHappy trading! 🚀")
            break
        else:
            print("\nInvalid choice. Please enter 1-4.")

    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. Copy your Pine Script strategy from TradingView
2. Use the template and examples above to convert it
3. Add your converted function to strategies.py
4. Import it in app.py and add to strategy_options
5. Test it with the backtest engine!

Need help? Check the examples in strategies.py for reference.
    """)


if __name__ == "__main__":
    main()
