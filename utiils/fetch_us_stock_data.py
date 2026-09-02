import requests
import time
import config
import yfinance as yf
import pandas as pd


class FetchUsStockData:

    def __init__(self):
        self.api_key = config.Config.API_KEY_twelvedata
        self.base_url_rsi = "https://api.twelvedata.com/rsi"
        self.base_url_sma = "https://api.twelvedata.com/sma"
        self.base_url_time_series = "https://api.twelvedata.com/time_series"

    def get_us_stock_rsi(self, ticker: str, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "time_period": 14,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_rsi, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_rsi = float(data["values"][0]["rsi"])
                print(f"current rsi of {ticker} ({interval}) is : {latest_rsi:.2f}")
                return latest_rsi
            else:
                error_msg = data.get("message", "not found")
                print(f"❌ Error while getting data {ticker}: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error while connecting to api {ticker}: {e}")
            return None

    def get_us_stock_ma50(self, ticker: str, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "time_period": 50,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_sma, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_sma = float(data["values"][0]["sma"])
                print(f"current sma50 of {ticker} ({interval}) is : {latest_sma:.2f}")
                return latest_sma
            else:
                error_msg = data.get("message", "not found")
                print(f"❌ Error while getting data {ticker}: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error while connecting to api {ticker}: {e}")
            return None

    def get_us_stock_ma200(self, ticker: str, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "time_period": 200,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_sma, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_sma = float(data["values"][0]["sma"])
                print(f"current sma200 of {ticker} ({interval}) is : {latest_sma:.2f}")
                return latest_sma
            else:
                error_msg = data.get("message", "not found")
                print(f"❌ Error while getting data {ticker}: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error while connecting to api {ticker}: {e}")
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

    @staticmethod
    def get_current_stock_price(ticker):
        ticker = yf.Ticker(ticker)

        fast_info = ticker.fast_info
        current_price = fast_info['lastPrice']

        print(f"Ticker: {symbol.upper()}")
        print(f"Current Price: ${current_price:.2f}")

        return current_price

    def get_stock_data_from_timeseries(self, ticker, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "outputsize": 200,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_time_series, params=params, timeout=10)
            data = response.json()

            values = data.get("values", [])
            time.sleep(8)

            if len(values) < 200:
                return None, None, None

            current_price = float(values[0]["close"])

            closes_50 = [float(item["close"]) for item in values[:50]]
            closes_200 = [float(item["close"]) for item in values[:200]]

            sma50 = sum(closes_50) / 50
            sma200 = sum(closes_200) / 200

            return current_price, sma50, sma200

        except Exception as e:
            print(f"Error to get {ticker}: {e}")
            return None, None, None


if __name__ == "__main__":
    fetcher = FetchUsStockData()

    symbols_list = getattr(config.Config, "SYMBOLS_LIST", ["AAPL", "MSFT", "TSLA"])

    for symbol in symbols_list:
        fetcher.get_us_stock_rsi(ticker=symbol, interval="1day")
        fetcher.get_data_us_stock(symbol)

