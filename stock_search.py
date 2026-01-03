"""
Stock Symbol Search using multiple free APIs
"""

import requests
from typing import List, Dict
import time


class StockSearchAPI:
    """Search for stock symbols using free APIs"""

    def __init__(self):
        # No API keys required! Uses Yahoo Finance (free, no authentication)
        # Optional: You can add API keys for additional sources if desired
        self.finnhub_api_key = None  # Optional: Finnhub API key
        self.fmp_api_key = None  # Optional: Financial Modeling Prep API key
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 3600  # 1 hour

    def search_yahoo_finance(self, query: str) -> List[Dict]:
        """
        Search using Yahoo Finance (no API key required)
        """
        if len(query) < 1:
            return []

        try:
            url = f"https://query1.finance.yahoo.com/v1/finance/search"
            params = {
                'q': query,
                'quotesCount': 20,
                'newsCount': 0,
                'enableFuzzyQuery': False,
                'quotesQueryId': 'tss_match_phrase_query'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = []

                if 'quotes' in data:
                    for item in data['quotes']:
                        if 'symbol' in item:
                            # Determine exchange
                            exchange = item.get('exchange', 'UNKNOWN')
                            if exchange == 'NMS':
                                exchange = 'NASDAQ'
                            elif exchange == 'NYQ':
                                exchange = 'NYSE'
                            elif exchange == 'PCX':
                                exchange = 'NYSE'

                            results.append({
                                'symbol': item['symbol'],
                                'name': item.get('longname') or item.get('shortname', ''),
                                'exchange': exchange,
                                'type': item.get('quoteType', 'EQUITY')
                            })

                return results[:15]  # Limit to 15 results
        except Exception as e:
            print(f"Yahoo Finance search error: {e}")
            return []

        return []

    def search_finnhub(self, query: str) -> List[Dict]:
        """
        Search using Finnhub API (requires free API key)
        Get your key at: https://finnhub.io/
        """
        if not self.finnhub_api_key or len(query) < 1:
            return []

        try:
            url = f"https://finnhub.io/api/v1/search"
            params = {
                'q': query,
                'token': self.finnhub_api_key
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = []

                if 'result' in data:
                    for item in data['result'][:15]:
                        results.append({
                            'symbol': item['symbol'],
                            'name': item.get('description', ''),
                            'exchange': item.get('displaySymbol', '').split(':')[0] if ':' in item.get('displaySymbol', '') else '',
                            'type': item.get('type', 'Stock')
                        })

                return results
        except Exception as e:
            print(f"Finnhub search error: {e}")
            return []

        return []

    def search_crypto_symbols(self, query: str) -> List[Dict]:
        """
        Search crypto symbols
        """
        crypto_list = {
            'BTC': {'name': 'Bitcoin', 'exchange': 'BINANCE'},
            'ETH': {'name': 'Ethereum', 'exchange': 'BINANCE'},
            'BNB': {'name': 'Binance Coin', 'exchange': 'BINANCE'},
            'XRP': {'name': 'Ripple', 'exchange': 'BINANCE'},
            'SOL': {'name': 'Solana', 'exchange': 'BINANCE'},
            'ADA': {'name': 'Cardano', 'exchange': 'BINANCE'},
            'DOGE': {'name': 'Dogecoin', 'exchange': 'BINANCE'},
            'MATIC': {'name': 'Polygon', 'exchange': 'BINANCE'},
            'DOT': {'name': 'Polkadot', 'exchange': 'BINANCE'},
            'AVAX': {'name': 'Avalanche', 'exchange': 'BINANCE'},
            'LINK': {'name': 'Chainlink', 'exchange': 'BINANCE'},
            'UNI': {'name': 'Uniswap', 'exchange': 'BINANCE'},
            'ATOM': {'name': 'Cosmos', 'exchange': 'BINANCE'},
            'LTC': {'name': 'Litecoin', 'exchange': 'BINANCE'},
            'APT': {'name': 'Aptos', 'exchange': 'BINANCE'},
            'ARB': {'name': 'Arbitrum', 'exchange': 'BINANCE'},
            'OP': {'name': 'Optimism', 'exchange': 'BINANCE'},
        }

        query_upper = query.upper()
        results = []

        for symbol, info in crypto_list.items():
            symbol_usd = f"{symbol}USD"
            if query_upper in symbol or query_upper in info['name'].upper():
                results.append({
                    'symbol': symbol_usd,
                    'name': info['name'],
                    'exchange': info['exchange'],
                    'type': 'CRYPTO'
                })

        return results

    def search(self, query: str) -> List[Dict]:
        """
        Main search function that combines multiple sources
        """
        if not query or len(query.strip()) < 1:
            return []

        query = query.strip()

        # Check cache
        cache_key = query.lower()
        if cache_key in self.cache:
            if time.time() - self.cache_time.get(cache_key, 0) < self.cache_duration:
                return self.cache[cache_key]

        results = []

        # Search crypto first
        crypto_results = self.search_crypto_symbols(query)
        results.extend(crypto_results)

        # Search stocks
        if self.finnhub_api_key:
            finnhub_results = self.search_finnhub(query)
            results.extend(finnhub_results)
        else:
            # Fallback to Yahoo Finance
            yahoo_results = self.search_yahoo_finance(query)
            results.extend(yahoo_results)

        # Remove duplicates based on symbol
        seen = set()
        unique_results = []
        for item in results:
            if item['symbol'] not in seen:
                seen.add(item['symbol'])
                unique_results.append(item)

        # Cache results
        self.cache[cache_key] = unique_results
        self.cache_time[cache_key] = time.time()

        return unique_results[:20]  # Return top 20 results

    def format_result(self, result: Dict) -> str:
        """Format search result for display"""
        symbol = result['symbol']
        name = result['name']
        exchange = result['exchange']
        result_type = result.get('type', '')

        if result_type == 'CRYPTO':
            return f"{symbol} - {name} (Crypto)"
        elif exchange:
            return f"{symbol} - {name} ({exchange})"
        else:
            return f"{symbol} - {name}"


# Test the search
if __name__ == "__main__":
    searcher = StockSearchAPI()

    print("Testing stock search...\n")

    # Test searches
    test_queries = ["AAPL", "TESLA", "BTC", "GOOGL", "MSFT"]

    for query in test_queries:
        print(f"\nSearching for: {query}")
        print("-" * 50)
        results = searcher.search(query)

        if results:
            for result in results[:5]:
                print(f"  {searcher.format_result(result)}")
        else:
            print("  No results found")
