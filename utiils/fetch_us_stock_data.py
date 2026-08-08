import requests
import time
import config
import yfinance as yf
import pandas as pd


class FetchUsStockData:

    def __init__(self):
        self.api_key = config.Config.API_KEY_twelvedata
        self.base_url = "https://api.twelvedata.com/rsi"

    def get_us_stock_rsi(self, symbol: str, interval: str = "1day"):
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": 14,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_rsi = float(data["values"][0]["rsi"])
                print(f"current rsi of {symbol} ({interval}) is : {latest_rsi:.2f}")
                return latest_rsi
            else:
                error_msg = data.get("message", "not found")
                print(f"❌ Error while getting data {symbol}: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error while connecting to api {symbol}: {e}")
            return None

    @staticmethod
    def get_data_us_stock(ticker, period_data="100d", interval="1d"):
        """
            get us stock and calculate rsi
            - ticker: ('TSLA', 'AAPL', 'NVDA', 'MSFT', 'AMZN'...)
            - interval: ('5m', '15m', '1h', '1d'...)
            """

        # 1. load data from Yahoo Finance
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period_data, interval=interval)

            if df.empty:
                print(f"⚠️ not found '{ticker}'")
                return None

            df = df.reset_index()

            # correct columns (snake_case)
            rename_dict = {
                "Date": "timestamp",
                "Datetime": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
            df.rename(columns=rename_dict, inplace=True)

            # 3. remove timezones
            if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(
                    df["timestamp"]
            ):
                df["timestamp"] = df["timestamp"].dt.tz_localize(None)

            keep_cols = [
                col
                for col in ["timestamp", "open", "high", "low", "close", "volume"]
                if col in df.columns
            ]

            print(f"✅ load data successfully {len(df)} for {ticker}")
            print(df)
            return df[keep_cols]

        except Exception as e:
            print(f"❌ Error while loading data {ticker}: {e}")
            return None


if __name__ == "__main__":
    fetcher = FetchUsStockData()

    symbols_list = getattr(config.Config, "SYMBOLS_LIST", ["AAPL", "MSFT", "TSLA"])

    for symbol in symbols_list:
        fetcher.get_us_stock_rsi(symbol=symbol, interval="1day")
        fetcher.get_data_us_stock(symbol)

