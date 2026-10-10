import logging

import ccxt
import pandas as pd
import pandas_ta as ta

logger = logging.getLogger(__name__)


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
            logger.info("us stock %s on Binance Exchange: %s", target_symbol, matched_symbols)
        else:
            logger.warning("not found %s on Binance Exchange.", target_symbol)

        return matched_symbols

    def get_current_token_price(self, token):
        ticker = self.exchange.fetch_ticker(token)
        current_price = ticker['last']
        logger.info("Current %s price on Binance: $%s", token, f"{current_price:,.2f}")

        return current_price

    def get_binance_from_timeseries(self, token: str, timeframe: str = "1d"):

        try:

            ohlcv = self.exchange.fetch_ohlcv(token, timeframe, limit=200)

            if not ohlcv or len(ohlcv) < 200:
                logger.warning("not enough candles for %s: got %s", token, len(ohlcv) if ohlcv else 0)
                return None, None, None

            close_prices = [float(candle[4]) for candle in ohlcv]

            current_price = float(close_prices[-1])

            # Calculate SMAs from the most recent closing prices
            sma_50 = sum(close_prices[-50:]) / 50
            sma_200 = sum(close_prices[-200:]) / 200

            # check values from api's response
            if sma_50 > 0 and sma_200 > 0:
                logger.info("current sma50 of %s (%s) is : %.2f", token, timeframe, sma_50)
                logger.info("current sma200 of %s (%s) is : %.2f", token, timeframe, sma_200)
                return current_price, sma_50, sma_200
            else:
                logger.error("Invalid SMA for %s: sma50=%s, sma200=%s", token, sma_50, sma_200)
                return None, None, None

        except Exception as e:
            logger.error("Error while connecting to api %s: %s", token, e)
            return None, None, None


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
