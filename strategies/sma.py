"""
            đây đươc gọi là chiến lược chuan bị kiếm đảo chiều xh, bằng cách kiếm cổ phiếu dưới ma200 nhưng trên ma50

            và có đỉnh đáy đảo chiều thì gần như tỷ lệ thành công khá cao

            chiến lươc này dành cho đánh đảo chiều xh trên khung lớn


            thêm 1 chiến lược là : vượt ma50 và ma200 không quá 15% .
            mục tiêu là kiếm chiến lược polarity ( vượt kháng cự và backtest)
            """


"""
           giá nằm trên ma200

           rsi quá ban 4h ~~ 32

            kiểu : cool off rsi kết hợp với shakeout trước khi bay lên trời. ck vn có PET 2026-09-20
            """

from config import Config
from strategies.base import BaseStrategy
from strategies.rsi_oversold import latest_rsi_from_df
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_us_stock_data import FetchUsStockData

RSI_COOLOFF = 32
# RSI cool-off LUÔN chạy khung 4h: giá (SMA daily) nằm trên sma200 nhưng RSI 4h
# quá bán = nhịp cool-off/shakeout trước khi bay. Không dùng self.interval.
RSI_INTERVAL = "4h"
POLARITY_RATIO = 1.15


class SMA(BaseStrategy):

    def __init__(self):
        super().__init__(name="sma")
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()

    @staticmethod
    def _classify(price, sma50, sma200, rsi, sma_out, polarity_out, cooloff_out, label):
        if None not in (price, sma50, sma200):
            if sma200 >= price >= sma50:
                sma_out.append(label)

            # 2. Kiểm tra điều kiện:
            # - Lớn hơn SMA50 và SMA200
            # - Không vượt quá 15% (tức là <= 1.15 lần SMA)
            is_above_sma50 = sma50 < price <= (sma50 * POLARITY_RATIO)
            is_above_sma200 = sma200 < price <= (sma200 * POLARITY_RATIO)

            if is_above_sma50 and is_above_sma200:
                polarity_out.append(label)

        if None not in (price, rsi, sma200):
            if price >= sma200 and rsi <= RSI_COOLOFF:
                cooloff_out.append(label)

    def us_stock(self):
        sma_list, polarity_list, cooloff_list = [], [], []

        for ticker in Config.US_TICKERS:
            unpacked = self.safe_call(
                self.fetcher_us_data.get_stock_data_from_timeseries, ticker)
            if not unpacked:
                continue
            price, sma50, sma200 = unpacked
            rsi = self.safe_call(self.fetcher_us_data.get_us_stock_rsi, ticker,
                                 interval=RSI_INTERVAL)
            self._classify(price, sma50, sma200, rsi,
                           sma_list, polarity_list, cooloff_list, ticker)

        self.save_signal("us_stock_sma", sma_list)
        self.save_signal("us_stock_polarity", polarity_list)
        self.save_signal("us_stock_094h", cooloff_list)

    def binance_token(self):
        sma_list, polarity_list, cooloff_list = [], [], []

        for token in Config.TOKENS:
            unpacked = self.safe_call(
                self.fetcher_binance_data.get_binance_from_timeseries, token)
            if not unpacked:
                continue
            price, sma50, sma200 = unpacked
            df = self.safe_call(self.fetcher_binance_data.get_binance_data, token,
                                timeframe=RSI_INTERVAL)
            rsi = latest_rsi_from_df(df)
            self._classify(price, sma50, sma200, rsi,
                           sma_list, polarity_list, cooloff_list, token)

        self.save_signal("binance_token_sma", sma_list)
        self.save_signal("binance_token_polarity", polarity_list)
        self.save_signal("binance_token_094h", cooloff_list)

    def main(self):
        self.run_timed("sma", lambda: (self.us_stock(), self.binance_token()))


if __name__ == '__main__':
    SMA().main()


def python_operator_run(**kwargs):
    SMA().main()
