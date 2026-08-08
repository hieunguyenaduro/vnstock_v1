import ccxt
import pandas as pd
import pandas_ta as ta


class FetchBinanceData:

    def __init__(self):
        # Initializing ccxt exchange instance once for reuse
        self.exchange = ccxt.binance({
            'enableRateLimit': True,  # Good practice to avoid hitting rate limits
        })

    def get_binance_data(self, token="BTC/USDT", timeframe="1d", period=14, limit=100) -> pd.DataFrame:
        """Fetches OHLCV data from Binance and computes RSI."""
        # Fetch OHLCV data
        ohlcv = self.exchange.fetch_ohlcv(token, timeframe=timeframe, limit=limit)

        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Calculate RSI
        df['RSI'] = ta.rsi(df['close'], length=period)

        return df

    def get_us_stock_tickers_on_crypto_exchange(self, target_symbol: str = "B/USDT") -> list:
        """Searches for stock-related trading pairs on the exchange."""
        markets = self.exchange.load_markets()

        matched_symbols = [symbol for symbol in markets if target_symbol.upper() in symbol]

        list_remove = ['BNB/USDT', 'USDSB/USDT', 'DGB/USDT', 'TRB/USDT', 'CKB/USDT', 'SHIB/USDT', 'MOB/USDT',
                       'PHB/USDT', 'VIB/USDT', 'AMB/USDT', 'ARB/USDT', 'BB/USDT', 'YB/USDT']

        for item in list_remove:
            if item in matched_symbols:
                matched_symbols.remove(item)

        if matched_symbols:
            print(f" us stock {target_symbol} on Binance Exchange:", matched_symbols)
        else:
            print(f"not found {target_symbol} on Binance Exchange.")

        return matched_symbols


if __name__ == "__main__":
    token = "BTC/USDT"
    timeframe = "1d"

    fetcher = FetchBinanceData()

    # 1. Get RSI Data
    data = fetcher.get_binance_data(token=token, timeframe=timeframe, period=14)
    print(f"--- latest rsi {token} (timeframe {timeframe}) ---")
    print(data[['timestamp', 'close', 'RSI']].tail())

    # 2. Check for stock ticker
    print("\n--- check Tokenized Stocks ---")
    fetcher.get_us_stock_tickers_on_crypto_exchange("B/USDT")
