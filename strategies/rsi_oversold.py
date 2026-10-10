import time
from pathlib import Path

from utiils.common import Common
from config import Config
from utiils.fetch_us_stock_data import FetchUsStockData
from utiils.fetch_binance_data import FetchBinanceData

etl_path = str(Path(__file__).resolve().parents[1])


class RSIOverSold:

    def __init__(self, interval):
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def us_stock(self):
        list_ticker_rsi_oversold = []
        list_us_stock_rsi_overbought = []

        if self.interval == "1d":
            interval = "1day"
        else:
            interval = self.interval

        for ticket in Config.US_TICKERS:
            latest_rsi = self.fetcher_us_data.get_us_stock_rsi(ticker=ticket, interval=interval)
            if latest_rsi is not None and latest_rsi <= 33:
                list_ticker_rsi_oversold.append(ticket)
            if latest_rsi is not None and latest_rsi >= 67:
                list_us_stock_rsi_overbought.append(ticket)

        if list_ticker_rsi_oversold:
            data = [{"us_stock_rsi_oversold": list_ticker_rsi_oversold}]
        else:
            data = [{"us_stock_rsi_oversold": []}]
        Common.create_json_file(data, etl_path, "us_stock_rsi_oversold")
        if list_us_stock_rsi_overbought:
            data = [{"us_stock_rsi_overbought": list_us_stock_rsi_overbought}]
        else:
            data = [{"us_stock_rsi_overbought": []}]
        Common.create_json_file(data, etl_path, "us_stock_rsi_overbought")


    def binance_token(self):
        list_token_rsi_oversold = []
        list_token_rsi_overbought = []

        for token in Config.TOKENS:
            df = self.fetcher_binance_data.get_binance_data(token=token, timeframe=self.interval)
            if df is None or df.empty or "RSI" not in df.columns:
                continue
            rsi_series = df["RSI"].dropna()
            if rsi_series.empty:
                continue
            latest_rsi = float(rsi_series.iloc[-1])
            if latest_rsi is not None and latest_rsi <= 33:
                list_token_rsi_oversold.append(token)
            if latest_rsi is not None and latest_rsi >= 67:
                list_token_rsi_overbought.append(token)

        data = [{"binance_token_rsi_oversold": list_token_rsi_oversold}]
        Common.create_json_file(data, etl_path, "binance_token_rsi_oversold")
        data = [{"binance_token_rsi_overbought": list_token_rsi_overbought}]
        Common.create_json_file(data, etl_path, "binance_token_rsi_overbought")

    def main(self):
        start_time = time.perf_counter()

        self.us_stock()
        self.binance_token()

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    RSIOverSold(interval='1d').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""
def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    RSIOverSold(interval=interval if interval else "1d").main()
