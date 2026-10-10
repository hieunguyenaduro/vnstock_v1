"""Chiến lược downtrend: Lower-Low + Lower-High."""

import logging

from scipy.signal import find_peaks

from config import Config
from strategies.base import BaseStrategy
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_data import FetchData
from utils.fetch_us_stock_data import FetchUsStockData

logger = logging.getLogger(__name__)

PEAK_DISTANCE = 5
PEAK_PROMINENCE = 1


class LlLh(BaseStrategy):

    def __init__(self):
        super().__init__(name="ll_lh")
        self.fetcher = FetchData()
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()

    @staticmethod
    def ll_lh(df, list_ticker_downtrend, ticket):
        """Thứ tự tham số thống nhất với HhHl.hh_hl(df, tickers, ticket)."""
        if df is None or getattr(df, "empty", True) or "close" not in df.columns:
            return
        prices = df['close'].values

        # 2. Tìm Đỉnh (Peaks) và Đáy (Troughs)
        # distance=5: Khoảng cách tối thiểu giữa 2 đỉnh/đáy là 5 phiên
        # prominence=1: Độ cao chênh lệch tối thiểu để coi là 1 đỉnh/đáy rõ nét
        peaks, _ = find_peaks(prices, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)
        troughs, _ = find_peaks(-prices, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)

        # 3. Thuật toán xác định Điểm Đảo Chiều Giảm (LH + LL)
        reversal_signals = []

        # Chúng ta duyệt qua các đáy để tìm Lower Low (LL)
        for i in range(1, len(troughs)):
            current_trough_idx = troughs[i]
            prev_trough_idx = troughs[i - 1]

            # ĐIỀU KIỆN 1: Đáy sau thấp hơn đáy trước (Lower Low)
            if prices[current_trough_idx] < prices[prev_trough_idx]:

                # ĐIỀU KIỆN 2: Tìm các đỉnh nằm trước đáy hiện tại để kiểm tra Lower High (LH)
                recent_peaks = [p for p in peaks if p < current_trough_idx]

                if len(recent_peaks) >= 2:
                    # Nếu đỉnh gần nhất thấp hơn đỉnh trước đó
                    if prices[recent_peaks[-1]] < prices[recent_peaks[-2]]:
                        # Đây là điểm xác nhận đảo chiều xu hướng sang giảm
                        reversal_signals.append(current_trough_idx)

        logger.debug("prices peaks: %s (len %d)", prices[peaks], len(prices[peaks]))
        logger.debug("prices troughs: %s (len %d)", prices[troughs], len(prices[troughs]))

        # Đánh dấu điểm ĐẢO CHIỀU (Xác nhận cấu trúc LH + LL)
        if reversal_signals:
            logger.info("stock %s entering a downtrend wave", ticket)
            list_ticker_downtrend.append(ticket)

    def _vn_one(self, ticket, out):
        df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D',
                                                start_date=self.execution_range_date,
                                                end_date=self.execution_date)
        self.ll_lh(df, out, ticket)

    def _us_one(self, ticket, out):
        df = self.fetcher_us_data.get_data_us_stock(ticker=ticket)
        self.ll_lh(df, out, ticket)

    def _binance_one(self, token, out):
        df = self.fetcher_binance_data.get_binance_data(token=token)
        self.ll_lh(df, out, token)

    def vn_stock(self):
        found = self.scan_tickers(Config.ALL_TICKERS, self._vn_one)
        self.save_signal("vn_stock_ll_hh", found)

    def us_stock(self):
        found = self.scan_tickers(Config.US_TICKERS, self._us_one)
        self.save_signal("us_stock_ll_hh", found)

    def binance_token(self):
        found = self.scan_tickers(Config.TOKENS, self._binance_one)
        self.save_signal("binance_token_ll_hh", found)

    def main(self):
        if not Config.is_downtrend_off:
            self.run_timed("ll_lh", lambda: (self.vn_stock(), self.us_stock(), self.binance_token()))
        else:
            self.log.info("downtrend feature is off")


if __name__ == '__main__':
    LlLh().main()


def python_operator_run(**kwargs):
    LlLh().main()
