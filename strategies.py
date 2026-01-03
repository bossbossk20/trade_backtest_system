"""
Example Trading Strategies
"""

import pandas as pd


def simple_moving_average_crossover(data, index, position, short_window=20, long_window=50):
    """
    Simple Moving Average Crossover Strategy

    Buy when short MA crosses above long MA
    Sell when short MA crosses below long MA

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position (None if no position)
        short_window: Short MA period
        long_window: Long MA period

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < long_window:
        return 'hold'

    # Calculate moving averages
    close_prices = data['close'].iloc[:index+1]
    short_ma = close_prices.rolling(window=short_window).mean()
    long_ma = close_prices.rolling(window=long_window).mean()

    current_short_ma = short_ma.iloc[-1]
    current_long_ma = long_ma.iloc[-1]
    prev_short_ma = short_ma.iloc[-2]
    prev_long_ma = long_ma.iloc[-2]

    # Check for crossover
    if position is None:
        # Golden cross - buy signal
        if prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma:
            return 'buy'
    else:
        # Death cross - sell signal
        if prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma:
            return 'sell'

    return 'hold'


def rsi_strategy(data, index, position, period=14, oversold=30, overbought=70):
    """
    RSI (Relative Strength Index) Strategy

    Buy when RSI crosses above oversold level
    Sell when RSI crosses below overbought level

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position
        period: RSI period
        oversold: Oversold threshold
        overbought: Overbought threshold

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < period + 1:
        return 'hold'

    # Calculate RSI
    close_prices = data['close'].iloc[:index+1]
    delta = close_prices.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]

    if position is None:
        # Buy when RSI crosses above oversold
        if prev_rsi <= oversold and current_rsi > oversold:
            return 'buy'
    else:
        # Sell when RSI crosses below overbought
        if prev_rsi >= overbought and current_rsi < overbought:
            return 'sell'

    return 'hold'


def bollinger_bands_strategy(data, index, position, period=20, std_dev=2):
    """
    Bollinger Bands Mean Reversion Strategy

    Buy when price touches lower band
    Sell when price touches upper band

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position
        period: BB period
        std_dev: Standard deviation multiplier

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < period:
        return 'hold'

    # Calculate Bollinger Bands
    close_prices = data['close'].iloc[:index+1]
    sma = close_prices.rolling(window=period).mean()
    std = close_prices.rolling(window=period).std()

    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)

    current_price = data['close'].iloc[index]
    current_upper = upper_band.iloc[-1]
    current_lower = lower_band.iloc[-1]

    if position is None:
        # Buy when price touches lower band
        if current_price <= current_lower:
            return 'buy'
    else:
        # Sell when price touches upper band
        if current_price >= current_upper:
            return 'sell'

    return 'hold'


def buy_and_hold(data, index, position):
    """
    Simple buy and hold strategy

    Buy on first bar, hold until end

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index == 0 and position is None:
        return 'buy'

    return 'hold'


def macd_strategy(data, index, position, fast=12, slow=26, signal=9):
    """
    MACD (Moving Average Convergence Divergence) Strategy

    Buy when MACD crosses above signal line
    Sell when MACD crosses below signal line

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position
        fast: Fast EMA period
        slow: Slow EMA period
        signal: Signal line period

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < slow + signal:
        return 'hold'

    close_prices = data['close'].iloc[:index+1]

    # Calculate MACD
    exp1 = close_prices.ewm(span=fast, adjust=False).mean()
    exp2 = close_prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()

    current_macd = macd.iloc[-1]
    current_signal = signal_line.iloc[-1]
    prev_macd = macd.iloc[-2]
    prev_signal = signal_line.iloc[-2]

    if position is None:
        # Buy when MACD crosses above signal
        if prev_macd <= prev_signal and current_macd > current_signal:
            return 'buy'
    else:
        # Sell when MACD crosses below signal
        if prev_macd >= prev_signal and current_macd < current_signal:
            return 'sell'

    return 'hold'


def stochastic_strategy(data, index, position, k_period=14, d_period=3, overbought=80, oversold=20):
    """
    Stochastic Oscillator Strategy

    Buy when %K crosses above %D in oversold territory
    Sell when %K crosses below %D in overbought territory

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position
        k_period: %K period
        d_period: %D period
        overbought: Overbought threshold
        oversold: Oversold threshold

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < k_period + d_period:
        return 'hold'

    # Calculate Stochastic
    high_data = data['high'].iloc[:index+1]
    low_data = data['low'].iloc[:index+1]
    close_data = data['close'].iloc[:index+1]

    low_min = low_data.rolling(window=k_period).min()
    high_max = high_data.rolling(window=k_period).max()

    k_percent = 100 * ((close_data - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d_period).mean()

    current_k = k_percent.iloc[-1]
    current_d = d_percent.iloc[-1]
    prev_k = k_percent.iloc[-2]
    prev_d = d_percent.iloc[-2]

    if position is None:
        # Buy when %K crosses above %D in oversold
        if current_k < oversold and prev_k <= prev_d and current_k > current_d:
            return 'buy'
    else:
        # Sell when %K crosses below %D in overbought
        if current_k > overbought and prev_k >= prev_d and current_k < current_d:
            return 'sell'

    return 'hold'


def ema_crossover_strategy(data, index, position, short_period=9, long_period=21):
    """
    EMA (Exponential Moving Average) Crossover Strategy

    Buy when short EMA crosses above long EMA
    Sell when short EMA crosses below long EMA

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position
        short_period: Short EMA period
        long_period: Long EMA period

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < long_period:
        return 'hold'

    close_prices = data['close'].iloc[:index+1]

    short_ema = close_prices.ewm(span=short_period, adjust=False).mean()
    long_ema = close_prices.ewm(span=long_period, adjust=False).mean()

    current_short = short_ema.iloc[-1]
    current_long = long_ema.iloc[-1]
    prev_short = short_ema.iloc[-2]
    prev_long = long_ema.iloc[-2]

    if position is None:
        # Buy when short EMA crosses above long EMA
        if prev_short <= prev_long and current_short > current_long:
            return 'buy'
    else:
        # Sell when short EMA crosses below long EMA
        if prev_short >= prev_long and current_short < current_long:
            return 'sell'

    return 'hold'


def multi_indicator_strategy(data, index, position):
    """
    Multi-Indicator Strategy

    Combines RSI, MACD, and EMA for stronger signals
    Buy when: RSI oversold + MACD bullish + EMA bullish
    Sell when: RSI overbought + MACD bearish + EMA bearish

    Args:
        data: OHLCV DataFrame
        index: Current bar index
        position: Current position

    Returns:
        'buy', 'sell', or 'hold'
    """
    if index < 50:  # Need enough data for all indicators
        return 'hold'

    close_prices = data['close'].iloc[:index+1]

    # RSI calculation
    delta = close_prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]

    # MACD calculation
    exp1 = close_prices.ewm(span=12, adjust=False).mean()
    exp2 = close_prices.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - signal_line
    current_histogram = macd_histogram.iloc[-1]
    prev_histogram = macd_histogram.iloc[-2]

    # EMA calculation
    ema_short = close_prices.ewm(span=9, adjust=False).mean()
    ema_long = close_prices.ewm(span=21, adjust=False).mean()
    current_ema_short = ema_short.iloc[-1]
    current_ema_long = ema_long.iloc[-1]

    if position is None:
        # Buy signal: All indicators bullish
        rsi_bullish = current_rsi < 40
        macd_bullish = current_histogram > 0 and prev_histogram < 0
        ema_bullish = current_ema_short > current_ema_long

        if rsi_bullish and (macd_bullish or ema_bullish):
            return 'buy'
    else:
        # Sell signal: Any indicator bearish
        rsi_bearish = current_rsi > 60
        macd_bearish = current_histogram < 0 and prev_histogram > 0
        ema_bearish = current_ema_short < current_ema_long

        if rsi_bearish or macd_bearish or ema_bearish:
            return 'sell'

    return 'hold'
