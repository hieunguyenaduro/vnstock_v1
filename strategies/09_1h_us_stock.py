import time
from pathlib import Path

from utiils.common import Common
from utiils.fetch_us_stock_data import FetchUsStockData
from utiils.fetch_binance_data import FetchBinanceData

etl_path = str(Path(__file__).resolve().parents[1])


class RSIOverSold1h:

    def __init__(self, interval):
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def us_stock(self, list_tickers, file_name):
        list_ticker_rsi_oversold = []
        list_us_stock_rsi_overbought = []

        for ticket in list_tickers:
            latest_rsi = self.fetcher_us_data.get_us_stock_rsi(ticker=ticket, interval=self.interval)
            if latest_rsi is not None and latest_rsi <= 33:
                list_ticker_rsi_oversold.append(ticket)
            if latest_rsi is not None and latest_rsi >= 67:
                list_us_stock_rsi_overbought.append(ticket)

        if list_ticker_rsi_oversold:
            data = [{"us_stock_rsi_oversold_1h": list_ticker_rsi_oversold}]
            Common.create_json_file(data, etl_path, f"{file_name}_rsi_oversold_1h")

        if list_us_stock_rsi_overbought:
            data = [{"us_stock_rsi_overbought_1h": list_us_stock_rsi_overbought}]
            Common.create_json_file(data, etl_path, f"{file_name}_rsi_overbought_1h")

    def main(self):
        start_time = time.perf_counter()

        list_us_stock = ["us_stock_wave_down", "us_stock_wave_up", "us_stock_hh_hl", "us_stock_ll_hh", "us_stock_sma",
                         "us_stock_polarity"]

        for file_name in list_us_stock:
            list_tickers = Common.get_data_from_file(file_path=f'data/{file_name}.json', list_tickers=file_name)
            self.us_stock(list_tickers, file_name)

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    RSIOverSold1h(interval='1h').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""


def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    RSIOverSold1h(interval=interval if interval else "1h").main()
