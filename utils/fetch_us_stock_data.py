import logging
import requests
import time
import config
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)


class FetchUsStockData:

    def __init__(self):
        # Ưu tiên tên mới TWELVEDATA_API_KEY, fallback alias cũ để tương thích
        self.api_key = getattr(config.Config, "TWELVEDATA_API_KEY", "") or getattr(
            config.Config, "API_KEY_twelvedata", ""
        )
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
            response = requests.get(self.base_url_rsi, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_rsi = float(data["values"][0]["rsi"])
                logger.info("current rsi of %s (%s) is : %.2f", ticker, interval, latest_rsi)
                return latest_rsi
            else:
                error_msg = data.get("message", "not found")
                logger.error("Error while getting data %s: %s", ticker, error_msg)
                return None

        except requests.exceptions.RequestException as e:
            logger.error("Error while connecting to api %s: %s", ticker, e)
            return None

    def get_us_stock_ma50(self, ticker: str, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "time_period": 50,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_sma, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_sma = float(data["values"][0]["sma"])
                logger.info("current sma50 of %s (%s) is : %.2f", ticker, interval, latest_sma)
                return latest_sma
            else:
                error_msg = data.get("message", "not found")
                logger.error("Error while getting data %s: %s", ticker, error_msg)
                return None

        except requests.exceptions.RequestException as e:
            logger.error("Error while connecting to api %s: %s", ticker, e)
            return None

    def get_us_stock_ma200(self, ticker: str, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "time_period": 200,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_sma, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            time.sleep(8)

            # check values from api's response
            if "values" in data and len(data["values"]) > 0:
                latest_sma = float(data["values"][0]["sma"])
                logger.info("current sma200 of %s (%s) is : %.2f", ticker, interval, latest_sma)
                return latest_sma
            else:
                error_msg = data.get("message", "not found")
                logger.error("Error while getting data %s: %s", ticker, error_msg)
                return None

        except requests.exceptions.RequestException as e:
            logger.error("Error while connecting to api %s: %s", ticker, e)
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
                logger.warning("not found '%s'", ticker)
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

            # 3. remove timezones (chỉ khi cột thực sự có tz)
            if "timestamp" in df.columns and pd.api.types.is_datetime64_any_dtype(
                    df["timestamp"]
            ):
                try:
                    if getattr(df["timestamp"].dt, "tz", None) is not None:
                        df["timestamp"] = df["timestamp"].dt.tz_localize(None)
                except (TypeError, AttributeError):
                    pass

            keep_cols = [
                col
                for col in ["timestamp", "open", "high", "low", "close", "volume"]
                if col in df.columns
            ]

            logger.info("load data successfully %d rows for %s", len(df), ticker)
            logger.debug("%s", df.head())
            return df[keep_cols]

        except Exception as e:
            logger.error("Error while loading data %s: %s", ticker, e)
            return None

    @staticmethod
    def get_current_stock_price(ticker):
        stock = yf.Ticker(ticker)

        fast_info = stock.fast_info
        current_price = fast_info['lastPrice']

        logger.info("Ticker: %s", ticker.upper())
        logger.info("Current Price: $%.2f", current_price)

        return current_price

    def get_stock_data_from_timeseries(self, ticker, interval: str = "1day"):
        params = {
            "symbol": ticker,
            "interval": interval,
            "outputsize": 200,
            "apikey": self.api_key,
        }

        try:
            response = requests.get(self.base_url_time_series, params=params, timeout=30)
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
            logger.error("Error to get %s: %s", ticker, e)
            return None, None, None


if __name__ == "__main__":
    fetcher = FetchUsStockData()

    symbols_list = getattr(config.Config, "SYMBOLS_LIST", ["AAPL", "MSFT", "TSLA"])

    for symbol in symbols_list:
        fetcher.get_us_stock_rsi(ticker=symbol, interval="1day")
        fetcher.get_data_us_stock(symbol)

