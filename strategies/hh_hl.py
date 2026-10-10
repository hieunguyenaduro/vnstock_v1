"""Chiến lược uptrend: Higher-High + Higher-Low."""

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


class HhHl(BaseStrategy):

    def __init__(self):
        super().__init__(name="hh_hl")
        self.fetcher = FetchData()
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()

    @staticmethod
    def hh_hl(df, list_ticker_uptrend, ticket):
        if df is None or getattr(df, "empty", True) or "close" not in df.columns:
            return
        prices = df['close'].values

        # 2. Find all local peaks and troughs
        # Adjust distance and prominence depending on how noisy the stock is
        peaks, _ = find_peaks(prices, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)
        troughs, _ = find_peaks(-prices, distance=PEAK_DISTANCE, prominence=PEAK_PROMINENCE)

        # 3. Algorithm to detect reversal points (HH and HL)
        trend_signals = []

        for i in range(1, len(peaks)):
            # Check that the next peak is higher than the previous one (Higher High)
            if prices[peaks[i]] > prices[peaks[i - 1]]:
                # Check that the most recent trough is also higher than the one before it (Higher Low)
                # Find the troughs that fall between or right before these two peaks
                recent_troughs = [t for t in troughs if t < peaks[i]]
                if len(recent_troughs) >= 2:
                    if prices[recent_troughs[-1]] > prices[recent_troughs[-2]]:
                        trend_signals.append(peaks[i])

        logger.debug("prices peaks: %s (len %d)", prices[peaks], len(prices[peaks]))
        logger.debug("prices troughs: %s (len %d)", prices[troughs], len(prices[troughs]))

        # Flag confirmed uptrend points (next peak > previous peak & next trough > previous trough)
        if trend_signals:
            logger.info("stock %s entering an uptrend wave", ticket)
            list_ticker_uptrend.append(ticket)

    def _vn_one(self, ticket, out):
        df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D',
                                                start_date=self.execution_range_date,
                                                end_date=self.execution_date)
        self.hh_hl(df, out, ticket)

    def _us_one(self, ticket, out):
        df = self.fetcher_us_data.get_data_us_stock(ticker=ticket)
        self.hh_hl(df, out, ticket)

    def _binance_one(self, token, out):
        df = self.fetcher_binance_data.get_binance_data(token=token)
        self.hh_hl(df, out, token)

    def vn_stock(self):
        found = self.scan_tickers(Config.ALL_TICKERS, self._vn_one)
        self.save_signal("vn_stock_hh_hl", found)

    def us_stock(self):
        found = self.scan_tickers(Config.US_TICKERS, self._us_one)
        self.save_signal("us_stock_hh_hl", found)

    def binance_token(self):
        found = self.scan_tickers(Config.TOKENS, self._binance_one)
        self.save_signal("binance_token_hh_hl", found)

    def main(self):
        if not Config.is_uptrend_off:
            self.run_timed("hh_hl", lambda: (self.vn_stock(), self.us_stock(), self.binance_token()))
        else:
            self.log.info("uptrend feature is off")


if __name__ == '__main__':
    HhHl().main()


def python_operator_run(**kwargs):
    HhHl().main()
