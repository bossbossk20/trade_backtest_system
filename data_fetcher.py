"""
TradingView Data Fetcher
Fetches historical market data from TradingView using tvDatafeed
"""

from tvDatafeed import TvDatafeed, Interval
import pandas as pd


class TradingViewDataFetcher:
    """Fetches data from TradingView"""

    def __init__(self, username=None, password=None):
        """
        Initialize TradingView data fetcher

        Args:
            username: TradingView username (optional, for premium features)
            password: TradingView password (optional, for premium features)
        """
        self.tv = TvDatafeed(username, password)

    def get_data(self, symbol, exchange='', interval=Interval.in_daily, n_bars=500):
        """
        Fetch historical data for a symbol

        Args:
            symbol: Trading symbol (e.g., 'BTCUSD', 'AAPL')
            exchange: Exchange name (e.g., 'BINANCE', 'NASDAQ'). Empty string for default
            interval: Time interval (Interval.in_1_minute, in_5_minute, in_15_minute,
                     in_30_minute, in_1_hour, in_2_hour, in_4_hour, in_daily, in_weekly, in_monthly)
            n_bars: Number of bars to fetch

        Returns:
            pandas DataFrame with OHLCV data
        """
        data = self.tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)

        if data is None or data.empty:
            raise ValueError(f"No data retrieved for {symbol} on {exchange}")

        return data

    def get_multiple_symbols(self, symbols, exchange='', interval=Interval.in_daily, n_bars=500):
        """
        Fetch data for multiple symbols

        Args:
            symbols: List of trading symbols
            exchange: Exchange name
            interval: Time interval
            n_bars: Number of bars to fetch

        Returns:
            Dictionary with symbol as key and DataFrame as value
        """
        data_dict = {}
        for symbol in symbols:
            try:
                data_dict[symbol] = self.get_data(symbol, exchange, interval, n_bars)
                print(f"✓ Fetched data for {symbol}")
            except Exception as e:
                print(f"✗ Failed to fetch {symbol}: {str(e)}")

        return data_dict


if __name__ == "__main__":
    # Example usage
    fetcher = TradingViewDataFetcher()

    # Fetch Bitcoin data from Binance
    btc_data = fetcher.get_data('BTCUSD', 'BINANCE', Interval.in_daily, n_bars=365)
    print("\nBTC Data (last 5 rows):")
    print(btc_data.tail())

    # Fetch multiple symbols
    symbols = ['BTCUSD', 'ETHUSD']
    data = fetcher.get_multiple_symbols(symbols, 'BINANCE', Interval.in_daily, n_bars=100)
    print(f"\nFetched {len(data)} symbols")
