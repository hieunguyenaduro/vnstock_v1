"""Lọc RSI khung 1h cho các mã US đã qua vòng quét daily."""

from strategies.base import BaseStrategy
from strategies.rsi_oversold import RSI_OVERBOUGHT, RSI_OVERSOLD
from utils.common import Common
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_us_stock_data import FetchUsStockData

US_STOCK_SIGNAL_FILES = ["us_stock_wave_down", "us_stock_wave_up", "us_stock_hh_hl",
                         "us_stock_ll_hh", "us_stock_sma", "us_stock_polarity"]


class UsStock091h(BaseStrategy):

    def __init__(self, interval):
        super().__init__(name="us_stock_1h")
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def us_stock(self, list_tickers, file_name):
        oversold, overbought = [], []

        for ticket in list_tickers or []:
            rsi = self.safe_call(self.fetcher_us_data.get_us_stock_rsi, ticket,
                                 interval=self.interval)
            if rsi is not None and rsi <= RSI_OVERSOLD:
                oversold.append(ticket)
            if rsi is not None and rsi >= RSI_OVERBOUGHT:
                overbought.append(ticket)

        self.save_signal("us_stock_rsi_oversold_1h", oversold,
                         filename=f"{file_name}_rsi_oversold_1h")
        self.save_signal("us_stock_rsi_overbought_1h", overbought,
                         filename=f"{file_name}_rsi_overbought_1h")

    def main(self):
        def _run():
            for file_name in US_STOCK_SIGNAL_FILES:
                tickers = Common.get_data_from_file(file_path=f'data/{file_name}.json',
                                                    list_tickers=file_name)
                self.us_stock(tickers, file_name)

        self.run_timed("us_stock_1h", _run)


if __name__ == '__main__':
    UsStock091h(interval='1h').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""


def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    UsStock091h(interval=interval if interval else "1h").main()
