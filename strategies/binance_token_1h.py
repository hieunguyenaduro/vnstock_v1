import time
from pathlib import Path

from utiils.common import Common
from utiils.fetch_us_stock_data import FetchUsStockData
from utiils.fetch_binance_data import FetchBinanceData

etl_path = str(Path(__file__).resolve().parents[1])


class BinanceToken091h:

    def __init__(self, interval):
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def binance_token(self, list_tokens, file_name):
        list_token_rsi_oversold = []
        list_token_rsi_overbought = []

        for token in list_tokens:
            df = self.fetcher_binance_data.get_binance_data(token=token, timeframe=self.interval)
            latest_rsi = df[['timestamp', 'close', 'RSI']].tail()
            latest_rsi = latest_rsi.iloc[4]["RSI"]
            if latest_rsi is not None and latest_rsi <= 33:
                list_token_rsi_oversold.append(token)
            if latest_rsi is not None and latest_rsi >= 67:
                list_token_rsi_overbought.append(token)

        if list_token_rsi_oversold:
            data = [{"binance_token_rsi_oversold": list_token_rsi_oversold}]
            Common.create_json_file(data, etl_path, f"{file_name}_rsi_oversold")
        if list_token_rsi_overbought:
            data = [{"binance_token_rsi_overbought": list_token_rsi_overbought}]
            Common.create_json_file(data, etl_path, f"{file_name}_rsi_overbought")

    def main(self):
        start_time = time.perf_counter()

        list_binance_token = ["binance_token_wave_down", "binance_token_wave_up", "binance_token_hh_hl",
                              "binance_token_ll_hh", "binance_token_sma",
                              "binance_token_polarity"]

        for file_name in list_binance_token:
            list_tokens = Common.get_data_from_file(file_path=f'data/{file_name}.json', list_tickers=file_name)
            self.binance_token(list_tokens, file_name)

        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'"execution_time": {execution_time:.2f}')


if __name__ == '__main__':
    BinanceToken091h(interval='1h').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""


def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    BinanceToken091h(interval=interval if interval else "1h").main()
