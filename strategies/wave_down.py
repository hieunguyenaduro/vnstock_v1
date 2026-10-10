"""Chiến lược sóng giảm (zigzag theo % biến động)."""

from config import Config
from strategies.base import BaseStrategy
from utils.fetch_binance_data import FetchBinanceData
from utils.fetch_data import FetchData
from utils.fetch_us_stock_data import FetchUsStockData

WAVE_THRESHOLD_VN = 20
WAVE_THRESHOLD_US = 20
WAVE_THRESHOLD_CRYPTO = 20


class WaveDown(BaseStrategy):

    def __init__(self):
        super().__init__(name="wave_down")
        self.fetcher = FetchData()
        self.fetcher_us_data = FetchUsStockData()
        self.fetcher_binance_data = FetchBinanceData()

    @staticmethod
    def identify_zigzag_waves(df, threshold=10):
        """Xác định các đỉnh và đáy dựa trên phần trăm biến động."""
        return BaseStrategy.identify_zigzag(df, threshold)

    def plot_growth_waves(self, df, threshold=20):
        """Trả về % sóng giảm mạnh nhất vượt ngưỡng (số âm), None nếu không có."""
        pivots = self.identify_zigzag_waves(df, threshold)
        percentage_wave = None
        for change_pct in BaseStrategy.iter_wave_changes(pivots):
            # Chỉ đánh dấu sóng giảm vượt ngưỡng
            if change_pct <= -threshold:
                percentage_wave = change_pct
        return percentage_wave

    def _vn_one(self, ticket, out):
        df = self.fetcher.fetch_data_for_ticker(ticker=ticket, timeframe='1D',
                                                start_date=self.execution_range_date,
                                                end_date=self.execution_date)
        if self.plot_growth_waves(df, threshold=WAVE_THRESHOLD_VN):
            out.append(ticket)

    def _us_one(self, ticket, out):
        df = self.fetcher_us_data.get_data_us_stock(ticker=ticket)
        if self.plot_growth_waves(df, threshold=WAVE_THRESHOLD_US):
            out.append(ticket)

    def _binance_one(self, token, out):
        df = self.fetcher_binance_data.get_binance_data(token=token)
        if self.plot_growth_waves(df, threshold=WAVE_THRESHOLD_CRYPTO):
            out.append(token)

    def vn_stock(self):
        found = self.scan_tickers(Config.ALL_TICKERS, self._vn_one)
        self.save_signal("vn_stock_wave_down", found)

    def binance_token(self):
        found = self.scan_tickers(Config.TOKENS, self._binance_one)
        self.save_signal("binance_token_wave_down", found)

    def us_stock(self):
        found = self.scan_tickers(Config.US_TICKERS, self._us_one)
        self.save_signal("us_stock_wave_down", found)

    def main(self):
        if not Config.is_downtrend_off:
            self.run_timed("wave_down", lambda: (self.vn_stock(), self.binance_token(), self.us_stock()))
        else:
            self.log.info("downtrend feature is off")


if __name__ == '__main__':
    WaveDown().main()


def python_operator_run(**kwargs):
    WaveDown().main()
