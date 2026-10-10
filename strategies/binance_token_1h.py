"""Lọc RSI khung 1h cho các token Binance đã qua vòng quét daily."""

from strategies.base import BaseStrategy
from strategies.rsi_oversold import RSI_OVERBOUGHT, RSI_OVERSOLD, latest_rsi_from_df
from utils.common import Common
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_us_stock_data import FetchUsStockData

BINANCE_SIGNAL_FILES = ["binance_token_wave_down", "binance_token_wave_up",
                        "binance_token_hh_hl", "binance_token_ll_hh",
                        "binance_token_sma", "binance_token_polarity"]


class BinanceToken091h(BaseStrategy):

    def __init__(self, interval):
        super().__init__(name="binance_token_1h")
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()
        self.interval = interval

    def binance_token(self, list_tokens, file_name):
        oversold, overbought = [], []

        for token in list_tokens or []:
            df = self.safe_call(self.fetcher_binance_data.get_binance_data, token,
                                timeframe=self.interval)
            rsi = latest_rsi_from_df(df)
            if rsi is not None and rsi <= RSI_OVERSOLD:
                oversold.append(token)
            if rsi is not None and rsi >= RSI_OVERBOUGHT:
                overbought.append(token)

        self.save_signal("binance_token_rsi_oversold", oversold,
                         filename=f"{file_name}_rsi_oversold")
        self.save_signal("binance_token_rsi_overbought", overbought,
                         filename=f"{file_name}_rsi_overbought")

    def main(self):
        def _run():
            for file_name in BINANCE_SIGNAL_FILES:
                tokens = Common.get_data_from_file(file_path=f'data/{file_name}.json',
                                                   list_tickers=file_name)
                self.binance_token(tokens, file_name)

        self.run_timed("binance_token_1h", _run)


if __name__ == '__main__':
    BinanceToken091h(interval='1h').main()
"""
    - interval: ('5m', '15m', '1h', '1d'...)
"""


def python_operator_run(**kwargs):
    interval = kwargs.get("interval") or kwargs.get("op_kwargs", {}).get("interval")
    BinanceToken091h(interval=interval if interval else "1h").main()
